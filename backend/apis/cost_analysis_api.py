from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
from typing import List, Optional
import logging
from models import db
from services.stock import get_stock_quotes

logger = logging.getLogger(__name__)

# 创建路由实例
position_analysis_router = APIRouter(prefix="/api/position-analysis", tags=["持仓分析模块"])

# -------------- 数据模型 --------------
class CostPositionBase(BaseModel):
    stockCode: str = Field(..., description="股票代码")
    stockName: str = Field(..., description="股票名称")
    quantity: float = Field(..., gt=0, description="持有数量")
    costPrice: float = Field(..., gt=0, description="成本价")
    remark: Optional[str] = Field(None, description="备注")

class CostPositionCreate(CostPositionBase):
    pass

class CostPositionUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0, description="持有数量")
    costPrice: Optional[float] = Field(None, gt=0, description="成本价")
    remark: Optional[str] = Field(None, description="备注")

class CostPositionItem(BaseModel):
    id: str
    stockCode: str
    stockName: str
    quantity: float
    costPrice: float
    totalCost: float
    currentPrice: Optional[float] = Field(None, description="当前价格")
    marketValue: Optional[float] = Field(None, description="当前市值")
    profit: Optional[float] = Field(None, description="盈亏金额")
    profitRate: Optional[float] = Field(None, description="盈亏比例")
    remark: Optional[str] = None
    createTime: str
    updateTime: str
    
    class Config:
        from_attributes = True

class CostOverview(BaseModel):
    totalCost: float
    totalMarketValue: float
    totalProfit: float
    totalProfitRate: float
    positionCount: int

# -------------- API接口 --------------
@position_analysis_router.get("/positions", response_model=List[CostPositionItem])
def get_all_positions():
    """获取所有持仓股票记录（从股票清单表筛选持仓状态的记录）"""
    try:
        logger.info("调用get_all_positions接口")
        
        # 1. 从股票清单表获取所有持仓状态的股票
        all_stocks = db.get_all_stocks()
        hold_stocks = [stock for stock in all_stocks if stock['isHold']]
        logger.info(f"从股票清单表获取到{len(hold_stocks)}条持仓状态的股票")
        
        # 2. 获取所有成本持仓记录，用于关联
        cost_positions = db.get_all_cost_positions()
        # 创建股票代码到持仓详情的映射，方便快速查找
        cost_map = {pos['stockCode']: pos for pos in cost_positions}
        
        # 3. 构建最终的持仓列表
        positions = []
        for stock in hold_stocks:
            stock_code = stock['stockCode']
            # 如果在成本持仓表中有对应的记录，使用该记录
            if stock_code in cost_map:
                position = cost_map[stock_code].copy()
            else:
                # 如果没有对应的持仓记录，创建一个默认的持仓记录
                # 这种情况可能发生在股票被标记为持仓但还没有设置具体持仓详情时
                position = {
                    "id": str(uuid4()),  # 临时ID，实际使用时会被覆盖
                    "stockCode": stock_code,
                    "stockName": stock['stockName'],
                    "quantity": 0.0,
                    "costPrice": 0.0,
                    "totalCost": 0.0,
                    "remark": stock.get('remark', ''),
                    "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # 为持仓记录添加实时价格和市值信息
            try:
                stock_data = get_stock_quotes(stock_code)
                if stock_data and 'coreQuotes' in stock_data:
                    current_price = float(stock_data['coreQuotes']['currentPrice'])
                    position['currentPrice'] = current_price
                    position['marketValue'] = round(current_price * position.get('quantity', 0), 2)
                    position['profit'] = round(position['marketValue'] - position.get('totalCost', 0), 2)
                    if position.get('totalCost', 0) > 0:
                        position['profitRate'] = round((position['profit'] / position['totalCost']) * 100, 2)
                    else:
                        position['profitRate'] = 0.0
            except Exception as e:
                logger.warning(f"获取股票{stock_code}实时价格失败: {str(e)}")
            
            positions.append(position)
        
        logger.info(f"最终返回{len(positions)}条持仓记录")
        return positions
    except Exception as e:
        logger.error(f"获取持仓记录失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取持仓记录失败: {str(e)}")

@position_analysis_router.get("/positions/{position_id}", response_model=CostPositionItem)
def get_position(position_id: str):
    """获取单个持仓记录，包含实时价格和市值信息"""
    position = db.get_cost_position_by_id(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="持仓记录不存在")
    
    # 添加实时价格和市值信息
    try:
        stock_data = get_stock_quotes(position['stockCode'])
        if stock_data and 'coreQuotes' in stock_data:
            current_price = float(stock_data['coreQuotes']['currentPrice'])
            position['currentPrice'] = current_price
            position['marketValue'] = round(current_price * position['quantity'], 2)
            position['profit'] = round(position['marketValue'] - position['totalCost'], 2)
            position['profitRate'] = round((position['profit'] / position['totalCost']) * 100, 2)
    except Exception as e:
        logger.warning(f"获取股票{position['stockCode']}实时价格失败: {str(e)}")
    
    return position

@position_analysis_router.post("/positions", response_model=CostPositionItem)
def create_position(create_data: CostPositionCreate):
    """创建新的持仓记录"""
    try:
        # 检查是否已存在相同股票代码的持仓记录
        existing_positions = db.get_all_cost_positions()
        for pos in existing_positions:
            if pos['stockCode'] == create_data.stockCode:
                # 如果存在，更新现有记录
                return update_position(pos['id'], CostPositionUpdate(
                    quantity=create_data.quantity,
                    costPrice=create_data.costPrice,
                    remark=create_data.remark
                ))
        
        # 创建新记录
        new_position = {
            "id": str(uuid4()),
            "stockCode": create_data.stockCode,
            "stockName": create_data.stockName,
            "quantity": create_data.quantity,
            "costPrice": create_data.costPrice,
            "totalCost": create_data.quantity * create_data.costPrice,
            "remark": create_data.remark,
            "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 保存到数据库
        created_position = db.create_cost_position(new_position)
        
        # 添加实时价格信息
        try:
            stock_data = get_stock_quotes(created_position['stockCode'])
            if stock_data and 'coreQuotes' in stock_data:
                current_price = float(stock_data['coreQuotes']['currentPrice'])
                created_position['currentPrice'] = current_price
                created_position['marketValue'] = round(current_price * created_position['quantity'], 2)
                created_position['profit'] = round(created_position['marketValue'] - created_position['totalCost'], 2)
                created_position['profitRate'] = round((created_position['profit'] / created_position['totalCost']) * 100, 2)
        except Exception as e:
            logger.warning(f"获取股票{created_position['stockCode']}实时价格失败: {str(e)}")
        
        return created_position
    except Exception as e:
        logger.error(f"创建持仓记录失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建持仓记录失败: {str(e)}")

@position_analysis_router.put("/positions/{position_id}", response_model=CostPositionItem)
def update_position(position_id: str, update_data: CostPositionUpdate):
    """更新持仓记录（用于编辑持有数量和成本，支持补仓测算功能）"""
    # 验证持仓记录是否存在
    existing_position = db.get_cost_position_by_id(position_id)
    if not existing_position:
        raise HTTPException(status_code=404, detail="持仓记录不存在")
    
    # 构建更新字典
    update_dict = {}
    if update_data.quantity is not None:
        update_dict["quantity"] = update_data.quantity
    if update_data.costPrice is not None:
        update_dict["costPrice"] = update_data.costPrice
        # 自动计算总成本
        current_quantity = update_dict.get("quantity", existing_position.get("quantity", 0))
        update_dict["totalCost"] = current_quantity * update_data.costPrice
    if update_data.remark is not None:
        update_dict["remark"] = update_data.remark
    # 强制更新时间
    update_dict["updateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 执行更新
    updated_position = db.update_cost_position(position_id, update_dict)
    if not updated_position:
        raise HTTPException(status_code=404, detail="持仓记录不存在")
    
    # 添加实时价格信息
    try:
        stock_data = get_stock_quotes(updated_position['stockCode'])
        if stock_data and 'coreQuotes' in stock_data:
            current_price = float(stock_data['coreQuotes']['currentPrice'])
            updated_position['currentPrice'] = current_price
            updated_position['marketValue'] = round(current_price * updated_position['quantity'], 2)
            updated_position['profit'] = round(updated_position['marketValue'] - updated_position['totalCost'], 2)
            updated_position['profitRate'] = round((updated_position['profit'] / updated_position['totalCost']) * 100, 2)
    except Exception as e:
        logger.warning(f"获取股票{updated_position['stockCode']}实时价格失败: {str(e)}")
    
    return updated_position

@position_analysis_router.get("/overview", response_model=CostOverview)
def get_position_overview():
    """获取持仓分析概览，使用实时价格计算市值和盈亏（基于持仓状态的股票）"""
    try:
        # 从股票清单表获取所有持仓状态的股票
        all_stocks = db.get_all_stocks()
        hold_stocks = [stock for stock in all_stocks if stock['isHold']]
        
        # 获取所有成本持仓记录，用于关联
        cost_positions = db.get_all_cost_positions()
        cost_map = {pos['stockCode']: pos for pos in cost_positions}
        
        total_cost = 0
        total_market_value = 0
        
        # 计算总成本和总市值
        for stock in hold_stocks:
            stock_code = stock['stockCode']
            # 获取持仓成本信息
            if stock_code in cost_map:
                position = cost_map[stock_code]
                total_cost += position.get("totalCost", 0)
            
            # 获取实时价格并计算市值
            try:
                stock_data = get_stock_quotes(stock_code)
                if stock_data and 'coreQuotes' in stock_data:
                    current_price = float(stock_data['coreQuotes']['currentPrice'])
                    # 获取持仓数量（如果有）
                    quantity = cost_map.get(stock_code, {}).get('quantity', 0)
                    market_value = current_price * quantity
                    total_market_value += market_value
            except Exception as e:
                logger.warning(f"获取股票{stock_code}实时价格失败: {str(e)}")
        
        # 计算总盈亏和盈亏比例
        total_profit = round(total_market_value - total_cost, 2)
        total_profit_rate = round((total_profit / total_cost) * 100, 2) if total_cost > 0 else 0
        position_count = len(hold_stocks)
        
        return CostOverview(
            totalCost=total_cost,
            totalMarketValue=total_market_value,
            totalProfit=total_profit,
            totalProfitRate=total_profit_rate,
            positionCount=position_count
        )
    except Exception as e:
        logger.error(f"获取持仓分析概览失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取持仓分析概览失败: {str(e)}")
