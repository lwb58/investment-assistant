# 简化的测试脚本，专门测试A股的数据获取

from stock_data_fetcher import StockDataFetcher

# 创建数据获取器实例
fetcher = StockDataFetcher()

# 测试招商银行（A股，代码600036）
print("=== 测试招商银行 (600036.SH) ===")

# 获取基本信息
print("\n1. 获取基本信息:")
basic_info = fetcher.get_basic_info("600036")
if basic_info:
    print(f"股票名称: {basic_info.get('stock_name', '未知')}")
    print(f"总市值: {basic_info.get('total_market_cap', '未知')}")
    print(f"净利润率: {basic_info.get('net_profit_ratio', '未知')}%")
    print(f"平均净资产收益率: {basic_info.get('roe_avg', '未知')}%")
    print(f"最新总营收: {basic_info.get('operate_income', '未知')}")
else:
    print("获取基本信息失败")

# 获取杜邦分析数据
print("\n2. 获取杜邦分析数据:")
dupont_data = fetcher.get_dupont_analysis("600036")
if dupont_data and dupont_data.get('full_data'):
    print(f"数据条数: {len(dupont_data['full_data'])}")
    latest_data = dupont_data['full_data'][0]
    print(f"最新数据日期: {latest_data.get('date', '未知')}")
    print(f"净资产收益率: {latest_data.get('净资产收益率(%)', '未知')}%")
    print(f"经营利润率: {latest_data.get('经营利润率(%)', '未知')}%")
    print(f"利息负担: {latest_data.get('利息负担(%)', '未知')}%")
else:
    print("获取杜邦分析数据失败")
    print(f"杜邦分析原始数据: {dupont_data}")

# 获取金融数据
print("\n3. 获取金融数据:")
financial_data = fetcher.get_financial_data("600036")
if financial_data:
    print(f"可用年份: {[k for k in financial_data.keys() if k.isdigit()]}")
    latest_year = max([k for k in financial_data.keys() if k.isdigit()], default=None)
    if latest_year:
        print(f"{latest_year}年数据:")
        print(f"营业收入: {financial_data[latest_year].get('revenue', '未知')}亿元")
        print(f"净利润: {financial_data[latest_year].get('netProfit', '未知')}亿元")
        print(f"毛利率: {financial_data[latest_year].get('grossMargin', '未知')}%")
        print(f"净利率: {financial_data[latest_year].get('netMargin', '未知')}%")
else:
    print("获取金融数据失败")

# 获取行情数据
print("\n4. 获取行情数据:")
quote_data = fetcher.get_quote_data("600036")
if quote_data:
    if 'coreQuotes' in quote_data:
        print(f"股票名称: {quote_data['coreQuotes'].get('stockName', '未知')}")
        print(f"当前价格: {quote_data['coreQuotes'].get('currentPrice', '未知')}")
        print(f"涨跌幅: {quote_data['coreQuotes'].get('changePercent', '未知')}%")
    else:
        print(f"行情数据结构: {quote_data.keys()}")
        print(f"行情数据: {quote_data}")
else:
    print("获取行情数据失败")
