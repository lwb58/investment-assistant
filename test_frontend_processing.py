import requests
import json

# 获取后端数据
def get_backend_data():
    url = 'http://localhost:8000/api/stocks/02367/detail'
    response = requests.get(url)
    return response.json()

# 模拟前端处理逻辑
def simulate_frontend_processing(stock_data):
    # 提取财务数据
    finance_data = stock_data.get('financialData', {})
    dupont_data = stock_data.get('dupontData', {})
    full_data = dupont_data.get('full_data', [])
    
    print("=== 原始数据 ===")
    print("财务数据键:", list(finance_data.keys()))
    print("杜邦分析数据长度:", len(full_data))
    
    # 模拟前端处理逻辑
    processed_finance_data = {}
    
    if full_data:
        print("\n=== 使用杜邦分析数据 ===")
        for item in full_data:
            report_period = item.get('报告期', '')
            # 提取关键财务指标
            revenue = item.get('营业总收入', '0')
            net_profit = item.get('净利润', '0')
            
            processed_finance_data[report_period] = {
                'totalRevenue': float(revenue.replace(',', '')) / 10000 if revenue else 0,
                'netProfitAttribution': float(net_profit.replace(',', '')) / 10000 if net_profit else 0
            }
            print(f"报告期: {report_period}, 数据: {processed_finance_data[report_period]}")
    else:
        print("\n=== 使用后端直接返回的财务数据 ===")
        for year in finance_data:
            year_data = finance_data[year]
            processed_finance_data[year] = {
                'totalRevenue': float(year_data.get('revenue', '0')),
                'netProfitAttribution': float(year_data.get('netProfit', '0'))
            }
            print(f"年份: {year}, 数据: {processed_finance_data[year]}")
    
    # 模拟前端的年份排序和反转
    financial_years = list(processed_finance_data.keys())
    # 按日期降序排序
    financial_years.sort(key=lambda x: x, reverse=True)
    reversed_dates = financial_years[::-1]  # 最新报告期在右侧
    
    print("\n=== 处理后的年份列表 ===")
    print("financialYears:", financial_years)
    print("reversedDates:", reversed_dates)
    
    # 模拟前端的标签生成
    labels = []
    for date in reversed_dates:
        parts = date.split('-')
        year = parts[0]
        month = parts[1] if len(parts) > 1 else None
        
        if not month or isNaN(month):
            labels.append(year)
        else:
            quarter = (int(month) - 1) // 3 + 1
            labels.append(f"{year}-Q{quarter}")
    
    print("\n=== 生成的标签 ===")
    print("labels:", labels)
    
    # 模拟前端的数据生成
    net_profit_data = []
    for date in reversed_dates:
        value = processed_finance_data.get(date, {}).get('netProfitAttribution', 0)
        net_profit_data.append(round(value, 2))
    
    print("\n=== 生成的数据 ===")
    print("netProfitData:", net_profit_data)
    
    return {
        'processed_finance_data': processed_finance_data,
        'financial_years': financial_years,
        'reversed_dates': reversed_dates,
        'labels': labels,
        'net_profit_data': net_profit_data
    }

def isNaN(value):
    try:
        float(value)
        return False
    except ValueError:
        return True

# 执行测试
if __name__ == "__main__":
    data = get_backend_data()
    result = simulate_frontend_processing(data)
    
    # 检查是否有重复的年份
    print("\n=== 检查重复年份 ===")
    years_count = {}
    for label in result['labels']:
        year = label.split('-')[0]
        years_count[year] = years_count.get(year, 0) + 1
    
    for year, count in years_count.items():
        if count > 1:
            print(f"年份 {year} 出现 {count} 次")
        else:
            print(f"年份 {year} 出现 {count} 次")