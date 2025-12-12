from stock import calculate_tax_factor

# 模拟巨子生物的财务数据
financial_data = {
    "TAX_EBT": 16.395924034818,  # 所得税占税前利润比例
    "PRETAX_PROFIT": 4434970000,  # 利润总额
    "OPERATE_PROFIT": None,  # 营业利润
    "NET_PROFIT": 3713410000,  # 净利润
    "INCOME_TAX": None,  # 所得税费用（缺失）
    "TAX_EXPENSE": None  # 所得税费用（缺失）
}

# 测试税负因素计算
tax_factor = calculate_tax_factor(financial_data)
print(f"税负因素计算结果: {tax_factor}")
print(f"预期结果: 约83.6% (100 - 16.3959)")
