from urllib.parse import quote
from urllib.parse import urlencode  # 新增导入，无需额外安装
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

# 1. 新增：字段含义映射（新浪财经标准字段，确保不理解错）
CORE_QUOTES_FIELDS = {
    "stockName": (0, "股票名称", str, lambda x: x.strip() if x else "未知名称"),
    "prevClosePrice": (2, "昨收盘价", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "openPrice": (1, "开盘价", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "currentPrice": (3, "最新价", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "highestPrice": (4, "最高价", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "lowestPrice": (5, "最低价", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "buy1Price": (11, "买一价", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "sell1Price": (21, "卖一价", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "volume": (8, "成交量（股）", int, lambda x: int(x) if x and x.isdigit() else 0),
    "turnover": (9, "成交额（元）", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "tradeDate": (30, "交易日期", str, lambda x: x.strip() if x else ""),
    "tradeTime": (31, "交易时间", str, lambda x: x.strip() if x else "")
}

SUPPLEMENT_FIELDS = {
    "indexCode": (0, "关联指数代码", str, lambda x: x.strip() if x else ""),
    "indexName": (1, "关联指数名称", str, lambda x: x.strip() if x else "无关联指数"),
    "indexWeight": (2, "指数权重（‰）", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "isComponent": (3, "是否成分股", bool, lambda x: x == "1" if x else False),
    "industry": (34, "股票真实行业", str, lambda x: x.strip() if x and x != "," else "未知行业")  # 新增：从xxx_i提取行业
}

INDUSTRY_PLATE_FIELDS = {
    "plateName": (0, "板块名称", str, lambda x: x.strip() if x else "未知板块"),
    "plateIndex": (1, "板块指数", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "plateChangePoint": (2, "板块涨跌点", float, lambda x: float(x) if x and x.replace("-", "").replace(".", "").isdigit() else 0.0),
    "plateChangeRate": (3, "板块涨跌幅（%）", str, lambda x: x.strip() if x and "%" in x else "0.00%"),
    "componentCount": (4, "成分股数量", int, lambda x: int(x) if x and x.isdigit() else 0),
    "plateTurnover": (7, "板块成交额（万元）", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0),
    "plateAvgPE": (8, "板块平均PE", float, lambda x: float(x) if x and x.replace(".", "").isdigit() else 0.0)
}

# 2. 复用原有辅助函数（仅修改解析逻辑，不新增）
def get_stock_market(stock_code: str) -> Optional[str]:  # 仅改这一行
    if not stock_code.isdigit():
        return None
    if len(stock_code) < 6:
        return "rt_hk"  # 港股
    elif len(stock_code) == 6:
        if stock_code.startswith("60"):
            return "sh"  # 上海A股
        elif stock_code.startswith(("00", "30")):
            return "sz"  # 深圳A股
        elif stock_code.startswith("8") or stock_code.startswith("4"):
            return "bj"  # 北京A股
    return None

def parse_sina_hq(data: str) -> Dict[str, List[str]]:
    result = {}
    for match in re.findall(r'var hq_str_([^=]+)="([^"]+)"', data):
        result[match[0]] = match[1].split(",")
    return result
def get_stock_real_industry(stock_code: str, market: str) -> str:
    """从新浪搜索接口提取个股真实行业（复用已有逻辑）"""
    try:
        # 调用新浪搜索接口，获取股票详情（含行业）
        search_url = f"https://biz.finance.sina.com.cn/suggest/lookup_n.php?country=stock&q={stock_code}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/"
        }
        response = requests.get(search_url, headers=headers, timeout=15)
        response.encoding = "gb2312"
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 找到股票对应的链接（含行业信息）
        stock_link = soup.find("a", href=re.compile(f"{market}{stock_code}"), text=re.compile(stock_code))
        if not stock_link:
            return "未知行业"
        
        # 解析链接周边的行业信息（新浪搜索结果格式：股票名 行业）
        link_text = stock_link.get_text(strip=True)
        # 匹配格式：sz003009 中天火箭 国防军工 或 中天火箭(003009) 国防军工
        industry_match = re.search(r"(国防军工|信息技术|医药生物|新能源|电子制造|机械设备|化工|食品饮料|银行|证券|家电)", link_text)
        if industry_match:
            return industry_match.group(1)
        
        # 若未直接匹配，从父节点提取
        parent_div = stock_link.find_parent("div", class_="list")
        if parent_div:
            parent_text = parent_div.get_text(strip=True)
            for industry in ["国防军工", "信息技术", "医药生物", "新能源", "电子制造", "机械设备", "化工", "食品饮料", "银行", "证券", "家电"]:
                if industry in parent_text:
                    return industry
        return "未知行业"
    except Exception as e:
        logger.error(f"获取股票{stock_code}行业失败：{str(e)}")
        return "未知行业"
# 3. 新增：数据校验与格式化函数（最小新增）
def format_field(value: str, func: callable) -> any:
    """统一校验并格式化字段"""
    try:
        return func(value)
    except Exception:
        return func("")
def get_stock_quotes(stock_code: str):
    """
    获取指定股票的实时行情数据（复用用新浪财经接口）
    - stock_code: 6位股票代码（如600036）
    """
    logger.info(f"请求股票行情: {stock_code}")
    
    # 校验股票代码
    if not stock_code.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是数字")
    
    # 获取市场代码
    market = get_stock_market(stock_code)
    if not market:
        raise HTTPException(status_code=400, detail="仅支持沪深A（60/00/30开头）和港股（5位数字）")
    
    # 构造新浪行情接口URL（复用现有工具）
    sina_list = f"{market}{stock_code},{market}{stock_code}_i"
    sina_url = f"https://hq.sinajs.cn/rn={int(time.time()*1000)}&list={sina_list}"
    
    try:
        # 复用现有请求工具
        hq_data = fetch_url(sina_url, is_sina_var=True)
        if not hq_data:
            raise Exception("新浪接口返回空数据")
        
        # 复用用解析函数
        parsed_data = parse_sina_hq(hq_data)
        stock_key = f"{market}{stock_code}"
        supplement_key = f"{market}{stock_code}_i"
        
        # 解析核心行情字段（复用字段映射）
        core_data = parsed_data.get(stock_key, [])
        core_quotes = {}
        for field, (idx, _, _, formatter) in CORE_QUOTES_FIELDS.items():
            value = core_data[idx] if len(core_data) > idx else ""
            core_quotes[field] = format_field(value, formatter)
        
        # 解析补充信息（复用字段映射）
        supplement_data = parsed_data.get(supplement_key, [])
        supplement_info = {}
        for field, (idx, _, _, formatter) in SUPPLEMENT_FIELDS.items():
            value = supplement_data[idx] if len(supplement_data) > idx else ""
            supplement_info[field] = format_field(value, formatter)
        
        # 构造响应
        return {
            "baseInfo": {
                "stockCode": stock_code,
                "market": "沪A" if market == "sh" else "深A",
                "stockName": core_quotes["stockName"],
                "industry": supplement_info["industry"]
            },
            "coreQuotes": core_quotes,
            "supplementInfo": supplement_info,
            "dataValidity": {
                "isValid": core_quotes["currentPrice"] > 0 and core_quotes["stockName"] != "未知名称",
                "reason": "" if (core_quotes["currentPrice"] > 0 and core_quotes["stockName"] != "未知名称") 
                          else "股票数据无效（可能停牌、退市或代码错误）"
            }
        }
    
    except requestsHTTPException as e:
        logger.error(f"行情接口请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取行情失败（接口访问受限）")
    except Exception as e:
        logger.error(f"行情数据解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="行情数据解析失败")
def get_stock_base_info(stockCode: str):
    logger.info(f"收到股票基础信息请求：{stockCode}")
    
    if not stockCode.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是数字")
    
    market = get_stock_market(stockCode)
    if not market:
        raise HTTPException(status_code=400, detail="仅支持沪深A（60/00/30开头）和港股（5位数字）")
    
    # 关键修改1：去掉bk_new_jdhy，不查询无用板块数据
    sina_list = f"{market}{stockCode},{market}{stockCode}_i"
    sina_url = f"https://hq.sinajs.cn/rn={int(time.time()*1000)}&list={sina_list}"
    
    try:
        hq_data = fetch_url(sina_url, is_sina_var=True)
        if not hq_data:
            raise Exception("新浪接口返回空数据")
        
        parsed_data = parse_sina_hq(hq_data)
        stock_key = f"{market}{stockCode}"
        supplement_key = f"{market}{stockCode}_i"
        
        # 解析核心行情（不变）
        core_data = parsed_data.get(stock_key, [])
        core_quotes = {}
        for field, (idx, desc, _, formatter) in CORE_QUOTES_FIELDS.items():
            value = core_data[idx] if len(core_data) > idx else ""
            core_quotes[field] = format_field(value, formatter)
        
        # 解析补充信息（不变，自动包含新增的industry字段）
        supplement_data = parsed_data.get(supplement_key, [])
        supplement_info = {}
        for field, (idx, desc, _, formatter) in SUPPLEMENT_FIELDS.items():
            value = supplement_data[idx] if len(supplement_data) > idx else ""
            supplement_info[field] = format_field(value, formatter)
        
        # 关键修改2：baseInfo中直接用补充信息里的真实行业（替换之前的plateName）
        final_result = {
            "baseInfo": {
                "stockCode": stockCode,
                "market": "沪A" if market == "sh" else "深A",
                "stockName": core_quotes["stockName"],
                "industry": supplement_info["industry"]  # 从xxx_i提取的真实行业（如通信设备）
            },
            "coreQuotes": core_quotes,
            "supplementInfo": supplement_info,
            # 关键修改3：去掉无用的industryPlate字段
            "dataValidity": {
                "isValid": core_quotes["currentPrice"] > 0 and core_quotes["stockName"] != "未知名称",
                "reason": "" if (core_quotes["currentPrice"] > 0 and core_quotes["stockName"] != "未知名称") 
                          else "股票数据无效（可能停牌、退市或代码错误）"
            }
        }
        
        logger.info(f"股票{stockCode}信息查询成功，行业：{supplement_info['industry']}")
        return final_result
    
    except requests.exceptions.RequestException as e:
        logger.error(f"新浪行情接口请求失败：{str(e)}")
        raise HTTPException(status_code=500, detail="获取股票行情失败（接口访问受限）")
    except Exception as e:
        logger.error(f"股票数据解析失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="行情数据解析失败")
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
    """搜索股票（正则兜底+调试日志，确保匹配成功）"""
    if not keyword.strip():
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")
    
    try:
        encoded_keyword = quote(keyword.strip(), encoding='utf-8')
        search_url = f"https://biz.finance.sina.com.cn/suggest/lookup_n.php?country=stock&q={encoded_keyword}"
        logger.info(f"请求搜索接口：{search_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = "gb2312"  # 匹配你的HTML编码
        response_text = response.text
        logger.info(f"接口返回HTML长度：{len(response_text)} 字符")
        
        soup = BeautifulSoup(response_text, "html.parser")
        stock_list = []
        seen_codes = set()
        
        # 精准定位容器（不变）
        stock_market_div = soup.find("div", id="stock_stock")
        if not stock_market_div:
            logger.warning("未找到沪深个股板块，返回空结果")
            return {"stocks": []}
        
        stock_list_div = stock_market_div.find_next_sibling("div", class_="list")
        if not stock_list_div:
            logger.warning("未找到股票列表容器，返回空结果")
            return {"stocks": []}
        logger.info("找到股票列表容器，开始解析")
        
        # 提取a标签（不变）
        stock_links = stock_list_div.find_all("a")
        logger.info(f"从容器中提取到 {len(stock_links)} 个股票链接")
        
        # 核心改动1：超级宽松正则（兼容全角空格、半角空格、多空格，不区分大小写）
        # 匹配规则：任意位置的 sz/sh + 6位数字 + 任意字符（名称）
        stock_pattern = re.compile(
            r"(sz|sh)(\d{6})[\s\u3000]+(.+)",  # [\s\u3000]兼容半角/全角空格
            re.IGNORECASE  # 忽略大小写（SZ/SH/sz/sh都能匹配）
        )
        
        # 核心改动2：添加详细调试日志，看清每一步
        for idx, link in enumerate(stock_links):
            link_text = link.get_text(strip=True)
            logger.debug(f"第{idx+1}个链接文本：{repr(link_text)}")  # repr()显示隐藏字符（如全角空格）
            
            if not link_text:
                logger.debug("跳过空文本链接")
                continue
            
            # 尝试匹配正则
            match = stock_pattern.search(link_text)  # 用search代替match，允许文本前后有多余字符
            if not match:
                logger.debug(f"正则未匹配到：{repr(link_text)}，尝试手动分割")
                # 兜底方案：手动分割（如果正则还是失败，强制按“6位数字”分割）
                import re as re_split
                code_match = re_split.search(r"\d{6}", link_text)
                if code_match:
                    stock_code = code_match.group()
                    # 提取前缀（sz/sh）
                    if "sz" in link_text.lower():
                        market_prefix = "sz"
                    elif "sh" in link_text.lower():
                        market_prefix = "sh"
                    else:
                        logger.debug(f"未找到市场前缀，跳过：{link_text}")
                        continue
                    # 提取名称（6位数字后面的内容）
                    stock_name = link_text.split(stock_code)[-1].strip()
                    logger.debug(f"手动分割成功：{market_prefix} | {stock_code} | {stock_name}")
                else:
                    logger.debug(f"手动分割也失败，跳过：{link_text}")
                    continue
            else:
                market_prefix = match.group(1).lower()
                stock_code = match.group(2)
                stock_name = match.group(3).strip()
            
            # 过滤无效数据
            if len(stock_name) < 2 or stock_code in seen_codes:
                logger.debug(f"无效数据（重复/名称过短）：{stock_code} | {stock_name}")
                continue
            
            # 确定市场
            market = "深A" if market_prefix == "sz" else "沪A"
            seen_codes.add(stock_code)
            stock_list.append({
                "stockCode": stock_code,
                "stockName": stock_name,
                "market": market
            })
            logger.info(f"✅ 解析成功：{stock_code} | {stock_name} | {market}")
        
        # 按代码排序
        stock_list.sort(key=lambda x: x["stockCode"])
        logger.info(f"解析完成，共得到 {len(stock_list)} 支有效个股（去重后）")
        
        return {"stocks": stock_list[:50]}
    
    except requests.exceptions.RequestException as e:
        logger.error(f"接口请求失败：{str(e)}")
        raise HTTPException(status_code=500, detail="股票搜索接口请求失败")
    except Exception as e:
        logger.error(f"股票搜索解析失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="股票搜索失败，请重试")
def test():
    sina_url = f"https://hq.sinajs.cn/rn=list"
    hq_data = fetch_url(sina_url)
    print(f"新浪行情原始数据：{hq_data}")
# 执行（创业板成交额接近4600亿元）
if __name__ == "__main__":
    market_details= search_stocks('中际')
    print(market_details)