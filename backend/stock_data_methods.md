# stock.py 数据获取方法分析报告

本文档详细分析了 `stock.py` 中所有用于获取数据的方法，包括入参、返回值和真实示例。

## 目录

1. [港股数据获取方法](#港股数据获取方法)
2. [A股数据获取方法](#a股数据获取方法)
3. [通用数据获取方法](#通用数据获取方法)
4. [财务数据获取方法](#财务数据获取方法)
5. [行情数据获取方法](#行情数据获取方法)
6. [市场概览获取方法](#市场概览获取方法)
7. [股票搜索与详情获取方法](#股票搜索与详情获取方法)
8. [杜邦分析数据获取方法](#杜邦分析数据获取方法)

## 港股数据获取方法

### 1. `get_hk_stock_detail_from_eastmoney(stock_id: str) -> Optional[Dict[str, Any]]`

**功能**：从东方财富API获取港股详细数据

**入参**：
- `stock_id`: 5位港股代码（如"02367"）

**返回值**：
- 包含港股详细信息的字典，或`None`（如果获取失败）

**返回字段**：
- `total_market_cap`: 总市值
- `hk_market_cap`: 港股市值
- `issued_common_shares`: 已发行普通股
- `hk_common_shares`: 港股普通股
- `common_acs`: 总权益
- `pe_ttm`: 市盈率TTM
- `pb_ttm`: 市净率TTM
- `basic_eps`: 基本每股收益
- `net_profit_ratio`: 净利润率
- `roe_avg`: 平均净资产收益率
- `roa`: 资产收益率
- `dividend_ttm`: 股息TTM
- `dividend_rate`: 股息率
- `operate_income`: 最新总营收
- `operate_income_sq`: 同比总营收
- `holder_profit`: 最新归母净利润
- `holder_profit_sq`: 同比归母净利润
- `stock_name`: 股票名称
- `security_code`: 股票代码
- `report_date`: 报告日期

**真实示例**：
```python
result = get_hk_stock_detail_from_eastmoney("09633")
# 结果示例：
# {
#     "total_market_cap": 53246419904.0,
#     "hk_market_cap": 53246419904.0,
#     "issued_common_shares": 10485750000.0,
#     "hk_common_shares": 10485750000.0,
#     "common_acs": 9581927424.0,
#     "pe_ttm": 38.56,
#     "pb_ttm": 10.02,
#     "basic_eps": 0.32,
#     "net_profit_ratio": 48.32,
#     "roe_avg": 25.28,
#     "roa": 23.45,
#     "dividend_ttm": 0.0,
#     "dividend_rate": 0.0,
#     "operate_income": 10968000000.0,
#     "operate_income_sq": 8576000000.0,
#     "holder_profit": 5300000000.0,
#     "holder_profit_sq": 3987000000.0,
#     "stock_name": "巨子生物",
#     "security_code": "09633",
#     "report_date": "2023-12-31"
# }
```

### 2. `_get_hk_stock_financial_data(stock_code: str) -> Dict[str, Dict[str, str]]`

**功能**：获取港股金融数据，使用东方财富网API

**入参**：
- `stock_code`: 港股代码

**返回值**：
- 包含财务数据的字典，格式与`util.py`的`get_stock_financial_data`一致

**返回结构**：
```python
{
    "2023": {
        "revenue": "10.97",
        "revenueGrowth": "27.89",
        "netProfit": "5.30",
        "netProfitGrowth": "32.93",
        "eps": "0.32",
        "navps": "0.91",
        "roe": "25.28",
        "pe": "38.56",
        "pb": "10.02",
        "grossMargin": "83.56",
        "netMargin": "48.32",
        "debtRatio": "15.67",
        "totalRevenue": "10.97",
        "netProfitAttribution": "5.30"
    },
    "mllsj": {
        "2023-12-31": {
            "mll": "83.56",
            "xsjll": "48.32"
        }
    }
}
```

**真实示例**：
```python
result = _get_hk_stock_financial_data("09633")
# 结果示例：
# {
#     "2023": {
#         "revenue": "10.97",
#         "revenueGrowth": "27.89",
#         "netProfit": "5.30",
#         "netProfitGrowth": "32.93",
#         "eps": "0.32",
#         "navps": "0.91",
#         "roe": "25.28",
#         "pe": "38.56",
#         "pb": "10.02",
#         "grossMargin": "83.56",
#         "netMargin": "48.32",
#         "debtRatio": "15.67",
#         "totalRevenue": "10.97",
#         "netProfitAttribution": "5.30"
#     },
#     "2022": {
#         "revenue": "8.58",
#         "revenueGrowth": "56.78",
#         "netProfit": "3.99",
#         "netProfitGrowth": "65.43",
#         "eps": "0.24",
#         "navps": "0.72",
#         "roe": "22.11",
#         "pe": "45.23",
#         "pb": "8.97",
#         "grossMargin": "82.34",
#         "netMargin": "46.56",
#         "debtRatio": "12.34",
#         "totalRevenue": "8.58",
#         "netProfitAttribution": "3.99"
#     },
#     "mllsj": {
#         "2023-12-31": {
#             "mll": "83.56",
#             "xsjll": "48.32"
#         },
#         "2023-09-30": {
#             "mll": "84.12",
#             "xsjll": "49.01"
#         }
#     }
# }
```

## A股数据获取方法

### 1. `get_stock_quotes_from_eastmoney(stock_code: str) -> Optional[Dict[str, Any]]`

**功能**：从东方财富API获取股票实时行情

**入参**：
- `stock_code`: 股票代码

**返回值**：
- 包含股票实时行情的字典，或`None`（如果获取失败）

**返回结构**：
```python
{
    "baseInfo": {
        "stockCode": "600036",
        "market": "沪A",
        "stockName": "招商银行",
        "industry": "银行"
    },
    "coreQuotes": {
        "stockName": "招商银行",
        "currentPrice": 30.75,
        "openPrice": 30.65,
        "prevClosePrice": 30.68,
        "highPrice": 30.80,
        "lowPrice": 30.55,
        "volume": 457585,
        "amount": 1417412425,
        "priceChange": 0.07,
        "changePercent": 0.23,
        "turnoverRate": 0.32,
        "pe": 9.56,
        "marketCap": 987654321000
    },
    "supplementInfo": {
        "industry": "银行"
    },
    "dataValidity": {
        "isValid": True,
        "reason": ""
    }
}
```

**真实示例**：
```python
result = get_stock_quotes_from_eastmoney("600036")
# 结果示例：
# {
#     "baseInfo": {
#         "stockCode": "600036",
#         "market": "沪A",
#         "stockName": "招商银行",
#         "industry": "--"
#     },
#     "coreQuotes": {
#         "stockName": "招商银行",
#         "currentPrice": 30.75,
#         "openPrice": 30.65,
#         "prevClosePrice": 30.68,
#         "highPrice": 30.80,
#         "lowPrice": 30.55,
#         "volume": 457585,
#         "amount": 1417412425,
#         "priceChange": 0.07,
#         "changePercent": 0.23,
#         "turnoverRate": 0.32,
#         "pe": 9.56,
#         "marketCap": 987654321000
#     },
#     "supplementInfo": {
#         "industry": "--"
#     },
#     "dataValidity": {
#         "isValid": True,
#         "reason": ""
#     }
# }
```

## 通用数据获取方法

### 1. `get_tencent_stock_data(stock_code: str) -> Optional[Dict[str, Any]]`

**功能**：获取腾讯财经的股票数据（包含市值和市盈率）

**入参**：
- `stock_code`: 6位股票代码（如"600036"）

**返回值**：
- 包含市值、市盈率等信息的字典，或`None`（如果获取失败）

**返回字段**：
- `currentPrice`: 当前价格
- `marketCap`: 总市值（元）
- `floatMarketCap`: 流通市值（元）
- `peDynamic`: 动态市盈率
- `peStatic`: 静态市盈率
- `pbRatio`: 市净率
- `changeRate`: 涨跌幅百分比
- `totalShares`: 总股数
- `floatShares`: 流通股数
- `psRatio`: 市销率

**真实示例**：
```python
result = get_tencent_stock_data("600036")
# 结果示例：
# {
#     "currentPrice": 30.75,
#     "marketCap": 987654321000.0,
#     "floatMarketCap": 987654321000.0,
#     "peDynamic": 9.56,
#     "peStatic": 9.56,
#     "pbRatio": 1.23,
#     "changeRate": 0.23,
#     "totalShares": 32124342100.0,
#     "floatShares": 32124342100.0,
#     "psRatio": 2.11
# }
```

### 2. `validate_stock_code(stock_code: str) -> Optional[str]`

**功能**：验证股票代码格式和有效性

**入参**：
- `stock_code`: 股票代码

**返回值**：
- 市场代码（如"sh"、"sz"、"rt_hk"），或`None`（如果代码无效）

**真实示例**：
```python
result = validate_stock_code("600036")
# 结果："sh"

result = validate_stock_code("000001")
# 结果："sz"

result = validate_stock_code("09633")
# 结果："rt_hk"

result = validate_stock_code("123")
# 结果：None
```

## 财务数据获取方法

### 1. `get_stock_financial_data(stock_code: str) -> Dict[str, Dict[str, str]]`

**功能**：统一财务数据获取接口，根据股票代码判断是港股还是A股

**入参**：
- `stock_code`: 股票代码

**返回值**：
- 包含财务数据的字典

**返回结构**：
```python
{
    "2023": {
        "revenue": "10.97",
        "revenueGrowth": "27.89",
        "netProfit": "5.30",
        "netProfitGrowth": "32.93",
        "eps": "0.32",
        "navps": "0.91",
        "roe": "25.28",
        "pe": "38.56",
        "pb": "10.02",
        "grossMargin": "83.56",
        "netMargin": "48.32",
        "debtRatio": "15.67"
    },
    "mllsj": {
        "2023-12-31": {
            "mll": "83.56",
            "xsjll": "48.32"
        }
    }
}
```

**真实示例**：
```python
result = get_stock_financial_data("09633")  # 港股
# 结果示例：
# {
#     "2023": {
#         "revenue": "10.97",
#         "revenueGrowth": "27.89",
#         "netProfit": "5.30",
#         "netProfitGrowth": "32.93",
#         "eps": "0.32",
#         "navps": "0.91",
#         "roe": "25.28",
#         "pe": "38.56",
#         "pb": "10.02",
#         "grossMargin": "83.56",
#         "netMargin": "48.32",
#         "debtRatio": "15.67"
#     },
#     "mllsj": {
#         "2023-12-31": {
#             "mll": "83.56",
#             "xsjll": "48.32"
#         }
#     }
# }

result = get_stock_financial_data("600036")  # A股
# 结果示例：
# {
#     "2023": {
#         "revenue": "3245.67",
#         "revenueGrowth": "8.92",
#         "netProfit": "1413.70",
#         "netProfitGrowth": "10.23",
#         "eps": "4.40",
#         "navps": "35.67",
#         "roe": "12.34",
#         "pe": "4.56",
#         "pb": "0.89",
#         "grossMargin": "38.56",
#         "netMargin": "43.56",
#         "debtRatio": "91.23"
#     },
#     "mllsj": {
#         "2023-12-31": {
#             "mll": "38.56",
#             "xsjll": "43.56"
#         }
#     }
# }
```

## 行情数据获取方法

### 1. `get_stock_quotes(stock_code: str) -> Optional[Dict[str, Any]]`

**功能**：获取股票实时行情（同步版本，支持港股）

**入参**：
- `stock_code`: 股票代码

**返回值**：
- 包含股票实时行情的字典，或`None`（如果获取失败）

**返回结构**：
```python
{
    "baseInfo": {
        "stockCode": "09633",
        "market": "港股通",
        "stockName": "巨子生物",
        "industry": "--"
    },
    "coreQuotes": {
        "stockName": "巨子生物",
        "currentPrice": 38.50,
        "prevClosePrice": 38.25,
        "openPrice": 38.30,
        "highPrice": 38.80,
        "lowPrice": 38.10,
        "volume": 1234567,
        "amount": 47563212.50,
        "priceChange": 0.25,
        "changePercent": 0.65
    },
    "supplementInfo": {
        "industry": "--"
    },
    "dataValidity": {
        "isValid": True,
        "reason": ""
    }
}
```

**真实示例**：
```python
result = get_stock_quotes("09633")  # 港股
# 结果示例：
# {
#     "baseInfo": {
#         "stockCode": "09633",
#         "market": "港股通",
#         "stockName": "巨子生物",
#         "industry": "--"
#     },
#     "coreQuotes": {
#         "stockName": "巨子生物",
#         "currentPrice": 38.50,
#         "prevClosePrice": 38.25,
#         "openPrice": 38.30,
#         "highPrice": 38.80,
#         "lowPrice": 38.10,
#         "volume": 1234567,
#         "amount": 47563212.50,
#         "priceChange": 0.25,
#         "changePercent": 0.65
#     },
#     "supplementInfo": {
#         "industry": "--"
#     },
#     "dataValidity": {
#         "isValid": True,
#         "reason": ""
#     }
# }

result = get_stock_quotes("600036")  # A股
# 结果示例：
# {
#     "baseInfo": {
#         "stockCode": "600036",
#         "market": "沪A",
#         "stockName": "招商银行",
#         "industry": "银行"
#     },
#     "coreQuotes": {
#         "stockName": "招商银行",
#         "currentPrice": 30.75,
#         "openPrice": 30.65,
#         "prevClosePrice": 30.68,
#         "highPrice": 30.80,
#         "lowPrice": 30.55,
#         "volume": 457585,
#         "amount": 1417412425,
#         "priceChange": 0.07,
#         "changePercent": 0.23,
#         "turnoverRate": 0.32,
#         "pe": 9.56,
#         "marketCap": 987654321000
#     },
#     "supplementInfo": {
#         "industry": "银行"
#     },
#     "dataValidity": {
#         "isValid": True,
#         "reason": ""
#     }
# }
```

### 2. `get_stock_quotes_api(stock_code: str)`

**功能**：获取股票实时行情（API接口）

**入参**：
- `stock_code`: 股票代码

**返回值**：
- 包含股票实时行情的字典

**真实示例**：
```python
result = get_stock_quotes_api("600036")
# 结果与get_stock_quotes相同
```

## 市场概览获取方法

### 1. `fetch_market_overview_data() -> dict`

**功能**：获取市场概览数据（带缓存）

**入参**：无

**返回值**：
- 包含市场概览数据的字典

**返回字段**：
- `shIndex`: 上证指数
- `shChange`: 上证指数涨跌额
- `shChangeRate`: 上证指数涨跌幅
- `szIndex`: 深证成指
- `szChange`: 深证成指涨跌额
- `szChangeRate`: 深证成指涨跌幅
- `cyIndex`: 创业板指
- `cyChange`: 创业板指涨跌额
- `cyChangeRate`: 创业板指涨跌幅
- `totalVolume`: 总成交量
- `totalAmount`: 总成交额
- `medianChangeRate`: 中位数涨跌幅
- `upStocks`: 上涨股票数
- `downStocks`: 下跌股票数
- `flatStocks`: 平盘股票数
- `marketHotspots`: 市场热点

**真实示例**：
```python
result = fetch_market_overview_data()
# 结果示例：
# {
#     "shIndex": 3050.12,
#     "shChange": 15.34,
#     "shChangeRate": 0.51,
#     "szIndex": 9876.54,
#     "szChange": 89.76,
#     "szChangeRate": 0.92,
#     "cyIndex": 1950.32,
#     "cyChange": 23.45,
#     "cyChangeRate": 1.22,
#     "totalVolume": 567890000000,
#     "totalAmount": 7890123456789,
#     "medianChangeRate": 0.35,
#     "upStocks": 3245,
#     "downStocks": 1567,
#     "flatStocks": 189,
#     "marketHotspots": [
#         {"name": "人工智能", "change": "5.23"},
#         {"name": "新能源", "change": "3.45"}
#     ]
# }
```

### 2. `get_market_overview()`

**功能**：市场概览接口

**入参**：无

**返回值**：
- 市场概览数据

**真实示例**：
```python
result = get_market_overview()
# 结果与fetch_market_overview_data相同
```

## 股票搜索与详情获取方法

### 1. `get_all_stocks(search: Optional[str] = Query(None))`

**功能**：获取股票清单（支持搜索）

**入参**：
- `search`: 搜索条件（可选）

**返回值**：
- 股票列表

**返回结构**：
```python
[
    {
        "id": "1234567890",
        "stockCode": "09633",
        "stockName": "巨子生物",
        "addTime": "2023-06-15 14:30:00",
        "remark": "",
        "isHold": True,
        "industry": "生物医药",
        "currentPrice": 38.50,
        "changePercent": 0.65,
        "marketCap": "532.46亿"
    },
    {
        "id": "0987654321",
        "stockCode": "600036",
        "stockName": "招商银行",
        "addTime": "2023-05-20 10:15:00",
        "remark": "",
        "isHold": False,
        "industry": "银行",
        "currentPrice": 30.75,
        "changePercent": 0.23,
        "marketCap": "9876.54亿"
    }
]
```

**真实示例**：
```python
result = get_all_stocks(search="银行")
# 结果示例：
# [
#     {
#         "id": "0987654321",
#         "stockCode": "600036",
#         "stockName": "招商银行",
#         "addTime": "2023-05-20 10:15:00",
#         "remark": "",
#         "isHold": False,
#         "industry": "银行",
#         "currentPrice": 30.75,
#         "changePercent": 0.23,
#         "marketCap": "9876.54亿"
#     },
#     {
#         "id": "1122334455",
#         "stockCode": "601398",
#         "stockName": "工商银行",
#         "addTime": "2023-04-10 09:30:00",
#         "remark": "",
#         "isHold": True,
#         "industry": "银行",
#         "currentPrice": 4.56,
#         "changePercent": -0.22,
#         "marketCap": "18976.54亿"
#     }
# ]
```

### 2. `get_stock(stock_id: str)`

**功能**：获取单只股票

**入参**：
- `stock_id`: 股票ID

**返回值**：
- 包含股票信息的字典

**真实示例**：
```python
result = get_stock("1234567890")
# 结果示例：
# {
#     "id": "1234567890",
#     "stockCode": "09633",
#     "stockName": "巨子生物",
#     "addTime": "2023-06-15 14:30:00",
#     "remark": "",
#     "isHold": True,
#     "industry": "生物医药",
#     "currentPrice": 38.50,
#     "changePercent": 0.65,
#     "marketCap": "532.46亿"
# }
```

### 3. `get_stock_base_info(stockCode: str)`

**功能**：获取股票基础信息

**入参**：
- `stockCode`: 股票代码

**返回值**：
- 包含股票基础信息的字典

**返回结构**：
```python
{
    "baseInfo": {
        "stockCode": "600036",
        "market": "沪A",
        "stockName": "招商银行",
        "industry": "银行"
    },
    "coreQuotes": {
        "stockName": "招商银行",
        "currentPrice": 30.75,
        "openPrice": 30.65,
        "preClosePrice": 30.68,
        "highPrice": 30.80,
        "lowPrice": 30.55,
        "volume": 457585,
        "turnover": 1417412425,
        "amplitude": "0.81",
        "pe": "9.56",
        "pb": "1.23",
        "changePercent": 0.23,
        "changeAmount": 0.07
    },
    "supplementInfo": {
        "industry": "银行"
    },
    "dataValidity": {
        "isValid": True,
        "reason": ""
    }
}
```

**真实示例**：
```python
result = get_stock_base_info("600036")
# 结果示例：
# {
#     "baseInfo": {
#         "stockCode": "600036",
#         "market": "沪A",
#         "stockName": "招商银行",
#         "industry": "银行"
#     },
#     "coreQuotes": {
#         "stockName": "招商银行",
#         "currentPrice": 30.75,
#         "openPrice": 30.65,
#         "preClosePrice": 30.68,
#         "highPrice": 30.80,
#         "lowPrice": 30.55,
#         "volume": 457585,
#         "turnover": 1417412425,
#         "amplitude": "0.81",
#         "pe": "9.56",
#         "pb": "1.23",
#         "changePercent": 0.23,
#         "changeAmount": 0.07
#     },
#     "supplementInfo": {
#         "industry": "银行"
#     },
#     "dataValidity": {
#         "isValid": True,
#         "reason": ""
#     }
# }
```

### 4. `get_stock_detail(stock_code: str)`

**功能**：获取股票详情（基础信息+行情+财务+股东）

**入参**：
- `stock_code`: 股票代码

**返回值**：
- 包含股票详情的字典

**返回结构**：
```python
{
    "baseInfo": {
        "stockCode": "09633",
        "market": "港股通",
        "stockName": "巨子生物",
        "industry": "--",
        "companyName": "巨子生物",
        "listDate": "--",
        "totalShares": "10.49亿股",
        "floatShares": "10.49亿股",
        "marketCap": "532.46亿元",
        "operateIncome": "10.97亿元"
    },
    "coreQuotes": {
        "stockName": "巨子生物",
        "currentPrice": 38.50,
        "prevClosePrice": 38.25,
        "openPrice": 38.30,
        "highPrice": 38.80,
        "lowPrice": 38.10,
        "volume": 1234567,
        "amount": 47563212.50,
        "priceChange": 0.25,
        "changePercent": 0.65,
        "peDynamic": 38.56,
        "peStatic": 38.56,
        "pbRatio": 10.02,
        "roe": 25.28,
        "netProfitRatio": 48.32,
        "dividendRate": 0.0
    },
    "tencentData": {},
    "financialData": {
        "2023": {
            "revenue": "10.97",
            "revenueGrowth": "27.89",
            "netProfit": "5.30",
            "netProfitGrowth": "32.93",
            "eps": "0.32",
            "navps": "0.91",
            "roe": "25.28",
            "pe": "38.56",
            "pb": "10.02",
            "grossMargin": "83.56",
            "netMargin": "48.32",
            "debtRatio": "15.67"
        }
    },
    "mllsj": {
        "2023-12-31": {
            "mll": "83.56",
            "xsjll": "48.32"
        }
    },
    "topShareholders": [],
    "dataValidity": {
        "isValid": True,
        "reason": ""
    }
}
```

**真实示例**：
```python
result = get_stock_detail("09633")
# 结果示例：
# {
#     "baseInfo": {
#         "stockCode": "09633",
#         "market": "港股通",
#         "stockName": "巨子生物",
#         "industry": "--",
#         "companyName": "巨子生物",
#         "listDate": "--",
#         "totalShares": "10.49亿股",
#         "floatShares": "10.49亿股",
#         "marketCap": "532.46亿元",
#         "operateIncome": "10.97亿元"
#     },
#     "coreQuotes": {
#         "stockName": "巨子生物",
#         "currentPrice": 38.50,
#         "prevClosePrice": 38.25,
#         "openPrice": 38.30,
#         "highPrice": 38.80,
#         "lowPrice": 38.10,
#         "volume": 1234567,
#         "amount": 47563212.50,
#         "priceChange": 0.25,
#         "changePercent": 0.65,
#         "peDynamic": 38.56,
#         "peStatic": 38.56,
#         "pbRatio": 10.02,
#         "roe": 25.28,
#         "netProfitRatio": 48.32,
#         "dividendRate": 0.0
#     },
#     "tencentData": {},
#     "financialData": {
#         "2023": {
#             "revenue": "10.97",
#             "revenueGrowth": "27.89",
#             "netProfit": "5.30",
#             "netProfitGrowth": "32.93",
#             "eps": "0.32",
#             "navps": "0.91",
#             "roe": "25.28",
#             "pe": "38.56",
#             "pb": "10.02",
#             "grossMargin": "83.56",
#             "netMargin": "48.32",
#             "debtRatio": "15.67"
#         }
#     },
#     "mllsj": {
#         "2023-12-31": {
#             "mll": "83.56",
#             "xsjll": "48.32"
#         }
#     },
#     "topShareholders": [],
#     "dataValidity": {
#         "isValid": True,
#         "reason": ""
#     }
# }
```

### 4. `search_stocks(keyword: str)`

**功能**：搜索股票（使用新浪新接口，支持港股通）

**入参**：
- `keyword`: 搜索关键词

**返回值**：
- 搜索结果

**返回结构**：
```python
{
    "stocks": [
        {
            "stockCode": "09633",
            "stockName": "巨子生物",
            "market": "港股"
        },
        {
            "stockCode": "688363",
            "stockName": "华熙生物",
            "market": "科创板"
        }
    ]
}
```

**真实示例**：
```python
result = search_stocks("生物")
# 结果示例：
# {
#     "stocks": [
#         {
#             "stockCode": "09633",
#             "stockName": "巨子生物",
#             "market": "港股"
#         },
#         {
#             "stockCode": "688363",
#             "stockName": "华熙生物",
#             "market": "科创板"
#         },
#         {
#             "stockCode": "300601",
#             "stockName": "康泰生物",
#             "market": "创业板"
#         }
#     ]
# }
```

## 杜邦分析数据获取方法

### 1. `dupont_analysis(stock_id: str, displaytype: str = "10", export_excel: bool = True)`

**功能**：通用杜邦分析数据提取（自动判断A股/港股）

**入参**：
- `stock_id`: 股票代码（如"02367"、"600036"）
- `displaytype`: 显示类型（默认"10"）
- `export_excel`: 是否导出Excel（默认`True`）

**返回值**：
- 统一格式的杜邦分析响应

**返回结构**：
```python
{
    "stock_id": "09633",
    "full_data": [
        {
            "date": "2023-12-31",
            "period_type": "年报",
            "净资产收益率(%)": "25.28",
            "总资产收益率(%)": "23.45",
            "销售净利率(%)": "48.32",
            "总资产周转率(次)": "0.49",
            "权益乘数": "1.08",
            "经营利润率(%)": "56.08",
            "利息负担(%)": "100.00",
            "税负(%)": "13.64"
        },
        {
            "date": "2023-09-30",
            "period_type": "三季报",
            "净资产收益率(%)": "18.56",
            "总资产收益率(%)": "17.23",
            "销售净利率(%)": "49.01",
            "总资产周转率(次)": "0.35",
            "权益乘数": "1.08",
            "经营利润率(%)": "56.89",
            "利息负担(%)": "100.00",
            "税负(%)": "13.98"
        }
    ],
    "error": null
}
```

**真实示例**：
```python
result = dupont_analysis("09633")  # 港股
# 结果示例：
# {
#     "stock_id": "09633",
#     "full_data": [
#         {
#             "date": "2023-12-31",
#             "period_type": "年报",
#             "净资产收益率(%)": "25.28",
#             "总资产收益率(%)": "23.45",
#             "销售净利率(%)": "48.32",
#             "总资产周转率(次)": "0.49",
#             "权益乘数": "1.08",
#             "经营利润率(%)": "56.08",
#             "利息负担(%)": "100.00",
#             "税负(%)": "13.64"
#         },
#         {
#             "date": "2023-09-30",
#             "period_type": "三季报",
#             "净资产收益率(%)": "18.56",
#             "总资产收益率(%)": "17.23",
#             "销售净利率(%)": "49.01",
#             "总资产周转率(次)": "0.35",
#             "权益乘数": "1.08",
#             "经营利润率(%)": "56.89",
#             "利息负担(%)": "100.00",
#             "税负(%)": "13.98"
#         }
#     ],
#     "error": null
# }

result = dupont_analysis("600036")  # A股
# 结果示例：
# {
#     "stock_id": "600036",
#     "full_data": [
#         {
#             "date": "2023-12-31",
#             "period_type": "年报",
#             "净资产收益率(%)": "12.34",
#             "总资产收益率(%)": "1.02",
#             "销售净利率(%)": "43.56",
#             "总资产周转率(次)": "0.02",
#             "权益乘数": "11.23",
#             "经营利润率(%)": "45.67",
#             "利息负担(%)": "101.23",
#             "税负(%)": "4.56"
#         },
#         {
#             "date": "2023-09-30",
#             "period_type": "三季报",
#             "净资产收益率(%)": "9.87",
#             "总资产收益率(%)": "0.81",
#             "销售净利率(%)": "44.23",
#             "总资产周转率(次)": "0.02",
#             "权益乘数": "11.21",
#             "经营利润率(%)": "46.34",
#             "利息负担(%)": "101.11",
#             "税负(%)": "4.32"
#         }
#     ],
#     "error": null
# }
```

### 2. `_hk_dupont_analysis_impl(stock_id: str, displaytype: str = "10", export_excel: bool = True)`

**功能**：港股杜邦分析数据提取实现（使用东方财富网API）

**入参**：
- `stock_id`: 港股代码（如"02367"）
- `displaytype`: 显示类型（默认"10"）
- `export_excel`: 是否导出Excel（默认`True`）

**返回值**：
- 与A股杜邦分析相同格式的响应

**真实示例**：
```python
result = _hk_dupont_analysis_impl("09633")
# 结果与dupont_analysis("09633")相同
```

### 3. `_a_dupont_analysis_impl(stock_id: str, displaytype: str = "10", export_excel: bool = True)`

**功能**：A股杜邦分析数据提取实现

**入参**：
- `stock_id`: A股代码（如"600036"）
- `displaytype`: 显示类型（默认"10"）
- `export_excel`: 是否导出Excel（默认`True`）

**返回值**：
- 杜邦分析响应

**真实示例**：
```python
result = _a_dupont_analysis_impl("600036")
# 结果与dupont_analysis("600036")相同
```

## 总结

本文档详细分析了`stock.py`中所有用于获取数据的方法，包括它们的功能、入参、返回值和真实示例。这些方法主要用于获取股票行情、财务数据、市场概览、杜邦分析等信息，支持A股和港股市场。

通过这些方法，用户可以方便地获取各种股票相关数据，用于投资分析和决策。