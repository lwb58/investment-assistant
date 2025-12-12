import sys
import os
import json

# 设置项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.stock import _hk_dupont_analysis_impl, _a_dupont_analysis_impl

def compare_dupont_implementations(stock_id):
    print(f"\n=== 比较 A股股票 {stock_id} 的港股和A股杜邦分析实现 ===")
    
    # 调用港股实现
    print("\n1. 调用港股杜邦分析实现 _hk_dupont_analysis_impl:")
    hk_result = _hk_dupont_analysis_impl(stock_id)
    print(f"   状态: {'成功' if hk_result.get('full_data') else '失败'}")
    if hk_result.get('error'):
        print(f"   错误信息: {hk_result['error']}")
    
    # 调用A股实现
    print("\n2. 调用A股杜邦分析实现 _a_dupont_analysis_impl:")
    a_result = _a_dupont_analysis_impl(stock_id)
    print(f"   状态: {'成功' if a_result.get('full_data') else '失败'}")
    if a_result.get('error'):
        print(f"   错误信息: {a_result['error']}")
    
    # 详细比较返回数据
    if hk_result.get('full_data') and a_result.get('full_data'):
        print(f"\n3. 数据对比:")
        
        # 比较数据条数
        print(f"   - 港股接口返回数据条数: {len(hk_result['full_data'])}")
        print(f"   - A股接口返回数据条数: {len(a_result['full_data'])}")
        
        # 比较报告期
        hk_dates = [item.get('report_date', item.get('报告期', '')) for item in hk_result['full_data']]
        a_dates = [item.get('报告期', '') for item in a_result['full_data']]
        print(f"   - 港股接口报告期: {hk_dates[:5]}...")
        print(f"   - A股接口报告期: {a_dates[:5]}...")
        
        # 比较字段名称
        if hk_result['full_data'] and a_result['full_data']:
            hk_fields = set(hk_result['full_data'][0].keys())
            a_fields = set(a_result['full_data'][0].keys())
            
            print(f"\n4. 字段对比:")
            print(f"   - 港股接口特有字段: {sorted(list(hk_fields - a_fields))[:10]}...")
            print(f"   - A股接口特有字段: {sorted(list(a_fields - hk_fields))[:10]}...")
            print(f"   - 共同字段: {sorted(list(hk_fields & a_fields))[:10]}...")
            
            # 比较关键指标值
            print(f"\n5. 关键指标对比 (最新报告期):")
            latest_hk = hk_result['full_data'][0] if hk_result['full_data'] else {}
            latest_a = a_result['full_data'][0] if a_result['full_data'] else {}
            
            # 映射关键指标字段名
            key_metrics = {
                '报告期': ['report_date', '报告期'],
                '净资产收益率': ['净资产收益率(%)', '净资产收益率'],
                '销售净利率': ['销售净利率(%)', '归属母公司股东的销售净利率'],
                '总资产周转率': ['总资产周转率(次)', '资产周转率(次)'],
                '权益乘数': ['权益乘数', '权益乘数']
            }
            
            for metric_name, (hk_field, a_field) in key_metrics.items():
                hk_value = latest_hk.get(hk_field, 'N/A')
                a_value = latest_a.get(a_field, 'N/A')
                print(f"   - {metric_name}: 港股={hk_value}, A股={a_value}")
    
    # 保存结果到文件
    with open(f'股票{stock_id}_港股杜邦结果.json', 'w', encoding='utf-8') as f:
        json.dump(hk_result, f, ensure_ascii=False, indent=2)
    
    with open(f'股票{stock_id}_A股杜邦结果.json', 'w', encoding='utf-8') as f:
        json.dump(a_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存到文件")

if __name__ == "__main__":
    stock_id = "603259"  # A股股票代码
    compare_dupont_implementations(stock_id)