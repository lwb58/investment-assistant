const express = require('express');
const router = express.Router();
const investmentRecordController = require('../controllers/investmentRecordController');
const authMiddleware = require('../middleware/authMiddleware');

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

module.exports = router;