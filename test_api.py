import requests
import json

# 测试股票详情API
url = "http://localhost:8000/api/stocks/600036/detail"
try:
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    
    # 解析JSON数据
    data = response.json()
    
    # 打印市值和市盈率相关数据
    print("=== 股票详情API测试结果 ===")
    print(f"股票代码: {data.get('baseInfo', {}).get('stockCode', 'N/A')}")
    print(f"股票名称: {data.get('baseInfo', {}).get('stockName', 'N/A')}")
    print(f"市值: {data.get('baseInfo', {}).get('marketCap', 'N/A')}")
    print(f"总股本: {data.get('baseInfo', {}).get('totalShares', 'N/A')}")
    print(f"流通股: {data.get('baseInfo', {}).get('floatShares', 'N/A')}")
    
    # 检查是否有腾讯财经数据
    if 'tencentData' in data:
        print("\n=== 腾讯财经数据 ===")
        tencent_data = data['tencentData']
        print(f"动态市盈率(PE-TTM): {tencent_data.get('peDynamic', 'N/A')}")
        print(f"静态市盈率(PE-LYR): {tencent_data.get('peStatic', 'N/A')}")
        print(f"总市值(元): {tencent_data.get('marketCap', 'N/A')}")
        print(f"流通市值(元): {tencent_data.get('floatMarketCap', 'N/A')}")
    
    # 检查coreQuotes中的市盈率
    if 'coreQuotes' in data:
        print("\n=== 核心行情数据 ===")
        core_quotes = data['coreQuotes']
        print(f"动态市盈率: {core_quotes.get('peDynamic', 'N/A')}")
        print(f"静态市盈率: {core_quotes.get('peStatic', 'N/A')}")
    
    print("\n测试成功！")
    
except Exception as e:
    print(f"测试失败: {str(e)}")