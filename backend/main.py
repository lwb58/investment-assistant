from urllib.parse import urlencode
from urllib.parse import quote
from bs4 import BeautifulSoup
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
from functools import lru_cache, wraps
from uuid import uuid4
import logging
import db  # 导入数据库操作模块

# 配置日志（仅保留关键日志）
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

# 初始化数据库（无需内存存储参数，直接初始化）
db.init_database()

# -------------- 缓存机制类（仅用于行情缓存）--------------
class StockQuoteCache:
    """股票行情数据缓存类（30分钟过期）"""
    def __init__(self, expiry_seconds: int = 1800):
        self.cache = {}
        self.expiry_seconds = expiry_seconds
    
    def get(self, stock_code: str) -> Optional[Dict[str, Any]]:
        if stock_code not in self.cache:
            return None
        current_time = time.time()
        if current_time - self.cache[stock_code]["timestamp"] > self.expiry_seconds:
            del self.cache[stock_code]
            return None
        return self.cache[stock_code]["data"]
    
    def set(self, stock_code: str, data: Dict[str, Any]) -> None:
        self.cache[stock_code] = {"data": data, "timestamp": time.time()}
    
    def clear(self, stock_code: str = None) -> None:
        if stock_code and stock_code in self.cache:
            del self.cache[stock_code]
        elif not stock_code:
            self.cache.clear()

# 创建全局行情缓存实例
stock_quote_cache = StockQuoteCache()

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

# -------------- 辅助函数 --------------
def get_stock_market(stock_code: str) -> Optional[str]:
    if len(stock_code) != 6 or not stock_code.isdigit():
        return None
    return "sh" if stock_code.startswith("60") else "sz" if stock_code.startswith(("00", "30")) else None

def parse_sina_hq(data: str) -> Dict[str, List[str]]:
    result = {}
    for match in re.findall(r'var hq_str_([^=]+)="([^"]+)"', data):
        result[match[0]] = match[1].split(",")
    return result

def format_field(value: str, func: callable) -> any:
    """统一校验并格式化字段"""
    try:
        return func(value)
    except Exception:
        return func("")

# -------------- 工具函数 --------------
def fetch_url(url: str, timeout: int = 15, is_sina_var: bool = False) -> Optional[Union[dict, str]]:
    """新浪财经接口请求工具"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/",
            "Accept": "application/json, text/plain, */*"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = "gbk"
        if is_sina_var:
            return response.text
        try:
            return response.json()
        except:
            return response.text
    except Exception as e:
        logger.error(f"接口请求失败: {url} | 错误: {str(e)}")
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
    """获取上一交易日（跳过周末）"""
    today = date.today()
    if today.weekday() == 0:  # 周一
        return (today - timedelta(days=3)).strftime("%Y%m%d")
    else:
        return (today - timedelta(days=1)).strftime("%Y%m%d")

# -------------- 同步缓存装饰器（用于行情）--------------
def sync_cache_with_timeout(seconds: int = 300):
    """同步函数缓存装饰器（适配行情接口）"""
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(stock_code: str):
            now = time.time()
            # 检查缓存
            if stock_code in cache and (now - cache[stock_code]["timestamp"] < seconds):
                logger.info(f"股票{stock_code}行情命中缓存")
                return cache[stock_code]["data"]
            # 缓存失效，获取新数据
            data = func(stock_code)
            # 只缓存有效数据
            if data and "coreQuotes" in data:
                current_price = data["coreQuotes"].get("currentPrice", 0)
                prev_close = data["coreQuotes"].get("prevClosePrice", 0)
                if current_price > 0 and prev_close > 0:
                    cache[stock_code] = {"data": data, "timestamp": now}
                    logger.info(f"股票{stock_code}行情缓存成功")
            return data
        return wrapper
    return decorator

# -------------- 数据模型 --------------
# 市场概览模型
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
    marketHotspots: List[Dict[str, Union[str, float]]]

# 笔记模块模型
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteItem(BaseModel):
    id: str
    title: str
    content: str
    createTime: str
    updateTime: str

# 股票行情响应模型
class StockQuoteResponse(BaseModel):
    baseInfo: Dict[str, str]
    coreQuotes: Dict[str, Union[str, float, int]]
    supplementInfo: Dict[str, Union[str, float, bool]]
    dataValidity: Dict[str, Union[bool, str]]

# 股票清单模型
class StockCreate(BaseModel):
    stockCode: str
    stockName: str
    industry: Optional[str] = ""
    remark: Optional[str] = ""
    isHold: bool = False

class StockUpdate(BaseModel):
    stockName: Optional[str] = None
    industry: Optional[str] = None
    remark: Optional[str] = None
    isHold: Optional[bool] = None

class StockItem(BaseModel):
    id: str
    stockCode: str
    stockName: str
    industry: str
    addTime: str
    remark: str
    isHold: bool
    currentPrice: Optional[float] = 0.0
    changeAmount: Optional[float] = 0.0
    changeRate: Optional[float] = 0.0
    updateTime: Optional[str] = ""

# -------------- 核心数据源 --------------
class DataSource:
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

            # 上证A股
            sh_response = requests.get(f"https://qt.gtimg.cn/r={random_r}&q=bkqtRank_A_sh", headers=headers, timeout=15, verify=False)
            sh_response.encoding = "utf-8"
            sh_line = [l for l in sh_response.text.split('\n') if "v_bkqtRank_A_sh" in l][0]
            sh_data = sh_line.split('"')[1].split('~')
            sh_up = int(sh_data[2].strip())
            sh_down = int(sh_data[4].strip())
            sh_flat = int(sh_data[3].strip())
            sh_amount = round(int(sh_data[10].strip()) / 10000, 2)
            sh_volume = round(int(sh_data[9].strip()) / 10000 / 100, 2)

            # 深证A股
            sz_response = requests.get(f"https://qt.gtimg.cn/r={random_r}&q=bkqtRank_A_sz", headers=headers, timeout=15, verify=False)
            sz_response.encoding = "utf-8"
            sz_line = [l for l in sz_response.text.split('\n') if "v_bkqtRank_A_sz" in l][0]
            sz_data = sz_line.split('"')[1].split('~')
            sz_up = int(sz_data[2].strip())
            sz_down = int(sz_data[4].strip())
            sz_flat = int(sz_data[3].strip())
            sz_amount = round(int(sz_data[10].strip()) / 10000, 2)
            sz_volume = round(int(sz_data[9].strip()) / 10000 / 100, 2)

            # 创业板
            cyb_response = requests.get(f"https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_sz399006&code=sz399006&r={random_r}", headers=headers, timeout=15, verify=False)
            cyb_response.encoding = "utf-8"
            cyb_text = cyb_response.text.strip().split('=', 1)[1]
            cyb_json = json.loads(cyb_text)
            sz399006_qt = cyb_json["data"]["sz399006"]["qt"]
            zhishu_list = sz399006_qt["zhishu"]
            sz399006_data = sz399006_qt["sz399006"]
            cyb_up = int(zhishu_list[2].strip())
            cyb_down = int(zhishu_list[4].strip())
            cyb_flat = int(zhishu_list[3].strip())
            cyb_amount_str = sz399006_data[35].split('/')[2].strip().replace(',', '')
            cyb_amount = round(int(cyb_amount_str) / 100000000, 2)
            cyb_volume_str = sz399006_data[35].split('/')[1].strip().replace(',', '')
            cyb_volume = round(int(cyb_volume_str) / 10000 / 100, 2)

            # 汇总数据
            total_up = sh_up + sz_up + cyb_up
            total_down = sh_down + sz_down + cyb_down
            total_flat = sh_flat + sz_flat + cyb_flat
            total_volume = round(sh_volume + sz_volume + cyb_volume, 2)
            total_amount = round(sh_amount + sz_amount + cyb_amount, 2)

            # 涨幅中位数
            median = None
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
                "totalVolume": f"{total_volume:.2f}" if total_volume is not None else None,
                "totalAmount": f"{total_amount:.2f}" if total_amount is not None else None,
                "medianChangeRate": median
            }
        except Exception as e:
            logger.error(f"市场统计解析失败：{str(e)}")

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
                    continue
                close = float(text_data[3]) if text_data[3].strip() else 0.0
                preclose = float(text_data[2]) if text_data[2].strip() else 0.0
                change = close - preclose
                change_rate = (change / preclose) * 100 if preclose != 0 else 0.0
                
                index_data[f"{key}Index"] = f"{close:.2f}"
                index_data[f"{key}Change"] = round(change, 2)
                index_data[f"{key}ChangeRate"] = round(change_rate, 2)
            except Exception as e:
                logger.error(f"{code}指数解析失败：{str(e)}")
                continue
        
        return index_data

# -------------- 行情缓存函数 --------------
@sync_cache_with_timeout(300)
def _get_cached_stock_quotes(stock_code: str) -> Optional[Dict[str, Any]]:
    """带缓存的股票行情获取（同步版本）"""
    return get_stock_quotes(stock_code)

# -------------- 核心数据整合 --------------
@cache_with_timeout(300)
def fetch_market_overview_data() -> dict:
    """获取市场概览数据（带缓存）"""
    target_date = get_last_trade_date()
    logger.info(f"获取 {target_date} 市场数据")
    
    top5_data = DataSource.get_sina_industry_concept_top5(target_date)
    market_hotspots = (
        top5_data["industry_up"] + top5_data["industry_down"] +
        top5_data["concept_up"] + top5_data["concept_down"]
    )
    
    market_stats = DataSource.get_sina_market_stats()
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

# -------------- API接口 --------------
# 1. 市场概览接口
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
        logger.error(f"市场接口异常: {str(e)}")
        raise HTTPException(status_code=500, detail="市场数据获取失败")

# 2. 笔记模块接口
@app.get("/api/notes", response_model=List[NoteItem])
async def get_all_notes():
    """获取所有笔记（直接从数据库读取）"""
    return db.get_all_notes()

@app.get("/api/notes/{note_id}", response_model=NoteItem)
async def get_note(note_id: str):
    """获取单条笔记"""
    note = db.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return note

@app.post("/api/notes", response_model=NoteItem)
async def create_note(note: NoteCreate):
    """创建笔记"""
    new_note = {
        "id": str(uuid4()),
        "title": note.title,
        "content": note.content,
        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    created_note = db.create_note(new_note)
    if not created_note:
        raise HTTPException(status_code=500, detail="笔记创建失败")
    return created_note

@app.put("/api/notes/{note_id}", response_model=NoteItem)
async def update_note(note_id: str, update_data: NoteUpdate):
    """更新笔记"""
    update_dict = {}
    if update_data.title:
        update_dict["title"] = update_data.title
    if update_data.content:
        update_dict["content"] = update_data.content
    
    updated_note = db.update_note(note_id, update_dict)
    if not updated_note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return updated_note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: str):
    """删除笔记"""
    success = db.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return {"detail": "笔记删除成功"}

# 3. 股票模块接口
@app.get("/api/stocks", response_model=List[StockItem])
async def get_all_stocks(search: Optional[str] = None):
    """获取股票清单（支持搜索，直接从数据库读取）"""
    stocks_to_process = db.get_all_stocks(search=search)
    result_stocks = []
    
    logger.info(f"获取股票清单，搜索条件：{search}，共{len(stocks_to_process)}支股票")
    for stock in stocks_to_process:
        stock_with_quotes = stock.copy()
        stock_code = stock["stockCode"]
        
        try:
            logger.info(f"获取股票{stock_code}行情数据")
            quote_data = _get_cached_stock_quotes(stock_code)
            
            if quote_data and "coreQuotes" in quote_data:
                core_quotes = quote_data["coreQuotes"]
                current_price = core_quotes.get("currentPrice", 0.0)
                prev_close = core_quotes.get("prevClosePrice", 0.0)
                
                if prev_close > 0.01 and current_price > 0:
                    change_amount = current_price - prev_close
                    change_rate = (change_amount / prev_close) * 100
                else:
                    change_amount = 0.0
                    change_rate = 0.0
                    logger.warning(f"股票{stock_code}涨跌幅为0（昨收盘价={prev_close} 或 最新价={current_price}）")
                
                stock_with_quotes["currentPrice"] = round(current_price, 2)
                stock_with_quotes["changeAmount"] = round(change_amount, 2)
                stock_with_quotes["changeRate"] = round(change_rate, 2)
                stock_with_quotes["updateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        except Exception as e:
            logger.error(f"获取股票{stock_code}行情失败: {str(e)}")
            stock_with_quotes["currentPrice"] = 0.0
            stock_with_quotes["changeAmount"] = 0.0
            stock_with_quotes["changeRate"] = 0.0
        
        result_stocks.append(stock_with_quotes)
    
    logger.info(f"股票清单获取完成，返回{len(result_stocks)}支数据")
    return result_stocks

@app.get("/api/stocks/{stock_id}", response_model=StockItem)
async def get_stock(stock_id: str):
    """获取单只股票"""
    stock = db.get_stock_by_id(stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 添加行情数据
    try:
        quote_data = _get_cached_stock_quotes(stock["stockCode"])
        if quote_data and "coreQuotes" in quote_data:
            core_quotes = quote_data["coreQuotes"]
            current_price = core_quotes.get("currentPrice", 0.0)
            prev_close = core_quotes.get("prevClosePrice", 0.0)
            
            if prev_close > 0.01 and current_price > 0:
                change_amount = current_price - prev_close
                change_rate = (change_amount / prev_close) * 100
            else:
                change_amount = 0.0
                change_rate = 0.0
            
            stock["currentPrice"] = round(current_price, 2)
            stock["changeAmount"] = round(change_amount, 2)
            stock["changeRate"] = round(change_rate, 2)
            stock["updateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            stock["currentPrice"] = 0.0
            stock["changeAmount"] = 0.0
            stock["changeRate"] = 0.0
            stock["updateTime"] = ""
    except Exception as e:
        logger.error(f"获取股票{stock['stockCode']}行情失败: {str(e)}")
        stock["currentPrice"] = 0.0
        stock["changeAmount"] = 0.0
        stock["changeRate"] = 0.0
        stock["updateTime"] = ""
    
    return stock

@app.post("/api/stocks/add", response_model=StockItem)
async def add_stock(stock: StockCreate):
    """添加股票到清单"""
    try:
        # 检查是否已存在
        stocks = db.get_all_stocks()
        if any(item["stockCode"] == stock.stockCode for item in stocks):
            raise HTTPException(status_code=400, detail=f"股票代码 {stock.stockCode} 已存在")
        
        new_stock = {
            "id": str(uuid4()),
            "stockCode": stock.stockCode,
            "stockName": stock.stockName,
            "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "remark": stock.remark or "",
            "isHold": stock.isHold,
            "industry": stock.industry or ""
        }
        
        saved_stock = db.create_stock(new_stock)
        if not saved_stock:
            raise HTTPException(status_code=500, detail="股票保存失败")
        
        logger.info(f"成功添加股票: {stock.stockCode} {stock.stockName}")
        return saved_stock
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加股票异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加股票失败: {str(e)}")

@app.put("/api/stocks/{stock_id}", response_model=StockItem)
async def update_stock(stock_id: str, update_data: StockUpdate):
    """更新股票信息（完全依赖数据库，无内存同步）"""
    update_dict = {}
    if update_data.stockName:
        update_dict["stockName"] = update_data.stockName
    if update_data.remark is not None:
        update_dict["remark"] = update_data.remark
    if update_data.isHold is not None:
        update_dict["isHold"] = update_data.isHold
    if update_data.industry is not None:
        update_dict["industry"] = update_data.industry
    
    updated_stock = db.update_stock(stock_id, update_dict)
    if not updated_stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 清除该股票的行情缓存（可选，避免行情与状态不匹配）
    stock_quote_cache.clear(updated_stock["stockCode"])
    
    logger.info(f"成功更新股票: {updated_stock['stockCode']} 持仓状态={updated_stock['isHold']}")
    return updated_stock

@app.delete("/api/stocks/{stock_id}")
async def delete_stock(stock_id: str):
    """删除股票"""
    success = db.delete_stock(stock_id)
    if not success:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 清除缓存
    stock = db.get_stock_by_id(stock_id)
    if stock:
        stock_quote_cache.clear(stock["stockCode"])
    
    logger.info(f"成功删除股票: {stock_id}")
    return {"detail": "股票删除成功"}

@app.get("/api/stocks/{stock_code}/quotes", response_model=StockQuoteResponse)
def get_stock_quotes(stock_code: str):
    """获取股票实时行情（同步版本）"""
    logger.info(f"请求股票行情: {stock_code}")
    
    # 校验股票代码
    if len(stock_code) != 6 or not stock_code.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是6位数字")
    
    market = get_stock_market(stock_code)
    if not market:
        raise HTTPException(status_code=400, detail="仅支持沪深A（60/00/30开头）")
    
    # 构造接口URL
    sina_list = f"{market}{stock_code},{market}{stock_code}_i"
    sina_url = f"https://hq.sinajs.cn/rn={int(time.time()*1000)}&list={sina_list}"
    
    try:
        hq_data = fetch_url(sina_url, is_sina_var=True)
        if not hq_data:
            raise Exception("新浪接口返回空数据")
        
        parsed_data = parse_sina_hq(hq_data)
        stock_key = f"{market}{stock_code}"
        supplement_key = f"{market}{stock_code}_i"
        
        # 校验字段长度
        core_data = parsed_data.get(stock_key, [])
        if len(core_data) < 32:
            raise Exception(f"核心字段不足（仅{len(core_data)}个）")
        
        # 解析核心行情
        core_quotes = {}
        for field, (idx, _, _, formatter) in CORE_QUOTES_FIELDS.items():
            value = core_data[idx] if len(core_data) > idx else ""
            core_quotes[field] = format_field(value, formatter)
        
        # 解析补充信息
        supplement_data = parsed_data.get(supplement_key, [])
        supplement_info = {}
        for field, (idx, _, _, formatter) in SUPPLEMENT_FIELDS.items():
            value = supplement_data[idx] if len(supplement_data) > idx else ""
            supplement_info[field] = format_field(value, formatter)
        
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
    
    except requests.exceptions.RequestException as e:
        logger.error(f"行情接口请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取行情失败（接口访问受限）")
    except Exception as e:
        logger.error(f"行情数据解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="行情数据解析失败")

@app.get("/api/stock/baseInfo/{stockCode}")
async def get_stock_base_info(stockCode: str):
    """获取股票基础信息"""
    logger.info(f"请求股票基础信息：{stockCode}")
    
    if len(stockCode) != 6 or not stockCode.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是6位数字")
    
    market = get_stock_market(stockCode)
    if not market:
        raise HTTPException(status_code=400, detail="仅支持沪深A（60/00/30开头）")
    
    sina_list = f"{market}{stockCode},{market}{stockCode}_i"
    sina_url = f"https://hq.sinajs.cn/rn={int(time.time()*1000)}&list={sina_list}"
    
    try:
        hq_data = fetch_url(sina_url, is_sina_var=True)
        if not hq_data:
            raise Exception("新浪接口返回空数据")
        
        parsed_data = parse_sina_hq(hq_data)
        stock_key = f"{market}{stockCode}"
        supplement_key = f"{market}{stockCode}_i"
        
        core_data = parsed_data.get(stock_key, [])
        if len(core_data) < 32:
            raise Exception("核心字段不足")
        
        core_quotes = {}
        for field, (idx, _, _, formatter) in CORE_QUOTES_FIELDS.items():
            value = core_data[idx] if len(core_data) > idx else ""
            core_quotes[field] = format_field(value, formatter)
        
        supplement_data = parsed_data.get(supplement_key, [])
        supplement_info = {}
        for field, (idx, _, _, formatter) in SUPPLEMENT_FIELDS.items():
            value = supplement_data[idx] if len(supplement_data) > idx else ""
            supplement_info[field] = format_field(value, formatter)
        
        return {
            "baseInfo": {
                "stockCode": stockCode,
                "market": "沪A" if market == "sh" else "深A",
                "stockName": core_quotes["stockName"],
                "industry": supplement_info["industry"]
            },
            "coreQuotes": core_quotes,
            "supplementInfo": supplement_info,
            "dataValidity": {
                "isValid": core_quotes["currentPrice"] > 0 and core_quotes["stockName"] != "未知名称",
                "reason": "" if (core_quotes["currentPrice"] > 0 and core_quotes["stockName"] != "未知名称") 
                          else "股票数据无效"
            }
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"接口请求失败：{str(e)}")
        raise HTTPException(status_code=500, detail="获取股票信息失败")
    except Exception as e:
        logger.error(f"数据解析失败：{str(e)}")
        raise HTTPException(status_code=500, detail="股票数据解析失败")

@app.get("/api/stocks/search/{keyword}")
async def search_stocks(keyword: str):
    """搜索股票（优化后，无多余日志）"""
    if not keyword.strip():
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")
    
    try:
        encoded_keyword = quote(keyword.strip(), encoding='utf-8')
        search_url = f"https://biz.finance.sina.com.cn/suggest/lookup_n.php?country=stock&q={encoded_keyword}"
        logger.info(f"请求股票搜索接口：{search_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = "gb2312"
        soup = BeautifulSoup(response.text, "html.parser")
        
        stock_list = []
        seen_codes = set()
        
        # 定位股票容器
        stock_market_div = soup.find("div", id="stock_stock")
        if not stock_market_div:
            logger.warning("未找到沪深个股板块")
            return {"stocks": []}
        
        stock_list_div = stock_market_div.find_next_sibling("div", class_="list")
        if not stock_list_div:
            logger.warning("未找到股票列表容器")
            return {"stocks": []}
        
        # 解析股票链接
        stock_links = stock_list_div.find_all("a")
        logger.info(f"提取到{len(stock_links)}个股票链接")
        
        stock_pattern = re.compile(r"(sz|sh)(\d{6})[\s\u3000]+(.+)", re.IGNORECASE)
        for link in stock_links:
            link_text = link.get_text(strip=True)
            if not link_text:
                continue
            
            match = stock_pattern.search(link_text)
            if not match:
                continue
            
            market_prefix = match.group(1).lower()
            stock_code = match.group(2)
            stock_name = match.group(3).strip()
            
            if len(stock_name) < 2 or stock_code in seen_codes:
                continue
            
            market = "深A" if market_prefix == "sz" else "沪A"
            seen_codes.add(stock_code)
            stock_list.append({
                "stockCode": stock_code,
                "stockName": stock_name,
                "market": market
            })
            logger.info(f"解析成功：{stock_code} | {stock_name} | {market}")
        
        stock_list.sort(key=lambda x: x["stockCode"])
        logger.info(f"搜索完成，共{len(stock_list)}支有效个股")
        return {"stocks": stock_list[:50]}
    
    except requests.exceptions.RequestException as e:
        logger.error(f"搜索接口失败：{str(e)}")
        raise HTTPException(status_code=500, detail="股票搜索接口请求失败")
    except Exception as e:
        logger.error(f"搜索解析失败：{str(e)}")
        raise HTTPException(status_code=500, detail="股票搜索失败，请重试")

# -------------- 启动服务 --------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)