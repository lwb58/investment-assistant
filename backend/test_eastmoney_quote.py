import requests
import json

def test_eastmoney_quote():
    """测试东方财富行情接口"""
    # 东财行情接口URL
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    
    # 请求参数
    params = {
        "fields": "f57,f58,f47,f43,f169,f170,f44,f45,f46,f48,f60,f168,f164,f50,f171",
        "secid": "1.603259",  # A股股票：1.股票代码；港股股票：0.股票代码
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "wbp2u": "|0|0|0|web",
        "v": "09371029070054959"
    }
    
    try:
        # 发送请求
        response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应
        data = response.json()
        print("=== 东方财富行情接口测试结果 ===")
        print(f"请求状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 分析返回值结构
        if data.get("rc") == 0:  # 请求成功
            stock_data = data.get("data", {})
            print("\n=== 股票数据解析 ===")
            print(f"股票代码 (f57): {stock_data.get('f57')}")
            print(f"股票名称 (f58): {stock_data.get('f58')}")
            print(f"当前价格 (f43): {stock_data.get('f43')}")
            print(f"今开 (f44): {stock_data.get('f44')}")
            print(f"昨收 (f45): {stock_data.get('f45')}")
            print(f"最高 (f46): {stock_data.get('f46')}")
            print(f"成交量 (f47): {stock_data.get('f47')}")
            print(f"成交额 (f48): {stock_data.get('f48')}")
            print(f"最新价 (f60): {stock_data.get('f60')}")
            print(f"涨跌额 (f164): {stock_data.get('f164')}")
            print(f"涨跌幅 (f168): {stock_data.get('f168')}")
            print(f"换手率 (f169): {stock_data.get('f169')}")
            print(f"市盈率 (f170): {stock_data.get('f170')}")
            print(f"市净率 (f171): {stock_data.get('f171')}")
            print(f"总股本 (f50): {stock_data.get('f50')}")
        else:
            print(f"请求失败: {data.get('msg', '未知错误')}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    test_eastmoney_quote()
