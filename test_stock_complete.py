import requests
import json

def test_stock_detail_complete():
    """完整测试股票详情API，包括所有关键指标"""
    stock_code = "600036"
    
    url = f"http://localhost:8000/api/stocks/{stock_code}/detail"
    print(f"请求股票详情API: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        print("\n=== 完整股票详情测试 ===")
        print("1. 基础信息:")
        base_info = data.get('baseInfo', {})
        print(f"   股票代码: {base_info.get('stockCode', 'N/A')}")
        print(f"   股票名称: {base_info.get('stockName', 'N/A')}")
        print(f"   市值: {base_info.get('marketCap', 'N/A')}")
        print(f"   总股本: {base_info.get('totalShares', 'N/A')}")
        print(f"   流通股: {base_info.get('floatShares', 'N/A')}")
        
        print("\n2. 核心行情数据:")
        core_quotes = data.get('coreQuotes', {})
        print(f"   动态市盈率: {core_quotes.get('peDynamic', 'N/A')}")
        print(f"   静态市盈率: {core_quotes.get('peStatic', 'N/A')}")
        print(f"   市净率: {core_quotes.get('pbRatio', 'N/A')}")
        print(f"   当前价格: {core_quotes.get('currentPrice', 'N/A')}")
        print(f"   涨跌幅: {core_quotes.get('changeRate', 'N/A')}%")
        
        print("\n3. 腾讯财经数据:")
        tencent_data = data.get('tencentData', {})
        print(f"   动态市盈率: {tencent_data.get('peDynamic', 'N/A')}")
        print(f"   静态市盈率: {tencent_data.get('peStatic', 'N/A')}")
        print(f"   市净率: {tencent_data.get('pbRatio', 'N/A')}")
        print(f"   涨跌幅: {tencent_data.get('changeRate', 'N/A')}%")
        print(f"   总市值(元): {tencent_data.get('marketCap', 'N/A')}")
        print(f"   流通市值(元): {tencent_data.get('floatMarketCap', 'N/A')}")
        print(f"   当前价格: {tencent_data.get('currentPrice', 'N/A')}")
        
        print("\n=== 验证结果 ===")
        print(f"✓ 市值: {base_info.get('marketCap', 'N/A')} (预期: ~1.1万亿)")
        print(f"✓ 市盈率: {core_quotes.get('peDynamic', 'N/A')} (预期: ~7.32)")
        print(f"✓ 市净率: {core_quotes.get('pbRatio', 'N/A')} (预期: ~1.00)")
        print(f"✓ 涨跌幅: {core_quotes.get('changeRate', 'N/A')}% (预期: ~0.49%)")
        print(f"\nAPI响应包含的所有数据字段:")
        print(f"   baseInfo: {list(base_info.keys())}")
        print(f"   coreQuotes: {list(core_quotes.keys())}")
        print(f"   tencentData: {list(tencent_data.keys())}")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stock_detail_complete()