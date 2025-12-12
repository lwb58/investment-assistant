from stock import dupont_analysis

# 测试港股02367的杜邦分析接口
result = dupont_analysis('02367')
print('港股02367杜邦分析接口返回值:')
print('数据条数:', len(result.get('full_data', [])))
print('\n关键数据（报告期、归母净利润）:')
for item in result.get('full_data', []):
    print(f'报告期: {item.get("报告期")}, 归母净利润（亿元）: {item.get("归母净利润（亿元）")}, HOLDER_PROFIT: {item.get("HOLDER_PROFIT")}')

# 查看A股的情况作为对比
print('\n\nA股000001杜邦分析接口返回值:')
result_a = dupont_analysis('000001')
print('数据条数:', len(result_a.get('full_data', [])))
print('\n关键数据（报告期、归母净利润）:')
[print(f'报告期: {item.get("报告期")}, 归母净利润（亿元）: {item.get("归母净利润（亿元）")}') for item in result_a.get('full_data', [])[:3]]
