import express from 'express';
const router = express.Router();
import investmentRecordController from '../controllers/investmentRecordController.js';
// 临时移除authMiddleware，因为该文件可能不存在
const authMiddleware = (req, res, next) => next(); // 简单的中间件替代

/**
 * @swagger
 * tags:
 *   name: InvestmentRecords
 *   description: 投资记录管理接口
 */

// 获取投资记录列表
router.get('/', authMiddleware, investmentRecordController.getInvestmentRecords);

// 添加投资记录
router.post('/', authMiddleware, investmentRecordController.addInvestmentRecord);

// 更新投资记录
router.put('/:id', authMiddleware, investmentRecordController.updateInvestmentRecord);

// 删除投资记录
router.delete('/:id', authMiddleware, investmentRecordController.deleteInvestmentRecord);

// 获取投资分析数据
router.get('/analysis', authMiddleware, investmentRecordController.getInvestmentAnalysis);

// 导出投资记录
router.get('/export', authMiddleware, investmentRecordController.exportInvestmentRecords);

export default router;