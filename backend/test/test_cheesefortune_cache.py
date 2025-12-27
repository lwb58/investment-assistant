import requests
import time
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/cheesefortune"

# 测试的股票代码
STOCK_CODE = "300308.SZ"

def test_cheesefortune_cache():
    print("测试芝士财富API缓存功能...")
    print(f"API基础URL: {BASE_URL}")
    print(f"测试股票: {STOCK_CODE}")
    print("=" * 50)
    headers = {"Connection": "close"}  # 保留不影响，可加可不加
    url = f"{BASE_URL}/vip-data/{STOCK_CODE}"
    
    # 第一次请求 - 应该获取新数据
    print("\n1. 第一次请求（应该获取新数据）:")
    try:
        start_time = time.time()
        # ============ 优化点1：创建独立会话+请求+强制关闭连接 ============
        s1 = requests.Session()
        response1 = s1.get(url, headers=headers, timeout=30)
        s1.close()  # 核心！强制销毁连接，不放回连接池，立即断开
        # ==============================================================
        print("客户端手动配置的请求头：", headers)
        print("服务端返回的Connection响应头：", response1.headers.get("Connection"))
        print("请求是否复用连接池：", response1.connection != None)
        end_time = time.time()
        
        print(f"   请求耗时: {end_time - start_time:.2f}秒")
        print(f"   状态码: {response1.status_code}")
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"   返回数据: code={data1.get('code')}, message={data1.get('message')}")
            
            if data1.get('code') == "000":
                print("   ✅ 成功获取到股票数据")
                cache_key1 = json.dumps(data1)
            else:
                print(f"   ❌ API返回非预期结果: {data1}")
                return False
        else:
            print(f"   ❌ API请求失败: {response1.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ API请求异常: {str(e)}")
        return False
    
    # 短暂等待
    time.sleep(2)
    
    # 第二次请求 - 应该使用缓存数据
    print("\n2. 第二次请求（应该使用缓存数据）:")
    try:
        start_time2 = time.time()
        # ============ 优化点2：创建新的独立会话+请求+强制关闭连接 ============
        s2 = requests.Session()
        response2 = s2.get(url, headers=headers, timeout=30)
        s2.close()  # 核心！强制销毁连接，不放回连接池，立即断开
        # ==============================================================
        print("客户端手动配置的请求头：", headers)
        print("服务端返回的Connection响应头：", response2.headers.get("Connection"))
        print("请求是否复用连接池：", response2.connection != None)
        end_time2 = time.time()
        second_request_time = end_time2 - start_time2
        
        print(f"   请求耗时: {second_request_time:.2f}秒")
        print(f"   状态码: {response2.status_code}")
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"   返回数据: code={data2.get('code')}, message={data2.get('message')}")
            
            if data2.get('code') == "000":
                print("   ✅ 成功获取到股票数据")
                cache_key2 = json.dumps(data2)
            else:
                print(f"   ❌ API返回非预期结果: {data2}")
                return False
        else:
            print(f"   ❌ API请求失败: {response2.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ API请求异常: {str(e)}")
        return False
    
    # 验证两次请求的数据是否相同
    print("\n3. 验证缓存功能:")
    if cache_key1 == cache_key2:
        print("   ✅ 缓存功能正常: 两次请求返回相同的数据")
        # 验证第二次请求是否更快
        first_request_time = end_time - start_time
        print(f"   第一次请求耗时: {first_request_time:.2f}秒")
        print(f"   第二次请求耗时: {second_request_time:.2f}秒")
        if second_request_time < first_request_time * 0.5:
            print("   ✅ 缓存请求速度更快: 第二次请求耗时明显减少")
        return True
    else:
        print("   ❌ 缓存功能异常: 两次请求返回不同的数据")
        print(f"      第一次请求数据: {data1}")
        print(f"      第二次请求数据: {data2}")
        return False

if __name__ == "__main__":
    success = test_cheesefortune_cache()
    if success:
        print("\n🎉 所有缓存功能测试通过!")
    else:
        print("\n❌ 缓存功能测试失败!")
        exit(1)