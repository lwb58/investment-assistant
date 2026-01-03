from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import os
import glob
import json
from datetime import datetime

# 创建路由实例
router = APIRouter(prefix="/api/transaction", tags=["交割单分析模块"])

# 定义交割单文件目录
TRANSACTION_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../file/trans')

# 支持的券商交割单格式映射
# 这里可以根据不同券商的交割单格式进行扩展
SUPPORTED_FORMATS = {
    'default': {
        'date_column': '成交日期',
        'stock_code_column': '证券代码',
        'stock_name_column': '证券名称',
        'trade_type_column': '买卖方向',
        'price_column': '成交价格',
        'quantity_column': '成交数量',
        'amount_column': '成交金额'
    }
}

@router.get("/analyze")
async def analyze_transactions(stockCode: str = Query(..., description="要分析的股票代码")):
    """分析指定股票的交割单数据"""
    try:
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
            try:
                # 读取Excel文件
                df = pd.read_excel(file_path)
                # 去除列名中的空格
                df.columns = df.columns.str.strip()
                
                # 检查是否为空文件
                if df.empty:
                    continue
                
                # 根据文件格式获取列名映射
                # 这里简单使用默认格式，实际项目中可以根据文件内容自动识别格式
                format_mapping = SUPPORTED_FORMATS['default']
                
                # 检查必要列是否存在
                required_columns = list(format_mapping.values())
                if not all(col in df.columns for col in required_columns):
                    # 如果列名不匹配，尝试使用另一种常见格式
                    # 这里可以根据实际情况扩展
                    continue
                
                # 转换数据格式
                transactions = df[[
                    format_mapping['date_column'],
                    format_mapping['stock_code_column'],
                    format_mapping['stock_name_column'],
                    format_mapping['trade_type_column'],
                    format_mapping['price_column'],
                    format_mapping['quantity_column'],
                    format_mapping['amount_column']
                ]].copy()
                
                # 确保股票代码是字符串类型，并处理可能的浮点数格式（如563200.0或3006.0）
                transactions[format_mapping['stock_code_column']] = transactions[format_mapping['stock_code_column']].apply(
                    lambda x: str(int(float(x))) if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.', '', 1).isdigit()) else str(x).rstrip('.0')
                )
                
                # 重命名列
                transactions.columns = [
                    'tradeDate',
                    'stockCode',
                    'stockName',
                    'tradeType',
                    'price',
                    'quantity',
                    'amount'
                ]
                
                # 转换日期格式
                transactions['tradeDate'] = pd.to_datetime(transactions['tradeDate']).dt.strftime('%Y-%m-%d')
                
                # 转换数值格式
                transactions['price'] = transactions['price'].astype(float)
                transactions['quantity'] = transactions['quantity'].astype(int)
                transactions['amount'] = transactions['amount'].astype(float)
                
                # 添加到总列表
                all_transactions.extend(transactions.to_dict('records'))
                
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {str(e)}")
                continue
        
        if not all_transactions:
            raise HTTPException(status_code=404, detail="未找到有效交割单数据")
        
        # 按股票代码筛选数据 - 处理可能的数值类型差异
        def match_stock_code(transaction_code, target_code):
            try:
                # 尝试将交易代码转换为浮点数进行比较（处理类似"563200.0"的情况）
                return float(transaction_code) == float(target_code)
            except (ValueError, TypeError):
                # 如果转换失败，使用字符串比较
                return str(transaction_code) == target_code
        
        filtered_transactions = [t for t in all_transactions if match_stock_code(t['stockCode'], stockCode)]
        
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
        
        # 收集所有股票代码
        stock_codes = set()
        
        for file_path in excel_files:
            try:
                # 读取Excel文件
                df = pd.read_excel(file_path)
                
                # 检查是否为空文件
                if df.empty:
                    continue
                
                # 根据文件格式获取列名映射
                format_mapping = SUPPORTED_FORMATS['default']
                
                # 检查必要列是否存在
                if format_mapping['stock_code_column'] not in df.columns:
                    continue
                
                # 收集股票代码
                codes = df[format_mapping['stock_code_column']].dropna().unique()
                stock_codes.update(codes)
                
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {str(e)}")
                continue
        
        if not stock_codes:
            raise HTTPException(status_code=404, detail="未找到任何股票交割单数据")
        
        # 格式化股票代码，确保一致的格式
        def format_stock_code(code):
            try:
                # 尝试将代码转换为浮点数，然后取整并转换为字符串（处理类似"3006.0"的情况）
                return str(int(float(code)))
            except (ValueError, TypeError):
                # 如果转换失败，直接返回字符串并去除可能的\.0"后缀
                return str(code).rstrip('.0')
        
        # 构建响应数据
        formatted_stocks = set()
        for code in stock_codes:
            formatted_code = format_stock_code(code)
            formatted_stocks.add(formatted_code)
        
        stocks = [{'code': code, 'name': ''} for code in formatted_stocks]
        
        return {
            "stocks": stocks
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交割单股票列表时发生错误: {str(e)}")