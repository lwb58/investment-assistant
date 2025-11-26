# 智能投资助手系统

## 项目简介
智能投资助手是一个集成了股票数据分析、估值模型、投资组合管理的全方位投资决策支持平台。本系统通过数据驱动的方式，为用户提供科学的投资建议和组合管理功能，帮助用户做出更明智的投资决策。

## 核心功能特性

### 📊 数据分析
- 股票基本面数据采集与存储
- 实时市场行情监控
- 财务报表数据分析
- 历史数据趋势分析

### 🧠 智能估值
- 多因子估值模型
- 相对估值分析（PE、PB、PS等）
- 行业对比分析
- 内在价值计算

### 📈 投资组合管理
- 创建和管理多个投资组合
- 持仓分析与绩效跟踪
- 资产配置优化
- 风险收益分析

### 💡 投资决策支持
- 个性化投资建议生成
- 买入/卖出信号提示
- 历史决策回测
- 风险管理建议

## 技术架构

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **UI组件库**: Element Plus
- **图表可视化**: ECharts
- **HTTP请求**: Axios

### 后端技术栈
- **运行环境**: Node.js
- **Web框架**: Express
- **数据库**: SQLite（开发环境）/ MySQL（生产环境）
- **API设计**: RESTful
- **认证**: JWT

## 系统架构设计

- **数据采集层**: 负责从外部API获取股票数据、财务数据和市场行情
- **数据存储层**: 管理SQLite数据库，存储所有业务数据
- **业务逻辑层**: 包含估值算法、投资决策模型、组合管理逻辑
- **API服务层**: 提供RESTful API接口供前端调用
- **前端应用层**: 用户交互界面，展示数据分析结果和提供操作入口

## 快速开始

### 环境要求
- Node.js 16+
- npm 7+

### 后端部署

1. 进入后端目录
```bash
cd backend
```

2. 安装依赖
```bash
npm install
```

3. 启动服务
```bash
npm start
```

后端服务默认运行在 http://localhost:3000

### 前端部署

1. 安装依赖
```bash
npm install
```

2. 开发环境启动
```bash
npm run dev
```

3. 构建生产版本
```bash
npm run build
```

### 环境配置

后端配置文件位于 `backend/.env`（需自行创建）：
```
# 服务器配置
PORT=3000

# 数据库配置
DB_PATH=./database/investment_assistant.db

# JWT密钥
SECRET_KEY=your_secret_key_here

# API配置
API_TIMEOUT=10000
```

## API文档

### 健康检查
- `GET /health` - 检查服务健康状态

### 估值API
- `GET /api/valuation/stock/:code` - 获取股票估值信息
- `POST /api/valuation/compare` - 股票估值对比
- `GET /api/valuation/industry/:industry` - 行业估值分析

### 投资组合API
- `GET /api/portfolios` - 获取所有投资组合
- `POST /api/portfolios` - 创建新投资组合
- `GET /api/portfolios/:id` - 获取指定投资组合
- `PUT /api/portfolios/:id` - 更新投资组合
- `DELETE /api/portfolios/:id` - 删除投资组合
- `POST /api/portfolios/:id/holdings` - 添加持仓
- `GET /api/portfolios/:id/holdings` - 获取持仓列表
- `GET /api/portfolios/:id/performance` - 获取组合绩效
- `GET /api/portfolios/:id/allocation` - 获取资产配置

## 项目结构

```
investment-assistant/
├── backend/              # 后端应用
│   ├── config/           # 配置文件
│   ├── controllers/      # 控制器
│   ├── database/         # 数据库相关
│   ├── middleware/       # 中间件
│   ├── models/           # 数据模型
│   ├── routes/           # 路由定义
│   ├── services/         # 业务逻辑
│   ├── utils/            # 工具函数
│   ├── index.js          # 应用入口
│   └── package.json      # 依赖配置
├── src/                  # 前端应用
│   ├── assets/           # 静态资源
│   ├── components/       # 组件
│   ├── layouts/          # 布局
│   ├── pages/            # 页面
│   ├── router/           # 路由
│   ├── stores/           # 状态管理
│   ├── utils/            # 工具函数
│   ├── api/              # API接口
│   ├── App.vue           # 根组件
│   └── main.ts           # 入口文件
├── public/               # 公共资源
├── index.html            # HTML模板
├── vite.config.ts        # Vite配置
├── tsconfig.json         # TypeScript配置
└── README.md             # 项目文档
```

## 开发指南

### 代码规范
- 前端遵循 Vue 3 和 TypeScript 最佳实践
- 后端遵循 Node.js 和 Express 代码规范
- 使用 ESLint 和 Prettier 进行代码检查和格式化

### 测试
- 单元测试使用 Jest
- API测试使用 Supertest
- 前端组件测试使用 Vitest

### 版本控制
- 使用 Git 进行版本管理
- 遵循 GitFlow 工作流

## 生产部署建议

1. **数据库迁移**：从SQLite迁移到MySQL或PostgreSQL以提高性能
2. **服务部署**：使用PM2管理Node.js进程
3. **静态资源**：使用CDN加速静态资源访问
4. **安全措施**：
   - 使用HTTPS
   - 设置合理的CORS策略
   - 实现请求频率限制
   - 定期更新依赖包

## 已知限制

- 目前使用的是模拟数据，实际应用需要接入真实的金融数据源
- 估值模型仅供参考，不构成投资建议
- 系统性能在大量数据时可能需要优化

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License