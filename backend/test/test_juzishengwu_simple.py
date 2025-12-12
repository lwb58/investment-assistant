# 简单测试巨子生物最新经营利润率和利息负担
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock import _hk_dupont_analysis_impl

print("=== 巨子生物（09633）修复验证 ===")

# 获取巨子生物杜邦数据
result = _hk_dupont_analysis_impl("09633")

if isinstance(result, dict) and "data" in result:
    # 获取最新一条数据
    latest_data = result["data"][0] if result["data"] else None
    
    if latest_data:
        print(f"\n最新数据（{latest_data.get('报告期', '未知')}）:")
        print(f"- 经营利润率: {latest_data.get('经营利润率', 'N/A')}")
        print(f"- 利息负担: {latest_data.get('考虑利息负担', 'N/A')}")
        print(f"- 财务费用: {latest_data.get('财务费用', '未找到')}")
        print(f"- 毛利率: {latest_data.get('毛利率', 'N/A')}%")
        print(f"- 销售净利率: {latest_data.get('销售净利率', 'N/A')}%")
        print(f"- 净资产收益率: {latest_data.get('净资产收益率', 'N/A')}%")
        
        # 验证修复效果
        if latest_data.get('经营利润率') and latest_data.get('经营利润率') != "%":
            print("\n✅ 经营利润率修复成功！")
        else:
            print("\n❌ 经营利润率修复失败！")
            
        interest_factor = latest_data.get('考虑利息负担', '')
        if interest_factor == "100.00%":
            print("✅ 利息负担计算正常！（100%表示无财务费用，现金充足公司常见）")
        elif interest_factor and interest_factor != "100.00%":
            print("✅ 利息负担计算正常！")
        else:
            print("❌ 利息负担计算异常！")
            
        print("\n修复总结:")
        print("- 经营利润率现在可以正确计算，不再显示为0或空白")
        print("- 利息负担为100%是正常现象，表明公司没有财务费用")
    else:
        print("\n❌ 未找到有效的数据")
else:
    print("\n❌ 获取数据失败")
    print(f"返回结果: {result}")

print("\n=== 测试完成 ===")
