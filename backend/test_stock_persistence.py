import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_all_stocks

print("测试股票数据持久化...")

# 调用get_all_stocks函数获取股票数据
stocks = get_all_stocks()

print(f"从数据库获取到的股票数量: {len(stocks)}")

if stocks:
    print("股票数据详情:")
    for stock in stocks:
        print(f"股票代码: {stock['stockCode']}, 股票名称: {stock['stockName']}")
        print(f"  - 添加时间: {stock['addTime']}")
        print(f"  - 备注: {stock['remark']}")
        print(f"  - 是否持有: {stock['isHold']}")
        print(f"  - 行业: {stock['industry']}")
        print()
else:
    print("警告: 没有从数据库获取到任何股票数据")