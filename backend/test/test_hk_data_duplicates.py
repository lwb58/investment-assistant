import pandas as pd
from stock import _hk_dupont_analysis_impl

print("=== 港股数据重复检查测试 ===")
print()

try:
    # 获取港股数据
    hk_data = _hk_dupont_analysis_impl("09633")
    if hk_data.get("full_data"):
        print(f"获取到 {len(hk_data['full_data'])} 条数据")
        
        # 转换为DataFrame
        df = pd.DataFrame(hk_data['full_data'])
        
        # 检查基本信息
        print(f"\n数据列：{list(df.columns)}")
        print(f"\n数据摘要：")
        print(df[['报告期', '周期类型', '净资产收益率', '销售净利率', '总资产周转率', '权益乘数']].head())
        
        # 检查重复项
        print(f"\n重复检查：")
        
        # 检查报告期重复
        duplicate_dates = df[df.duplicated('报告期', keep=False)]
        if not duplicate_dates.empty:
            print(f"报告期有重复：")
            print(duplicate_dates[['报告期', '周期类型']])
        else:
            print("报告期没有重复")
            
        # 检查报告期+周期类型组合重复
        duplicate_combinations = df[df.duplicated(['报告期', '周期类型'], keep=False)]
        if not duplicate_combinations.empty:
            print(f"\n报告期+周期类型组合有重复：")
            print(duplicate_combinations[['报告期', '周期类型']])
        else:
            print("报告期+周期类型组合没有重复")
            
        # 检查索引重复
        df_reset = df.reset_index(drop=True)
        if df_reset.index.duplicated().any():
            print("\n索引有重复")
        else:
            print("\n索引没有重复")
            
        # 检查字段名重复
        if df.columns.duplicated().any():
            print("\n字段名有重复")
            print(df.columns[df.columns.duplicated()])
        else:
            print("\n字段名没有重复")
            
        # 打印所有数据的报告期和周期类型
        print(f"\n所有数据的报告期和周期类型：")
        for index, row in df.iterrows():
            print(f"{row['报告期']} - {row['周期类型']}")
            
    else:
        print(f"获取数据失败：{hk_data.get('error')}")
except Exception as e:
    print(f"测试失败：{str(e)}")
    import traceback
    traceback.print_exc()

print()
print("=== 测试完成 ===")