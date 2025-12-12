#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试港股行情API返回结构，查看是否包含总市值或总股本信息
"""

import sys
import os
import logging
import time
import random
from urllib.parse import quote

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from stock import fetch_url

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_hk_quotes(stock_code):
    """测试港股行情API返回结构"""
    logger.info(f"测试港股{stock_code}行情API")
    
    # 港股URL格式
    random_num = random.random()  # 生成0到1之间的随机浮点数
    full_stock_code = stock_code.zfill(5)  # 确保是5位代码
    sina_list = f"rt_hk{full_stock_code},rt_hkHSI,rt_hk{full_stock_code}_preipo,rt_hkHSI_preipo"
    sina_url = f"https://hq.sinajs.cn/?_={random_num}&list={sina_list}"
    
    try:
        # 获取原始数据
        hq_data = fetch_url(sina_url, is_sina_var=True, retry=3)
        
        if hq_data:
            logger.info(f"原始数据: {hq_data}")
            
            # 解析数据
            if isinstance(hq_data, dict):
                for key, value in hq_data.items():
                    logger.info(f"\n{key} 字段数量: {len(value)}")
                    logger.info(f"字段值: {value}")
                    logger.info(f"详细字段列表:")
                    for i, item in enumerate(value):
                        logger.info(f"  [{i}]: {item}")
        else:
            logger.error("未获取到数据")
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # 测试腾讯控股
    test_hk_quotes("00700")
