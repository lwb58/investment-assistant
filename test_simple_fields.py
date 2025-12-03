import requests
import json

# 设置请求URL和参数
ticker = '000001'
url = f'https://esf-finance.sina.cn/ifinance/esf/finance/view/{ticker}?type=lrb&rtype=report'

# 发送请求
response = requests.get(url, timeout=20, verify=False)
print(f"响应状态码: {response.status_code}")

# 解析响应
raw_data = response.text
print("\n原始响应内容:")
print(raw_data[:10000])  # 只打印前10000字符

# 尝试解析JSON
try:
    data = json.loads(raw_data)
    print("\n解析后的JSON结构:")
    print(f"结果状态: {data.get('result', {}).get('code')}")
    print(f"结果消息: {data.get('result', {}).get('msg')}")
    print(f"数据结构: {json.dumps(data['result']['data'], indent=2)[:10000]}")
    
    # 获取报告列表
    report_list = data['result']['data']['report_list']
    print("\n报告列表:")
    print(f"报告日期: {list(report_list.keys())}")
    
    # 遍历所有报告
    for report_date, report_data in report_list.items():
        print(f"\n\n=== {report_date} ===")
        
        # 遍历所有财务字段
        for item in report_data['data']:
            print(f"字段名: {item['item_field']}, 标题: {item['item_title']}, 值: {item['item_value']}")
            
except json.JSONDecodeError as e:
    print(f"JSON解析错误: {e}")
