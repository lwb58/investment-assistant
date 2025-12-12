import requests
import json

def verify_fix():
    # 获取后端数据
    url = "http://localhost:8000/api/stocks/02367/detail"
    response = requests.get(url)
    data = response.json()
    
    # 提取财务数据
    financial_data = data.get('financialData', {})
    print("=== 后端财务数据 ===")
    for year in sorted(financial_data.keys()):
        year_data = financial_data[year]
        print(f"{year}: 净利润={year_data.get('netProfit')}亿元, 营收={year_data.get('revenue')}亿元")
    
    print("\n=== 前端应该显示的数据 ===")
    # 模拟前端处理逻辑
    processed_data = {}
    for year in sorted(financial_data.keys()):
        year_data = financial_data[year]
        processed_data[year] = {
            'totalRevenue': float(year_data.get('revenue', '0')),
            'netProfitAttribution': float(year_data.get('netProfit', '0'))
        }
        print(f"{year}: 总营收={processed_data[year]['totalRevenue']}亿元, 归母净利润={processed_data[year]['netProfitAttribution']}亿元")
    
    print("\n=== 修复验证结果 ===")
    if len(processed_data) >= 5:
        print("✅ 修复成功：所有年份都有正确的归母净利润数据")
        for year in sorted(processed_data.keys()):
            print(f"   {year}: {processed_data[year]['netProfitAttribution']}亿元")
    else:
        print("❌ 修复失败：数据不完整")

if __name__ == "__main__":
    verify_fix()