import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)

# 数据库路径
DATABASE_PATH = "../stock_notes.db"

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 允许通过列名访问
    return conn

def init_database(notes_storage: List[Dict[str, Any]] = None, stock_storage: List[Dict[str, Any]] = None):
    """
    初始化数据库并进行数据迁移
    
    Args:
        notes_storage: 笔记内存存储（用于迁移）
        stock_storage: 股票内存存储（用于迁移）
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查notes表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # 检查表结构
            cursor.execute("PRAGMA table_info(notes)")
            columns = [column[1] for column in cursor.fetchall()]
            logger.info(f"当前notes表结构: {columns}")
            
            # 如果缺少关键字段，删除旧表并重新创建
            if 'create_time' not in columns or 'update_time' not in columns:
                logger.warning("notes表结构不完整，删除旧表并重新创建")
                cursor.execute("DROP TABLE notes")
                table_exists = False
        
        # 创建笔记表，包含关联股票字段
        if not table_exists:
            logger.info("创建新的notes表")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    stock_code TEXT DEFAULT '',
                    stock_name TEXT DEFAULT '',
                    type TEXT DEFAULT 'note',  -- note: 普通笔记, pros_cons: 利好利空分析
                    create_time TEXT NOT NULL,
                    update_time TEXT NOT NULL
                )
            ''')
        else:
            # 如果表已存在但缺少必要字段，添加这些字段
            cursor.execute("PRAGMA table_info(notes)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'stock_code' not in columns:
                logger.info("添加stock_code字段到notes表")
                cursor.execute("ALTER TABLE notes ADD COLUMN stock_code TEXT DEFAULT ''")
            if 'stock_name' not in columns:
                logger.info("添加stock_name字段到notes表")
                cursor.execute("ALTER TABLE notes ADD COLUMN stock_name TEXT DEFAULT ''")
            if 'type' not in columns:
                logger.info("添加type字段到notes表")
                cursor.execute("ALTER TABLE notes ADD COLUMN type TEXT DEFAULT 'note'")
        
        conn.commit()
        logger.info("notes表结构初始化成功")
    except Exception as e:
        logger.error(f"初始化notes表失败: {str(e)}")
        conn.rollback()
    # 注意：不要在这里关闭连接，因为后续还有其他数据库操作
    
    # 创建股票清单表
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id TEXT PRIMARY KEY,
                stock_code TEXT NOT NULL UNIQUE,
                stock_name TEXT NOT NULL,
                add_time TEXT NOT NULL,
                remark TEXT DEFAULT '',
                is_hold BOOLEAN DEFAULT 0,
                industry TEXT DEFAULT ''
            )
        ''')
        conn.commit()
        logger.info("stocks表结构初始化成功")
    except Exception as e:
        logger.error(f"初始化stocks表失败: {str(e)}")
        conn.rollback()
    
    # 创建持仓分析持仓表
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_positions (
                id TEXT PRIMARY KEY,
                stock_code TEXT NOT NULL,
                stock_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                cost_price REAL NOT NULL,
                total_cost REAL NOT NULL,
                remark TEXT DEFAULT '',
                create_time TEXT NOT NULL,
                update_time TEXT NOT NULL
            )
        ''')
        conn.commit()
        logger.info("cost_positions表结构初始化成功")
    except Exception as e:
        logger.error(f"初始化cost_positions表失败: {str(e)}")
        conn.rollback()
    
    # 创建估值逻辑表
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS valuation_logic (
                id TEXT PRIMARY KEY,
                stock_code TEXT NOT NULL,
                stock_name TEXT NOT NULL,
                valuation_content TEXT NOT NULL,
                investment_forecast TEXT DEFAULT '',
                trading_plan TEXT DEFAULT '',
                create_time TEXT NOT NULL,
                update_time TEXT NOT NULL
            )
        ''')
        conn.commit()
        logger.info("valuation_logic表结构初始化成功")
    except Exception as e:
        logger.error(f"初始化valuation_logic表失败: {str(e)}")
        conn.rollback()
    
    # 实现数据迁移逻辑
    try:
        # 迁移笔记数据
        cursor.execute("SELECT COUNT(*) FROM notes")
        if cursor.fetchone()[0] == 0 and notes_storage:
            logger.info("检测到数据库为空，开始从内存迁移笔记数据...")
            for note in notes_storage:
                # 尝试映射不同的字段名
                create_time = note.get("create_time", note.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                update_time = note.get("update_time", note.get("updated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                cursor.execute(
                    "INSERT INTO notes (id, title, content, create_time, update_time) VALUES (?, ?, ?, ?, ?)",
                    (note["id"], note["title"], note["content"], create_time, update_time)
                )
            logger.info(f"成功迁移 {len(notes_storage)} 条笔记数据")
        
        # 迁移股票数据
        cursor.execute("SELECT COUNT(*) FROM stocks")
        if cursor.fetchone()[0] == 0 and stock_storage:
            logger.info("检测到数据库为空，开始从内存迁移股票数据...")
            for stock in stock_storage:
                # 避免重复插入
                try:
                    cursor.execute(
                        "INSERT INTO stocks (id, stock_code, stock_name, add_time, remark, is_hold, industry) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (stock["id"], stock["stockCode"], stock["stockName"], stock["addTime"], 
                         stock.get("remark", ""), 1 if stock.get("isHold", False) else 0, stock.get("industry", ""))
                    )
                except sqlite3.IntegrityError:
                    logger.warning(f"股票代码 {stock['stockCode']} 已存在，跳过插入")
            logger.info("成功迁移股票数据")
        
        conn.commit()
    except Exception as e:
        logger.error(f"数据迁移失败: {str(e)}")
        conn.rollback()
    finally:
        conn.close()
        logger.info("数据库初始化完成")

# 笔记相关操作
def get_all_notes(stock_code: Optional[str] = None, note_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取所有笔记，可按股票代码和类型筛选"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if stock_code and note_type:
        cursor.execute("SELECT * FROM notes WHERE stock_code = ? AND type = ? ORDER BY create_time DESC", (stock_code, note_type))
    elif stock_code:
        cursor.execute("SELECT * FROM notes WHERE stock_code = ? ORDER BY create_time DESC", (stock_code,))
    elif note_type:
        cursor.execute("SELECT * FROM notes WHERE type = ? ORDER BY create_time DESC", (note_type,))
    else:
        cursor.execute("SELECT * FROM notes ORDER BY create_time DESC")
    
    rows = cursor.fetchall()
    conn.close()
    
    # 将数据库字段转换为API需要的格式（驼峰命名法）
    result = []
    for row in rows:
        row_dict = dict(row)
        result.append({
            "id": row_dict["id"],
            "title": row_dict["title"],
            "content": row_dict["content"],
            "stockCode": row_dict["stock_code"],
            "stockName": row_dict["stock_name"],
            "type": row_dict["type"],  # 添加type字段
            "createTime": row_dict["create_time"],
            "updateTime": row_dict["update_time"]
        })
    
    return result

def get_note_by_id(note_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取笔记"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    # 将数据库字段转换为API需要的格式（驼峰命名法）
    row_dict = dict(row)
    return {
        "id": row_dict["id"],
        "title": row_dict["title"],
        "content": row_dict["content"],
        "stockCode": row_dict["stock_code"],
        "stockName": row_dict["stock_name"],
        "type": row_dict["type"],  # 添加type字段
        "createTime": row_dict["create_time"],
        "updateTime": row_dict["update_time"]
    }

def create_note(note_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建新笔记"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 支持驼峰命名法和下划线命名法的字段
    stock_code = note_data.get("stock_code", note_data.get("stockCode", ""))
    stock_name = note_data.get("stock_name", note_data.get("stockName", ""))
    note_type = note_data.get("type", "note")  # 默认值为"note"
    create_time = note_data.get("create_time", note_data.get("createTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    update_time = note_data.get("update_time", note_data.get("updateTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    cursor.execute(
        "INSERT INTO notes (id, title, content, stock_code, stock_name, type, create_time, update_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (note_data["id"], note_data["title"], note_data["content"], 
         stock_code, stock_name, note_type, create_time, update_time)
    )
    conn.commit()
    conn.close()
    
    # 返回的数据中包含type字段
    return {
        **note_data,
        "type": note_type,
        "stockCode": stock_code,
        "stockName": stock_name,
        "createTime": create_time,
        "updateTime": update_time
    }

def update_note(note_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新笔记"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查笔记是否存在
    if not get_note_by_id(note_id):
        conn.close()
        return None
    
    # 构建更新语句
    update_fields = []
    update_values = []
    
    if "title" in update_data:
        update_fields.append("title = ?")
        update_values.append(update_data["title"])
    if "content" in update_data:
        update_fields.append("content = ?")
        update_values.append(update_data["content"])
    # 支持股票相关字段的更新
    if "stock_code" in update_data or "stockCode" in update_data:
        stock_code = update_data.get("stock_code", update_data.get("stockCode", ""))
        update_fields.append("stock_code = ?")
        update_values.append(stock_code)
    if "stock_name" in update_data or "stockName" in update_data:
        stock_name = update_data.get("stock_name", update_data.get("stockName", ""))
        update_fields.append("stock_name = ?")
        update_values.append(stock_name)
    # 支持type字段的更新
    if "type" in update_data:
        update_fields.append("type = ?")
        update_values.append(update_data["type"])
    
    # 总是更新update_time
    update_fields.append("update_time = ?")
    update_values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 添加WHERE条件
    update_values.append(note_id)
    query = f"UPDATE notes SET {', '.join(update_fields)} WHERE id = ?"
    cursor.execute(query, update_values)
    conn.commit()
    conn.close()
    
    return get_note_by_id(note_id)

def delete_note(note_id: str) -> bool:
    """删除笔记"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查笔记是否存在
    if not get_note_by_id(note_id):
        conn.close()
        return False
    
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    
    return True

# 估值逻辑相关操作
def get_valuation_by_stock_code(stock_code: str) -> Optional[Dict[str, Any]]:
    """根据股票代码获取估值逻辑数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM valuation_logic WHERE stock_code = ?", (stock_code,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    row_dict = dict(row)
    return {
        "id": row_dict["id"],
        "stockCode": row_dict["stock_code"],
        "stockName": row_dict["stock_name"],
        "valuationContent": row_dict["valuation_content"],
        "investmentForecast": row_dict["investment_forecast"],
        "tradingPlan": row_dict["trading_plan"],
        "createTime": row_dict["create_time"],
        "updateTime": row_dict["update_time"]
    }

def create_valuation(valuation_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建估值逻辑数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO valuation_logic (id, stock_code, stock_name, valuation_content, investment_forecast, trading_plan, create_time, update_time) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (valuation_data["id"], valuation_data["stockCode"], valuation_data["stockName"], 
         valuation_data["valuationContent"], valuation_data["investmentForecast"], 
         valuation_data["tradingPlan"], valuation_data["createTime"], valuation_data["updateTime"])
    )
    conn.commit()
    conn.close()
    
    return valuation_data

def update_valuation(valuation_id: str, valuation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新估值逻辑数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查记录是否存在
    cursor.execute("SELECT * FROM valuation_logic WHERE id = ?", (valuation_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    # 更新记录
    update_fields = []
    update_values = []
    
    if "stockName" in valuation_data:
        update_fields.append("stock_name = ?")
        update_values.append(valuation_data["stockName"])
    
    if "valuationContent" in valuation_data:
        update_fields.append("valuation_content = ?")
        update_values.append(valuation_data["valuationContent"])
    
    if "investmentForecast" in valuation_data:
        update_fields.append("investment_forecast = ?")
        update_values.append(valuation_data["investmentForecast"])
    
    if "tradingPlan" in valuation_data:
        update_fields.append("trading_plan = ?")
        update_values.append(valuation_data["tradingPlan"])
    
    # 强制更新时间
    update_fields.append("update_time = ?")
    update_values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 添加WHERE条件
    update_values.append(valuation_id)
    
    # 执行更新
    sql = f"UPDATE valuation_logic SET {', '.join(update_fields)} WHERE id = ?"
    cursor.execute(sql, update_values)
    conn.commit()
    conn.close()
    
    return get_valuation_by_stock_code(dict(row)["stock_code"])

# 股票相关操作
def get_all_stocks(search: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取股票列表（支持搜索）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if not search or not search.strip():
        # 不需要搜索，获取所有股票
        cursor.execute("SELECT * FROM stocks ORDER BY add_time DESC")
    else:
        # 使用LIKE进行模糊搜索
        keyword = search.strip().lower()
        cursor.execute(
            "SELECT * FROM stocks WHERE LOWER(stock_code) LIKE ? OR LOWER(stock_name) LIKE ? OR LOWER(industry) LIKE ? ORDER BY add_time DESC",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    # 转换为字典列表并处理字段名映射
    result = []
    for row in rows:
        row_dict = dict(row)
        result.append({
            "id": row_dict["id"],
            "stockCode": row_dict["stock_code"],
            "stockName": row_dict["stock_name"],
            "addTime": row_dict["add_time"],
            "remark": row_dict["remark"],
            "isHold": bool(row_dict["is_hold"]),
            "industry": row_dict["industry"]
        })
    
    return result

def get_stock_by_id(stock_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取股票"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stocks WHERE id = ?", (stock_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    row_dict = dict(row)
    return {
        "id": row_dict["id"],
        "stockCode": row_dict["stock_code"],
        "stockName": row_dict["stock_name"],
        "addTime": row_dict["add_time"],
        "remark": row_dict["remark"],
        "isHold": bool(row_dict["is_hold"]),
        "industry": row_dict["industry"]
    }

def create_stock(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建新股票"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO stocks (id, stock_code, stock_name, add_time, remark, is_hold, industry) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (stock_data["id"], stock_data["stockCode"], stock_data["stockName"], 
             stock_data.get("addTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
             stock_data.get("remark", ""), 1 if stock_data.get("isHold", False) else 0,
             stock_data.get("industry", ""))
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError as e:
        logger.error(f"创建股票失败: {str(e)}")
        success = False
    finally:
        conn.close()
    
    return stock_data if success else None

def update_stock(stock_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新股票信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查股票是否存在
    if not get_stock_by_id(stock_id):
        conn.close()
        return None
    
    # 构建更新语句
    update_fields = []
    update_values = []
    
    if "stockName" in update_data:
        update_fields.append("stock_name = ?")
        update_values.append(update_data["stockName"])
    if "remark" in update_data:
        update_fields.append("remark = ?")
        update_values.append(update_data["remark"])
    if "isHold" in update_data:
        update_fields.append("is_hold = ?")
        update_values.append(1 if update_data["isHold"] else 0)
    if "industry" in update_data:
        update_fields.append("industry = ?")
        update_values.append(update_data["industry"])
    
    if update_fields:
        # 添加WHERE条件
        update_values.append(stock_id)
        query = f"UPDATE stocks SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        conn.commit()
    
    conn.close()
    return get_stock_by_id(stock_id)

def delete_stock(stock_id: str) -> bool:
    """删除股票"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查股票是否存在
    if not get_stock_by_id(stock_id):
        conn.close()
        return False
    
    cursor.execute("DELETE FROM stocks WHERE id = ?", (stock_id,))
    conn.commit()
    conn.close()
    
    return True

# 持仓分析相关操作
def get_all_cost_positions() -> List[Dict[str, Any]]:
    """获取所有持仓分析持仓记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cost_positions ORDER BY create_time DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # 将数据库字段转换为API需要的格式（驼峰命名法）
    result = []
    for row in rows:
        row_dict = dict(row)
        result.append({
            "id": row_dict["id"],
            "stockCode": row_dict["stock_code"],
            "stockName": row_dict["stock_name"],
            "quantity": row_dict["quantity"],
            "costPrice": row_dict["cost_price"],
            "totalCost": row_dict["total_cost"],
            "remark": row_dict["remark"],
            "createTime": row_dict["create_time"],
            "updateTime": row_dict["update_time"],
            # 这些字段可以在前端根据实时价格计算
            "currentPrice": 0.0,
            "marketValue": 0.0,
            "profit": 0.0,
            "profitRate": 0.0
        })
    
    return result

def get_cost_position_by_id(position_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取持仓分析持仓记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cost_positions WHERE id = ?", (position_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    # 将数据库字段转换为API需要的格式（驼峰命名法）
    row_dict = dict(row)
    return {
        "id": row_dict["id"],
        "stockCode": row_dict["stock_code"],
        "stockName": row_dict["stock_name"],
        "quantity": row_dict["quantity"],
        "costPrice": row_dict["cost_price"],
        "totalCost": row_dict["total_cost"],
        "remark": row_dict["remark"],
        "createTime": row_dict["create_time"],
        "updateTime": row_dict["update_time"],
        # 这些字段可以在前端根据实时价格计算
        "currentPrice": 0.0,
        "marketValue": 0.0,
        "profit": 0.0,
        "profitRate": 0.0
    }

def create_cost_position(position_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建新的持仓分析持仓记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO cost_positions (id, stock_code, stock_name, quantity, cost_price, total_cost, remark, create_time, update_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (position_data["id"], position_data["stockCode"], position_data["stockName"], 
             position_data["quantity"], position_data["costPrice"], position_data["totalCost"],
             position_data.get("remark", ""), position_data.get("createTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
             position_data.get("updateTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        )
        conn.commit()
        success = True
    except Exception as e:
        logger.error(f"创建持仓分析持仓记录失败: {str(e)}")
        success = False
    finally:
        conn.close()
    
    return position_data if success else None

def update_cost_position(position_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新持仓分析持仓记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查记录是否存在
    if not get_cost_position_by_id(position_id):
        conn.close()
        return None
    
    # 获取当前记录，用于计算total_cost
    cursor.execute("SELECT quantity, cost_price FROM cost_positions WHERE id = ?", (position_id,))
    row = cursor.fetchone()
    current_quantity = row[0] if row else 0
    current_cost_price = row[1] if row else 0
    
    # 构建更新语句
    update_fields = []
    update_values = []
    
    # 计算新的总成本
    new_quantity = update_data.get("quantity", current_quantity)
    new_cost_price = update_data.get("costPrice", current_cost_price)
    new_total_cost = new_quantity * new_cost_price
    
    if "quantity" in update_data:
        update_fields.append("quantity = ?")
        update_values.append(update_data["quantity"])
    if "costPrice" in update_data:
        update_fields.append("cost_price = ?")
        update_values.append(update_data["costPrice"])
    if "remark" in update_data:
        update_fields.append("remark = ?")
        update_values.append(update_data["remark"])
    
    # 总是更新total_cost和update_time
    update_fields.append("total_cost = ?")
    update_values.append(new_total_cost)
    update_fields.append("update_time = ?")
    update_values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 添加WHERE条件
    update_values.append(position_id)
    query = f"UPDATE cost_positions SET {', '.join(update_fields)} WHERE id = ?"
    cursor.execute(query, update_values)
    conn.commit()
    conn.close()
    
    return get_cost_position_by_id(position_id)

def delete_cost_position(position_id: str) -> bool:
    """删除持仓分析持仓记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查记录是否存在
    if not get_cost_position_by_id(position_id):
        conn.close()
        return False
    
    cursor.execute("DELETE FROM cost_positions WHERE id = ?", (position_id,))
    conn.commit()
    conn.close()
    
    return True

def get_cost_overview() -> Dict[str, Any]:
    """获取持仓分析概览数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取总投入成本和持仓数量
    cursor.execute("SELECT SUM(total_cost) as total_cost, COUNT(*) as position_count FROM cost_positions")
    result = cursor.fetchone()
    conn.close()
    
    total_cost = result["total_cost"] or 0.0
    position_count = result["position_count"] or 0
    
    # 由于没有实时价格数据，这里返回基础概览
    # 实时市值、盈亏和盈亏率可以在前端计算
    return {
        "totalCost": round(total_cost, 2),
        "totalMarketValue": 0.0,
        "totalProfit": 0.0,
        "totalProfitRate": 0.0,
        "positionCount": position_count
    }