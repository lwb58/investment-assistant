# -*- coding: utf-8 -*-
"""详细测试财务数据获取流程"""
import json
import requests

# 直接调用API获取数据
def get_raw_finance_data(stock_code):
    market = "sz"  # 简化测试，假设是深市股票
    paper_code = f"{market}{stock_code}"
    report_type = "lrb"  # 利润表
    
    url = (
        f"https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"\
        f"?paperCode={paper_code}&source={report_type}&type=0&page=1&num=10"
    )
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, verify=False)
    return response.json()

# 测试获取原始数据
print("1. 获取原始API数据...")
data = get_raw_finance_data("300300")

# 打印完整数据结构
print(f"\n2. 完整数据结构:")
print(f"   顶级键: {list(data.keys())}")

# 检查result字段
result = data.get("result", {})
print(f"\n3. result字段:")
print(f"   内容: {result}")

# 检查data字段
main_data = data.get("data", {})
print(f"\n4. data字段:")
print(f"   类型: {type(main_data)}")
print(f"   键: {list(main_data.keys()) if isinstance(main_data, dict) else '不是字典'}")

# 检查report_list
if isinstance(main_data, dict):
    report_list = main_data.get("report_list", {})
    print(f"\n5. report_list字段:")
    print(f"   类型: {type(report_list)}")
    print(f"   键(日期): {list(report_list.keys()) if isinstance(report_list, dict) else '不是字典'}")
    
    # 获取最新报表
    if isinstance(report_list, dict) and report_list:
        latest_date = sorted(report_list.keys(), reverse=True)[0]
        print(f"\n6. 最新报表日期: {latest_date}")
        
        latest_report = report_list[latest_date]
        print(f"   最新报表内容: {latest_report}")
        
        # 检查report_data
        if isinstance(latest_report, dict):
            report_data = latest_report.get("report_data", [])
            print(f"\n7. report_data字段:")
            print(f"   类型: {type(report_data)}")
            print(f"   长度: {len(report_data)}")
            
            # 打印所有财务项的字段名和值
            print(f"\n8. 所有财务项字段:")
            field_map = {}
            for i, item in enumerate(report_data[:20]):  # 只显示前20项
                if isinstance(item, dict):
                    field = item.get("item_field", "")
                    title = item.get("item_title", "")
                    value = item.get("item_value", "")
                    field_map[field] = (title, value)
                    print(f"   {i+1}. {field} ({title}): {value}")
            
            # 查找我们需要的字段
            print(f"\n9. 查找关键财务指标:")
            target_fields = {
                "BASICEPS": "基本每股收益",
                "NETPROFIT": "净利润",
                "OPERATINCO": "营业收入"
            }
            
            for field, desc in target_fields.items():
                if field in field_map:
                    title, value = field_map[field]
                    print(f"   ✓ {field} ({title}): {value}")
                else:
                    print(f"   ✗ 未找到 {field} ({desc})")
                    # 尝试通过标题查找
                    for f, (t, v) in field_map.items():
                        if desc in t:
                            print(f"     但在 {f} ({t}) 中找到类似内容: {v}")
