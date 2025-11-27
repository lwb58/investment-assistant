import tushareApi from './tushareApi.js';
import eastmoneyApi from './eastmoneyApi.js';
import sinacnApi from './sinacnApi.js';
import baostockApi from './baostockApi.js';
import dtshareApi from './dtshareApi.js';

/**
 * 股票数据API集成客户端
 * 整合多个数据源的股票数据接口，提供统一访问和故障转移功能
 */
class StockApi {
  constructor() {
    this.dataSources = {
      tushare: tushareApi,
      dtshare: dtshareApi,
      eastmoney: eastmoneyApi,
      sinacn: sinacnApi,
      baostock: baostockApi
    };
    // 设置默认数据源优先级
    this.priorityOrder = ['tushare', 'dtshare', 'eastmoney', 'sinacn', 'baostock'];
    // 为了向后兼容，也设置apis属性
    this.apis = this.dataSources;
  }

  /**
   * 配置API参数
   * @param {Object} config - 配置对象
   */
  configure(config) {
    if (config.tushareToken && this.dataSources.tushare) {
      this.dataSources.tushare.setToken(config.tushareToken);
    }
    if (config.apiOrder) {
      this.priorityOrder = config.apiOrder;
    }
  }

  /**
   * 使用故障转移机制调用多个API
   * @param {string} method - 要调用的方法名
   * @param {Array} params - 方法参数数组
   * @param {Array} apiOrder - API调用顺序（可选）
   * @returns {Promise<any>} 调用结果
   */
  async callWithFallback(method, params = [], apiOrder = this.priorityOrder) {
    const errors = [];
    
    for (const apiName of apiOrder) {
      const api = this.dataSources[apiName];
      if (!api || !api[method]) {
        continue;
      }
      
      try {
        console.log(`尝试使用${apiName}的${method}方法`);
        const result = await api[method](...params);
        if (result !== null && result !== undefined) {
          // 对于返回对象，检查是否有有意义的数据
          if (typeof result === 'object' && !Array.isArray(result)) {
            if (Object.keys(result).length === 0 || 
                (result.data && result.data.length === 0)) {
              errors.push(`${apiName}: 返回空数据`);
              continue;
            }
          }
          // 对于返回数组，检查是否有数据
          if (Array.isArray(result) && result.length === 0) {
            errors.push(`${apiName}: 返回空数据`);
            continue;
          }
          return result;
        }
        errors.push(`${apiName}: 返回空数据`);
      } catch (error) {
        console.error(`${apiName}调用${method}失败:`, error.message);
        errors.push(`${apiName}: ${error.message}`);
      }
    }
    
    throw new Error(`所有数据源调用${method}失败: ${errors.join('; ')}`);
  }

  /**
   * 获取股票实时行情
   * @param {string} stockCode - 股票代码
   * @returns {Promise<Object>} 股票行情数据
   */
  async getStockQuote(stockCode) {
    return this.callWithFallback('getStockQuote', [stockCode]);
  }

  /**
   * 批量获取股票行情
   * @param {Array<string>} stockCodes - 股票代码数组
   * @returns {Promise<Object>} 股票行情对象，键为股票代码
   */
  async getBatchStockQuotes(stockCodes) {
    // 优先使用sinacn的批量查询功能
    return this.callWithFallback('getBatchStockQuotes', [stockCodes], ['sinacn']);
  }

  /**
   * 获取大盘指数数据
   * @param {string} indexCode - 指数代码
   * @returns {Promise<Object>} 指数数据
   */
  async getIndexQuote(indexCode) {
    return this.callWithFallback('getIndexQuote', [indexCode]);
  }

  /**
   * 获取股票基本信息
   * @param {string} code - 股票代码
   */
  async getStockBasicInfo(code) {
    return this.callWithFallback('getStockBasicInfo', [code]);
  }

  /**
   * 获取历史K线数据
   * @param {string} code - 股票代码
   * @param {string} startDate - 开始日期
   * @param {string} endDate - 结束日期
   * @param {string} frequency - 数据频率
   */
  async getHistoricalKData(code, startDate, endDate, frequency = 'd') {
    // 对于历史K线数据，我们使用自定义的fallback逻辑，因为不同API的参数可能有所不同
    const errors = [];
    
    // 优先使用tushare获取K线数据
    try {
      const data = await this.dataSources.tushare.getHistoricalKData(code, startDate, endDate, frequency);
      if (data && data.length > 0) {
        return data;
      }
      errors.push('tushare: 返回空数据');
    } catch (error) {
      console.error('Tushare获取K线数据失败:', error.message);
      errors.push(`tushare: ${error.message}`);
    }
    
    // 尝试dtshare (注意参数转换)
    try {
      const freqMap = { 'd': 'D', 'w': 'W', 'm': 'M' };
      const dtshareFreq = freqMap[frequency.toLowerCase()] || 'D';
      
      const data = await this.dataSources.dtshare.getHistoricalData(
        code,
        startDate || '2020-01-01',
        endDate || new Date().toISOString().split('T')[0],
        dtshareFreq
      );
      
      if (data && data.data && data.data.length > 0) {
        return data.data;
      }
      errors.push('dtshare: 返回空数据');
    } catch (error) {
      console.error('Dtshare获取K线数据失败:', error.message);
      errors.push(`dtshare: ${error.message}`);
    }
    
    // 尝试baostock
    try {
      if (this.dataSources.baostock && this.dataSources.baostock.getHistoricalKData) {
        const data = await this.dataSources.baostock.getHistoricalKData(code, startDate, endDate, frequency);
        if (data && data.length > 0) {
          return data;
        }
        errors.push('baostock: 返回空数据');
      }
    } catch (error) {
      console.error('Baostock获取K线数据失败:', error.message);
      errors.push(`baostock: ${error.message}`);
    }
    
    // 尝试eastmoney
    try {
      if (this.dataSources.eastmoney && this.dataSources.eastmoney.getHistoricalKData) {
        const data = await this.dataSources.eastmoney.getHistoricalKData(code, startDate, endDate, frequency);
        if (data && data.length > 0) {
          return data;
        }
        errors.push('eastmoney: 返回空数据');
      }
    } catch (error) {
      console.error('Eastmoney获取K线数据失败:', error.message);
      errors.push(`eastmoney: ${error.message}`);
    }
    
    // 尝试sinacn
    try {
      if (this.dataSources.sinacn && this.dataSources.sinacn.getHistoricalKData) {
        const data = await this.dataSources.sinacn.getHistoricalKData(code, startDate, endDate, frequency);
        if (data && data.length > 0) {
          return data;
        }
        errors.push('sinacn: 返回空数据');
      }
    } catch (error) {
      console.error('Sinacn获取K线数据失败:', error.message);
      errors.push(`sinacn: ${error.message}`);
    }
    
    throw new Error(`所有数据源获取历史K线数据失败: ${errors.join('; ')}`);
  }

  /**
   * 获取股票财务指标数据
   * @param {string} code - 股票代码
   * @param {Object} options - 查询选项（year, quarter）
   * @returns {Promise<Object>} 财务指标数据
   */
  async getFinancialIndicators(code, options = {}) {
    // 尝试多个数据源获取财务指标
    const sources = ['dtshare', 'tushare', 'baostock'];
    
    for (const source of sources) {
      try {
        let data;
        if (source === 'dtshare') {
          data = await this.dataSources[source].getFinancialIndicators(
            code,
            options.year || new Date().getFullYear(),
            options.quarter || 4
          );
        } else if (source === 'tushare' && this.dataSources[source].getFinancialIndicators) {
          data = await this.dataSources[source].getFinancialIndicators(code, options);
        } else if (source === 'baostock' && this.dataSources[source].getFinancialIndicators) {
          data = await this.dataSources[source].getFinancialIndicators(code, options);
        }
        
        if (data && Object.keys(data).length > 0) {
          return data;
        }
      } catch (error) {
        console.error(`${source}获取财务指标失败，尝试其他数据源:`, error.message);
      }
    }
    
    throw new Error('所有数据源获取财务指标失败');
  }

  /**
   * 获取行业估值数据
   * @param {string} industryName - 行业名称
   * @returns {Promise<Object>} 行业估值数据
   */
  async getIndustryValuation(industryName) {
    // 尝试多个数据源获取行业估值
    const sources = ['tushare', 'dtshare', 'eastmoney'];
    
    for (const source of sources) {
      try {
        let data;
        if (source === 'tushare') {
          data = await this.dataSources[source].getIndustryValuation(industryName);
        } else if (source === 'dtshare' && this.dataSources[source].getIndustryValuation) {
          data = await this.dataSources[source].getIndustryValuation(industryName);
        } else if (source === 'eastmoney' && this.dataSources[source].getIndustryValuation) {
          data = await this.dataSources[source].getIndustryValuation(industryName);
        }
        
        if (data) {
          return data;
        }
      } catch (error) {
        console.error(`${source}获取行业估值失败，尝试其他数据源:`, error.message);
      }
    }
    
    throw new Error('所有数据源获取行业估值失败');
  }

  /**
   * 获取行业分类信息
   */
  async getIndustryClassification() {
    return this.fetchWithFallback('getIndustryClassification', []);
  }

  /**
   * 获取指数成分股
   * @param {string} indexType - 指数类型: sz50, hs300, zz500
   */
  async getIndexComponentStocks(indexType) {
    const methodMap = {
      sz50: 'getSZ50Stocks',
      hs300: 'getHS300Stocks',
      zz500: 'getZZ500Stocks'
    };
    
    const method = methodMap[indexType.toLowerCase()];
    if (!method) {
      throw new Error(`不支持的指数类型: ${indexType}`);
    }
    
    return this.callWithFallback(method, []);
  }

  /**
   * 获取财务数据
   * @param {string} code - 股票代码
   * @param {string} year - 年份
   * @param {string} quarter - 季度
   */
  async getFinancialData(code, year, quarter) {
    return this.callWithFallback('getFinancialData', [code, year, quarter]);
  }

  /**
   * 获取股票历史K线数据
   * @param {string} stockCode - 股票代码
   * @param {string} period - 周期
   * @param {number} count - 数据条数
   * @returns {Promise<Array>} K线数据
   */
  async getHistoricalData(stockCode, period = 'day', count = 100) {
    return this.callWithFallback('getHistoricalData', [stockCode, period, count]);
  }

  // 移除重复的getIndustryClassification方法定义

  /**
   * 获取行业股票列表
   * @param {string} industryCode - 行业代码
   * @returns {Promise<Array>} 行业股票列表
   */
  async getIndustryStocks(industryCode) {
    // 优先使用eastmoney的行业股票列表功能
    return this.callWithFallback('getIndustryStocks', [industryCode], ['eastmoney', 'tushare']);
  }

  /**
   * 获取股票列表（基础信息）
   * @param {Object} options - 筛选条件
   * @returns {Promise<Array>} 股票列表
   */
  async getStockList(options = {}) {
    // 优先使用tushare的股票列表功能
    return this.callWithFallback('getStockBasic', [options], ['tushare']);
  }

  /**
   * 测试所有API连接
   */
  async testAllApis() {
    const results = {};
    
    for (const [name, api] of Object.entries(this.dataSources)) {
      try {
        // 根据不同API调用适当的测试方法
        if (name === 'tushare') {
          await api.validateTushareToken();
          results[name] = 'Connected';
        } else if (name === 'dtshare') {
          const testResult = await api.getStockList();
          results[name] = testResult && testResult.length > 0 ? 'Connected' : 'Failed';
        } else if (name === 'eastmoney' || name === 'sinacn') {
          const testResult = await api.getStockQuote('000001');
          results[name] = testResult && testResult.code === '000001' ? 'Connected' : 'Failed';
        } else if (name === 'baostock') {
          await api.login();
          results[name] = 'Connected';
        } else {
          results[name] = 'Test not implemented';
        }
      } catch (error) {
        results[name] = `Failed: ${error.message}`;
      }
    }
    
    return results;
  }

  /**
   * 获取可用数据源列表
   * @returns {Array} 数据源名称列表
   */
  getAvailableApis() {
    return Object.keys(this.dataSources);
  }
}

// 导出统一API实例和各数据源实例
export default new StockApi();
export { tushareApi, eastmoneyApi, sinacnApi, baostockApi, dtshareApi };