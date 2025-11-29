from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple, FrozenSet
import os
import json
import time
import requests
from functools import wraps
from datetime import datetime

# 数据库依赖（SQLAlchemy 2.x）
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, select, or_
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# 应用初始化
app = FastAPI(
    title="股票投资清单管理系统API",
    description="真实数据+SQLite笔记存储",
    version="2.0.2"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型（Pydantic 2.x）
class StockBase(BaseModel):
    code: str
    name: str
    industry: Optional[str] = None
    holding: bool = False
# 添加 MarketOverview 模型（关键修复）
class MarketOverview(BaseModel):
    date: str  # 日期时间（格式：YYYY-MM-DD HH:MM:SS）
    shIndex: str  # 上证指数
    shChange: float  # 上证涨跌额
    shChangeRate: float  # 上证涨跌幅
    szIndex: str  # 深证成指
    szChange: float  # 深证涨跌额
    szChangeRate: float  # 深证涨跌幅
    cyIndex: str  # 创业板指
    cyChange: float  # 创业板涨跌额
    cyChangeRate: float  # 创业板涨跌幅
    totalVolume: str  # 市场总成交量（亿手）
    totalAmount: str  # 市场总成交额（亿元）
    upStocks: int  # 上涨家数
    downStocks: int  # 下跌家数
    flatStocks: int  # 平盘家数
    marketHotspots: List[dict]  # 市场热点行业（[{industry: str, changeRate: float}]）

    class Config:
        from_attributes = True  # 兼容 SQLAlchemy 模型（如果后续用到）

class StockCreate(StockBase):
    pass

class StockUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    holding: Optional[bool] = None

class Stock(StockBase):
    price: str = "0.00"
    changeRate: float = 0.0
    
    class Config:
        from_attributes = True

class NoteBase(BaseModel):
    title: str
    content: str
    stockCode: Optional[str] = None
    stockName: Optional[str] = None
    tags: Optional[str] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    stockCode: Optional[str] = None
    tags: Optional[str] = None

class Note(NoteBase):
    id: int
    createTime: str
    updateTime: Optional[str] = None
    
    class Config:
        from_attributes = True

class StockDetail(BaseModel):
    code: str
    name: str
    price: str
    changeRate: float
    industry: str
    companyName: str
    listDate: str
    totalShares: str
    floatShares: str
    marketCap: str
    topShareholders: List[dict]

class FinancialData(BaseModel):
    revenue: str
    revenueGrowth: str
    netProfit: str
    netProfitGrowth: str
    eps: str
    navps: str
    roe: str
    pe: str
    pb: str
    grossMargin: str
    netMargin: str
    debtRatio: str

# 工具函数
def cache_with_timeout(seconds: int = 300):
    """带超时的缓存装饰器（默认5分钟）"""
    def decorator(func):
        cache: dict[Tuple[Tuple, FrozenSet], Tuple[float, any]] = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            now = time.time()
            
            if key in cache and now - cache[key][0] < seconds:
                return cache[key][1]
            
            result = func(*args, **kwargs)
            cache[key] = (now, result)
            return result
        return wrapper
    return decorator

def fetch_url(url: str, timeout: int = 10, is_jsonp: bool = False) -> Optional[str]:
    """通用HTTP请求函数（增强反爬，模拟真实浏览器）"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.cn",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # 自动识别编码（解决中文乱码）
        data = response.text
        
        if is_jsonp:
            start_idx = data.find("{")
            end_idx = data.rfind("}") + 1
            if start_idx != -1 and end_idx != 0:
                data = data[start_idx:end_idx]
            else:
                print(f"JSONP解析失败：{url} | 原始数据：{data[:100]}")
                return None
        return data
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{url} | 错误：{str(e)}")
        return None

def get_market_prefix(stock_code: str) -> str:
    """获取股票市场前缀（SH=沪市，SZ=深市）"""
    if stock_code.startswith("6"):
        return "SH"
    elif stock_code.startswith(("0", "3")):
        return "SZ"
    else:
        raise HTTPException(status_code=400, detail="仅支持A股沪/深市场（6/0/3开头代码）")

# SQLite数据库（SQLAlchemy 2.x）
SQLALCHEMY_DATABASE_URL = "sqlite:///./stock_notes.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 笔记数据库模型
class DBNote(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    content = Column(Text, nullable=False)
    stockCode = Column(String(20), index=True, default="")
    stockName = Column(String(50), default="")
    tags = Column(String(100), default="")
    createTime = Column(DateTime, default=datetime.now)
    updateTime = Column(DateTime, nullable=True)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 数据库会话依赖
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化默认笔记
def init_default_notes():
    db = next(get_db())
    note_list = db.scalars(select(DBNote)).all()
    if len(note_list) == 0:
        default_notes = [
            DBNote(
                title="贵州茅台基本面分析",
                content="# 贵州茅台基本面分析\n\n## 财务状况\n- 营收持续增长\n- 毛利率保持高位\n- 现金流充足\n\n## 行业地位\n- 白酒行业龙头\n- 品牌价值突出\n\n## 投资建议\n长期持有，逢低加仓。",
                stockCode="600519",
                stockName="贵州茅台",
                tags="基本面, 白酒, 长期持有",
                createTime=datetime.fromisoformat("2024-05-20T10:30:00"),
                updateTime=datetime.fromisoformat("2024-05-20T11:45:00")
            ),
            DBNote(
                title="市场趋势分析",
                content="# 市场趋势分析\n\n## 宏观经济\n- 经济稳步复苏\n- 货币政策偏宽松\n\n## 行业轮动\n- 消费板块表现强势\n- 科技板块有估值压力\n\n## 操作策略\n关注低估值蓝筹股。",
                stockCode="",
                stockName="",
                tags="宏观, 策略, 市场分析",
                createTime=datetime.fromisoformat("2024-05-19T15:20:00")
            )
        ]
        db.add_all(default_notes)
        db.commit()
        print("默认笔记初始化成功！")
    db.close()

init_default_notes()

# 用户股票清单（实际项目中应存储在数据库，这里为演示用）
user_stocks = [
    {"code": "600519", "name": "贵州茅台", "industry": "白酒", "holding": True},
    {"code": "000858", "name": "五粮液", "industry": "白酒", "holding": False},
    {"code": "000333", "name": "美的集团", "industry": "家电", "holding": True},
    {"code": "000651", "name": "格力电器", "industry": "家电", "holding": False},
    {"code": "601318", "name": "中国平安", "industry": "金融", "holding": True}
]

# 真实股票数据获取
@cache_with_timeout(300)
def fetch_stock_quote(stock_code: str) -> Optional[dict]:
    """获取实时行情（新浪财经API）"""
    market_prefix = get_market_prefix(stock_code).lower()
    url = f"http://hq.sinajs.cn/list={market_prefix}{stock_code}"
    data = fetch_url(url)
    if not data:
        return None
    try:
        quote_list = data.split('"')[1].split(',')
        if len(quote_list) < 4:
            return None
        name = quote_list[0]
        current_price = quote_list[3]
        prev_close = quote_list[2]
        change = round(float(current_price) - float(prev_close), 2)
        change_rate = round(change / float(prev_close) * 100, 2)
        return {"name": name, "price": current_price, "changeRate": change_rate}
    except Exception as e:
        print(f"行情解析失败：{stock_code} | {str(e)}")
        return None

@cache_with_timeout(3600)
def fetch_company_profile(stock_code: str) -> Optional[dict]:
    """获取公司信息（东方财富API）"""
    market_prefix = get_market_prefix(stock_code)
    url = f"http://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/CompanySurveyAjax?code={market_prefix}{stock_code}"
    data = fetch_url(url, is_jsonp=True)
    if not data:
        return None
    try:
        profile = json.loads(data)
        return {
            "companyName": profile.get("gsmc", f"{stock_code}股份有限公司"),
            "listDate": profile.get("ssrq", "2020-01-01"),
            "totalShares": str(round(float(profile.get("zgb", 0)) / 10000, 2)) if profile.get("zgb") else "0.00",
            "floatShares": str(round(float(profile.get("ltgb", 0)) / 10000, 2)) if profile.get("ltgb") else "0.00",
            "marketCap": str(round(float(profile.get("zsz", 0)) / 10000, 2)) if profile.get("zsz") else "0.00",
            "industry": profile.get("hyfl", "").split("|")[0]
        }
    except Exception as e:
        print(f"公司信息解析失败：{stock_code} | {str(e)}")
        return None

@cache_with_timeout(3600)
def fetch_top_shareholders(stock_code: str) -> List[dict]:
    """获取前十大股东（东方财富API）"""
    market_prefix = get_market_prefix(stock_code)
    url = f"http://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/ShareholderResearchAjax?code={market_prefix}{stock_code}&type=10"
    data = fetch_url(url, is_jsonp=True)
    if not data:
        return []
    try:
        shareholders = json.loads(data)
        if "gdList" in shareholders:
            return [
                {
                    "name": item.get("gdxm", ""),
                    "holdings": item.get("cgsl", ""),
                    "percentage": item.get("cgbl", "")
                } 
                for item in shareholders["gdList"]
            ]
        return []
    except Exception as e:
        print(f"股东信息解析失败：{stock_code} | {str(e)}")
        return []
@cache_with_timeout(300)  # 缓存5分钟
def fetch_market_overview_data() -> dict:
    """抓取真实市场概况数据（所有数值保留两位小数）"""
    market_data = {
        "shIndex": "0.00", "shChange": 0.00, "shChangeRate": 0.00,
        "szIndex": "0.00", "szChange": 0.00, "szChangeRate": 0.00,
        "cyIndex": "0.00", "cyChange": 0.00, "cyChangeRate": 0.00,
        "totalVolume": "0.00", "totalAmount": "0.00",
        "upStocks": 0, "downStocks": 0, "flatStocks": 0,
        "marketHotspots": []
    }

    try:
        # -------------------------- 1. 三大指数解析（强制保留两位小数）--------------------------
        index_url = "http://hq.sinajs.cn/list=sh000001,sz399001,sz399006"
        index_data = fetch_url(index_url)
        if index_data:
            index_list = [item for item in index_data.split(';') if item.strip()]
            
            # 上证指数
            if len(index_list) >= 1:
                try:
                    sh_data = index_list[0].split('"')[1].split(',')
                    if len(sh_data) >= 30:
                        sh_prev_close = float(sh_data[2])
                        sh_current = float(sh_data[3])
                        # 强制保留两位小数
                        sh_change = round(sh_current - sh_prev_close, 2)
                        sh_change_rate = round((sh_current - sh_prev_close)/sh_prev_close*100, 2)
                        
                        market_data["shIndex"] = f"{sh_current:.2f}"  # 字符串类型，两位小数
                        market_data["shChange"] = sh_change  # 浮点数，两位小数
                        market_data["shChangeRate"] = sh_change_rate  # 浮点数，两位小数
                except Exception as e:
                    print(f"上证指数解析失败：{str(e)}")

            # 深证成指
            if len(index_list) >= 2:
                try:
                    sz_data = index_list[1].split('"')[1].split(',')
                    if len(sz_data) >= 30:
                        sz_prev_close = float(sz_data[2])
                        sz_current = float(sz_data[3])
                        sz_change = round(sz_current - sz_prev_close, 2)
                        sz_change_rate = round((sz_current - sz_prev_close)/sz_prev_close*100, 2)
                        
                        market_data["szIndex"] = f"{sz_current:.2f}"
                        market_data["szChange"] = sz_change
                        market_data["szChangeRate"] = sz_change_rate
                except Exception as e:
                    print(f"深证成指解析失败：{str(e)}")

            # 创业板指
            if len(index_list) >= 3:
                try:
                    cy_data = index_list[2].split('"')[1].split(',')
                    if len(cy_data) >= 30:
                        cy_prev_close = float(cy_data[2])
                        cy_current = float(cy_data[3])
                        cy_change = round(cy_current - cy_prev_close, 2)
                        cy_change_rate = round((cy_current - cy_prev_close)/cy_prev_close*100, 2)
                        
                        market_data["cyIndex"] = f"{cy_current:.2f}"
                        market_data["cyChange"] = cy_change
                        market_data["cyChangeRate"] = cy_change_rate
                except Exception as e:
                    print(f"创业板指解析失败：{str(e)}")

        # -------------------------- 2. 市场整体数据（成交量/成交额强制两位小数）--------------------------
        market_summary_url = "http://vip.stock.finance.sina.cn/q/view/vRiseFall.php?page=1&num=1&t=0"
        summary_data = fetch_url(market_summary_url)
        if summary_data:
            try:
                summary_json = json.loads(summary_data)
                if "data" in summary_json and len(summary_json["data"]) > 0:
                    data = summary_json["data"][0]
                    market_data["upStocks"] = int(data.get("up", 0))
                    market_data["downStocks"] = int(data.get("down", 0))
                    market_data["flatStocks"] = int(data.get("flat", 0))
                    
                    # 成交量：手 → 亿手，保留两位小数
                    total_volume = round(float(data.get('volume', 0)) / 10000, 2)
                    market_data["totalVolume"] = f"{total_volume:.2f}"
                    
                    # 成交额：元 → 亿元，保留两位小数
                    total_amount = round(float(data.get('amount', 0)) / 100000000, 2)
                    market_data["totalAmount"] = f"{total_amount:.2f}"
            except Exception as e:
                print(f"市场汇总数据解析失败：{str(e)}")

        # -------------------------- 3. 行业涨跌幅（强制两位小数）--------------------------
        def fetch_industry_ranking(is_up: bool = True) -> List[dict]:
            sort_type = 1 if is_up else 2
            industry_url = (
                f"http://64.push2.eastmoney.com/api/qt/clist/get?"
                f"pn=1&pz=5&po={sort_type}&np=1&"
                f"ut=bd1d9ddb04089700cf9c27f6f7426281&"
                f"fltt=2&invt=2&fid=f3&"
                f"fs=m:90+t:2+f:!50&"
                f"fields=f14,f3&"
                f"_={int(time.time() * 1000)}"
            )
            industry_data = fetch_url(industry_url)
            if not industry_data:
                return []
            
            try:
                industry_json = json.loads(industry_data)
                if "data" in industry_json and "diff" in industry_json["data"]:
                    return [
                        {
                            "industry": item.get("f14", "未知行业"),
                            "changeRate": round(float(item.get("f3", 0.00)), 2),  # 强制两位小数
                            "type": "up" if is_up else "down"
                        }
                        for item in industry_json["data"]["diff"]
                    ]
            except Exception as e:
                print(f"{'涨幅' if is_up else '跌幅'}行业解析失败：{str(e)}")
            return []

        up_industries = fetch_industry_ranking(is_up=True)
        down_industries = fetch_industry_ranking(is_up=False)
        market_data["marketHotspots"] = up_industries + down_industries

    except Exception as e:
        print(f"市场概况数据抓取失败：{str(e)}")

    return market_data

@app.get("/api/market/overview", response_model=MarketOverview)
async def get_market_overview():
    """获取真实市场概况数据（含涨幅前5+跌幅前5行业）"""
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
        "upStocks": real_data["upStocks"],
        "downStocks": real_data["downStocks"],
        "flatStocks": real_data["flatStocks"],
        "marketHotspots": real_data["marketHotspots"]  # 含 type 字段
    }
# API路由 - 股票清单管理
@app.get("/api/stocks", response_model=List[Stock])
async def get_stocks(search: Optional[str] = Query(None, description="模糊搜索关键词（代码/名称/行业）")):
    """获取股票列表（支持模糊搜索）"""
    result = []
    for stock in user_stocks:
        # 模糊搜索逻辑：如果提供了搜索词，检查是否匹配代码、名称或行业
        if search:
            search_lower = search.lower()
            # 三个字段任一包含搜索词即匹配（不区分大小写）
            if (search_lower not in stock["code"].lower() and 
                search_lower not in stock["name"].lower() and 
                (not stock["industry"] or search_lower not in stock["industry"].lower())):
                continue  # 不匹配则跳过
            
        # 获取实时行情
        quote = fetch_stock_quote(stock["code"]) or {}
        result.append({
            "code": stock["code"],
            "name": stock["name"],
            "industry": stock["industry"],
            "holding": stock["holding"],
            "price": quote.get("price", "0.00"),
            "changeRate": quote.get("changeRate", 0.0)
        })
    return result

@app.post("/api/stocks", response_model=Stock)
async def add_stock(stock: StockCreate):
    """添加新股票"""
    # 检查股票是否已存在
    if any(s["code"] == stock.code for s in user_stocks):
        raise HTTPException(status_code=400, detail=f"股票代码 {stock.code} 已存在")
    
    # 获取股票实时数据
    quote = fetch_stock_quote(stock.code) or {}
    
    # 添加到股票列表
    new_stock = {
        "code": stock.code,
        "name": stock.name,
        "industry": stock.industry,
        "holding": stock.holding
    }
    user_stocks.append(new_stock)
    
    return {**new_stock,** quote}

@app.put("/api/stocks/{stock_code}", response_model=Stock)
async def update_stock(stock_code: str, update_data: StockUpdate):
    """更新股票信息"""
    for stock in user_stocks:
        if stock["code"] == stock_code:
            # 更新字段（只更新提供的字段）
            if update_data.name is not None:
                stock["name"] = update_data.name
            if update_data.industry is not None:
                stock["industry"] = update_data.industry
            if update_data.holding is not None:
                stock["holding"] = update_data.holding
            
            # 获取实时行情
            quote = fetch_stock_quote(stock_code) or {}
            return {**stock,** quote}
    
    raise HTTPException(status_code=404, detail=f"股票代码 {stock_code} 不存在")

@app.delete("/api/stocks/{stock_code}")
async def delete_stock(stock_code: str):
    """删除股票"""
    global user_stocks
    initial_length = len(user_stocks)
    user_stocks = [s for s in user_stocks if s["code"] != stock_code]
    
    if len(user_stocks) == initial_length:
        raise HTTPException(status_code=404, detail=f"股票代码 {stock_code} 不存在")
    
    return {"message": f"股票 {stock_code} 已成功删除"}

# API路由 - 股票详情
@app.get("/api/stocks/{stock_code}/detail", response_model=StockDetail)
async def get_stock_detail(stock_code: str):
    """获取股票详细信息"""
    # 获取基本信息
    stock = next((s for s in user_stocks if s["code"] == stock_code), None)
    if not stock:
        raise HTTPException(status_code=404, detail=f"股票代码 {stock_code} 不存在")
    
    # 获取实时行情
    quote = fetch_stock_quote(stock_code) or {}
    
    # 获取公司信息
    profile = fetch_company_profile(stock_code) or {}
    
    # 获取股东信息
    shareholders = fetch_top_shareholders(stock_code)
    
    return {
        "code": stock_code,
        "name": stock["name"],
        "price": quote.get("price", "0.00"),
        "changeRate": quote.get("changeRate", 0.0),
        "industry": profile.get("industry", stock["industry"] or ""),
        "companyName": profile.get("companyName", ""),
        "listDate": profile.get("listDate", ""),
        "totalShares": profile.get("totalShares", ""),
        "floatShares": profile.get("floatShares", ""),
        "marketCap": profile.get("marketCap", ""),
        "topShareholders": shareholders
    }

# API路由 - 笔记管理
@app.get("/api/notes", response_model=List[Note])
async def get_notes(search: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """获取笔记列表（支持搜索）"""
    query = select(DBNote)
    
    # 笔记搜索逻辑（模糊匹配标题、内容、股票代码）
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            or_(
                DBNote.title.ilike(search_lower),
                DBNote.content.ilike(search_lower),
                DBNote.stockCode.ilike(search_lower)
            )
        )
    
    # 按创建时间倒序
    query = query.order_by(DBNote.createTime.desc())
    notes = db.scalars(query).all()
    
    return [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "stockCode": note.stockCode,
            "stockName": note.stockName,
            "tags": note.tags,
            "createTime": note.createTime.isoformat(),
            "updateTime": note.updateTime.isoformat() if note.updateTime else None
        }
        for note in notes
    ]

@app.get("/api/notes/{note_id}", response_model=Note)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """获取单条笔记"""
    note = db.scalar(select(DBNote).where(DBNote.id == note_id))
    if not note:
        raise HTTPException(status_code=404, detail=f"笔记ID {note_id} 不存在")
    
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "stockCode": note.stockCode,
        "stockName": note.stockName,
        "tags": note.tags,
        "createTime": note.createTime.isoformat(),
        "updateTime": note.updateTime.isoformat() if note.updateTime else None
    }

@app.post("/api/notes", response_model=Note)
async def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """创建新笔记"""
    db_note = DBNote(
        title=note.title,
        content=note.content,
        stockCode=note.stockCode,
        stockName=note.stockName,
        tags=note.tags,
        createTime=datetime.now()
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return {
        "id": db_note.id,
        "title": db_note.title,
        "content": db_note.content,
        "stockCode": db_note.stockCode,
        "stockName": db_note.stockName,
        "tags": db_note.tags,
        "createTime": db_note.createTime.isoformat(),
        "updateTime": db_note.updateTime.isoformat() if db_note.updateTime else None
    }

@app.put("/api/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, update_data: NoteUpdate, db: Session = Depends(get_db)):
    """更新笔记"""
    note = db.scalar(select(DBNote).where(DBNote.id == note_id))
    if not note:
        raise HTTPException(status_code=404, detail=f"笔记ID {note_id} 不存在")
    
    # 更新字段
    if update_data.title is not None:
        note.title = update_data.title
    if update_data.content is not None:
        note.content = update_data.content
    if update_data.stockCode is not None:
        note.stockCode = update_data.stockCode
    if update_data.tags is not None:
        note.tags = update_data.tags
    
    note.updateTime = datetime.now()
    db.commit()
    db.refresh(note)
    
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "stockCode": note.stockCode,
        "stockName": note.stockName,
        "tags": note.tags,
        "createTime": note.createTime.isoformat(),
        "updateTime": note.updateTime.isoformat() if note.updateTime else None
    }

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """删除笔记"""
    note = db.scalar(select(DBNote).where(DBNote.id == note_id))
    if not note:
        raise HTTPException(status_code=404, detail=f"笔记ID {note_id} 不存在")
    
    db.delete(note)
    db.commit()
    return {"message": f"笔记 {note_id} 已成功删除"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)