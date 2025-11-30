from urllib.parse import urlencode  # 新增导入，无需额外安装
from urllib.parse import quote
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
import db  # 导入数据库操作模块

# 新增：配置简单日志（方便看排查信息）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# -------------- 基础配置 --------------
app = FastAPI(title="市场概览+笔记+股票清单API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 为了向后兼容，保留内存存储变量
# 但实际数据操作将通过数据库完成
NOTES_STORAGE: List[Dict[str, str]] = []
STOCK_LIST_STORAGE: List[Dict[str, Any]] = []

# 初始化数据库
# 将内存存储作为参数传入，以便迁移数据
db.init_database(notes_storage=NOTES_STORAGE, stock_storage=STOCK_LIST_STORAGE)

# -------------- 缓存机制类 --------------
class StockQuoteCache:
    """
    股票行情数据缓存类
    - 缓存时间：30分钟
    - 存储结构：{"stock_code": {"data": {...}, "timestamp": 1234567890}}
    """
    def __init__(self, expiry_seconds: int = 1800):
        """初始化缓存，默认30分钟过期"""
        self.cache = {}
        self.expiry_seconds = expiry_seconds
    
    def get(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取缓存的股票行情数据，如果过期则返回None"""
        if stock_code not in self.cache:
            return None
        
        cache_item = self.cache[stock_code]
        current_time = time.time()
        
        # 检查是否过期
        if current_time - cache_item["timestamp"] > self.expiry_seconds:
            # 删除过期缓存
            del self.cache[stock_code]
            return None
        
        return cache_item["data"]
    
    def set(self, stock_code: str, data: Dict[str, Any]) -> None:
        """设置股票行情缓存数据"""
        self.cache[stock_code] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def clear(self, stock_code: str = None) -> None:
        """清除指定股票或所有缓存"""
        if stock_code:
            if stock_code in self.cache:
                del self.cache[stock_code]
        else:
            self.cache.clear()

# 创建全局缓存实例
stock_quote_cache = StockQuoteCache()

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
    if len(stock_code) != 6 or not stock_code.isdigit():
        return None
    return "sh" if stock_code.startswith("60") else "sz" if stock_code.startswith(("00", "30")) else None

def parse_sina_hq(data: str) -> Dict[str, List[str]]:
    result = {}
    for match in re.findall(r'var hq_str_([^=]+)="([^"]+)"', data):
        result[match[0]] = match[1].split(",")
    return result

# 3. 新增：数据校验与格式化函数（最小新增）
def format_field(value: str, func: callable) -> any:
    """统一校验并格式化字段"""
    try:
        return func(value)
    except Exception:
        return func("")


# -------------- 工具函数（仅保留必要）--------------
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

def cache_with_timeout(seconds: int = 300):
    """5分钟缓存（市场数据专用）"""
    def decorator(func):
        cached_func = lru_cache(maxsize=1)(func)
        cached_func.expire_time = time.time() + seconds
        
        def wrapper(*args, **kwargs):
            if time.time() > cached_func.expire_time:
                cached_func.cache_clear()
                cached_func.expire_time = time.time() + seconds
            return cached_func(*args, **kwargs)
        return wrapper
    return decorator

def get_last_trade_date() -> str:
    """简化版：获取上一交易日（跳过周末）"""
    today = date.today()
    if today.weekday() == 0:  # 0=周一
        return (today - timedelta(days=3)).strftime("%Y%m%d")
    else:
        return (today - timedelta(days=1)).strftime("%Y%m%d")

# -------------- 数据模型（市场+笔记+股票清单，保持前端兼容）--------------
# 1. 市场概览模型
class MarketOverview(BaseModel):
    date: str
    shIndex: str
    shChange: float
    shChangeRate: float
    szIndex: str
    szChange: float
    szChangeRate: float
    cyIndex: str
    cyChange: float
    cyChangeRate: float
    totalVolume: str
    totalAmount: str
    medianChangeRate: float
    upStocks: int
    downStocks: int
    flatStocks: int
    marketHotspots: List[Dict[str, Union[str, float]]]  # 行业+概念TOP5

# 2. 笔记模块模型
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
class StockQuoteResponse(BaseModel):
    baseInfo: Dict[str, str]
    coreQuotes: Dict[str, Union[str, float, int]]
    supplementInfo: Dict[str, Union[str, float, bool]]
    dataValidity: Dict[str, Union[bool, str]]  # 支持 bool（isValid）和 str（reason）
class NoteItem(BaseModel):
    id: str
    title: str
    content: str
    createTime: str
    updateTime: str

# 3. 股票清单模型
class StockCreate(BaseModel):
    stockCode: str  # 股票代码（如600036）
    stockName: str  # 股票名称
    industry: Optional[str] = ""  # 新增行业字段
    remark: Optional[str] = ""  # 备注
    isHold: bool = False  # 是否持仓

class StockUpdate(BaseModel):
    stockName: Optional[str] = None
    industry: Optional[str] = None  # 新增行业字段
    remark: Optional[str] = None
    isHold: Optional[bool] = None

class StockItem(BaseModel):
    id: str
    stockCode: str
    stockName: str
    industry: str  # 新增行业字段
    addTime: str
    remark: str
    isHold: bool
    # 补充行情相关字段（与接口返回一致，设默认值确保兼容性）
    currentPrice: Optional[float] = 0.0  # 当前价
    changeAmount: Optional[float] = 0.0  # 涨跌额
    changeRate: Optional[float] = 0.0    # 涨跌幅（%）
    updateTime: Optional[str] = ""       # 行情更新时间

# -------------- 核心数据源（仅新浪财经）--------------
class DataSource:
    @staticmethod
    def get_sina_industry_concept_top5(target_date: str) -> Dict[str, List[Dict]]:
        """
        严格按你要求：两个独立接口，不合并！
        1. 行业专属接口：仅获取行业数据（sinaindustry_up, sinaindustry_down）
        2. 概念专属接口：仅获取概念数据（si_api4, si_api5, si_api6, si_api7）
        完全独立请求，互不干扰，保留所有错误修复
        """
        random_num = round(time.time() * 1000) + 0.1
        
        # ============== 1. 行业专属接口（独立请求，不包含任何概念参数）==============
        industry_url = f"https://hq.sinajs.cn/ran={random_num}&format=json&list=sinaindustry_up,sinaindustry_down"
        industry_raw_text = fetch_url(industry_url, is_sina_var=True)  # 仅请求行业接口
        
        # ============== 2. 概念专属接口（独立请求，不包含任何行业参数）==============
        concept_url = f"https://hq.sinajs.cn/ran={random_num}&format=json&list=si_api4,si_api5,si_api6,si_api7"
        concept_raw_text = fetch_url(concept_url, is_sina_var=True)  # 仅请求概念接口
        
        # 正则提取工具（独立处理两个接口的原始数据，不混淆）
        def extract_var_value(raw_text: str, var_name: str) -> Optional[str]:
            if not raw_text:
                return None
            pattern = rf"var\s+hq_json_{var_name}\s*=\s*(.*?);"
            match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
            return match.group(1).strip() if match else None
        
        # ============== 行业数据提取+解析（完全独立，不依赖概念接口）==============
        industry_up_str = extract_var_value(industry_raw_text, "sinaindustry_up")
        industry_down_str = extract_var_value(industry_raw_text, "sinaindustry_down")
        
        industry_up = []
        if industry_up_str:
            try:
                safe_str = industry_up_str.replace("'", '"')
                industry_up_list = json.loads(safe_str)[:5]
                for item in industry_up_list:
                    fields = item.split(',')
                    if len(fields) >= 13:
                        industry_name = fields[1].strip()
                        industry_change = round(float(fields[5].strip()), 2) if fields[5].strip().replace('.','').isdigit() else 0.0
                        leader_name = fields[12].strip()  # 领涨股名称（*ST松发）
                        leader_code = fields[8].strip().replace('sh', '').replace('sz', '')
                        leader_change = fields[9].strip() 
                        industry_up.append({
                            "type": "industry_up",
                            "name": industry_name,
                            "changeRate": industry_change,
                            "leaderStock": leader_name,
                            "leaderStockCode": leader_code,
                            "leaderStockChange": leader_change
                        })
            except Exception as e:
                print(f"行业涨幅解析失败：{str(e)}")
        
        industry_down = []
        if industry_down_str:
            try:
                safe_str = industry_down_str.replace("'", '"')
                industry_down_list = json.loads(safe_str)[:5]
                for item in industry_down_list:
                    fields = item.split(',')
                    if len(fields) >= 13:
                        industry_name = fields[1].strip()
                        industry_change = round(float(fields[5].strip()), 2) if fields[5].strip().replace('.','').replace('-','').isdigit() else 0.0
                        leader_name = fields[12].strip()  # 领跌股名称（中国银行）
                        leader_code = fields[8].strip().replace('sh', '').replace('sz', '')
                        leader_change =fields[9].strip() 
                        industry_down.append({
                            "type": "industry_down",
                            "name": industry_name,
                            "changeRate": industry_change,
                            "leaderStock": leader_name,
                            "leaderStockCode": leader_code,
                            "leaderStockChange": leader_change
                        })
            except Exception as e:
                print(f"行业跌幅解析失败：{str(e)}")
        
        # ============== 概念数据提取+解析（完全独立，不依赖行业接口）==============
        api4_str = extract_var_value(concept_raw_text, "si_api4")
        api5_str = extract_var_value(concept_raw_text, "si_api5")
        api6_str = extract_var_value(concept_raw_text, "si_api6")
        api7_str = extract_var_value(concept_raw_text, "si_api7")
        
        concept_up = []
        all_concept_up = []
        for api_str in [api4_str, api6_str]:
            if not api_str:
                continue
            try:
                concept_list = json.loads(api_str)
                for item in concept_list:
                    concept_name = item.get("name", "").strip()
                    concept_change = round(float(item.get("avg_changeratio", 0)) * 100, 2)
                    leader_name = item.get("ts_name", "").strip()
                    leader_code = item.get("ts_symbol", "").strip().replace('sh', '').replace('sz', '')
                    leader_change = round(float(item.get("ts_changeratio", 0)) * 100, 2)
                    if concept_name and concept_change > 0:
                        all_concept_up.append({
                            "type": "concept_up",
                            "name": concept_name,
                            "changeRate": concept_change,
                            "leaderStock": leader_name,
                            "leaderStockCode": leader_code,
                            "leaderStockChange": leader_change
                        })
            except Exception as e:
                print(f"概念涨幅解析失败：{str(e)}")
        
        unique_concept_up = []
        seen_names = set()
        for item in sorted(all_concept_up, key=lambda x: x["changeRate"], reverse=True):
            if item["name"] not in seen_names:
                seen_names.add(item["name"])
                unique_concept_up.append(item)
        concept_up = unique_concept_up[:5]
        
        concept_down = []
        all_concept_down = []
        for api_str in [api5_str, api7_str]:
            if not api_str:
                continue
            try:
                # 修复JSON格式：无引号key加双引号
                fixed_api_str = re.sub(r'(\w+):', r'"\1":', api_str)
                fixed_api_str = fixed_api_str.replace("'", '"')
                concept_list = json.loads(fixed_api_str)
                for item in concept_list:
                    concept_name = item.get("name", "").strip()
                    concept_change = round(float(item.get("avg_changeratio", 0)) * 100, 2)
                    leader_name = item.get("ts_name", "").strip()
                    leader_code = item.get("ts_symbol", "").strip().replace('sh', '').replace('sz', '')
                    leader_change = round(float(item.get("ts_changeratio", 0)) * 100, 2)
                    if concept_name and concept_change < 0:
                        all_concept_down.append({
                            "type": "concept_down",
                            "name": concept_name,
                            "changeRate": concept_change,
                            "leaderStock": leader_name,
                            "leaderStockCode": leader_code,
                            "leaderStockChange": leader_change
                        })
            except Exception as e:
                print(f"概念跌幅解析失败：{str(e)}")
        
        unique_concept_down = []
        seen_names = set()
        for item in sorted(all_concept_down, key=lambda x: x["changeRate"]):
            if item["name"] not in seen_names:
                seen_names.add(item["name"])
                unique_concept_down.append(item)
        concept_down = unique_concept_down[:5]
        
        # 独立返回两个接口的数据，无任何合并逻辑
        return {
            "industry_up": industry_up,    # 纯行业接口数据
            "industry_down": industry_down,
            "concept_up": concept_up,      # 纯概念接口数据
            "concept_down": concept_down
        }


    @staticmethod
    def get_sina_market_stats() -> Dict[str, Optional[Union[int, float, str]]]:
        """新浪市场统计（迁移分市场汇总逻辑，无任何兜底数据）"""
        # 初始化返回结构（键名完整，值默认为None）
        result = {
            "upStocks": None,
            "downStocks": None,
            "flatStocks": None,
            "totalVolume": None,
            "totalAmount": None,
            "medianChangeRate": None
        }

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
            random_r = random.random()

            # ---------------------- 1. 上证A股（无兜底，字段不足抛异常）----------------------
            sh_url = f"https://qt.gtimg.cn/r={random_r}&q=bkqtRank_A_sh"
            sh_response = requests.get(sh_url, headers=headers, timeout=15, verify=False)
            sh_response.encoding = "utf-8"
            sh_line = [l for l in sh_response.text.split('\n') if "v_bkqtRank_A_sh" in l][0]
            sh_data = sh_line.split('"')[1].split('~')
            sh_up = int(sh_data[2].strip())
            sh_down = int(sh_data[4].strip())
            sh_flat = int(sh_data[3].strip())
            sh_amount = round(int(sh_data[10].strip()) / 10000, 2)
            sh_volume = round(int(sh_data[9].strip()) / 10000 / 100, 2)

            # ---------------------- 2. 深证A股（无兜底，字段不足抛异常）----------------------
            sz_url = f"https://qt.gtimg.cn/r={random_r}&q=bkqtRank_A_sz"
            sz_response = requests.get(sz_url, headers=headers, timeout=15, verify=False)
            sz_response.encoding = "utf-8"
            sz_line = [l for l in sz_response.text.split('\n') if "v_bkqtRank_A_sz" in l][0]
            sz_data = sz_line.split('"')[1].split('~')
            sz_up = int(sz_data[2].strip())
            sz_down = int(sz_data[4].strip())
            sz_flat = int(sz_data[3].strip())
            sz_amount = round(int(sz_data[10].strip()) / 10000, 2)
            sz_volume = round(int(sz_data[9].strip()) / 10000 / 100, 2)

            # ---------------------- 3. 创业板A股（无兜底，字段不足抛异常）----------------------
            cyb_url = f"https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_sz399006&code=sz399006&r={random_r}"
            cyb_response = requests.get(cyb_url, headers=headers, timeout=15, verify=False)
            cyb_response.encoding = "utf-8"
            cyb_text = cyb_response.text.strip().split('=', 1)[1]
            cyb_json = requests.models.complexjson.loads(cyb_text)
            sz399006_qt = cyb_json["data"]["sz399006"]["qt"]  # 无get，字段不存在直接抛异常
            zhishu_list = sz399006_qt["zhishu"]
            sz399006_data = sz399006_qt["sz399006"]
            cyb_up = int(zhishu_list[2].strip())
            cyb_down = int(zhishu_list[4].strip())
            cyb_flat = int(zhishu_list[3].strip())
            # 成交额：元→亿元（无默认值）
            cyb_amount_str = sz399006_data[35].split('/')[2].strip().replace(',', '')
            cyb_amount = round(int(cyb_amount_str) / 100000000, 2)
            # 成交量：股→万手（无默认值）
            cyb_volume_str = sz399006_data[35].split('/')[1].strip().replace(',', '')
            cyb_volume = round(int(cyb_volume_str) / 10000 / 100, 2)

            # ---------------------- 总汇总（无兜底）----------------------
            total_up = sh_up + sz_up + cyb_up
            total_down = sh_down + sz_down + cyb_down
            total_flat = sh_flat + sz_flat + cyb_flat
            total_volume = round(sh_volume + sz_volume + cyb_volume, 2)
            total_amount = round(sh_amount + sz_amount + cyb_amount, 2)

            # 涨幅中位数（无兜底，获取失败设为None）
            median = None
            try:
                top5_data = DataSource.get_sina_industry_concept_top5(get_last_trade_date())
                all_rates = [item["changeRate"] for item in 
                            top5_data["industry_up"] + top5_data["industry_down"] +
                            top5_data["concept_up"] + top5_data["concept_down"]]
                if all_rates:
                    median = round(sum(all_rates)/len(all_rates), 2)
            except:
                pass  # 不设兜底，保持None

            # 填充结果（完全匹配你的返回格式）
            result = {
                "upStocks": total_up,
                "downStocks": total_down,
                "flatStocks": total_flat,
                "totalVolume": f"{total_volume:.2f}" if total_volume is not None else None,
                "totalAmount": f"{total_amount:.2f}" if total_amount is not None else None,
                "medianChangeRate": median
            }
        except Exception as e:
            print(f"市场统计解析失败：{str(e)}")
            # 失败时返回键名完整、值为None的字典（无任何兜底假数据）

        return result

    @staticmethod
    def get_sina_index_data() -> Dict[str, Union[str, float]]:
        """新浪大盘指数（上证、深证、创业板）"""
        index_codes = {"sh": "sh000001", "sz": "sz399001", "cy": "sz399006"}
        index_data = {
            "shIndex": "0.00", "shChange": 0.00, "shChangeRate": 0.00,
            "szIndex": "0.00", "szChange": 0.00, "szChangeRate": 0.00,
            "cyIndex": "0.00", "cyChange": 0.00, "cyChangeRate": 0.00
        }
        
        for key, code in index_codes.items():
            try:
                url = f"http://hq.sinajs.cn/list={code}"
                # 调用fetch_url，默认is_sina_var=False，返回文本
                response_text = fetch_url(url)
                if not response_text:
                    continue
                
                # 解析指数文本格式
                text_data = response_text.split('"')[1].split(',')
                if len(text_data) < 30:
                    continue
                
                # 最新价、前收盘价（字段索引确认）
                close = float(text_data[3]) if text_data[3].strip() else 0.0
                preclose = float(text_data[2]) if text_data[2].strip() else 0.0
                change = close - preclose
                change_rate = (change / preclose) * 100 if preclose != 0 else 0.0
                
                index_data[f"{key}Index"] = f"{close:.2f}"
                index_data[f"{key}Change"] = round(change, 2)
                index_data[f"{key}ChangeRate"] = round(change_rate, 2)
            except Exception as e:
                print(f"{code}指数解析失败：{str(e)}")
                continue
        
        return index_data
@cache_with_timeout(300)  # 300秒缓存，与市场概览缓存逻辑一致
def _get_cached_stock_quotes(stock_code: str) -> Dict[str, Any]:
    data = get_stock_quotes(stock_code)
    # 新增：检查行情数据是否有效
    if data and "coreQuotes" in data:
        current_price = data["coreQuotes"].get("currentPrice", 0)
        prev_close = data["coreQuotes"].get("prevClosePrice", 0)
        if current_price <= 0 or prev_close <= 0:
            logger.warning(f"股票{stock_code}行情数据无效（current_price={current_price}, prev_close={prev_close}），不缓存")
            return None  # 无效数据不缓存，下次重新获取
    return data

# -------------- 核心数据整合（市场概览）--------------
@cache_with_timeout(300)
def fetch_market_overview_data() -> dict:
    target_date = get_last_trade_date()
    print(f"获取 {target_date} 市场数据（新浪财经）")
    
    # 行业+概念TOP5
    top5_data = DataSource.get_sina_industry_concept_top5(target_date)
    market_hotspots = (
        top5_data["industry_up"] + top5_data["industry_down"] +
        top5_data["concept_up"] + top5_data["concept_down"]
    )
    
    # 市场统计
    market_stats = DataSource.get_sina_market_stats()
    
    # 大盘指数
    index_data = DataSource.get_sina_index_data()
    
    return {
        "shIndex": index_data["shIndex"],
        "shChange": index_data["shChange"],
        "shChangeRate": index_data["shChangeRate"],
        "szIndex": index_data["szIndex"],
        "szChange": index_data["szChange"],
        "szChangeRate": index_data["szChangeRate"],
        "cyIndex": index_data["cyIndex"],
        "cyChange": index_data["cyChange"],
        "cyChangeRate": index_data["cyChangeRate"],
        "totalVolume": market_stats["totalVolume"],
        "totalAmount": market_stats["totalAmount"],
        "medianChangeRate": market_stats["medianChangeRate"],
        "upStocks": market_stats["upStocks"],
        "downStocks": market_stats["downStocks"],
        "flatStocks": market_stats["flatStocks"],
        "marketHotspots": market_hotspots
    }

# -------------- API接口（市场概览+笔记+股票清单）--------------
# 1. 市场概览接口（原有）
@app.get("/api/market/overview", response_model=MarketOverview)
async def get_market_overview():
    try:
        real_data = fetch_market_overview_data()
        return {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "shIndex": real_data["shIndex"],
            "shChange": real_data["shChange"],
            "shChangeRate": real_data["shChangeRate"],
            "szIndex": real_data["szIndex"],
            "szChange": real_data["szChange"],
            "szChangeRate": real_data["szChangeRate"],
            "cyIndex": real_data["cyIndex"],
            "cyChange": real_data["cyChange"],
            "cyChangeRate": real_data["cyChangeRate"],
            "totalVolume": real_data["totalVolume"],
            "totalAmount": real_data["totalAmount"],
            "medianChangeRate": real_data["medianChangeRate"],
            "upStocks": real_data["upStocks"],
            "downStocks": real_data["downStocks"],
            "flatStocks": real_data["flatStocks"],
            "marketHotspots": real_data["marketHotspots"]
        }
    except Exception as e:
        print(f"市场接口异常: {str(e)}")
        raise HTTPException(status_code=500, detail="市场数据获取失败")

# 2. 笔记模块API（完整CRUD）
@app.get("/api/notes", response_model=List[NoteItem])
async def get_all_notes():
    """获取所有笔记"""
    # 使用db模块中的函数
    notes = db.get_all_notes()
    
    # 同时更新内存存储以便兼容
    global NOTES_STORAGE
    NOTES_STORAGE = notes
    
    return notes

@app.get("/api/notes/{note_id}", response_model=NoteItem)
async def get_note(note_id: str):
    """获取单条笔记"""
    # 使用db模块中的函数
    note = db.get_note(note_id)
    
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    note = {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "createTime": row["create_time"],
        "updateTime": row["update_time"]
    }
    
    return note

@app.post("/api/notes", response_model=NoteItem)
async def create_note(note: NoteCreate):
    """创建笔记"""
    # 使用db模块中的函数
    new_note = db.create_note(note.title, note.content)
    
    # 更新内存存储以便兼容
    global NOTES_STORAGE
    NOTES_STORAGE.append(new_note)
    
    return new_note

@app.put("/api/notes/{note_id}", response_model=NoteItem)
async def update_note(note_id: str, update_data: NoteUpdate):
    """更新笔记"""
    # 构建更新数据字典
    update_dict = {}
    if update_data.title:
        update_dict["title"] = update_data.title
    if update_data.content:
        update_dict["content"] = update_data.content
    
    # 使用db模块中的函数
    updated_note = db.update_note(note_id, update_dict)
    
    if not updated_note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    # 更新内存存储以便兼容
    global NOTES_STORAGE
    for note in NOTES_STORAGE:
        if note["id"] == note_id:
            note.update(updated_note)
            break
    
    return updated_note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: str):
    """删除笔记"""
    # 使用db模块中的函数
    success = db.delete_note(note_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    # 更新内存存储以便兼容
    global NOTES_STORAGE
    NOTES_STORAGE = [item for item in NOTES_STORAGE if item["id"] != note_id]
    
    return {"detail": "笔记删除成功"}

@app.get("/api/stocks/{stock_id}", response_model=StockItem)
async def get_stock(stock_id: str):
    """获取单只股票"""
    # 先从内存中查找
    stock = next((item for item in STOCK_LIST_STORAGE if item["id"] == stock_id), None)
    
    # 如果内存中没有，从数据库查找
    if not stock:
        stock = db.get_stock_by_id(stock_id)
        
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    return stock

@app.post("/api/stocks/add", response_model=StockItem)
async def add_stock(stock: StockCreate):
    """添加股票到清单"""
    # 更严格地检查股票代码是否已存在
    try:
        # 1. 先检查数据库中的唯一约束（更权威）
        stocks = db.get_all_stocks()
        exists_in_db = any(item["stockCode"] == stock.stockCode for item in stocks)
        exists_in_memory = any(item["stockCode"] == stock.stockCode for item in STOCK_LIST_STORAGE)
        
        if exists_in_db or exists_in_memory:
            raise HTTPException(status_code=400, detail=f"股票代码 {stock.stockCode} 已存在于清单中")
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_stock = {
            "id": str(uuid4()),  # 唯一ID
            "stockCode": stock.stockCode,
            "stockName": stock.stockName,
            "addTime": now,
            "remark": stock.remark or "",
            "isHold": stock.isHold,
            "industry": stock.industry or "",
        }
        
        # 保存到数据库
        saved_stock = db.create_stock(new_stock)
        if not saved_stock:
            raise HTTPException(status_code=500, detail=f"股票 {stock.stockCode} {stock.stockName} 保存失败，请稍后重试")
        
        # 同时更新内存存储
        STOCK_LIST_STORAGE.append(new_stock)
        logger.info(f"成功添加股票: {stock.stockCode} {stock.stockName}")
        return new_stock
    except HTTPException:
        raise  # 重新抛出已定义的HTTP异常
    except sqlite3.IntegrityError:
        # 捕获数据库唯一约束错误，提供更明确的错误信息
        raise HTTPException(status_code=400, detail=f"股票代码 {stock.stockCode} 已存在，请使用其他股票代码")
    except Exception as e:
        logger.error(f"添加股票时发生未预期错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加股票时发生错误: {str(e)}")
@app.get("/api/stocks/{stock_code}/quotes", response_model=StockQuoteResponse, summary="获取股票实时行情")
def get_stock_quotes(stock_code: str):
    """
    获取指定股票的实时行情数据（复用用新浪财经接口）
    - stock_code: 6位股票代码（如600036）
    """
    logger.info(f"请求股票行情: {stock_code}")
    
    # 校验股票代码
    if len(stock_code) != 6 or not stock_code.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是6位数字")
    
    # 获取市场代码（sh/sz）
    market = get_stock_market(stock_code)
    if not market:
        raise HTTPException(status_code=400, detail="仅支持沪深A（60/00/30开头）")
    logger.info(f"获取股票{market}行情数据")
    # 构造新浪行情接口URL（复用现有工具）
    sina_list = f"{market}{stock_code},{market}{stock_code}_i"
    sina_url = f"https://hq.sinajs.cn/rn={int(time.time()*1000)}&list={sina_list}"
    
    try:
        # 复用现有请求工具
        hq_data = fetch_url(sina_url, is_sina_var=True)
        if not hq_data:
            raise Exception("新浪接口返回空数据")
        logger.info(f"新浪接口返回数据：{hq_data}")
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
        logger.info(f"股票{stock_code}核心行情数据：{supplement_data}")
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
    
    except requestsHTTPException as e:
        logger.error(f"行情接口请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取行情失败（接口访问受限）")
    except Exception as e:
        logger.error(f"行情数据解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="行情数据解析失败")
@app.get("/api/stocks", response_model=List[StockItem])
async def get_all_stocks(search: Optional[str] = None):
    """获取股票清单（支持搜索功能，并集成行情数据）"""
    # 使用db模块中的函数获取股票数据
    stocks_to_process = db.get_all_stocks(search=search)
    
    # 更新内存存储以便兼容
    global STOCK_LIST_STORAGE
    if not search or not search.strip():
        STOCK_LIST_STORAGE = stocks_to_process.copy()
    
    # 为每个股票添加行情数据
    result_stocks = []
    logger.info(f"获取股票清单，搜索条件：{search}")
    for stock in stocks_to_process:
        # 创建股票的副本，避免修改原始数据
        stock_with_quotes = stock.copy()
        stock_code = stock["stockCode"]
        
        try:
            # 关键优化：直接调用带缓存的函数，装饰器自动处理缓存逻辑
            logger.info(f"获取股票{stock_code}行情数据")
            quote_data = _get_cached_stock_quotes(stock_code)  # 无需手动判断缓存
            
            # 提取价格和涨跌幅信息（原逻辑不变）
            if quote_data and "coreQuotes" in quote_data:
                core_quotes = quote_data["coreQuotes"]
                # 计算涨跌幅
                current_price = core_quotes.get("currentPrice", 0)
                prev_close = core_quotes.get("prevClosePrice", 0)
                
                if prev_close > 0:
                    change_amount = current_price - prev_close
                    change_rate = (change_amount / prev_close) * 100
                else:
                    change_amount = 0
                    change_rate = 0
                
                # 添加行情信息到股票对象（原逻辑不变）
                stock_with_quotes["currentPrice"] = current_price
                stock_with_quotes["changeAmount"] = change_amount
                stock_with_quotes["changeRate"] = round(change_rate, 2)
                stock_with_quotes["updateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        except Exception as e:
            # 行情数据获取失败时记录错误，但不影响股票列表返回
            logger.error(f"获取股票{stock_code}行情数据失败: {str(e)}")
            # 设置默认值
            stock_with_quotes["currentPrice"] = 0
            stock_with_quotes["changeAmount"] = 0
            stock_with_quotes["changeRate"] = 0
        
        result_stocks.append(stock_with_quotes)
    logger.info(f"获取股票清单完成，共{result_stocks}条数据")
    return result_stocks

@app.get("/api/stock/baseInfo/{stockCode}")
async def get_stock_base_info(stockCode: str):
    logger.info(f"收到股票基础信息请求：{stockCode}")
    
    if len(stockCode) != 6 or not stockCode.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是6位数字")
    
    market = get_stock_market(stockCode)
    if not market:
        raise HTTPException(status_code=400, detail="仅支持沪深A（60/00/30开头）")
    
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
        logger.info(f"股票{stockCode}核心行情数据：{supplement_key}")
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
        logger.info(f"股票{stockCode}行业：{supplement_info['industry']}")
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

@app.get("/api/stocks/search/{keyword}")
async def search_stocks(keyword: str):
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
@app.put("/api/stocks/{stock_id}", response_model=StockItem)
async def update_stock(stock_id: str, update_data: StockUpdate):
    """更新股票信息"""
    # 构建更新数据字典
    update_dict = {}
    if update_data.stockName:
        update_dict["stock_name"] = update_data.stockName
    if update_data.remark is not None:
        update_dict["remark"] = update_data.remark
    if update_data.isHold is not None:
        update_dict["is_hold"] = 1 if update_data.isHold else 0
    if hasattr(update_data, 'industry') and update_data.industry is not None:
        update_dict["industry"] = update_data.industry
    
    # 使用db模块中的函数
    updated_stock = db.update_stock(stock_id, update_dict)
    
    if not updated_stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 更新内存存储
    global STOCK_LIST_STORAGE
    # 直接使用get_stock_by_id返回的数据格式
    stock_dict = updated_stock
    
    # 更新内存列表中的对应项
    for i, s in enumerate(STOCK_LIST_STORAGE):
        if s["id"] == stock_id:
            STOCK_LIST_STORAGE[i] = stock_dict
            break
    
    return stock_dict

@app.delete("/api/stocks/{stock_id}")
async def delete_stock(stock_id: str):
    """删除股票"""
    # 使用db模块中的函数
    success = db.delete_stock(stock_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 更新内存存储
    global STOCK_LIST_STORAGE
    STOCK_LIST_STORAGE = [item for item in STOCK_LIST_STORAGE if item["id"] != stock_id]
    
    return {"detail": "股票删除成功"}


# -------------- 启动服务 --------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)