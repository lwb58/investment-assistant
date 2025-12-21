import sys
import os
import requests
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入URL常量
from stock import (
    EASTMONEY_HK_MAIN_INDICATOR_MAX_URL,
    EASTMONEY_QUOTE_URL,
    EASTMONEY_HK_MAIN_INDICATOR_URL,
    SINA_DUPONT_ANALYSIS_URL,
    SINA_QUOTE_URL_HK,
    SINA_QUOTE_URL_A,
    SINA_SEARCH_URL,
    SINA_FINANCE_SEARCH_URL,
    SINA_SEARCH_SUGGEST_URL,
    TENCENT_QUOTE_URL
)
from util import (
    SINA_FINANCE_API_URL,
    SINA_INDUSTRY_URL,
    SINA_CONCEPT_URL,
    SINA_HTTP_HQ_URL,
    TENCENT_BKQT_RANK_SH_URL,
    TENCENT_BKQT_RANK_SZ_URL,
    TENCENT_MINUTE_QUERY_URL
)

# 测试股票代码
TEST_STOCKS = {
    "伯特利": "603596",  # A股
    "巨子生物": "02367"   # 港股
}

# 测试结果保存目录
RESULT_DIR = r"d:\yypt\xingziyuan\investment-assistant\backend\test\url_test_results"
os.makedirs(RESULT_DIR, exist_ok=True)

def test_url(url, stock_name, stock_code, url_name, headers=None):
    """测试单个URL并保存结果"""
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        # 保存结果
        result_file = os.path.join(RESULT_DIR, f"{stock_name}_{stock_code}_{url_name}_result.md")
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"# {stock_name}({stock_code}) {url_name} 测试结果\n\n")
            f.write(f"## URL\n```\n{url}\n```\n\n")
            f.write(f"## 返回状态码\n{response.status_code}\n\n")
            f.write(f"## 返回内容\n```json\n{response.text[:2000]}...\n```\n\n")
            f.write(f"## 测试时间\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"✅ {stock_name}({stock_code}) {url_name} 测试成功")
        return True
    except Exception as e:
        print(f"❌ {stock_name}({stock_code}) {url_name} 测试失败: {e}")
        return False

def main():
    print("开始测试所有URL...")
    
    # 通用请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://finance.sina.com.cn/"
    }
    
    for stock_name, stock_code in TEST_STOCKS.items():
        print(f"\n--- 开始测试 {stock_name}({stock_code}) ---")
        
        if stock_code.startswith(('0', '3')):  # 深市A股
            market = "sz"
            secid = f"0.{stock_code}"
        elif stock_code.startswith('6'):  # 沪市A股
            market = "sh"
            secid = f"1.{stock_code}"
        else:  # 港股
            market = "rt_hk"
            secid = f"116.{stock_code}"
        
        # 东方财富URL测试
        if market == "rt_hk":  # 港股特有URL
            test_url(
                EASTMONEY_HK_MAIN_INDICATOR_MAX_URL.format(stock_id=stock_code),
                stock_name, stock_code, "东方财富主指标最大值"
            )
            test_url(
                EASTMONEY_HK_MAIN_INDICATOR_URL.format(secucode=f"{stock_code}.HK"),
                stock_name, stock_code, "东方财富港股主指标"
            )
        
        test_url(
            EASTMONEY_QUOTE_URL.format(secid=secid),
            stock_name, stock_code, "东方财富行情"
        )
        
        # 新浪URL测试
        test_url(
            SINA_DUPONT_ANALYSIS_URL.format(stock_id=stock_code, displaytype=1),
            stock_name, stock_code, "新浪杜邦分析"
        )
        
        if market == "rt_hk":  # 港股
            test_url(
                SINA_QUOTE_URL_HK.format(random_num=123456789, sina_list=f"rt_hk{stock_code},rt_hk{stock_code}_preipo"),
                stock_name, stock_code, "新浪港股行情"
            )
        else:  # A股
            test_url(
                SINA_QUOTE_URL_A.format(random_num=1234567890, sina_list=f"{market}{stock_code},{market}{stock_code}_i"),
                stock_name, stock_code, "新浪A股行情"
            )
        
        test_url(
            SINA_FINANCE_SEARCH_URL.format(stock_code=stock_code),
            stock_name, stock_code, "新浪财经搜索"
        )
        
        test_url(
            SINA_SEARCH_SUGGEST_URL.format(stock_code=stock_code, random_num=123456789),
            stock_name, stock_code, "新浪搜索建议"
        )
        
        # 腾讯URL测试
        if market == "rt_hk":
            test_url(
                TENCENT_QUOTE_URL.format(tencent_code=f"hk{stock_code}"),
                stock_name, stock_code, "腾讯行情"
            )
        else:
            test_url(
                TENCENT_QUOTE_URL.format(tencent_code=f"{market}{stock_code}"),
                stock_name, stock_code, "腾讯行情"
            )
        
    # 通用URL测试（不依赖具体股票）
    print("\n--- 开始测试通用URL ---")
    
    # 新浪财务API
    test_url(
        SINA_FINANCE_API_URL + "?paperCode=sh600000&source=lrb&type=0&page=1&num=10",
        "通用测试", "600000", "新浪财务API",
        headers=headers
    )
    
    # 新浪行业和概念URL
    test_url(
        SINA_INDUSTRY_URL.format(random_num=123456789),
        "通用测试", "", "新浪行业数据",
        headers=headers
    )
    
    test_url(
        SINA_CONCEPT_URL.format(random_num=123456789),
        "通用测试", "", "新浪概念数据",
        headers=headers
    )
    
    # 新浪HTTP行情URL
    test_url(
        SINA_HTTP_HQ_URL.format(code="sh600000"),
        "通用测试", "600000", "新浪HTTP行情"
    )
    
    # 腾讯板块行情URL
    test_url(
        TENCENT_BKQT_RANK_SH_URL.format(random_r=123456789),
        "通用测试", "", "腾讯上海板块行情"
    )
    
    test_url(
        TENCENT_BKQT_RANK_SZ_URL.format(random_r=123456789),
        "通用测试", "", "腾讯深圳板块行情"
    )
    
    # 腾讯分钟数据URL
    test_url(
        TENCENT_MINUTE_QUERY_URL.format(random_r=123456789),
        "通用测试", "", "腾讯创业板分钟数据"
    )
    
    print("\n所有URL测试完成！结果保存在:", RESULT_DIR)

if __name__ == "__main__":
    main()
