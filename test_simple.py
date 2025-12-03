# -*- coding: utf-8 -*-
"""简化的测试脚本"""
import re
import json
import requests

# 直接测试新浪财经API
url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022?paperCode=sz300300&source=lrb&type=0&page=1&num=10"

print(f"请求URL: {url}")

# 发送请求
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers, verify=False)

print(f"响应状态码: {response.status_code}")
print(f"响应内容长度: {len(response.text)}")
print("\n响应内容前1000字符:")
print(response.text[:1000])
print("\n响应内容后1000字符:")
print(response.text[-1000:])

# 处理JSONP响应
if response.text.startswith("hqccall"):
    json_str = re.sub(r'^hqccall\d+\(', '', response.text).rstrip(')')
    print("\n处理后的JSON字符串前1000字符:")
    print(json_str[:1000])
    
    # 解析JSON
    data = json.loads(json_str)
    print("\nJSON数据结构:")
    print(f"顶级键: {list(data.keys())}")
    
    if "data" in data:
        print(f"data键的内容类型: {type(data['data'])}")
        print(f"data键的内容: {data['data']}")
        
        if isinstance(data['data'], dict) and "report_list" in data['data']:
            report_list = data['data']['report_list']
            print(f"\nreport_list长度: {len(report_list)}")
            
            if report_list:
                latest_report = report_list[0]
                print(f"\n最新报表内容: {latest_report}")
                
                if "report_data" in latest_report:
                    report_data = latest_report['report_data']
                    print(f"\nreport_data长度: {len(report_data)}")
                    
                    # 打印所有财务项
                    print("\n所有财务项:")
                    for item in report_data:
                        print(f"item_field: {item.get('item_field')}, item_title: {item.get('item_title')}, item_value: {item.get('item_value')}")
