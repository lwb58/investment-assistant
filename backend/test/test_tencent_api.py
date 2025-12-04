import requests

# 测试腾讯财经API直接调用
def test_tencent_api():
    stock_code = "600036"
    market = "sh"  # 上海市场
    tencent_code = f"{market}{stock_code}"
    tencent_url = f"http://qt.gtimg.cn/q={tencent_code}"
    
    try:
        response = requests.get(tencent_url)
        response.encoding = "gbk"  # 腾讯财经返回的是GBK编码
        data = response.text
        
        print(f"腾讯财经API原始数据: {data}")
        
        # 解析数据
        if "=" in data and "\"" in data:
            data_part = data.split('=')[1].strip().strip('"')
            fields = data_part.split('~')
            
            print(f"\n解析后的字段数量: {len(fields)}")
            
            # 打印所有字段，查看索引
            print("\n所有字段（索引: 值）:")
            for i, field in enumerate(fields):
                print(f"{i}: {field}")
                
            # 尝试获取我们需要的字段
            if len(fields) >= 41:
                print("\n=== 关键数据提取 ===")
                print(f"股票名称: {fields[1]}")
                print(f"当前价格: {fields[3]}")
                print(f"总市值（索引44，单位：亿元）: {fields[44]}")
                print(f"流通市值（索引45，单位：亿元）: {fields[45]}")
                print(f"\n=== 市盈率相关字段 ===")
                for i in range(35, 50):
                    if fields[i] and fields[i] != '~':
                        print(f"索引{i}: {fields[i]}")
                print(f"\n=== 其他可能的关键数据 ===")
                print(f"索引69（市净率）: {fields[69]}")
                print(f"索引70（市销率）: {fields[70]}")
                print(f"索引71（市盈率TTM）: {fields[71]}")
                print(f"索引72（市现率）: {fields[72]}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    test_tencent_api()