from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import os
import glob
from datetime import datetime

# 创建路由实例
router = APIRouter(prefix="/api/transaction", tags=["交割单分析模块"])

# 定义交割单文件目录
TRANSACTION_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../file/trans')

# 根据测试用例分析的Excel格式，定义列名映射
COLUMN_MAPPING = {
    'date_column': '成交日期',
    'stock_code_column': '证券代码',
    'stock_name_column': '证券名称',
    'trade_type_column': '操作',
    'quantity_column': '成交数量',
    'amount_column': '成交金额',
    'price_columns': ['成交均价', '成交价格']  # 支持多种价格列名
}

# 格式化股票代码的辅助函数
def format_stock_code(code):
    """将股票代码格式化为6位数字字符串"""
    try:
        # 尝试将代码转换为浮点数，然后取整并转换为字符串（处理类似"3006.0"的情况）
        code_num = int(float(code))
        # 确保A股股票代码保持6位数字格式，不足6位的前面补零
        return f"{code_num:06d}"
    except (ValueError, TypeError):
        # 如果转换失败，直接返回字符串并去除可能的".0"后缀
        return str(code).rstrip('.0')

# 解析日期的辅助函数
def parse_date(date_value):
    """将各种格式的日期转换为YYYY-MM-DD格式"""
    try:
        # 直接处理整数格式的日期（YYYYMMDD）
        date_int = int(date_value)
        year = date_int // 10000
        month = (date_int % 10000) // 100
        day = date_int % 100
        return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, TypeError):
        try:
            # 尝试字符串格式
            date_str = str(date_value).strip()
            if len(date_str) == 8 and date_str.isdigit():
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:])
                return f"{year:04d}-{month:02d}-{day:02d}"
            # 尝试其他格式
            return pd.to_datetime(date_value).strftime('%Y-%m-%d')
        except:
            # 如果解析失败，返回当前日期
            return datetime.now().strftime('%Y-%m-%d')

# 读取和处理单个Excel文件的辅助函数
def process_excel_file(file_path):
    """读取并处理单个Excel文件，返回标准化的交易数据"""
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 去除列名中的空格
        df.columns = df.columns.str.strip()
        
        # 检查是否为空文件
        if df.empty:
            return []
        
        # 查找价格列
        price_column = None
        for col in COLUMN_MAPPING['price_columns']:
            if col in df.columns:
                price_column = col
                break
        
        if not price_column:
            print(f"文件 {file_path} 缺少价格列，跳过处理")
            return []
        
        # 检查必要列是否存在
        required_columns = [
            COLUMN_MAPPING['date_column'],
            COLUMN_MAPPING['stock_code_column'],
            COLUMN_MAPPING['stock_name_column'],
            COLUMN_MAPPING['trade_type_column'],
            COLUMN_MAPPING['quantity_column'],
            COLUMN_MAPPING['amount_column']
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"文件 {file_path} 缺少必要列 {missing_columns}，跳过处理")
            return []
        
        # 选择需要的列
        selected_columns = required_columns + [price_column]
        transactions = df[selected_columns].copy()
        
        # 确保股票代码是字符串类型，并处理可能的浮点数格式
        transactions[COLUMN_MAPPING['stock_code_column']] = transactions[COLUMN_MAPPING['stock_code_column']].apply(format_stock_code)
        
        # 重命名列
        column_mapping = {
            COLUMN_MAPPING['date_column']: 'tradeDate',
            COLUMN_MAPPING['stock_code_column']: 'stockCode',
            COLUMN_MAPPING['stock_name_column']: 'stockName',
            COLUMN_MAPPING['trade_type_column']: 'tradeType',
            COLUMN_MAPPING['quantity_column']: 'quantity',
            COLUMN_MAPPING['amount_column']: 'amount',
            price_column: 'price'
        }
        
        transactions = transactions.rename(columns=column_mapping)
        
        # 转换日期格式
        transactions['tradeDate'] = transactions['tradeDate'].apply(parse_date)
        
        # 转换数值格式
        transactions['price'] = transactions['price'].astype(float)
        transactions['quantity'] = transactions['quantity'].astype(int)
        transactions['amount'] = transactions['amount'].astype(float)
        
        return transactions.to_dict('records')
        
    except Exception as e:
        import traceback
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        traceback.print_exc()
        return []

@router.get("/analyze")
async def analyze_transactions(stockCode: str = Query(..., description="要分析的股票代码")):
    """分析指定股票的交割单数据"""
    try:
        # 格式化输入的股票代码
        formatted_stock_code = format_stock_code(stockCode)
        
        # 检查目录是否存在
        if not os.path.exists(TRANSACTION_FILES_DIR):
            raise HTTPException(status_code=404, detail=f"交割单文件目录不存在: {TRANSACTION_FILES_DIR}")
        
        # 获取目录下所有Excel文件（包括子目录）
        excel_files = glob.glob(os.path.join(TRANSACTION_FILES_DIR, "**", "*.xlsx"), recursive=True) + glob.glob(os.path.join(TRANSACTION_FILES_DIR, "**", "*.xls"), recursive=True)
        
        if not excel_files:
            raise HTTPException(status_code=404, detail="未找到任何交割单Excel文件")
        
        # 整合所有文件的数据
        all_transactions = []
        
        for file_path in excel_files:
            print(f"开始处理文件: {file_path}")
            # 使用辅助函数处理单个文件
            file_transactions = process_excel_file(file_path)
            all_transactions.extend(file_transactions)
        
        if not all_transactions:
            raise HTTPException(status_code=404, detail="未找到有效交割单数据")
        
        # 按股票代码筛选数据
        filtered_transactions = [t for t in all_transactions if t['stockCode'] == formatted_stock_code]
        
        if not filtered_transactions:
            raise HTTPException(status_code=404, detail=f"未找到股票 {stockCode} 的交割单数据")
        
        # 按交易日期排序
        filtered_transactions.sort(key=lambda x: x['tradeDate'])
        
        # 构建响应数据
        response_data = {
            "stockCode": stockCode,
            "stockName": filtered_transactions[0]['stockName'],
            "totalTransactions": len(filtered_transactions),
            "data": filtered_transactions
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析交割单时发生错误: {str(e)}")

@router.get("/stocks")
async def get_transaction_stocks():
    """获取所有有交割单记录的股票列表"""
    try:
        # 检查目录是否存在
        if not os.path.exists(TRANSACTION_FILES_DIR):
            raise HTTPException(status_code=404, detail=f"交割单文件目录不存在: {TRANSACTION_FILES_DIR}")
        
        # 获取目录下所有Excel文件（包括子目录）
        excel_files = glob.glob(os.path.join(TRANSACTION_FILES_DIR, "**", "*.xlsx"), recursive=True) + glob.glob(os.path.join(TRANSACTION_FILES_DIR, "**", "*.xls"), recursive=True)
        
        if not excel_files:
            raise HTTPException(status_code=404, detail="未找到任何交割单Excel文件")
        
        # 收集所有股票代码和名称的映射关系
        stock_mapping = {}
        
        for file_path in excel_files:
            try:
                print(f"开始处理文件: {file_path}")
                
                # 使用辅助函数处理单个文件
                file_transactions = process_excel_file(file_path)
                
                # 只收集那些有实际交易记录的股票
                for transaction in file_transactions:
                    formatted_code = transaction['stockCode']
                    name = transaction['stockName']
                    trade_type = transaction['tradeType']
                    
                    # 确保是实际的买卖交易（不是其他操作如配号、转账等）
                    if not isinstance(trade_type, str) or (trade_type not in ['买入', '卖出', '证券买入', '证券卖出', '交易买入', '交易卖出']):
                        continue
                    
                    # 尝试多种方式获取名称
                    try:
                        stock_name = str(name)
                        # 如果名称为空字符串，使用默认名称
                        if not stock_name.strip():
                            stock_name = f"股票{formatted_code}"
                            print(f"警告: 文件 {file_path} 中股票代码 {formatted_code} 的名称为空，使用默认名称")
                        # 过滤掉配号记录
                        elif '配号' in stock_name:
                            continue
                    except Exception as e:
                        stock_name = f"股票{formatted_code}"
                        print(f"处理名称时出错: {e}, 值: {name}, 类型: {type(name)}，使用默认名称")
                    
                    # 只保存第一个出现的非空名称
                    if formatted_code not in stock_mapping:
                        stock_mapping[formatted_code] = stock_name
                        print(f"添加股票: {formatted_code} -> {stock_name}")
                
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        if not stock_mapping:
            raise HTTPException(status_code=404, detail="未找到任何股票交割单数据")
        
        # 构建响应数据，按股票代码排序
        # 直接返回格式化好的下拉选项数据，减少前端处理负担
        options = [
            {
                "value": code,
                "label": f"{code} - {name}"
            }
            for code, name in sorted(stock_mapping.items())
        ]
        
        return {
            "options": options
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交割单股票列表时发生错误: {str(e)}")