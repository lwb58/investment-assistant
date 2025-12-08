#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例：直接返回新浪财经API的完整原始数据，不进行任何解析
"""

import sys
import os
import logging
import json
from datetime import datetime

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from util import fetch_url, get_stock_market

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_raw_financial_data(stock_code: str):
    """直接获取并返回新浪财经API的完整原始数据"""
    market = get_stock_market(stock_code)
    if not market:
        logger.error(f"股票市场不支持：{stock_code}")
        return None
    
    # 拼接 paperCode（market+股票代码，如 sh601669）
    paper_code = f"{market}{stock_code}"
    # 报表类型（lrb=利润表，核心财务数据来源）
    report_type = "gjzb"  # lrb-利润表、zcfz-资产负债表、xjll-现金流量表
    
    try:
        # 构造URL，使用固定的getFinanceReport2022接口路径
        url = (
            f"https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
            f"?paperCode={paper_code}&source={report_type}&type=0&page=1&num=10"
        )
        logger.info(f"请求财务数据：{url}")
        
        # 调用fetch_url获取原始数据
        raw_data = fetch_url(url, timeout=20, is_sina_var=True)
        
        if not raw_data:
            logger.warning(f"财务数据接口返回空或格式错误：{stock_code}")
            return None
        
        logger.info("成功获取到原始财务数据")
        logger.info(f"数据类型: {type(raw_data)}")
        logger.info(f"数据大小: {sys.getsizeof(raw_data)} bytes")
        
        # 将原始数据写入JSON文件
        try:
            # 创建输出目录（如果不存在）
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"raw_financial_data_{stock_code}_{timestamp}.json"
            file_path = os.path.join(output_dir, file_name)
            
            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                if isinstance(raw_data, dict):
                    json.dump(raw_data, f, ensure_ascii=False, indent=2)
                else:
                    # 如果不是字典类型，尝试解析
                    try:
                        parsed_data = json.loads(raw_data)
                        json.dump(parsed_data, f, ensure_ascii=False, indent=2)
                    except json.JSONDecodeError:
                        # 如果无法解析，直接写入原始字符串
                        f.write(raw_data)
            
            logger.info(f"原始财务数据已保存到文件: {file_path}")
            
        except Exception as e:
            logger.error(f"保存财务数据到文件时发生错误：{e}", exc_info=True)
        
        return raw_data
    
    except Exception as e:
        logger.error(f"获取原始财务数据时发生错误：{e}", exc_info=True)
        return None

if __name__ == "__main__":
    # 测试股票代码（可修改为其他股票代码）
    test_stock = "002920"  # 中国平安
    
    logger.info(f"开始测试获取股票 {test_stock} 的原始财务数据")
    
    # 获取原始数据
    raw_data = test_raw_financial_data(test_stock)
    
    if raw_data:
        logger.info("\n=== 原始数据完整内容 ===")
        logger.info(raw_data)
        logger.info("\n=== 测试完成 ===")
    else:
        logger.error("测试失败：未获取到原始财务数据")
