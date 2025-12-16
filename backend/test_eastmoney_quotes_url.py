#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试get_stock_quotes_from_eastmoney方法并获取URL返回值
"""

import sys
import os
import json
import requests

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock import get_stock_quotes_from_eastmoney, validate_stock_code

def test_get_stock_quotes_from_eastmoney(stock_code):
    """
    测试get_stock_quotes_from_eastmoney方法并获取URL返回值
    
    Args:
        stock_code: 股票代码（如"600036"、"02367"）
    """
    print(f"=== 测试get_stock_quotes_from_eastmoney方法 ===")
    print(f"测试股票代码: {stock_code}")
    print("=" * 60)
    
    # 首先，我们模拟方法内部构造URL的过程，以便获取完整的URL
    market = validate_stock_code(stock_code)
    print(f"检测到的市场类型: {market}")
    
    if not market:
        print(f"无效的股票代码: {stock_code}")
        return
    
    # 构造东方财富接口的secid参数
    if market == "rt_hk":
        secid = f"116.{stock_code}"
    elif market == "sh":
        secid = f"1.{stock_code}"
    elif market == "sz":
        secid = f"0.{stock_code}"
    elif market == "bj":
        secid = f"1.{stock_code}"
    else:
        print(f"不支持的市场类型: {market}")
        return
    
    # 构造完整的东方财富行情接口URL
    eastmoney_url = f"https://push2.eastmoney.com/api/qt/stock/get?fields=f57%2Cf58%2Cf43%2Cf44%2Cf45%2Cf46%2Cf47%2Cf48%2Cf50%2Cf164%2Cf168%2Cf170%2Cf171%2Cf179%2Cf183&secid={secid}&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&wbp2u=%7C0%7C0%7C0%7Cweb&v=09371029070054959"
    
    print(f"\n1. 完整的东方财富API URL:")
    print(eastmoney_url)
    print("\n" + "=" * 60)
    
    # 直接请求这个URL，获取原始返回值
    try:
        print("2. 发送请求到东方财富API...")
        response = requests.get(eastmoney_url, timeout=10)
        print(f"   响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            raw_data = response.json()
            print("\n3. 东方财富API原始返回值:")
            print(json.dumps(raw_data, indent=2, ensure_ascii=False))
            print("\n" + "=" * 60)
            
            # 调用实际方法获取处理后的结果
            print("4. 调用get_stock_quotes_from_eastmoney方法获取处理后的结果:")
            result = get_stock_quotes_from_eastmoney(stock_code)
            
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
                print("\n" + "=" * 60)
                print("5. 测试总结:")
                print("   ✓ 成功获取东方财富API URL和返回值")
                print("   ✓ 成功调用get_stock_quotes_from_eastmoney方法")
                print(f"   ✓ 处理后的当前价格: {result['coreQuotes']['currentPrice']}")
                print(f"   ✓ 处理后的涨跌幅: {result['coreQuotes']['changePercent']}%")
            else:
                print("   ✗ 调用方法失败")
        else:
            print(f"   ✗ 请求失败，状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except Exception as e:
        print(f"   ✗ 请求异常: {str(e)}")

if __name__ == "__main__":
    # 测试A股
    print("\n" + "=" * 80)
    print("测试A股股票: 600036 (招商银行)")
    print("=" * 80)
    test_get_stock_quotes_from_eastmoney("600036")
    
    # 测试港股
    print("\n" + "=" * 80)
    print("测试港股股票: 02367 (巨子生物)")
    print("=" * 80)
    test_get_stock_quotes_from_eastmoney("02367")