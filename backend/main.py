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
    totalVolume: str  # 成交量（亿手）
    totalAmount: str  # 成交额（亿元）
    medianChangeRate: float  # 新增：市场涨幅中位数（%）
    upStocks: int  # 上涨家数
    downStocks: int  # 下跌家数
    flatStocks: int  # 平盘家数
    marketHotspots: List[dict]  # type: up/down

    class Config:
        from_attributes = True

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
@cache_with_timeout(300)
def fetch_market_overview_data() -> dict:
    """修复涨跌平数据+新增涨幅中位数+优化行业排行"""
    market_data = {
        "shIndex": "0.00", "shChange": 0.00, "shChangeRate": 0.00,
        "szIndex": "0.00", "szChange": 0.00, "szChangeRate": 0.00,
        "cyIndex": "0.00", "cyChange": 0.00, "cyChangeRate": 0.00,
        "totalVolume": "0.00", "totalAmount": "0.00",
        "medianChangeRate": 0.00,  # 新增中位数
        "upStocks": 0, "downStocks": 0, "flatStocks": 0,
        "marketHotspots": []
    }

    try:
        # -------------------------- 1. 三大指数（新浪财经，稳定）--------------------------
        index_url = "http://hq.sinajs.cn/list=sh000001,sz399001,sz399006"
        index_data = fetch_url(index_url)
        if index_data:
            index_list = [item for item in index_data.split(';') if item.strip()]
            # 上证指数
            if len(index_list) >= 1:
                try:
                    sh_data = index_list[0].split('"')[1].split(',')
                    if len(sh_data) >= 30:
                        sh_prev = float(sh_data[2])
                        sh_curr = float(sh_data[3])
                        market_data["shIndex"] = f"{sh_curr:.2f}"
                        market_data["shChange"] = round(sh_curr - sh_prev, 2)
                        market_data["shChangeRate"] = round((sh_curr - sh_prev)/sh_prev*100, 2)
                except Exception as e:
                    print(f"上证解析失败：{e}")
            # 深证成指
            if len(index_list) >= 2:
                try:
                    sz_data = index_list[1].split('"')[1].split(',')
                    if len(sz_data) >= 30:
                        sz_prev = float(sz_data[2])
                        sz_curr = float(sz_data[3])
                        market_data["szIndex"] = f"{sz_curr:.2f}"
                        market_data["szChange"] = round(sz_curr - sz_prev, 2)
                        market_data["szChangeRate"] = round((sz_curr - sz_prev)/sz_prev*100, 2)
                except Exception as e:
                    print(f"深证解析失败：{e}")
            # 创业板指
            if len(index_list) >= 3:
                try:
                    cy_data = index_list[2].split('"')[1].split(',')
                    if len(cy_data) >= 30:
                        cy_prev = float(cy_data[2])
                        cy_curr = float(cy_data[3])
                        market_data["cyIndex"] = f"{cy_curr:.2f}"
                        market_data["cyChange"] = round(cy_curr - cy_prev, 2)
                        market_data["cyChangeRate"] = round((cy_curr - cy_prev)/cy_prev*100, 2)
                except Exception as e:
                    print(f"创业板解析失败：{e}")

        # -------------------------- 2. 涨跌平+成交量+中位数（东方财富，稳定）--------------------------
        # 东方财富市场汇总API（包含涨跌家数、中位数）
        summary_url = "http://push2.eastmoney.com/api/qt/stock/marketOverview/get?secid=0.000001&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65&_=1730000000000"
        summary_data = fetch_url(summary_url)
        if summary_data:
            try:
                summary_json = json.loads(summary_data)["data"]
                # 涨跌平家数
                market_data["upStocks"] = int(summary_json.get("f13", 0))  # 上涨家数
                market_data["downStocks"] = int(summary_json.get("f14", 0))  # 下跌家数
                market_data["flatStocks"] = int(summary_json.get("f15", 0))  # 平盘家数
                # 成交量（亿手）= 总成交量（手）/10000
                total_volume = round(float(summary_json.get("f57", 0)) / 10000, 2)
                market_data["totalVolume"] = f"{total_volume:.2f}"
                # 成交额（亿元）= 总成交额（元）/100000000
                total_amount = round(float(summary_json.get("f58", 0)) / 100000000, 2)
                market_data["totalAmount"] = f"{total_amount:.2f}"
                # 涨幅中位数（%）
                market_data["medianChangeRate"] = round(float(summary_json.get("f28", 0)), 2)
            except Exception as e:
                print(f"市场汇总解析失败：{e}")

        # -------------------------- 3. 行业排行（涨幅前5+跌幅前5）--------------------------
        def fetch_industry(is_up: bool):
            sort = 1 if is_up else 2  # 1=涨幅降序，2=跌幅降序
            url = (
                f"http://64.push2.eastmoney.com/api/qt/clist/get?"
                f"pn=1&pz=5&po={sort}&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&"
                f"fltt=2&invt=2&fid=f3&fs=m:90+t:2+f:!50&fields=f14,f3&_={int(time.time()*1000)}"
            )
            data = fetch_url(url)
            if not data:
                return []
            try:
                diff = json.loads(data)["data"]["diff"]
                return [
                    {"industry": item.get("f14", "未知行业"), "changeRate": round(float(item.get("f3", 0)), 2), "type": "up" if is_up else "down"}
                    for item in diff
                ]
            except Exception as e:
                print(f"{'涨幅' if is_up else '跌幅'}行业解析失败：{e}")
                return []

        market_data["marketHotspots"] = fetch_industry(True) + fetch_industry(False)

    except Exception as e:
        print(f"市场数据抓取失败：{e}")

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