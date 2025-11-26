# 投资辅助系统数据库设计

## 1. 数据库整体架构

投资辅助系统采用混合数据库架构，结合关系型数据库(MySQL)和非关系型数据库(MongoDB)的优势：

- **MySQL**：存储结构化的业务数据，如用户信息、股票基本信息、行业分类等
- **MongoDB**：存储非结构化或半结构化的数据，如股票价格历史、财务报表详情、估值计算结果等
- **Redis**：缓存热点数据，提高系统响应速度

## 2. MySQL数据库设计

### 2.1 用户管理模块

#### 2.1.1 用户表 (users)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | VARCHAR(36) | PRIMARY KEY, DEFAULT(UUID()) | 用户唯一标识 |
| username | VARCHAR(50) | UNIQUE NOT NULL | 用户名 |
| email | VARCHAR(100) | UNIQUE NOT NULL | 邮箱地址 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希值 |
| phone | VARCHAR(20) | UNIQUE | 手机号码 |
| avatar | VARCHAR(255) | | 头像URL |
| nickname | VARCHAR(50) | | 昵称 |
| role | ENUM('admin', 'user', 'guest') | DEFAULT 'user' | 用户角色 |
| status | ENUM('active', 'inactive', 'locked') | DEFAULT 'active' | 账号状态 |
| last_login_at | DATETIME | | 最后登录时间 |
| created_at | DATETIME | NOT NULL, DEFAULT(NOW()) | 创建时间 |
| updated_at | DATETIME | NOT NULL, DEFAULT(NOW()) ON UPDATE NOW() | 更新时间 |

**索引**：
- 唯一索引: `idx_username`, `idx_email`, `idx_phone`
- 普通索引: `idx_created_at`, `idx_status`

#### 2.1.2 用户偏好设置表 (user_preferences)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | VARCHAR(36) | PRIMARY KEY, DEFAULT(UUID()) | 设置ID |
| user_id | VARCHAR(36) | NOT NULL, FOREIGN KEY REFERENCES users(id) | 用户ID |
| theme | ENUM('light', 'dark', 'auto') | DEFAULT 'light' | 界面主题 |
| language | VARCHAR(10) | DEFAULT 'zh-CN' | 语言设置 |
| default_market | VARCHAR(20) | DEFAULT 'SH' | 默认市场 |
| favorite_stocks | JSON | | 收藏的股票列表 |
| notification_settings | JSON | | 通知设置 |
| created_at | DATETIME | NOT NULL, DEFAULT(NOW()) | 创建时间 |
| updated_at | DATETIME | NOT NULL, DEFAULT(NOW()) ON UPDATE NOW() | 更新时间 |

**索引**：
- 外键索引: `idx_user_id`

### 2.2 股票基础信息模块

#### 2.2.1 行业分类表 (industries)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| code | VARCHAR(20) | PRIMARY KEY | 行业代码 |
| name | VARCHAR(50) | NOT NULL | 行业名称 |
| parent_code | VARCHAR(20) | FOREIGN KEY REFERENCES industries(code) | 父行业代码 |
| level | TINYINT | NOT NULL DEFAULT 1 | 行业级别(1-4) |
| description | TEXT | | 行业描述 |
| icon | VARCHAR(255) | | 行业图标 |
| created_at | DATETIME | NOT NULL, DEFAULT(NOW()) | 创建时间 |
| updated_at | DATETIME | NOT NULL, DEFAULT(NOW()) ON UPDATE NOW() | 更新时间 |

**索引**：
- 外键索引: `idx_parent_code`
- 普通索引: `idx_level`

#### 2.2.2 板块分类表 (sectors)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| code | VARCHAR(20) | PRIMARY KEY | 板块代码 |
| name | VARCHAR(50) | NOT NULL | 板块名称 |
| type | ENUM('concept', 'region', 'theme') | NOT NULL | 板块类型 |
| description | TEXT | | 板块描述 |
| created_at | DATETIME | NOT NULL, DEFAULT(NOW()) | 创建时间 |
| updated_at | DATETIME | NOT NULL, DEFAULT(NOW()) ON UPDATE NOW() | 更新时间 |

**索引**：
- 普通索引: `idx_type`

#### 2.2.3 股票基本信息表 (stocks)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | VARCHAR(36) | PRIMARY KEY, DEFAULT(UUID()) | 股票ID |
| code | VARCHAR(20) | UNIQUE NOT NULL | 股票代码 |
| name | VARCHAR(50) | NOT NULL | 股票名称 |
| market | ENUM('SH', 'SZ', 'BJ', 'HK', 'US') | NOT NULL | 所属市场 |
| full_code | VARCHAR(30) | UNIQUE NOT NULL | 带市场标识的完整代码 |
| industry_code | VARCHAR(20) | NOT NULL, FOREIGN KEY REFERENCES industries(code) | 所属行业代码 |
| listing_date | DATE | | 上市日期 |
| delisting_date | DATE | | 退市日期 |
| status | ENUM('listing', 'delisting', 'suspended') | DEFAULT 'listing' | 股票状态 |
| total_shares | DECIMAL(20,4) | | 总股本(万股) |
| circulation_shares | DECIMAL(20,4) | | 流通股本(万股) |
| company_name | VARCHAR(100) | | 公司全称 |
| company_website | VARCHAR(255) | | 公司网站 |
| business_scope | TEXT | | 经营范围 |
| headquarters | VARCHAR(100) | | 总部地址 |
| latest_price | DECIMAL(10,2) | | 最新价格 |
| created_at | DATETIME | NOT NULL, DEFAULT(NOW()) | 创建时间 |
| updated_at | DATETIME | NOT NULL, DEFAULT(NOW()) ON UPDATE NOW() | 更新时间 |

**索引**：
- 唯一索引: `idx_code`, `idx_full_code`
- 外键索引: `idx_industry_code`
- 普通索引: `idx_market`, `idx_status`

#### 2.2.4 股票板块关联表 (stock_sectors)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | VARCHAR(36) | PRIMARY KEY, DEFAULT(UUID()) | 关联ID |
| stock_id | VARCHAR(36) | NOT NULL, FOREIGN KEY REFERENCES stocks(id) | 股票ID |
| sector_code | VARCHAR(20) | NOT NULL, FOREIGN KEY REFERENCES sectors(code) | 板块代码 |
| created_at | DATETIME | NOT NULL, DEFAULT(NOW()) | 创建时间 |

**索引**：
- 外键索引: `idx_stock_id`, `idx_sector_code`
- 联合索引: `idx_stock_sector` (stock_id, sector_code)

### 2.3 系统配置模块

#### 2.3.1 系统配置表 (system_configs)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | VARCHAR(36) | PRIMARY KEY, DEFAULT(UUID()) | 配置ID |
| key | VARCHAR(100) | UNIQUE NOT NULL | 配置键名 |
| value | TEXT | NOT NULL | 配置值(JSON格式) |
| type | VARCHAR(50) | NOT NULL | 配置类型 |
| description | VARCHAR(255) | | 配置描述 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用 |
| created_at | DATETIME | NOT NULL, DEFAULT(NOW()) | 创建时间 |
| updated_at | DATETIME | NOT NULL, DEFAULT(NOW()) ON UPDATE NOW() | 更新时间 |

**索引**：
- 唯一索引: `idx_key`
- 普通索引: `idx_type`, `idx_is_active`

#### 2.3.2 数据源配置表 (data_sources)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | VARCHAR(36) | PRIMARY KEY, DEFAULT(UUID()) | 数据源ID |
| name | VARCHAR(100) | NOT NULL | 数据源名称 |
| type | ENUM('market', 'financial', 'valuation', 'news') | NOT NULL | 数据类型 |
| url | VARCHAR(255) | | API URL |
| api_key | VARCHAR(255) | | API密钥 |
| refresh_rate | INT | NOT NULL DEFAULT 3600 | 刷新频率(秒) |
| status | ENUM('active', 'inactive', 'error') | DEFAULT 'active' | 数据源状态 |
| last_sync_at | DATETIME | | 最后同步时间 |
| created_at | DATETIME | NOT NULL, DEFAULT(NOW()) | 创建时间 |
| updated_at | DATETIME | NOT NULL, DEFAULT(NOW()) ON UPDATE NOW() | 更新时间 |

**索引**：
- 普通索引: `idx_type`, `idx_status`

### 2.4 历史记录模块

#### 2.4.1 用户浏览记录表 (user_browsing_history)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | VARCHAR(36) | PRIMARY KEY, DEFAULT(UUID()) | 记录ID |
| user_id | VARCHAR(36) | NOT NULL, FOREIGN KEY REFERENCES users(id) | 用户ID |
| stock_id | VARCHAR(36) | NOT NULL, FOREIGN KEY REFERENCES stocks(id) | 股票ID |
| page_type | VARCHAR(50) | NOT NULL | 页面类型 |
| browse_at | DATETIME | NOT NULL, DEFAULT(NOW()) | 浏览时间 |

**索引**：
- 外键索引: `idx_user_id`, `idx_stock_id`
- 联合索引: `idx_user_stock` (user_id, stock_id)
- 普通索引: `idx_browse_at`

#### 2.4.2 搜索历史记录表 (search_history)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | VARCHAR(36) | PRIMARY KEY, DEFAULT(UUID()) | 记录ID |
| user_id | VARCHAR(36) | NOT NULL, FOREIGN KEY REFERENCES users(id) | 用户ID |
| keyword | VARCHAR(255) | NOT NULL | 搜索关键词 |
| search_type | VARCHAR(50) | NOT NULL | 搜索类型 |
| search_at | DATETIME | NOT NULL, DEFAULT(NOW()) | 搜索时间 |

**索引**：
- 外键索引: `idx_user_id`
- 全文索引: `idx_keyword` (keyword)
- 普通索引: `idx_search_at`

## 3. MongoDB数据库设计

### 3.1 市场数据集合

#### 3.1.1 股票价格历史集合 (stock_prices)

**文档结构**:
```javascript
{
  "_id": ObjectId("6467c48e9d31a0a4d7c6f341"),
  "stockCode": "600519",
  "market": "SH",
  "date": ISODate("2024-01-01T00:00:00.000Z"),
  "open": 1800.00,
  "high": 1825.00,
  "low": 1795.00,
  "close": 1823.00,
  "volume": 123456789,
  "amount": 22567890123.45,
  "change": 18.23,
  "changePercent": 1.01,
  "turnoverRate": 0.52,
  "createdAt": ISODate("2024-01-01T15:00:00.000Z"),
  "updatedAt": ISODate("2024-01-01T15:00:00.000Z")
}
```

**索引**:
- 复合索引: `{ stockCode: 1, date: 1 }` (唯一)
- 普通索引: `{ date: 1 }`, `{ market: 1 }`

#### 3.1.2 指数价格历史集合 (index_prices)

**文档结构**:
```javascript
{
  "_id": ObjectId("6467c48e9d31a0a4d7c6f342"),
  "indexCode": "000001.SH",
  "indexName": "上证指数",
  "date": ISODate("2024-01-01T00:00:00.000Z"),
  "open": 3075.56,
  "high": 3098.76,
  "low": 3071.23,
  "close": 3087.24,
  "volume": 28000000000,
  "amount": 325000000000,
  "change": 15.32,
  "changePercent": 0.50,
  "createdAt": ISODate("2024-01-01T15:00:00.000Z"),
  "updatedAt": ISODate("2024-01-01T15:00:00.000Z")
}
```

**索引**:
- 复合索引: `{ indexCode: 1, date: 1 }` (唯一)
- 普通索引: `{ date: 1 }`

#### 3.1.3 行业估值集合 (industry_valuations)

**文档结构**:
```javascript
{
  "_id": ObjectId("6467c48e9d31a0a4d7c6f343"),
  "industryCode": "bank",
  "industryName": "银行业",
  "date": ISODate("2024-01-01T00:00:00.000Z"),
  "pe": 5.8,
  "peChange": -2.3,
  "pePercentile": 15,
  "pb": 0.65,
  "pbChange": -1.5,
  "pbPercentile": 10,
  "ps": 0.98,
  "psChange": 0.5,
  "psPercentile": 20,
  "pcf": 4.5,
  "pcfChange": -1.2,
  "pcfPercentile": 12,
  "totalMarketCap": 12345678900000,
  "stockCount": 42,
  "createdAt": ISODate("2024-01-01T15:00:00.000Z"),
  "updatedAt": ISODate("2024-01-01T15:00:00.000Z")
}
```

**索引**:
- 复合索引: `{ industryCode: 1, date: 1 }` (唯一)
- 普通索引: `{ date: 1 }`

#### 3.1.4 资金流向集合 (fund_flows)

**文档结构**:
```javascript
{
  "_id": ObjectId("6467c48e9d31a0a4d7c6f344"),
  "stockCode": "600519",
  "date": ISODate("2024-01-01T00:00:00.000Z"),
  "mainInflow": 1234567890.12,
  "mainOutflow": 987654321.34,
  "mainNetFlow": 246913568.78,
  "mainRatio": 0.25,
  "largeInflow": 5678901234.56,
  "largeOutflow": 4567890123.45,
  "largeNetFlow": 1111011111.11,
  "mediumInflow": 3456789012.34,
  "mediumOutflow": 2345678901.23,
  "mediumNetFlow": 1111110111.11,
  "smallInflow": 2345678901.23,
  "smallOutflow": 3456789012.34,
  "smallNetFlow": -1111110111.11,
  "totalVolume": 12345678901.23,
  "createdAt": ISODate("2024-01-01T15:00:00.000Z"),
  "updatedAt": ISODate("2024-01-01T15:00:00.000Z")
}
```

**索引**:
- 复合索引: `{ stockCode: 1, date: 1 }` (唯一)
- 普通索引: `{ date: 1 }`, `{ mainNetFlow: -1 }`

### 3.2 财务数据集合

#### 3.2.1 财务指标集合 (financial_indicators)

**文档结构**:
```javascript
{
  "_id": ObjectId("6467c48e9d31a0a4d7c6f345"),
  "stockCode": "600519",
  "reportDate": "2023-12-31",
  "reportType": "annual", // annual, quarterly, semi-annual
  "publishDate": ISODate("2024-03-31T00:00:00.000Z"),
  
  // 盈利能力指标
  "profitability": {
    "revenue": 1062750000000,
    "revenueYoY": 16.85,
    "netProfit": 484220000000,
    "netProfitYoY": 19.49,
    "grossMargin": 91.87,
    "netMargin": 45.56,
    "roe": 31.25,
    "roa": 26.54,
    "operatingProfit": 523450000000,
    "operatingMargin": 49.25
  },
  
  // 成长能力指标
  "growth": {
    "revenueGrowthRate3Y": 15.67,
    "profitGrowthRate3Y": 18.23,
    "assetGrowthRate": 12.34,
    "equityGrowthRate": 14.56
  },
  
  // 偿债能力指标
  "solvency": {
    "debtRatio": 17.68,
    "debtToEquityRatio": 21.48,
    "currentRatio": 3.45,
    "quickRatio": 3.21,
    "interestCoverageRatio": 56.78
  },
  
  // 运营能力指标
  "operation": {
    "assetTurnover": 0.59,
    "inventoryTurnover": 18.92,
    "accountsReceivableTurnover": 25.34,
    "cashCycle": 12.34
  },
  
  // 现金流指标
  "cashFlow": {
    "operatingCashFlow": 123450000000,
    "investingCashFlow": -56780000000,
    "financingCashFlow": -67890000000,
    "freeCashFlow": 66560000000,
    "cashFlowToRevenue": 11.61,
    "cashFlowToProfit": 25.49
  },
  
  "createdAt": ISODate("2024-03-31T15:00:00.000Z"),
  "updatedAt": ISODate("2024-03-31T15:00:00.000Z")
}
```

**索引**:
- 复合索引: `{ stockCode: 1, reportDate: 1 }` (唯一)
- 普通索引: `{ reportType: 1 }`, `{ publishDate: -1 }`

#### 3.2.2 资产负债表集合 (balance_sheets)

**文档结构**:
```javascript
{
  "_id": ObjectId("6467c48e9d31a0a4d7c6f346"),
  "stockCode": "600519",
  "reportDate": "2023-12-31",
  "reportType": "annual",
  
  // 资产部分
  "assets": {
    "currentAssets": {
      "cash": 135678000000,
      "shortTermInvestments": 23456000000,
      "accountsReceivable": 4567000000,
      "inventory": 325678000000,
      "prepaidExpenses": 12345000000,
      "otherCurrentAssets": 89012000000,
      "total": 601849000000
    },
    "nonCurrentAssets": {
      "propertyPlantEquipment": 287654000000,
      "intangibleAssets": 45678000000,
      "goodwill": 12345000000,
      "longTermInvestments": 1023456000000,
      "deferredTaxAssets": 15678000000,
      "otherNonCurrentAssets": 78901000000,
      "total": 1536059000000
    },
    "total": 2137908000000
  },
  
  // 负债部分
  "liabilities": {
    "currentLiabilities": {
      "shortTermDebt": 0,
      "accountsPayable": 123456000000,
      "accruedExpenses": 45678000000,
      "otherCurrentLiabilities": 34567000000,
      "total": 203691000000
    },
    "nonCurrentLiabilities": {
      "longTermDebt": 123456000000,
      "deferredTaxLiabilities": 50198000000,
      "otherNonCurrentLiabilities": 0,
      "total": 173654000000
    },
    "total": 377345000000
  },
  
  // 股东权益
  "equity": {
    "shareCapital": 125678000000,
    "additionalPaidInCapital": 0,
    "retainedEarnings": 1623456000000,
    "treasuryStock": 0,
    "otherComprehensiveIncome": 8000000000,
    "total": 1757134000000
  },
  
  "createdAt": ISODate("2024-03-31T15:00:00.000Z"),
  "updatedAt": ISODate("2024-03-31T15:00:00.000Z")
}
```

**索引**:
- 复合索引: `{ stockCode: 1, reportDate: 1 }` (唯一)
- 普通索引: `{ reportType: 1 }`

#### 3.2.3 利润表集合 (income_statements)

**文档结构**:
```javascript
{
  "_id": ObjectId("6467c48e9d31a0a4d7c6f347"),
  "stockCode": "600519",
  "reportDate": "2023-12-31",
  "reportType": "annual",
  
  // 收入部分
  "revenue": {
    "operatingRevenue": 1062750000000,
    "otherRevenue": 12345000000,
    "total": 1075095000000
  },
  
  // 成本部分
  "costs": {
    "costOfGoodsSold": 87985000000,
    "sellingExpenses": 87654000000,
    "administrativeExpenses": 45678000000,
    "researchDevelopment": 23456000000,
    "financialExpenses": -5678000000,
    "otherExpenses": 12345000000,
    "total": 245430000000
  },
  
  // 利润部分
  "profits": {
    "grossProfit": 974840000000,
    "operatingProfit": 523450000000,
    "profitBeforeTax": 512345000000,
    "incomeTax": 28125000000,
    "netProfit": 484220000000,
    "profitAttributableToShareholders": 484220000000,
    "otherComprehensiveIncome": 8000000000,
    "totalComprehensiveIncome": 492220000000
  },
  
  // 每股指标
  "perShare": {
    "epsBasic": 48.42,
    "epsDiluted": 48.42,
    "dividendPerShare": 25.14,
    "bookValuePerShare": 175.71
  },
  
  "createdAt": ISODate("2024-03-31T15:00:00.000Z"),
  "updatedAt": ISODate("2024-03-31T15:00:00.000Z")
}
```

**索引**:
- 复合索引: `{ stockCode: 1, reportDate: 1 }` (唯一)
- 普通索引: `{ reportType: 1 }`

#### 3.2.4 现金流量表集合 (cash_flow_statements)

**文档结构**:
```javascript
{
  "_id": ObjectId("6467c48e9d31a0a4d7c6f348"),
  "stockCode": "600519",
  "reportDate": "2023-12-31",
  "reportType": "annual",
  
  // 经营活动现金流
  "operatingActivities": {
    "netIncome": 484220000000,
    "depreciationAmortization": 23456000000,
    "changeInWorkingCapital": -345670000000,
    "otherAdjustments": 12345000000,
    "netCashFlow": 123450000000
  },
  
  // 投资活动现金流
  "investingActivities": {
    "purchaseOfPPE": -34567000000,
    "proceedsFromSaleOfPPE": 1234000000,
    "acquisitions": -23456000000,
    "proceedsFromDisposals": 0,
    "investmentsInSecurities": -56789000000,
    "proceedsFromSecurities": 61234000000,
    "otherInvestingActivities": 0,
    "netCashFlow": -56780000000
  },
  
  // 筹资活动现金流
  "financingActivities": {
    "proceedsFromDebt": 0,
    "repaymentOfDebt": 0,
    "proceedsFromEquity": 0,
    "dividendsPaid": -67890000000,
    "shareRepurchases": 0,
    "otherFinancingActivities": 0,
    "netCashFlow": -67890000000
  },
  
  // 现金余额变化
  "cashChange": {
    "netIncreaseDecrease": -1220000000,
    "cashAtBeginning": 136898000000,
    "cashAtEnd": 135678000000
  },
  
  "createdAt": ISODate("2024-03-31T15:00:00.000Z"),
  "updatedAt": ISODate("2024-03-31T15:00:00.000Z")
}
```

**索引**:
- 复合索引: `{ stockCode: 1, reportDate: 1 }` (唯一)
- 普通索引: `{ reportType: 1 }`

### 3.3 估值数据集合

#### 3.3.1 股票估值集合 (stock_valuations)

**文档结构**:
```javascript
{
  "_id": ObjectId("6467c48e9d31a0a4d7c6f349"),
  "stockCode": "600519",
  "date": ISODate("2024-01-01T00:00:00.000Z"),
  "price": 1823.00,
  
  // 估值指标
  "valuationMetrics": {
    "pe": 25.6,
    "peTtm": 24.8,
    "pb": 9.8,
    "pbLf": 9.5,
    "ps": 13.2,
    "psTtm": 12.8,
    "pcf": 18.5,
    "pcfTtm": 17.9,
    "evToRevenue": 14.5,
    "evToEbitda": 20.5,
    "evToEbit": 22.3,
    "dividendYield": 1.38,
    "pegRatio": 1.41
  },
  
  // 估值历史分位
  "percentiles": {
    "pePercentile3Y": 75,
    "pePercentile5Y": 80,
    "pePercentile10Y": 85,
    "pbPercentile3Y": 70,
    "pbPercentile5Y": 75,
    "pbPercentile10Y": 80,
    "psPercentile3Y": 65,
    "psPercentile5Y": 70,
    "psPercentile10Y": 75
  },
  
  // 估值模型结果
  "models": {
    "dcfValue": 1987.65,
    "dcfPercentDiff": 8.98,
    "peValuation": 2016.54,
    "pePercentDiff": 10.62,
    "pbValuation": 1798.32,
    "pbPercentDiff": -1.35,
    "avgValuation": 1934.17,
    "avgPercentDiff": 6.09,
    "finalValuation": "undervalued" // undervalued, fair, overvalued
  },
  
  "createdAt": ISODate("2024-01-01T15:00:00.000Z"),
  "updatedAt": ISODate("2024-01-01T15:00:00.000Z")
}
```

**索引**:
- 复合索引: `{ stockCode: 1, date: 1 }` (唯一)
- 普通索引: `{ date: 1 }`, `{ models.finalValuation: 1 }`

#### 3.3.2 综合评分集合 (comprehensive_scores)

**文档结构**:
```javascript
{
  "_id": ObjectId("6467c48e9d31a0a4d7c6f350"),
  "stockCode": "600519",
  "date": ISODate("2024-01-01T00:00:00.000Z"),
  
  // 各项评分
  "scores": {
    "fundamental": 95,
    "growth": 88,
    "valuation": 75,
    "technical": 82,
    "quality": 92,
    "risk": 85,
    "sentiment": 80,
    "total": 85
  },
  
  // 评分详情
  "details": {
    "fundamental": {
      "profitability": 95,
      "solvency": 92,
      "operation": 98
    },
    "growth": {
      "revenueGrowth": 85,
      "profitGrowth": 90,
      "industryComparison": 89
    },
    "valuation": {
      "peScore": 70,
      "pbScore": 75,
      "psScore": 80,
      "percentileScore": 75
    },
    "technical": {
      "trend": 85,
      "momentum": 80,
      "volume": 81
    }
  },
  
  // 投资建议
  "investment": {
    "suggestion": "强烈买入", // 强烈买入, 买入, 持有, 卖出, 强烈卖出
    "confidence": 90,
    "targetPrice": 2050.00,
    "upside": 12.45,
    "timeHorizon": "1Y"
  },
  
  "createdAt": ISODate("2024-01-01T15:00:00.000Z"),
  "updatedAt": ISODate("2024-01-01T15:00:00.000Z")
}
```

**索引**:
- 复合索引: `{ stockCode: 1, date: 1 }` (唯一)
- 普通索引: `{ date: 1 }`, `{ scores.total: -1 }`, `{ investment.suggestion: 1 }`

## 4. Redis缓存设计

### 4.1 缓存策略

- **热点数据缓存**: 市场指数、热门股票、行业估值等高频访问数据
- **会话缓存**: 用户会话信息、权限数据
- **限流缓存**: API访问频率限制
- **临时计算结果缓存**: 复杂计算的中间结果

### 4.2 缓存键命名规范

```
{业务模块}:{数据类型}:{唯一标识}:{版本}
```

### 4.3 主要缓存键设计

| 缓存键 | 类型 | 过期时间 | 说明 |
|-------|------|---------|------|
| `market:index:latest` | Hash | 5分钟 | 最新市场指数数据 |
| `stock:{code}:quote` | Hash | 1分钟 | 股票实时行情 |
| `industry:valuations:latest` | Hash | 1小时 | 最新行业估值数据 |
| `user:{userId}:session` | Hash | 1小时 | 用户会话信息 |
| `user:{userId}:permissions` | Set | 1小时 | 用户权限集合 |
| `api:limit:{ip}:{path}` | String | 1分钟 | API限流计数器 |
| `search:hot:keywords` | List | 30分钟 | 热门搜索关键词 |
| `valuation:cache:{stockCode}` | String | 24小时 | 估值计算结果缓存 |

## 5. 数据库优化策略

### 5.1 MySQL优化

1. **索引优化**
   - 为频繁查询的字段创建索引
   - 避免在频繁更新的字段上创建索引
   - 使用复合索引替代单列索引
   - 定期分析和优化索引

2. **查询优化**
   - 使用EXPLAIN分析执行计划
   - 避免SELECT * 查询
   - 合理使用JOIN，避免过多JOIN
   - 分页查询优化
   - 使用LIMIT限制结果集大小

3. **表结构优化**
   - 选择合适的数据类型
   - 避免使用TEXT/BLOB类型
   - 适当反范式设计提高性能
   - 定期维护表结构

### 5.2 MongoDB优化

1. **索引优化**
   - 创建合适的复合索引
   - 使用TTL索引管理过期数据
   - 避免过多索引

2. **查询优化**
   - 使用投影减少返回字段
   - 合理使用聚合管道
   - 避免全集合扫描

3. **数据模型优化**
   - 根据查询模式设计数据模型
   - 适当数据冗余减少JOIN操作
   - 使用内嵌文档提高查询效率

### 5.3 缓存优化

1. **缓存命中率提升**
   - 合理设置缓存过期时间
   - 使用缓存预热机制
   - 实现缓存穿透保护

2. **缓存一致性维护**
   - 写操作后更新或删除缓存
   - 使用消息队列保证缓存异步更新
   - 实现缓存版本控制

## 6. 数据同步与备份策略

### 6.1 数据同步

- **实时同步**: 股票行情、市场数据使用WebSocket实时推送
- **准实时同步**: 财务数据、估值数据每小时更新
- **定时同步**: 历史数据、统计数据每日更新
- **增量同步**: 仅同步变更数据，减少网络传输

### 6.2 数据备份

- **MySQL备份**:
  - 全量备份: 每日凌晨执行
  - 增量备份: 每小时执行
  - 备份保留策略: 7天全量+30天增量

- **MongoDB备份**:
  - 逻辑备份: 每日执行mongodump
  - 时间点恢复: 配置oplog
  - 备份保留策略: 7天备份

- **备份验证**:
  - 定期恢复测试
  - 备份完整性检查

### 6.3 高可用设计

- **MySQL主从复制**: 一主多从架构
- **MongoDB副本集**: 至少3节点副本集
- **Redis集群**: 主从+哨兵模式
- **数据分片**: 对大数据集合实施分片策略

## 7. 数据库安全策略

### 7.1 访问控制

- **最小权限原则**: 只授予必要的权限
- **角色分离**: 不同用户分配不同角色
- **定期权限审计**: 定期检查权限设置

### 7.2 数据加密

- **传输加密**: 所有数据库连接使用SSL/TLS
- **存储加密**: 敏感数据加密存储
- **密钥管理**: 定期轮换加密密钥

### 7.3 审计与监控

- **操作审计**: 记录所有数据库操作
- **异常监控**: 实时监控异常访问
- **性能监控**: 监控数据库性能指标

## 8. 未来扩展考虑

### 8.1 数据量扩展

- **分库分表**: 按时间或股票代码范围分库分表
- **读写分离**: 主库写，从库读
- **垂直拆分**: 按业务模块拆分数据库

### 8.2 功能扩展

- **时序数据库**: 考虑引入InfluxDB存储时序行情数据
- **全文搜索**: 引入Elasticsearch支持高级搜索功能
- **图数据库**: 引入Neo4j支持复杂关系分析

### 8.3 性能扩展

- **数据库集群**: 部署多节点集群
- **分布式缓存**: 扩展Redis集群
- **数据预计算**: 定期预计算常用统计数据