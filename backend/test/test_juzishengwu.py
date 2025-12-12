import json
import os

# 读取巨子生物的财务数据
file_path = "d:\\yypt\\xingziyuan\\investment-assistant\\backend\\巨子_09633_dupont_test.json"

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 查看数据结构
print("=== 巨子生物财务数据结构 ===")
for key, value in data.items():
    if isinstance(value, dict):
        print(f"{key}: {list(value.keys())[:5]}...")
    else:
        print(f"{key}: {value}")

# 查看财务数据的详细字段
if "financial_data" in data:
    print("\n=== 财务数据字段 ===")
    financial_data = data["financial_data"]
    for key, value in financial_data.items():
        print(f"{key}: {value}")

# 查看是否有TAX_EBT和PRETAX_PROFIT字段
print("\n=== 关键字段检查 ===")
print(f"TAX_EBT: {financial_data.get('TAX_EBT')}")
print(f"PRETAX_PROFIT: {financial_data.get('PRETAX_PROFIT')}")
print(f"INCOME_TAX: {financial_data.get('INCOME_TAX')}")
print(f"TAX_EXPENSE: {financial_data.get('TAX_EXPENSE')}")
print(f"OPERATE_PROFIT: {financial_data.get('OPERATE_PROFIT')}")

# 手动计算税负因素
from stock import calculate_tax_factor

print("\n=== 税负因素计算 ===")
tax_factor = calculate_tax_factor(financial_data)
print(f"计算结果: {tax_factor}")
