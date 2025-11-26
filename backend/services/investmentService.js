import { getDB } from '../config/db.js';

class InvestmentService {
  constructor() {
    this.initialize();
  }

  async initialize() {
    // 初始化时可以加载一些配置或缓存数据
    console.log('投资决策服务初始化完成');
  }

  /**
   * 生成投资建议
   * @param {string} symbol 股票代码
   * @param {Object} valuationResult 估值结果
   * @returns {Object} 投资建议
   */
  async generateInvestmentAdvice(symbol, valuationResult) {
    try {
      // 获取股票基本信息
      const stockInfo = await this.getStockInfo(symbol);
      if (!stockInfo) {
        throw new Error(`未找到股票代码 ${symbol} 的基本信息`);
      }

      // 获取历史财务数据
      const financialData = await this.getFinancialData(symbol);

      // 获取市场数据
      const marketData = await this.getMarketData(symbol);

      // 计算综合评分
      const scores = this.calculateScores(valuationResult, financialData, marketData);
      const totalScore = this.calculateTotalScore(scores);

      // 生成建议
      const advice = this.buildAdvice(totalScore, scores, valuationResult);

      // 保存建议到数据库
      await this.saveAdvice(symbol, totalScore, advice, scores);

      return {
        symbol,
        stockName: stockInfo.name,
        totalScore,
        scores,
        advice,
        valuationData: valuationResult,
        timestamp: new Date()
      };
    } catch (error) {
      console.error('生成投资建议失败:', error);
      throw error;
    }
  }

  /**
   * 获取股票基本信息
   */
  async getStockInfo(symbol) {
    const database = await getDB();
    return new Promise((resolve, reject) => {
      database.get(
        'SELECT * FROM stock_basic_info WHERE stock_code = ?',
        [symbol],
        (err, row) => {
          if (err) reject(err);
          else resolve(row);
        }
      );
    });
  }

  /**
   * 获取财务数据
   */
  async getFinancialData(symbol) {
    const database = await getDB();
    return new Promise((resolve, reject) => {
      database.all(
        'SELECT * FROM company_financial_data WHERE stock_code = ? ORDER BY fiscal_year DESC LIMIT 3',
        [symbol],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  /**
   * 获取市场数据
   */
  async getMarketData(symbol) {
    const database = await getDB();
    return new Promise((resolve, reject) => {
      database.get(
        'SELECT * FROM stock_quotes WHERE stock_code = ? ORDER BY quote_date DESC LIMIT 1',
        [symbol],
        (err, row) => {
          if (err) reject(err);
          else resolve(row);
        }
      );
    });
  }

  /**
   * 计算各维度得分
   */
  calculateScores(valuationResult, financialData, marketData) {
    const scores = {
      valuationScore: this.calculateValuationScore(valuationResult),
      growthScore: this.calculateGrowthScore(financialData),
      financialHealthScore: this.calculateFinancialHealthScore(financialData),
      marketSentimentScore: this.calculateMarketSentimentScore(marketData)
    };

    return scores;
  }

  /**
   * 计算估值得分
   */
  calculateValuationScore(valuationResult) {
    if (!valuationResult) return 50;

    // 安全边际越大，得分越高
    let score = 50;
    const marginOfSafety = valuationResult.marginOfSafety || 0;

    if (marginOfSafety >= 30) {
      score = 90 + Math.min(10, marginOfSafety - 30); // 30%以上安全边际得分90-100
    } else if (marginOfSafety >= 20) {
      score = 80 + (marginOfSafety - 20) * 1; // 20-30%安全边际得分80-90
    } else if (marginOfSafety >= 10) {
      score = 70 + (marginOfSafety - 10) * 1; // 10-20%安全边际得分70-80
    } else if (marginOfSafety >= 0) {
      score = 50 + marginOfSafety * 2; // 0-10%安全边际得分50-70
    } else if (marginOfSafety >= -10) {
      score = 50 + marginOfSafety * 2; // -10-0%安全边际得分30-50
    } else {
      score = Math.max(0, 30 + marginOfSafety); // -10%以下安全边际得分0-30
    }

    return Math.round(score);
  }

  /**
   * 计算成长性得分
   */
  calculateGrowthScore(financialData) {
    if (!financialData || financialData.length < 2) return 50;

    // 计算营收增长率
    const revenueGrowths = [];
    for (let i = 0; i < financialData.length - 1; i++) {
      if (financialData[i]?.revenue && financialData[i + 1]?.revenue && financialData[i + 1].revenue > 0) {
        const growth = (financialData[i].revenue - financialData[i + 1].revenue) / financialData[i + 1].revenue;
        revenueGrowths.push(growth);
      }
    }

    // 计算净利润增长率
    const profitGrowths = [];
    for (let i = 0; i < financialData.length - 1; i++) {
      if (financialData[i]?.net_profit && financialData[i + 1]?.net_profit && financialData[i + 1].net_profit > 0) {
        const growth = (financialData[i].net_profit - financialData[i + 1].net_profit) / financialData[i + 1].net_profit;
        profitGrowths.push(growth);
      }
    }

    // 计算平均增长率
    let avgRevenueGrowth = 0;
    if (revenueGrowths.length > 0) {
      avgRevenueGrowth = revenueGrowths.reduce((sum, growth) => sum + growth, 0) / revenueGrowths.length;
    }

    let avgProfitGrowth = 0;
    if (profitGrowths.length > 0) {
      avgProfitGrowth = profitGrowths.reduce((sum, growth) => sum + growth, 0) / profitGrowths.length;
    }

    // 综合计算成长得分
    const growthScore = (avgRevenueGrowth + avgProfitGrowth) / 2 * 100;
    return Math.min(100, Math.max(0, Math.round(50 + growthScore)));
  }

  /**
   * 计算财务健康得分
   */
  calculateFinancialHealthScore(financialData) {
    if (!financialData || financialData.length === 0) return 50;

    const latestData = financialData[0];
    let score = 0;

    // 净资产收益率（ROE）评分
    const roe = latestData?.roe || 0;
    if (roe >= 0.2) score += 30;
    else if (roe >= 0.15) score += 25;
    else if (roe >= 0.1) score += 20;
    else if (roe >= 0.05) score += 15;
    else score += 10;

    // 资产负债率评分
    const debtRatio = latestData?.debt_ratio || 1;
    if (debtRatio <= 0.4) score += 25;
    else if (debtRatio <= 0.5) score += 20;
    else if (debtRatio <= 0.6) score += 15;
    else if (debtRatio <= 0.7) score += 10;
    else score += 5;

    // 净利率评分
    const netMargin = latestData?.net_profit && latestData?.revenue && latestData.revenue > 0
      ? latestData.net_profit / latestData.revenue
      : 0;
    if (netMargin >= 0.2) score += 20;
    else if (netMargin >= 0.15) score += 15;
    else if (netMargin >= 0.1) score += 10;
    else if (netMargin >= 0.05) score += 5;

    // 现金流量评分
    const cashFlowRatio = latestData?.operating_cash_flow && latestData?.net_profit && latestData.net_profit > 0
      ? latestData.operating_cash_flow / latestData.net_profit
      : 0;
    if (cashFlowRatio >= 1.5) score += 25;
    else if (cashFlowRatio >= 1.2) score += 20;
    else if (cashFlowRatio >= 1.0) score += 15;
    else if (cashFlowRatio >= 0.8) score += 10;
    else score += 5;

    return Math.min(100, Math.round(score));
  }

  /**
   * 计算市场情绪得分
   */
  calculateMarketSentimentScore(marketData) {
    if (!marketData) return 50;

    // 简化的市场情绪评分，基于估值倍数
    let score = 50;
    const pe = marketData?.pe || 0;
    const pb = marketData?.pb || 0;

    // PE较低通常表示更好的价值
    if (pe > 0 && pe < 10) score += 20;
    else if (pe >= 10 && pe < 20) score += 10;
    else if (pe >= 30 && pe < 50) score -= 10;
    else if (pe >= 50) score -= 20;

    // PB较低通常表示更好的价值
    if (pb > 0 && pb < 1) score += 20;
    else if (pb >= 1 && pb < 2) score += 10;
    else if (pb >= 5 && pb < 10) score -= 10;
    else if (pb >= 10) score -= 20;

    return Math.min(100, Math.max(0, Math.round(score)));
  }

  /**
   * 计算综合得分
   */
  calculateTotalScore(scores) {
    // 加权平均，估值因素权重更高
    const weights = {
      valuationScore: 0.4,
      growthScore: 0.25,
      financialHealthScore: 0.25,
      marketSentimentScore: 0.1
    };

    let total = 0;
    for (const [key, weight] of Object.entries(weights)) {
      if (scores[key] !== undefined) {
        total += scores[key] * weight;
      }
    }

    return Math.round(total);
  }

  /**
   * 构建投资建议
   */
  buildAdvice(totalScore, scores, valuationResult) {
    let action, confidence, rationale, riskLevel, holdingPeriod;

    if (totalScore >= 85) {
      action = '强烈买入';
      confidence = '高';
      rationale = `估值得分(${scores.valuationScore})、成长性得分(${scores.growthScore})、财务健康得分(${scores.financialHealthScore})和市场情绪得分(${scores.marketSentimentScore})均表现优异。`;
      riskLevel = '低';
      holdingPeriod = '长期';
    } else if (totalScore >= 75) {
      action = '买入';
      confidence = '中高';
      rationale = `综合评分良好，尤其在${this.getBestScoreCategory(scores)}方面表现突出。`;
      riskLevel = '中低';
      holdingPeriod = '中长期';
    } else if (totalScore >= 65) {
      action = '持有';
      confidence = '中等';
      rationale = `综合评分一般，在${this.getWeakestScoreCategory(scores)}方面需要关注。`;
      riskLevel = '中等';
      holdingPeriod = '中期';
    } else if (totalScore >= 55) {
      action = '谨慎持有';
      confidence = '中低';
      rationale = `综合评分偏低，主要在${this.getWeakestScoreCategory(scores)}方面存在不足。`;
      riskLevel = '中高';
      holdingPeriod = '短期';
    } else {
      action = '卖出';
      confidence = '低';
      rationale = `综合评分较差，多项指标表现不佳，建议考虑减持。`;
      riskLevel = '高';
      holdingPeriod = '不建议持有';
    }

    // 添加安全边际相关建议
    if (valuationResult?.marginOfSafety) {
      const marginOfSafety = valuationResult.marginOfSafety;
      if (marginOfSafety > 20) {
        rationale += ` 当前安全边际超过20%，具有很好的投资价值。`;
      } else if (marginOfSafety > 0) {
        rationale += ` 当前安全边际为${marginOfSafety.toFixed(1)}%，具有一定投资价值。`;
      } else {
        rationale += ` 当前安全边际为${marginOfSafety.toFixed(1)}%，存在高估风险。`;
      }
    }

    return {
      action,
      confidence,
      rationale,
      riskLevel,
      holdingPeriod,
      totalScore
    };
  }

  /**
   * 获取得分最高的类别
   */
  getBestScoreCategory(scores) {
    let bestCategory = '';
    let bestScore = 0;
    
    const categories = {
      valuationScore: '估值',
      growthScore: '成长性',
      financialHealthScore: '财务健康',
      marketSentimentScore: '市场情绪'
    };

    for (const [key, score] of Object.entries(scores)) {
      if (score > bestScore) {
        bestScore = score;
        bestCategory = categories[key] || key;
      }
    }

    return bestCategory;
  }

  /**
   * 获取得分最低的类别
   */
  getWeakestScoreCategory(scores) {
    let weakestCategory = '';
    let weakestScore = 100;
    
    const categories = {
      valuationScore: '估值',
      growthScore: '成长性',
      financialHealthScore: '财务健康',
      marketSentimentScore: '市场情绪'
    };

    for (const [key, score] of Object.entries(scores)) {
      if (score < weakestScore) {
        weakestScore = score;
        weakestCategory = categories[key] || key;
      }
    }

    return weakestCategory;
  }

  /**
   * 保存建议到数据库
   */
  async saveAdvice(stockCode, totalScore, advice, scores) {
    const database = await getDB();
    return new Promise((resolve, reject) => {
      const sql = `
        INSERT INTO investment_advice 
        (stock_code, total_score, action, confidence, rationale, risk_level, 
         holding_period, valuation_score, growth_score, financial_health_score, 
         market_sentiment_score, created_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `;
      
      const params = [
        stockCode,
        totalScore,
        advice.action,
        advice.confidence,
        advice.rationale,
        advice.riskLevel,
        advice.holdingPeriod,
        scores.valuationScore,
        scores.growthScore,
        scores.financialHealthScore,
        scores.marketSentimentScore,
        new Date().toISOString()
      ];

      database.run(sql, params, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  /**
   * 获取历史投资建议
   */
  async getHistoricalAdvice(symbol, limit = 10) {
    const database = await getDB();
    return new Promise((resolve, reject) => {
      database.all(
        'SELECT * FROM investment_advice WHERE stock_code = ? ORDER BY created_at DESC LIMIT ?',
        [symbol, limit],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  /**
   * 批量获取投资建议
   */
  async getBatchAdvice(symbols) {
    const results = {};
    
    for (const symbol of symbols) {
      try {
        // 获取最新的估值结果
        const latestValuation = await this.getLatestValuation(symbol);
        
        if (latestValuation) {
          const advice = await this.generateInvestmentAdvice(symbol, latestValuation);
          results[symbol] = advice;
        } else {
          results[symbol] = { error: '没有找到估值数据' };
        }
      } catch (error) {
        console.error(`获取${symbol}的投资建议失败:`, error);
        results[symbol] = { error: error.message };
      }
    }
    
    return results;
  }

  /**
   * 获取最新估值结果
   */
  async getLatestValuation(symbol) {
    const database = await getDB();
    return new Promise((resolve, reject) => {
      database.get(
        'SELECT * FROM valuation_results WHERE stock_code = ? ORDER BY valuation_date DESC LIMIT 1',
        [symbol],
        (err, row) => {
          if (err) reject(err);
          else resolve(row);
        }
      );
    });
  }
}

// 导出单例实例
export default new InvestmentService();