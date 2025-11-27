const mongoose = require('mongoose');

/**
 * 用户关注股票数据模型
 * 用于管理用户关注的股票列表，支持个性化提醒设置
 */
const UserFavoriteStockSchema = new mongoose.Schema({
  // 用户ID
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  
  // 股票代码
  stockCode: {
    type: String,
    required: true
  },
  
  // 股票名称
  stockName: {
    type: String,
    required: true
  },
  
  // 所属市场
  market: {
    type: String,
    enum: ['SH', 'SZ', 'BJ', 'HK', 'US'],
    default: 'SH'
  },
  
  // 关注时间
  followDate: {
    type: Date,
    default: Date.now
  },
  
  // 提醒设置
  alerts: {
    priceAlert: {
      enabled: {
        type: Boolean,
        default: false
      },
      upperLimit: {
        type: Number,
        default: 0
      },
      lowerLimit: {
        type: Number,
        default: 0
      }
    },
    volumeAlert: {
      enabled: {
        type: Boolean,
        default: false
      },
      threshold: {
        type: Number,
        default: 0
      }
    },
    newsAlert: {
      enabled: {
        type: Boolean,
        default: false
      }
    },
    financialReportAlert: {
      enabled: {
        type: Boolean,
        default: false
      }
    }
  },
  
  // 自定义标签
  tags: {
    type: [String],
    default: []
  },
  
  // 备注信息
  notes: {
    type: String
  },
  
  // 最后查看时间
  lastViewedAt: {
    type: Date
  },
  
  // 创建时间
  createdAt: {
    type: Date,
    default: Date.now
  },
  
  // 更新时间
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// 更新updatedAt字段的中间件
UserFavoriteStockSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// 索引，提高查询性能
UserFavoriteStockSchema.index({ userId: 1, stockCode: 1 }, { unique: true }); // 确保每个用户对每个股票只有一条关注记录
UserFavoriteStockSchema.index({ userId: 1, followDate: -1 }); // 按关注时间排序
UserFavoriteStockSchema.index({ stockCode: 1 }); // 按股票代码查询

/**
 * 静态方法：获取用户关注的所有股票
 * @param {String} userId - 用户ID
 * @param {Object} options - 查询选项
 * @returns {Promise<Array>} 关注的股票列表
 */
UserFavoriteStockSchema.statics.getUserFavorites = async function(userId, options = {}) {
  const { limit = 50, skip = 0, sortBy = 'followDate', sortOrder = -1 } = options;
  
  return this.find({ userId })
    .sort({ [sortBy]: sortOrder })
    .limit(limit)
    .skip(skip)
    .exec();
};

/**
 * 静态方法：检查用户是否已关注某只股票
 * @param {String} userId - 用户ID
 * @param {String} stockCode - 股票代码
 * @returns {Promise<Boolean>} 是否已关注
 */
UserFavoriteStockSchema.statics.isFavorite = async function(userId, stockCode) {
  const count = await this.countDocuments({ userId, stockCode }).exec();
  return count > 0;
};

/**
 * 实例方法：更新价格提醒设置
 * @param {Boolean} enabled - 是否启用
 * @param {Number} upperLimit - 上限价格
 * @param {Number} lowerLimit - 下限价格
 * @returns {Promise<Object>} 更新后的文档
 */
UserFavoriteStockSchema.methods.updatePriceAlert = function(enabled, upperLimit = 0, lowerLimit = 0) {
  this.alerts.priceAlert = {
    enabled,
    upperLimit,
    lowerLimit
  };
  return this.save();
};

/**
 * 实例方法：添加标签
 * @param {String|Array} tag - 标签或标签数组
 * @returns {Promise<Object>} 更新后的文档
 */
UserFavoriteStockSchema.methods.addTags = function(tag) {
  const tagsToAdd = Array.isArray(tag) ? tag : [tag];
  const uniqueTags = [...new Set([...this.tags, ...tagsToAdd])];
  this.tags = uniqueTags;
  return this.save();
};

/**
 * 实例方法：移除标签
 * @param {String|Array} tag - 标签或标签数组
 * @returns {Promise<Object>} 更新后的文档
 */
UserFavoriteStockSchema.methods.removeTags = function(tag) {
  const tagsToRemove = Array.isArray(tag) ? tag : [tag];
  this.tags = this.tags.filter(t => !tagsToRemove.includes(t));
  return this.save();
};

module.exports = mongoose.model('UserFavoriteStock', UserFavoriteStockSchema);
