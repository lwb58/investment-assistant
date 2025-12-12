import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.stock import _get_hk_stock_financial_data

def test_hk_mllsj_data():
    """测试港股财务数据的mllsj是否返回多个季度数据"""
    print("开始测试港股财务数据的mllsj返回多个季度数据...")
    
    # 测试的港股代码
    hk_stock_codes = [
        "02367",  # 巨子生物
        "00700"   # 腾讯控股
    ]
    
    for stock_code in hk_stock_codes:
        print(f"\n{'='*60}")
        print(f"测试港股代码: {stock_code}")
        print(f"{'='*60}")
        
        try:
            # 调用港股财务数据函数
            financial_data = _get_hk_stock_financial_data(stock_code)
            
            # 检查返回的数据结构
            print(f"返回数据类型: {type(financial_data)}")
            print(f"包含的年份数据: {list(financial_data.keys())}")
            
            # 检查mllsj数据
            if 'mllsj' in financial_data:
                mllsj_data = financial_data['mllsj']
                print(f"\nmllsj数据包含的报告期数量: {len(mllsj_data)}")
                
                # 按报告日期降序排列
                sorted_report_dates = sorted(mllsj_data.keys(), reverse=True)
                print("\n按时间降序排列的报告期:")
                for i, report_date in enumerate(sorted_report_dates[:5]):  # 只显示前5个
                    data = mllsj_data[report_date]
                    print(f"  {i+1}. {report_date} - 毛利率: {data['mll']}%, 净利率: {data['xsjll']}%")
            else:
                print("\n❌ 未找到mllsj数据")
            
        except Exception as e:
            print(f"\n❌ 测试失败: {str(e)}")
    
    print(f"\n{'='*60}")
    print("港股财务数据mllsj测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_hk_mllsj_data()
