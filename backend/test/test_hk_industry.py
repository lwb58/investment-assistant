import json
import logging
from util import fetch_url

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_hk_industry_api(stock_code):
    """测试获取港股行业信息"""
    logger.info(f"测试获取港股{stock_code}行业信息")
    
    # 构造东方财富网港股基本信息API URL
    secucode = f"{stock_code}.HK"
    
    # 尝试获取财务数据，查看完整字段列表
    finance_url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_MAININDICATOR&columns=ALL&quoteColumns=&filter=(SECUCODE%3D%22{secucode}%22)&pageNumber=1&pageSize=1&sortTypes=-1&sortColumns=STD_REPORT_DATE&source=F10&client=PC&v=040146104118736425"
    
    try:
        # 获取财务数据
        finance_data = fetch_url(finance_url, retry=3, timeout=20)
        if not finance_data:
            logger.error("API返回空数据")
            return None
        
        logger.info("财务数据API返回数据结构:")
        logger.info(json.dumps(finance_data, ensure_ascii=False, indent=2))
        
        if finance_data and 'result' in finance_data and 'data' in finance_data['result']:
            data = finance_data['result']['data']
            if data:
                logger.info("\n财务数据字段列表:")
                for key, value in data[0].items():
                    logger.info(f"{key}: {value}")
        
        return finance_data
        
    except Exception as e:
        logger.error(f"API调用失败: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    # 测试用的港股代码
    test_stock_code = "02367"
    test_hk_industry_api(test_stock_code)
