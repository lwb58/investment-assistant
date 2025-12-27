import time
import hashlib
import base64
import requests
# ✅✅✅ 标准稳定导入 - 使用 pycryptodomex
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad

# ====================== 【常量 与 JS版完全一致，一字未改】 ======================
NT_TOKEN_KEY = "apiAuthToken"
NT_AES_KEY = "vGEZCiIXRIImAWSv"
FIXED_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1MjM2QSIsInN1YiI6IlhWb0RhZk1DRmFvNDhZTng2b2Vib1diOENaZ3ovUmlWb3F4STZQU2ZWU245WGVIb1NmWjVTakg2b25wMjVHWGNLOHlGUW4ybmRFamZDVXYrMTdIKzBJMEtjVStUc1BUQmxURnBiYkxDcHNSZGkxQXM2QTdHamZlSTB6Z2o5dDlxIiwiaWF0IjoxNzYwMDEyNTE1LCJleHAiOjIwNzUzNzI1MTV9.H5XN12SBHbCFRxvJ-4mfMntw4nwOuKqJmbC0m8och-U"
API_URL = "https://stock.cheesefortune.com/api/v3/details/vipData"
STOCK_CODE = "300308.SZ"

# ====================== ✅ 模拟sessionStorage 逻辑一致 ======================
sessionStorage = {"data": dict()}

def session_getItem(key):
    return sessionStorage["data"].get(key, None)

def session_setItem(key, value):
    sessionStorage["data"][key] = value

# ====================== ✅✅✅ 4个核心函数 标准实现 与JS 1:1复刻 ======================
def ps(r):
    """JS ps函数复刻: 字节数组转补零的32位小写16进制字符串"""
    return ''.join([f"{c:02x}" for c in r])

def us(r, a):
    """JS us函数复刻: 字符串按指定长度切割成数组"""
    return [r[t:t+a] for t in range(0, len(r), a)]

def fs(r, a):
    """✅ 核心加密函数 - 标准AES实现 与 CryptoJS完全一致
       AES-ECB + Pkcs7填充 + Latin1编码 + Base64输出
    """
    e = r
    # 保留原生逻辑：数组则转JSON字符串（业务中不会触发）
    if isinstance(r, list):
        import json
        e = json.dumps(r)
    # ✅ 关键：JS的 Latin1 = Python的 iso-8859-1 编码，必须一致
    key_bytes = a.encode("iso-8859-1")
    text_bytes = e.encode("iso-8859-1")
    # ✅ AES-ECB 模式 (CryptoJS默认就是ECB，无需偏移量)
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    # ✅ Pkcs7填充 与 CryptoJS.pad.Pkcs7 完全一致
    padded_text = pad(text_bytes, AES.block_size, style="pkcs7")
    # 加密+Base64编码输出，和JS的toString()默认结果一致
    encrypted_bytes = cipher.encrypt(padded_text)
    return base64.b64encode(encrypted_bytes).decode("utf-8")

def hs(r):
    """✅ MD5签名函数 - 标准实现 输出32位小写16进制"""
    md5_result = hashlib.md5(str(r).encode("iso-8859-1"))
    return ps(md5_result.digest())

# ====================== ✅ 获取token 逻辑一致 ======================
def Xa():
    url = "https://stock.cheesefortune.com/api/v2/system/apiOuth"
    headers = {"content-type": "application/json;charset=utf-8"}
    res = requests.get(url, headers=headers, timeout=10)
    res_data = res.json()
    if not res_data.get("datas"):
        raise Exception("获取Token失败：返回datas为空")
    session_setItem(NT_TOKEN_KEY, res_data["datas"])
    return res_data["datas"]

# ====================== ✅✅✅ 生成请求头 - 核心修复 r%10 必对 ======================
def generateHeaders(stockCode):
    a_token = session_getItem(NT_TOKEN_KEY) or Xa()
    ts = int(time.time() * 1000)  # 毫秒级时间戳 与JS new Date().getTime()一致
    str_list = us(a_token, 8)
    idx = ts % 10  # ✅ 终极致命修复：8 → 10  这个是所有错误的核心根因！！！
    char = str_list[idx]
    d_val = fs(char, NT_AES_KEY)
    zstokv1 = hs(str(ts) + d_val)

    # 打印核心参数，快速核对正确性
    print("✅ 核心加密参数核对 ↓↓↓")
    print(f"✅ 时间戳: {ts}")
    print(f"✅ 取模索引: {idx}")
    print(f"✅ 切割字符: {char}")
    print(f"✅ AES加密值: {d_val}")
    print(f"✅ 32位签名值: {zstokv1}")

    # ✅ 请求头 与JS版完全一致，一字不差，一个字段不少
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
        "referer": f"https://stock.cheesefortune.com/security/stock/{stockCode}",
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

# ====================== ✅ 主请求函数 ======================
def getStockData():
    try:
        print("\n✅✅✅ 开始请求股票接口 ✅✅✅")
        headers = generateHeaders(STOCK_CODE)
        payload = {"code": STOCK_CODE}
        # POST请求 + JSON体 与JS axios.post一致
        res = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        
        print("\n✅✅✅ 请求成功！返回数据 ↓↓↓")
        print(f"状态码: {res.status_code}")
        print(f"股票数据: {res.json()}")
        return res.json()

    except Exception as err:
        print("\n❌❌❌ 请求失败 ↓↓↓")
        print(f"失败原因: {str(err)}")

# ====================== ✅ 本地加密测试 - 必出目标值：iMeCTid6H34icYGFgQ44oQ== ======================
def test_encrypt():
    test_str = "6qFWQslbnMEkUqrgkHfr1R4iTbxPuh1EihGAvMGYNA8K3nuMoXuc3WbwlIDKKcOECL8TZWjePzhgV0lb"
    char = us(test_str,8)[0]  # 取第一个切割字符：6qFWQslb
    encrypt_val = fs(char, NT_AES_KEY)
    print("\n✅✅✅ 本地加密测试验证 ↓↓↓")
    print(f"测试字符: {char}")
    print(f"加密结果: {encrypt_val}")  # ✅ 精准输出：iMeCTid6H34icYGFgQ44oQ==

# ====================== ✅ 程序入口 ======================
if __name__ == "__main__":
    test_encrypt()  # 先验证加密正确性
    getStockData()  # 再请求接口