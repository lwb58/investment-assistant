import json
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入相关模块
from stock import process_hk_dupont_data

# 读取巨子生物的测试数据
file_path = "巨子_09633_dupont_test.json"

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

if "financial_data" in data:
    # 处理巨子生物的杜邦数据
    dupont_data = process_hk_dupont_data(data["financial_data"])
    
    print("=== 巨子生物杜邦分析结果 ===")
    for item in dupont_data[:3]:  # 只显示最近3条数据
        print(f"\n报告期: {item.get('报告期')}")
        print(f"ROE: {item.get('净资产收益率')}%")
        print(f"销售净利率: {item.get('销售净利率')}%")
        print(f"经营利润率: {item.get('经营利润率')}%")
        print(f"考虑税负因素: {item.get('考虑税负因素')}")
        print(f"考虑利息负担: {item.get('考虑利息负担')}")
        print(f"税负因素: {item.get('税负因素')}%")
        print(f"利息负担: {item.get('利息负担')}%")
        print("-" * 30)
    
    # 检查是否修复成功
    if dupont_data and dupont_data[0].get('经营利润率') != "0.00" and dupont_data[0].get('利息负担') != "100.00":
        print("\n✅ 修复成功！经营利润率和利息负担现在能正确显示了。")
    else:
        print("\n❌ 修复未生效，仍有问题需要解决。")
else:
    print("❌ 数据格式不正确，缺少 financial_data 字段。")
