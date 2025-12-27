from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import db
from services.stock import stock_router, market_router
from services.note import note_router
from apis.cost_analysis_api import position_analysis_router
from apis.cheesefortune_api import cheesefortune_router
from apis.cache_management_api import cache_router

# -------------- 初始化APP --------------
app = FastAPI(title="市场概览+笔记+股票清单API", version="1.0")

# -------------- 跨域配置 --------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------- 初始化数据库 --------------
db.init_database()

# -------------- 注册路由 --------------
app.include_router(market_router)  # 市场概览路由
app.include_router(stock_router)   # 股票模块路由
app.include_router(note_router)    # 笔记模块路由
app.include_router(position_analysis_router)  # 持仓分析模块路由
app.include_router(cheesefortune_router)  # 芝士财富API路由
app.include_router(cache_router)  # 缓存管理API路由

# -------------- 启动服务 --------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)