const favoriteStockService = require('../services/favoriteStockService');

/**
 * 股票关注控制器
 * 处理股票关注相关的HTTP请求
 */
class FavoriteStockController {
  /**
   * 添加股票到关注列表
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   * @returns {Promise<void>}
   */
  async addFavorite(req, res) {
    try {
      const { userId } = req.user || req.session; // 从用户认证中间件获取
      const { stockCode } = req.params;
      const options = req.body || {};
      
      if (!userId) {
        return res.status(401).json({ success: false, message: '用户未登录' });
      }
      
      if (!stockCode) {
        return res.status(400).json({ success: false, message: '股票代码不能为空' });
      }
      
      const result = await favoriteStockService.addFavoriteStock(userId, stockCode, options);
      
      res.status(201).json({
        success: true,
        message: '添加关注成功',
        data: result
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error.message || '添加关注失败'
      });
    }
  }
  
  /**
   * 从关注列表移除股票
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   * @returns {Promise<void>}
   */
  async removeFavorite(req, res) {
    try {
      const { userId } = req.user || req.session;
      const { stockCode } = req.params;
      
      if (!userId) {
        return res.status(401).json({ success: false, message: '用户未登录' });
      }
      
      if (!stockCode) {
        return res.status(400).json({ success: false, message: '股票代码不能为空' });
      }
      
      const success = await favoriteStockService.removeFavoriteStock(userId, stockCode);
      
      if (success) {
        res.json({
          success: true,
          message: '移除关注成功'
        });
      } else {
        res.status(404).json({
          success: false,
          message: '未找到关注记录'
        });
      }
    } catch (error) {
      res.status(500).json({
        success: false,
        message: error.message || '移除关注失败'
      });
    }
  }
  
  /**
   * 批量移除关注股票
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   * @returns {Promise<void>}
   */
  async batchRemoveFavorites(req, res) {
    try {
      const { userId } = req.user || req.session;
      const { stockCodes } = req.body;
      
      if (!userId) {
        return res.status(401).json({ success: false, message: '用户未登录' });
      }
      
      if (!Array.isArray(stockCodes) || stockCodes.length === 0) {
        return res.status(400).json({ success: false, message: '请提供有效的股票代码数组' });
      }
      
      const deletedCount = await favoriteStockService.batchRemoveFavoriteStocks(userId, stockCodes);
      
      res.json({
        success: true,
        message: '批量移除成功',
        data: {
          deletedCount
        }
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: error.message || '批量移除失败'
      });
    }
  }
  
  /**
   * 获取用户关注的股票列表
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   * @returns {Promise<void>}
   */
  async getUserFavorites(req, res) {
    try {
      const { userId } = req.user || req.session;
      const { page = 1, limit = 50, sortBy = 'followDate', sortOrder = '-1', includeMarketData = false } = req.query;
      
      if (!userId) {
        return res.status(401).json({ success: false, message: '用户未登录' });
      }
      
      const options = {
        page: parseInt(page, 10),
        limit: parseInt(limit, 10),
        sortBy,
        sortOrder: parseInt(sortOrder, 10),
        includeMarketData: includeMarketData === 'true' || includeMarketData === true
      };
      
      const result = await favoriteStockService.getUserFavoriteStocks(userId, options);
      
      res.json({
        success: true,
        data: result.list,
        pagination: result.pagination
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: error.message || '获取关注列表失败'
      });
    }
  }
  
  /**
   * 检查股票是否已关注
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   * @returns {Promise<void>}
   */
  async checkFavorite(req, res) {
    try {
      const { userId } = req.user || req.session;
      const { stockCode } = req.params;
      
      if (!userId) {
        return res.status(401).json({ success: false, message: '用户未登录' });
      }
      
      if (!stockCode) {
        return res.status(400).json({ success: false, message: '股票代码不能为空' });
      }
      
      const favoriteData = await favoriteStockService.isFavoriteStock(userId, stockCode);
      
      res.json({
        success: true,
        data: {
          isFavorite: !!favoriteData,
          favoriteInfo: favoriteData
        }
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: error.message || '检查关注状态失败'
      });
    }
  }
  
  /**
   * 更新关注股票的提醒设置
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   * @returns {Promise<void>}
   */
  async updateAlertSettings(req, res) {
    try {
      const { userId } = req.user || req.session;
      const { stockCode } = req.params;
      const alertConfig = req.body || {};
      
      if (!userId) {
        return res.status(401).json({ success: false, message: '用户未登录' });
      }
      
      if (!stockCode) {
        return res.status(400).json({ success: false, message: '股票代码不能为空' });
      }
      
      const updatedFavorite = await favoriteStockService.updateAlertSettings(userId, stockCode, alertConfig);
      
      res.json({
        success: true,
        message: '提醒设置更新成功',
        data: updatedFavorite
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error.message || '更新提醒设置失败'
      });
    }
  }
  
  /**
   * 更新关注股票的标签
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   * @returns {Promise<void>}
   */
  async updateTags(req, res) {
    try {
      const { userId } = req.user || req.session;
      const { stockCode } = req.params;
      const { tags } = req.body;
      
      if (!userId) {
        return res.status(401).json({ success: false, message: '用户未登录' });
      }
      
      if (!stockCode) {
        return res.status(400).json({ success: false, message: '股票代码不能为空' });
      }
      
      if (!Array.isArray(tags)) {
        return res.status(400).json({ success: false, message: '标签必须是数组格式' });
      }
      
      const updatedFavorite = await favoriteStockService.updateTags(userId, stockCode, tags);
      
      res.json({
        success: true,
        message: '标签更新成功',
        data: updatedFavorite
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error.message || '更新标签失败'
      });
    }
  }
  
  /**
   * 更新关注股票的备注
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   * @returns {Promise<void>}
   */
  async updateNotes(req, res) {
    try {
      const { userId } = req.user || req.session;
      const { stockCode } = req.params;
      const { notes } = req.body;
      
      if (!userId) {
        return res.status(401).json({ success: false, message: '用户未登录' });
      }
      
      if (!stockCode) {
        return res.status(400).json({ success: false, message: '股票代码不能为空' });
      }
      
      const updatedFavorite = await favoriteStockService.updateNotes(userId, stockCode, notes);
      
      res.json({
        success: true,
        message: '备注更新成功',
        data: updatedFavorite
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error.message || '更新备注失败'
      });
    }
  }
  
  /**
   * 按标签筛选关注的股票
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   * @returns {Promise<void>}
   */
  async filterByTags(req, res) {
    try {
      const { userId } = req.user || req.session;
      const { tags } = req.query;
      const { page = 1, limit = 50 } = req.query;
      
      if (!userId) {
        return res.status(401).json({ success: false, message: '用户未登录' });
      }
      
      if (!tags) {
        return res.status(400).json({ success: false, message: '标签参数不能为空' });
      }
      
      // 处理标签参数，支持逗号分隔的多个标签
      const tagsArray = typeof tags === 'string' ? tags.split(',').map(t => t.trim()) : tags;
      
      const options = {
        page: parseInt(page, 10),
        limit: parseInt(limit, 10)
      };
      
      const result = await favoriteStockService.filterByTags(userId, tagsArray, options);
      
      res.json({
        success: true,
        data: result.list,
        pagination: result.pagination
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: error.message || '按标签筛选失败'
      });
    }
  }
  
  /**
   * 更新股票最后查看时间
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   * @returns {Promise<void>}
   */
  async updateLastViewed(req, res) {
    try {
      const { userId } = req.user || req.session;
      const { stockCode } = req.params;
      
      if (!userId) {
        return res.status(401).json({ success: false, message: '用户未登录' });
      }
      
      if (!stockCode) {
        return res.status(400).json({ success: false, message: '股票代码不能为空' });
      }
      
      const success = await favoriteStockService.updateLastViewed(userId, stockCode);
      
      res.json({
        success: success,
        message: success ? '更新成功' : '更新失败'
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: error.message || '更新最后查看时间失败'
      });
    }
  }
}

module.exports = new FavoriteStockController();
