import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { getDB } from './config/db.js';
import valuationRoutes from './routes/valuationRoutes.js';
import portfolioRoutes from './routes/portfolioRoutes.js';
import stockDataRoutes from './routes/stockDataRoutes.js';
import investmentRecordRoutes from './routes/investmentRecordRoutes.js';
import industryRoutes from './routes/industryRoutes.js';
import valuationService from './services/valuationService.js';
import performanceMonitor from './middleware/performanceMonitor.js';

// 加载环境变量
dotenv.config();

// 创建Express应用
const app = express();
const PORT = process.env.PORT || 3000;

// 配置中间件
app.use(cors());
app.use(express.json());
app.use(performanceMonitor);

// 健康检查接口
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    message: '投资辅助系统后端服务运行正常',
    timestamp: new Date().toISOString()
  });
});

// API路由
app.use('/api/valuation', valuationRoutes);
app.use('/api/stock', stockDataRoutes);
app.use(portfolioRoutes);
app.use('/api/investment-records', investmentRecordRoutes);
app.use('/api/industry', industryRoutes);

// 404处理
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: '接口不存在'
  });
});

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error('服务器错误:', err);
  res.status(500).json({
    success: false,
    error: '服务器内部错误',
    details: err.message
  });
});

// 启动服务器
async function startServer() {
  try {
    // 初始化数据库
    await getDB();
    console.log('数据库连接成功');
    
    // 初始化估值服务
    await valuationService.initialize();
    console.log('估值服务初始化成功');
    
    // 启动服务器
    app.listen(PORT, () => {
      console.log(`服务器启动成功，监听端口: ${PORT}`);
      console.log(`健康检查: http://localhost:${PORT}/health`);
      console.log(`API文档: http://localhost:${PORT}/api/valuation`);
    console.log(`投资组合API: http://localhost:${PORT}/api/portfolios`);
    });
  } catch (error) {
    console.error('服务器启动失败:', error);
    process.exit(1);
  }
}

// 启动应用
startServer();

// 优雅关闭
process.on('SIGINT', async () => {
  console.log('正在关闭服务器...');
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('正在关闭服务器...');
  process.exit(0);
});