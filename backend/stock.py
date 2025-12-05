import chardet
from urllib.parse import quote
import requests
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import Optional, List, Dict, Union, Any
import random
import logging
import db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from util import (
    get_stock_market, parse_sina_hq, format_field, fetch_url,
    cache_with_timeout, get_last_trade_date, sync_cache_with_timeout,
    CORE_QUOTES_FIELDS, SUPPLEMENT_FIELDS, DataSource, stock_quote_cache
)
from bs4 import BeautifulSoup
import re
import time

logger = logging.getLogger(__name__)

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
def get_stock_quotes(stock_code: str) -> Optional[Dict[str, Any]]:
    """获取股票实时行情（同步版本，修复核心问题）"""
    logger.info(f"同步请求股票行情: {stock_code}")
    
    # 校验股票代码
    if len(stock_code) != 6 or not stock_code.isdigit():
        logger.warning(f"股票代码格式错误: {stock_code}")
        return None
    
    market = get_stock_market(stock_code)
    if not market:
        logger.warning(f"不支持的市场: {stock_code}（仅支持沪深A：60/00/30开头）")
        return None
    
    # 构造接口URL（优化URL参数，增加随机数避免缓存）
    random_num = int(time.time() * 1000)
    sina_list = f"{market}{stock_code},{market}{stock_code}_i"
    sina_url = f"https://hq.sinajs.cn/rn={random_num}&list={sina_list}"
    
    try:
        # 增加重试机制，确保接口访问成功
        hq_data = fetch_url(sina_url, is_sina_var=True, retry=3)
        if not hq_data:
            logger.error(f"新浪接口返回空数据: {stock_code}")
            return None
        
        # 解析行情数据
        parsed_data = parse_sina_hq(hq_data)
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
        
        # 解析核心行情（优化字段格式化）
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
                "market": "沪A" if market == "sh" else "深A",
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
@market_router.get("/overview", response_model=MarketOverview)
def get_market_overview():
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

# -------------- 股票清单接口（核心修复）--------------
@stock_router.get("", response_model=List[StockItem])
def get_all_stocks(search: Optional[str] = Query(None)):
    """获取股票清单（支持搜索，修复价格和涨跌幅为0的问题）"""
    stocks_to_process = db.get_all_stocks(search=search)
    result_stocks = []
    
    logger.info(f"获取股票清单，搜索条件：{search}，共{len(stocks_to_process)}支股票")
    
    for stock in stocks_to_process:
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
        
        result_stocks.append(stock_with_quotes)
    
    logger.info(f"股票清单获取完成，返回{len(result_stocks)}支数据")
    return result_stocks

# -------------- 单只股票接口（修复）--------------
@stock_router.get("/{stock_id}", response_model=StockItem)
def get_stock(stock_id: str):
    """获取单只股票"""
    stock = db.get_stock_by_id(stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 添加行情数据
    try:
        quote_data = get_stock_quotes(stock["stockCode"])
        if quote_data and "coreQuotes" in quote_data:
            core_quotes = quote_data["coreQuotes"]
            current_price = core_quotes.get("currentPrice", 0.0)
            prev_close = core_quotes.get("prevClosePrice", 0.0)
            
            # 计算涨跌幅
            if prev_close > 0.01 and current_price >= 0:
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
            logger.warning(f"股票{stock['stockCode']}无有效行情数据")
            stock["currentPrice"] = 0.0
            stock["changeAmount"] = 0.0
            stock["changeRate"] = 0.0
            stock["updateTime"] = ""
    except Exception as e:
        logger.error(f"获取股票{stock['stockCode']}行情失败: {str(e)}", exc_info=True)
        stock["currentPrice"] = 0.0
        stock["changeAmount"] = 0.0
        stock["changeRate"] = 0.0
        stock["updateTime"] = ""
    
    return stock

# -------------- 股票行情接口 --------------
@stock_router.get("/{stock_code}/quotes", response_model=StockQuoteResponse)
def get_stock_quotes_api(stock_code: str):
    """获取股票实时行情（API接口）"""
    data = get_stock_quotes(stock_code)
    if not data:
        raise HTTPException(status_code=500, detail="行情数据获取失败")
    return data



# ------------------- 杜邦分析数据提取 -------------------
@stock_router.get("/dubang/{stock_id}", response_model=DupontAnalysisResponse)
def sina_dupont_analysis(
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
        response = requests.get(url, headers=headers, timeout=20, verify=False)
        response.encoding = "gb2312"
        if response.status_code != 200:
            result["error"] = f"请求失败，状态码：{response.status_code}"
            return result
        
        soup = BeautifulSoup(response.text, "html.parser")
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
@stock_router.get("/dupont/chart", response_class=StreamingResponse)
def generate_dupont_chart(
    stock_id: str = Query(..., description="股票代码（如600000）"),
    factor_type: str = Query("all", description="指标类型：all/roe/three/five/net_profit_margin/asset_turnover/equity_multiplier"),
    cycle_type: str = Query("all", description="周期类型：all/年报/中报/季报（仅对比同周期数据）")
):
    """生成杜邦分析图表（支持周期筛选，确保同周期对比）"""
    try:
        # 1. 获取杜邦分析数据（含周期类型）
        dupont_data = sina_dupont_analysis(stock_id, export_excel=False)
        logger.info(f"获取到的杜邦分析数据：{dupont_data}")
        if dupont_data.get("error") or not dupont_data.get("full_data"):
            raise HTTPException(status_code=404, detail=dupont_data.get("error") or "未找到杜邦分析数据")
        
        # 2. 处理数据（清洗+周期筛选）
        df = pd.DataFrame(dupont_data["full_data"])
        df.columns = df.columns.str.strip()  # 修复列名空格问题
        df["报告期"] = pd.to_datetime(df["报告期"])  # 转为日期格式
        
        # 按周期类型筛选（仅保留同周期数据）
        if cycle_type != "all":
            df = df[df["周期类型"] == cycle_type]
            if df.empty:
                raise HTTPException(status_code=404, detail=f"无{cycle_type}数据，请更换周期类型")
        
        df = df.sort_values("报告期")  # 按时间升序排列

        # 3. 定义要显示的指标
        indicator_map = {
            "roe": {"name": "净资产收益率", "color": "#409eff"},
            "net_profit_margin": {"name": "归属母公司股东的销售净利率", "color": "#67c23a"},
            "asset_turnover": {"name": "资产周转率(次)", "color": "#faad14"},
            "equity_multiplier": {"name": "权益乘数", "color": "#f5222d"},
            "interest_burden": {"name": "考虑利息负担", "color": "#8c8c8c"},
            "tax_burden": {"name": "考虑税负因素", "color": "#52c41a"}
        }
        
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
            if info["name"] not in df.columns:
                raise HTTPException(
                    status_code=404, 
                    detail=f"数据中缺少指标：{info['name']}（可能页面结构变更）"
                )
            # 处理指标值（去除百分号并转为数值）
            y_values = df[info["name"]].replace("%", "", regex=True).astype(float)
            # x轴标签：报告期+周期类型（如2023-12-31（年报））
            x_labels = [f"{d.strftime('%Y-%m-%d')}（{t}）" for d, t in zip(df["报告期"], df["周期类型"])]
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=y_values,
                mode="lines+markers",
                name=info["name"],
                line=dict(color=info["color"], width=2),
                marker=dict(size=6),
                hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>"  # 悬停显示周期和数值
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
@stock_router.get("/baseInfo/{stockCode}")
def get_stock_base_info(stockCode: str):
    """获取股票基础信息"""
    logger.info(f"请求股票基础信息：{stockCode}")
    
    if len(stockCode) != 6 or not stockCode.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是6位数字")
    
    market = get_stock_market(stockCode)
    if not market:
        raise HTTPException(status_code=400, detail="仅支持沪深A（60/00/30/68开头）")
    
    sina_list = f"{market}{stockCode},{market}{stockCode}_i"
    sina_url = f"https://hq.sinajs.cn/rn={int(time.time()*1000)}&list={sina_list}"
    
    try:
        hq_data = fetch_url(sina_url, is_sina_var=True, retry=3)
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
                "isValid": core_quotes["currentPrice"] >= 0 and core_quotes["stockName"] != "未知名称",
                "reason": "" if (core_quotes["currentPrice"] >= 0 and core_quotes["stockName"] != "未知名称") 
                          else "股票数据无效"
            }
        }
    
    except Exception as e:
        logger.error(f"接口请求失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取股票信息失败")

# -------------- 股票搜索接口 --------------
@stock_router.get("/search/{keyword}")
def search_stocks(keyword: str):
    """搜索股票（基于你的原有逻辑，修复SSL/编码/拦截问题）"""
    if not keyword.strip():
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")
    
    try:
        encoded_keyword = quote(keyword.strip(), encoding='utf-8')
        search_url = f"https://biz.finance.sina.com.cn/suggest/lookup_n.php?country=stock&q={encoded_keyword}"
        logger.info(f"请求搜索接口：{search_url}")
        
        # 核心修复1：增强请求头，避免被新浪拦截（原有头信息太简单）
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",  # 支持压缩，避免编码异常
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",  # 禁用缓存，获取最新数据
            "Pragma": "no-cache"
        }
        
        # 核心修复2：关闭SSL验证（新浪这个接口的SSL证书可能有问题）
        # 增加超时时间到20秒，避免网络波动超时
        response = requests.get(
            search_url, 
            headers=headers, 
            timeout=20,
            verify=False  # 关键：关闭SSL证书验证，解决请求失败
        )
        response.raise_for_status()
        
        # 核心修复3：智能编码处理（原有固定gb2312导致乱码）
        # 先尝试gb2312，失败则用chardet自动识别
        try:
            response.encoding = "gb2312"
            response_text = response.text
            # 验证编码是否正确（如果包含大量�，说明编码错误）
            if "�" in response_text:
                raise ValueError("gb2312编码失败，自动识别")
        except:
            # 自动识别编码
            detected_encoding = chardet.detect(response.content)["encoding"] or "utf-8"
            logger.info(f"自动识别编码：{detected_encoding}")
            response.encoding = detected_encoding
            response_text = response.content.decode(detected_encoding, errors="replace")
        
        logger.info(f"接口返回HTML长度：{len(response_text)} 字符")
        logger.debug(f"HTML前500字符：{response_text[:500]}")  # 查看实际返回内容，确认是否有数据
        
        soup = BeautifulSoup(response_text, "html.parser")
        stock_list = []
        seen_codes = set()
        
        # 保持你的原有定位逻辑（不变）
        stock_market_div = soup.find("div", id="stock_stock")
        if not stock_market_div:
            logger.warning("未找到沪深个股板块，返回空结果")
            return {"stocks": [], "message": "未找到沪深个股板块"}
        
        stock_list_div = stock_market_div.find_next_sibling("div", class_="list")
        if not stock_list_div:
            logger.warning("未找到股票列表容器，返回空结果")
            return {"stocks": [], "message": "未找到股票列表容器"}
        logger.info("找到股票列表容器，开始解析")
        
        # 保持你的原有提取逻辑（不变）
        stock_links = stock_list_div.find_all("a")
        logger.info(f"从容器中提取到 {len(stock_links)} 个股票链接")
        
        # 保持你的超级宽松正则（不变）
        stock_pattern = re.compile(
            r"(sz|sh)(\d{6})[\s\u3000]+(.+)",
            re.IGNORECASE
        )
        
        # 优化你的手动分割逻辑，避免索引错误
        for idx, link in enumerate(stock_links):
            link_text = link.get_text(strip=True)
            logger.info(f"第{idx+1}个链接文本：{repr(link_text)}")  # 改为info级别，让你直接看到
            
            if not link_text:
                logger.info("跳过空文本链接")
                continue
            
            match = stock_pattern.search(link_text)
            if not match:
                logger.info(f"正则未匹配到：{repr(link_text)}，尝试手动分割")
                # 修复手动分割逻辑：避免split后索引错误
                code_match = re.search(r"\d{6}", link_text)
                if code_match:
                    stock_code = code_match.group()
                    # 优化市场前缀判断：更健壮
                    link_text_lower = link_text.lower()
                    if "sz" in link_text_lower:
                        market_prefix = "sz"
                    elif "sh" in link_text_lower:
                        market_prefix = "sh"
                    else:
                        # 兜底：根据股票代码前缀判断市场
                        if stock_code.startswith("60"):
                            market_prefix = "sh"
                        elif stock_code.startswith(("00", "30")):
                            market_prefix = "sz"
                        else:
                            logger.info(f"未找到市场前缀且代码不合法，跳过：{link_text}")
                            continue
                    # 修复名称提取：避免split后无元素
                    parts = link_text.split(stock_code)
                    stock_name = parts[-1].strip() if len(parts) > 1 else ""
                    # 名称为空时，从parts[0]提取
                    if not stock_name and len(parts) > 0:
                        stock_name = parts[0].replace("sz", "").replace("sh", "").replace("SZ", "").replace("SH", "").strip()
                    if not stock_name:
                        logger.info(f"手动分割未提取到名称，跳过：{link_text}")
                        continue
                    logger.info(f"手动分割成功：{market_prefix} | {stock_code} | {stock_name}")
                else:
                    logger.info(f"手动分割也失败，跳过：{link_text}")
                    continue
            else:
                market_prefix = match.group(1).lower()
                stock_code = match.group(2)
                stock_name = match.group(3).strip()
            
            # 过滤无效数据（保持不变）
            if len(stock_name) < 2 or stock_code in seen_codes:
                logger.info(f"无效数据（重复/名称过短）：{stock_code} | {stock_name}")
                continue
            
            # 确定市场（保持不变）
            market = "深A" if market_prefix == "sz" else "沪A"
            seen_codes.add(stock_code)
            stock_list.append({
                "stockCode": stock_code,
                "stockName": stock_name,
                "market": market
            })
            logger.info(f"✅ 解析成功：{stock_code} | {stock_name} | {market}")
        
        # 保持你的排序逻辑（不变）
        stock_list.sort(key=lambda x: x["stockCode"])
        logger.info(f"解析完成，共得到 {len(stock_list)} 支有效个股（去重后）")
        
        # 无结果时返回友好提示
        if not stock_list:
            return {"stocks": [], "message": f"未找到包含'{keyword}'的股票，请尝试其他关键词"}
        
        return {"stocks": stock_list[:50]}
    
    except requests.exceptions.SSLError:
        logger.error("SSL证书验证失败（已关闭验证仍报错，请检查网络环境）")
        raise HTTPException(status_code=500, detail="SSL证书验证失败，请检查网络环境")
    except requests.exceptions.RequestException as e:
        logger.error(f"接口请求失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"股票搜索接口请求失败：{str(e)}")
    except Exception as e:
        logger.error(f"股票搜索解析失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"股票搜索失败：{str(e)}")

# -------------- 股票详情接口 --------------
@stock_router.get("/{stock_code}/detail", response_model=StockDetailResponse)
def get_stock_detail(stock_code: str):
    """获取股票详情（基础信息+行情+财务+股东）- 已集成指定财务接口"""
    logger.info(f"请求股票详情: {stock_code}")
    
    # 校验股票代码
    if len(stock_code) != 6 or not stock_code.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是6位数字")
    
    market = get_stock_market(stock_code)
    if not market:
        raise HTTPException(status_code=400, detail="仅支持沪深A（60/00/30开头）")
    
    try:
        # 1. 获取基础行情数据
        base_info_data = get_stock_quotes(stock_code)
        if not base_info_data or not base_info_data["dataValidity"]["isValid"]:
            raise HTTPException(status_code=500, detail="股票基础数据无效")
        
        # 2. 获取财务数据（调用上面修改后的方法，使用指定新浪接口）
        financial_data = DataSource.get_stock_financial_data(stock_code)
        
        # 3. 构造基础信息（使用实际可用的数据）
        base_info = {
            **base_info_data["baseInfo"],
            "companyName": base_info_data['baseInfo']['stockName'] or '未知公司',
            "listDate": "--",  # 实际数据接口暂不提供，显示占位符
            "totalShares": "--",  # 默认占位符
            "floatShares": "--",  # 默认占位符
            "marketCap": "--"    # 默认占位符
        }
        
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
@stock_router.get("/valuation/{stock_code}", response_model=Optional[ValuationLogicItem])
def get_stock_valuation(stock_code: str):
    """获取特定股票的估值逻辑数据"""
    try:
        valuation_data = db.get_valuation_by_stock_code(stock_code)
        return valuation_data
    except Exception as e:
        logger.error(f"获取估值逻辑数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取估值逻辑数据失败")

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

