import json
import pandas as pd
from stock import _hk_dupont_analysis_impl, _a_dupont_analysis_impl, generate_dupont_chart
from fastapi import Query

print("=== 港股接口字段统一修复测试 ===")
print()

# 测试1：港股接口字段统一验证
print("1. 测试港股接口（巨子生物，09633）字段统一：")
try:
    hk_data = _hk_dupont_analysis_impl("09633")
    if hk_data.get("full_data"):
        print(f"   ✓ 成功获取 {len(hk_data['full_data'])} 条数据")
        
        # 检查统一字段名
        first_item = hk_data['full_data'][0]
        required_fields = ["净资产收益率", "销售净利率", "总资产周转率", "权益乘数"]
        for field in required_fields:
            if field in first_item:
                print(f"   ✓ 包含统一字段名：{field} = {first_item[field]}")
            else:
                print(f"   ✗ 缺少统一字段名：{field}")
        
        # 检查兼容字段名
        compatible_fields = ["净资产收益率(%)", "销售净利率(%)", "总资产周转率(次)"]
        for field in compatible_fields:
            if field in first_item:
                print(f"   ✓ 保留兼容字段名：{field} = {first_item[field]}")
    else:
        print(f"   ✗ 获取数据失败：{hk_data.get('error')}")
except Exception as e:
    print(f"   ✗ 测试失败：{str(e)}")

print()

# 测试2：A股接口对比验证
print("2. 测试A股接口（603259）字段格式：")
try:
    a_data = _a_dupont_analysis_impl("603259")
    if a_data.get("full_data"):
        print(f"   ✓ 成功获取 {len(a_data['full_data'])} 条数据")
        
        first_item = a_data['full_data'][0]
        required_fields = ["净资产收益率", "销售净利率", "总资产周转率", "权益乘数"]
        for field in required_fields:
            if field in first_item:
                print(f"   ✓ 包含字段名：{field} = {first_item[field]}")
    else:
        print(f"   ✗ 获取数据失败：{a_data.get('error')}")
except Exception as e:
    print(f"   ✗ 测试失败：{str(e)}")

print()

# 测试3：图表生成逻辑验证
print("3. 测试图表生成逻辑：")
try:
    # 模拟请求参数
    stock_id = "09633"
    factor_type = "all"
    cycle_type = "all"
    
    # 测试图表生成的核心逻辑（不实际生成图表，只测试数据处理）
    from stock import dupont_analysis
    
    # 获取杜邦分析数据
    dupont_data = dupont_analysis(stock_id, export_excel=False)
    if dupont_data.get("error") or not dupont_data.get("full_data"):
        print(f"   ✗ 获取杜邦分析数据失败：{dupont_data.get('error')}")
    else:
        print(f"   ✓ 成功获取杜邦分析数据：{len(dupont_data['full_data'])} 条")
        
        # 转换为DataFrame模拟图表生成的数据处理
        df = pd.DataFrame(dupont_data["full_data"])
        df.columns = df.columns.str.strip()
        
        # 测试字段处理逻辑
        indicator_map = {
            "roe": {"name": "净资产收益率", "color": "#409eff"},
            "net_profit_margin": {"name": "销售净利率(%)", "color": "#67c23a"},
            "asset_turnover": {"name": "资产周转率(次)", "color": "#faad14"},
            "equity_multiplier": {"name": "权益乘数", "color": "#f5222d"}
        }
        
        # 应用修复后的字段处理逻辑
        if "净资产收益率" in df.columns:
            indicator_map["roe"]["name"] = "净资产收益率"
        elif "净资产收益率(%)" in df.columns:
            indicator_map["roe"]["name"] = "净资产收益率(%)"
        
        if "销售净利率" in df.columns:
            indicator_map["net_profit_margin"]["name"] = "销售净利率"
        elif "销售净利率(%)" in df.columns:
            indicator_map["net_profit_margin"]["name"] = "销售净利率(%)"
        
        if "总资产周转率" in df.columns:
            indicator_map["asset_turnover"]["name"] = "总资产周转率"
        elif "总资产周转率(次)" in df.columns:
            indicator_map["asset_turnover"]["name"] = "总资产周转率(次)"
        elif "资产周转率(次)" in df.columns:
            indicator_map["asset_turnover"]["name"] = "资产周转率(次)"
        
        print("   ✓ 字段处理逻辑验证通过")
        for key, info in indicator_map.items():
            if info["name"] in df.columns:
                print(f"   ✓ 指标 {info['name']} 可以在数据中找到")
            else:
                print(f"   ✗ 指标 {info['name']} 无法在数据中找到")
    
except Exception as e:
    print(f"   ✗ 测试失败：{str(e)}")

print()
print("=== 测试完成 ===")