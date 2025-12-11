import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.stock import dupont_analysis
from backend.stock import DupontAnalysisResponse

def test_hk_dupont_analysis():
    """测试港股杜邦分析方法"""
    print("开始测试港股杜邦分析方法...")
    
    # 测试的港股代码
    hk_stock_codes = [
        "02367",  # 巨子生物
        "00700",  # 腾讯控股
        "09988"   # 阿里巴巴-SW
    ]
    
    for stock_code in hk_stock_codes:
        print(f"\n{'='*60}")
        print(f"测试港股代码: {stock_code}")
        print(f"{'='*60}")
        
        try:
            # 调用杜邦分析方法
            result = dupont_analysis(stock_code)
            
            # 验证返回类型
            print(f"返回类型: {type(result)}")
            
            # 打印结果
            print(f"股票代码: {result['stock_id']}")
            print(f"错误信息: {result['error']}")
            
            # 检查是否有全量数据
            if result['full_data']:
                print(f"全量数据条数: {len(result['full_data'])}")
                print("\n前两条数据:")
                for i, item in enumerate(result['full_data'][:2]):
                    print(f"\n数据 {i+1}:")
                    print(f"  报告日期: {item.get('report_date', 'N/A')}")
                    print(f"  周期类型: {item.get('period_type', 'N/A')}")
                    print(f"  净资产收益率(%) : {item.get('净资产收益率(%)', 'N/A')}")
                    print(f"  销售净利率(%) : {item.get('销售净利率(%)', 'N/A')}")
                    print(f"  总资产周转率(次) : {item.get('总资产周转率(次)', 'N/A')}")
                    print(f"  权益乘数 : {item.get('权益乘数', 'N/A')}")
                    print(f"  总资产收益率(%) : {item.get('总资产收益率(%)', 'N/A')}")
                    print(f"  毛利率(%) : {item.get('毛利率(%)', 'N/A')}")
            else:
                print("❌ 未获取到全量数据")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    print(f"\n{'='*60}")
    print("港股杜邦分析方法测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_hk_dupont_analysis()
