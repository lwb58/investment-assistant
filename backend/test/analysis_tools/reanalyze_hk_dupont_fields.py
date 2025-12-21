import requests
import json
import logging
from urllib3.exceptions import InsecureRequestWarning

# 忽略不安全请求警告
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_hk_dupont_data(stock_code):
    """获取港股杜邦分析相关字段的详细信息"""
    try:
        secucode = f"{stock_code}.HK"
        url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_MAININDICATOR&columns=ALL&quoteColumns=&filter=(SECUCODE%3D%22{secucode}%22)&pageNumber=1&pageSize=5&sortTypes=-1&sortColumns=STD_REPORT_DATE&source=F10&client=PC&v=040146104118736425"
        
        logger.info(f"请求港股数据: {stock_code}, URL: {url}")
        
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data
    except Exception as e:
        logger.error(f"获取港股数据失败: {str(e)}")
        return None

def analyze_hk_dupont_fields(stock_code):
    """分析港股杜邦分析相关字段"""
    logger.info(f"开始分析港股{stock_code}的杜邦分析字段")
    
    # 获取数据
    data = fetch_hk_dupont_data(stock_code)
    if not data or "result" not in data:
        logger.error(f"获取不到港股{stock_code}的数据")
        return
    
    financial_records = data["result"].get("data", [])
    if not financial_records:
        logger.error(f"港股{stock_code}没有财务数据")
        return
    
    # 获取第一条记录，查看所有字段
    first_record = financial_records[0]
    all_fields = list(first_record.keys())
    
    logger.info(f"港股{stock_code} API返回的所有字段 ({len(all_fields)}个):")
    for i, field in enumerate(sorted(all_fields)):
        value = first_record[field]
        logger.info(f"  {i+1:2d}. {field}: {value} (类型: {type(value).__name__})")
    
    # 特别查找与毛利率、净利率相关的字段
    profit_fields = []
    for field in all_fields:
        lower_field = field.lower()
        if any(keyword in lower_field for keyword in ['profit', 'margin', 'rate', 'gross', 'net']):
            profit_fields.append(field)
    
    logger.info(f"\n与利润相关的字段 ({len(profit_fields)}个):")
    for field in sorted(profit_fields):
        value = first_record[field]
        logger.info(f"  {field}: {value} (类型: {type(value).__name__})")
    
    # 查看报告日期相关字段
    date_fields = []
    for field in all_fields:
        lower_field = field.lower()
        if any(keyword in lower_field for keyword in ['date', 'period']):
            date_fields.append(field)
    
    logger.info(f"\n与日期相关的字段 ({len(date_fields)}个):")
    for field in sorted(date_fields):
        value = first_record[field]
        logger.info(f"  {field}: {value}")
    
    # 保存完整数据到文件以便进一步分析
    output_file = f"hk_dupont_fields_{stock_code}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(financial_records, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n完整数据已保存到: {output_file}")
    logger.info(f"分析完成，共获取 {len(financial_records)} 条记录")

if __name__ == "__main__":
    # 测试港股代码
    hk_stock_codes = ["02367"]  # 巨子生物
    
    for stock_code in hk_stock_codes:
        logger.info(f"\n{'='*80}")
        logger.info(f"分析港股代码: {stock_code}")
        logger.info(f"{'='*80}")
        analyze_hk_dupont_fields(stock_code)
