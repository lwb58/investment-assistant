from bs4 import BeautifulSoup  # 新增导入（需放在文件顶部）
import re
import random
import time
import json
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Union, Any
import requests
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from functools import lru_cache
from uuid import uuid4  # 用于生成笔记/股票清单唯一ID
import logging  # 新增：用于日志排查

# 新增：配置简单日志（方便看排查信息）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def fetch_url(url: str, timeout: int = 10, is_sina_var: bool = False) -> Optional[Union[dict, str]]:
    """
    新浪财经接口请求工具（is_sina_var默认False，兼容旧调用）
    :param is_sina_var: 是否为新浪变量格式（返回var xxx = ...;）
    :return: JSON对象 或 原始文本
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/",
            "Accept": "application/json, text/plain, */*"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = "gbk"  # 新浪接口返回GBK编码
        if is_sina_var:
            return response.text  # 新浪变量格式，返回原始文本
        # 非JSON格式时返回文本（避免解析失败）
        try:
            return response.json()
        except:
            return response.text
    except Exception as e:
        print(f"接口请求失败: {url} | 错误: {str(e)}")
        return None

def search_stocks(keyword: str):
    """搜索股票（精准适配页面：解析默认+隐藏容器，提取全部50条个股数据）"""
    if not keyword.strip():
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")
    
    try:
        search_url = f"https://biz.finance.sina.com.cn/suggest/lookup_n.php?country=stock&q={keyword.strip()}"
        logger.info(f"请求搜索接口：{search_url}")
        
        # 保持稳定的请求逻辑
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "gb2312"
        response_text = response.text
        logger.info(f"接口返回HTML长度：{len(response_text)} 字符")
        
        soup = BeautifulSoup(response_text, "html.parser")
        stock_list = []
        seen_codes = set()
        
        # 关键修改1：精准定位个股板块（沪深股市-个股）
        stock_market_div = soup.find("div", id="stock_stock")
        if not stock_market_div:
            logger.warning("未找到沪深个股板块，返回空结果")
            return {"stocks": []}
        
        # 关键修改2：获取所有个股容器（2个来源）
        stock_containers = []
        # 来源1：默认显示的股票容器（class="list"）
        default_list = stock_market_div.find_next_sibling("div", class_="list")
        if default_list:
            stock_containers.append(default_list)
            logger.info("找到默认显示的股票容器")
        # 来源2：隐藏的更多股票容器（id="sotck_stock_more"，注意页面拼写是sotck不是stock）
        hidden_list = soup.find("div", id="sotck_stock_more")
        if hidden_list:
            stock_containers.append(hidden_list)
            logger.info("找到隐藏的更多股票容器")
        
        if not stock_containers:
            logger.warning("未找到任何股票数据容器，返回空结果")
            return {"stocks": []}
        
        # 关键修改3：解析所有容器中的股票数据
        all_stock_links = []
        for container in stock_containers:
            # 提取容器中所有股票链接（a标签href含"realstock/company/"）
            links = container.find_all("a", href=re.compile(r"realstock/company/"))
            all_stock_links.extend(links)
            logger.info(f"从容器中提取到 {len(links)} 个股票链接")
        
        logger.info(f"共提取到 {len(all_stock_links)} 个股票链接（含默认+隐藏）")
        
        # 关键修改4：精准解析股票信息（适配页面文本格式：sz300308 中际旭创）
        for link in all_stock_links:
            link_text = link.get_text(strip=True).replace("\n", "").replace("\t", "")
            if not link_text:
                continue
            
            # 正则优化：精准匹配「sz/sh + 6位数字 + 股票名称」格式
            # 匹配示例：sz300308 中际旭创、sh600036 招商银行
            match = re.match(r"^(sz|sh)(\d{6})\s+(.+)$", link_text.lower())
            if not match:
                logger.debug(f"跳过非标准格式：{link_text}")
                continue
            
            market_prefix = match.group(1)  # sz/sh
            stock_code = match.group(2)     # 6位纯数字代码
            stock_name = match.group(3).strip()  # 股票名称（去空格）
            
            # 过滤无效名称
            if not stock_name or len(stock_name) < 2:
                logger.debug(f"跳过无效名称：{link_text}")
                continue
            
            # 确定市场
            market = "深A" if market_prefix == "sz" else "沪A"
            
            # 去重（避免默认+隐藏容器重复数据）
            if stock_code not in seen_codes:
                seen_codes.add(stock_code)
                stock_list.append({
                    "stockCode": stock_code,
                    "stockName": stock_name,
                    "market": market
                })
                logger.debug(f"✅ 解析成功：{stock_code} | {stock_name} | {market}")
        
        # 按代码排序（可选，让结果更规整）
        stock_list.sort(key=lambda x: x["stockCode"])
        
        logger.info(f"解析完成，共得到 {len(stock_list)} 支有效个股（去重后）")
        # 返回前10条（保持原有逻辑，避免数据过多）
        return {"stocks": stock_list[:50]}
    
    except requests.exceptions.RequestException as e:
        logger.error(f"接口请求失败：{str(e)}")
        raise HTTPException(status_code=500, detail="股票搜索接口请求失败")
    except Exception as e:
        logger.error(f"股票搜索解析失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="股票搜索失败，请重试")

# 执行（创业板成交额接近4600亿元）
if __name__ == "__main__":
    market_details= search_stocks('300')
    print(market_details)