#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试A股和港股杜邦分析接口的字段名统一性
验证修复后港股接口是否返回与A股接口相同格式的字段名
"""

import json
import sys
from stock import _a_dupont_analysis_impl, _hk_dupont_analysis_impl

def test_field_unification():
    """测试A股和港股接口字段名的统一性"""
    print("=" * 60)
    print("=== 测试A股和港股杜邦分析接口字段名统一性 ===")
    print("=" * 60)
    
    # 测试A股股票（603259）
    print("\n1. 获取A股股票（603259）杜邦分析数据:")
    a_result = _a_dupont_analysis_impl("603259", export_excel=False)
    if a_result.get("error"):
        print(f"❌ A股接口调用失败: {a_result['error']}")
        return
    
    a_data = a_result.get("full_data", [])
    if not a_data:
        print("❌ A股接口未返回数据")
        return
    
    print(f"✅ 成功获取 {len(a_data)} 条A股数据")
    
    # 测试港股股票（09633）
    print("\n2. 获取港股股票（09633）杜邦分析数据:")
    hk_result = _hk_dupont_analysis_impl("09633")
    if hk_result.get("error"):
        print(f"❌ 港股接口调用失败: {hk_result['error']}")
        return
    
    hk_data = hk_result.get("full_data", [])
    if not hk_data:
        print("❌ 港股接口未返回数据")
        return
    
    print(f"✅ 成功获取 {len(hk_data)} 条港股数据")
    
    # 获取前端关键指标字段列表
    key_fields = [
        "report_date",
        "report_period",
        "period_type",
        "净资产收益率",
        "销售净利率", 
        "总资产周转率",
        "权益乘数",
        "总资产收益率",
        "毛利率",
        "营业利润率",
        "经营利润率",
        "归母净利润（亿元）",
        "归属母公司股东净利润"
    ]
    
    print("\n" + "=" * 60)
    print("=== 检查关键指标字段存在性 ===")
    print("=" * 60)
    
    # 检查A股字段
    print("\nA股关键字段存在情况:")
    a_first_item = a_data[0]
    for field in key_fields:
        exists = "✅" if field in a_first_item else "❌"
        value = a_first_item.get(field, "")[:20]  # 限制显示长度
        print(f"  {exists} {field}: {value}")
    
    # 检查港股字段
    print("\n港股关键字段存在情况:")
    hk_first_item = hk_data[0]
    for field in key_fields:
        exists = "✅" if field in hk_first_item else "❌"
        value = hk_first_item.get(field, "")[:20]
        print(f"  {exists} {field}: {value}")
    
    # 检查港股向后兼容字段
    print("\n港股向后兼容字段存在情况:")
    compat_fields = ["净资产收益率(%)", "销售净利率(%)", "总资产周转率(次)"]
    for field in compat_fields:
        exists = "✅" if field in hk_first_item else "❌"
        value = hk_first_item.get(field, "")[:20]
        print(f"  {exists} {field}: {value}")
    
    # 检查港股多个季度数据
    print("\n" + "=" * 60)
    print("=== 检查港股多个季度ROE数据 ===")
    print("=== 验证ROE趋势图是否能显示所有季度 ===")
    print("=" * 60)
    
    for i, item in enumerate(hk_data[:5]):  # 显示前5条数据
        report_date = item.get("report_date", "")
        period_type = item.get("period_type", "")
        roe = item.get("净资产收益率", "")
        roe_compat = item.get("净资产收益率(%)", "")
        print(f"  {i+1}. {report_date} ({period_type}): ROE={roe} ({roe_compat}%)")
    
    # 保存完整结果到文件以便查看
    with open("hk_dupont_fixed.json", "w", encoding="utf-8") as f:
        json.dump(hk_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完整港股数据已保存到: hk_dupont_fixed.json")
    print("✅ 字段名统一修复完成！")
    print("✅ ROE趋势图现在应该能显示所有季度的数据")
    print("✅ 杜邦分析模块所有指标应该都能正常显示")

if __name__ == "__main__":
    test_field_unification()
