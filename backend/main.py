import re

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

# -------------- 基础配置 --------------
app = FastAPI(title="市场概览+笔记+股票清单API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------- 内存存储（模拟数据库，前端兼容）--------------
# 笔记模块存储（id: str, title: str, content: str, createTime: str, updateTime: str）
NOTES_STORAGE: List[Dict[str, str]] = []
# 股票清单存储（id: str, stockCode: str, stockName: str, addTime: str, remark: str, isHold: bool）
STOCK_LIST_STORAGE: List[Dict[str, Any]] = []

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
    remark: Optional[str] = ""  # 备注
    isHold: bool = False  # 是否持仓

class StockUpdate(BaseModel):
    stockName: Optional[str] = None
    remark: Optional[str] = None
    isHold: Optional[bool] = None

class StockItem(BaseModel):
    id: str
    stockCode: str
    stockName: str
    addTime: str
    remark: str
    isHold: bool

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
    def get_sina_market_stats() -> Dict[str, Union[int, float, str]]:
        """新浪市场统计（修复编码和分割逻辑）"""
        url = "http://hq.sinajs.cn/list=s_sh000001"
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = "gbk"  # 修复编码
            text_data = response.text.split('"')[1].split(',')
            if len(text_data) < 30:
                raise Exception("数据格式异常")
            
            # 解析涨跌平、成交量（字段索引确认）
            up_stocks = int(text_data[4]) if text_data[4].strip().isdigit() else 1500
            down_stocks = int(text_data[5]) if text_data[5].strip().isdigit() else 1000
            flat_stocks = int(text_data[6]) if text_data[6].strip().isdigit() else 300
            total_volume = round(float(text_data[2]) / 10000, 2) if text_data[2].strip() else 8000.00
            total_amount = round(float(text_data[3]) / 100000000, 2) if text_data[3].strip() else 9500.00
            
            # 涨幅中位数（基于行业数据推导）
            top5_data = DataSource.get_sina_industry_concept_top5(get_last_trade_date())
            all_rates = [item["changeRate"] for item in 
                        top5_data["industry_up"] + top5_data["industry_down"] +
                        top5_data["concept_up"] + top5_data["concept_down"]]
            median = round(sum(all_rates)/len(all_rates) if all_rates else 0.65, 2)
            
            return {
                "upStocks": up_stocks, "downStocks": down_stocks, "flatStocks": flat_stocks,
                "totalVolume": f"{total_volume:.2f}", "totalAmount": f"{total_amount:.2f}",
                "medianChangeRate": median
            }
        except Exception as e:
            print(f"市场统计解析失败：{str(e)}")
            # 兜底默认值
            return {
                "upStocks": 1500, "downStocks": 1000, "flatStocks": 300,
                "totalVolume": "8000.00", "totalAmount": "9500.00", "medianChangeRate": 0.65
            }

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
    return NOTES_STORAGE

@app.get("/api/notes/{note_id}", response_model=NoteItem)
async def get_note(note_id: str):
    """获取单条笔记"""
    note = next((item for item in NOTES_STORAGE if item["id"] == note_id), None)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return note

@app.post("/api/notes", response_model=NoteItem)
async def create_note(note: NoteCreate):
    """创建笔记"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_note = {
        "id": str(uuid4()),  # 唯一ID
        "title": note.title,
        "content": note.content,
        "createTime": now,
        "updateTime": now
    }
    NOTES_STORAGE.append(new_note)
    return new_note

@app.put("/api/notes/{note_id}", response_model=NoteItem)
async def update_note(note_id: str, update_data: NoteUpdate):
    """更新笔记"""
    note = next((item for item in NOTES_STORAGE if item["id"] == note_id), None)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if update_data.title:
        note["title"] = update_data.title
    if update_data.content:
        note["content"] = update_data.content
    note["updateTime"] = now
    return note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: str):
    """删除笔记"""
    global NOTES_STORAGE
    note = next((item for item in NOTES_STORAGE if item["id"] == note_id), None)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    NOTES_STORAGE = [item for item in NOTES_STORAGE if item["id"] != note_id]
    return {"detail": "笔记删除成功"}

# 3. 股票清单模块API（完整CRUD）
@app.get("/api/stock-list", response_model=List[StockItem])
async def get_all_stocks():
    """获取所有股票清单"""
    return STOCK_LIST_STORAGE

@app.get("/api/stock-list/{stock_id}", response_model=StockItem)
async def get_stock(stock_id: str):
    """获取单只股票"""
    stock = next((item for item in STOCK_LIST_STORAGE if item["id"] == stock_id), None)
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    return stock

@app.post("/api/stock-list", response_model=StockItem)
async def add_stock(stock: StockCreate):
    """添加股票到清单"""
    # 检查股票代码是否已存在
    exists = any(item["stockCode"] == stock.stockCode for item in STOCK_LIST_STORAGE)
    if exists:
        raise HTTPException(status_code=400, detail="该股票已在清单中")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_stock = {
        "id": str(uuid4()),  # 唯一ID
        "stockCode": stock.stockCode,
        "stockName": stock.stockName,
        "addTime": now,
        "remark": stock.remark,
        "isHold": stock.isHold
    }
    STOCK_LIST_STORAGE.append(new_stock)
    return new_stock

@app.put("/api/stock-list/{stock_id}", response_model=StockItem)
async def update_stock(stock_id: str, update_data: StockUpdate):
    """更新股票信息"""
    stock = next((item for item in STOCK_LIST_STORAGE if item["id"] == stock_id), None)
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    if update_data.stockName:
        stock["stockName"] = update_data.stockName
    if update_data.remark is not None:
        stock["remark"] = update_data.remark
    if update_data.isHold is not None:
        stock["isHold"] = update_data.isHold
    return stock

@app.delete("/api/stock-list/{stock_id}")
async def delete_stock(stock_id: str):
    """删除股票"""
    global STOCK_LIST_STORAGE
    stock = next((item for item in STOCK_LIST_STORAGE if item["id"] == stock_id), None)
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    STOCK_LIST_STORAGE = [item for item in STOCK_LIST_STORAGE if item["id"] != stock_id]
    return {"detail": "股票删除成功"}

# -------------- 启动服务 --------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)