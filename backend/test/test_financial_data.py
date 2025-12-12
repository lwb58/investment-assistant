import requests
import json

# 测试巨子生物(02367)的财务数据
def test_financial_data():
    url = "http://localhost:8000/api/stocks/02367/detail"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        
        data = response.json()
        
        print("=== 财务数据结构 ===")
        print("是否有financialData:", "financialData" in data)
        
        if "financialData" in data:
            financial_data = data["financialData"]
            print(f"财务数据年份数量: {len(financial_data)}")
            print(f"财务数据年份: {list(financial_data.keys())}")
            
            # 打印每个年份的财务数据
            for year, fin_data in financial_data.items():
                print(f"\n=== {year} ===")
                print(f"数据内容: {json.dumps(fin_data, ensure_ascii=False, indent=2)}")
                print(f"字段列表: {list(fin_data.keys())}")
    
    except requests.RequestException as e:
        print(f"请求错误: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")

if __name__ == "__main__":
    test_financial_data()