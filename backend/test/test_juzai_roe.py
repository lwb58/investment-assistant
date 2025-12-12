import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock import dupont_analysis, _hk_dupont_analysis_impl, _a_dupont_analysis_impl
import json

def test_juzai_dupont_data():
    """测试巨子（港股）的杜邦分析数据"""
    print("=== 巨子（港股）杜邦分析数据测试 ===")
    
    # 巨子港股代码：09633
    hk_stock_id = "09633"
    
    try:
        # 调用港股杜邦分析接口
        print(f"\n1. 调用港股杜邦分析接口（09633）:")
        result_hk = _hk_dupont_analysis_impl(hk_stock_id, export_excel=False)
        
        if result_hk.get("error"):
            print(f"❌ 获取港股数据失败: {result_hk.get('error')}")
        else:
            full_data_hk = result_hk.get("full_data", [])
            print(f"✅ 成功获取 {len(full_data_hk)} 条港股数据")
            
            # 保存港股数据到文件
            with open("巨子_09633_dupont_test.json", "w", encoding="utf-8") as f:
                json.dump(result_hk, f, ensure_ascii=False, indent=2)
            print(f"📁 港股数据已保存到：巨子_09633_dupont_test.json")
            
            # 打印前3条数据的核心指标
            print("\n港股前3条数据核心指标:")
            for i, item in enumerate(full_data_hk[:3]):
                print(f"\n📅 第{i+1}条数据（{item.get('报告期', '-')}）:")
                print(f"   净资产收益率: {item.get('净资产收益率(%)', '-')}")
                print(f"   销售净利率: {item.get('销售净利率(%)', '-')}")
                print(f"   总资产周转率: {item.get('总资产周转率(次)', '-')}")
                print(f"   权益乘数: {item.get('权益乘数', '-')}")
                print(f"   归母净利润（亿元）: {item.get('归母净利润（亿元）', '-')}")
                
                # 打印所有ROE相关字段
                print("\n   ROE相关原始字段:")
                roe_fields = [k for k in item.keys() if "ROE" in k.upper() or "净资产收益率" in k]
                for field in roe_fields:
                    print(f"     {field}: {item.get(field, '-')}")
    
    except Exception as e:
        print(f"❌ 港股测试发生错误: {str(e)}")

    # 对比A股数据
    print("\n" + "="*50)
    print("=== A股对比测试 ===")
    
    # 选择一个A股股票进行对比
    a_stock_id = "603259"  # 药明康德
    
    try:
        # 调用A股杜邦分析接口
        print(f"\n2. 调用A股杜邦分析接口（{a_stock_id}）:")
        result_a = _a_dupont_analysis_impl(a_stock_id, export_excel=False)
        
        if result_a.get("error"):
            print(f"❌ 获取A股数据失败: {result_a.get('error')}")
        else:
            full_data_a = result_a.get("full_data", [])
            print(f"✅ 成功获取 {len(full_data_a)} 条A股数据")
            
            # 打印前3条数据的核心指标
            print("\nA股前3条数据核心指标:")
            for i, item in enumerate(full_data_a[:3]):
                print(f"\n📅 第{i+1}条数据（{item.get('报告期', '-')}）:")
                print(f"   净资产收益率: {item.get('净资产收益率', '-')}")
                print(f"   销售净利率: {item.get('归属母公司股东的销售净利率', '-')}")
                print(f"   总资产周转率: {item.get('资产周转率(次)', '-')}")
                print(f"   权益乘数: {item.get('权益乘数', '-')}")
                print(f"   归母净利润（亿元）: {item.get('归属母公司股东净利润', '-')}")
    
    except Exception as e:
        print(f"❌ A股测试发生错误: {str(e)}")

if __name__ == "__main__":
    test_juzai_dupont_data()
