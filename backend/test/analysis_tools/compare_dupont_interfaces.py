import sys
import os
sys.path.append(r'D:\yypt\xingziyuan\investment-assistant\backend')
from stock import dupont_analysis, _hk_dupont_analysis_impl, _a_dupont_analysis_impl
import json

# 测试股票代码
# A股股票
test_a_stock = '000001'  # 平安银行
# 港股股票
test_hk_stock = '02367'  # 药明生物

def analyze_hk_interface_for_a_stock(a_stock_code):
    """测试港股接口对A股股票的处理"""
    print(f"\n=== 测试港股接口对A股股票 {a_stock_code} 的处理 ===")
    
    # 直接调用港股实现函数
    print("\n1. 直接调用港股实现函数:")
    try:
        hk_result = _hk_dupont_analysis_impl(a_stock_code)
        if hk_result.get('error'):
            print(f"   港股接口返回错误: {hk_result['error']}")
        else:
            print(f"   港股接口成功返回数据")
            print(f"   港股接口返回数据条数: {len(hk_result.get('full_data', []))}")
            if hk_result.get('full_data'):
                print(f"   港股接口返回的报告期:")
                for item in hk_result['full_data'][:3]:
                    print(f"     - {item.get('报告期')}")
    except Exception as e:
        print(f"   港股接口调用失败: {e}")
    
    # 尝试构造港股格式的股票代码（添加.HK后缀）
    print("\n2. 尝试构造港股格式的股票代码:")
    try:
        # 手动构造请求URL，模拟港股接口调用
        from stock import fetch_url
        secucode = f"{a_stock_code}.HK"
        url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_MAININDICATOR&columns=ALL&quoteColumns=&filter=(SECUCODE%3D%22{secucode}%22)&pageNumber=1&pageSize=20&sortTypes=-1&sortColumns=STD_REPORT_DATE&source=F10&client=PC&v=040146104118736425"
        
        print(f"   尝试访问URL: {url}")
        data = fetch_url(url, timeout=10, retry=1)
        
        if data:
            print(f"   请求成功，响应状态: {data.get('result') is not None}")
            if data.get('result'):
                print(f"   返回数据条数: {len(data['result'].get('data', []))}")
                if data['result'].get('data'):
                    print(f"   实际返回的股票代码: {data['result']['data'][0].get('SECURITY_CODE')}")
                    print(f"   实际返回的股票名称: {data['result']['data'][0].get('SECURITY_NAME_ABBR')}")
        else:
            print(f"   请求失败，未获取到数据")
            
    except Exception as e:
        print(f"   测试失败: {e}")

def compare_a_stock_interfaces(a_stock_code):
    """比较A股股票使用两个不同接口的结果差异"""
    print(f"\n=== 比较A股股票 {a_stock_code} 的两个杜邦分析接口 ===")
    
    # 使用A股接口
    print("\n1. 使用A股杜邦分析接口:")
    try:
        a_result = _a_dupont_analysis_impl(a_stock_code)
        print(f"   A股接口返回数据条数: {len(a_result.get('full_data', []))}")
        if a_result.get('full_data'):
            print(f"   A股接口返回的报告期:")
            for item in a_result['full_data'][:5]:  # 只显示前5条
                print(f"     - {item.get('报告期')}")
            
            # 显示关键财务指标
            print(f"\n   A股接口返回的关键财务指标 (最新一期):")
            latest_a = a_result['full_data'][0]
            print(f"     归母净利润（亿元）: {latest_a.get('归母净利润（亿元）')}")
            print(f"     净资产收益率: {latest_a.get('净资产收益率')}")
            print(f"     营业总收入: {latest_a.get('营业总收入')}")
            print(f"     销售净利率(%): {latest_a.get('销售净利率(%)')}")
            print(f"     总资产周转率(次): {latest_a.get('总资产周转率(次)')}")
            print(f"     权益乘数: {latest_a.get('权益乘数')}")
    except Exception as e:
        print(f"   A股接口调用失败: {e}")
    
    # 使用统一接口
    print("\n2. 使用统一dupont_analysis接口:")
    try:
        result = dupont_analysis(a_stock_code)
        print(f"   统一接口返回数据条数: {len(result.get('full_data', []))}")
        if result.get('full_data'):
            print(f"   统一接口返回的报告期:")
            for item in result['full_data'][:3]:
                print(f"     - {item.get('报告期')}")
    except Exception as e:
        print(f"   统一接口调用失败: {e}")

def test_hk_stock_normal_operation():
    """测试港股接口对正常港股股票的处理"""
    print(f"\n=== 测试港股接口对正常港股股票 {test_hk_stock} 的处理 ===")
    
    try:
        # 使用统一接口（应该自动选择港股处理）
        print("\n1. 使用统一接口:")
        result = dupont_analysis(test_hk_stock)
        print(f"   统一接口返回数据条数: {len(result.get('full_data', []))}")
        if result.get('full_data'):
            print(f"   统一接口返回的报告期:")
            for item in result['full_data'][:3]:
                print(f"     - {item.get('报告期')}")
        
        # 直接调用港股实现函数
        print("\n2. 直接调用港股实现函数:")
        hk_result = _hk_dupont_analysis_impl(test_hk_stock)
        print(f"   港股实现函数返回数据条数: {len(hk_result.get('full_data', []))}")
        if hk_result.get('full_data'):
            print(f"   港股实现函数返回的报告期:")
            for item in hk_result['full_data'][:3]:
                print(f"     - {item.get('报告期')}")
    except Exception as e:
        print(f"   测试失败: {e}")

def compare_interface_structures():
    """比较两个接口返回的数据结构差异"""
    print("\n=== 比较两个接口的数据结构 ===")
    
    print("\n1. 港股接口数据结构特点:")
    print("   - 数据源: 东方财富网港股API")
    print("   - 数据格式: JSON格式，包含完整的报告期信息")
    print("   - 报告期: 完整日期格式 (如2025-09-30)")
    print("   - 字段命名: 同时支持A股字段名和港股API原始字段")
    print("   - 数据类型: 数字统一转换为字符串格式")
    
    print("\n2. A股接口数据结构特点:")
    print("   - 数据源: 新浪财经A股杜邦分析页面")
    print("   - 数据格式: 解析HTML表格，提取结构化数据")
    print("   - 报告期: 完整日期格式 (如2025-09-30)")
    print("   - 字段命名: A股传统财务指标命名")
    print("   - 数据类型: 数字统一转换为字符串格式")
    
    print("\n3. 共同特点:")
    print("   - 保持相同的响应格式，便于前端统一处理")
    print("   - 都包含核心杜邦分析指标")
    print("   - 都支持报告期和周期类型")

def main():
    """运行所有测试用例"""
    print("开始比较A股和港股杜邦分析接口")
    
    # 1. 测试港股接口对正常港股股票的处理
    test_hk_stock_normal_operation()
    
    # 2. 测试港股接口对A股股票的处理
    analyze_hk_interface_for_a_stock(test_a_stock)
    
    # 3. 比较A股股票使用两个不同接口的结果
    compare_a_stock_interfaces(test_a_stock)
    
    # 4. 比较两个接口的数据结构
    compare_interface_structures()
    
    print("\n=== 所有测试完成 ===")

if __name__ == "__main__":
    main()