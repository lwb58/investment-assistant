import json
from util import fetch_url

def find_dupont_fields():
    """查找港股主要财务指标API中的杜邦分析相关字段"""
    url = "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_MAININDICATOR&columns=ALL&quoteColumns=&filter=(SECUCODE%3D%2202367.HK%22)&pageNumber=1&pageSize=9&sortTypes=-1&sortColumns=STD_REPORT_DATE&source=F10&client=PC&v=040146104118736425"
    
    try:
        data = fetch_url(url, timeout=20, retry=3)
        if not data or "result" not in data or "data" not in data["result"]:
            print("❌ API返回数据格式不正确")
            return
        
        indicator_data = data["result"]["data"]
        if not indicator_data:
            print("❌ API返回数据为空")
            return
        
        print(f"✅ 成功获取{len(indicator_data)}条财务指标数据")
        
        # 获取所有唯一字段名
        all_fields = set()
        for item in indicator_data:
            all_fields.update(item.keys())
        
        print(f"\n所有唯一字段名 ({len(all_fields)}个):")
        sorted_fields = sorted(all_fields)
        for field in sorted_fields:
            print(f"  - {field}")
        
        # 查找可能的杜邦分析相关字段
        print("\n" + "="*60)
        print("查找可能的杜邦分析相关字段:")
        
        # 关键词列表
        keywords = [
            "ROE", "ROA", "NET", "PROFIT", "MARGIN", "TURNOVER", 
            "ASSET", "EQUITY", "MULTIPLIER", "RATIO", "GROSS", 
            "OPERATING", "INCOME", "REVENUE", "COST"
        ]
        
        potential_dupont_fields = []
        for field in sorted_fields:
            field_upper = field.upper()
            for keyword in keywords:
                if keyword in field_upper:
                    potential_dupont_fields.append(field)
                    break
        
        print(f"\n找到{len(potential_dupont_fields)}个可能的杜邦分析相关字段:")
        for field in potential_dupont_fields:
            # 显示该字段在数据中的值示例
            sample_values = []
            for item in indicator_data:
                if field in item and item[field] is not None:
                    sample_values.append(str(item[field]))
                    if len(sample_values) >= 2:  # 只显示前2个示例
                        break
            
            if sample_values:
                sample_text = f"示例值: {', '.join(sample_values)}"
            else:
                sample_text = "示例值: None"
                
            print(f"  - {field} ({sample_text})")
        
        # 特别关注ROE、销售净利率、总资产周转率、权益乘数
        print("\n" + "="*60)
        print("关键杜邦分析指标详细信息:")
        
        key_metrics = {
            "ROE": "净资产收益率",
            "NET_PROFIT_MARGIN": "销售净利率",
            "OPERATING_MARGIN": "营业利润率",
            "GROSS_PROFIT_MARGIN": "毛利率",
            "TOTAL_ASSET_TURNOVER": "总资产周转率",
            "EQUITY_MULTIPLIER": "权益乘数",
            "ASSET_EQUITY_RATIO": "权益乘数(资产/权益)"
        }
        
        for field, description in key_metrics.items():
            print(f"\n{field} ({description}):")
            for item in indicator_data:
                if field in item:
                    report_date = item.get("STD_REPORT_DATE", "N/A")
                    value = item[field]
                    date_type = item.get("DATE_TYPE_CODE", "N/A")
                    print(f"  {report_date} (类型: {date_type}): {value}")
        
        # 保存结果到文件
        result = {
            "all_fields": sorted_fields,
            "potential_dupont_fields": potential_dupont_fields,
            "key_metrics": key_metrics
        }
        
        with open("hk_potential_dupont_fields.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 分析结果已保存到: hk_potential_dupont_fields.json")
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")

if __name__ == "__main__":
    find_dupont_fields()
