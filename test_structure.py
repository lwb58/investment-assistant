# -*- coding: utf-8 -*-
"""测试API返回数据的完整结构"""
import json
import requests

# 直接获取API数据
def get_full_api_data():
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022?paperCode=sz300300&source=lrb&type=0&page=1&num=10"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, verify=False)
    return response.json()

# 获取并保存完整数据
data = get_full_api_data()

# 打印完整数据
print("=== 完整API返回数据 ===")
print(json.dumps(data, ensure_ascii=False, indent=2))

# 保存到文件便于查看
with open('api_response.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n=== 数据已保存到 api_response.json 文件 ===")
