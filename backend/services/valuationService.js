import { getDB } from '../config/db.js';

/**
 * 估值模型服务
 * 实现巴菲特DCF和FCF估值模型
 */
class ValuationService {
  constructor() {
    this.db = null;
    this.initializePromise = null;
  }

  async initialize() {
    if (!this.initializePromise) {
      this.initializePromise = this._initService();
    }
    return this.initializePromise;
  }

  async _initService() {
    try {
      this.db = await getDB();
      console.log('估值服务初始化成功');
      return this;
    } catch (error) {
      console.error('估值服务初始化失败:', error);
      throw error;
    }
  }

  /**
   * DCF估值模型（折现现金流模型）- 改进版
   * @param {Object} params - 估值参数
   * @returns {Object} 估值结果
   */
  calculateDCF(params) {
    const {
      freeCashFlow,
      growthRate = 0.1, // 默认10%增长率
      discountRate = 0.15, // 默认15%折现率（巴菲特推荐）
      terminalGrowthRate = 0.03, // 永续增长率3%
      years = 10, // 预测10年
      taxRate = 0.25,
      capexRate = 0.15
    } = params;

    let presentValue = 0;
    const cashFlows = [];
    
    // 计算未来10年的现金流现值（考虑增长率逐步下降）
    for (let i = 1; i <= years; i++) {
      // 模拟增长率逐步下降的过程
      let yearGrowthRate = growthRate * (1 - (i * 0.05)); // 每年增长率下降5%
      yearGrowthRate = Math.max(yearGrowthRate, terminalGrowthRate);
      
      const futureFCF = freeCashFlow * Math.pow(1 + yearGrowthRate, i);
      const discountFactor = Math.pow(1 + discountRate, i);
      const cashFlowPV = futureFCF / discountFactor;
      presentValue += cashFlowPV;
      
      cashFlows.push({
        year: i,
        fcf: futureFCF,
        presentValue: cashFlowPV,
        growthRate: yearGrowthRate
      });
    }

    // 计算终值
    const terminalValue = freeCashFlow * Math.pow(1 + growthRate, years) * (1 + terminalGrowthRate) / 
                         (discountRate - terminalGrowthRate);
    const presentTerminalValue = terminalValue / Math.pow(1 + discountRate, years);

    // 计算总内在价值
    const intrinsicValue = presentValue + presentTerminalValue;

    return {
      freeCashFlow,
      growthRate,
      discountRate,
      terminalGrowthRate,
      years,
      presentValue,
      terminalValue,
      presentTerminalValue,
      intrinsicValue,
      cashFlows
    };
  }

  /**
   * FCF估值模型（自由现金流估值）- 改进版
   * @param {Object} params - 估值参数
   * @returns {Object} 估值结果
   */
  calculateFCF(params) {
    const {
      freeCashFlow,
      fcfGrowthRate = 0.12, // FCF增长率
      wacc = 0.14, // 加权平均资本成本
      sharesOutstanding = 1, // 总股数
      fcfMultiple = 20 // FCF乘数
    } = params;

    // 使用增长率计算企业价值
    const enterpriseValue = freeCashFlow * (1 + fcfGrowthRate) / (wacc - fcfGrowthRate);
    
    // 使用乘数法计算企业价值
    const multipleBasedValue = freeCashFlow * fcfMultiple;
    
    // 综合两种方法的结果
    const finalEnterpriseValue = (enterpriseValue + multipleBasedValue) / 2;

    // 计算每股价值
    const perShareValue = finalEnterpriseValue / sharesOutstanding;

    return {
      freeCashFlow,
      fcfGrowthRate,
      wacc,
      sharesOutstanding,
      fcfMultiple,
      enterpriseValue,
      multipleBasedValue,
      finalEnterpriseValue,
      perShareValue
    };
  }

  /**
   * 巴菲特风格DCF估值模型
   * 基于巴菲特的投资理念和回报率要求
   */
  calculateBuffettDCF(params) {
    const {
      netIncome,
      roe = 0.15,
      requiredReturn = 0.15, // 巴菲特要求的15%回报率
      growthYears = 10,
      marginOfSafety = 0.30, // 30%安全边际
      moatFactor = 1.0 // 护城河系数（1.0-1.5）
    } = params;

    // 计算可持续增长率（ROE * 留存收益率）
    const retentionRate = 0.7; // 假设70%的留存率
    const sustainableGrowthRate = roe * retentionRate;
    
    // 计算10年后的价值
    let futureValue = netIncome;
    for (let i = 1; i <= growthYears; i++) {
      // 增长率随时间递减
      const yearGrowthRate = sustainableGrowthRate * (1 - (i * 0.04));
      futureValue = futureValue * (1 + yearGrowthRate);
    }
    
    // 使用合理PE倍数计算终值
    const terminalPE = 18; // 巴菲特偏好的合理PE
    const terminalValue = futureValue * terminalPE;
    
    // 折现到现在
    const presentValue = terminalValue / Math.pow(1 + requiredReturn, growthYears);
    
    // 应用护城河因子和安全边际
    const intrinsicValueWithMoat = presentValue * moatFactor;
    const intrinsicValueWithSafety = intrinsicValueWithMoat * (1 - marginOfSafety);

    return {
      netIncome,
      roe,
      requiredReturn,
      growthYears,
      marginOfSafety,
      moatFactor,
      sustainableGrowthRate,
      futureValue,
      terminalValue,
      intrinsicValue: intrinsicValueWithMoat,
      intrinsicValueWithSafety,
      terminalPE
    };
  }

  /**
   * 综合估值（结合DCF和FCF）
   * @param {string} symbol - 股票代码
   * @param {Object} params - 估值参数
   * @returns {Object} 综合估值结果
   */
  async calculateValuation(symbol, params = {}) {
    try {
      if (!this.db) await this.initialize();

      // 获取最新财务数据
      const financialData = await this.getLatestFinancialData(symbol);
      
      if (!financialData) {
        throw new Error(`未找到股票 ${symbol} 的财务数据`);
      }

      // 使用财务数据和用户提供的参数进行估值
      const valuationParams = {
        freeCashFlow: financialData.free_cash_flow || params.freeCashFlow || 100,
        netIncome: financialData.net_income || params.netIncome || 50,
        roe: financialData.roe || params.roe || 0.15,
        growthRate: params.growthRate || 0.1,
        discountRate: params.discountRate || 0.15,
        terminalGrowthRate: params.terminalGrowthRate || 0.03,
        fcfGrowthRate: params.fcfGrowthRate || 0.12,
        wacc: params.wacc || 0.14,
        sharesOutstanding: params.sharesOutstanding || 1,
        fcfMultiple: params.fcfMultiple || 20,
        marginOfSafety: params.marginOfSafety || 0.3,
        moatFactor: params.moatFactor || 1.0
      };

      // 执行DCF估值
      const dcfResult = this.calculateDCF(valuationParams);
      
      // 执行FCF估值
      const fcfResult = this.calculateFCF(valuationParams);
      
      // 执行巴菲特风格DCF估值
      const buffettResult = this.calculateBuffettDCF(valuationParams);

      // 获取最新股价（如果有）
      const latestPrice = await this.getLatestPrice(symbol);

      // 权重配置
      const weights = {
        dcf: params.weights?.dcf || 0.4,
        fcf: params.weights?.fcf || 0.3,
        buffett: params.weights?.buffett || 0.3
      };
      
      // 计算加权平均内在价值
      const dcfPerShare = dcfResult.intrinsicValue / valuationParams.sharesOutstanding;
      const intrinsicValue = (
        dcfPerShare * weights.dcf +
        fcfResult.perShareValue * weights.fcf +
        buffettResult.intrinsicValueWithSafety / valuationParams.sharesOutstanding * weights.buffett
      );
      
      // 计算安全边际
      const marginOfSafety = latestPrice ? 
        ((intrinsicValue - latestPrice) / latestPrice * 100) : null;

      // 生成投资建议
      let recommendation = null;
      let confidence = '中等';
      
      if (marginOfSafety !== null) {
        if (marginOfSafety > 50) {
          recommendation = '强烈买入';
          confidence = '高';
        } else if (marginOfSafety > 30) {
          recommendation = '买入';
          confidence = '中高';
        } else if (marginOfSafety > 15) {
          recommendation = '观望';
          confidence = '中等';
        } else if (marginOfSafety > -10) {
          recommendation = '谨慎';
          confidence = '低';
        } else {
          recommendation = '避免';
          confidence = '高';
        }
      }
      
      // 保存估值结果
      const valuationResult = {
        symbol,
        valuationDate: new Date(),
        dcfValue: dcfPerShare,
        fcfValue: fcfResult.perShareValue,
        buffettValue: buffettResult.intrinsicValueWithSafety / valuationParams.sharesOutstanding,
        fcfGrowthRate: valuationParams.fcfGrowthRate,
        discountRate: valuationParams.discountRate,
        roe: valuationParams.roe,
        intrinsicValue,
        currentPrice: latestPrice,
        marginOfSafety,
        recommendation,
        confidence,
        parameters: JSON.stringify(params)
      };

      await this.saveValuationResult(valuationResult);

      return {
        symbol,
        valuationDate: valuationResult.valuationDate,
        dcf: dcfResult,
        fcf: fcfResult,
        buffett: buffettResult,
        intrinsicValue,
        currentPrice: latestPrice,
        marginOfSafety,
        recommendation,
        confidence,
        weights
      };
    } catch (error) {
      console.error(`计算股票 ${symbol} 估值失败:`, error);
      throw error;
    }
  }

  /**
   * 获取股票最新财务数据
   */
  async getLatestFinancialData(symbol) {
    const db = await getDB();
    const sql = `
      SELECT * FROM company_financial_data 
      WHERE symbol = ? 
      ORDER BY fiscal_year DESC, fiscal_quarter DESC 
      LIMIT 1
    `;
    const result = await db.get(sql, [symbol]);
    return result;
  }

  /**
   * 获取股票最新价格
   */
  async getLatestPrice(symbol) {
    const db = await getDB();
    const sql = `
      SELECT current FROM stock_quotes 
      WHERE symbol = ? 
      ORDER BY quote_date DESC 
      LIMIT 1
    `;
    const result = await db.get(sql, [symbol]);
    return result ? result.current : null;
  }

  /**
   * 保存估值结果
   */
  async saveValuationResult(result) {
    const db = await getDB();
    const sql = `
      INSERT INTO valuation_results 
      (symbol, valuation_date, dcf_value, fcf_value, buffett_value, 
       fcf_growth_rate, discount_rate, roe, intrinsic_value, 
       current_price, margin_of_safety, recommendation, confidence, parameters)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    await db.run(sql, [
      result.symbol,
      result.valuationDate,
      result.dcfValue,
      result.fcfValue || null,
      result.buffettValue || null,
      result.fcfGrowthRate,
      result.discountRate,
      result.roe || null,
      result.intrinsicValue,
      result.currentPrice || null,
      result.marginOfSafety || null,
      result.recommendation || null,
      result.confidence || null,
      result.parameters || '{}'
    ]);
  }

  /**
   * 批量导入财务数据
   */
  async importFinancialData(data) {
    const db = await getDB();
    
    for (const record of data) {
      const sql = `
        INSERT OR REPLACE INTO company_financial_data 
        (symbol, fiscal_year, fiscal_quarter, total_revenue, 
         net_income, free_cash_flow, total_equity, roe)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `;
      await db.run(sql, [
        record.symbol,
        record.fiscal_year,
        record.fiscal_quarter || 0,
        record.total_revenue || 0,
        record.net_income || 0,
        record.free_cash_flow || 0,
        record.total_equity || 0,
        record.roe || 0
      ]);
    }
    
    return { success: true, imported: data.length };
  }

  /**
   * 手动输入财务数据
   */
  async addFinancialData(data) {
    return this.importFinancialData([data]);
  }

  /**
   * 获取估值历史记录
   */
  async getValuationHistory(symbol) {
    const db = await getDB();
    const sql = `
      SELECT * FROM valuation_results 
      WHERE symbol = ? 
      ORDER BY valuation_date DESC
      LIMIT 50
    `;
    const results = await db.all(sql, [symbol]);
    
    // 解析参数JSON
    return results.map(row => ({
      ...row,
      parameters: row.parameters ? JSON.parse(row.parameters) : {}
    }));
  }

  /**
   * 获取历史财务数据用于趋势分析
   */
  async getHistoricalFinancialData(symbol, years = 5) {
    const db = await getDB();
    const sql = `
      SELECT * FROM company_financial_data 
      WHERE symbol = ? 
      ORDER BY fiscal_year DESC, fiscal_quarter DESC 
      LIMIT ?
    `;
    const results = await db.all(sql, [symbol, years]);
    return results;
  }

  /**
   * 获取估值指标数据
   */
  async getValuationData(symbol) {
    try {
      // 使用模拟数据提供估值指标
      return {
        success: true,
        data: {
          peTTM: (Math.random() * 50 + 5).toFixed(2),
          pbMRQ: (Math.random() * 10 + 1).toFixed(2),
          psTTM: (Math.random() * 5 + 0.5).toFixed(2),
          dividendRate: (Math.random() * 8).toFixed(2),
          pegRatio: (Math.random() * 3).toFixed(2),
          evToEbitda: (Math.random() * 30 + 5).toFixed(2),
          pePercentile: Math.floor(Math.random() * 100).toString(),
          pbPercentile: Math.floor(Math.random() * 100).toString()
        }
      };
    } catch (error) {
      console.error('获取估值指标失败:', error);
      throw error;
    }
  }

  /**
   * 获取基本面数据
   */
  async getFundamentalData(symbol) {
    try {
      // 使用模拟数据提供基本面分析数据
      return {
        success: true,
        data: {
          revenueGrowth: (Math.random() * 50 - 10).toFixed(2),
          netProfitGrowth: (Math.random() * 60 - 15).toFixed(2),
          grossMarginChange: (Math.random() * 10 - 5).toFixed(2),
          netMarginChange: (Math.random() * 8 - 4).toFixed(2),
          roe: (Math.random() * 30).toFixed(2),
          roa: (Math.random() * 15).toFixed(2),
          roic: (Math.random() * 25).toFixed(2),
          debtToAsset: (Math.random() * 80).toFixed(2),
          currentRatio: (Math.random() * 5 + 0.5).toFixed(2),
          quickRatio: (Math.random() * 4 + 0.2).toFixed(2),
          operatingCashFlow: (Math.random() * 10000 + 1000).toFixed(2),
          operatingCashFlowTrend: Math.random() > 0.5 ? 1 : -1
        }
      };
    } catch (error) {
      console.error('获取基本面数据失败:', error);
      throw error;
    }
  }

  /**
   * 获取事件数据
   */
  async getEventsData(symbol) {
    try {
      // 使用模拟数据提供事件分析数据
      const impactLevels = ['high', 'medium', 'low'];
      const eventTypes = ['财报发布', '股东大会', '资产重组', '股权激励', '业绩预告', '产品发布'];
      
      const events = [];
      const now = new Date();
      
      for (let i = 0; i < 5; i++) {
        const date = new Date(now.getTime() - i * 7 * 24 * 60 * 60 * 1000); // 过去几周的事件
        events.push({
          id: `event_${i}_${Date.now()}`,
          title: `${eventTypes[Math.floor(Math.random() * eventTypes.length)]}公告`,
          content: `公司发布了重要公告，涉及公司业务发展的重大事项。这可能对公司未来的发展产生积极影响。`,
          date: date.toISOString(),
          impact: impactLevels[Math.floor(Math.random() * impactLevels.length)]
        });
      }
      
      return {
        success: true,
        data: events
      };
    } catch (error) {
      console.error('获取事件数据失败:', error);
      throw error;
    }
  }
}

// 导出单例实例
export default new ValuationService();