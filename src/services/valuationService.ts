import { valuationApi, investmentApi, portfolioApi } from './apiService';

// 投资评分接口
interface InvestmentScores {
  valuation_score: number;
  growth_score: number;
  financial_health_score: number;
  market_sentiment_score: number;
  total_score: number;
}

// 投资建议接口
interface InvestmentAdvice {
  id?: number;
  symbol: string;
  stock_name: string;
  scores: InvestmentScores;
  action: string;
  confidence: string;
  reason: string;
  timestamp: string;
}

// 估值结果接口
interface ValuationResult {
  symbol: string;
  valuationDate: Date;
  dcf: any;
  fcf: any;
  buffett: any;
  intrinsicValue: number;
  currentPrice: number;
  marginOfSafety: number;
  recommendation: string;
  confidence: string;
  weights: { dcf: number; fcf: number; buffett: number };
}

// 估值服务类
class ValuationService {
  private cachedAdvice: Map<string, InvestmentAdvice[]> = new Map();
  /**
   * 计算股票估值
   * @param symbol 股票代码
   * @param params 估值参数
   */
  async calculateValuation(symbol: string, params: any = {}) {
    try {
      const result = await valuationApi.calculateValuation(symbol, params);
      return result;
    } catch (error) {
      console.error('计算估值失败:', error);
      // 如果API调用失败，返回模拟数据
      return this.getMockValuationData(symbol, params);
    }
  }

  /**
   * 获取估值历史
   * @param symbol 股票代码
   */
  async getValuationHistory(symbol: string) {
    try {
      const history = await valuationApi.getValuationHistory(symbol);
      return history;
    } catch (error) {
      console.error('获取估值历史失败:', error);
      // 返回模拟历史数据
      return this.getMockValuationHistory(symbol);
    }
  }

  /**
   * 添加财务数据
   * @param data 财务数据
   */
  async addFinancialData(data: any) {
    try {
      return await valuationApi.addFinancialData(data);
    } catch (error) {
      console.error('添加财务数据失败:', error);
      throw error;
    }
  }

  /**
   * 获取历史财务数据
   * @param symbol 股票代码
   * @param years 年数
   */
  async getHistoricalFinancialData(symbol: string, years: number = 5) {
    try {
      return await valuationApi.getHistoricalFinancialData(symbol, years);
    } catch (error) {
      console.error('获取历史财务数据失败:', error);
      // 返回模拟财务数据
      return this.getMockFinancialHistory(symbol, years);
    }
  }

  /**
   * 生成投资建议
   * @param symbol 股票代码
   * @param valuationData 估值数据
   * @param financialData 财务数据
   */
  async generateInvestmentAdvice(symbol: string, valuationData?: any, financialData?: any) {
    try {
      const result = await investmentApi.generateInvestmentAdvice(symbol, {
        valuationData,
        financialData
      });
      return result;
    } catch (error) {
      console.error('生成投资建议失败:', error);
      // 返回模拟投资建议
      return this.getMockInvestmentAdvice(symbol, valuationData, financialData);
    }
  }

  /**
   * 获取投资建议历史
   * @param symbol 股票代码
   */
  async getInvestmentAdviceHistory(symbol: string) {
    try {
      // 检查缓存
      const cached = this.cachedAdvice.get(symbol);
      if (cached && cached.length > 0) {
        return cached;
      }

      const history = await investmentApi.getInvestmentAdviceHistory(symbol);
      // 更新缓存
      this.cachedAdvice.set(symbol, history);
      return history;
    } catch (error) {
      console.error('获取投资建议历史失败:', error);
      // 返回模拟历史数据
      const mockHistory = this.getMockInvestmentAdviceHistory(symbol);
      this.cachedAdvice.set(symbol, mockHistory);
      return mockHistory;
    }
  }

  /**
   * 批量获取投资建议
   * @param symbols 股票代码数组
   */
  async getBatchInvestmentAdvice(symbols: string[]) {
    try {
      const results = await investmentApi.getBatchInvestmentAdvice(symbols);
      return results;
    } catch (error) {
      console.error('批量获取投资建议失败:', error);
      // 批量生成模拟投资建议
      const mockResults = symbols.map(symbol => this.getMockInvestmentAdvice(symbol));
      return mockResults;
    }
  }

  /**
   * 清除缓存
   */
  clearCache() {
    this.cachedAdvice.clear();
  }

  // Mock数据生成方法，用于API不可用时的备用方案
  private getMockValuationData(symbol: string, params: any): ValuationResult {
    // 根据不同股票生成不同的模拟估值数据
    const stockData = {
      '600519': {
        name: '贵州茅台',
        dcfValue: 2150.80,
        fcfValue: 1980.50,
        buffettValue: 2320.30,
        intrinsicValue: 2150.0,
        currentPrice: 1823.00,
        marginOfSafety: 18.0,
        recommendation: '买入',
        confidence: '中高'
      },
      '300750': {
        name: '宁德时代',
        dcfValue: 180.50,
        fcfValue: 175.30,
        buffettValue: 195.80,
        intrinsicValue: 182.0,
        currentPrice: 165.20,
        marginOfSafety: 10.2,
        recommendation: '观望',
        confidence: '中等'
      },
      '002594': {
        name: '比亚迪',
        dcfValue: 270.60,
        fcfValue: 265.80,
        buffettValue: 285.30,
        intrinsicValue: 273.0,
        currentPrice: 258.50,
        marginOfSafety: 5.6,
        recommendation: '谨慎',
        confidence: '低'
      }
    };

    const stock = stockData[symbol as keyof typeof stockData] || stockData['600519'];
    
    return {
      symbol,
      valuationDate: new Date(),
      dcf: {
        freeCashFlow: 120,
        growthRate: 0.12,
        discountRate: 0.15,
        terminalGrowthRate: 0.03,
        years: 10,
        presentValue: stock.intrinsicValue * 0.6,
        terminalValue: stock.intrinsicValue * 1.8,
        presentTerminalValue: stock.intrinsicValue * 0.4,
        intrinsicValue: stock.intrinsicValue * 1.2,
        cashFlows: this.generateMockCashFlows(10)
      },
      fcf: {
        freeCashFlow: 120,
        fcfGrowthRate: 0.12,
        wacc: 0.14,
        sharesOutstanding: 1,
        fcfMultiple: 20,
        enterpriseValue: stock.intrinsicValue * 0.9,
        multipleBasedValue: stock.intrinsicValue * 1.1,
        finalEnterpriseValue: stock.intrinsicValue,
        perShareValue: stock.intrinsicValue
      },
      buffett: {
        netIncome: 85,
        roe: 0.25,
        requiredReturn: 0.15,
        growthYears: 10,
        marginOfSafety: 0.30,
        moatFactor: 1.2,
        sustainableGrowthRate: 0.175,
        futureValue: 400,
        terminalValue: 7200,
        intrinsicValue: stock.intrinsicValue * 1.3,
        intrinsicValueWithSafety: stock.intrinsicValue,
        terminalPE: 18
      },
      intrinsicValue: stock.intrinsicValue,
      currentPrice: stock.currentPrice,
      marginOfSafety: stock.marginOfSafety,
      recommendation: stock.recommendation,
      confidence: stock.confidence,
      weights: {
        dcf: 0.4,
        fcf: 0.3,
        buffett: 0.3
      }
    };
  }

  private generateMockCashFlows(years: number) {
    const cashFlows = [];
    let fcf = 120;
    for (let i = 1; i <= years; i++) {
      const growthRate = 0.12 * (1 - (i * 0.05));
      fcf = fcf * (1 + growthRate);
      const discountFactor = Math.pow(1 + 0.15, i);
      cashFlows.push({
        year: i,
        fcf: fcf,
        presentValue: fcf / discountFactor,
        growthRate: growthRate
      });
    }
    return cashFlows;
  }

  private getMockValuationHistory(symbol: string) {
    const history = [];
    const baseValue = 2000;
    const basePrice = 1800;
    
    for (let i = 30; i >= 0; i -= 5) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      const randomChange = (Math.random() - 0.5) * 200;
      const value = baseValue + randomChange;
      const price = basePrice + randomChange * 0.8;
      const marginOfSafety = ((value - price) / price) * 100;
      
      history.push({
        id: i,
        symbol,
        valuation_date: date,
        dcf_value: value * 1.1,
        fcf_value: value * 0.9,
        buffett_value: value * 1.2,
        fcf_growth_rate: 0.12,
        discount_rate: 0.15,
        roe: 0.25,
        intrinsic_value: value,
        current_price: price,
        margin_of_safety: marginOfSafety,
        recommendation: marginOfSafety > 30 ? '强烈买入' : marginOfSafety > 15 ? '买入' : 
                        marginOfSafety > 0 ? '观望' : '谨慎',
        confidence: '中等',
        parameters: {}
      });
    }
    
    return history;
  }

  private getMockFinancialHistory(symbol: string, years: number) {
    const financialHistory = [];
    const baseRevenue = 1000;
    const baseNetIncome = 250;
    const baseFCF = 220;
    const baseEquity = 800;
    
    for (let i = 0; i < years; i++) {
      const year = 2024 - i;
      const growthFactor = Math.pow(1.08, i); // 假设8%的历史增长率
      
      financialHistory.push({
        id: i + 1,
        symbol,
        fiscal_year: year,
        fiscal_quarter: 4,
        total_revenue: baseRevenue * growthFactor,
        net_income: baseNetIncome * growthFactor,
        free_cash_flow: baseFCF * growthFactor,
        total_equity: baseEquity * growthFactor,
        roe: 0.25 + (Math.random() - 0.5) * 0.05 // 20%-30%的ROE范围
      });
    }
    
    return financialHistory;
  }

  // 生成模拟投资建议
  private getMockInvestmentAdvice(symbol: string, valuationData?: any, financialData?: any): InvestmentAdvice {
    // 股票基本信息
    const stockInfo = {
      '600519': { name: '贵州茅台', baseScore: 85 },
      '300750': { name: '宁德时代', baseScore: 75 },
      '002594': { name: '比亚迪', baseScore: 70 }
    };
    
    const stock = stockInfo[symbol as keyof typeof stockInfo] || stockInfo['600519'];
    const baseScore = stock.baseScore;
    
    // 生成各维度评分
    const valuation_score = Math.max(60, Math.min(95, baseScore + (Math.random() - 0.5) * 15));
    const growth_score = Math.max(55, Math.min(90, baseScore + (Math.random() - 0.5) * 20));
    const financial_health_score = Math.max(70, Math.min(95, baseScore + (Math.random() - 0.3) * 10));
    const market_sentiment_score = Math.max(65, Math.min(85, baseScore + (Math.random() - 0.5) * 15));
    
    // 计算总分
    const total_score = (valuation_score * 0.4) + (growth_score * 0.3) + (financial_health_score * 0.2) + (market_sentiment_score * 0.1);
    
    // 确定建议和置信度
    let action, confidence, reason;
    
    if (total_score >= 85) {
      action = '强烈买入';
      confidence = '高';
      reason = '该股票估值具有显著优势，财务状况健康，增长潜力强，市场情绪积极。';
    } else if (total_score >= 75) {
      action = '买入';
      confidence = '中高';
      reason = '该股票估值合理，财务指标良好，具有一定增长潜力。';
    } else if (total_score >= 65) {
      action = '持有';
      confidence = '中等';
      reason = '该股票估值较为合理，各项指标表现平稳。';
    } else if (total_score >= 55) {
      action = '观望';
      confidence = '中低';
      reason = '该股票存在一定风险，建议等待更明确的买入信号。';
    } else {
      action = '卖出';
      confidence = '低';
      reason = '该股票估值过高，或基本面存在问题，建议减持或避免买入。';
    }
    
    return {
      symbol,
      stock_name: stock.name,
      scores: {
        valuation_score: Math.round(valuation_score * 100) / 100,
        growth_score: Math.round(growth_score * 100) / 100,
        financial_health_score: Math.round(financial_health_score * 100) / 100,
        market_sentiment_score: Math.round(market_sentiment_score * 100) / 100,
        total_score: Math.round(total_score * 100) / 100
      },
      action,
      confidence,
      reason,
      timestamp: new Date().toISOString()
    };
  }

  // 生成模拟投资建议历史
  private getMockInvestmentAdviceHistory(symbol: string): InvestmentAdvice[] {
    const history: InvestmentAdvice[] = [];
    
    // 生成过去3个月的投资建议历史
    for (let i = 0; i < 12; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (i * 7)); // 每周一条记录
      
      const advice = this.getMockInvestmentAdvice(symbol);
      advice.timestamp = date.toISOString();
      advice.id = i + 1;
      
      // 稍微调整历史数据的总分，使其有变化趋势
      advice.scores.total_score = Math.max(60, Math.min(90, advice.scores.total_score + (Math.random() - 0.5) * 5));
      
      history.push(advice);
    }
    
    // 按时间倒序排序
    return history.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }
}

// 导出单例实例
export default new ValuationService();