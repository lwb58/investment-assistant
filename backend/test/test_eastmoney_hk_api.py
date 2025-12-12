import json
import logging
import sys
from util import fetch_url

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_eastmoney_hk_api(stock_code):
    """测试东方财富网港股API接口"""
    logger.info(f"测试东方财富网港股API接口: {stock_code}")
    
    # 构造主要财务指标API URL
    secucode = f"{stock_code}.HK"
    main_indicator_url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_MAININDICATOR&columns=ALL&quoteColumns=&filter=(SECUCODE%3D%22{secucode}%22)&pageNumber=1&pageSize=9&sortTypes=-1&sortColumns=STD_REPORT_DATE&source=F10&client=PC&v=040146104118736425"
    
    try:
        # 获取主要财务指标数据
        data = fetch_url(main_indicator_url, retry=3, timeout=20)
        if not data:
            logger.error("API返回空数据")
            return None
        
        # 打印数据结构
        logger.info("API返回数据结构:")
        logger.info(f"总页数: {data.get('result', {}).get('pages', 0)}")
        logger.info(f"数据数量: {data.get('result', {}).get('count', 0)}")
        
        if 'data' in data.get('result', {}):
            logger.info(f"第一页数据数量: {len(data['result']['data'])}")
            
            # 打印第一条数据的所有字段
            if data['result']['data']:
                logger.info("\n第一条数据字段:")
                first_item = data['result']['data'][0]
                for key, value in first_item.items():
                    logger.info(f"{key}: {value}")
                    
            # 提取我们需要的财务指标
            logger.info("\n提取的财务指标:")
            for item in data['result']['data']:
                report_date = item.get('REPORT_DATE', '')
                logger.info(f"\n报告日期: {report_date}")
                logger.info(f"营业收入: {item.get('OPERATE_INCOME', '')}")
                logger.info(f"净利润: {item.get('HOLDER_PROFIT', '')}")
                logger.info(f"基本每股收益: {item.get('BASIC_EPS', '')}")
                logger.info(f"每股净资产: {item.get('BPS', '')}")
                logger.info(f"净资产收益率: {item.get('ROE_AVG', '')}")
                logger.info(f"毛利率: {item.get('GROSS_PROFIT_RATIO', '')}")
                logger.info(f"净利率: {item.get('NET_PROFIT_RATIO', '')}")
                logger.info(f"资产负债率: {item.get('DEBT_ASSET_RATIO', '')}")
                logger.info(f"市盈率: {item.get('PE_TTM', '')}")
                logger.info(f"市净率: {item.get('PB_TTM', '')}")
        
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"API调用失败: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    # 测试用的港股代码
    test_stock_code = "02367"
    test_eastmoney_hk_api(test_stock_code)
