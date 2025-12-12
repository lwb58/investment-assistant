import requests
import json

# 定义图表生成接口URL
BASE_URL = "http://localhost:8000"
CHART_URL = f"{BASE_URL}/api/stocks/dupont/chart"

# 测试用例
stock_ids = ["09633", "603259"]  # 港股和A股
factor_types = ["all", "roe", "three", "five"]
cycle_types = ["all", "年报", "中报", "季报"]

print("=== 杜邦分析图表生成接口测试 ===")
print()

for stock_id in stock_ids:
    print(f"测试股票：{stock_id}")
    
    # 先测试基本图表生成
    params = {
        "stock_id": stock_id,
        "factor_type": "all",
        "cycle_type": "all"
    }
    
    try:
        response = requests.get(CHART_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            # 检查响应头
            content_type = response.headers.get("content-type")
            if "image/png" in content_type:
                print(f"   ✓ 成功生成图表，响应大小：{len(response.content)} 字节")
                print(f"   ✓ 响应类型：{content_type}")
                
                # 保存图表到文件
                with open(f"dupont_chart_{stock_id}.png", "wb") as f:
                    f.write(response.content)
                print(f"   ✓ 图表已保存为：dupont_chart_{stock_id}.png")
            else:
                print(f"   ✗ 生成图表失败，响应类型错误：{content_type}")
                print(f"   ✗ 响应内容：{response.text}")
        else:
            print(f"   ✗ 请求失败，状态码：{response.status_code}")
            print(f"   ✗ 响应内容：{response.text}")
            
    except requests.exceptions.Timeout:
        print(f"   ✗ 请求超时")
    except requests.exceptions.ConnectionError:
        print(f"   ✗ 连接错误，请检查服务器是否正在运行")
    except Exception as e:
        print(f"   ✗ 测试失败：{str(e)}")
    
    print()

print("=== 测试完成 ===")