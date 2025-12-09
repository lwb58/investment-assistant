from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
import os
import shutil
import logging
from typing import Optional, List
import db

logger = logging.getLogger(__name__)

# 创建路由实例
note_router = APIRouter(prefix="/api/notes", tags=["笔记模块"])

# -------------- 数据模型 --------------
class NoteCreate(BaseModel):
    title: str
    content: str
    stockCode: Optional[str] = None  # 关联股票代码
    stockName: Optional[str] = None  # 关联股票名称

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    stockCode: Optional[str] = None  # 关联股票代码
    stockName: Optional[str] = None  # 关联股票名称

class NoteItem(BaseModel):
    id: str
    title: str
    content: str
    createTime: str
    updateTime: str
    stockCode: Optional[str] = None  # 保留字段
    stockName: Optional[str] = None  # 保留字段

# -------------- API接口 --------------
@note_router.get("", response_model=List[NoteItem])
def get_all_notes():
    """获取所有笔记（纯同步）"""
    try:
        logger.info("调用get_all_notes接口")
        notes = db.get_all_notes()
        logger.info(f"成功获取{len(notes)}条笔记")
        return notes
    except Exception as e:
        logger.error(f"获取笔记失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取笔记失败: {str(e)}")

@note_router.get("/{note_id}", response_model=NoteItem)
def get_note(note_id: str):
    """获取单条笔记"""
    note = db.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return note

@note_router.post("", response_model=NoteItem)
def create_note(note: NoteCreate):
    """创建笔记（支持关联股票）"""
    new_note = {
        "id": str(uuid4()),
        "title": note.title,
        "content": note.content,
        "stockCode": note.stockCode or "",
        "stockName": note.stockName or "",
        "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    created_note = db.create_note(new_note)
    if not created_note:
        raise HTTPException(status_code=500, detail="笔记创建失败")
    return created_note

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

@note_router.get("/stock/{stock_code}", response_model=List[NoteItem])
def get_notes_by_stock(stock_code: str):
    """获取指定股票的关联笔记"""
    logger.info(f"请求股票{stock_code}的关联笔记")
    
    # 校验股票代码格式
    if len(stock_code) != 6 or not stock_code.isdigit():
        raise HTTPException(status_code=400, detail="股票代码必须是6位数字")
    
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
async def upload_image(file: UploadFile = File(...), stock_code: str = None):
    """上传图片，按股票代码分类保存"""
    try:
        # 确保picture目录存在
        base_dir = "d:\\yypt\\xingziyuan\\investment-assistant\\backend\\picture"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        
        # 如果提供了股票代码，创建股票代码目录
        if stock_code:
            # 校验股票代码格式
            if len(stock_code) != 6 or not stock_code.isdigit():
                raise HTTPException(status_code=400, detail="股票代码必须是6位数字")
            
            stock_dir = os.path.join(base_dir, stock_code)
            if not os.path.exists(stock_dir):
                os.makedirs(stock_dir)
            
            # 构建保存路径
            file_path = os.path.join(stock_dir, file.filename)
            # 构建相对路径（用于前端显示）
            relative_path = f"/backend/picture/{stock_code}/{file.filename}"
        else:
            # 没有股票代码时直接保存在picture目录
            file_path = os.path.join(base_dir, file.filename)
            relative_path = f"/backend/picture/{file.filename}"
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"图片上传成功: {relative_path}")
        
        # 返回相对路径和文件名
        return JSONResponse(
            content={
                "url": relative_path,
                "filename": file.filename
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"图片上传失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")