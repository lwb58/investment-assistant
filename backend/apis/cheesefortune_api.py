import time
import hashlib
import base64
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad

# 导入配置
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CHEESEFORTUNE_FIXED_TOKEN, CACHE_EXPIRATION_TIME

# 导入通用缓存装饰器（修复后的，已无BUG）
from utils.cache import cache

# 创建路由实例
cheesefortune_router = APIRouter(prefix="/api/cheesefortune", tags=["芝士财富API"])

# ====================== 常量定义 ======================
NT_TOKEN_KEY = "apiAuthToken"
NT_AES_KEY = "vGEZCiIXRIImAWSv"
FIXED_TOKEN = CHEESEFORTUNE_FIXED_TOKEN  # 从配置文件导入
API_URL = "https://stock.cheesefortune.com/api/v3/details/vipData"

# ====================== 模拟sessionStorage ======================
sessionStorage = {"data": dict()}

def session_getItem(key):
    return sessionStorage["data"].get(key, None)

def session_setItem(key, value):
    sessionStorage["data"][key] = value

# ====================== 核心函数 ======================
def ps(r):
    """字节数组转补零的32位小写16进制字符串"""
    return ''.join([f"{c:02x}" for c in r])

def us(r, a):
    """字符串按指定长度切割成数组"""
    return [r[t:t+a] for t in range(0, len(r), a)]

def fs(r, a):
    """AES加密函数 - AES-ECB + Pkcs7填充 + Latin1编码 + Base64输出"""
    e = r
    if isinstance(r, list):
        import json
        e = json.dumps(r)
    key_bytes = a.encode("iso-8859-1")
    text_bytes = e.encode("iso-8859-1")
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    padded_text = pad(text_bytes, AES.block_size, style="pkcs7")
    encrypted_bytes = cipher.encrypt(padded_text)
    return base64.b64encode(encrypted_bytes).decode("utf-8")

def hs(r):
    """MD5签名函数 - 输出32位小写16进制"""
    md5_result = hashlib.md5(str(r).encode("iso-8859-1"))
    return ps(md5_result.digest())

# ====================== 获取token ======================
def get_token():
    """获取API访问令牌"""
    url = "https://stock.cheesefortune.com/api/v2/system/apiOuth"
    headers = {"content-type": "application/json;charset=utf-8"}
    res = requests.get(url, headers=headers, timeout=10)
    res_data = res.json()
    if not res_data.get("datas"):
        raise Exception("获取Token失败：返回datas为空")
    session_setItem(NT_TOKEN_KEY, res_data["datas"])
    return res_data["datas"]

# ====================== 生成请求头 ======================
def generate_headers(stock_code):
    """生成芝士财富API请求头"""
    a_token = session_getItem(NT_TOKEN_KEY) or get_token()
    ts = int(time.time() * 1000)
    str_list = us(a_token, 8)
    idx = ts % 10
    char = str_list[idx]
    d_val = fs(char, NT_AES_KEY)
    zstokv1 = hs(str(ts) + d_val)

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "connection": "keep-alive",
        "content-type": "application/json;charset=utf-8",
        "cookie": "x-hng=lang=zh-CN&domain=stock.cheesefortune.com",
        "devicetype": "pc",
        "expires": "-1",
        "host": "stock.cheesefortune.com",
        "referer": f"https://stock.cheesefortune.com/security/stock/{stock_code}",
        "requestfrom": "wechat",
        "runtimetype": "browser",
        "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "timestamp": str(ts),
        "token": FIXED_TOKEN,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
        "zstokv1": zstokv1
    }
    return headers

# ====================== 全局会话，复用连接（小优化，保留） ======================
session = requests.Session()

# ====================== 获取VIP数据 ======================
@cache(expiration_time=CACHE_EXPIRATION_TIME)
def get_vip_data(stock_code):
    """获取芝士财富股票VIP数据（带通用缓存装饰器）"""
    print(f"🔴【函数执行实锤】get_vip_data被完整调用！股票代码: {stock_code}")
    try:
        headers = generate_headers(stock_code)
        payload = {"code": stock_code}
        print(f"🔴【网络请求实锤】正在发起真实请求！股票代码: {stock_code}")
        res = session.post(API_URL, json=payload, headers=headers, timeout=20)
        
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=f"芝士财富API请求失败: {res.text}")
        
        data = res.json()
        
        if data.get("code") == "-002":
            raise HTTPException(status_code=429, detail="芝士财富API访问频繁，请稍后再试")
        
        return data

    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"获取芝士财富VIP数据失败: {str(err)}")

# ====================== API接口 ======================
@cheesefortune_router.get("/vip-data/{stock_code}")
def get_cheesefortune_vip_data(stock_code: str):
    """获取芝士财富股票VIP数据（带30分钟缓存机制）"""
    total_start = time.time()
    try:
        data = get_vip_data(stock_code)
        # ✅ 只加了这一行日志，无任何逻辑改动
        print(f"🌐【接口耗时统计】股票代码: {stock_code} | 总耗时: {(time.time()-total_start)*1000:.2f} ms")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取芝士财富VIP数据失败: {str(e)}")

# ====================== 缓存管理接口已移至 cache_management_api.py ======================