# -*- coding: utf-8 -*-
"""
测试港股数据中的重复键问题
"""

import sys
import os
import pandas as pd
from stock import _hk_dupont_analysis_impl  # 港股杜邦分析接口
from stock import dupont_analysis  # 通用杜邦分析接口

# 设置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_hk_data_structure():
    """测试港股数据结构，找出重复键问题"""
    print("=== 测试港股数据结构 ===")
    
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
    print(f"原始数据列名：{list(df.columns)}")
    
    # 检查周期类型字段
    print("\n=== 周期类型字段检查 ===")
    if "周期类型" in df.columns:
        print(f"周期类型：{df['周期类型'].unique()}")
    elif "period_type" in df.columns:
        print(f"period_type：{df['period_type'].unique()}")
    else:
        print("无周期类型相关字段")
    
    # 检查报告期字段
    print("\n=== 报告期字段检查 ===")
    date_fields = ["报告期", "report_date", "report_period"]
    for field in date_fields:
        if field in df.columns:
            print(f"{field}：{len(df[field].unique())} 个唯一值")
            print(f"前5个值：{list(df[field].head())}")
            break
    
    # 检查指标字段
    print("\n=== 指标字段检查 ===")
    indicator_fields = [
        "净资产收益率", "净资产收益率(%)",
        "销售净利率", "销售净利率(%)",
        "总资产周转率", "总资产周转率(次)", "资产周转率(次)",
        "权益乘数"
    ]
    
    for field in indicator_fields:
        if field in df.columns:
            print(f"{field}：存在")
            # 检查该字段是否有值
            non_empty = df[field].replace("", pd.NA).dropna()
            print(f"  非空值数量：{len(non_empty)}")
            if len(non_empty) > 0:
                print(f"  前3个值：{list(non_empty.head())}")
        else:
            print(f"{field}：不存在")
    
    # 模拟图表生成的数据处理过程
    print("\n=== 模拟图表生成数据处理 ===")
    
    # 清洗列名
    df.columns = df.columns.str.strip()
    print(f"清洗后列名：{list(df.columns)}")
    
    # 处理报告期字段
    if "report_date" in df.columns:
        df = df.rename(columns={"report_date": "报告期"})
    elif "report_period" in df.columns:
        df = df.rename(columns={"report_period": "报告期"})
    
    df["报告期"] = pd.to_datetime(df["报告期"])
    print(f"报告期处理后类型：{df['报告期'].dtype}")
    print(f"报告期值：{list(df['报告期'].dt.strftime('%Y-%m-%d'))}")
    
    # 处理周期类型字段
    if "period_type" in df.columns:
        df = df.rename(columns={"period_type": "周期类型"})
    elif "周期类型" not in df.columns:
        df["周期类型"] = "年报"
    
    print(f"周期类型：{list(df['周期类型'])}")
    
    # 检查重复的报告期+周期类型
    print("\n=== 检查重复的报告期+周期类型 ===")
    df['period_key'] = df['报告期'].dt.strftime('%Y-%m-%d') + "_" + df['周期类型']
    print(f"唯一period_key数量：{df['period_key'].nunique()}")
    print(f"总记录数：{len(df)}")
    
    # 查找重复的键
    duplicate_keys = df[df.duplicated('period_key', keep=False)]
    if not duplicate_keys.empty:
        print("\n发现重复键：")
        print(duplicate_keys[['报告期', '周期类型', 'period_key']])
    else:
        print("\n无重复键")
    
    # 检查是否有重复的列名
    print("\n=== 检查重复的列名 ===")
    duplicate_cols = df.columns[df.columns.duplicated(keep=False)]
    if len(duplicate_cols) > 0:
        print(f"发现重复列名：{list(duplicate_cols)}")
    else:
        print("无重复列名")
    
    # 查看数据前几行
    print("\n=== 数据前3行 ===")
    print(df.head(3).T)

if __name__ == "__main__":
    test_hk_data_structure()
