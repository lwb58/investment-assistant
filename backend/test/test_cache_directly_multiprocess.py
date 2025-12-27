import time
import requests
import multiprocessing
import subprocess
import sys

# 定义启动服务器的函数
def start_server():
    """在子进程中启动服务器"""
    server_process = subprocess.Popen(
        [sys.executable, 'main.py'],
        cwd='d:/code/investment-assistant/backend',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return server_process

# 定义测试缓存功能的函数
def test_cache():
    """测试芝士财富API的缓存功能"""
    # API基础URL
    BASE_URL = "http://localhost:8001/api/cheesefortune"
    
    # 测试的股票代码
    stock_code = "600219.SH"
    
    print("测试芝士财富API缓存功能...")
    print(f"API基础URL: {BASE_URL}")
    print(f"测试股票: {stock_code}")
    print("=" * 50)
    
    # 等待服务器启动
    time.sleep(3)
    
    try:
        # 第一次请求（应该获取新数据）
        print("\n1. 第一次请求（应该获取新数据）:")
        start_time = time.time()
        response = requests.get(f"{BASE_URL}?stock_code={stock_code}")
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"   请求成功，状态码: {response.status_code}")
            print(f"   响应时间: {end_time - start_time:.2f}秒")
        else:
            print(f"   请求失败，状态码: {response.status_code}")
        
        # 第二次请求（应该使用缓存）
        print("\n2. 第二次请求（应该使用缓存）:")
        start_time = time.time()
        response = requests.get(f"{BASE_URL}?stock_code={stock_code}")
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"   请求成功，状态码: {response.status_code}")
            print(f"   响应时间: {end_time - start_time:.2f}秒")
        else:
            print(f"   请求失败，状态码: {response.status_code}")
            
        print("\n" + "=" * 50)
        print("缓存功能测试完成！")
        print("如果第二次请求的响应时间明显短于第一次，说明缓存功能正常工作。")
        
    except requests.exceptions.ConnectionError:
        print("\n错误：无法连接到服务器，请确保服务器已正确启动！")
    except Exception as e:
        print(f"\n错误：{e}")

# 主函数
if __name__ == "__main__":
    # 启动服务器
    print("启动服务器...")
    server_process = start_server()
    
    try:
        # 运行测试
        test_cache()
    finally:
        # 关闭服务器
        print("\n关闭服务器...")
        server_process.terminate()
        server_process.wait()
        print("服务器已关闭")