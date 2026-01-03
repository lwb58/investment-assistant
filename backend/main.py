from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from models import db
from services.stock import stock_router, market_router
from services.note import note_router
from services.tag import tag_router
from apis.cost_analysis_api import position_analysis_router
from apis.cheesefortune_api import cheesefortune_router
from apis.cache_management_api import cache_router
from apis.transaction_analysis_api import router as transaction_analysis_router

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

# -------------- 配置静态文件服务 --------------
# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 配置/picture路径为静态文件目录
app.mount("/picture", StaticFiles(directory=os.path.join(current_dir, "picture")), name="picture")

# -------------- 注册路由 --------------
app.include_router(market_router)  # 市场概览路由
app.include_router(stock_router)   # 股票模块路由
app.include_router(note_router)    # 笔记模块路由
app.include_router(tag_router)     # 标签模块路由
app.include_router(position_analysis_router)  # 持仓分析模块路由
app.include_router(cheesefortune_router)  # 芝士财富API路由
app.include_router(cache_router)  # 缓存管理API路由
app.include_router(transaction_analysis_router)  # 交割单分析模块路由

# -------------- 启动服务 --------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)