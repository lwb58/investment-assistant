#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试集成后的东方财富行情接口
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock import get_stock_quotes

def test_stock_quotes(stock_code):
    """测试获取股票行情数据"""
    print(f"\n=== 测试股票 {stock_code} 的行情数据 ===")
    
    try:
        data = get_stock_quotes(stock_code)
        
        if data:
            print(f"\n1. 基础信息:")
            print(f"   股票代码: {data['baseInfo']['stockCode']}")
            print(f"   市场: {data['baseInfo']['market']}")
            print(f"   股票名称: {data['baseInfo']['stockName']}")
            print(f"   行业: {data['baseInfo']['industry']}")
            
            print(f"\n2. 核心行情数据:")
            core_quotes = data['coreQuotes']
            print(f"   当前价格: {core_quotes.get('currentPrice', '--')}")
            print(f"   今开: {core_quotes.get('openPrice', '--')}")
            print(f"   昨收: {core_quotes.get('prevClosePrice', '--')}")
            print(f"   最高: {core_quotes.get('highPrice', '--')}")
            print(f"   最低: {core_quotes.get('lowPrice', '--')}")
            print(f"   成交量: {core_quotes.get('volume', '--')}")
            print(f"   成交额: {core_quotes.get('amount', '--')}")
            print(f"   涨跌额: {core_quotes.get('priceChange', '--')}")
            print(f"   涨跌幅: {core_quotes.get('changePercent', '--')}%")
            print(f"   换手率: {core_quotes.get('turnoverRate', '--')}%")
            print(f"   市盈率(TTM): {core_quotes.get('pe', '--')}")
            print(f"   总市值: {core_quotes.get('marketCap', '--')}")
            
            print(f"\n3. 数据有效性:")
            print(f"   是否有效: {data['dataValidity']['isValid']}")
            print(f"   原因: {data['dataValidity']['reason']}")
            
            print(f"\n测试成功！")
        else:
            print("\n测试失败: 获取行情数据返回None")
            
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 测试A股
    test_stock_quotes("603259")  # 药明康德
    
    # 测试港股
    test_stock_quotes("09633")  # 农夫山泉