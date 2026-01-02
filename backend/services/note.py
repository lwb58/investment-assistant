from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
import os
import shutil
import logging
from typing import Optional, List
from models import db

logger = logging.getLogger(__name__)

# 创建路由实例
note_router = APIRouter(prefix="/api/notes", tags=["笔记模块"])

# -------------- 数据模型 --------------
class NoteCreate(BaseModel):
    title: str
    content: str
    stockCode: Optional[str] = None  # 关联股票代码
    stockName: Optional[str] = None  # 关联股票名称
    type: str = "note"  # 默认值为"note"
    source: Optional[str] = None  # 来源字段
    tags: Optional[str] = None  # 标签，使用逗号分隔

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    stockCode: Optional[str] = None  # 关联股票代码
    stockName: Optional[str] = None  # 关联股票名称
    type: Optional[str] = None
    source: Optional[str] = None  # 来源字段
    tags: Optional[str] = None  # 标签，使用逗号分隔

class NoteItem(BaseModel):
    id: str
    title: str
    content: str
    createTime: str
    updateTime: str
    stockCode: Optional[str] = None  # 保留字段
    stockName: Optional[str] = None  # 保留字段
    type: str  # 添加type字段
    source: Optional[str] = None  # 来源字段
    tags: Optional[str] = None  # 标签，使用逗号分隔


class TagCreate(BaseModel):
    name: str


class TagItem(BaseModel):
    id: str
    name: str
    createTime: str
    updateTime: str

# -------------- API接口 --------------
@note_router.get("", response_model=List[NoteItem])
def get_all_notes(stock_code: Optional[str] = None, note_type: Optional[str] = None):
    """获取所有笔记，支持按股票代码和笔记类型过滤"""
    try:
        logger.info("调用get_all_notes接口")
        notes = db.get_all_notes(stock_code, note_type)
        logger.info(f"成功获取{len(notes)}条笔记")
        return notes
    except Exception as e:
        logger.error(f"获取笔记失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取笔记失败: {str(e)}")

@note_router.get("/tags", response_model=List[TagItem])
def get_all_tags():
    """获取所有标签"""
    try:
        tags = db.get_all_tags()
        return tags
    except Exception as e:
        logger.error(f"获取标签失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取标签失败: {str(e)}")


@note_router.post("/tags", response_model=TagItem)
def create_tag(tag: TagCreate):
    """创建标签"""
    try:
        new_tag = db.create_tag(tag.name)
        return new_tag
    except Exception as e:
        logger.error(f"创建标签失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建标签失败: {str(e)}")

@note_router.get("/stock/{stock_code}", response_model=List[NoteItem])
def get_notes_by_stock(stock_code: str):
    """获取指定股票的关联笔记"""
    try:
        notes = db.get_all_notes(stock_code=stock_code)
        return notes
    except Exception as e:
        logger.error(f"获取股票笔记失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取股票笔记失败: {str(e)}")

@note_router.post("", response_model=NoteItem)
def create_note(note: NoteCreate):
    """创建笔记（支持关联股票和笔记类型）"""
    new_note = {
        "id": str(uuid4()),
        "title": note.title,
        "content": note.content,
        "stockCode": note.stockCode or "",
        "stockName": note.stockName or "",
        "type": note.type or "note",  # 确保type字段被传递
        "source": note.source or "",  # 确保source字段被传递
        "tags": note.tags or "",  # 确保tags字段被传递
        "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    created_note = db.create_note(new_note)
    if not created_note:
        raise HTTPException(status_code=500, detail="笔记创建失败")
    return created_note

@note_router.get("/{note_id}", response_model=NoteItem)
def get_note(note_id: str):
    """获取单条笔记"""
    note = db.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return note

@note_router.put("/{note_id}", response_model=NoteItem)
def update_note(note_id: str, update_data: NoteUpdate):
    """更新笔记（支持关联股票）"""
    update_dict = {}
    if update_data.title:
        update_dict["title"] = update_data.title
    if update_data.content:
        update_dict["content"] = update_data.content
    if update_data.stockCode is not None:
        update_dict["stockCode"] = update_data.stockCode
    if update_data.stockName is not None:
        update_dict["stockName"] = update_data.stockName
    if update_data.type:
        update_dict["type"] = update_data.type
    if update_data.source:
        update_dict["source"] = update_data.source
    if update_data.tags is not None:
        update_dict["tags"] = update_data.tags
    # 强制更新时间
    update_dict["updateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    updated_note = db.update_note(note_id, update_dict)
    if not updated_note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return updated_note

@note_router.delete("/{note_id}")
def delete_note(note_id: str):
    """删除笔记"""
    success = db.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return {"detail": "笔记删除成功"}
    logger.info(f"请求股票{stock_code}的关联笔记")
    
    # 校验股票代码格式
    if not stock_code.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是数字")
    
    # 检查是否为支持的股票代码
    from utils.util import get_stock_market
    market = get_stock_market(stock_code)
    if not market:
        raise HTTPException(status_code=400, detail="仅支持沪深A（60/00/30开头）和港股（5位数字）")
    
    try:
        all_notes = db.get_all_notes()
        # 兼容字典和对象格式
        stock_notes = []
        for note in all_notes:
            note_dict = note if isinstance(note, dict) else note.dict()
            note_stock_code = note_dict.get('stockCode') or ''
            # 检查笔记的stockCode是否包含指定的股票代码（支持多选情况）
            if note_stock_code == stock_code or f",{stock_code}," in f",{note_stock_code},":
                stock_notes.append(note)
        return stock_notes
    except Exception as e:
        logger.error(f"获取股票关联笔记失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="股票关联笔记获取失败")

@note_router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """上传图片，按日期分目录保存"""
    try:
        # 获取backend目录的绝对路径（当前文件在services目录下，需要向上一层）
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        
        # 确保backend/picture目录存在
        base_dir = os.path.join(backend_dir, "picture")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        
        # 获取当前日期，创建日期目录 (YYYY-MM-DD格式)
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_dir = os.path.join(base_dir, current_date)
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)
        
        # 生成唯一文件名，避免重复
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid4().hex}{file_extension}"
        
        # 构建保存路径
        file_path = os.path.join(date_dir, unique_filename)
        
        # 构建相对路径（用于数据库存储和前端显示）
        relative_path = f"/picture/{current_date}/{unique_filename}"
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"图片上传成功: {relative_path}")
        
        # 返回相对路径和文件名
        return JSONResponse(
            content={
                "url": relative_path,
                "filename": unique_filename
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"图片上传失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")