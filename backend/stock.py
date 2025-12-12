from urllib.parse import quote
import asyncio
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import Optional, List, Dict, Union, Any, Callable
import random
import logging
import db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from functools import wraps
from util import (
    get_stock_market, parse_sina_hq, format_field, fetch_url,
    cache_with_timeout, get_last_trade_date, sync_cache_with_timeout,
    CORE_QUOTES_FIELDS, SUPPLEMENT_FIELDS, DataSource, stock_quote_cache
)
from bs4 import BeautifulSoup
import re
import time

logger = logging.getLogger(__name__)

# -------------- 统一错误处理装饰器 --------------
def api_error_handler(func: Callable) -> Callable:
    """API错误处理装饰器
    统一处理API函数中的异常，记录日志并返回标准格式的错误响应
    :param func: API函数
    :return: 包装后的API函数
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # 已处理的HTTP异常，直接抛出
            raise
        except Exception as e:
            logger.error(f"API错误 [{func.__name__}]: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException:
            # 已处理的HTTP异常，直接抛出
            raise
        except Exception as e:
            logger.error(f"API错误 [{func.__name__}]: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

# 创建路由实例
stock_router = APIRouter(prefix="/api/stocks", tags=["股票模块"])
market_router = APIRouter(prefix="/api/market", tags=["市场概览"])

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

# 股票相关模型
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

class StockQuoteResponse(BaseModel):
    baseInfo: Dict[str, str]
    coreQuotes: Dict[str, Union[str, float, int]]
    supplementInfo: Dict[str, Union[str, float, bool]]
    dataValidity: Dict[str, Union[bool, str]]

class StockFinancialData(BaseModel):
    """股票财务数据模型"""
    revenue: str  # 营业收入（亿元）
    revenueGrowth: str  # 营收增长率（%）
    netProfit: str  # 净利润（亿元）
    netProfitGrowth: str  # 净利润增长率（%）
    eps: str  # 每股收益（元）
    navps: str  # 每股净资产（元）
    roe: str  # 净资产收益率（%）
    pe: str  # 市盈率（TTM）
    pb: str  # 市净率
    grossMargin: str  # 毛利率（%）
    netMargin: str  # 净利率（%）
    debtRatio: str  # 负债率（%）

class StockShareholder(BaseModel):
    """十大股东模型"""
    name: str  # 股东名称
    type: str  # 股东类型
    percentage: str  # 持股比例（%）

# 估值逻辑相关模型
class ValuationLogicItem(BaseModel):
    id: Optional[str] = None
    stockCode: str
    stockName: str
    valuationContent: str
    investmentForecast: Optional[str] = ""
    tradingPlan: Optional[str] = ""
    createTime: Optional[str] = None
    updateTime: Optional[str] = None

class StockDetailResponse(BaseModel):
    """股票详情响应模型"""
    baseInfo: Dict[str, Union[str, float]]  # 基础信息
    coreQuotes: Dict[str, Union[str, float, int]]  # 实时行情
    financialData: Dict[str, StockFinancialData]  # 年度财务数据（key: 年份）
    mllsj: Dict[str, Dict[str, str]]  # 毛利率和净利率季度数据
    topShareholders: List[StockShareholder]  # 十大股东
    dataValidity: Dict[str, Union[bool, str]]  # 数据有效性

class DupontAnalysisResponse(BaseModel):
    """杜邦分析响应模型"""
    stock_id: str  # 股票代码
    full_data: Optional[List[Dict]]  # 全量数据
    error: Optional[str]  # 错误信息

# -------------- 港股详细数据获取函数 --------------
def get_hk_stock_detail_from_eastmoney(stock_id: str) -> Optional[Dict[str, Any]]:
    """
    从东方财富API获取港股详细数据
    - stock_id: 5位港股代码（如02367）
    - 返回: 包含总市值、股本、行业等信息的字典
    """
    logger.info(f"从东方财富API获取港股{stock_id}详细数据")
    
    try:
        # 使用东方财富API获取港股数据
        url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_CUSTOM_HKF10_FN_MAININDICATORMAX&columns=ORG_CODE%2CSECUCODE%2CSECURITY_CODE%2CSECURITY_NAME_ABBR%2CSECURITY_INNER_CODE%2CREPORT_DATE%2CBASIC_EPS%2CPER_NETCASH_OPERATE%2CBPS%2CBPS_NEDILUTED%2CCOMMON_ACS%2CPER_SHARES%2CISSUED_COMMON_SHARES%2CHK_COMMON_SHARES%2CTOTAL_MARKET_CAP%2CHKSK_MARKET_CAP%2COPERATE_INCOME%2COPERATE_INCOME_SQ%2COPERATE_INCOME_QOQ%2COPERATE_INCOME_QOQ_SQ%2CHOLDER_PROFIT%2CHOLDER_PROFIT_SQ%2CHOLDER_PROFIT_QOQ%2CHOLDER_PROFIT_QOQ_SQ%2CPE_TTM%2CPE_TTM_SQ%2CPB_TTM%2CPB_TTM_SQ%2CNET_PROFIT_RATIO%2CNET_PROFIT_RATIO_SQ%2CROE_AVG%2CROE_AVG_SQ%2CROA%2CROA_SQ%2CDIVIDEND_TTM%2CDIVIDEND_LFY%2CDIVI_RATIO%2CDIVIDEND_RATE%2CIS_CNY_CODE&filter=(SECUCODE%3D%22{stock_id}.HK%22)&pageNumber=1&pageSize=1&sortTypes=-1&sortColumns=REPORT_DATE&source=F10&client=PC&v=06695186382178545"
        
        response = fetch_url(url, retry=3)
        if not response:
            logger.error(f"东方财富API返回空数据: {stock_id}")
            return None
        
        data = response
        if not data.get('success') or not data.get('result', {}).get('data'):
            logger.error(f"东方财富API返回错误或无数据: {stock_id}")
            return None
        
        eastmoney_data = data['result']['data'][0]
        
        # 转换数据格式
        result = {
            "total_market_cap": eastmoney_data.get("TOTAL_MARKET_CAP", 0),  # 总市值
            "hk_market_cap": eastmoney_data.get("HKSK_MARKET_CAP", 0),  # 港股市值
            "issued_common_shares": eastmoney_data.get("ISSUED_COMMON_SHARES", 0),  # 已发行普通股
            "hk_common_shares": eastmoney_data.get("HK_COMMON_SHARES", 0),  # 港股普通股
            "common_acs": eastmoney_data.get("COMMON_ACS", 0),  # 总权益
            "pe_ttm": round(eastmoney_data.get("PE_TTM", 0), 2),  # 市盈率TTM（保留两位小数）
            "pb_ttm": round(eastmoney_data.get("PB_TTM", 0), 2),  # 市净率TTM（保留两位小数）
            "basic_eps": eastmoney_data.get("BASIC_EPS", 0),  # 基本每股收益
            "net_profit_ratio": round(eastmoney_data.get("NET_PROFIT_RATIO", 0), 2),  # 净利润率（保留两位小数）
            "roe_avg": round(eastmoney_data.get("ROE_AVG", 0), 2),  # 平均净资产收益率（保留两位小数）
            "roa": round(eastmoney_data.get("ROA", 0), 2),  # 资产收益率（保留两位小数）
            "dividend_ttm": eastmoney_data.get("DIVIDEND_TTM", 0),  # 股息TTM
            "dividend_rate": round(eastmoney_data.get("DIVIDEND_RATE", 0), 2),  # 股息率（保留两位小数）
            "operate_income": eastmoney_data.get("OPERATE_INCOME", 0),  # 最新总营收
            "operate_income_sq": eastmoney_data.get("OPERATE_INCOME_SQ", 0),  # 同比总营收
            "holder_profit": eastmoney_data.get("HOLDER_PROFIT", 0),  # 最新归母净利润
            "holder_profit_sq": eastmoney_data.get("HOLDER_PROFIT_SQ", 0),  # 同比归母净利润
            "stock_name": eastmoney_data.get("SECURITY_NAME_ABBR", ""),  # 股票名称
            "security_code": eastmoney_data.get("SECURITY_CODE", ""),  # 股票代码
            "report_date": eastmoney_data.get("REPORT_DATE", ""),  # 报告日期
        }
        
        logger.info(f"成功获取港股{stock_id}详细数据 - 总市值: {result['total_market_cap']}, 已发行股本: {result['issued_common_shares']}")
        return result
        
    except Exception as e:
        logger.error(f"获取港股{stock_id}详细数据失败: {str(e)}", exc_info=True)
        return None

# -------------- 核心修复：同步行情获取函数 --------------
def get_tencent_stock_data(stock_code: str) -> Optional[Dict[str, Any]]:
    """
    获取腾讯财经的股票数据（包含市值和市盈率）
    - stock_code: 6位股票代码（如600036）
    - 返回: 包含市值、市盈率等信息的字典
    """
    logger.info(f"请求腾讯财经股票数据: {stock_code}")
    
    # 获取市场代码（sh/sz）
    market = get_stock_market(stock_code)
    if not market:
        logger.warning(f"不支持的市场: {stock_code}（仅支持沪深A：60/00/30开头）")
        return None
    
    # 构造腾讯财经接口URL
    # 格式：http://qt.gtimg.cn/q=sh600036
    tencent_code = f"{market}{stock_code}"
    tencent_url = f"http://qt.gtimg.cn/q={tencent_code}"
    
    try:
        # 请求数据
        response = fetch_url(tencent_url, retry=3)
        if not response:
            logger.error(f"腾讯接口返回空数据: {stock_code}")
            return None
        
        # 解析腾讯财经的数据格式
        # 格式：v_sh600036="1~招商银行~600036~30.75~30.65~30.68~457585~27775~28689~457585~4817412425~..."
        if isinstance(response, str):
            # 提取数据部分
            data_part = response.split('="')[1].split('"')[0]
            fields = data_part.split('~')
            
            if len(fields) < 41:
                logger.error(f"腾讯财经数据字段不足: {stock_code}")
                return None
            
            # 提取市值和市盈率数据
            # 根据实际测试的腾讯财经数据字段映射：
            # 3: 当前价格
            # 32: 涨跌幅百分比
            # 39: 市盈率(PE)
            # 44: 总市值（亿元，可能是旧数据）
            # 45: 流通市值（亿元，约等于总市值）
            # 46: 市净率(PB)
            return {
                "currentPrice": float(fields[3]) if fields[3] and fields[3].replace('.', '').isdigit() else 0.0,
                "marketCap": float(fields[45]) * 100000000 if fields[45] and fields[45].replace('.', '').isdigit() else 0.0,  # 流通市值（亿元转元，约1.1万亿）
                "floatMarketCap": float(fields[45]) * 100000000 if fields[45] and fields[45].replace('.', '').isdigit() else 0.0,  # 流通市值（亿元转元）
                "peDynamic": float(fields[39]) if fields[39] and fields[39].replace('.', '').isdigit() and float(fields[39]) > 0 and float(fields[39]) < 1000 else 0.0,  # 市盈率(7.32)
                "peStatic": float(fields[39]) if fields[39] and fields[39].replace('.', '').isdigit() and float(fields[39]) > 0 and float(fields[39]) < 1000 else 0.0,  # 暂时使用同一市盈率
                "pbRatio": float(fields[46]) if fields[46] and fields[46].replace('.', '').isdigit() and float(fields[46]) > 0 else 0.0,  # 市净率(1.00)
                "changeRate": float(fields[32]) if fields[32] and fields[32].replace('.', '').isdigit() else 0.0,  # 涨跌幅(0.49%)
                "totalShares": float(fields[45]) * 100000000 / float(fields[3]) if fields[3] and fields[3] != '0.00' and fields[45] else 0.0,  # 市值/价格 = 总股数
                "floatShares": float(fields[45]) * 100000000 / float(fields[3]) if fields[3] and fields[3] != '0.00' and fields[45] else 0.0,  # 流通市值/价格 = 流通股数
                "psRatio": float(fields[70]) if fields[70] and fields[70].replace('.', '').isdigit() and float(fields[70]) > 0 else 0.0  # 市销率
            }
        
    except Exception as e:
        logger.error(f"获取腾讯财经股票{stock_code}数据失败: {str(e)}", exc_info=True)
    
    return None

@sync_cache_with_timeout(300)
def validate_stock_code(stock_code: str) -> Optional[str]:
    """验证股票代码格式和有效性
    :param stock_code: 股票代码
    :return: 市场代码或None（如果代码无效）
    """
    if not stock_code.isdigit():
        logger.warning(f"股票代码格式错误: {stock_code}（必须是纯数字）")
        return None
    
    market = get_stock_market(stock_code)
    if not market:
        logger.warning(f"不支持的市场: {stock_code}")
        return None
    
    return market

@sync_cache_with_timeout(300)
def get_stock_quotes_from_eastmoney(stock_code: str) -> Optional[Dict[str, Any]]:
    """从东方财富API获取股票实时行情"""
    logger.info(f"从东方财富API获取股票{stock_code}行情数据")
    
    # 校验股票代码
    market = validate_stock_code(stock_code)
    if not market:
        return None
    
    # 构造东方财富接口的secid参数
    if market == "rt_hk":
        # 港股：secid=116.股票代码（如116.09633）
        secid = f"116.{stock_code}"
    elif market == "sh":
        # 沪A：secid=1.股票代码
        secid = f"1.{stock_code}"
    elif market == "sz":
        # 深A：secid=0.股票代码
        secid = f"0.{stock_code}"
    elif market == "bj":
        # 北交所：secid=1.股票代码
        secid = f"1.{stock_code}"
    else:
        logger.error(f"不支持的市场类型：{market}")
        return None
    
    # 构造东方财富行情接口URL，获取必要的字段
    eastmoney_url = f"https://push2.eastmoney.com/api/qt/stock/get?fields=f57%2Cf58%2Cf43%2Cf44%2Cf45%2Cf46%2Cf47%2Cf48%2Cf50%2Cf164%2Cf168%2Cf170%2Cf171%2Cf179%2Cf183&secid={secid}&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&wbp2u=%7C0%7C0%7C0%7Cweb&v=09371029070054959"
    
    try:
        # 请求东方财富接口
        response = fetch_url(eastmoney_url, retry=3)
        
        if not response or "data" not in response:
            logger.error(f"东方财富接口返回无效数据：{response}")
            return None
        
        data = response["data"]
        
        # 获取当前价格（使用f43或f179，两者相同）
        current_price = format_field(data.get("f43"), float) or format_field(data.get("f179"), float)
        if not current_price:
            logger.error(f"东方财富接口未返回有效价格数据：{data}")
            return None
        
        # 计算昨收价（根据当前价和涨跌额计算）
        price_change = format_field(data.get("f168"), float) or 0.0
        prev_close_price = current_price - price_change
        
        # 构造行情数据结构，使用正确的字段和单位转换
        core_quotes = {
            "stockName": data.get("f58", "未知名称"),  # 股票名称
            "currentPrice": current_price,  # 当前价
            "openPrice": format_field(data.get("f46"), float),  # 今开
            "prevClosePrice": round(prev_close_price, 2),  # 昨收（通过当前价和涨跌额计算）
            "highPrice": format_field(data.get("f44"), float),  # 最高
            "lowPrice": format_field(data.get("f45"), float),  # 最低
            "volume": format_field(data.get("f48"), int),  # 成交量
            "amount": format_field(data.get("f47"), float),  # 成交额（使用f47字段）
            "priceChange": round(format_field(data.get("f168"), float) or 0.0, 2),  # 涨跌额
            "changePercent": round((format_field(data.get("f164"), float) or 0.0) / 100, 2),  # 涨跌幅（除以100）
            "turnoverRate": format_field(data.get("f50"), float),  # 换手率
            "pe": round(format_field(data.get("f170"), float) or 0.0, 2),  # 市盈率（直接使用）
            "marketCap": format_field(data.get("f183"), float)  # 总市值（使用f183字段）
        }
        
        # 确定市场名称
        market_name = "港股通" if market == "rt_hk" else "沪A" if market == "sh" else "深A" if market == "sz" else "北交所"
        
        result = {
            "baseInfo": {
                "stockCode": stock_code,
                "market": market_name,
                "stockName": core_quotes["stockName"],
                "industry": "--"
            },
            "coreQuotes": core_quotes,
            "supplementInfo": {
                "industry": "--"
            },
            "dataValidity": {
                "isValid": core_quotes["currentPrice"] >= 0 and core_quotes["stockName"] != "未知名称",
                "reason": "" if (core_quotes["currentPrice"] >= 0 and core_quotes["stockName"] != "未知名称") else "股票数据无效"
            }
        }
        
        logger.info(f"东方财富行情解析完成 - 股票: {stock_code}, 最新价: {core_quotes['currentPrice']}, 涨跌幅: {core_quotes['changePercent']}%")
        return result
        
    except Exception as e:
        logger.error(f"获取东方财富行情失败: {str(e)}", exc_info=True)
        return None

@sync_cache_with_timeout(300)
def get_stock_quotes(stock_code: str) -> Optional[Dict[str, Any]]:
    """获取股票实时行情（同步版本，支持港股）"""
    logger.info(f"同步请求股票行情: {stock_code}")
    
    # 优先使用东方财富接口
    eastmoney_data = get_stock_quotes_from_eastmoney(stock_code)
    if eastmoney_data:
        return eastmoney_data
    
    # 如果东方财富接口失败，降级使用新浪接口
    logger.info(f"东方财富接口失败，降级使用新浪接口")
    
    # 校验股票代码
    market = validate_stock_code(stock_code)
    if not market:
        return None
    
    # 构造接口URL
    if market == "rt_hk":
        # 港股URL格式 - 使用正确的参数列表、随机数格式（浮点数）和完整的5位股票代码
        random_num = random.random()  # 生成0到1之间的随机浮点数
        full_stock_code = stock_code.zfill(5)  # 确保是5位代码
        sina_list = f"rt_hk{full_stock_code},rt_hk{full_stock_code}_preipo,rt_hkHSI,rt_hkHSI_preipo"
        sina_url = f"https://hq.sinajs.cn/?_={random_num}&list={sina_list}"
    else:
        # A股URL格式
        random_num = int(time.time() * 1000)
        sina_list = f"{market}{stock_code},{market}{stock_code}_i"
        sina_url = f"https://hq.sinajs.cn/rn={random_num}&list={sina_list}"
    
    try:
        # 增加重试机制，确保接口访问成功
        hq_data = fetch_url(sina_url, is_sina_var=True, retry=3)
        parsed_data = {}
        
        if hq_data:
            # 解析行情数据
            parsed_data = parse_sina_hq(hq_data)
        
        # 如果港股核心数据不存在，尝试从搜索建议接口获取
        stock_key = f"rt_hk{stock_code.zfill(5)}"  # 使用5位代码作为stock_key
        stock_name = f"港股{stock_code}"
        
        if market == "rt_hk" and stock_key not in parsed_data:
            logger.info(f"尝试从搜索建议接口获取港股{stock_code}的信息")
            search_url = f"https://suggest3.sinajs.cn/suggest/type=11&key={stock_code}&name=suggestdata_{random.random()}"
            search_data = fetch_url(search_url, is_sina_var=False, retry=2)
            
            if search_data:
                # 解析搜索建议数据
                match = re.search(r'"([^"]+)"', search_data)
                if match:
                    suggest_data = match.group(1)
                    if suggest_data:
                        # 查找匹配的股票数据
                        for item in suggest_data.split(";"):
                            if item:
                                fields = item.split(",")
                                if len(fields) >= 5 and fields[2] == stock_code:
                                    # 构造模拟的行情数据
                                    stock_name = fields[4] if len(fields) > 4 else stock_name
                                    mock_data = f'var hq_str_{stock_key}="{stock_name},0,0,0,0,0,0,0,0,0";'
                                    parsed_data.update(parse_sina_hq(mock_data))
                                    logger.info(f"成功从搜索建议接口获取港股{stock_code}的信息")
                                    break
            
            # 如果仍然没有数据，返回None而不是构造全0的模拟数据
            if stock_key not in parsed_data:
                logger.info(f"无法获取港股{stock_code}的信息，返回None")
                return None
        
        if not parsed_data:
            logger.error(f"新浪接口返回空数据: {stock_code}")
            return None
        
        if market == "rt_hk":
            # 港股数据处理 - 使用5位代码作为stock_key
            stock_key = f"rt_hk{stock_code.zfill(5)}"
            
            # 校验核心数据是否存在
            if stock_key not in parsed_data:
                logger.error(f"未找到港股{stock_code}的核心行情数据")
                return None
            
            core_data = parsed_data[stock_key]
            if len(core_data) < 10:
                logger.error(f"港股{stock_code}核心字段不足（仅{len(core_data)}个）")
                return None
            
            # 解析港股核心行情 - 根据新浪港股数据格式调整字段索引
            core_quotes = {
                "stockName": core_data[1] if len(core_data) > 1 else core_data[0],  # 使用中文名称
                "currentPrice": format_field(core_data[6], lambda x: float(x) if x else 0.0),  # 当前价
                "prevClosePrice": format_field(core_data[2], lambda x: float(x) if x else 0.0),  # 昨收价
                "openPrice": format_field(core_data[3], lambda x: float(x) if x else 0.0),  # 开盘价
                "highPrice": format_field(core_data[4], lambda x: float(x) if x else 0.0),  # 最高价
                "lowPrice": format_field(core_data[5], lambda x: float(x) if x else 0.0),  # 最低价
                "volume": format_field(core_data[12], lambda x: int(x) if x else 0),  # 成交量
                "amount": format_field(core_data[11], lambda x: float(x) if x else 0.0),  # 成交额
                "priceChange": format_field(core_data[7], lambda x: float(x) if x else 0.0),  # 涨跌额
                "changePercent": format_field(core_data[8], lambda x: float(x) if x else 0.0)  # 涨跌幅
                # 新浪港股接口没有直接提供总市值字段，所以不设置marketCap
            }
            
            # 港股没有补充信息和腾讯数据
            supplement_info = {"industry": "--"}
            tencent_data = None
            
            logger.info(f"港股{stock_code}行情解析完成 - 最新价: {core_quotes['currentPrice']}, 昨收: {core_quotes['prevClosePrice']}, 股票名称: {core_quotes['stockName']}")
            
            result = {
                "baseInfo": {
                    "stockCode": stock_code,
                    "market": "港股通",
                    "stockName": core_quotes["stockName"],
                    "industry": supplement_info["industry"]
                },
                "coreQuotes": core_quotes,
                "supplementInfo": supplement_info,
                "dataValidity": {
                    "isValid": core_quotes["currentPrice"] >= 0 and core_quotes["stockName"] != "",
                    "reason": "" if (core_quotes["currentPrice"] >= 0 and core_quotes["stockName"] != "") 
                              else "股票数据无效（可能停牌、退市或代码错误）"
                }
            }
        else:
            # A股数据处理
            stock_key = f"{market}{stock_code}"
            supplement_key = f"{market}{stock_code}_i"
            
            # 校验核心数据是否存在
            if stock_key not in parsed_data:
                logger.error(f"未找到股票{stock_code}的核心行情数据")
                return None
            
            core_data = parsed_data[stock_key]
            if len(core_data) < 32:
                logger.error(f"股票{stock_code}核心字段不足（仅{len(core_data)}个）")
                return None
            
            # 解析核心行情
            core_quotes = {}
            for field, (idx, field_name, field_type, formatter) in CORE_QUOTES_FIELDS.items():
                value = core_data[idx] if len(core_data) > idx else ""
                core_quotes[field] = format_field(value, formatter)
                logger.debug(f"股票{stock_code} - {field_name}: {core_quotes[field]}")
            
            # 解析补充信息
            supplement_data = parsed_data.get(supplement_key, [])
            supplement_info = {}
            for field, (idx, field_name, field_type, formatter) in SUPPLEMENT_FIELDS.items():
                value = supplement_data[idx] if len(supplement_data) > idx else ""
                supplement_info[field] = format_field(value, formatter)
            
            # 获取腾讯财经的补充数据（市值和市盈率）
            tencent_data = get_tencent_stock_data(stock_code)
            
            # 输出关键数据日志，便于排查
            current_price = core_quotes["currentPrice"]
            prev_close = core_quotes["prevClosePrice"]
            logger.info(f"股票{stock_code}行情解析完成 - 最新价: {current_price}, 昨收: {prev_close}, 股票名称: {core_quotes['stockName']}")
            
            result = {
                "baseInfo": {
                    "stockCode": stock_code,
                    "market": "沪A" if market == "sh" else "深A" if market == "sz" else "北A",
                    "stockName": core_quotes["stockName"],
                    "industry": supplement_info["industry"]
                },
                "coreQuotes": core_quotes,
                "supplementInfo": supplement_info,
                "dataValidity": {
                    "isValid": current_price >= 0 and core_quotes["stockName"] != "未知名称",
                    "reason": "" if (current_price >= 0 and core_quotes["stockName"] != "未知名称") 
                              else "股票数据无效（可能停牌、退市或代码错误）"
                }
            }
            
            # 添加腾讯财经数据（如果获取成功）
            if tencent_data:
                result["tencentData"] = tencent_data
        
        return result
    
    except Exception as e:
        logger.error(f"股票{stock_code}行情解析失败: {str(e)}", exc_info=True)
        return None

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

# -------------- 市场概览接口 --------------
@api_error_handler
@market_router.get("/overview", response_model=MarketOverview)
def get_market_overview():
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

def enhance_stock_with_quotes(stock: Dict[str, Any]) -> Dict[str, Any]:
    """增强股票数据，添加行情信息（当前价、涨跌幅等）
    :param stock: 股票基本信息
    :return: 添加了行情信息的股票字典
    """
    stock_with_quotes = stock.copy()
    stock_code = stock["stockCode"]
    
    try:
        logger.info(f"正在获取股票{stock_code}行情数据")
        # 直接调用同步行情函数（带缓存）
        quote_data = get_stock_quotes(stock_code)
        
        if quote_data and "coreQuotes" in quote_data:
            core_quotes = quote_data["coreQuotes"]
            current_price = core_quotes.get("currentPrice", 0.0)
            prev_close = core_quotes.get("prevClosePrice", 0.0)
            
            # 计算涨跌幅（优化逻辑，处理特殊情况）
            if prev_close > 0.01 and current_price >= 0:
                change_amount = current_price - prev_close
                change_rate = (change_amount / prev_close) * 100
            else:
                change_amount = 0.0
                change_rate = 0.0
                if prev_close <= 0.01:
                    logger.warning(f"股票{stock_code}昨收盘价无效（{prev_close}），无法计算涨跌幅")
                else:
                    logger.info(f"股票{stock_code}当前价为0（可能停牌）")
            
            # 赋值结果（保留两位小数）
            stock_with_quotes["currentPrice"] = round(current_price, 2)
            stock_with_quotes["changeAmount"] = round(change_amount, 2)
            stock_with_quotes["changeRate"] = round(change_rate, 2)
            stock_with_quotes["updateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"股票{stock_code}行情处理完成 - 最新价: {current_price}, 涨跌幅: {change_rate:.2f}%")
        else:
            logger.warning(f"股票{stock_code}无有效行情数据")
            stock_with_quotes["currentPrice"] = 0.0
            stock_with_quotes["changeAmount"] = 0.0
            stock_with_quotes["changeRate"] = 0.0
            stock_with_quotes["updateTime"] = ""
            
    except Exception as e:
        logger.error(f"处理股票{stock_code}行情失败: {str(e)}", exc_info=True)
        stock_with_quotes["currentPrice"] = 0.0
        stock_with_quotes["changeAmount"] = 0.0
        stock_with_quotes["changeRate"] = 0.0
        stock_with_quotes["updateTime"] = ""
    
    return stock_with_quotes

# -------------- 股票清单接口（核心修复）--------------
@api_error_handler
@stock_router.get("", response_model=List[StockItem])
def get_all_stocks(search: Optional[str] = Query(None)):
    """获取股票清单（支持搜索，修复价格和涨跌幅为0的问题）"""
    stocks_to_process = db.get_all_stocks(search=search)
    result_stocks = []
    
    logger.info(f"获取股票清单，搜索条件：{search}，共{len(stocks_to_process)}支股票")
    
    for stock in stocks_to_process:
        stock_with_quotes = enhance_stock_with_quotes(stock)
        result_stocks.append(stock_with_quotes)
    
    logger.info(f"股票清单获取完成，返回{len(result_stocks)}支数据")
    return result_stocks

# -------------- 单只股票接口（修复）--------------
@api_error_handler
@stock_router.get("/{stock_id}", response_model=StockItem)
def get_stock(stock_id: str):
    """获取单只股票"""
    stock = db.get_stock_by_id(stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 添加行情数据
    enhanced_stock = enhance_stock_with_quotes(stock)
    return enhanced_stock

# -------------- 股票行情接口 --------------
@api_error_handler
@stock_router.get("/{stock_code}/quotes", response_model=StockQuoteResponse)
def get_stock_quotes_api(stock_code: str):
    """获取股票实时行情（API接口）"""
    data = get_stock_quotes(stock_code)
    if not data:
        raise HTTPException(status_code=500, detail="行情数据获取失败")
    return data



# ------------------- 通用杜邦分析数据提取（支持A股和港股） -------------------
@api_error_handler
@stock_router.get("/dubang/{stock_id}", response_model=DupontAnalysisResponse)
def dupont_analysis(
    stock_id: str, 
    displaytype: str = "10",
    export_excel: bool = True  # 默认导出Excel（全量数据）
):
    """
    通用杜邦分析数据提取（自动判断A股/港股）
    - stock_id: 股票代码（如02367、600036）
    - 返回: 统一格式的杜邦分析响应
    """
    # 自动判断是A股还是港股
    # 港股代码通常为5位数字（如02367），A股为6位数字
    if len(stock_id) == 5 and stock_id.isdigit():
        # 港股处理
        return _hk_dupont_analysis_impl(stock_id, displaytype, export_excel)
    else:
        # A股处理（保留原有逻辑）
        return _a_dupont_analysis_impl(stock_id, displaytype, export_excel)


def _hk_dupont_analysis_impl(
    stock_id: str, 
    displaytype: str = "10",  # 保留参数以保持接口兼容性
    export_excel: bool = True  # 默认导出Excel（全量数据）
):
    """
    港股杜邦分析数据提取实现（使用东方财富网API）
    - stock_id: 港股代码（如02367）
    - 返回: 与A股杜邦分析相同格式的响应
    """
    result = {
        "stock_id": stock_id,  # 响应模型要求stock_id为字符串类型
        "full_data": None,  # 全量数据（含周期类型）
        "error": None
    }
    
    try:
        # 1. 构造东方财富网API请求URL
        secucode = f"{stock_id}.HK"
        url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_MAININDICATOR&columns=ALL&quoteColumns=&filter=(SECUCODE%3D%22{secucode}%22)&pageNumber=1&pageSize=20&sortTypes=-1&sortColumns=STD_REPORT_DATE&source=F10&client=PC&v=040146104118736425"
        
        logger.info(f"请求东方财富网港股杜邦分析数据: {stock_id}, URL: {url}")
        
        # 2. 发送请求并解析数据
        data = fetch_url(url, timeout=20, retry=3)
        if not data:
            result["error"] = "请求失败，未获取到数据"
            return result
        if "result" not in data or "data" not in data["result"]:
            result["error"] = "请求成功，但数据格式不正确"
            return result
        
        indicator_data = data["result"]["data"]
        if not indicator_data:
            result["error"] = "未找到有效数据（可能股票代码错误或无数据）"
            return result
        
        # 3. 解析并转换为与A股杜邦分析相同的格式
        full_data = []
        
        for item in indicator_data:
            # 解析报告日期和周期类型
            std_report_date = item.get("STD_REPORT_DATE", "").split()[0]  # 去除时间部分
            date_type_code = item.get("DATE_TYPE_CODE", "001")
            
            # 周期类型映射
            date_type_map = {
                "001": "年报",
                "002": "中报",
                "003": "一季报",
                "004": "三季报"
            }
            period_type = date_type_map.get(date_type_code, "未知周期")
            
            # 将数值转换为字符串并保留两位小数的辅助函数
            def format_value(value):
                if value is None or value == "":
                    return ""
                try:
                    # 尝试转换为浮点数
                    float_value = float(value)
                    # 保留两位小数并转换为字符串
                    return f"{float_value:.2f}"
                except (ValueError, TypeError):
                    # 如果转换失败，直接返回字符串
                    return str(value)
            
            # 获取关键指标用于计算
            operate_income = item.get("OPERATE_INCOME", "")
            total_assets = item.get("TOTAL_ASSETS", "")
            
            # 计算总资产周转率(次) = 营业总收入 / 总资产
            total_asset_turnover = ""
            try:
                op_income = float(operate_income)
                tot_assets = float(total_assets)
                if op_income != 0 and tot_assets != 0:
                    total_asset_turnover = op_income / tot_assets
            except (ValueError, TypeError):
                pass
            
            # 计算归母净利润（单位：亿元）
            def format_yuan_to_billion(value):
                if value is None or value == "":
                    return ""
                try:
                    # 尝试转换为浮点数并转换为亿元（除以100000000）
                    float_value = float(value)
                    # 保留两位小数并转换为字符串
                    return f"{float_value / 100000000:.2f}"
                except (ValueError, TypeError):
                    # 如果转换失败，直接返回字符串
                    return str(value)
            
            # 计算税负因素和利息负担
            # 税负因素 = (1 - 所得税费用/利润总额) * 100
            tax_factor = ""
            try:
                # 尝试获取利润总额，可能的字段名：TOTAL_PROFIT, PROFIT, PRETAX_PROFIT
                total_profit = float(item.get("TOTAL_PROFIT", item.get("PROFIT", item.get("PRETAX_PROFIT", "0"))))
                
                if total_profit != 0:
                    # 优先尝试获取所得税费用，可能的字段名：INCOME_TAX, TAX_EXPENSE
                    income_tax = float(item.get("INCOME_TAX", item.get("TAX_EXPENSE", "0")))
                    
                    if income_tax > 0:
                        # 如果有直接的所得税费用数据，使用它计算
                        tax_factor = f"{((1 - income_tax/total_profit) * 100):.2f}"
                    else:
                        # 否则尝试使用TAX_EBT（所得税占税前利润的比例）
                        tax_ebt = float(item.get("TAX_EBT", "0"))
                        if tax_ebt > 0:
                            # TAX_EBT是百分比，需要转换为小数
                            tax_factor = f"{(100 - tax_ebt):.2f}"
            except (ValueError, TypeError):
                tax_factor = ""
            
            # 利息负担 = (1 - 财务费用/营业利润) * 100
            interest_factor = ""
            try:
                # 财务费用字段查找：尝试多种可能的字段名
                financial_expense_fields = ["FINANCIAL_EXPENSE", "FINANCE_EXPENSE", "INTEREST_EXPENSE", "PREMIUM_EXPENSE"]
                financial_expense_value = None
                
                for field in financial_expense_fields:
                    field_value = item.get(field)
                    if field_value is not None:
                        financial_expense_value = field_value
                        break
                
                # 如果没有找到财务费用字段或值为None，设为0
                financial_expense = float(financial_expense_value) if financial_expense_value is not None else 0.0
                
                # 获取营业利润，尝试多种可能的字段
                operate_profit = None
                try:
                    # 尝试直接获取营业利润
                    if item.get("OPERATE_PROFIT") is not None:
                        operate_profit = float(item.get("OPERATE_PROFIT"))
                    elif item.get("GROSS_PROFIT") is not None and item.get("OPERATE_INCOME") is not None:
                        # 如果没有直接的营业利润，尝试使用毛利润作为近似值
                        operate_profit = float(item.get("GROSS_PROFIT"))
                    elif item.get("NET_PROFIT") is not None:
                        # 或者使用净利润作为近似值
                        operate_profit = float(item.get("NET_PROFIT"))
                    else:
                        operate_profit = 0.0
                except (ValueError, TypeError):
                    operate_profit = 0.0
                
                if operate_profit != 0:
                    interest_factor = f"{((1 - financial_expense/operate_profit) * 100):.2f}"
                else:
                    # 如果没有可用的利润数据，保持默认值100%
                    interest_factor = "100.00"
            except (ValueError, TypeError) as e:
                # 如果计算出错，默认设为100%
                interest_factor = "100.00"
            
            # 注意：当利息负担为100%时，通常表示该公司没有财务费用（利息支出）
            # 这在现金充足、几乎没有债务的公司中很常见
            
            # 获取营业利润率（前端五因素分析使用经营利润率）
            # 尝试获取营业利润率，可能的字段名：OPERATE_PROFIT_RATIO, OPERATING_PROFIT_RATIO
            operating_margin = format_value(item.get("OPERATE_PROFIT_RATIO", item.get("OPERATING_PROFIT_RATIO", "")))
            
            # 如果没有直接的营业利润率数据，尝试手动计算
            if not operating_margin:
                try:
                    # 尝试获取营业利润
                    operate_profit_value = item.get("OPERATE_PROFIT")
                    if operate_profit_value is None:
                        # 如果营业利润为None，尝试使用其他替代方案
                        if "GROSS_PROFIT" in item:
                            # 使用毛利润作为近似值
                            operate_profit = float(item.get("GROSS_PROFIT", "0"))
                        elif "NET_PROFIT" in item:
                            # 使用净利润作为近似值
                            operate_profit = float(item.get("NET_PROFIT", "0"))
                        else:
                            operate_profit = 0.0
                    else:
                        try:
                            operate_profit = float(operate_profit_value)
                        except (ValueError, TypeError):
                            operate_profit = 0.0
                    
                    # 尝试获取营业总收入
                    op_income = float(operate_income) if operate_income else float(item.get("OPERATE_INCOME", "0"))
                    
                    if op_income != 0:
                        if operate_profit != 0:
                            operating_margin = f"{(operate_profit / op_income * 100):.2f}"
                        elif "GROSS_PROFIT" in item:
                            # 如果没有营业利润，尝试使用毛利率作为近似值
                            gross_profit = float(item.get("GROSS_PROFIT", "0"))
                            operating_margin = f"{(gross_profit / op_income * 100):.2f}"
                except (ValueError, TypeError):
                    operating_margin = ""
            
            # 确保销售净利率有值（使用NET_PROFIT_RATIO或手动计算）
            net_profit_ratio = item.get("NET_PROFIT_RATIO", "")
            if not net_profit_ratio:
                # 如果没有直接的销售净利率字段，手动计算：净利润/营业总收入
                try:
                    net_profit = float(item.get("NET_PROFIT", item.get("HOLDER_PROFIT", "0")))
                    op_income = float(operate_income)
                    if op_income != 0:
                        net_profit_ratio = net_profit / op_income * 100
                except (ValueError, TypeError):
                    net_profit_ratio = ""
            
            # 构建杜邦分析数据条目（保持与A股格式一致，使用统一的字段名）
            # 修复经营利润率字段：当值为空时不显示百分号
            operating_margin_with_percent = f"{operating_margin}%" if operating_margin else ""
            
            dupont_item = {
                "报告期": std_report_date,  # 前端使用的报告期字段
                "周期类型": period_type,  # 前端使用的周期类型字段
                "净资产收益率": format_value(item.get("ROE_AVG", item.get("ROE_AVG_SQ", ""))),
                "销售净利率": format_value(net_profit_ratio),
                "归属母公司股东的销售净利率": format_value(net_profit_ratio),  # 前端表格使用的字段名
                "总资产周转率": format_value(total_asset_turnover),
                "资产周转率(次)": format_value(total_asset_turnover),  # 前端表格使用的字段名
                "权益乘数": format_value(item.get("EQUITY_MULTIPLIER", item.get("ASSETEQUITYRATIO", ""))),
                "总资产收益率": format_value(item.get("ROA", item.get("ROA_SQ", ""))),
                "毛利率": format_value(item.get("GROSS_PROFIT_RATIO", "")),
                "营业利润率": operating_margin,
                "经营利润率": operating_margin_with_percent,  # 五因素分析所需字段
                "净利润": format_value(item.get("NET_PROFIT", item.get("NETPROFIT", ""))),
                "营业总收入": format_value(operate_income),
                "总资产": format_value(total_assets),
                "股东权益": format_value(item.get("TOTAL_PARENT_EQUITY", "")),
                "每股收益": format_value(item.get("BASIC_EPS", "")),
                "每股净资产": format_value(item.get("BVPS", "")),
                "每股经营现金流": format_value(item.get("PER_NETCASH_OPERATE", "")),
                "归母净利润（亿元）": format_yuan_to_billion(item.get("HOLDER_PROFIT", "")),
                "归属母公司股东净利润": format_yuan_to_billion(item.get("HOLDER_PROFIT", "")),  # 前端使用的归母净利润字段
                "归母净利润同比": format_value(item.get("HOLDER_PROFIT_YOY", "")),
                "归母净利润环比": format_value(item.get("HOLDER_PROFIT_QOQ", "")),
                "考虑税负因素": f"{tax_factor}%",  # 五因素分析所需字段
                "考虑利息负担": f"{interest_factor}%",  # 五因素分析所需字段
                "税负因素": format_value(tax_factor),  # 额外添加的税负因素字段
                "利息负担": format_value(interest_factor),  # 额外添加的利息负担字段
            }
            
            # 兼容原有带括号的字段名，确保向前兼容
            dupont_item["净资产收益率(%)"] = dupont_item["净资产收益率"]
            dupont_item["销售净利率(%)"] = dupont_item["销售净利率"]
            dupont_item["总资产周转率(次)"] = dupont_item["总资产周转率"]
            dupont_item["总资产收益率(%)"] = dupont_item["总资产收益率"]
            dupont_item["毛利率(%)"] = dupont_item["毛利率"]
            dupont_item["营业利润率(%)"] = dupont_item["营业利润率"]
            dupont_item["归母净利润同比(%)"] = dupont_item["归母净利润同比"]
            dupont_item["归母净利润环比(%)"] = dupont_item["归母净利润环比"]
            dupont_item["税负因素(%)"] = dupont_item["税负因素"]
            dupont_item["利息负担(%)"] = dupont_item["利息负担"]
            
            full_data.append(dupont_item)
        
        if not full_data:
            result["error"] = "未解析到有效杜邦分析数据"
            return result
        
        # 4. 按报告日期倒序排列
        full_data.sort(key=lambda x: x.get("report_date", ""), reverse=True)
        
        # 5. 设置结果
        result["full_data"] = full_data
        return result
        
    except Exception as e:
        logger.error(f"港股杜邦分析失败 [{stock_id}]: {str(e)}", exc_info=True)
        result["error"] = f"获取数据失败: {str(e)}"
        return result


def _a_dupont_analysis_impl(
    stock_id: str, 
    displaytype: str = "10",
    export_excel: bool = True  # 默认导出Excel（全量数据）
):
    """
    全量解析新浪财经股票杜邦分析页面，提取所有指标（含周期类型识别）
    包含：核心指标 + 完整拆解指标 + 周期类型（年报/中报/季报）
    """
    def parse_period_type(date_str: str) -> str:
        """从报告期日期解析周期类型"""
        try:
            month = int(date_str.split("-")[1])
            if month == 12:
                return "年报"
            elif month == 6:
                return "中报"
            elif month in [3, 9]:
                return "季报"
            else:
                return "未知周期"
        except:
            return "未知周期"

    url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vFD_DupontAnalysis/stockid/{stock_id}/displaytype/{displaytype}.phtml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://finance.sina.com.cn/"
    }
    
    result = {
        "stock_id": stock_id,  # 响应模型要求stock_id为字符串类型
        "full_data": None,  # 全量数据（含周期类型）
        "error": None
    }
    
    try:
        # 1. 发送请求并解析页面
        response_text = fetch_url(url, timeout=20, retry=3)
        if not response_text:
            result["error"] = "请求失败，未获取到数据"
            return result
        
        soup = BeautifulSoup(response_text, "html.parser")
        full_data = []
        
        # 2. 提取所有有效报告期（严格匹配YYYY-MM-DD格式）
        report_dates = []
        for a in soup.find_all("a", attrs={"name": True}):
            date_str = a.get("name", "").strip()
            if len(date_str) == 10 and date_str.count("-") == 2:
                try:
                    year, month, day = map(int, date_str.split("-"))
                    if 2010 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                        report_dates.append(date_str)
                except:
                    continue
        
        if not report_dates:
            result["error"] = "未找到有效报告期（页面无数据或结构变更）"
            return result
        
        report_dates = list(set(report_dates))  # 去重
        report_dates.sort(reverse=True)  # 按时间倒序
        
        # 3. 全量提取每个报告期的所有指标（新增周期类型）
        for date in report_dates:
            # 定位当前报告期的完整容器
            anchor = soup.find("a", attrs={"name": date})
            if not anchor:
                continue
            
            # 找到包含所有指标的.wrap容器
            wrap_div = anchor.find_next("div", class_="wrap")
            if not wrap_div:
                # 降级查找：如果找不到.wrap，查找包含.node的最近div
                wrap_div = anchor.find_next("div", string=lambda text: text and "净资产收益率" in text)
                if wrap_div:
                    wrap_div = wrap_div.find_parent("div", recursive=True)
            
            if not wrap_div:
                continue
            
            # 提取该容器下所有.node节点
            node_divs = wrap_div.find_all("div", class_=lambda c: c and "node" in c)
            period_indicators = {
                "报告期": date,
                "周期类型": parse_period_type(date)  # 新增周期类型字段
            }
            
            for node in node_divs:
                key_tags = node.find_all("p", class_=lambda c: c and "key" in c)
                value_tag = node.find("p", class_=lambda c: c and "value" in c)
                
                if not key_tags or not value_tag:
                    continue
                
                indicator_name = "".join([tag.get_text(strip=True) for tag in key_tags])
                indicator_value = value_tag.get_text(strip=True)
                
                # 修复归母净利润单位问题：将万元转换为亿元（统一与港股格式一致）
                if "归属母公司股东净利润" in indicator_name:
                    try:
                        # 移除千位分隔符
                        clean_value = indicator_value.replace(",", "")
                        # 检查是否包含"万"单位
                        if "万" in clean_value:
                            # 提取数值部分并转换为亿元（万元/10000）
                            numeric_part = clean_value.replace("万", "")
                            float_value = float(numeric_part)
                            # 转换为亿元并保留两位小数
                            converted_value = f"{float_value / 10000:.2f}"
                            period_indicators[indicator_name] = converted_value
                        else:
                            period_indicators[indicator_name] = indicator_value
                    except (ValueError, TypeError):
                        # 转换失败时保留原始值
                        period_indicators[indicator_name] = indicator_value
                else:
                    period_indicators[indicator_name] = indicator_value
            
            # 过滤无效数据（至少包含核心4个指标）
            core_keys = {"净资产收益率", "归属母公司股东的销售净利率", "资产周转率(次)", "权益乘数"}
            if all(key in period_indicators for key in core_keys):
                full_data.append(period_indicators)
        
        if not full_data:
            result["error"] = "找到报告期，但未提取到有效指标（可能页面结构变更）"
            return result
        
        result["full_data"] = full_data
        
        # 4. 导出全量数据到Excel（包含周期类型）
        if export_excel:
            df = pd.DataFrame(full_data)
            # 重新排列列：报告期、周期类型在前，核心指标次之
            core_cols = ["报告期", "周期类型", "净资产收益率", "归属母公司股东的销售净利率", "资产周转率(次)", "权益乘数"]
            other_cols = [col for col in df.columns if col not in core_cols]
            df = df[core_cols + other_cols]
            excel_filename = f"股票{stock_id}_杜邦分析全量数据.xlsx"
            df.to_excel(excel_filename, index=False, engine="openpyxl")
            print(f"\n✅ 全量数据已导出到：{excel_filename}")
        
    except requests.exceptions.Timeout:
        result["error"] = "请求超时（网络不稳定或页面响应慢）"
    except requests.exceptions.ConnectionError:
        result["error"] = "网络连接错误（请检查网络）"
    except Exception as e:
        result["error"] = f"解析失败：{str(e)}"
    
    return result
@api_error_handler
@stock_router.get("/dupont/chart", response_class=StreamingResponse)
def generate_dupont_chart(
    stock_id: str = Query(..., description="股票代码（如600000）"),
    factor_type: str = Query("all", description="指标类型：all/roe/three/five/net_profit_margin/asset_turnover/equity_multiplier"),
    cycle_type: str = Query("all", description="周期类型：all/年报/中报/季报（仅对比同周期数据）")
):
    """生成杜邦分析图表（支持周期筛选，确保同周期对比）"""
    try:
        # 1. 获取杜邦分析数据（含周期类型）
        dupont_data = dupont_analysis(stock_id, export_excel=False)
        logger.info(f"获取到的杜邦分析数据：{dupont_data}")
        if dupont_data.get("error") or not dupont_data.get("full_data"):
            raise HTTPException(status_code=404, detail=dupont_data.get("error") or "未找到杜邦分析数据")
        
        # 2. 处理数据（清洗+周期筛选）
        df = pd.DataFrame(dupont_data["full_data"])
        df.columns = df.columns.str.strip()  # 修复列名空格问题
        
        # 处理重复列名问题
        if df.columns.duplicated().any():
            # 给重复的列名添加后缀
            df = df.loc[:, ~df.columns.duplicated(keep='first')]
        
        # 只保留必要的列，避免重复键问题
        necessary_columns = [
            "报告期",
            "周期类型",
            "净资产收益率", "净资产收益率(%)",
            "销售净利率", "销售净利率(%)",
            "总资产周转率", "总资产周转率(次)", "资产周转率(次)",
            "权益乘数"
        ]
        
        # 只保留存在的必要列
        existing_columns = [col for col in necessary_columns if col in df.columns]
        df = df[existing_columns]
        
        # 数据清洗：去除空行和重复行
        df = df.dropna(subset=["报告期"])
        df = df.drop_duplicates()
        
        # 处理报告期字段，添加错误处理
        try:
            df["报告期"] = pd.to_datetime(df["报告期"])
        except ValueError as e:
            logger.warning(f"报告期转换失败：{e}")
            # 尝试另一种日期格式
            df["报告期"] = pd.to_datetime(df["报告期"], format='%Y-%m-%d', errors='coerce')
            # 去除转换失败的行
            df = df.dropna(subset=["报告期"])
        
        # 确保周期类型字段存在
        if "周期类型" not in df.columns:
            df["周期类型"] = "年报"
        else:
            # 清洗周期类型字段
            df["周期类型"] = df["周期类型"].fillna("年报")
        
        # 按周期类型筛选（仅保留同周期数据）
        if cycle_type != "all":
            df = df[df["周期类型"] == cycle_type]
            if df.empty:
                raise HTTPException(status_code=404, detail=f"无{cycle_type}数据，请更换周期类型")
        
        df = df.sort_values("报告期")  # 按时间升序排列
        
        # 确保数据中没有重复的报告期
        df = df.drop_duplicates(subset=["报告期"], keep="first")
        df = df.reset_index(drop=True)  # 重置索引

        # 3. 定义要显示的指标，支持A股和港股的不同指标名称
        indicator_map = {
            "roe": {"name": "净资产收益率", "color": "#409eff"},
            "net_profit_margin": {"name": "销售净利率(%)", "color": "#67c23a"},  # 港股默认
            "asset_turnover": {"name": "资产周转率(次)", "color": "#faad14"},
            "equity_multiplier": {"name": "权益乘数", "color": "#f5222d"},
            "interest_burden": {"name": "考虑利息负担", "color": "#8c8c8c"},
            "tax_burden": {"name": "考虑税负因素", "color": "#52c41a"}
        }
        
        # 处理指标名称差异 - 优先使用统一的字段名格式
        # 1. 处理净资产收益率字段（优先使用统一格式"净资产收益率"）
        if "净资产收益率" in df.columns:
            indicator_map["roe"]["name"] = "净资产收益率"
        elif "净资产收益率(%)" in df.columns:
            indicator_map["roe"]["name"] = "净资产收益率(%)"
        
        # 2. 处理销售净利率字段（优先使用统一格式"销售净利率"）
        if "销售净利率" in df.columns:
            indicator_map["net_profit_margin"]["name"] = "销售净利率"
        elif "销售净利率(%)" in df.columns:
            indicator_map["net_profit_margin"]["name"] = "销售净利率(%)"
        elif "归属母公司股东的销售净利率" in df.columns:
            indicator_map["net_profit_margin"]["name"] = "归属母公司股东的销售净利率"
        
        # 3. 处理总资产周转率字段（优先使用统一格式"总资产周转率"）
        if "总资产周转率" in df.columns:
            indicator_map["asset_turnover"]["name"] = "总资产周转率"
        elif "总资产周转率(次)" in df.columns:
            indicator_map["asset_turnover"]["name"] = "总资产周转率(次)"
        elif "资产周转率(次)" in df.columns:
            indicator_map["asset_turnover"]["name"] = "资产周转率(次)"
        
        # 4. 验证指标类型合法性
        valid_factor_types = ["all", "three", "five"] + list(indicator_map.keys())
        if factor_type not in valid_factor_types:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的指标类型，允许值：{valid_factor_types}"
            )

        # 5. 生成图表
        fig = go.Figure()

        # 辅助函数：添加指标曲线
        def add_trace(indicator_key):
            info = indicator_map[indicator_key]
            
            # 检查指标名称是否存在，支持A股和港股的不同指标名称
            indicator_name = info["name"]
            
            # 确保使用统一的字段名（优先使用不带括号的版本）
            uniform_name_map = {
                "净资产收益率(%)": "净资产收益率",
                "销售净利率(%)": "销售净利率",
                "总资产周转率(次)": "总资产周转率",
                "资产周转率(次)": "总资产周转率"
            }
            
            # 检查是否有统一版本的字段名
            if uniform_name_map.get(indicator_name) in df.columns:
                indicator_name = uniform_name_map[indicator_name]
            elif indicator_key == "net_profit_margin" and "销售净利率" in df.columns:
                indicator_name = "销售净利率"
            elif indicator_key == "asset_turnover" and "总资产周转率" in df.columns:
                indicator_name = "总资产周转率"
                
            if indicator_name not in df.columns:
                logger.warning(f"数据中缺少指标：{info['name']}，将跳过此指标")
                return
                
            # 获取指标数据
            # 处理指标值（去除百分号并转为数值）
            y_values = df[indicator_name]
            # 尝试转换为字符串后处理
            if y_values.dtype == 'object':
                y_values = y_values.astype(str).replace("%", "", regex=True).replace("", "NaN").astype(float)
            # 处理可能的NaN值
            y_values = pd.to_numeric(y_values, errors='coerce')
            
            # 如果所有值都是NaN，则跳过此指标
            if y_values.isna().all():
                logger.warning(f"指标：{indicator_name} 的所有值都是NaN，将跳过此指标")
                return
                
            # x轴标签：报告期+周期类型（如2023-12-31（年报））
            x_labels = [f"{d.strftime('%Y-%m-%d')}（{t}）" for d, t in zip(df["报告期"], df["周期类型"])]
            
            # 根据指标类型设置不同的悬停显示格式
            hover_format = "%{x}<br>%{y:.2f}%<extra></extra>"  # 默认带百分号
            if "周转率" in indicator_name or "权益乘数" in indicator_name:
                hover_format = "%{x}<br>%{y:.4f}<extra></extra>"  # 周转率和权益乘数不带百分号
            
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=y_values,
                mode="lines+markers",
                name=indicator_name,
                line=dict(color=info["color"], width=2),
                marker=dict(size=6),
                hovertemplate=hover_format
            ))

        # 6. 根据factor_type添加曲线
        if factor_type == "all":
            for key in indicator_map:
                add_trace(key)
            title = f"{stock_id} 杜邦分析核心指标趋势（{cycle_type if cycle_type != 'all' else '全周期'}）"
        elif factor_type == "three":
            three_factors = ["net_profit_margin", "asset_turnover", "equity_multiplier"]
            for key in three_factors:
                add_trace(key)
            title = f"{stock_id} 杜邦三因素分析趋势（{cycle_type if cycle_type != 'all' else '全周期'}）"
        elif factor_type == "five":
            five_factors = ["net_profit_margin", "asset_turnover", "equity_multiplier", "interest_burden", "tax_burden"]
            for key in five_factors:
                add_trace(key)
            title = f"{stock_id} 杜邦五因素分析趋势（{cycle_type if cycle_type != 'all' else '全周期'}）"
        else:
            add_trace(factor_type)
            title = f"{stock_id} {indicator_map[factor_type]['name']}趋势（{cycle_type if cycle_type != 'all' else '全周期'}）"

        # 7. 美化图表布局
        fig.update_layout(
            title=dict(text=title, font=dict(size=16, color="#333"), x=0.5, xanchor="center"),
            xaxis=dict(
                title="报告期（周期类型）", 
                showgrid=True, 
                gridcolor="#f0f0f0", 
                tickangle=45,
                tickfont=dict(size=10)  # 缩小x轴标签字体，避免重叠
            ),
            yaxis=dict(
                title="指标值（%）", 
                showgrid=True, 
                gridcolor="#f0f0f0"
            ),
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="right", 
                x=1
            ),
            margin=dict(l=40, r=40, t=60, b=120),  # 增加底部边距，避免x轴标签被截断
            hovermode="x unified",
            plot_bgcolor="white"
        )

        # 8. 保存图表并返回
        buf = BytesIO()
        fig.write_image(buf, format="png", width=1200, height=700, scale=1.5, engine="kaleido")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成图表失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成图表失败：{str(e)}")


# -------------- 股票基础信息接口 --------------
@api_error_handler
@stock_router.get("/baseInfo/{stockCode}")
def get_stock_base_info(stockCode: str):
    """获取股票基础信息"""
    logger.info(f"请求股票基础信息：{stockCode}")
    
    if not stockCode.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是数字")
    
    market = get_stock_market(stockCode)
    if not market:
        raise HTTPException(status_code=400, detail="不支持的股票代码")
    
    # 构造接口URL
    random_num = int(time.time() * 1000)
    
    if market == "rt_hk":
        # 港股URL格式
        sina_list = f"rt_hk{stockCode}"
        sina_url = f"https://hq.sinajs.cn/?_={random_num}&list={sina_list}"
    else:
        # A股URL格式
        sina_list = f"{market}{stockCode},{market}{stockCode}_i"
        sina_url = f"https://hq.sinajs.cn/rn={random_num}&list={sina_list}"
    
    try:
        hq_data = fetch_url(sina_url, is_sina_var=True, retry=3)
        if not hq_data:
            raise Exception("新浪接口返回空数据")
        
        parsed_data = parse_sina_hq(hq_data)
        stock_key = f"{market}{stockCode}"
        
        if market == "rt_hk":
            # 港股数据处理
            core_data = parsed_data.get(stock_key, [])
            if not core_data:
                # 如果返回空数据，说明新浪接口不支持该港股
                raise HTTPException(status_code=404, detail=f"新浪接口不支持该港股：{stockCode}")
            if len(core_data) < 10:
                raise Exception("港股核心字段不足")
            
            # 解析港股核心行情
            core_quotes = {
                "stockName": core_data[0],
                "currentPrice": format_field(core_data[1], lambda x: float(x) if x else 0.0),
                "openPrice": format_field(core_data[2], lambda x: float(x) if x else 0.0),
                "preClosePrice": format_field(core_data[3], lambda x: float(x) if x else 0.0),
                "highPrice": format_field(core_data[4], lambda x: float(x) if x else 0.0),
                "lowPrice": format_field(core_data[5], lambda x: float(x) if x else 0.0),
                "volume": format_field(core_data[6], lambda x: int(x) if x else 0),
                "turnover": format_field(core_data[7], lambda x: float(x) if x else 0.0),
                "amplitude": "",
                "pe": "",
                "pb": "",
                "changePercent": format_field(core_data[8], lambda x: float(x) if x else 0.0),
                "changeAmount": format_field(core_data[9], lambda x: float(x) if x else 0.0)
            }
            
            return {
                "baseInfo": {
                    "stockCode": stockCode,
                    "market": "港股通",
                    "stockName": core_quotes["stockName"],
                    "industry": ""
                },
                "coreQuotes": core_quotes,
                "supplementInfo": {},
                "dataValidity": {
                    "isValid": core_quotes["currentPrice"] >= 0 and core_quotes["stockName"] != "",
                    "reason": "" if (core_quotes["currentPrice"] >= 0 and core_quotes["stockName"] != "") else "股票数据无效"
                }
            }
        else:
            # A股数据处理
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
                    "market": "沪A" if market == "sh" else "深A" if market == "sz" else "北A",
                    "stockName": core_quotes["stockName"],
                    "industry": supplement_info["industry"]
                },
                "coreQuotes": core_quotes,
                "supplementInfo": supplement_info,
                "dataValidity": {
                    "isValid": core_quotes["currentPrice"] >= 0 and core_quotes["stockName"] != "未知名称",
                    "reason": "" if (core_quotes["currentPrice"] >= 0 and core_quotes["stockName"] != "未知名称") 
                              else "股票数据无效"
                }
            }
    
    except HTTPException:
        # 如果是HTTPException，直接重新抛出
        raise
    except Exception as e:
        logger.error(f"接口请求失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取股票信息失败")

# -------------- 股票搜索接口 --------------
@api_error_handler
@stock_router.get("/search/{keyword}")
def search_stocks(keyword: str):
    """搜索股票（使用新浪新接口，支持港股通）"""
    if not keyword.strip():
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")
    
    try:
        encoded_keyword = quote(keyword.strip(), encoding='utf-8')
        # 生成随机数作为name参数
        timestamp = str(int(time.time() * 1000))
        search_url = f"https://suggest3.sinajs.cn/suggest/type=&key={encoded_keyword}&name=suggestdata_{timestamp}"
        logger.info(f"请求搜索接口：{search_url}")
        
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/",
            "Accept": "text/javascript, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        # 解析响应内容
        response_text = fetch_url(search_url, timeout=20, retry=3)
        logger.info(f"接口返回内容长度：{len(response_text)} 字符")
        logger.debug(f"返回内容：{response_text}")
        
        stock_list = []
        seen_codes = set()
        
        # 提取JavaScript变量中的股票数据
        match = re.search(r'var\s+suggestdata_\d+\s*=\s*"([^"]+)"', response_text)
        if not match:
            logger.warning("未找到股票数据")
            return {"stocks": [], "message": "未找到股票数据"}
        
        stock_data_str = match.group(1)
        logger.info(f"提取到股票数据字符串：{stock_data_str[:100]}...")
        
        # 分割股票数据
        stock_items = stock_data_str.split(';')
        logger.info(f"解析到 {len(stock_items)} 个股票项")
        
        for item in stock_items:
            if not item:
                continue
            
            fields = item.split(',')
            if len(fields) < 4:
                logger.warning(f"股票数据字段不足：{item}")
                continue
            
            stock_name = fields[0]
            stock_type = fields[1]
            stock_code = fields[2]
            full_code = fields[3]
            
            # 过滤无效数据
            if len(stock_name) < 2 or stock_code in seen_codes:
                logger.info(f"无效数据（重复/名称过短）：{stock_code} | {stock_name}")
                continue
            
            # 确定市场
            market = ""
            if stock_type == "31":
                # 31代表港股通
                market = "港股通"
            elif stock_type == "11":
                # 11代表A股
                if full_code.startswith("sz"):
                    market = "深A"
                elif full_code.startswith("sh"):
                    market = "沪A"
                elif full_code.startswith("bj"):
                    market = "北A"
                else:
                    # 根据股票代码前缀判断
                    if stock_code.startswith(("60", "68")):
                        market = "沪A"
                    elif stock_code.startswith(("00", "30")):
                        market = "深A"
                    elif stock_code.startswith("8"):
                        market = "北A"
                    else:
                        logger.warning(f"无法确定A股市场：{stock_code}")
                        continue
            else:
                logger.info(f"跳过未知类型股票：{stock_code} | {stock_name} (type: {stock_type})")
                continue
            
            seen_codes.add(stock_code)
            stock_list.append({
                "stockCode": stock_code,
                "stockName": stock_name,
                "market": market
            })
            logger.info(f"✅ 解析成功：{stock_code} | {stock_name} | {market}")
        
        # 排序
        stock_list.sort(key=lambda x: x["stockCode"])
        logger.info(f"解析完成，共得到 {len(stock_list)} 支有效个股（去重后）")
        
        # 无结果时返回友好提示
        if not stock_list:
            return {"stocks": [], "message": f"未找到包含'{keyword}'的股票，请尝试其他关键词"}
        
        return {"stocks": stock_list[:50]}
    
    except requests.exceptions.SSLError:
        logger.error("SSL证书验证失败")
        raise HTTPException(status_code=500, detail="SSL证书验证失败，请检查网络环境")
    except requests.exceptions.RequestException as e:
        logger.error(f"接口请求失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"股票搜索接口请求失败：{str(e)}")
    except Exception as e:
        logger.error(f"股票搜索解析失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"股票搜索失败：{str(e)}")

# -------------- 股票详情接口 --------------
@api_error_handler
@stock_router.get("/{stock_code}/detail", response_model=StockDetailResponse)
def get_stock_detail(stock_code: str):
    """获取股票详情（基础信息+行情+财务+股东）- 已集成指定财务接口"""
    logger.info(f"请求股票详情: {stock_code}")
    
    # 校验股票代码
    if not stock_code.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是数字")
    
    market = get_stock_market(stock_code)
    if not market:
        raise HTTPException(status_code=400, detail="仅支持沪深A（60/00/30开头）和港股（5位数字）")
    
    try:
        # 1. 获取基础行情数据
        base_info_data = get_stock_quotes(stock_code)
        if not base_info_data or not base_info_data["dataValidity"]["isValid"]:
            raise HTTPException(status_code=500, detail="股票基础数据无效")
        
        # 2. 获取财务数据（使用统一接口）
        financial_data = get_stock_financial_data(stock_code)
        
        # 3. 构造基础信息（使用实际可用的数据）
        base_info = {
            **base_info_data["baseInfo"],
            "companyName": base_info_data['baseInfo']['stockName'] or '未知公司',
            "listDate": "--",  # 实际数据接口暂不提供，显示占位符
            "totalShares": "--",  # 默认占位符
            "floatShares": "--",  # 默认占位符
            "marketCap": "--"    # 默认占位符
        }
        
        # 新浪港股接口没有直接提供总市值字段，保持默认值
        
        # 4. 如果有腾讯财经数据，替换占位符
        if "tencentData" in base_info_data and base_info_data["tencentData"]:
            tencent_data = base_info_data["tencentData"]
            
            # 替换市值（单位：元）
            if tencent_data["marketCap"] > 0:
                # 转换为亿元显示，保留两位小数
                base_info["marketCap"] = f"{tencent_data['marketCap'] / 100000000:.2f}亿元"
            
            # 替换总股本和流通股（单位：股）
            if tencent_data["totalShares"] > 0:
                # 转换为亿股显示，保留两位小数
                base_info["totalShares"] = f"{tencent_data['totalShares'] / 100000000:.2f}亿股"
            
            if tencent_data["floatShares"] > 0:
                # 转换为亿股显示，保留两位小数
                base_info["floatShares"] = f"{tencent_data['floatShares'] / 100000000:.2f}亿股"
            
            # 在coreQuotes中添加腾讯财经数据
            if tencent_data["peDynamic"] >= 0:
                base_info_data["coreQuotes"]["peDynamic"] = tencent_data["peDynamic"]
            
            if tencent_data["peStatic"] >= 0:
                base_info_data["coreQuotes"]["peStatic"] = tencent_data["peStatic"]
            
            # 添加市净率和涨跌幅
            if tencent_data["pbRatio"] >= 0:
                base_info_data["coreQuotes"]["pbRatio"] = tencent_data["pbRatio"]
            
            if tencent_data["changeRate"] >= 0:
                base_info_data["coreQuotes"]["changeRate"] = tencent_data["changeRate"]
        
        # 5. 对于港股，使用东方财富API获取详细数据
        if len(stock_code) == 5:  # 港股是5位数字代码
            try:
                hk_detail_data = get_hk_stock_detail_from_eastmoney(stock_code)
                
                # 填充总市值、股本、市盈率等数据到base_info
                if hk_detail_data:
                        # 总市值（单位：元 -> 亿元）
                        if "total_market_cap" in hk_detail_data and hk_detail_data["total_market_cap"] > 0:
                            base_info["marketCap"] = f"{hk_detail_data['total_market_cap'] / 100000000:.2f}亿元"
                        
                        # 总股本（单位：股 -> 亿股）
                        if "issued_common_shares" in hk_detail_data and hk_detail_data["issued_common_shares"] > 0:
                            base_info["totalShares"] = f"{hk_detail_data['issued_common_shares'] / 100000000:.2f}亿股"
                        
                        # 流通股本（单位：股 -> 亿股）
                        if "hk_common_shares" in hk_detail_data and hk_detail_data["hk_common_shares"] > 0:
                            base_info["floatShares"] = f"{hk_detail_data['hk_common_shares'] / 100000000:.2f}亿股"
                        
                        # 在coreQuotes中添加东方财富港股数据
                        if "pe_ttm" in hk_detail_data and hk_detail_data["pe_ttm"] > 0:
                            base_info_data["coreQuotes"]["peDynamic"] = hk_detail_data["pe_ttm"]
                        
                        if "pe_ttm" in hk_detail_data and hk_detail_data["pe_ttm"] > 0:
                            base_info_data["coreQuotes"]["peStatic"] = hk_detail_data["pe_ttm"]
                        
                        if "pb_ttm" in hk_detail_data and hk_detail_data["pb_ttm"] > 0:
                            base_info_data["coreQuotes"]["pbRatio"] = hk_detail_data["pb_ttm"]
                        
                        # 添加净资产收益率和其他财务数据到coreQuotes
                        if "roe_avg" in hk_detail_data:
                            base_info_data["coreQuotes"]["roe"] = hk_detail_data["roe_avg"]
                        
                        if "net_profit_ratio" in hk_detail_data:
                            base_info_data["coreQuotes"]["netProfitRatio"] = hk_detail_data["net_profit_ratio"]
                        
                        if "dividend_rate" in hk_detail_data:
                            base_info_data["coreQuotes"]["dividendRate"] = hk_detail_data["dividend_rate"]
                        
                        # 添加最新营收和归母净利润到base_info
                        if "operate_income" in hk_detail_data and hk_detail_data["operate_income"] != 0:
                            # 检查数据大小，判断单位是否已经是亿元
                            if hk_detail_data["operate_income"] > 100000000:  # 如果大于1亿元（以元为单位）
                                base_info["operateIncome"] = f"{hk_detail_data['operate_income'] / 100000000:.2f}亿元"
                            else:  # 已经是亿元单位
                                base_info["operateIncome"] = f"{hk_detail_data['operate_income']:.2f}亿元"
                        
                        if "holder_profit" in hk_detail_data and hk_detail_data["holder_profit"] != 0:
                            # 检查数据大小，判断单位是否已经是亿元
                            if hk_detail_data["holder_profit"] > 100000000:  # 如果大于1亿元（以元为单位）
                                base_info["holderProfit"] = f"{hk_detail_data['holder_profit'] / 100000000:.2f}亿元"
                            else:  # 已经是亿元单位
                                base_info["holderProfit"] = f"{hk_detail_data['holder_profit']:.2f}亿元"
            except Exception as e:
                logger.error(f"获取东方财富港股详情失败: {str(e)}", exc_info=True)
                # 失败时不影响原有数据
        
        
        # 处理财务数据，将mllsj从financialData中分离出来，避免模型验证错误
        processed_financial_data = {}
        mllsj_data = {}
        
        for key, value in financial_data.items():
            if key == "mllsj":
                # 保存mllsj数据
                mllsj_data = value
            else:
                # 只保留符合StockFinancialData模型的数据（年份数据）
                processed_financial_data[key] = value
        
        return {
            "baseInfo": base_info,
            "coreQuotes": base_info_data["coreQuotes"],
            "tencentData": base_info_data.get("tencentData", {}),  # 包含完整的腾讯财经数据
            "financialData": processed_financial_data,  # 这里返回的是符合模型要求的财务数据
            "mllsj": mllsj_data,  # 将mllsj作为单独字段返回
            "topShareholders": [],  # 已移除十大股东数据
            "dataValidity": {
                "isValid": True,
                "reason": ""
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票详情失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="股票详情数据获取失败")

# -------------- 股票CRUD接口 --------------
@api_error_handler
@stock_router.post("/add", response_model=StockItem)
def add_stock(stock: StockCreate):
    """添加股票到清单"""
    try:
        # 检查是否已存在
        stocks = db.get_all_stocks()
        if any(item["stockCode"] == stock.stockCode for item in stocks):
            raise HTTPException(status_code=400, detail=f"股票代码 {stock.stockCode} 已存在")
        
        new_stock = {
            "id": str(datetime.now().timestamp()).replace('.', '')[-10:],
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
        logger.error(f"添加股票异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"添加股票失败: {str(e)}")

@api_error_handler
@stock_router.put("/{stock_id}", response_model=StockItem)
def update_stock(stock_id: str, update_data: StockUpdate):
    """更新股票信息"""
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
    
    # 清除该股票的行情缓存
    stock_quote_cache.clear(updated_stock["stockCode"])
    
    logger.info(f"成功更新股票: {updated_stock['stockCode']} 持仓状态={updated_stock['isHold']}")
    return updated_stock

@api_error_handler
@stock_router.delete("/{stock_id}")
def delete_stock(stock_id: str):
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

# -------------- 估值逻辑API --------------
@api_error_handler
@stock_router.get("/valuation/{stock_code}", response_model=Optional[ValuationLogicItem])
def get_stock_valuation(stock_code: str):
    """获取特定股票的估值逻辑数据"""
    try:
        valuation_data = db.get_valuation_by_stock_code(stock_code)
        return valuation_data
    except Exception as e:
        logger.error(f"获取估值逻辑数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取估值逻辑数据失败")

@api_error_handler
@stock_router.post("/valuation", response_model=ValuationLogicItem)
def save_stock_valuation(valuation: ValuationLogicItem):
    """保存或更新股票估值逻辑数据"""
    try:
        # 检查是否已存在
        existing_valuation = db.get_valuation_by_stock_code(valuation.stockCode)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if existing_valuation:
            # 更新现有记录
            update_data = {
                "stockName": valuation.stockName,
                "valuationContent": valuation.valuationContent,
                "investmentForecast": valuation.investmentForecast or "",
                "tradingPlan": valuation.tradingPlan or ""
            }
            updated_valuation = db.update_valuation(existing_valuation["id"], update_data)
            if not updated_valuation:
                raise HTTPException(status_code=500, detail="更新估值逻辑数据失败")
            logger.info(f"成功更新股票估值逻辑: {valuation.stockCode}")
            return updated_valuation
        else:
            # 创建新记录
            new_valuation = {
                "id": str(datetime.now().timestamp()).replace('.', '')[-10:],
                "stockCode": valuation.stockCode,
                "stockName": valuation.stockName,
                "valuationContent": valuation.valuationContent,
                "investmentForecast": valuation.investmentForecast or "",
                "tradingPlan": valuation.tradingPlan or "",
                "createTime": current_time,
                "updateTime": current_time
            }
            saved_valuation = db.create_valuation(new_valuation)
            logger.info(f"成功创建股票估值逻辑: {valuation.stockCode}")
            return saved_valuation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存估值逻辑数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="保存估值逻辑数据失败")


def get_stock_financial_data(stock_code: str) -> Dict[str, Dict[str, str]]:
    """统一财务数据获取接口，根据股票代码判断是港股还是A股
    - stock_code: 股票代码
    - 返回: 包含财务数据的字典，格式与util.py的get_stock_financial_data一致
    """
    logger.info(f"获取股票{stock_code}金融数据")
    
    # 判断股票市场
    market = get_stock_market(stock_code)
    
    # 如果是港股（market为rt_hk），调用港股财务数据获取函数
    if market == "rt_hk":
        return _get_hk_stock_financial_data(stock_code)
    # 否则调用util.py中的A股财务数据获取函数
    else:
        from util import DataSource
        return DataSource.get_stock_financial_data(stock_code)


def _get_hk_stock_financial_data(stock_code: str) -> Dict[str, Dict[str, str]]:
    """获取港股金融数据，使用东方财富网API
    返回值与util.py的get_stock_financial_data格式一致
    """
    logger.info(f"获取港股{stock_code}金融数据")
    
    # 校验股票代码
    if not stock_code.isdigit():
        logger.warning(f"股票代码格式错误: {stock_code}（必须是纯数字）")
        return {}
    
    # 构造东方财富网港股财务数据API URL
    secucode = f"{stock_code}.HK"
    api_url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_HKF10_FN_MAININDICATOR&columns=ALL&quoteColumns=&filter=(SECUCODE%3D%22{secucode}%22)&pageNumber=1&pageSize=9&sortTypes=-1&sortColumns=STD_REPORT_DATE&source=F10&client=PC&v=040146104118736425"
    
    try:
        # 获取财务数据
        response_data = fetch_url(api_url, retry=3, timeout=20)
        if not response_data or "result" not in response_data:
            logger.error(f"东方财富网API返回空数据或格式错误: {stock_code}")
            financial_data = {}
            latest_year = "2022"
            financial_data[latest_year] = {
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
            return financial_data
        
        # 获取最新的财务数据（按报告日期降序排列，第一条为最新）
        financial_records = response_data.get("result", {}).get("data", [])
        if not financial_records:
            logger.error(f"未找到港股{stock_code}财务数据")
            financial_data = {}
            latest_year = "2022"
            financial_data[latest_year] = {
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
            return financial_data
        
        # 设置返回数据结构
        financial_data = {}
        mllsj_data = {}
        
        # 处理所有财务记录（按报告日期降序排列）
        for record in financial_records:
            # 提取报告日期和年份
            report_date = record.get("REPORT_DATE", "")
            if not report_date:
                continue
            
            year = report_date[:4]
            
            # 将数值转换为字符串并保留两位小数的辅助函数
            def format_value(value, default="0.00", convert_to_billion=False):
                if value is None or value == "":
                    return default
                try:
                    # 尝试转换为浮点数
                    float_value = float(value)
                    
                    # 如果需要转换为亿元，除以100000000
                    if convert_to_billion:
                        float_value = float_value / 100000000
                        
                    # 保留两位小数并转换为字符串
                    return f"{float_value:.2f}"
                except (ValueError, TypeError):
                    # 如果转换失败，返回默认值
                    return default
            
            # 构建财务指标字典
            indicators = {
                "revenue": format_value(record.get("OPERATE_INCOME"), convert_to_billion=True),
                "revenueGrowth": format_value(record.get("OPERATE_INCOME_YOY")),
                "netProfit": format_value(record.get("HOLDER_PROFIT"), convert_to_billion=True),
                "netProfitGrowth": format_value(record.get("HOLDER_PROFIT_YOY")),
                "eps": format_value(record.get("BASIC_EPS")),
                "navps": format_value(record.get("BPS")),
                "roe": format_value(record.get("ROE_AVG")),
                "pe": format_value(record.get("PE_TTM")),
                "pb": format_value(record.get("PB_TTM")),
                "grossMargin": format_value(record.get("GROSS_PROFIT_RATIO")),
                "netMargin": format_value(record.get("NET_PROFIT_RATIO")),
                "debtRatio": format_value(record.get("DEBT_ASSET_RATIO")),
                # 添加前端需要的字段，转换为亿元
                "totalRevenue": format_value(record.get("OPERATE_INCOME"), convert_to_billion=True),
                "netProfitAttribution": format_value(record.get("HOLDER_PROFIT"), convert_to_billion=True)
            }
            
            # 只有在当前年份没有数据或者该记录是年报时才添加到年度数据中
            # 优先使用年报数据
            if year not in financial_data or record.get("DATE_TYPE_CODE") == "001":
                financial_data[year] = indicators
            
            # 添加毛利率和净利率数据（所有报告期）
            mllsj_data[report_date] = {
                "mll": indicators["grossMargin"],
                "xsjll": indicators["netMargin"]
            }
        
        # 确保至少有一年的数据
        if not financial_data:
            financial_data = {
                "2022": {
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
            }
        
        # 添加毛利率和净利率数据（包含所有季度）
        financial_data['mllsj'] = mllsj_data
        
        logger.info(f"港股{stock_code}金融数据获取成功")
        return financial_data
    
    except Exception as e:
        logger.error(f"港股{stock_code}金融数据获取失败: {str(e)}", exc_info=True)
        # 返回默认数据结构
        financial_data = {
            "2022": {
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
            },
            "mllsj": {
                "2022-12-31": {
                    "mll": "0.0",
                    "xsjll": "0.0"
                }
            }
        }
        return financial_data

