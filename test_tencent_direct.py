import requests
import json

def test_tencent_api():
    """测试腾讯财经API，打印所有字段"""
    stock_code = "600036"
    
    # 构造腾讯财经API URL
    url = f"http://qt.gtimg.cn/q=sh{stock_code}"
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.text
        print(f"原始响应: {data}")
        
        # 解析数据
        # 格式: v_sh600036="字段1~字段2~字段3~..."
        fields = data.split('=')[1].strip().strip('"').strip(';').split('~')
        print(f"\n解析到 {len(fields)} 个字段")
        
        # 打印所有字段，每行10个字段
        for i in range(0, len(fields), 10):
            line = []
            for j in range(i, min(i+10, len(fields))):
                line.append(f"{j}: {fields[j]}")
            print('\t'.join(line))
        
        # 特别打印我们关心的字段
        print(f"\n=== 关键字段值 ===")
        print(f"3: 当前价格: {fields[3]}")
        print(f"32: 涨跌幅百分比: {fields[32]}")
        print(f"39: 市盈率: {fields[39]}")
        print(f"44: 总市值: {fields[44]}")
        print(f"45: 流通市值: {fields[45]}")
        print(f"46: 市净率: {fields[46]}")
        print(f"71: 市盈率TTM: {fields[71]}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    test_tencent_api()