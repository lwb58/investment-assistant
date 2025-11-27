const UserFavoriteStock = require('../models/UserFavoriteStock');
const stockDataService = require('./stockDataService');

/**
 * 股票关注服务
 * 处理用户关注股票的相关业务逻辑
 */
class FavoriteStockService {
  /**
   * 添加股票到关注列表
   * @param {String} userId - 用户ID
   * @param {String} stockCode - 股票代码
   * @param {Object} options - 附加选项
   * @returns {Promise<Object>} 关注记录
   */
  async addFavoriteStock(userId, stockCode, options = {}) {
    try {
      // 检查是否已关注
      const isAlreadyFavorite = await UserFavoriteStock.isFavorite(userId, stockCode);
      if (isAlreadyFavorite) {
        throw new Error('该股票已经在您的关注列表中');
      }
      
      // 获取股票基本信息（如果需要）
      let stockInfo = options.stockInfo;
      if (!stockInfo) {
        try {
          stockInfo = await stockDataService.getStockData(stockCode);
        } catch (error) {
          console.warn(`获取股票${stockCode}信息失败，使用传入的名称或默认名称`);
        }
      }
      
      // 创建关注记录
      const favoriteStock = new UserFavoriteStock({
        userId,
        stockCode,
        stockName: stockInfo?.name || options.stockName || `股票${stockCode}`,
        market: stockInfo?.market || options.market || 'SH',
        alerts: options.alerts || {},
        tags: options.tags || [],
        notes: options.notes || ''
      });
      
      await favoriteStock.save();
      return favoriteStock;
    } catch (error) {
      console.error('添加关注股票失败:', error);
      throw error;
    }
  }
  
  /**
   * 从关注列表移除股票
   * @param {String} userId - 用户ID
   * @param {String} stockCode - 股票代码
   * @returns {Promise<Boolean>} 是否成功移除
   */
  async removeFavoriteStock(userId, stockCode) {
    try {
      const result = await UserFavoriteStock.deleteOne({ userId, stockCode });
      return result.deletedCount > 0;
    } catch (error) {
      console.error('移除关注股票失败:', error);
      throw error;
    }
  }
  
  /**
   * 批量移除关注股票
   * @param {String} userId - 用户ID
   * @param {Array<String>} stockCodes - 股票代码数组
   * @returns {Promise<Number>} 成功移除的数量
   */
  async batchRemoveFavoriteStocks(userId, stockCodes) {
    try {
      const result = await UserFavoriteStock.deleteMany({
        userId,
        stockCode: { $in: stockCodes }
      });
      return result.deletedCount;
    } catch (error) {
      console.error('批量移除关注股票失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取用户关注的股票列表
   * @param {String} userId - 用户ID
   * @param {Object} options - 查询选项
   * @returns {Promise<Object>} 包含列表和总数的对象
   */
  async getUserFavoriteStocks(userId, options = {}) {
    try {
      const { limit = 50, page = 1, sortBy = 'followDate', sortOrder = -1, includeMarketData = false } = options;
      
      // 计算分页
      const skip = (page - 1) * limit;
      
      // 查询关注列表
      const favorites = await UserFavoriteStock.getUserFavorites(userId, {
        limit,
        skip,
        sortBy,
        sortOrder
      });
      
      // 获取总数
      const total = await UserFavoriteStock.countDocuments({ userId });
      
      // 如果需要市场数据，批量获取股票行情
      if (includeMarketData && favorites.length > 0) {
        const stockCodes = favorites.map(fav => fav.stockCode);
        try {
          const marketDataMap = await this._getBatchMarketData(stockCodes);
          
          // 合并市场数据
          favorites.forEach(fav => {
            fav.marketData = marketDataMap[fav.stockCode] || null;
          });
        } catch (error) {
          console.warn('获取市场数据失败，但不影响关注列表查询:', error);
        }
      }
      
      return {
        list: favorites,
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit)
        }
      };
    } catch (error) {
      console.error('获取用户关注股票列表失败:', error);
      throw error;
    }
  }
  
  /**
   * 检查用户是否关注了某只股票
   * @param {String} userId - 用户ID
   * @param {String} stockCode - 股票代码
   * @returns {Promise<Object|null>} 关注记录或null
   */
  async isFavoriteStock(userId, stockCode) {
    try {
      return await UserFavoriteStock.findOne({ userId, stockCode });
    } catch (error) {
      console.error('检查关注状态失败:', error);
      return null;
    }
  }
  
  /**
   * 更新关注股票的提醒设置
   * @param {String} userId - 用户ID
   * @param {String} stockCode - 股票代码
   * @param {Object} alertConfig - 提醒配置
   * @returns {Promise<Object>} 更新后的关注记录
   */
  async updateAlertSettings(userId, stockCode, alertConfig) {
    try {
      const favoriteStock = await UserFavoriteStock.findOne({ userId, stockCode });
      if (!favoriteStock) {
        throw new Error('未找到关注记录');
      }
      
      // 更新提醒设置
      if (alertConfig.priceAlert !== undefined) {
        favoriteStock.alerts.priceAlert = { ...favoriteStock.alerts.priceAlert, ...alertConfig.priceAlert };
      }
      if (alertConfig.volumeAlert !== undefined) {
        favoriteStock.alerts.volumeAlert = { ...favoriteStock.alerts.volumeAlert, ...alertConfig.volumeAlert };
      }
      if (alertConfig.newsAlert !== undefined) {
        favoriteStock.alerts.newsAlert = { ...favoriteStock.alerts.newsAlert, ...alertConfig.newsAlert };
      }
      if (alertConfig.financialReportAlert !== undefined) {
        favoriteStock.alerts.financialReportAlert = { ...favoriteStock.alerts.financialReportAlert, ...alertConfig.financialReportAlert };
      }
      
      await favoriteStock.save();
      return favoriteStock;
    } catch (error) {
      console.error('更新提醒设置失败:', error);
      throw error;
    }
  }
  
  /**
   * 更新关注股票的标签
   * @param {String} userId - 用户ID
   * @param {String} stockCode - 股票代码
   * @param {Array<String>} tags - 新的标签数组
   * @returns {Promise<Object>} 更新后的关注记录
   */
  async updateTags(userId, stockCode, tags) {
    try {
      const favoriteStock = await UserFavoriteStock.findOne({ userId, stockCode });
      if (!favoriteStock) {
        throw new Error('未找到关注记录');
      }
      
      favoriteStock.tags = tags;
      await favoriteStock.save();
      return favoriteStock;
    } catch (error) {
      console.error('更新标签失败:', error);
      throw error;
    }
  }
  
  /**
   * 更新关注股票的备注
   * @param {String} userId - 用户ID
   * @param {String} stockCode - 股票代码
   * @param {String} notes - 备注内容
   * @returns {Promise<Object>} 更新后的关注记录
   */
  async updateNotes(userId, stockCode, notes) {
    try {
      const favoriteStock = await UserFavoriteStock.findOne({ userId, stockCode });
      if (!favoriteStock) {
        throw new Error('未找到关注记录');
      }
      
      favoriteStock.notes = notes;
      await favoriteStock.save();
      return favoriteStock;
    } catch (error) {
      console.error('更新备注失败:', error);
      throw error;
    }
  }
  
  /**
   * 更新最后查看时间
   * @param {String} userId - 用户ID
   * @param {String} stockCode - 股票代码
   * @returns {Promise<Boolean>} 是否成功更新
   */
  async updateLastViewed(userId, stockCode) {
    try {
      const result = await UserFavoriteStock.updateOne(
        { userId, stockCode },
        { $set: { lastViewedAt: Date.now() } }
      );
      return result.nModified > 0;
    } catch (error) {
      console.error('更新最后查看时间失败:', error);
      return false;
    }
  }
  
  /**
   * 按标签筛选关注的股票
   * @param {String} userId - 用户ID
   * @param {String|Array<String>} tags - 标签或标签数组
   * @param {Object} options - 查询选项
   * @returns {Promise<Array>} 筛选后的关注列表
   */
  async filterByTags(userId, tags, options = {}) {
    try {
      const { limit = 50, page = 1 } = options;
      const skip = (page - 1) * limit;
      
      const query = {
        userId,
        tags: { $in: Array.isArray(tags) ? tags : [tags] }
      };
      
      const filtered = await UserFavoriteStock.find(query)
        .sort({ followDate: -1 })
        .limit(limit)
        .skip(skip);
      
      const total = await UserFavoriteStock.countDocuments(query);
      
      return {
        list: filtered,
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit)
        }
      };
    } catch (error) {
      console.error('按标签筛选关注股票失败:', error);
      throw error;
    }
  }
  
  /**
   * 批量获取股票市场数据
   * @private
   * @param {Array<String>} stockCodes - 股票代码数组
   * @returns {Promise<Object>} 股票代码到市场数据的映射
   */
  async _getBatchMarketData(stockCodes) {
    try {
      // 使用批量获取接口提高性能
      const batchData = await stockDataService.batchGetStockData(stockCodes);
      
      // 转换为映射格式
      const dataMap = {};
      if (Array.isArray(batchData)) {
        batchData.forEach(item => {
          if (item && item.code) {
            dataMap[item.code] = {
              price: item.latestPrice || item.close,
              change: item.change,
              changePercent: item.changePercent,
              volume: item.volume
            };
          }
        });
      }
      
      return dataMap;
    } catch (error) {
      console.error('批量获取市场数据失败:', error);
      return {};
    }
  }
}

module.exports = new FavoriteStockService();
