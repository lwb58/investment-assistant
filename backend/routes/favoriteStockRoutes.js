const express = require('express');
const router = express.Router();
const favoriteStockController = require('../controllers/favoriteStockController');

// 假设我们有一个认证中间件，用于验证用户登录状态
// const authMiddleware = require('../middleware/authMiddleware');

/**
 * 股票关注相关路由
 * 定义所有与用户关注股票功能相关的API端点
 */

// 添加股票到关注列表
router.post('/:stockCode', /* authMiddleware, */ favoriteStockController.addFavorite);

// 从关注列表移除股票
router.delete('/:stockCode', /* authMiddleware, */ favoriteStockController.removeFavorite);

// 批量移除关注股票
router.delete('/batch/remove', /* authMiddleware, */ favoriteStockController.batchRemoveFavorites);

// 获取用户关注的股票列表
router.get('/', /* authMiddleware, */ favoriteStockController.getUserFavorites);

// 检查股票是否已关注
router.get('/:stockCode/check', /* authMiddleware, */ favoriteStockController.checkFavorite);

// 更新关注股票的提醒设置
router.put('/:stockCode/alerts', /* authMiddleware, */ favoriteStockController.updateAlertSettings);

// 更新关注股票的标签
router.put('/:stockCode/tags', /* authMiddleware, */ favoriteStockController.updateTags);

// 更新关注股票的备注
router.put('/:stockCode/notes', /* authMiddleware, */ favoriteStockController.updateNotes);

// 按标签筛选关注的股票
router.get('/filter/tags', /* authMiddleware, */ favoriteStockController.filterByTags);

// 更新股票最后查看时间
router.put('/:stockCode/last-viewed', /* authMiddleware, */ favoriteStockController.updateLastViewed);

module.exports = router;
