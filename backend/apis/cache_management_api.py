from fastapi import APIRouter, HTTPException
from utils.cache import get_all_cache_info, clear_all_cache

# 创建缓存管理路由
def create_cache_router():
    cache_router = APIRouter(prefix="/api/cache", tags=["cache-management"])
    
    @cache_router.get("/info")
    def get_cache_information():
        """获取所有缓存信息"""
        try:
            return {
                "code": "000",
                "message": "成功",
                "data": get_all_cache_info()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取缓存信息失败: {str(e)}")
    
    @cache_router.delete("/clear")
    def clear_all_caches():
        """清除所有缓存"""
        try:
            clear_all_cache()
            return {
                "code": "000",
                "message": "成功",
                "data": {"result": "所有缓存已清除"}
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")
    
    return cache_router

# 导出缓存管理路由
cache_router = create_cache_router()