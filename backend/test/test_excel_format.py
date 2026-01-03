import pandas as pd
import os
import glob

# 定义交割单文件目录
TRANSACTION_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../file/trans')

def test_excel_format():
    """测试Excel文件格式，分析所有交割单文件的列名和数据结构"""
    # 获取目录下所有Excel文件（包括子目录）
    excel_files = glob.glob(os.path.join(TRANSACTION_FILES_DIR, "**", "*.xlsx"), recursive=True) + glob.glob(os.path.join(TRANSACTION_FILES_DIR, "**", "*.xls"), recursive=True)
    
    if not excel_files:
        print("未找到任何交割单Excel文件")
        return
    
    print("开始分析Excel文件格式...")
    print("=" * 50)
    
    # 收集所有文件的列信息
    all_columns = []
    
    for file_path in excel_files:
        try:
            print(f"\n文件: {os.path.basename(file_path)}")
            print("-" * 30)
            
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 去除列名中的空格
            df.columns = df.columns.str.strip()
            
            # 打印列名
            print("列名:", list(df.columns))
            all_columns.extend(list(df.columns))
            
            # 打印前几行数据样例
            print("\n数据样例:")
            print(df.head(3))
            
            # 打印数据类型
            print("\n数据类型:")
            print(df.dtypes)
            
        except Exception as e:
            print(f"处理文件时出错: {str(e)}")
    
    print("\n" + "=" * 50)
    print("所有文件中出现的列名统计:")
    
    # 统计所有列名的出现频率
    from collections import Counter
    column_counter = Counter(all_columns)
    
    for column, count in column_counter.most_common():
        print(f"{column}: 出现 {count} 次")

if __name__ == "__main__":
    test_excel_format()