# -*- coding: utf-8 -*-
"""测试财务数据字段名"""
import json
import requests

# 直接调用API获取数据
def get_finance_data():
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022?paperCode=sz300300&source=lrb&type=0&page=1&num=10"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    print(f"请求URL: {url}")
    response = requests.get(url, headers=headers, verify=False)
    print(f"响应状态码: {response.status_code}")
    return response.json()

# 获取数据
data = get_finance_data()

# 打印完整数据
print(f"\n=== 完整数据结构 ===")
print(f"顶级键: {list(data.keys())}")

# 检查result字段
result = data.get("result", {})
print(f"result字段: {result}")

# 检查data字段
main_data = data.get("data", {})
print(f"data字段类型: {type(main_data)}")
print(f"data字段键: {list(main_data.keys()) if isinstance(main_data, dict) else '不是字典'}")

# 检查report_list
if isinstance(main_data, dict):
    report_list = main_data.get("report_list", {})
    print(f"report_list字段类型: {type(report_list)}")
    print(f"report_list字段键: {list(report_list.keys()) if isinstance(report_list, dict) else '不是字典'}")
    
    if isinstance(report_list, dict) and report_list:
        latest_date = sorted(report_list.keys(), reverse=True)[0]
        print(f"最新报表日期: {latest_date}")
        
        latest_report = report_list[latest_date]
        print(f"最新报表类型: {type(latest_report)}")
        print(f"最新报表键: {list(latest_report.keys()) if isinstance(latest_report, dict) else '不是字典'}")
        
        if isinstance(latest_report, dict):
            report_data = latest_report.get("report_data", [])
            print(f"report_data类型: {type(report_data)}")
            print(f"report_data长度: {len(report_data)}")
            
            print(f"\n=== 所有财务字段 ===")
            for i, item in enumerate(report_data[:100]):
                if isinstance(item, dict):
                    field = item.get("item_field", "")
                    value = item.get("item_value", None)
                    title = item.get("item_title", "")
                    print(f"{i+1:3d}. {field:<20} {title:<20} = {value}")
        else:
            print(f"最新报表不是字典")
    else:
        print(f"report_list为空或不是字典")
else:
    print(f"data不是字典")
