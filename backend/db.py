import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)

# 数据库路径
DATABASE_PATH = "stock_notes.db"

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
    
    # 创建笔记表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            create_time TEXT NOT NULL,
            update_time TEXT NOT NULL
        )
    ''')
    
    # 创建股票清单表
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
def get_all_notes() -> List[Dict[str, Any]]:
    """获取所有笔记"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY create_time DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_note_by_id(note_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取笔记"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def create_note(note_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建新笔记"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO notes (id, title, content, create_time, update_time) VALUES (?, ?, ?, ?, ?)",
        (note_data["id"], note_data["title"], note_data["content"], 
         note_data.get("create_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
         note_data.get("update_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    )
    conn.commit()
    conn.close()
    
    return note_data

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