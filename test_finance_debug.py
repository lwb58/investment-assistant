# -*- coding: utf-8 -*-
"""测试财务数据获取函数的调试脚本"""
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# 导入工具模块
import requests
import json
from backend.util import DataSource

# 直接测试字段匹配逻辑
print("=== 直接字段匹配测试 ===")

# 测试数据
mock_items = [
    {'item_field': 'BIZTOTINCO', 'item_title': '营业总收入', 'item_value': '64253607.510000'},
    {'item_field': 'BIZINCO', 'item_title': '营业收入', 'item_value': '64253607.510000'},
    {'item_field': 'TOTPROFIT', 'item_title': '利润总额', 'item_value': '-70547975.550000'},
    {'item_field': 'INCOTAXEXPE', 'item_title': '所得税费用', 'item_value': '4123566.630000'},
    {'item_field': 'BASICEPS', 'item_title': '基本每股收益', 'item_value': '-0.110000'},
    {'item_field': 'NETPROFIT', 'item_title': '净利润', 'item_value': '-74671542.180000'}
]

# 测试字段匹配
finance_data = {
    "revenue": "0.00",
    "revenueGrowth": "0.0",
    "netProfit": "0.00",
    "netProfitGrowth": "0.0",
    "eps": "0.00",
    "roe": "0.0",
    "debtRatio": "0.0"
}

total_profit = None
income_tax = None

for item in mock_items:
    field = item['item_field']
    title = item['item_title']
    value = item.get('item_value', '0.00')
    
    print(f"测试字段: {field} - {title} = {value}")
    
    # 直接匹配字段名
    if field == "BASICEPS" and value:
        finance_data["eps"] = value
        print(f"  ✅ 设置基本每股收益: {value}")
    elif (field == "BIZINCO" or field == "BIZTOTINCO") and value:
        finance_data["revenue"] = value
        print(f"  ✅ 设置营业总收入: {value}")
    elif field == "TOTPROFIT" and value:
        total_profit = float(value) if value else 0.0
        print(f"  ✅ 设置利润总额: {value}")
    elif field == "INCOTAXEXPE" and value:
        income_tax = float(value) if value else 0.0
        print(f"  ✅ 设置所得税费用: {value}")
    elif field == "NETPROFIT" and value:
        finance_data["netProfit"] = value
        print(f"  ✅ 设置净利润: {value}")

# 计算净利润
if "netProfit" not in finance_data and total_profit is not None:
    if income_tax is not None:
        net_profit = total_profit - income_tax
        finance_data["netProfit"] = f"{net_profit:.2f}"
        print(f"  ✅ 计算净利润 (利润总额 - 所得税费用): {finance_data['netProfit']}")
    else:
        finance_data["netProfit"] = f"{total_profit:.2f}"
        print(f"  ✅ 使用利润总额作为净利润: {finance_data['netProfit']}")

print(f"\n最终测试结果: {finance_data}")

# 原始测试
print("\n" + "="*50)
print("=== 原始util.py测试 ===")
stock_code = "000001"
finance_data = DataSource.get_stock_financial_data(stock_code)

# 打印结果
print("\n" + "="*50)
print(f"最终财务数据获取结果:")
print(finance_data)
print("="*50)
print("测试结束")
