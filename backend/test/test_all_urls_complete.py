import requests
import json
import os
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建结果目录
result_dir = "d:\\yypt\\xingziyuan\\investment-assistant\\backend\\test\\url_test_results"
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

# 测试股票
TEST_STOCKS = {
    "伯特利": "603596",
    "巨子生物": "02367"
}

# 测试函数装饰器，用于保存结果到MD文件
def save_result_to_md(func):
    def wrapper(*args, **kwargs):
        stock_name, stock_id = args
        result = func(*args, **kwargs)
        if result:
            url_name, url, response, success = result
            
            # 创建MD文件名
            md_filename = f"{result_dir}\\{stock_name}_{stock_id}_{url_name.replace(' ', '_')}_result.md"
            
            # 写入MD文件
            with open(md_filename, "w", encoding="utf-8") as f:
                f.write(f"# {stock_name}({stock_id}) - {url_name}\n\n")
                f.write(f"## URL\n")
                f.write(f"`{url}`\n\n")
                f.write(f"## 请求状态\n")
                f.write(f"{'✅ 成功' if success else '❌ 失败'}\n\n")
                if success:
                    f.write(f"## 响应状态码\n")
                    f.write(f"`{response.status_code}`\n\n")
                    f.write(f"## 响应头\n")
                    f.write("```\n")
                    for key, value in response.headers.items():
                        f.write(f"{key}: {value}\n")
                    f.write("```\n\n")
                    f.write(f"## 响应内容\n")
                    try:
                        json_data = response.json()
                        f.write("```json\n")
                        f.write(json.dumps(json_data, ensure_ascii=False, indent=2))
                        f.write("\n```\n")
                    except json.JSONDecodeError:
                        f.write("```\n")
                        f.write(response.text)
                        f.write("\n```\n")
                else:
                    f.write(f"## 错误信息\n")
                    f.write(f"`{str(response)}`\n")
            
            logger.info(f"测试结果已保存到 {md_filename}")
    return wrapper

# 通用请求函数
def make_request(url, headers=None, params=None, method="GET", timeout=10):
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=timeout, verify=False)
        elif method == "POST":
            response = requests.post(url, headers=headers, params=params, timeout=timeout, verify=False)
        return response
    except Exception as e:
        logger.error(f"请求失败: {str(e)}")
        return e

# 测试东方财富主要指标URL（港股）
@save_result_to_md
def test_eastmoney_main_indicator_hk(stock_name, stock_id):
    url_name = "东方财富港股主要指标"
    url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_CUSTOM_HKF10_FN_MAININDICATORMAX&columns=ORG_CODE%2CSECUCODE%2CSECURITY_CODE%2CSECURITY_NAME_ABBR%2CSECURITY_INNER_CODE%2CREPORT_DATE%2CBASIC_EPS%2CPER_NETCASH_OPERATE%2CBPS%2CBPS_NEDILUTED%2CCOMMON_ACS%2CPER_SHARES%2CISSUED_COMMON_SHARES%2CHK_COMMON_SHARES%2CTOTAL_MARKET_CAP%2CHKSK_MARKET_CAP%2COPERATE_INCOME%2COPERATE_INCOME_SQ%2COPERATE_INCOME_QOQ%2COPERATE_INCOME_QOQ_SQ%2CHOLDER_PROFIT%2CHOLDER_PROFIT_SQ%2CHOLDER_PROFIT_QOQ%2CHOLDER_PROFIT_QOQ_SQ%2CPE_TTM%2CPE_TTM_SQ%2CPB_TTM%2CPB_TTM_SQ%2CNET_PROFIT_RATIO%2CNET_PROFIT_RATIO_SQ%2CROE_AVG%2CROE_AVG_SQ%2CROA%2CROA_SQ%2CDIVIDEND_TTM%2CDIVIDEND_LFY%2CDIVI_RATIO%2CDIVIDEND_RATE%2CIS_CNY_CODE&filter=(SECUCODE%3D%22{stock_id}.HK%22)&pageNumber=1&pageSize=1&sortTypes=-1&sortColumns=REPORT_DATE&source=F10&client=PC&v=06695186382178545"
    response = make_request(url)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试东方财富行情URL（A股）
@save_result_to_md
def test_eastmoney_quote_a(stock_name, stock_id):
    url_name = "东方财富A股行情"
    secid = f"1.{stock_id}"  # A股沪市
    url = f"https://push2.eastmoney.com/api/qt/stock/get?fields=f57%2Cf58%2Cf43%2Cf44%2Cf45%2Cf46%2Cf47%2Cf48%2Cf50%2Cf164%2Cf168%2Cf170%2Cf171%2Cf179%2Cf183&secid={secid}&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&wbp2u=%7C0%7C0%7C0%7Cweb&v=09371029070054959"
    response = make_request(url)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试东方财富行情URL（港股）
@save_result_to_md
def test_eastmoney_quote_hk(stock_name, stock_id):
    url_name = "东方财富港股行情"
    secid = f"116.{stock_id}"  # 港股
    url = f"https://push2.eastmoney.com/api/qt/stock/get?fields=f57%2Cf58%2Cf43%2Cf44%2Cf45%2Cf46%2Cf47%2Cf48%2Cf50%2Cf164%2Cf168%2Cf170%2Cf171%2Cf179%2Cf183&secid={secid}&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&wbp2u=%7C0%7C0%7C0%7Cweb&v=09371029070054959"
    response = make_request(url)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试东方财富港股F10主要指标URL
@save_result_to_md
def test_eastmoney_hk_main_indicator(stock_name, stock_id):
    url_name = "东方财富港股F10主要指标"
    secucode = f"{stock_id}.HK"
    url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_MAININDICATOR&columns=ALL&quoteColumns=&filter=(SECUCODE%3D%22{secucode}%22)&pageNumber=1&pageSize=9&sortTypes=-1&sortColumns=STD_REPORT_DATE&source=F10&client=PC&v=040146104118736425"
    response = make_request(url)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试新浪杜邦分析URL（A股）
@save_result_to_md
def test_sina_dupont_a(stock_name, stock_id):
    url_name = "新浪A股杜邦分析"
    displaytype = 4  # 年报
    url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vFD_DupontAnalysis/stockid/{stock_id}/displaytype/{displaytype}.phtml"
    headers = {
        "Referer": "https://finance.sina.com.cn/"
    }
    response = make_request(url, headers=headers)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试新浪行情URL
@save_result_to_md
def test_sina_quote(stock_name, stock_id):
    url_name = "新浪行情"
    # 根据股票代码判断市场
    if len(stock_id) == 6 and stock_id.startswith(('6', '5')):
        sina_list = f"sh{stock_id}"  # 沪A
    elif len(stock_id) == 6:
        sina_list = f"sz{stock_id}"  # 深A
    else:
        sina_list = f"hk{stock_id}"  # 港股
    url = f"https://hq.sinajs.cn/?_={int(time.time()*1000)}&list={sina_list}"
    response = make_request(url)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试新浪搜索URL
@save_result_to_md
def test_sina_search(stock_name, stock_id):
    url_name = "新浪股票搜索"
    encoded_keyword = stock_id
    timestamp = int(time.time()*1000)
    url = f"https://suggest3.sinajs.cn/suggest/type=&key={encoded_keyword}&name=suggestdata_{timestamp}"
    headers = {
        "Referer": "https://finance.sina.com.cn/"
    }
    response = make_request(url, headers=headers)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试新浪财务报告URL
@save_result_to_md
def test_sina_finance_report(stock_name, stock_id):
    url_name = "新浪财务报告"
    # 根据股票代码判断市场
    if len(stock_id) == 6 and stock_id.startswith(('6', '5')):
        paper_code = f"sh{stock_id}"  # 沪A
    elif len(stock_id) == 6:
        paper_code = f"sz{stock_id}"  # 深A
    else:
        paper_code = f"hk{stock_id}"  # 港股
    url = f"https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022?paperCode={paper_code}&source=lrb&type=0&page=1&num=10"
    response = make_request(url)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试新浪财经搜索URL
@save_result_to_md
def test_sina_finance_search(stock_name, stock_id):
    url_name = "新浪财经搜索"
    url = f"https://biz.finance.sina.com.cn/suggest/lookup_n.php?country=stock&q={stock_id}"
    headers = {
        "Referer": "https://finance.sina.com.cn/"
    }
    response = make_request(url, headers=headers)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试腾讯行情URL
@save_result_to_md
def test_tencent_quote(stock_name, stock_id):
    url_name = "腾讯行情"
    # 根据股票代码判断市场
    if len(stock_id) == 6 and stock_id.startswith(('6', '5')):
        tencent_code = f"sh{stock_id}"  # 沪A
    elif len(stock_id) == 6:
        tencent_code = f"sz{stock_id}"  # 深A
    else:
        tencent_code = f"hk{stock_id}"  # 港股
    url = f"http://qt.gtimg.cn/q={tencent_code}"
    response = make_request(url)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试腾讯上海板块行情URL
@save_result_to_md
def test_tencent_sh_board(stock_name, stock_id):
    url_name = "腾讯上海板块行情"
    random_r = int(time.time()*1000)
    url = f"https://qt.gtimg.cn/r={random_r}&q=bkqtRank_A_sh"
    headers = {
        "Referer": "https://finance.sina.com.cn/"
    }
    response = make_request(url, headers=headers)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试腾讯深圳板块行情URL
@save_result_to_md
def test_tencent_sz_board(stock_name, stock_id):
    url_name = "腾讯深圳板块行情"
    random_r = int(time.time()*1000)
    url = f"https://qt.gtimg.cn/r={random_r}&q=bkqtRank_A_sz"
    headers = {
        "Referer": "https://finance.sina.com.cn/"
    }
    response = make_request(url, headers=headers)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试腾讯创业板分钟数据URL
@save_result_to_md
def test_tencent_cyb_minute(stock_name, stock_id):
    url_name = "腾讯创业板分钟数据"
    random_r = int(time.time()*1000)
    url = f"https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_sz399006&code=sz399006&r={random_r}"
    headers = {
        "Referer": "https://finance.sina.com.cn/"
    }
    response = make_request(url, headers=headers)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试新浪行业URL
@save_result_to_md
def test_sina_industry(stock_name, stock_id):
    url_name = "新浪行业数据"
    random_num = int(time.time()*1000)
    url = f"https://hq.sinajs.cn/ran={random_num}&format=json&list=sinaindustry_up,sinaindustry_down"
    response = make_request(url)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 测试新浪概念URL
@save_result_to_md
def test_sina_concept(stock_name, stock_id):
    url_name = "新浪概念数据"
    random_num = int(time.time()*1000)
    url = f"https://hq.sinajs.cn/ran={random_num}&format=json&list=si_api4,si_api5,si_api6,si_api7"
    response = make_request(url)
    success = isinstance(response, requests.Response) and response.status_code == 200
    return url_name, url, response, success

# 主测试函数
def main():
    logger.info("开始测试所有URL")
    
    for stock_name, stock_id in TEST_STOCKS.items():
        logger.info(f"\n=== 开始测试 {stock_name}({stock_id}) ===")
        
        # 东方财富URL
        test_eastmoney_quote_a(stock_name, stock_id)
        test_eastmoney_quote_hk(stock_name, stock_id)
        test_eastmoney_hk_main_indicator(stock_name, stock_id)
        
        # 新浪URL
        test_sina_dupont_a(stock_name, stock_id)
        test_sina_quote(stock_name, stock_id)
        test_sina_search(stock_name, stock_id)
        test_sina_finance_report(stock_name, stock_id)
        test_sina_finance_search(stock_name, stock_id)
        test_sina_industry(stock_name, stock_id)
        test_sina_concept(stock_name, stock_id)
        
        # 腾讯URL
        test_tencent_quote(stock_name, stock_id)
        test_tencent_sh_board(stock_name, stock_id)
        test_tencent_sz_board(stock_name, stock_id)
        test_tencent_cyb_minute(stock_name, stock_id)
        
        logger.info(f"=== 完成测试 {stock_name}({stock_id}) ===")
    
    logger.info("\n所有URL测试完成")

if __name__ == "__main__":
    main()
