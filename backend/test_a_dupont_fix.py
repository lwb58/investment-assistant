import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock import _a_dupont_analysis_impl

def test_a_dupont_net_profit_fix():
    """测试A股杜邦分析归母净利润单位转换修复"""
    print("=== A股杜邦分析归母净利润单位转换修复测试 ===")
    
    # 测试股票代码：603259（药明康德）
    stock_id = "603259"
    
    try:
        # 调用A股杜邦分析接口
        result = _a_dupont_analysis_impl(stock_id, export_excel=False)
        
        if result.get("error"):
            print(f"❌ 获取数据失败: {result.get('error')}")
            return
        
        full_data = result.get("full_data", [])
        if not full_data:
            print("❌ 未获取到有效数据")
            return
        
        print(f"✅ 成功获取 {len(full_data)} 条数据")
        
        # 打印前3条数据的归母净利润
        print("\n前3条数据的归母净利润（亿元）:")
        for i, item in enumerate(full_data[:3]):
            net_profit = item.get("归属母公司股东净利润", "-").strip()
            report_date = item.get("报告期", "-").strip()
            print(f"📅 {report_date}: {net_profit} 亿元")
            
            # 检查是否转换为了合理的数值范围
            try:
                if net_profit and net_profit != "-":
                    float_value = float(net_profit)
                    if float_value > 1000:
                        print(f"   ⚠️  警告：数值 {float_value} 可能仍然过大")
            except ValueError:
                pass
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_a_dupont_net_profit_fix()
