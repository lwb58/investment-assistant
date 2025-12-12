#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的港股财务数据获取函数
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from stock import _get_hk_stock_financial_data

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_hk_financial_data():
    """测试港股财务数据获取函数"""
    logger.info("开始测试港股财务数据获取函数...")
    
    # 测试的港股股票代码（02367.HK - 天味食品港股）
    stock_codes = ["02367", "00700", "09988"]
    
    for stock_code in stock_codes:
        logger.info(f"\n测试股票代码: {stock_code}")
        
        try:
            start_time = datetime.now()
            financial_data = _get_hk_stock_financial_data(stock_code)
            end_time = datetime.now()
            
            logger.info(f"获取耗时: {(end_time - start_time).total_seconds():.2f}秒")
            logger.info(f"返回数据类型: {type(financial_data)}")
            logger.info(f"返回数据: {financial_data}")
            
            # 验证返回数据格式
            if financial_data:
                logger.info("✅ 数据获取成功")
                
                # 检查年份数据
                years = [key for key in financial_data.keys() if key.isdigit()]
                if years:
                    latest_year = years[0]
                    logger.info(f"最新年份: {latest_year}")
                    
                    # 检查财务指标是否完整
                    required_indicators = [
                        "revenue", "revenueGrowth", "netProfit", "netProfitGrowth",
                        "eps", "navps", "roe", "pe", "pb", "grossMargin", "netMargin", "debtRatio"
                    ]
                    
                    if latest_year in financial_data:
                        missing_indicators = [ind for ind in required_indicators 
                                            if ind not in financial_data[latest_year]]
                        
                        if missing_indicators:
                            logger.warning(f"❌ 缺少指标: {missing_indicators}")
                        else:
                            logger.info("✅ 所有财务指标完整")
                            
                            # 打印关键指标值
                            logger.info(f"营业收入: {financial_data[latest_year]['revenue']}")
                            logger.info(f"净利润: {financial_data[latest_year]['netProfit']}")
                            logger.info(f"EPS: {financial_data[latest_year]['eps']}")
                            logger.info(f"ROE: {financial_data[latest_year]['roe']}")
                            logger.info(f"市盈率: {financial_data[latest_year]['pe']}")
                            logger.info(f"市净率: {financial_data[latest_year]['pb']}")
                
                # 检查毛利率和净利率数据结构
                if "mllsj" in financial_data:
                    logger.info("✅ 毛利率和净利率数据结构完整")
                    logger.info(f"mllsj数据: {financial_data['mllsj']}")
                else:
                    logger.warning("❌ 缺少毛利率和净利率数据结构")
            else:
                logger.warning("❌ 返回空数据")
                
        except Exception as e:
            logger.error(f"❌ 测试失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_hk_financial_data()
