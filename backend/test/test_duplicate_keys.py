# -*- coding: utf-8 -*-
"""
详细测试港股数据中的重复键问题
"""

import sys
import os
import pandas as pd
from stock import _hk_dupont_analysis_impl  # 港股杜邦分析接口

# 设置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_duplicate_report_dates():
    """详细测试报告期字段的重复情况"""
    print("=== 详细测试报告期字段的重复情况 ===")
    
    # 获取港股数据
    stock_id = "09633"
    result = _hk_dupont_analysis_impl(stock_id)
    
    if result.get("error"):
        print(f"获取数据失败：{result['error']}")
        return
    
    data = result.get("full_data", [])
    print(f"数据总数：{len(data)}")
    
    if not data:
        print("无数据")
        return
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    print(f"\n数据列数：{len(df.columns)}")
    
    # 检查所有可能的日期字段
    date_candidates = ["报告期", "report_date", "report_period", "STD_REPORT_DATE"]
    found_date_field = None
    
    for field in date_candidates:
        if field in df.columns:
            found_date_field = field
            print(f"\n找到日期字段：{field}")
            print(f"字段类型：{df[field].dtype}")
            print(f"唯一值数量：{df[field].nunique()}")
            print(f"总记录数：{len(df)}")
            
            # 找出重复的值
            duplicates = df[df.duplicated(field, keep=False)]
            if not duplicates.empty:
                print(f"\n发现重复的{field}值：")
                duplicate_values = df[field].value_counts()[df[field].value_counts() > 1]
                print(f"重复值列表：{list(duplicate_values.index)}")
                print(f"重复值及出现次数：{duplicate_values.to_dict()}")
                
                # 显示重复行的详细信息
                print(f"\n重复行的详细信息（前10行）：")
                print(duplicates[[field, 'report_date', 'report_period', 'period_type', 'ROE_AVG', 'NET_PROFIT_RATIO']].head(10))
            else:
                print("\n无重复值")
            
            break
    
    if not found_date_field:
        print("\n未找到日期相关字段")
        return
    
    # 尝试不同的日期转换方法
    print(f"\n=== 测试日期转换方法 ===")
    try:
        # 方法1：直接转换
        df['test_date1'] = pd.to_datetime(df[found_date_field], errors='coerce')
        print(f"方法1 - 成功转换的记录数：{df['test_date1'].notna().sum()}")
        print(f"方法1 - 转换失败的记录数：{df['test_date1'].isna().sum()}")
        
        if df['test_date1'].isna().sum() > 0:
            print(f"转换失败的记录：{list(df[df['test_date1'].isna()][found_date_field])}")
            
    except Exception as e:
        print(f"方法1失败：{str(e)}")
    
    try:
        # 方法2：先转换为字符串
        df['test_date2'] = pd.to_datetime(df[found_date_field].astype(str), errors='coerce')
        print(f"方法2 - 成功转换的记录数：{df['test_date2'].notna().sum()}")
        print(f"方法2 - 转换失败的记录数：{df['test_date2'].isna().sum()}")
    except Exception as e:
        print(f"方法2失败：{str(e)}")
    
    try:
        # 方法3：使用指定格式
        df['test_date3'] = pd.to_datetime(df[found_date_field], format='%Y-%m-%d', errors='coerce')
        print(f"方法3 - 成功转换的记录数：{df['test_date3'].notna().sum()}")
        print(f"方法3 - 转换失败的记录数：{df['test_date3'].isna().sum()}")
    except Exception as e:
        print(f"方法3失败：{str(e)}")
    
    # 检查数据中是否有重复的字段名
    print(f"\n=== 检查重复的字段名 ===")
    if df.columns.duplicated().any():
        duplicate_columns = df.columns[df.columns.duplicated()]
        print(f"发现重复字段名：{list(duplicate_columns)}")
    else:
        print("无重复字段名")
    
    # 检查是否有相同内容的不同字段
    print(f"\n=== 检查字段内容重复 ===")
    for i, field1 in enumerate(df.columns):
        for field2 in df.columns[i+1:]:
            if field1 != field2 and df[field1].equals(df[field2]):
                print(f"字段 {field1} 和 {field2} 内容完全相同")
    
    # 显示数据的基本信息
    print(f"\n=== 数据基本信息 ===")
    print(df.info())

if __name__ == "__main__":
    test_duplicate_report_dates()
