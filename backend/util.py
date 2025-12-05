from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
import re
import random
import time
import json
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Union, Any
import requests
from functools import lru_cache, wraps
import logging

# 配置日志（增强详细度，便于排查）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -------------- 字段含义映射 --------------
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
    "industry": (34, "股票真实行业", str, lambda x: x.strip() if x and x != "," else "未知行业")
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

# -------------- 缓存机制类（优化过期逻辑）--------------
class StockQuoteCache:
    """股票行情数据缓存类（30分钟过期）"""
    def __init__(self, expiry_seconds: int = 1800):
        self.cache = {}
        self.expiry_seconds = expiry_seconds
    
    def get(self, stock_code: str) -> Optional[Dict[str, Any]]:
        if stock_code not in self.cache:
            logger.debug(f"股票{stock_code}缓存未命中")
            return None
        current_time = time.time()
        if current_time - self.cache[stock_code]["timestamp"] > self.expiry_seconds:
            logger.info(f"股票{stock_code}缓存过期，清除")
            del self.cache[stock_code]
            return None
        logger.info(f"股票{stock_code}缓存命中")
        return self.cache[stock_code]["data"]
    
    def set(self, stock_code: str, data: Dict[str, Any]) -> None:
        self.cache[stock_code] = {"data": data, "timestamp": time.time()}
        logger.info(f"股票{stock_code}缓存成功")
    
    def clear(self, stock_code: str = None) -> None:
        if stock_code and stock_code in self.cache:
            del self.cache[stock_code]
            logger.info(f"股票{stock_code}缓存已清除")
        elif not stock_code:
            self.cache.clear()
            logger.info("所有股票缓存已清除")

# 创建全局行情缓存实例
stock_quote_cache = StockQuoteCache()

# -------------- 辅助函数 --------------
def get_stock_market(stock_code: str) -> Optional[str]:
    """
    根据A股股票代码判断所属市场
    返回值说明：sh=沪市（60开头），sz=深市（00/30开头），bj=北交所（8开头），None=格式错误或非A股代码
    """
    if len(stock_code) != 6 or not stock_code.isdigit():
        logger.warning(f"股票代码格式错误：{stock_code}（必须是6位数字）")
        return None
    
    # 补充北交所判断，覆盖全A股市场
    if stock_code.startswith(("60","68")):
        return "sh"
    elif stock_code.startswith(("00", "30")):
        return "sz"
    elif stock_code.startswith("8"):
        return "bj"
    else:
        logger.warning(f"非A股股票代码：{stock_code}（仅支持60/00/30/8开头的A股代码）")
        return None

def parse_sina_hq(data: str) -> Dict[str, List[str]]:
    result = {}
    try:
        # 优化正则表达式，适配不同格式
        for match in re.findall(r'var\s+hq_str_([^=]+)\s*=\s*"([^"]+)"', data, re.IGNORECASE):
            result[match[0]] = match[1].split(",")
        logger.debug(f"解析新浪行情数据，共获取{len(result)}个标的")
    except Exception as e:
        logger.error(f"解析新浪行情失败：{str(e)}")
    return result

def format_field(value: str, func: callable) -> any:
    """统一校验并格式化字段，增强容错性"""
    try:
        if value is None or value == "" or value == "-":
            return func("0" if func in (float, int) else "")
        return func(value)
    except Exception as e:
        logger.debug(f"字段格式化失败：值={value}，函数={func.__name__}，错误={str(e)}")
        return func("0" if func in (float, int) else "")

# -------------- 工具函数（优化请求稳定性）--------------
def fetch_url(url: str, timeout: int = 15, is_sina_var: bool = False, retry: int = 2) -> Optional[Union[dict, str]]:
    """新浪财经接口请求工具（增加重试机制）"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Referer": "https://finance.sina.com.cn/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    # 特别为财务数据接口添加调试
    is_finance_api = "getFinanceReport2022" in url
    if is_finance_api:
        print(f"DEBUG: fetch_url - 正在请求财务数据API: {url}")
    
    for attempt in range(retry + 1):
        try:
            response = requests.get(
                url, 
                headers=headers, 
                timeout=timeout,
                verify=False  # 忽略SSL验证，避免证书问题
            )
            response.raise_for_status()
            
            # 优化编码处理（新浪接口可能返回gbk或gb2312）
            if response.encoding is None:
                response.encoding = "gbk"
            elif response.encoding.lower() in ["iso-8859-1", "latin-1"]:
                response.encoding = "gbk"
            
            content = response.text
            if not content:
                logger.warning(f"接口返回空内容：{url}，重试次数：{attempt}")
                if attempt < retry:
                    time.sleep(0.5)
                    continue
                return None
            
            # 打印财务数据API的完整返回内容
            if is_finance_api:
                print(f"DEBUG: fetch_url - 财务数据API返回内容:")
                print(f"DEBUG: {content[:500]}..." if len(content) > 500 else f"DEBUG: {content}")
            
            if is_sina_var:
                return content
            try:
                return json.loads(content)
            except:
                return content
        except requests.exceptions.RequestException as e:
            logger.error(f"接口请求失败（{attempt+1}/{retry+1}）：{url} | 错误：{str(e)}")
            if attempt < retry:
                time.sleep(0.5)
                continue
        except Exception as e:
            logger.error(f"接口处理失败：{url} | 错误：{str(e)}")
            break
    return None

def cache_with_timeout(seconds: int = 300):
    """5分钟缓存（市场数据专用）"""
    def decorator(func):
        cached_func = lru_cache(maxsize=1)(func)
        cached_func.expire_time = time.time() + seconds
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            if time.time() > cached_func.expire_time:
                cached_func.cache_clear()
                cached_func.expire_time = time.time() + seconds
                logger.info(f"市场数据缓存过期，重新获取")
            return cached_func(*args, **kwargs)
        return wrapper
    return decorator

def get_last_trade_date() -> str:
    """获取上一交易日（跳过周末和节假日逻辑优化）"""
    today = date.today()
    delta = 1
    if today.weekday() == 0:  # 周一
        delta = 3
    elif today.weekday() == 6:  # 周日
        delta = 2
    
    last_trade_date = today - timedelta(days=delta)
    # 简单跳过法定节假日（可根据实际需求扩展）
    holidays = ["20250101", "20250129", "20250130", "20250131", "20250201", "20250202"]
    while last_trade_date.strftime("%Y%m%d") in holidays or last_trade_date.weekday() >= 5:
        last_trade_date -= timedelta(days=1)
    
    return last_trade_date.strftime("%Y%m%d")

def sync_cache_with_timeout(seconds: int = 300):
    """同步函数缓存装饰器（优化缓存逻辑，修复数据过滤问题）"""
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(stock_code: str):
            now = time.time()
            # 检查缓存
            if stock_code in cache:
                cache_item = cache[stock_code]
                if now - cache_item["timestamp"] < seconds:
                    logger.info(f"股票{stock_code}行情命中本地缓存")
                    return cache_item["data"]
                else:
                    logger.info(f"股票{stock_code}行情缓存过期")
                    del cache[stock_code]
            
            # 缓存失效，获取新数据
            data = func(stock_code)
            
            # 优化缓存条件：只要有有效价格就缓存（修复原逻辑过滤过严问题）
            if data and "coreQuotes" in data:
                current_price = data["coreQuotes"].get("currentPrice", 0)
                stock_name = data["coreQuotes"].get("stockName", "")
                # 放宽条件：价格>=0且股票名称有效（停牌股票价格可能为0）
                if current_price >= 0 and stock_name != "未知名称":
                    cache[stock_code] = {"data": data, "timestamp": now}
                    logger.info(f"股票{stock_code}行情缓存成功（最新价：{current_price}）")
            
            return data
        return wrapper
    return decorator

# -------------- 核心数据源 --------------
class DataSource:
    @staticmethod
    def get_stock_financial_data(stock_code: str) -> Dict[str, Dict[str, str]]:
        """使用指定新浪接口获取股票财务数据：https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport"""
        market = get_stock_market(stock_code)
        if not market:
            logger.error(f"股票市场不支持：{stock_code}")
            return {}
        
        # 拼接 paperCode（market+股票代码，如 sh601669）
        paper_code = f"{market}{stock_code}"
        # 报表类型（lrb=利润表，核心财务数据来源）
        report_type = "gjzb"  # lrb-利润表、zcfz-资产负债表、xjll-现金流量表
        financial_data = {}
        
        try:
            # 构造URL，使用固定的getFinanceReport2022接口路径（2022是接口固定标识，不是年份）
            url = (
                f"https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
                f"?paperCode={paper_code}&source={report_type}&type=0&page=1&num=10"
            )
            logger.info(f"请求财务数据：{url}")
            
            # 调用fetch_url获取JSONP数据
            raw_data = fetch_url(url, timeout=20, is_sina_var=False)
            
            if not raw_data:
                logger.warning(f"财务数据接口返回空或格式错误：{stock_code}")
                financial_data["2022"] = DataSource._get_default_finance_data()
                return financial_data
            
            # 直接使用返回的字典数据
            data = raw_data
            
            # 解析接口返回结果（适配新的数据结构路径）
            # 注意：数据结构可能是 result.code 或 result.status.code
            if isinstance(data.get("result"), dict):
                result_code = data["result"].get("code")
                if result_code is None:
                    result_code = data["result"].get("status", {}).get("code", -1)
            else:
                result_code = -1
                
            if result_code != 0:
                logger.error(f"财务数据接口返回错误：{data.get('result', {})}")
                financial_data["2022"] = DataSource._get_default_finance_data()
                return financial_data
            
            # 提取最新报表数据（适配新路径：data['result']['data']['report_list']）
            result_data = data.get("result", {})
            report_list = result_data.get("data", {}).get("report_list", {})
            
            # 获取最新报表的年份和数据
            latest_year = "2022"
            report_data = []
            
            if report_list and isinstance(report_list, dict):
                # report_list是一个以日期为键的字典，获取最新的日期
                latest_date = sorted(report_list.keys(), reverse=True)[0] if report_list else None
                if latest_date:
                    latest_report = report_list[latest_date]
                    
                    # 提取年份
                    latest_year = latest_date[:4]
                    
                    # 提取报表数据（适配新字段名：'data' 而不是 'report_data'）
                    if isinstance(latest_report, dict):
                        report_data = latest_report.get("data", [])
            else:
                logger.warning(f"report_list不是预期的字典类型: {type(report_list)}")
                financial_data["2022"] = DataSource._get_default_finance_data()
                return financial_data
            
            # 初始化该年份的财务数据
            financial_data[latest_year] = DataSource._get_default_finance_data()
            
            # 遍历所有财务项，提取需要的指标
            if report_data and isinstance(report_data, list):
                total_profit = None
                income_tax = None
                
                for item in report_data:
                    if not isinstance(item, dict):
                        continue
                    
                    item_field = item.get("item_field", "")
                    item_title = item.get("item_title", "")
                    item_value = item.get("item_value", "0.0")
                    
                    # 直接匹配字段名
                    if item_field == "BASICEPS" and item_value:
                        financial_data[latest_year]["eps"] = item_value
                    elif (item_field == "BIZINCO" or item_field == "BIZTOTINCO") and item_value:  # 营业收入或营业总收入
                        financial_data[latest_year]["revenue"] = item_value
                    elif item_field == "TOTPROFIT" and item_value:  # 利润总额
                        total_profit = float(item_value) if item_value else 0.0
                    elif item_field == "INCOTAXEXPE" and item_value:  # 所得税费用
                        income_tax = float(item_value) if item_value else 0.0
                    elif item_field == "NETPROFIT" and item_value:
                        financial_data[latest_year]["netProfit"] = item_value
                    elif item_field == "NAVPS" and item_value:
                        financial_data[latest_year]["navps"] = item_value
                    elif item_field == "ROE" and item_value:
                        financial_data[latest_year]["roe"] = item_value
                    elif item_field == "TOTASS" and item_value:
                        financial_data[latest_year]["totalAssets"] = item_value
                    elif item_field == "TOTSHOLDEREQ" and item_value:
                        financial_data[latest_year]["totalEquity"] = item_value
                    elif item_field == "TOTDEBT" and item_value:
                        financial_data[latest_year]["totalDebt"] = item_value
                    elif item_field == "GROSMPROFIT" and item_value:
                        financial_data[latest_year]["grossProfit"] = item_value
                    elif item_field == "NETCASHFLOWOPS" and item_value:
                        financial_data[latest_year]["operatingCashFlow"] = item_value
                    
                    # 基于标题匹配（备用方案）
                    elif item_title == "基本每股收益" and item_value:
                        financial_data[latest_year]["eps"] = item_value
                    elif ("营业" in item_title and "收入" in item_title) and item_value:
                        financial_data[latest_year]["revenue"] = item_value
                    elif "利润总额" in item_title and item_value:
                        total_profit = float(item_value) if item_value else 0.0
                    elif "所得税费用" in item_title and item_value:
                        income_tax = float(item_value) if item_value else 0.0
                    elif "净利润" in item_title and item_value:
                        financial_data[latest_year]["netProfit"] = item_value
                    elif "每股净资产" in item_title and item_value:
                        financial_data[latest_year]["navps"] = item_value
                    elif "净资产收益率" in item_title and item_value:
                        financial_data[latest_year]["roe"] = item_value
                
                # 计算净利润：利润总额 - 所得税费用
                if total_profit is not None and income_tax is not None and financial_data[latest_year]["netProfit"] == "0.00":
                    net_profit = total_profit - income_tax
                    financial_data[latest_year]["netProfit"] = f"{net_profit:.2f}"
                elif total_profit is not None and financial_data[latest_year]["netProfit"] == "0.00":
                    financial_data[latest_year]["netProfit"] = f"{total_profit:.2f}"  # 如果没有所得税费用，直接使用利润总额
                
            # 使用提取的年份作为键，保持向后兼容
            financial_data[latest_year] = financial_data[latest_year]
             # 毛利率和净利率数据（字典结构，键为季度日期）
            gross_data = {}
            
            # 遍历所有季度报表数据
            for date_key, report_info in report_list.items():
                
                # 获取季度数据
                if isinstance(report_info, dict):
                    report_items = report_info.get("data", [])
                    
                    # 初始化当前季度的毛利率和净利率数据
                    if date_key not in gross_data:
                        gross_data[date_key] = {"mll": "0.0", "xsjll": "0.0"}
                    
                    # 提取毛利率和净利率
                    for item in report_items:
                        item_title = item.get("item_title", "")
                        item_value = item.get("item_value", "0.0")
                          
                        # 处理毛利率（可能是"毛利率"或"销售毛利率"）
                        if "毛利率" in item_title:
                            gross_data[date_key]["mll"] = item_value
                        # 处理净利率（可能是"净利率"或"销售净利率"）
                        elif "净利率" in item_title:
                            gross_data[date_key]["xsjll"] = item_value
            
            # 将处理后的毛利率和净利率数据添加到财务数据中
            if gross_data:
                financial_data['mllsj'] = gross_data

        except json.JSONDecodeError as e:
            logger.error(f"财务数据JSON解析失败：{stock_code} | 错误：{str(e)}")
            financial_data["2022"] = DataSource._get_default_finance_data()
        except Exception as e:
            logger.error(f"财务数据获取失败：{stock_code} | 错误：{str(e)}", exc_info=True)
            financial_data["2022"] = DataSource._get_default_finance_data()
        
        return financial_data

    @staticmethod
    def _get_default_finance_data() -> Dict[str, str]:
        """财务数据兜底默认值"""
        return {
            "revenue": "0.00",
            "revenueGrowth": "0.0",
            "netProfit": "0.00",
            "netProfitGrowth": "0.0",
            "eps": "0.00",
            "navps": "0.00",
            "roe": "0.0",
            "pe": "0.0",
            "pb": "0.0",
            "grossMargin": "0.0",
            "netMargin": "0.0",
            "debtRatio": "0.0"
        }

    @staticmethod
    def get_sina_industry_concept_top5(target_date: str) -> Dict[str, List[Dict]]:
        """获取行业+概念TOP5（独立接口）"""
        random_num = round(time.time() * 1000) + 0.1
        
        # 行业接口
        industry_url = f"https://hq.sinajs.cn/ran={random_num}&format=json&list=sinaindustry_up,sinaindustry_down"
        industry_raw_text = fetch_url(industry_url, is_sina_var=True)
        
        # 概念接口
        concept_url = f"https://hq.sinajs.cn/ran={random_num}&format=json&list=si_api4,si_api5,si_api6,si_api7"
        concept_raw_text = fetch_url(concept_url, is_sina_var=True)
        
        # 提取变量值
        def extract_var_value(raw_text: str, var_name: str) -> Optional[str]:
            if not raw_text:
                return None
            pattern = rf"var\s+hq_json_{var_name}\s*=\s*(.*?);"
            match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
            return match.group(1).strip() if match else None
        
        # 解析行业数据
        industry_up = []
        industry_up_str = extract_var_value(industry_raw_text, "sinaindustry_up")
        if industry_up_str:
            try:
                industry_up_list = json.loads(industry_up_str.replace("'", '"'))[:5]
                for item in industry_up_list:
                    fields = item.split(',')
                    if len(fields) >= 13:
                        industry_up.append({
                            "type": "industry_up",
                            "name": fields[1].strip(),
                            "changeRate": round(float(fields[5].strip()), 2) if fields[5].strip().replace('.','').isdigit() else 0.0,
                            "leaderStock": fields[12].strip(),
                            "leaderStockCode": fields[8].strip().replace('sh', '').replace('sz', ''),
                            "leaderStockChange": fields[9].strip()
                        })
            except Exception as e:
                logger.error(f"行业涨幅解析失败：{str(e)}")
        
        industry_down = []
        industry_down_str = extract_var_value(industry_raw_text, "sinaindustry_down")
        if industry_down_str:
            try:
                industry_down_list = json.loads(industry_down_str.replace("'", '"'))[:5]
                for item in industry_down_list:
                    fields = item.split(',')
                    if len(fields) >= 13:
                        industry_down.append({
                            "type": "industry_down",
                            "name": fields[1].strip(),
                            "changeRate": round(float(fields[5].strip()), 2) if fields[5].strip().replace('.','').replace('-','').isdigit() else 0.0,
                            "leaderStock": fields[12].strip(),
                            "leaderStockCode": fields[8].strip().replace('sh', '').replace('sz', ''),
                            "leaderStockChange": fields[9].strip()
                        })
            except Exception as e:
                logger.error(f"行业跌幅解析失败：{str(e)}")
        
        # 解析概念数据
        concept_up = []
        all_concept_up = []
        for api_str in [extract_var_value(concept_raw_text, "si_api4"), extract_var_value(concept_raw_text, "si_api6")]:
            if not api_str:
                continue
            try:
                for item in json.loads(api_str):
                    concept_name = item.get("name", "").strip()
                    concept_change = round(float(item.get("avg_changeratio", 0)) * 100, 2)
                    if concept_name and concept_change > 0:
                        all_concept_up.append({
                            "type": "concept_up",
                            "name": concept_name,
                            "changeRate": concept_change,
                            "leaderStock": item.get("ts_name", "").strip(),
                            "leaderStockCode": item.get("ts_symbol", "").strip().replace('sh', '').replace('sz', ''),
                            "leaderStockChange": round(float(item.get("ts_changeratio", 0)) * 100, 2)
                        })
            except Exception as e:
                logger.error(f"概念涨幅解析失败：{str(e)}")
        
        # 去重并取TOP5
        unique_concept_up = []
        seen_names = set()
        for item in sorted(all_concept_up, key=lambda x: x["changeRate"], reverse=True):
            if item["name"] not in seen_names:
                seen_names.add(item["name"])
                unique_concept_up.append(item)
        concept_up = unique_concept_up[:5]
        
        concept_down = []
        all_concept_down = []
        for api_str in [extract_var_value(concept_raw_text, "si_api5"), extract_var_value(concept_raw_text, "si_api7")]:
            if not api_str:
                continue
            try:
                fixed_api_str = re.sub(r'(\w+):', r'"\1":', api_str).replace("'", '"')
                for item in json.loads(fixed_api_str):
                    concept_name = item.get("name", "").strip()
                    concept_change = round(float(item.get("avg_changeratio", 0)) * 100, 2)
                    if concept_name and concept_change < 0:
                        all_concept_down.append({
                            "type": "concept_down",
                            "name": concept_name,
                            "changeRate": concept_change,
                            "leaderStock": item.get("ts_name", "").strip(),
                            "leaderStockCode": item.get("ts_symbol", "").strip().replace('sh', '').replace('sz', ''),
                            "leaderStockChange": round(float(item.get("ts_changeratio", 0)) * 100, 2)
                        })
            except Exception as e:
                logger.error(f"概念跌幅解析失败：{str(e)}")
        
        # 去重并取TOP5
        unique_concept_down = []
        seen_names = set()
        for item in sorted(all_concept_down, key=lambda x: x["changeRate"]):
            if item["name"] not in seen_names:
                seen_names.add(item["name"])
                unique_concept_down.append(item)
        concept_down = unique_concept_down[:5]
        
        return {
            "industry_up": industry_up,
            "industry_down": industry_down,
            "concept_up": concept_up,
            "concept_down": concept_down
        }

    @staticmethod
    def get_sina_market_stats() -> Dict[str, Optional[Union[int, float, str]]]:
        """获取市场统计数据"""
        result = {
            "upStocks": 0,
            "downStocks": 0,
            "flatStocks": 0,
            "totalVolume": "0.00",
            "totalAmount": "0.00",
            "medianChangeRate": 0.0
        }

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
            random_r = random.random()

            # 上证A股
            sh_response = requests.get(f"https://qt.gtimg.cn/r={random_r}&q=bkqtRank_A_sh", headers=headers, timeout=15, verify=False)
            sh_response.encoding = "utf-8"
            sh_line = [l for l in sh_response.text.split('\n') if "v_bkqtRank_A_sh" in l][0]
            sh_data = sh_line.split('"')[1].split('~')
            sh_up = int(sh_data[2].strip()) if sh_data[2].strip().isdigit() else 0
            sh_down = int(sh_data[4].strip()) if sh_data[4].strip().isdigit() else 0
            sh_flat = int(sh_data[3].strip()) if sh_data[3].strip().isdigit() else 0
            sh_amount = round(int(sh_data[10].strip()) / 10000, 2) if sh_data[10].strip().isdigit() else 0.0
            sh_volume = round(int(sh_data[9].strip()) / 10000 / 100, 2) if sh_data[9].strip().isdigit() else 0.0

            # 深证A股
            sz_response = requests.get(f"https://qt.gtimg.cn/r={random_r}&q=bkqtRank_A_sz", headers=headers, timeout=15, verify=False)
            sz_response.encoding = "utf-8"
            sz_line = [l for l in sz_response.text.split('\n') if "v_bkqtRank_A_sz" in l][0]
            sz_data = sz_line.split('"')[1].split('~')
            sz_up = int(sz_data[2].strip()) if sz_data[2].strip().isdigit() else 0
            sz_down = int(sz_data[4].strip()) if sz_data[4].strip().isdigit() else 0
            sz_flat = int(sz_data[3].strip()) if sz_data[3].strip().isdigit() else 0
            sz_amount = round(int(sz_data[10].strip()) / 10000, 2) if sz_data[10].strip().isdigit() else 0.0
            sz_volume = round(int(sz_data[9].strip()) / 10000 / 100, 2) if sz_data[9].strip().isdigit() else 0.0

            # 创业板
            cyb_response = requests.get(f"https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_sz399006&code=sz399006&r={random_r}", headers=headers, timeout=15, verify=False)
            cyb_response.encoding = "utf-8"
            cyb_text = cyb_response.text.strip().split('=', 1)[1] if '=' in cyb_response.text else '{}'
            cyb_json = json.loads(cyb_text)
            sz399006_qt = cyb_json.get("data", {}).get("sz399006", {}).get("qt", {})
            zhishu_list = sz399006_qt.get("zhishu", [])
            sz399006_data = sz399006_qt.get("sz399006", [])
            
            cyb_up = int(zhishu_list[2].strip()) if len(zhishu_list) > 2 and zhishu_list[2].strip().isdigit() else 0
            cyb_down = int(zhishu_list[4].strip()) if len(zhishu_list) > 4 and zhishu_list[4].strip().isdigit() else 0
            cyb_flat = int(zhishu_list[3].strip()) if len(zhishu_list) > 3 and zhishu_list[3].strip().isdigit() else 0
            
            cyb_amount_str = sz399006_data[35].split('/')[2].strip().replace(',', '') if len(sz399006_data) > 35 else '0'
            cyb_amount = round(int(cyb_amount_str) / 100000000, 2) if cyb_amount_str.isdigit() else 0.0
            cyb_volume_str = sz399006_data[35].split('/')[1].strip().replace(',', '') if len(sz399006_data) > 35 else '0'
            cyb_volume = round(int(cyb_volume_str) / 10000 / 100, 2) if cyb_volume_str.isdigit() else 0.0

            # 汇总数据
            total_up = sh_up + sz_up + cyb_up
            total_down = sh_down + sz_down + cyb_down
            total_flat = sh_flat + sz_flat + cyb_flat
            total_volume = round(sh_volume + sz_volume + cyb_volume, 2)
            total_amount = round(sh_amount + sz_amount + cyb_amount, 2)

            # 涨幅中位数
            median = 0.0
            try:
                top5_data = DataSource.get_sina_industry_concept_top5(get_last_trade_date())
                all_rates = [item["changeRate"] for item in 
                            top5_data["industry_up"] + top5_data["industry_down"] +
                            top5_data["concept_up"] + top5_data["concept_down"]]
                if all_rates:
                    median = round(sum(all_rates)/len(all_rates), 2)
            except Exception as e:
                logger.error(f"中位数计算失败：{str(e)}")

            result = {
                "upStocks": total_up,
                "downStocks": total_down,
                "flatStocks": total_flat,
                "totalVolume": f"{total_volume:.2f}",
                "totalAmount": f"{total_amount:.2f}",
                "medianChangeRate": median
            }
        except Exception as e:
            logger.error(f"市场统计解析失败：{str(e)}", exc_info=True)

        return result

    @staticmethod
    def get_sina_index_data() -> Dict[str, Union[str, float]]:
        """获取大盘指数数据"""
        index_codes = {"sh": "sh000001", "sz": "sz399001", "cy": "sz399006"}
        index_data = {
            "shIndex": "0.00", "shChange": 0.00, "shChangeRate": 0.00,
            "szIndex": "0.00", "szChange": 0.00, "szChangeRate": 0.00,
            "cyIndex": "0.00", "cyChange": 0.00, "cyChangeRate": 0.00
        }
        
        for key, code in index_codes.items():
            try:
                response_text = fetch_url(f"http://hq.sinajs.cn/list={code}")
                if not response_text:
                    continue
                text_data = response_text.split('"')[1].split(',')
                if len(text_data) < 30:
                    logger.warning(f"{code}指数数据字段不足：仅{len(text_data)}个字段")
                    continue
                
                close = float(text_data[3]) if text_data[3].strip() and text_data[3].strip().replace('.','').isdigit() else 0.0
                preclose = float(text_data[2]) if text_data[2].strip() and text_data[2].strip().replace('.','').isdigit() else 0.0
                change = close - preclose
                change_rate = (change / preclose) * 100 if preclose != 0 else 0.0
                
                index_data[f"{key}Index"] = f"{close:.2f}"
                index_data[f"{key}Change"] = round(change, 2)
                index_data[f"{key}ChangeRate"] = round(change_rate, 2)
            except Exception as e:
                logger.error(f"{code}指数解析失败：{str(e)}")
                continue
        
        return index_data