import requests
import json

print("测试股票列表API...")

try:
    # 调用后端的股票列表API
    response = requests.get("http://localhost:8000/api/stocks")
    
    # 检查响应状态
    if response.status_code == 200:
        stocks = response.json()
        print(f"API返回的股票数量: {len(stocks)}")
        
        if stocks:
            print("股票数据详情:")
            for i, stock in enumerate(stocks, 1):
                print(f"\n{i}. 股票代码: {stock.get('stockCode', 'N/A')}")
                print(f"   股票名称: {stock.get('stockName', 'N/A')}")
                print(f"   当前价格: {stock.get('currentPrice', 'N/A')}")
                print(f"   涨跌幅: {stock.get('changeRate', 'N/A')}")
        else:
            print("警告: API返回空列表")
    else:
        print(f"API请求失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")

except Exception as e:
    print(f"调用API时出错: {str(e)}")