import mongoose from 'mongoose';

/**
 * 投资记录数据模型
 */
const InvestmentRecordSchema = new mongoose.Schema({
  // 用户ID
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
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
  
  // 交易类型：买入或卖出
  transactionType: {
    type: String,
    enum: ['buy', 'sell'],
    required: true
  },
  
  // 交易日期
  transactionDate: {
    type: Date,
    required: true
  },
  
  // 成交价格
  price: {
    type: Number,
    required: true,
    min: 0
  },
  
  // 交易数量
  quantity: {
    type: Number,
    required: true,
    min: 1
  },
  
  // 交易金额
  amount: {
    type: Number,
    required: true,
    min: 0
  },
  
  // 备注信息
  notes: {
    type: String
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
InvestmentRecordSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// 索引，提高查询性能
InvestmentRecordSchema.index({ userId: 1, stockCode: 1 });
InvestmentRecordSchema.index({ userId: 1, transactionDate: -1 });

export default mongoose.model('InvestmentRecord', InvestmentRecordSchema);