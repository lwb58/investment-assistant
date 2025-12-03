# -*- coding: utf-8 -*-
"""完整测试API返回的数据结构"""
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

# 递归打印数据结构，只显示键和类型，不显示值
def print_structure(obj, indent=0):
    if isinstance(obj, dict):
        print(" " * indent + "{")
        for key, value in obj.items():
            print(" " * (indent + 2) + f"{key}: {type(value).__name__}")
            if isinstance(value, (dict, list)):
                print_structure(value, indent + 4)
        print(" " * indent + "}")
    elif isinstance(obj, list):
        print(" " * indent + "[")
        if len(obj) > 0:
            print(" " * (indent + 2) + f"元素类型: {type(obj[0]).__name__}, 长度: {len(obj)}")
            if isinstance(obj[0], (dict, list)):
                print_structure(obj[0], indent + 4)
        print(" " * indent + "]")

# 打印完整数据结构
print("=== 完整数据结构 ===")
print_structure(data)

# 检查所有可能的路径
print("\n=== 检查所有可能的数据路径 ===")
for key in data.keys():
    print(f"\n路径: data['{key}']")
    value = data[key]
    print(f"类型: {type(value).__name__}")
    
    if isinstance(value, dict):
        for subkey in value.keys():
            subvalue = value[subkey]
            print(f"  {subkey}: {type(subvalue).__name__}")
            
            if isinstance(subvalue, dict):
                for subsubkey in subvalue.keys():
                    subsubvalue = subvalue[subsubkey]
                    print(f"    {subsubkey}: {type(subsubvalue).__name__}")
                    
                    if isinstance(subsubvalue, dict):
                        for subsubsubkey in subsubvalue.keys():
                            subsubsubvalue = subsubvalue[subsubsubkey]
                            print(f"      {subsubsubkey}: {type(subsubsubvalue).__name__}")
                            
                            if isinstance(subsubsubvalue, list) and len(subsubsubvalue) > 0:
                                print(f"        列表元素类型: {type(subsubsubvalue[0]).__name__}")
                                if isinstance(subsubsubvalue[0], dict):
                                    print(f"        元素示例: {subsubsubvalue[0]}")
                    elif isinstance(subsubvalue, list) and len(subsubvalue) > 0:
                        print(f"      列表元素类型: {type(subsubvalue[0]).__name__}")
                        if isinstance(subsubvalue[0], dict):
                            print(f"      元素示例: {subsubvalue[0]}")
            elif isinstance(subvalue, list) and len(subvalue) > 0:
                print(f"  列表元素类型: {type(subvalue[0]).__name__}")
                if isinstance(subvalue[0], dict):
                    print(f"  元素示例: {subvalue[0]}")
