import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apis.cheesefortune_api import get_vip_data

def test_cache_directly():
    print("直接测试缓存装饰器功能...")
    print("=" * 50)
    
    stock_code = "600219.SH"
    
    # 第一次调用 - 应该获取新数据
    print("\n1. 第一次调用（应该获取新数据）:")
    start_time = time.time()
    result1 = get_vip_data(stock_code)
    end_time = time.time()
    print(f"   调用耗时: {end_time - start_time:.2f}秒")
    print(f"   返回数据: code={result1.get('code')}, message={result1.get('message')}")
    
    # 第二次调用 - 应该使用缓存数据
    print("\n2. 第二次调用（应该使用缓存数据）:")
    start_time = time.time()
    result2 = get_vip_data(stock_code)
    end_time = time.time()
    print(f"   调用耗时: {end_time - start_time:.2f}秒")
    print(f"   返回数据: code={result2.get('code')}, message={result2.get('message')}")
    
    # 验证两次结果是否相同
    print("\n3. 验证缓存功能:")
    if result1 == result2:
        print("   ✅ 缓存功能正常: 两次调用返回相同的数据")
    else:
        print("   ❌ 缓存功能异常: 两次调用返回不同的数据")
    
    print(f"   第一次调用耗时: {result1.get('__time__', 'N/A') if isinstance(result1, dict) else 'N/A'}秒")
    print(f"   第二次调用耗时: {end_time - start_time:.2f}秒")

if __name__ == "__main__":
    test_cache_directly()