# 个人股票投资辅助系统

## 项目简介
这是一个功能完善的个人股票投资辅助系统，用于集中管理股票投资清单、记录投资复盘笔记，并提供个股基本面数据展示，帮助投资者做出更明智的投资决策，积累投资经验。

## 技术栈
- **前端**：Vue.js 3 + Vite + Vue Router + CSS
- **后端**：FastAPI (Python)
- **数据库**：SQLite
- **API层**：统一的API服务层设计，支持Mock数据和真实API切换

## 核心功能

### 1. 股票清单管理
- **股票列表展示**：显示股票代码、名称、当前价格、涨跌幅、行业分类等信息
- **股票搜索与筛选**：支持按代码、名称、行业进行搜索
- **持仓状态标记**：直观标识已持仓和未持仓的股票
- **CRUD操作**：支持新增、编辑、删除股票信息
- **响应式设计**：适配不同屏幕尺寸的设备

### 2. 个股详情展示
- **基本信息展示**：股票代码、名称、价格、涨跌幅、行业等
- **公司信息展示**：公司全称、上市日期、总股数、流通股数、市值等
- **财务数据展示**：支持多年份财务数据切换展示，包括营收、利润、毛利率、净利率等关键财务指标
- **股东信息展示**：显示前十大股东列表及其持股比例
- **加载和错误状态处理**：提供友好的加载动画和错误提示

### 3. 复盘笔记管理
- **笔记列表展示**：按创建时间倒序排列，显示标题、创建/更新时间、相关股票信息
- **笔记搜索功能**：支持按标题、内容、股票代码搜索
- **笔记编辑功能**：富文本编辑，支持Markdown格式
- **笔记标签管理**：添加和管理笔记标签
- **股票关联**：可关联特定股票，便于后续回顾
- **完整的CRUD操作**：创建、读取、更新、删除笔记
- **状态管理**：完善的加载状态、错误处理和用户反馈

## 项目结构
```
investment-assistant/
├── .gitignore          # Git忽略文件
├── .vscode/            # VS Code配置
├── index.html          # HTML入口文件
├── package.json        # 项目依赖配置
├── package-lock.json   # 依赖版本锁定
├── vite.config.js      # Vite配置文件
├── src/                # 前端源代码
│   ├── App.vue         # 根组件
│   ├── main.js         # 应用入口文件
│   ├── api/            # API服务层
│   │   └── apiService.js # 统一的API服务
│   ├── assets/         # 静态资源
│   │   └── main.css    # 全局样式
│   ├── router/         # 路由配置
│   │   ├── index.js    # 路由定义
│   │   └── router.js   # 路由配置
│   └── views/          # 页面组件
│       ├── ReviewNotesView.vue    # 复盘笔记页面
│       ├── StockDetailView.vue    # 股票详情页面
│       └── StockListView.vue      # 股票清单页面
└── backend/            # 后端代码
    ├── .env            # 后端环境变量
    ├── database/       # 数据库相关
    ├── main.py         # 后端入口
    └── requirements.txt # Python依赖
```

## 快速开始

### 环境要求
- Node.js 16.x 或更高版本
- npm 8.x 或更高版本
- Python 3.8 或更高版本
- pip 20.x 或更高版本

### 前端安装与运行

1. **安装依赖**
```bash
npm install
```

2. **开发模式运行**
```bash
npm run dev
```
前端服务默认在 http://localhost:5173 启动

3. **构建生产版本**
```bash
npm run build
```
构建产物将生成在 `dist` 目录中

### 后端安装与运行

1. **进入后端目录**
```bash
cd backend
```

2. **安装Python依赖**
```bash
pip install -r requirements.txt
```

3. **启动后端服务**
```bash
python main.py
```
后端服务默认在 http://localhost:8000 启动

## 配置说明

### 前端配置
- **API模式切换**：在 `src/api/apiService.js` 中设置 `useMockData` 属性
  - `true`: 使用模拟数据（无需后端服务）
  - `false`: 使用真实后端API

- **路由配置**：在 `src/router/index.js` 中可修改路由规则

### 后端配置
- **环境变量**：在 `backend/.env` 文件中配置数据库连接等信息
- **数据库**：SQLite数据库文件位于 `backend/database/investment.db`

## 功能亮点

1. **统一的API服务层**：采用单例模式设计，集中管理所有API请求，便于维护和扩展
2. **Mock数据支持**：即使没有后端服务，也能通过模拟数据展示完整功能
3. **响应式UI设计**：适配桌面端和移动端设备
4. **完善的状态管理**：包含加载状态、错误处理、空状态等各种场景的UI展示
5. **用户友好的交互**：提供清晰的操作反馈和视觉提示

## 开发指南

### 添加新页面
1. 在 `src/views/` 目录下创建新的Vue组件
2. 在 `src/router/index.js` 中注册新路由
3. 在 `src/api/apiService.js` 中添加相关API方法

### 扩展API服务
1. 在 `src/api/apiService.js` 中的 `ApiService` 类中添加新方法
2. 同时实现模拟数据和真实API调用逻辑

### 代码规范
- 组件命名：采用PascalCase命名规范
- API方法：使用清晰的动词+名词命名，如 `getStocks`, `updateNote`
- 状态管理：使用Vue 3的Composition API（ref, computed, onMounted等）

## 注意事项
- 开发环境下默认使用Mock数据，生产环境请切换到真实API
- 确保后端服务在真实API模式下正常运行
- 构建前请检查是否有语法错误或未使用的导入

## License
MIT

