from stock import get_stock_detail, get_hk_stock_detail_from_eastmoney

# 测试股票代码：巨子生物
stock_code = "02367"

# 第一步：测试get_hk_stock_detail_from_eastmoney方法
print(f"\n=== 测试1：get_hk_stock_detail_from_eastmoney方法 ===")
hk_detail_data = get_hk_stock_detail_from_eastmoney(stock_code)

if hk_detail_data:
    print(f"返回的完整数据：")
    for key, value in hk_detail_data.items():
        print(f"{key}: {value} (类型: {type(value)})")
    
    # 重点检查与问题相关的字段
    print(f"\n重点字段检查：")
    print(f"roe_avg（净资产收益率）: {hk_detail_data.get('roe_avg')}")
    print(f"operate_income（总营收）: {hk_detail_data.get('operate_income')}")
    print(f"holder_profit（归母净利润）: {hk_detail_data.get('holder_profit')}")
else:
    print("未获取到数据")

# 第二步：测试get_stock_detail方法（完整流程）
print(f"\n=== 测试2：get_stock_detail方法 ===")
full_detail_data = get_stock_detail(stock_code)

if full_detail_data:
    print(f"\n返回的完整数据结构：")
    print(f"数据类型: {type(full_detail_data)}")
    print(f"包含的键: {list(full_detail_data.keys())}")
    
    # 检查baseInfo
    if "baseInfo" in full_detail_data:
        print(f"\nbaseInfo内容：")
        for key, value in full_detail_data["baseInfo"].items():
            print(f"{key}: {value}")
    
    # 检查coreQuotes
    if "coreQuotes" in full_detail_data:
        print(f"\ncoreQuotes内容：")
        for key, value in full_detail_data["coreQuotes"].items():
            print(f"{key}: {value}")
else:
    print("未获取到完整数据")
