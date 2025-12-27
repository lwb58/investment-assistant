import time
import inspect
from typing import Dict, Any, Callable, Optional

# 全局缓存存储: {函数名: {参数哈希值: (时间戳, 结果)}}
_cache_storage: Dict[str, Dict[str, tuple[float, Any]]] = {}

def cache(expiration_time: int = 1800):
    """通用缓存装饰器 - 彻底修复缓存键BUG，真缓存命中，日志精准
    
    Args:
        expiration_time: 缓存过期时间，单位秒，默认30分钟(1800秒)
    
    Returns:
        装饰后的函数，带有缓存功能
    """
    def decorator(func: Callable) -> Callable:
        # 获取函数名称
        func_name = func.__qualname__
        
        def wrapper(*args, **kwargs):
            # 生成唯一的缓存键 - ✅✅✅ 核心修复：生成【固定、唯一、稳定】的缓存键，永不变化
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 构建参数字典，排除self/cls等特殊参数
            param_dict = dict(bound_args.arguments)
            if 'self' in param_dict:
                del param_dict['self']
            if 'cls' in param_dict:
                del param_dict['cls']
            
            # ✅✅✅ 修复1：生成【固定唯一的字符串缓存键】，替代不稳定的hash()，这是核心！
            # 原理：将参数拼接成固定格式的字符串，同一个参数永远生成同一个字符串，永不变化
            cache_key = str(sorted(param_dict.items()))
            
            current_time = time.time()
            
            # 初始化函数的缓存存储
            if func_name not in _cache_storage:
                _cache_storage[func_name] = {}
            
            # 检查缓存是否存在且未过期 - ✅✅✅ 修复2：精准判断，日志只在真命中时打印
            if cache_key in _cache_storage[func_name]:
                cache_time, cache_result = _cache_storage[func_name][cache_key]
                if current_time - cache_time < expiration_time:
                    print(f"✅【真缓存命中】{func_name} | 缓存键: {cache_key} | 缓存存活: {int(current_time - cache_time)}s")
                    return cache_result
                else:
                    print(f"❌【缓存过期】{func_name} | 缓存键: {cache_key} | 删除过期缓存")
                    del _cache_storage[func_name][cache_key]
            
            # 执行函数获取新结果（缓存未命中/过期）
            result = func(*args, **kwargs)
            
            # 缓存结果
            _cache_storage[func_name][cache_key] = (current_time, result)
            print(f"📌【缓存新增】{func_name} | 缓存键: {cache_key} | 过期时间: {expiration_time}s")
            
            return result
        
        # 添加缓存管理方法 - 保留你所有的原有方法，无改动
        def clear_cache() -> None:
            """清除该函数的所有缓存"""
            if func_name in _cache_storage:
                del _cache_storage[func_name]
                print(f"[缓存清除] {func_name} 的所有缓存已清除")
        
        def get_cache_info() -> Dict[str, Any]:
            """获取缓存信息"""
            if func_name not in _cache_storage:
                return {"function": func_name, "cache_count": 0, "caches": {}}
            
            cache_info = {"function": func_name, "cache_count": len(_cache_storage[func_name]), "caches": {}}
            current_time = time.time()
            
            for key, (timestamp, _) in _cache_storage[func_name].items():
                cache_info["caches"][key] = {
                    "timestamp": timestamp,
                    "age": current_time - timestamp,
                    "expired": current_time - timestamp >= expiration_time
                }
            
            return cache_info
        
        # 将管理方法添加到wrapper
        wrapper.clear_cache = clear_cache
        wrapper.get_cache_info = get_cache_info
        
        return wrapper
    
    return decorator

def clear_all_cache() -> None:
    """清除所有缓存"""
    global _cache_storage
    cache_count = sum(len(func_cache) for func_cache in _cache_storage.values())
    _cache_storage.clear()
    print(f"[缓存清除] 已清除所有 {cache_count} 个缓存项")

def get_all_cache_info() -> Dict[str, Any]:
    """获取所有缓存信息"""
    info = {"total_functions": len(_cache_storage), "total_caches": 0, "functions": {}}
    
    for func_name, func_cache in _cache_storage.items():
        info["functions"][func_name] = {"cache_count": len(func_cache), "cache_keys": list(func_cache.keys())}
        info["total_caches"] += len(func_cache)
    
    return info