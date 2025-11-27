import InvestmentRecord from '../models/InvestmentRecord.js';
import StockDataService from '../services/stockDataService.js';
import { exportToCSV } from '../utils/csvUtils.js';

/**
 * 投资记录控制器
 */
const investmentRecordController = {
  /**
   * 获取用户的投资记录列表
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async getInvestmentRecords(req, res) {
    try {
      const userId = req.user.id;
      
      // 查找用户的所有投资记录
      const records = await InvestmentRecord.find({ userId }).sort({ transactionDate: -1 });
      
      // 为每条记录获取最新股票价格
      const recordsWithCurrentPrice = await Promise.all(
        records.map(async (record) => {
          try {
            const stockData = await StockDataService.getStockDetail(record.stockCode);
            return {
              ...record.toObject(),
              currentPrice: stockData?.price || record.price
            };
          } catch (error) {
            console.error(`获取股票${record.stockCode}价格失败:`, error);
            return record.toObject();
          }
        })
      );
      
      res.json({
        success: true,
        data: recordsWithCurrentPrice
      });
    } catch (error) {
      console.error('获取投资记录失败:', error);
      res.status(500).json({
        success: false,
        error: '获取投资记录失败，请稍后重试'
      });
    }
  },

  /**
   * 添加新的投资记录
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async addInvestmentRecord(req, res) {
    try {
      const userId = req.user.id;
      const { stockCode, stockName, transactionType, transactionDate, price, quantity, amount } = req.body;
      
      // 验证必要字段
      if (!stockCode || !stockName || !transactionType || !transactionDate || !price || !quantity) {
        return res.status(400).json({
          success: false,
          error: '请填写所有必填字段'
        });
      }
      
      // 如果没有提供金额，自动计算
      const calculatedAmount = amount || (price * quantity);
      
      // 创建新的投资记录
      const newRecord = new InvestmentRecord({
        userId,
        stockCode,
        stockName,
        transactionType,
        transactionDate,
        price,
        quantity,
        amount: calculatedAmount
      });
      
      await newRecord.save();
      
      res.status(201).json({
        success: true,
        data: newRecord
      });
    } catch (error) {
      console.error('添加投资记录失败:', error);
      res.status(500).json({
        success: false,
        error: '添加投资记录失败，请稍后重试'
      });
    }
  },

  /**
   * 更新投资记录
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async updateInvestmentRecord(req, res) {
    try {
      const userId = req.user.id;
      const { id } = req.params;
      const updateData = req.body;
      
      // 查找并验证记录是否属于当前用户
      const record = await InvestmentRecord.findOne({ _id: id, userId });
      if (!record) {
        return res.status(404).json({
          success: false,
          error: '投资记录不存在或无权访问'
        });
      }
      
      // 如果更新价格或数量，重新计算金额
      if (updateData.price !== undefined || updateData.quantity !== undefined) {
        const newPrice = updateData.price !== undefined ? updateData.price : record.price;
        const newQuantity = updateData.quantity !== undefined ? updateData.quantity : record.quantity;
        updateData.amount = newPrice * newQuantity;
      }
      
      // 更新记录
      const updatedRecord = await InvestmentRecord.findByIdAndUpdate(id, updateData, { new: true });
      
      res.json({
        success: true,
        data: updatedRecord
      });
    } catch (error) {
      console.error('更新投资记录失败:', error);
      res.status(500).json({
        success: false,
        error: '更新投资记录失败，请稍后重试'
      });
    }
  },

  /**
   * 删除投资记录
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async deleteInvestmentRecord(req, res) {
    try {
      const userId = req.user.id;
      const { id } = req.params;
      
      // 查找并验证记录是否属于当前用户
      const record = await InvestmentRecord.findOne({ _id: id, userId });
      if (!record) {
        return res.status(404).json({
          success: false,
          error: '投资记录不存在或无权访问'
        });
      }
      
      // 删除记录
      await InvestmentRecord.findByIdAndDelete(id);
      
      res.json({
        success: true,
        data: { message: '投资记录已成功删除' }
      });
    } catch (error) {
      console.error('删除投资记录失败:', error);
      res.status(500).json({
        success: false,
        error: '删除投资记录失败，请稍后重试'
      });
    }
  },

  /**
   * 获取投资分析数据
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async getInvestmentAnalysis(req, res) {
    try {
      const userId = req.user.id;
      
      // 获取用户的所有投资记录
      const records = await InvestmentRecord.find({ userId });
      
      // 计算基本统计数据
      const analysis = await calculateInvestmentAnalysis(records);
      
      res.json({
        success: true,
        data: analysis
      });
    } catch (error) {
      console.error('获取投资分析数据失败:', error);
      res.status(500).json({
        success: false,
        error: '获取投资分析数据失败，请稍后重试'
      });
    }
  },

  /**
   * 导出投资记录为CSV
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async exportInvestmentRecords(req, res) {
    try {
      const userId = req.user.id;
      
      // 获取用户的所有投资记录
      const records = await InvestmentRecord.find({ userId })
        .sort({ transactionDate: -1 });
      
      // 转换为CSV格式
      const csvData = records.map(record => ({
        '股票代码': record.stockCode,
        '股票名称': record.stockName,
        '交易类型': record.transactionType === 'buy' ? '买入' : '卖出',
        '交易日期': record.transactionDate,
        '成交价格': record.price,
        '交易数量': record.quantity,
        '交易金额': record.amount,
        '创建时间': record.createdAt
      }));
      
      const csv = exportToCSV(csvData);
      
      // 设置响应头
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', `attachment; filename=investment_records_${new Date().toISOString().split('T')[0]}.csv`);
      
      res.send(csv);
    } catch (error) {
      console.error('导出投资记录失败:', error);
      res.status(500).json({
        success: false,
        error: '导出投资记录失败，请稍后重试'
      });
    }
  }
};

/**
 * 计算投资分析数据
 * @param {Array} records - 投资记录数组
 * @returns {Object} 分析结果
 */
async function calculateInvestmentAnalysis(records) {
  const buyRecords = records.filter(record => record.transactionType === 'buy');
  
  // 计算总投资金额
  const totalInvestment = buyRecords.reduce((sum, record) => sum + record.amount, 0);
  
  // 获取当前市值和盈亏
  let totalCurrentValue = 0;
  let totalProfit = 0;
  const stockPositions = {};
  
  // 计算每个股票的持仓情况
  for (const record of buyRecords) {
    if (!stockPositions[record.stockCode]) {
      stockPositions[record.stockCode] = {
        stockCode: record.stockCode,
        stockName: record.stockName,
        totalCost: 0,
        totalQuantity: 0,
        avgPrice: 0,
        currentPrice: 0,
        currentValue: 0,
        profit: 0,
        profitPercentage: 0
      };
    }
    
    stockPositions[record.stockCode].totalCost += record.amount;
    stockPositions[record.stockCode].totalQuantity += record.quantity;
  }
  
  // 获取每个股票的当前价格并计算价值
  for (const stockCode in stockPositions) {
    const position = stockPositions[stockCode];
    position.avgPrice = position.totalCost / position.totalQuantity;
    
    try {
      const stockData = await StockService.getStockDetail(stockCode);
      position.currentPrice = stockData?.price || position.avgPrice;
    } catch (error) {
      console.error(`获取股票${stockCode}价格失败:`, error);
      position.currentPrice = position.avgPrice;
    }
    
    position.currentValue = position.currentPrice * position.totalQuantity;
    position.profit = position.currentValue - position.totalCost;
    position.profitPercentage = position.totalCost > 0 ? (position.profit / position.totalCost) * 100 : 0;
    
    totalCurrentValue += position.currentValue;
    totalProfit += position.profit;
  }
  
  const profitPercentage = totalInvestment > 0 ? (totalProfit / totalInvestment) * 100 : 0;
  
  // 计算行业分布（简化处理，实际应基于行业数据）
  const industryDistribution = calculateIndustryDistribution(Object.values(stockPositions));
  
  // 计算价值分析指标
  const valueAnalysis = calculateValueAnalysis(Object.values(stockPositions));
  
  // 计算预期收益和最大可能亏损（基于历史波动）
  const riskReturnAnalysis = calculateRiskReturnAnalysis(Object.values(stockPositions));
  
  return {
    totalInvestment,
    totalCurrentValue,
    totalProfit,
    profitPercentage,
    stockPositions: Object.values(stockPositions),
    industryDistribution,
    valueAnalysis,
    riskReturnAnalysis
  };
}

/**
 * 计算行业分布
 * @param {Array} positions - 持仓数组
 * @returns {Array} 行业分布数据
 */
function calculateIndustryDistribution(positions) {
  // 简化处理，实际应基于行业数据
  // 这里使用模拟数据
  const mockIndustries = {
    '600000': '银行',
    '000858': '白酒',
    '300750': '新能源',
    '000002': '房地产',
    '600519': '白酒',
    '601318': '保险',
    '000333': '家电',
    '000651': '家电',
    '600036': '银行',
    '002594': '新能源'
  };
  
  const industryMap = {};
  
  for (const position of positions) {
    const industry = mockIndustries[position.stockCode] || '其他';
    
    if (!industryMap[industry]) {
      industryMap[industry] = {
        industry,
        value: 0,
        percentage: 0
      };
    }
    
    industryMap[industry].value += position.currentValue;
  }
  
  const totalValue = positions.reduce((sum, pos) => sum + pos.currentValue, 0);
  
  // 计算百分比
  for (const industry in industryMap) {
    industryMap[industry].percentage = totalValue > 0 ? 
      (industryMap[industry].value / totalValue) * 100 : 0;
  }
  
  return Object.values(industryMap).sort((a, b) => b.value - a.value);
}

/**
 * 计算价值分析指标
 * @param {Array} positions - 持仓数组
 * @returns {Object} 价值分析结果
 */
function calculateValueAnalysis(positions) {
  // 这里简化处理，实际应基于更复杂的价值评估模型
  let totalValueScore = 0;
  const undervaluedStocks = [];
  const fairvaluedStocks = [];
  const overvaluedStocks = [];
  
  for (const position of positions) {
    // 基于收益率简单评估价值
    let valueScore = 0;
    let valueCategory = 'fair';
    
    if (position.profitPercentage > 15) {
      valueScore = 75;
      valueCategory = 'overvalued';
      overvaluedStocks.push(position);
    } else if (position.profitPercentage > 5) {
      valueScore = 85;
      valueCategory = 'fair';
      fairvaluedStocks.push(position);
    } else {
      valueScore = 95;
      valueCategory = 'undervalued';
      undervaluedStocks.push(position);
    }
    
    totalValueScore += valueScore;
  }
  
  const avgValueScore = positions.length > 0 ? totalValueScore / positions.length : 0;
  
  return {
    averageValueScore: avgValueScore,
    undervaluedStocks,
    fairvaluedStocks,
    overvaluedStocks,
    valueAssessment: avgValueScore > 90 ? '整体低估' : avgValueScore > 70 ? '估值合理' : '整体高估'
  };
}

/**
 * 计算风险收益分析
 * @param {Array} positions - 持仓数组
 * @returns {Object} 风险收益分析结果
 */
function calculateRiskReturnAnalysis(positions) {
  // 基于历史波动率的简化风险评估
  // 这里使用模拟数据
  const mockVolatility = {
    '600000': 0.12, // 银行股波动较低
    '000858': 0.25, // 白酒股中等波动
    '300750': 0.35, // 新能源股波动较高
    '000002': 0.22,
    '600519': 0.28,
    '601318': 0.15,
    '000333': 0.20,
    '000651': 0.21,
    '600036': 0.13,
    '002594': 0.38
  };
  
  let totalExpectedReturn = 0;
  let totalMaxDrawdown = 0;
  let weightedVolatility = 0;
  const totalValue = positions.reduce((sum, pos) => sum + pos.currentValue, 0);
  
  for (const position of positions) {
    const volatility = mockVolatility[position.stockCode] || 0.25;
    const weight = totalValue > 0 ? position.currentValue / totalValue : 0;
    
    // 基于平均收益和波动率估计预期收益和最大回撤
    const expectedReturn = position.profitPercentage + (volatility * 10); // 简化模型
    const maxDrawdown = volatility * 1.5 * 100; // 简化模型
    
    totalExpectedReturn += expectedReturn * weight;
    totalMaxDrawdown += maxDrawdown * weight;
    weightedVolatility += volatility * weight;
  }
  
  return {
    expectedAnnualReturn: totalExpectedReturn,
    maximumPossibleDrawdown: totalMaxDrawdown,
    portfolioVolatility: weightedVolatility,
    riskLevel: weightedVolatility > 0.3 ? '高风险' : weightedVolatility > 0.2 ? '中等风险' : '低风险',
    riskAdjustedReturn: weightedVolatility > 0 ? totalExpectedReturn / weightedVolatility : 0
  };
}

export default investmentRecordController;