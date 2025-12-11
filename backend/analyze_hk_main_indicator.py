import json
from util import fetch_url

def analyze_hk_main_indicator():
    """分析港股主要财务指标API的数据结构"""
    url = "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_MAININDICATOR&columns=ALL&quoteColumns=&filter=(SECUCODE%3D%2202367.HK%22)&pageNumber=1&pageSize=9&sortTypes=-1&sortColumns=STD_REPORT_DATE&source=F10&client=PC&v=040146104118736425"
    
    try:
        data = fetch_url(url, timeout=20, retry=3)
        if not data or "result" not in data or "data" not in data["result"]:
            print("❌ API返回数据格式不正确")
            return
        
        indicator_data = data["result"]["data"]
        print(f"✅ 成功获取{len(indicator_data)}条财务指标数据")
        
        # 打印所有数据的报告日期，了解有哪些季度/年度数据
        print("\n" + "="*60)
        print("所有报告日期:")
        report_dates = []
        for item in indicator_data:
            if "STD_REPORT_DATE" in item:
                report_date = item["STD_REPORT_DATE"]
                report_dates.append(report_date)
                print(f"  - {report_date} (DATE_TYPE_CODE: {item.get('DATE_TYPE_CODE', 'N/A')})")
        
        # 分析第一条数据的所有字段
        print("\n" + "="*60)
        print("第一条数据的所有字段:")
        first_item = indicator_data[0]
        for key, value in first_item.items():
            print(f"  {key}: {value} (类型: {type(value).__name__})")
        
        # 查找杜邦分析相关字段
        print("\n" + "="*60)
        print("杜邦分析相关字段:")
        dupont_fields = [
            "NETPROFITMARGIN",  # 销售净利率
            "TOTALASSETTURNOVER",  # 总资产周转率
            "ASSETEQUITYRATIO",  # 权益乘数
            "ROE",  # 净资产收益率
            "GROSSMARGIN",  # 毛利率
            "OPERATINGMARGIN",  # 营业利润率
            "NETPROFIT",  # 净利润
            "TOTALOPERATINGREVENUE",  # 营业总收入
            "TOTALASSETS",  # 总资产
            "TOTAL_EQUITY"  # 总权益
        ]
        
        # 检查这些字段是否存在
        available_dupont_fields = []
        for field in dupont_fields:
            if field in first_item:
                available_dupont_fields.append(field)
                print(f"  ✅ {field}: {first_item[field]} ({type(first_item[field]).__name__})")
        
        # 统计可用字段
        print(f"\n可用的杜邦分析字段: {len(available_dupont_fields)}/{len(dupont_fields)}")
        
        # 按报告日期分组，看看每个日期有哪些数据
        print("\n" + "="*60)
        print("按报告日期分组的数据:")
        date_groups = {}
        for item in indicator_data:
            date = item["STD_REPORT_DATE"]
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(item)
        
        for date, items in date_groups.items():
            print(f"\n报告日期: {date} ({len(items)}条数据)")
            for item in items:
                # 打印关键财务指标
                roe = item.get("ROE", "N/A")
                netprofitmargin = item.get("NETPROFITMARGIN", "N/A")
                totalassetturnover = item.get("TOTALASSETTURNOVER", "N/A")
                assetequityratio = item.get("ASSETEQUITYRATIO", "N/A")
                date_type = item.get("DATE_TYPE_CODE", "N/A")
                
                print(f"  类型: {date_type}, ROE: {roe}, 净利率: {netprofitmargin}, 总资产周转率: {totalassetturnover}, 权益乘数: {assetequityratio}")
        
        # 检查DATE_TYPE_CODE的含义
        print("\n" + "="*60)
        print("DATE_TYPE_CODE含义分析:")
        date_types = set()
        for item in indicator_data:
            date_types.add(item.get("DATE_TYPE_CODE", "N/A"))
        print(f"  所有类型: {date_types}")
        
        # 推测类型含义
        type_meanings = {
            "001": "年报",
            "002": "中报", 
            "003": "一季报",
            "004": "三季报"
        }
        for date_type in date_types:
            print(f"  {date_type}: {type_meanings.get(date_type, '未知')}")
        
        # 保存简化的分析结果
        simplified_data = {
            "report_dates": report_dates,
            "available_dupont_fields": available_dupont_fields,
            "date_type_meanings": type_meanings,
            "first_item_sample": {k: v for k, v in first_item.items() if k in available_dupont_fields + ["STD_REPORT_DATE", "DATE_TYPE_CODE"]}
        }
        
        with open("hk_dupont_analysis_result.json", "w", encoding="utf-8") as f:
            json.dump(simplified_data, f, ensure_ascii=False, indent=2)
        print(f"\n📁 分析结果已保存到: hk_dupont_analysis_result.json")
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")

if __name__ == "__main__":
    analyze_hk_main_indicator()
