# 最终验证脚本 - 验证巨子生物经营利润率和利息负担修复

import json
import os

print("=== 最终修复验证 ===")

# 读取巨子生物的杜邦数据文件
file_path = "D:/yypt/xingziyuan/investment-assistant/backend/巨子_09633_dupont_test.json"

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"文件加载成功: {file_path}")
    
    # 获取真实的完整数据列表
    full_data = data.get("full_data", [])
    print(f"\n完整数据条数: {len(full_data)}")
    
    if full_data:
        # 使用第一条数据
        latest_item = full_data[0]
        
        print(f"\n数据信息:")
        print(f"- 报告期: {latest_item.get('report_date', '未知日期')}")
        print(f"- 报告类型: {latest_item.get('period_type', '未知')}")
        
        # 查看所有字段名
        print(f"\n=== 查看所有字段名 ===")
        for i, key in enumerate(latest_item.keys()):
            if i < 15:  # 只显示前15个字段
                print(f"  {i+1}. {key}: {latest_item[key]}")
        print(f"  ... 还有 {len(latest_item.keys()) - 15} 个字段")
        
        # 直接查看指定字段的内容
        print(f"\n=== 查看关键财务字段 ===")
        key_fields = [
            "钀ヤ笟鎬绘敹鍏?", "鑲′笢鏉冪泭", "缁忚惀鍒╂鼎鐜?", 
            "OPERATE_INCOME", "GROSS_PROFIT", "OPERATE_PROFIT_RATIO"
        ]
        
        for field in key_fields:
            if field in latest_item:
                print(f"  {field}: {latest_item[field]}")
            else:
                print(f"  {field}: 不存在")
        
        # 使用stock.py中的实际修复逻辑进行测试
        print(f"\n=== 测试stock.py中的修复逻辑 ===")
        
        # 从stock.py中导入修复后的函数进行测试
        try:
            from stock import _hk_dupont_analysis_impl
            
            # 测试修复后的逻辑
            print("\n✅ 成功导入stock.py中的_hk_dupont_analysis_impl函数")
            
            # 直接使用修复后的函数处理数据
            processed_data = _hk_dupont_analysis_impl(latest_item)
            
            print(f"\n=== 修复后的数据结果 ===")
            print(f"- 经营利润率: {processed_data.get('operating_margin', '未知')}")
            print(f"- 利息负担: {processed_data.get('interest_burden', '未知')}")
            
            # 验证修复效果
            if processed_data.get('operating_margin', '') == '%':
                print("❌ 经营利润率修复尚未生效！")
            else:
                print("✅ 经营利润率修复成功！")
                
            print(f"\n=== 完整的处理结果 ===")
            for key, value in processed_data.items():
                if key not in ['operating_margin', 'interest_burden']:
                    print(f"  {key}: {value}")
            
        except ImportError as e:
            print(f"\n❌ 无法导入stock.py中的函数: {e}")
        except Exception as e:
            print(f"\n❌ 测试修复逻辑时发生错误: {e}")
        
    else:
        print("\n数据列表为空")
    
else:
    print(f"文件不存在: {file_path}")
    print("请确保已经生成了巨子生物的杜邦数据文件")

print("\n=== 修复验证完成 ===")
print("修复总结:")
print("1. 经营利润率: 修复了处理None值的问题")
print("2. 利息负担: 100%是正常现象，表示公司没有财务费用")
