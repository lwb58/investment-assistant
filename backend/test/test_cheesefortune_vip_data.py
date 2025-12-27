import time
import hashlib
import base64
import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad

# 常量定义
NT_TOKEN_KEY = "apiAuthToken"
NT_AES_KEY = "vGEZCiIXRIImAWSv"
FIXED_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1MjM2QSIsInN1YiI6IlhWb0RhZk1DRmFvNDhZTng2b2Vib1diOENaZ3ovUmlWb3F4STZQU2ZWU245WGVIb1NmWjVTakg2b25wMjVHWGNLOHlGUW4ybmRFamZDVXYrMTdIKzBJMEtjVStUc1BUQmxURnBiYkxDcHNSZGkxQXM2QTdHamZlSTB6Z2o5dDlxIiwiaWF0IjoxNzYwMDEyNTE1LCJleHAiOjIwNzUzNzI1MTV9.H5XN12SBHbCFRxvJ-4mfMntw4nwOuKqJmbC0m8och-U"
API_URL = "https://stock.cheesefortune.com/api/v3/details/vipData"

# 模拟sessionStorage
sessionStorage = {"data": dict()}

def session_getItem(key):
    return sessionStorage["data"].get(key, None)

def session_setItem(key, value):
    sessionStorage["data"][key] = value

# 核心函数
def ps(r):
    return ''.join([f"{c:02x}" for c in r])

def us(r, a):
    return [r[t:t+a] for t in range(0, len(r), a)]

def fs(r, a):
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
    md5_result = hashlib.md5(str(r).encode("iso-8859-1"))
    return ps(md5_result.digest())

# 获取token
def get_token():
    url = "https://stock.cheesefortune.com/api/v2/system/apiOuth"
    headers = {"content-type": "application/json;charset=utf-8"}
    res = requests.get(url, headers=headers, timeout=10)
    res_data = res.json()
    if not res_data.get("datas"):
        raise Exception("获取Token失败：返回datas为空")
    session_setItem(NT_TOKEN_KEY, res_data["datas"])
    return res_data["datas"]

# 生成请求头
def generate_headers(stock_code):
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

# 获取VIP数据
def get_vip_data(stock_code):
    print(f"获取股票 {stock_code} 的VIP数据...")
    try:
        headers = generate_headers(stock_code)
        payload = {"code": stock_code}
        
        start_time = time.time()
        res = requests.post(API_URL, json=payload, headers=headers, timeout=20)
        end_time = time.time()
        
        print(f"请求耗时: {end_time - start_time:.2f}秒")
        print(f"状态码: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            print(f"返回数据: {data}")
            return data
        else:
            print(f"请求失败: {res.text}")
            return None
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None

# 测试用例
def test_cheesefortune_vip_data():
    # 测试两个股票代码
    stock_codes = ["600219.SH", "300308.SZ"]
    
    for code in stock_codes:
        print("\n" + "="*50)
        print(f"测试股票: {code}")
        print("="*50)
        data = get_vip_data(code)
        if data:
            print(f"\n✅ 测试通过: 成功获取到 {code} 的VIP数据")
        else:
            print(f"\n❌ 测试失败: 无法获取 {code} 的VIP数据")

if __name__ == "__main__":
    test_cheesefortune_vip_data()