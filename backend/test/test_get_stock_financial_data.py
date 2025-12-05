import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util import DataSource

if __name__ == "__main__":
    result = DataSource.get_stock_financial_data("002920")
    print("测试结果:")
    print(result)