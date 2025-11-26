# 投资辅助系统后端服务架构设计

## 1. 架构概述

投资辅助系统后端采用微服务架构，基于Node.js + NestJS框架构建，提供高内聚、低耦合的服务模块，支持系统的可扩展性和维护性。后端服务主要包括数据采集、数据处理、API网关、业务服务和认证授权等核心组件。

## 2. 技术栈选择

- **核心框架**: NestJS (Node.js)
- **数据库**: MongoDB (非结构化数据), MySQL (结构化数据)
- **缓存**: Redis
- **消息队列**: RabbitMQ
- **认证授权**: JWT (JSON Web Token)
- **API文档**: Swagger
- **日志系统**: Winston + ELK Stack
- **监控**: Prometheus + Grafana

## 3. 微服务划分

### 3.1 服务列表

| 服务名称 | 服务ID | 主要职责 | 技术栈 |
|---------|--------|---------|--------|
| API网关服务 | gateway-service | 请求路由、负载均衡、限流 | NestJS + Express |
| 用户认证服务 | auth-service | 用户注册、登录、权限管理 | NestJS + JWT |
| 数据采集服务 | data-collector | 爬虫引擎、数据抓取 | NestJS + Puppeteer |
| 数据处理服务 | data-processor | 数据清洗、转换、存储 | NestJS + TypeORM |
| 行业分析服务 | industry-service | 行业估值分析、行业对比 | NestJS + ECharts |
| 市场数据服务 | market-service | 市场指数、热点股票、资金流向 | NestJS + Redis |
| 财务分析服务 | financial-service | 财务指标计算、财务评分 | NestJS + MathJS |
| 估值决策服务 | valuation-service | DCF估值、相对估值、综合评分 | NestJS |
| 通知服务 | notification-service | 系统通知、邮件发送 | NestJS + Nodemailer |

### 3.2 服务间通信

- **同步通信**: REST API (使用Axios)
- **异步通信**: RabbitMQ消息队列
- **服务发现**: Consul

## 4. API接口规范

### 4.1 接口设计原则

- **RESTful规范**: 遵循REST设计风格
- **版本控制**: `/api/v1/` 形式的版本号
- **统一响应格式**: 标准的JSON响应结构
- **错误处理**: 统一的错误码和错误信息

### 4.2 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { /* 业务数据 */ },
  "timestamp": 1633046400000
}
```

### 4.3 错误码规范

| 错误码 | 描述 | HTTP状态码 |
|-------|------|-----------|
| 200 | 成功 | 200 |
| 400 | 请求参数错误 | 400 |
| 401 | 未授权 | 401 |
| 403 | 禁止访问 | 403 |
| 404 | 资源不存在 | 404 |
| 500 | 服务器内部错误 | 500 |
| 503 | 服务不可用 | 503 |

## 5. API接口详细设计

### 5.1 用户认证服务接口

#### 5.1.1 用户注册

- **URL**: `/api/v1/auth/register`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "注册成功",
    "data": {
      "userId": "string",
      "username": "string",
      "email": "string"
    }
  }
  ```

#### 5.1.2 用户登录

- **URL**: `/api/v1/auth/login`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": {
      "token": "string",
      "userId": "string",
      "username": "string",
      "expiresIn": 3600
    }
  }
  ```

### 5.2 行业分析服务接口

#### 5.2.1 获取行业列表

- **URL**: `/api/v1/industry/list`
- **方法**: `GET`
- **参数**: 无
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": [
      {
        "code": "bank",
        "name": "银行业"
      },
      {
        "code": "tech",
        "name": "科技业"
      }
    ]
  }
  ```

#### 5.2.2 获取行业估值

- **URL**: `/api/v1/industry/valuation/:code`
- **方法**: `GET`
- **参数**:
  - `code`: 行业代码
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "industryCode": "bank",
      "industryName": "银行业",
      "pe": 5.8,
      "pb": 0.65,
      "peChange": -2.3,
      "pbChange": -1.5,
      "pePercentile": 15,
      "pbPercentile": 10
    }
  }
  ```

### 5.3 市场数据服务接口

#### 5.3.1 获取市场指数

- **URL**: `/api/v1/market/indices`
- **方法**: `GET`
- **参数**: 无
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": [
      {
        "code": "000001.SH",
        "name": "上证指数",
        "price": 3087.24,
        "change": 15.32,
        "changePercent": 0.50,
        "volume": 28000000000
      }
    ]
  }
  ```

#### 5.3.2 获取热点股票

- **URL**: `/api/v1/market/hot-stocks`
- **方法**: `GET`
- **参数**:
  - `type`: `up`(涨幅榜), `down`(跌幅榜), `turnover`(换手率榜)
  - `limit`: 数量限制
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": [
      {
        "name": "贵州茅台",
        "code": "600519",
        "price": 1823.00,
        "change": 18.23,
        "changePercent": 1.01,
        "volume": 123.45,
        "amount": 225678.90
      }
    ]
  }
  ```

### 5.4 财务分析服务接口

#### 5.4.1 获取股票财务指标

- **URL**: `/api/v1/financial/indicators/:stockCode`
- **方法**: `GET`
- **参数**:
  - `stockCode`: 股票代码
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "stockCode": "600519",
      "indicators": {
        "revenue": 1062.75,
        "revenueYoY": 16.85,
        "netProfit": 484.22,
        "netProfitYoY": 19.49,
        "grossMargin": 91.87,
        "netMargin": 45.56,
        "roe": 31.25
      }
    }
  }
  ```

#### 5.4.2 获取资产负债表

- **URL**: `/api/v1/financial/balance-sheet/:stockCode`
- **方法**: `GET`
- **参数**:
  - `stockCode`: 股票代码
  - `period`: 报告期间
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": [
      {
        "item": "货币资金",
        "latest": 1356.78,
        "previous": 1234.56,
        "yearAgo": 1123.45,
        "yoyChange": 20.76
      }
    ]
  }
  ```

### 5.5 估值决策服务接口

#### 5.5.1 DCF估值计算

- **URL**: `/api/v1/valuation/dcf`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "stockCode": "600519",
    "forecastYears": 5,
    "growthRate": 15,
    "discountRate": 9,
    "terminalGrowthRate": 2.5
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "enterpriseValue": 1234567890000,
      "equityValue": 1234567890000,
      "perShareValue": 1987.65,
      "percentDiff": 8.98,
      "valuation": "undervalued"
    }
  }
  ```

#### 5.5.2 获取综合评分

- **URL**: `/api/v1/valuation/score/:stockCode`
- **方法**: `GET`
- **参数**:
  - `stockCode`: 股票代码
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "stockCode": "600519",
      "fundamental": 95,
      "growth": 88,
      "valuation": 75,
      "technical": 82,
      "total": 85,
      "suggestion": "强烈买入"
    }
  }
  ```

## 6. 数据库设计

### 6.1 主数据库 (MySQL)

#### 6.1.1 用户表 (users)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 用户ID |
| username | VARCHAR(50) | UNIQUE NOT NULL | 用户名 |
| email | VARCHAR(100) | UNIQUE NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | 哈希后的密码 |
| phone | VARCHAR(20) | | 手机号 |
| role | ENUM('admin', 'user') | DEFAULT 'user' | 用户角色 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### 6.1.2 股票基本信息表 (stocks)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 股票ID |
| code | VARCHAR(20) | UNIQUE NOT NULL | 股票代码 |
| name | VARCHAR(50) | NOT NULL | 股票名称 |
| industry_code | VARCHAR(20) | NOT NULL | 所属行业代码 |
| market | VARCHAR(20) | NOT NULL | 市场类型 |
| listing_date | DATE | | 上市日期 |
| total_shares | DECIMAL(20,4) | | 总股本 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### 6.1.3 行业表 (industries)

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| code | VARCHAR(20) | PRIMARY KEY | 行业代码 |
| name | VARCHAR(50) | NOT NULL | 行业名称 |
| parent_code | VARCHAR(20) | | 父行业代码 |
| level | INT | DEFAULT 1 | 行业级别 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 6.2 数据仓库 (MongoDB)

#### 6.2.1 股票价格数据 (stock_prices)

```javascript
{
  "stockCode": "600519",
  "date": ISODate("2024-01-01"),
  "open": 1800.00,
  "high": 1825.00,
  "low": 1795.00,
  "close": 1823.00,
  "volume": 123456789,
  "amount": 22567890123.45
}
```

#### 6.2.2 财务数据 (financial_data)

```javascript
{
  "stockCode": "600519",
  "reportDate": "2023-12-31",
  "reportType": "annual", // annual, quarterly
  "balanceSheet": {
    "cash": 135678000000,
    "accountsReceivable": 4567000000,
    "inventory": 325678000000,
    "totalAssets": 2134567000000,
    "totalLiabilities": 377345000000,
    "shareholdersEquity": 1757222000000
  },
  "incomeStatement": {
    "revenue": 1062750000000,
    "cost": 87985000000,
    "profit": 484220000000
  },
  "cashFlow": {
    "operatingCashFlow": 123450000000,
    "investingCashFlow": -56780000000,
    "financingCashFlow": -67890000000
  }
}
```

#### 6.2.3 估值数据 (valuation_data)

```javascript
{
  "stockCode": "600519",
  "date": ISODate("2024-01-01"),
  "pe": 25.6,
  "pb": 9.8,
  "ps": 13.2,
  "pcf": 18.5,
  "evToEbitda": 20.5,
  "dcfValue": 1987.65,
  "fairValue": 1950.00,
  "valuationScore": 85
}
```

## 7. 安全设计

### 7.1 认证与授权

- **JWT认证**: 无状态认证，便于水平扩展
- **权限控制**: 基于RBAC模型
- **API限流**: 防止恶意请求

### 7.2 数据安全

- **数据加密**: 敏感数据加密存储
- **HTTPS传输**: 所有API通信使用HTTPS
- **SQL注入防护**: 使用参数化查询
- **XSS防护**: 输入数据验证和输出转义

### 7.3 安全审计

- **操作日志**: 记录关键操作
- **访问日志**: 记录API访问情况
- **异常监控**: 实时监控异常访问

## 8. 部署架构

### 8.1 容器化部署

- **Docker容器**: 每个微服务独立容器
- **Kubernetes**: 容器编排和管理

### 8.2 高可用设计

- **服务集群**: 关键服务多实例部署
- **负载均衡**: Nginx反向代理
- **故障转移**: 自动检测和恢复

### 8.3 CI/CD流程

- **代码仓库**: Git
- **持续集成**: Jenkins
- **自动化测试**: Jest + Supertest
- **自动化部署**: Kubernetes + Helm

## 9. 性能优化

### 9.1 缓存策略

- **Redis缓存**: 热点数据缓存
- **本地缓存**: 频繁访问的配置数据
- **缓存过期策略**: LRU算法

### 9.2 数据库优化

- **索引优化**: 合理创建索引
- **查询优化**: 避免全表扫描
- **分库分表**: 大数据量场景下的水平扩展

### 9.3 异步处理

- **消息队列**: 异步处理耗时操作
- **批量处理**: 合并请求减少数据库压力
- **定时任务**: 非实时任务定时执行

## 10. 监控与告警

### 10.1 监控指标

- **系统指标**: CPU、内存、磁盘、网络
- **业务指标**: QPS、响应时间、错误率
- **数据库指标**: 连接数、查询耗时、慢查询

### 10.2 告警机制

- **阈值告警**: 超过预设阈值触发
- **趋势告警**: 指标异常波动触发
- **多渠道通知**: 邮件、短信、企业微信

## 11. 未来扩展性

### 11.1 服务扩展

- **新业务模块**: 基于现有架构快速添加
- **第三方集成**: 提供标准接口对接外部系统

### 11.2 数据扩展

- **数据源扩展**: 支持更多金融数据源
- **分析模型扩展**: 接入更多AI分析模型

### 11.3 全球化支持

- **多语言支持**: 国际化架构设计
- **多市场支持**: 扩展到海外市场数据