# 专门测试巨子生物（09633）的经营利润率和利息负担修复
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock import _hk_dupont_analysis_impl

print("=== 测试巨子生物（09633）经营利润率和利息负担修复 ===")

# 调用巨子生物的杜邦分析
juzishengwu_data = _hk_dupont_analysis_impl("09633")

# 检查返回的数据类型
print(f"\n返回数据类型: {type(juzishengwu_data)}")

if isinstance(juzishengwu_data, list):
    print(f"总数据条数: {len(juzishengwu_data)}")
    
    if juzishengwu_data:
        # 显示最新的几条数据
        for i, item in enumerate(juzishengwu_data[:3]):
            print(f"\n数据 {i+1}:")
            print(f"  报告期: {item.get('报告期', 'N/A')}")
            print(f"  周期类型: {item.get('周期类型', 'N/A')}")
            print(f"  净资产收益率: {item.get('净资产收益率', 'N/A')}%")
            print(f"  销售净利率: {item.get('销售净利率', 'N/A')}%")
            print(f"  总资产周转率: {item.get('总资产周转率', 'N/A')}次")
            print(f"  权益乘数: {item.get('权益乘数', 'N/A')}")
            print(f"  总资产收益率: {item.get('总资产收益率', 'N/A')}%")
            print(f"  毛利率: {item.get('毛利率', 'N/A')}%")
            print(f"  营业利润率: {item.get('营业利润率', 'N/A')}%")
            print(f"  经营利润率: {item.get('经营利润率', 'N/A')}")
            print(f"  利息负担: {item.get('考虑利息负担', 'N/A')}%")
            print(f"  税负因素: {item.get('考虑税负因素', 'N/A')}%")
            
            # 检查关键指标
            if item.get('经营利润率') and item.get('经营利润率') != "%":
                print("  ✅ 经营利润率修复成功！")
            else:
                print("  ❌ 经营利润率仍有问题！")
                
            interest_factor = item.get('考虑利息负担', '')
            if interest_factor and interest_factor != "100.00%" or (interest_factor == "100.00%" and item.get('财务费用', '0') == '0'):
                print("  ✅ 利息负担计算正常！")
            else:
                print("  ❌ 利息负担可能有问题！")
elif isinstance(juzishengwu_data, dict):
    # 如果返回的是字典类型
    print("\n数据结构:")
    for key, value in juzishengwu_data.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for subkey, subvalue in value.items():
                print(f"  {subkey}: {subvalue}")
        else:
            print(f"{key}: {value}")
else:
    print(f"\n未知的数据类型: {type(juzishengwu_data)}")
    print(f"数据内容: {juzishengwu_data}")

print("\n=== 测试完成 ===")
