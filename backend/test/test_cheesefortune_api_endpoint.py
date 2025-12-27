import requests
import time

# API基础URL
BASE_URL = "http://localhost:8000/api/cheesefortune"

# 测试的股票代码
STOCK_CODES = ["600219.SH", "300308.SZ"]

def test_cheesefortune_api_endpoint():
    print("测试芝士财富API接口...")
    print(f"API基础URL: {BASE_URL}")
    print("=" * 50)
    
    for code in STOCK_CODES:
        print(f"\n测试股票: {code}")
        url = f"{BASE_URL}/vip-data/{code}"
        print(f"请求URL: {url}")
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=30)
            end_time = time.time()
            
            print(f"请求耗时: {end_time - start_time:.2f}秒")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"返回数据: code={data.get('code')}, message={data.get('message')}")
                
                # 检查是否返回了有效的数据
                if data.get('code') == "000":
                    print("✅ API接口测试通过: 成功获取到股票数据")
                    # 打印一些关键数据点
                    if data.get('data'):
                        stock_data = data['data']
                        print(f"股票名称: {stock_data.get('name')}")
                        print(f"股票代码: {stock_data.get('code')}")
                        print(f"当前价格: {stock_data.get('price')}")
                else:
                    print(f"❌ API接口返回非预期结果: {data}")
            else:
                print(f"❌ API接口请求失败: {response.text}")
                
        except Exception as e:
            print(f"❌ API接口请求异常: {str(e)}")

if __name__ == "__main__":
    test_cheesefortune_api_endpoint()