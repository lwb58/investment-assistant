# -*- coding: utf-8 -*-
"""独立的财务数据获取测试脚本"""
import re
import json
import requests

# 测试股票代码
stock_code = "300300"
market = "sz"  # 深市股票
paper_code = f"{market}{stock_code}"
report_type = "lrb"  # 利润表

# 构造URL
url = (
    f"https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"\
    f"?paperCode={paper_code}&source={report_type}&type=0&page=1&num=10"
)

print(f"请求URL: {url}")

# 发送请求
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers, verify=False)

print(f"\n响应状态码: {response.status_code}")
print(f"响应内容类型: {response.headers.get('Content-Type')}")
print(f"响应内容长度: {len(response.text)}")

# 打印原始响应内容（前5000字符）
print("\n=== 原始响应内容（前5000字符） ===")
print(response.text[:5000])

# 打印响应内容（后5000字符）
print("\n=== 原始响应内容（后5000字符） ===")
print(response.text[-5000:])

# 尝试直接解析JSON
print("\n=== 尝试直接解析JSON ===")
try:
    data = response.json()
    print("成功解析为JSON")
    print(f"顶级键: {list(data.keys())}")
except json.JSONDecodeError as e:
    print(f"JSON解析失败: {e}")
