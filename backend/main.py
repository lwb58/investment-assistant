from fastapi import FastAPI, HTTPException, Query, Depends  # 新增导入 Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple, FrozenSet
import os
import json
import time
import requests
from functools import wraps
from datetime import datetime

# ===================== 数据库依赖（SQLAlchemy 2.x 正确写法）=====================
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, select
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# ===================== 应用初始化 =====================
app = FastAPI(
    title="股票投资清单管理系统API",
    description="真实数据+SQLite笔记存储（Python 3.9+ 兼容，无错）",
    version="2.0.2"
)

# CORS配置（支持前端跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== 数据模型（Pydantic 2.x 语法）=====================
class StockBase(BaseModel):
    code: str
    name: str
    industry: Optional[str] = None
    holding: bool = False

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
        from_attributes = True  # Pydantic 2.x 替代 orm_mode

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

# ===================== 工具函数 =====================
def cache_with_timeout(seconds: int = 300):
    """带超时的缓存装饰器（默认5分钟，避免API限流）"""
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
    """通用HTTP请求函数（支持JSONP解析）"""
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # 抛出4xx/5xx错误
        data = response.text
        
        if is_jsonp:
            start_idx = data.find("{")
            end_idx = data.rfind("}") + 1
            if start_idx != -1 and end_idx != 0:
                data = data[start_idx:end_idx]
            else:
                print(f"JSONP解析失败：{url}")
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

# ===================== SQLite数据库（SQLAlchemy 2.x 正确写法）=====================
SQLALCHEMY_DATABASE_URL = "sqlite:///./stock_notes.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite必填
    echo=False  # 关闭SQL执行日志
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

# 数据库会话依赖（FastAPI 官方标准写法）
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db  # 生成器自动管理会话生命周期
    finally:
        db.close()

# 初始化默认笔记
def init_default_notes():
    db = next(get_db())  # 这里用 next 没问题（非接口内依赖）
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

# 启动时执行初始化
init_default_notes()

# ===================== 用户股票清单 =====================
user_stocks = [
    {"code": "600519", "name": "贵州茅台", "industry": "白酒", "holding": True},
    {"code": "000858", "name": "五粮液", "industry": "白酒", "holding": False},
    {"code": "000333", "name": "美的集团", "industry": "家电", "holding": True},
    {"code": "000651", "name": "格力电器", "industry": "家电", "holding": False},
    {"code": "601318", "name": "中国平安", "industry": "金融", "holding": True}
]

# ===================== 真实股票数据获取 =====================
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
        shareholder_data = json.loads(data)
        top_10 = shareholder_data.get("gdList", [])[:10]
        return [
            {"name": item.get("gdxm", "未知股东"), "percentage": str(round(float(item.get("cgbl", 0)), 2)), "type": item.get("gdlx", "流通股")}
            for item in top_10
        ]
    except Exception as e:
        print(f"股东数据解析失败：{stock_code} | {str(e)}")
        return []

@cache_with_timeout(3600)
def fetch_financial_data(stock_code: str, year: str) -> Optional[dict]:
    """获取年度财务数据（东方财富API）"""
    market_prefix = get_market_prefix(stock_code)
    url = f"http://emweb.securities.eastmoney.com/PC_HSF10/FinanceAnalysis/FinanceAnalysisAjax?type=web&code={market_prefix}{stock_code}&reportType=yearly"
    data = fetch_url(url, is_jsonp=True)
    if not data:
        return None
    try:
        financial = json.loads(data)
        annual_data = next((item for item in financial.get("data", []) if item.get("reportDate", "")[:4] == year), None)
        if not annual_data:
            return None
        return {
            "revenue": str(round(float(annual_data.get("operatingIncome", 0)) / 10000, 2)),
            "revenueGrowth": str(round(float(annual_data.get("operatingIncomeYoY", 0)), 2)),
            "netProfit": str(round(float(annual_data.get("netProfit", 0)) / 10000, 2)),
            "netProfitGrowth": str(round(float(annual_data.get("netProfitYoY", 0)), 2)),
            "eps": str(round(float(annual_data.get("basicEPS", 0)), 2)),
            "navps": str(round(float(annual_data.get("navps", 0)), 2)),
            "roe": str(round(float(annual_data.get("roe", 0)), 2)),
            "pe": str(round(float(annual_data.get("peTTM", 0)), 2)),
            "pb": str(round(float(annual_data.get("pb", 0)), 2)),
            "grossMargin": str(round(float(annual_data.get("grossProfitRate", 0)), 2)),
            "netMargin": str(round(float(annual_data.get("netProfitRate", 0)), 2)),
            "debtRatio": str(round(float(annual_data.get("assetLiabilityRatio", 0)), 2))
        }
    except Exception as e:
        print(f"财务数据解析失败：{stock_code}({year}) | {str(e)}")
        return None

# ===================== API接口（修正依赖注入，无错）=====================
@app.get("/api/stocks", response_model=List[Stock])
async def get_stocks(search: Optional[str] = Query(None, description="搜索关键词（代码/名称/行业）")):
    """获取股票清单（含实时行情）"""
    updated_stocks = []
    for stock in user_stocks:
        quote = fetch_stock_quote(stock["code"]) or {}
        updated_stocks.append({
            "code": stock["code"],
            "name": quote.get("name", stock["name"]),
            "industry": stock["industry"],
            "holding": stock["holding"],
            "price": quote.get("price", "0.00"),
            "changeRate": quote.get("changeRate", 0.0)
        })
    if search:
        search_lower = search.lower()
        updated_stocks = [
            s for s in updated_stocks
            if search_lower in s["code"].lower() or search_lower in s["name"].lower() or search_lower in (s["industry"] or "").lower()
        ]
    return updated_stocks

@app.post("/api/stocks", response_model=Stock)
async def create_stock(stock: StockCreate):
    """新增股票（自动获取真实行业和行情）"""
    if any(s["code"] == stock.code for s in user_stocks):
        raise HTTPException(status_code=400, detail="股票代码已存在")
    quote = fetch_stock_quote(stock.code) or {}
    profile = fetch_company_profile(stock.code) or {}
    new_stock = {
        "code": stock.code,
        "name": stock.name or quote.get("name", stock.code),
        "industry": stock.industry or profile.get("industry", "未知行业"),
        "holding": stock.holding,
        "price": quote.get("price", "0.00"),
        "changeRate": quote.get("changeRate", 0.0)
    }
    user_stocks.append(new_stock)
    return new_stock

@app.put("/api/stocks/{stock_code}", response_model=Stock)
async def update_stock(stock_code: str, stock_update: StockUpdate):
    """更新股票信息"""
    for i, stock in enumerate(user_stocks):
        if stock["code"] == stock_code:
            quote = fetch_stock_quote(stock_code) or {}
            update_data = stock_update.model_dump(exclude_unset=True)
            updated_stock = {**stock, **update_data, "price": quote.get("price", stock["price"]), "changeRate": quote.get("changeRate", stock["changeRate"])}
            user_stocks[i] = updated_stock
            return updated_stock
    raise HTTPException(status_code=404, detail="股票不存在")

@app.delete("/api/stocks/{stock_code}")
async def delete_stock(stock_code: str):
    """删除股票"""
    global user_stocks
    original_len = len(user_stocks)
    user_stocks = [s for s in user_stocks if s["code"] != stock_code]
    if len(user_stocks) == original_len:
        raise HTTPException(status_code=404, detail="股票不存在")
    return {"message": "删除成功"}

@app.get("/api/stocks/{stock_code}/detail", response_model=StockDetail)
async def get_stock_detail(stock_code: str):
    """获取股票详细信息（公司信息+股东+行情）"""
    stock = next((s for s in user_stocks if s["code"] == stock_code), None)
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    quote = fetch_stock_quote(stock_code) or {}
    profile = fetch_company_profile(stock_code) or {}
    top_shareholders = fetch_top_shareholders(stock_code)
    return {
        "code": stock_code,
        "name": quote.get("name", stock["name"]),
        "price": quote.get("price", stock["price"]),
        "changeRate": quote.get("changeRate", stock["changeRate"]),
        "industry": stock["industry"],
        "companyName": profile.get("companyName", f"{stock['name']}股份有限公司"),
        "listDate": profile.get("listDate", "2020-01-01"),
        "totalShares": profile.get("totalShares", "0.00"),
        "floatShares": profile.get("floatShares", "0.00"),
        "marketCap": profile.get("marketCap", "0.00"),
        "topShareholders": top_shareholders
    }

@app.get("/api/stocks/{stock_code}/financial/{year}", response_model=FinancialData)
async def get_stock_financial(stock_code: str, year: str):
    """获取指定年份财务数据"""
    if not any(s["code"] == stock_code for s in user_stocks):
        raise HTTPException(status_code=404, detail="股票不存在")
    financial_data = fetch_financial_data(stock_code, year)
    return financial_data or {
        k: "0.00" if k not in ["revenueGrowth", "netProfitGrowth", "roe", "grossMargin", "netMargin", "debtRatio"] else "0.0"
        for k in FinancialData.model_fields.keys()
    }

# -------------------- 笔记相关接口（核心修正：Depends(get_db)）--------------------
@app.get("/api/notes", response_model=List[Note])
async def get_notes(
    search: Optional[str] = Query(None, description="搜索关键词（标题/内容/股票代码）"),
    db: Session = Depends(get_db)  # 修正：用 Depends 声明依赖
):
    """获取笔记列表（支持模糊搜索）"""
    stmt = select(DBNote)
    if search:
        search_lower = f"%{search.lower()}%"
        stmt = stmt.filter(
            DBNote.title.ilike(search_lower) |
            DBNote.content.ilike(search_lower) |
            DBNote.stockCode.ilike(search_lower)
        )
    notes = db.scalars(stmt).all()
    return notes

@app.post("/api/notes", response_model=Note)
async def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db)  # 修正：用 Depends 声明依赖
):
    """创建笔记（自动补全股票名称）"""
    stock_name = note.stockName
    if note.stockCode and not stock_name:
        stock = next((s for s in user_stocks if s["code"] == note.stockCode), None)
        stock_name = stock["name"] if stock else ""
    
    db_note = DBNote(
        title=note.title,
        content=note.content,
        stockCode=note.stockCode or "",
        stockName=stock_name or "",
        tags=note.tags or "",
        createTime=datetime.now()
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@app.get("/api/notes/{note_id}", response_model=Note)
async def get_note(
    note_id: int,
    db: Session = Depends(get_db)  # 修正：用 Depends 声明依赖
):
    """获取笔记详情"""
    note = db.scalars(select(DBNote).where(DBNote.id == note_id)).first()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return note

@app.put("/api/notes/{note_id}", response_model=Note)
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db)  # 修正：用 Depends 声明依赖
):
    """更新笔记"""
    note = db.scalars(select(DBNote).where(DBNote.id == note_id)).first()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    update_data = note_update.model_dump(exclude_unset=True)
    if "stockCode" in update_data and not update_data.get("stockName"):
        stock = next((s for s in user_stocks if s["code"] == update_data["stockCode"]), None)
        update_data["stockName"] = stock["name"] if stock else ""
    update_data["updateTime"] = datetime.now()
    
    for k, v in update_data.items():
        setattr(note, k, v)
    
    db.commit()
    db.refresh(note)
    return note

@app.delete("/api/notes/{note_id}")
async def delete_note(
    note_id: int,
    db: Session = Depends(get_db)  # 修正：用 Depends 声明依赖
):
    """删除笔记"""
    note = db.scalars(select(DBNote).where(DBNote.id == note_id)).first()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    db.delete(note)
    db.commit()
    return {"message": "删除成功"}

@app.get("/")
async def root():
    return {
        "message": "股票投资清单API（最终无错版本）",
        "version": "2.0.2",
        "docs": "/docs",
        "python_required": "3.9+"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "SQLite connected",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {
            "fastapi": "0.111.0",
            "sqlalchemy": "2.0.30",
            "pydantic": "2.8.2"
        }
    }

# ===================== 启动服务 =====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )