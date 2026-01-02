from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime
import logging
import models.db as db

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由

# 数据模型
class TagCreate(BaseModel):
    name: str
    userId: Optional[str] = None

class TagItem(BaseModel):
    id: str
    name: str
    userId: Optional[str]
    createTime: str
    updateTime: str

# -------------- API接口 --------------
tag_router = APIRouter(prefix="/api/tags", tags=["tags"])

@tag_router.get("", response_model=List[TagItem])
def get_all_tags(user_id: Optional[str] = None):
    """获取所有标签，支持按用户ID过滤"""
    try:
        tags = db.get_all_tags(user_id)
        return tags
    except Exception as e:
        logger.error(f"获取标签失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取标签失败: {str(e)}")

@tag_router.post("", response_model=TagItem)
def create_tag(tag: TagCreate):
    """创建标签"""
    try:
        new_tag = db.create_tag(tag.name, tag.userId)
        return new_tag
    except Exception as e:
        logger.error(f"创建标签失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建标签失败: {str(e)}")