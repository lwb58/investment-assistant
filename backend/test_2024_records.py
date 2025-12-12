import sys
sys.path.append(r'D:\yypt\xingziyuan\investment-assistant\backend')
from stock import dupont_analysis

# 测试港股02367
result = dupont_analysis('02367')
print('港股02367杜邦分析数据：')
print(f'数据总条数: {len(result.get("full_data", []))}')

# 筛选2024年的记录
year_2024 = [item for item in result.get("full_data", []) if "2024" in item.get("报告期")]
print('\n2024年记录：')
for item in year_2024:
    print(f'  报告期: {item.get("报告期")}')
print(f'2024年总计：{len(year_2024)}条')

# 打印所有报告期
print('\n所有报告期：')
for item in result.get("full_data", []):
    print(f'  {item.get("报告期")}')