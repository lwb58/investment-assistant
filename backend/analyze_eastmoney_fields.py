import requests
import json

# 测试A股
stock_code = "603259"
market = "sh"  # sh, sz, bj, hk

# 构造secid
if market == "hk":
    secid = f"116.{stock_code}"
elif market == "sh":
    secid = f"1.{stock_code}"
elif market == "sz":
    secid = f"0.{stock_code}"
elif market == "bj":
    secid = f"1.{stock_code}"

# 构造完整的东方财富接口URL
eastmoney_url = f"https://push2.eastmoney.com/api/qt/stock/get?fields=f57%2Cf58%2Cf43%2Cf44%2Cf45%2Cf46%2Cf47%2Cf48%2Cf49%2Cf50%2Cf51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf60%2Cf61%2Cf164%2Cf168%2Cf169%2Cf170%2Cf171%2Cf172%2Cf173%2Cf174%2Cf175%2Cf176%2Cf177%2Cf178%2Cf179%2Cf180%2Cf181%2Cf182%2Cf183%2Cf184%2Cf185%2Cf186%2Cf187%2Cf188%2Cf189%2Cf190&secid={secid}&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&wbp2u=%7C0%7C0%7C0%7Cweb&v=09371029070054959"

print(f"测试股票: {stock_code}({market})")
print(f"请求URL: {eastmoney_url}")
print("="*60)

try:
    response = requests.get(eastmoney_url, timeout=10)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n完整响应数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 提取data部分
        if "data" in data:
            stock_data = data["data"]
            print("\n\n股票数据部分:")
            for key, value in sorted(stock_data.items()):
                print(f"{key}: {value}")
        
        print("\n\n分析建议:")
        print("1. 检查字段值是否需要单位转换（如成交量可能是股数，需要除以100转为手）")
        print("2. 检查数值是否是科学计数法的字符串形式")
        print("3. 比较新浪接口和东方财富接口返回的同一字段值")
        
except Exception as e:
    print(f"请求失败: {e}")
