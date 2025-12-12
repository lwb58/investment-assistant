#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试巨子生物(02367)的杜邦分析数据
"""

import sys
import os
import logging

# 配置根日志，设置为DEBUG级别
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 设置stock模块的日志级别为DEBUG
logging.getLogger('backend.stock').setLevel(logging.DEBUG)

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.stock import dupont_analysis

def test_juzishengwu_dupont():
    """测试巨子生物(02367)的杜邦分析数据"""
    print("=" * 60)
    print("测试巨子生物(02367)的杜邦分析数据")
    print("=" * 60)
    
    try:
        # 获取巨子生物的杜邦分析数据
        result = dupont_analysis("02367")
        
        if result["error"]:
            print(f"❌ 获取数据失败: {result['error']}")
            return
        
        if not result["full_data"]:
            print("❌ 未获取到数据")
            return
        
        print(f"✅ 成功获取数据，共{len(result['full_data'])}条记录")
        
        # 显示前5条数据，重点关注销售净利率、总资产周转率和利息负担
        for i, item in enumerate(result["full_data"][:5]):
            print(f"\n数据 {i+1}:")
            print(f"  报告日期: {item.get('报告期', 'N/A')}")
            print(f"  周期类型: {item.get('周期类型', 'N/A')}")
            print(f"  净资产收益率(%) : {item.get('净资产收益率(%)', 'N/A')}")
            print(f"  销售净利率(%) : {item.get('销售净利率(%)', 'N/A')}")
            print(f"  总资产周转率(次) : {item.get('总资产周转率(次)', 'N/A')}")
            print(f"  权益乘数 : {item.get('权益乘数', 'N/A')}")
            print(f"  总资产收益率(%) : {item.get('总资产收益率(%)', 'N/A')}")
            print(f"  毛利率(%) : {item.get('毛利率(%)', 'N/A')}")
            print(f"  利息负担(%) : {item.get('利息负担(%)', 'N/A')}")
            print(f"  考虑利息负担 : {item.get('考虑利息负担', 'N/A')}")
            
            # 检查销售净利率和总资产周转率是否为空
            if not item.get('销售净利率(%)'):
                print("  ❌ 销售净利率为空")
            if not item.get('总资产周转率(次)'):
                print("  ❌ 总资产周转率为空")
            if item.get('利息负担(%)') == "100.00":
                print("  ⚠️  利息负担为100%")
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_juzishengwu_dupont()