import json
import requests
from util import fetch_url
from typing import Dict, List, Any

# 东方财富网港股API列表
hk_api_urls = {
    "main_indicator": "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_MAININDICATOR&columns=ALL&quoteColumns=&filter=(SECUCODE%3D%2202367.HK%22)&pageNumber=1&pageSize=9&sortTypes=-1&sortColumns=STD_REPORT_DATE&source=F10&client=PC&v=040146104118736425",
    "balance_summary": "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_CUSTOM_HKF10_APPFN_BALANCE_SUMMARY&columns=SECUCODE%2CSECURITY_CODE%2CSECURITY_NAME_ABBR%2CREPORT_DATE%2CFISCAL_YEAR%2CCURRENCY%2CACCOUNT_STANDARD%2CREPORT_TYPE&quoteColumns=&filter=(SECUCODE%3D%2202367.HK%22)&source=F10&client=PC&v=08409545666614856",
    "income_summary": "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_CUSTOM_HKF10_APPFN_INCOME_SUMMARY&columns=SECUCODE%2CSECURITY_CODE%2CSECURITY_NAME_ABBR%2CSTART_DATE%2CREPORT_DATE%2CFISCAL_YEAR%2CCURRENCY%2CACCOUNT_STANDARD%2CREPORT_TYPE&quoteColumns=&filter=(SECUCODE%3D%2202367.HK%22)&source=F10&client=PC&v=003154477787095611",
    "cashflow_summary": "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_CUSTOM_HKSK_APPFN_CASHFLOW_SUMMARY&columns=SECUCODE%2CSECURITY_CODE%2CSECURITY_NAME_ABBR%2CSTART_DATE%2CREPORT_DATE%2CFISCAL_YEAR%2CCURRENCY%2CACCOUNT_STANDARD%2CREPORT_TYPE&quoteColumns=&filter=(SECUCODE%3D%2202367.HK%22)&source=F10&client=PC&v=09795213078652865",
    "balance_pc": "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_BALANCE_PC&columns=SECUCODE%2CSECURITY_CODE%2CSECURITY_NAME_ABBR%2CORG_CODE%2CREPORT_DATE%2CDATE_TYPE_CODE%2CFISCAL_YEAR%2CSTD_ITEM_CODE%2CSTD_ITEM_NAME%2CAMOUNT%2CSTD_REPORT_DATE&quoteColumns=&filter=(SECUCODE%3D%2202367.HK%22)(REPORT_DATE%20in%20(%272025-06-30%27%2C%272024-12-31%27%2C%272024-06-30%27%2C%272023-12-31%27%2C%272023-06-30%27%2C%272022-12-31%27%2C%272021-12-31%27%2C%272020-12-31%27))&pageNumber=1&pageSize=&sortTypes=-1%2C1&sortColumns=REPORT_DATE%2CSTD_ITEM_CODE&source=F10&client=PC&v=012871960514961645",
    "income_pc": "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_INCOME_PC&columns=SECUCODE%2CSECURITY_CODE%2CSECURITY_NAME_ABBR%2CORG_CODE%2CREPORT_DATE%2CDATE_TYPE_CODE%2CFISCAL_YEAR%2CSTART_DATE%2CSTD_ITEM_CODE%2CSTD_ITEM_NAME%2CAMOUNT&quoteColumns=&filter=(SECUCODE%3D%2202367.HK%22)(REPORT_DATE%20in%20(%272025-06-30%27%2C%272024-12-31%27%2C%272024-06-30%27%2C%272023-12-31%27%2C%272023-06-30%27%2C%272022-12-31%27%2C%272022-06-30%27%2C%272021-12-31%27))&pageNumber=1&pageSize=&sortTypes=-1%2C1&sortColumns=REPORT_DATE%2CSTD_ITEM_CODE&source=F10&client=PC&v=017808899909637665",
    "cashflow_pc": "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_CASHFLOW_PC&columns=SECUCODE%2CSECURITY_CODE%2CSECURITY_NAME_ABBR%2CORG_CODE%2CREPORT_DATE%2CDATE_TYPE_CODE%2CFISCAL_YEAR%2CSTART_DATE%2CSTD_ITEM_CODE%2CSTD_ITEM_NAME%2CAMOUNT&quoteColumns=&filter=(SECUCODE%3D%2202367.HK%22)(REPORT_DATE%20in%20(%272025-06-30%27%2C%272024-12-31%27%2C%272024-06-30%27%2C%272023-12-31%27%2C%272023-06-30%27%2C%272022-12-31%27%2C%272022-06-30%27%2C%272021-12-31%27))&pageNumber=1&pageSize=&sortTypes=-1%2C1&sortColumns=REPORT_DATE%2CSTD_ITEM_CODE&source=F10&client=PC&v=08444454471053581"
}

def test_hk_api(api_name: str, url: str):
    """测试单个港股API并打印数据结构"""
    print(f"\n{'='*60}")
    print(f"测试API: {api_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        data = fetch_url(url, timeout=20, retry=3)
        if not data:
            print("❌ API返回空数据")
            return None
        
        print("✅ API请求成功")
        print(f"数据类型: {type(data)}")
        
        if isinstance(data, dict):
            print(f"顶级键: {list(data.keys())}")
            
            # 检查result字段
            if "result" in data:
                result = data["result"]
                print(f"result类型: {type(result)}")
                if isinstance(result, dict):
                    print(f"result键: {list(result.keys())}")
                    
                    # 检查data字段
                    if "data" in result:
                        result_data = result["data"]
                        print(f"result.data类型: {type(result_data)}")
                        if isinstance(result_data, list) and result_data:
                            print(f"result.data长度: {len(result_data)}")
                            print(f"第一条数据键: {list(result_data[0].keys())[:20]}...")  # 只显示前20个键
                            print(f"第一条数据示例: {json.dumps(result_data[0], ensure_ascii=False, indent=2)[:500]}...")
                
        return data
        
    except Exception as e:
        print(f"❌ API请求失败: {str(e)}")
        return None

def main():
    """测试所有港股API"""
    print("开始测试东方财富网港股API...")
    
    api_results = {}
    
    # 测试主要财务指标API（最重要的）
    main_indicator_data = test_hk_api("main_indicator", hk_api_urls["main_indicator"])
    if main_indicator_data:
        api_results["main_indicator"] = main_indicator_data
        
        # 保存到文件便于详细分析
        with open("hk_main_indicator_test.json", "w", encoding="utf-8") as f:
            json.dump(main_indicator_data, f, ensure_ascii=False, indent=2)
        print(f"\n📁 主要财务指标数据已保存到: hk_main_indicator_test.json")
    
    # 测试其他API（简化输出）
    for api_name, url in hk_api_urls.items():
        if api_name == "main_indicator":
            continue  # 已经测试过
            
        data = test_hk_api(api_name, url)
        if data:
            api_results[api_name] = data

if __name__ == "__main__":
    main()
