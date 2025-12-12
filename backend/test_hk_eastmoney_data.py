from stock import get_hk_stock_detail_from_eastmoney

# 测试股票代码：巨子生物
stock_code = "02367"

# 调用方法获取港股详情数据
hk_detail_data = get_hk_stock_detail_from_eastmoney(stock_code)

print(f"\n测试{stock_code}股票的get_hk_stock_detail_from_eastmoney方法返回数据：")
print(f"数据类型: {type(hk_detail_data)}")

if hk_detail_data:
    print(f"\n返回的完整数据：")
    for key, value in hk_detail_data.items():
        print(f"{key}: {value}")
    
    # 重点检查与问题相关的字段
    print(f"\n重点字段检查：")
    print(f"ROE_AVG（净资产收益率）: {hk_detail_data.get('ROE_AVG')}")
    print(f"OPERATE_INCOME（总营收）: {hk_detail_data.get('OPERATE_INCOME')}")
    print(f"HOLDER_PROFIT（归母净利润）: {hk_detail_data.get('HOLDER_PROFIT')}")
    print(f"PE_TTM（市盈率）: {hk_detail_data.get('PE_TTM')}")
else:
    print("\n未获取到数据")
