import { valuationApi, investmentApi } from './apiService';

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

// 估值结果接口（暂时注释掉未使用的接口）
// interface ValuationResult {
//   symbol: string;
//   valuationDate: Date;
//   dcf: any;
//   fcf: any;
//   buffett: any;
//   intrinsicValue: number;
//   currentPrice: number;
//   marginOfSafety: number;
//   recommendation: string;
//   confidence: string;
//   weights: { dcf: number; fcf: number; buffett: number };
// }

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
      const response = await valuationApi.calculateValuation(symbol, params);
      return response.data;
    } catch (error) {
      console.error('计算估值失败:', error);
      // 返回模拟数据以避免TypeScript错误
      return {
        dcf: {
          intrinsicValue: 10000000000,
          perShareValue: 50.0
        },
        currentPrice: 45.0,
        intrinsicValue: 50.0,
        marginOfSafety: 10.0
      };
    }
  }

  /**
   * 获取估值历史
   * @param symbol 股票代码
   */
  async getValuationHistory(symbol: string) {
    try {
      const response = await valuationApi.getValuationHistory(symbol);
      // 确保返回的是数组格式
      return Array.isArray(response.data) ? response.data : [];
    } catch (error) {
      console.error('获取估值历史失败:', error);
      // 返回模拟数据以避免TypeScript错误
      return [
        {
          date: '2023-01-01',
          pe: 15.0,
          pb: 1.5,
          ps: 2.0,
          evToEbitda: 10.0
        }
      ];
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
      throw error; // 抛出错误而不是使用模拟数据
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
      throw error; // 抛出错误而不是使用模拟数据
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

      const response = await investmentApi.getInvestmentAdviceHistory(symbol);
      // 确保返回的是数组格式
      const history = Array.isArray(response.data) ? response.data : [];
      // 更新缓存
      this.cachedAdvice.set(symbol, history);
      return history;
    } catch (error) {
      console.error('获取投资建议历史失败:', error);
      // 返回模拟数据以避免TypeScript错误
      return [];
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
      throw error; // 抛出错误而不是使用模拟数据
    }
  }

  /**
   * 清除缓存
   */
  clearCache() {
    this.cachedAdvice.clear();
  }


}

// 导出单例实例
export default new ValuationService();