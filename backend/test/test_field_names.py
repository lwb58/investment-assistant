# -*- coding: utf-8 -*-
"""测试API返回的所有财务字段名"""
import json
import requests

# 直接调用API获取数据
def get_finance_data():
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022?paperCode=sz300300&source=lrb&type=0&page=1&num=10"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, verify=False)
    return response.json()

# 获取数据
data = get_finance_data()

# 打印完整数据
print("=== 完整数据 ===")
print(json.dumps(data, indent=2, ensure_ascii=False))

# 提取财务数据
result = data.get("result", {})
print(f"\n=== result字段 ===")
print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get("code") == 0:
    main_data = result.get("data", {})
    print(f"\n=== data字段 ===")
    print(json.dumps(main_data, indent=2, ensure_ascii=False))
    
    report_list = main_data.get("report_list", {})
    print(f"\n=== report_list字段 ===")
    print(json.dumps(report_list, indent=2, ensure_ascii=False))
    
    if report_list:
        # 获取最新的报表
        latest_date = sorted(report_list.keys(), reverse=True)[0]
        latest_report = report_list[latest_date]
        report_data = latest_report.get("data", [])
        
        print(f"\n=== 所有财务字段名（按item_field排序） ===")
        fields = []
        for item in report_data:
            if isinstance(item, dict):
                field = item.get("item_field", "")
                title = item.get("item_title", "")
                value = item.get("item_value", "")
                fields.append((field, title, value))
        
        # 按item_field排序并打印
        fields.sort(key=lambda x: x[0])
        for field, title, value in fields:
            print(f"item_field: {field:<20} item_title: {title:<30} item_value: {value}")
    else:
        print("report_list为空")
else:
    print(f"API返回错误，错误代码: {result.get('code')}")
    print(f"错误信息: {result.get('msg')}")
