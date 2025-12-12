import requests
import json
import re

# 测试股票代码：巨子生物
stock_code = "02367"

# 测试后端API是否正常工作
print("=== 测试后端API ===")
backend_url = f"http://localhost:8000/api/stocks/{stock_code}/detail"
try:
    response = requests.get(backend_url, timeout=10)
    response.raise_for_status()
    backend_data = response.json()
    
    print(f"后端API请求成功！状态码: {response.status_code}")
    
    # 检查baseInfo中的关键字段
    print("\nbackend_data.baseInfo:")
    if "baseInfo" in backend_data:
        for key in ["operateIncome", "holderProfit", "industry"]:
            if key in backend_data["baseInfo"]:
                print(f"  {key}: {backend_data['baseInfo'][key]}")
            else:
                print(f"  {key}: 未找到")
    
    # 检查coreQuotes中的关键字段
    print("\nbackend_data.coreQuotes:")
    if "coreQuotes" in backend_data:
        for key in ["roe", "peDynamic", "netProfitRatio"]:
            if key in backend_data["coreQuotes"]:
                print(f"  {key}: {backend_data['coreQuotes'][key]}")
            else:
                print(f"  {key}: 未找到")
    
    # 保存后端返回的数据到文件，以便进一步分析
    with open(f"backend_response_{stock_code}.json", "w", encoding="utf-8") as f:
        json.dump(backend_data, f, ensure_ascii=False, indent=2)
    print(f"\n后端返回数据已保存到backend_response_{stock_code}.json文件")
    
    # 模拟前端处理逻辑
    print("\n=== 模拟前端处理逻辑 ===")
    
    # 模拟currentFinancialData的计算逻辑
    latestData = {}
    
    # 从后端coreQuotes中获取数据
    if "coreQuotes" in backend_data and backend_data["coreQuotes"]:
        coreQuotes = backend_data["coreQuotes"]
        
        # 市盈率
        if coreQuotes.get("peDynamic"):
            latestData["pe"] = coreQuotes["peDynamic"]
        elif coreQuotes.get("peStatic"):
            latestData["pe"] = coreQuotes["peStatic"]
        
        # 净资产收益率
        if coreQuotes.get("roe") is not None:
            latestData["roe"] = coreQuotes["roe"]
    
    # 从后端baseInfo中获取数据
    if "baseInfo" in backend_data and backend_data["baseInfo"]:
        baseInfo = backend_data["baseInfo"]
        
        # 总营收
        if baseInfo.get("operateIncome") and baseInfo["operateIncome"] != "--":
            operateIncomeNum = float(re.sub(r'[^\d.]', '', baseInfo["operateIncome"]))
            latestData["totalRevenue"] = operateIncomeNum
        
        # 归母净利润
        if baseInfo.get("holderProfit") and baseInfo["holderProfit"] != "--":
            holderProfitNum = float(re.sub(r'[^\d.]', '', baseInfo["holderProfit"]))
            latestData["netProfitAttribution"] = holderProfitNum
    
    print("模拟前端处理后的currentFinancialData:")
    print(f"  pe: {latestData.get('pe')}")
    print(f"  roe: {latestData.get('roe')}%")
    print(f"  totalRevenue: {latestData.get('totalRevenue')}亿元")
    print(f"  netProfitAttribution: {latestData.get('netProfitAttribution')}亿元")
    
except Exception as e:
    print(f"后端API请求失败: {e}")
    print("请确保后端服务已经启动")

print("\n=== 测试完成 ===")
