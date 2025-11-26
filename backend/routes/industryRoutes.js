const express = require('express');
const router = express.Router();
const industryController = require('../controllers/industryController');

/**
 * @swagger
 * tags:
 *   name: Industry
 *   description: 行业分析管理接口
 */

// 获取所有行业列表
router.get('/', industryController.getIndustries);

// 获取行业详情
router.get('/:industryCode', industryController.getIndustryDetail);

// 获取行业内股票列表
router.get('/:industryCode/stocks', industryController.getIndustryStocks);

// 获取行业对比分析
router.get('/analysis/compare', industryController.compareIndustries);

// 获取行业趋势数据
router.get('/:industryCode/trend', industryController.getIndustryTrend);

// 获取行业估值排名
router.get('/valuation/ranking', industryController.getIndustryValuationRanking);

module.exports = router;