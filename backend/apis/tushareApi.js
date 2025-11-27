import axios from 'axios';
import dotenv from 'dotenv';

// 加载环境变量
dotenv.config();

/**
 * Tushare API 客户端
 * 封装Tushare Pro的所有数据接口
 */
class TushareApi {
  constructor() {
    this.baseUrl = process.env.TUSHARE_BASE_URL || 'http://api.tushare.pro';
    this.token = process.env.TUSHARE_TOKEN || '';
    this.axios = axios.create({
      timeout: 15000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });
    this.setupInterceptors();
  }

  /**
   * 设置请求和响应拦截器
   */
  setupInterceptors() {
    // 请求拦截器
    this.axios.interceptors.request.use(
      config => {
        console.log(`Tushare API请求: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      error => Promise.reject(error)
    );

    // 响应拦截器
    this.axios.interceptors.response.use(
      response => response,
      async error => {
        const config = error.config || {};
        config.retry = config.retry || 2;
        config.retryCount = config.retryCount || 0;

        if (config.retryCount < config.retry) {
          config.retryCount++;
          const delay = Math.pow(2, config.retryCount) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
          return this.axios(config);
        }
        
        return Promise.reject(error);
      }
    );
  }

  /**
   * 通用API调用方法
   * @param {string} apiName - API名称
   * @param {Object} params - 请求参数
   * @param {string} fields - 返回字段
   * @returns {Promise<Object>} API响应数据
   */
  async callApi(apiName, params = {}, fields = '') {
    try {
      if (!this.token) {
        throw new Error('Tushare API token 未配置');
      }

      const response = await this.axios.post(this.baseUrl, {
        api_name: apiName,
        token: this.token,
        params: params,
        fields: fields
      });

      if (response.data.code !== 0) {
        throw new Error(`Tushare API错误: ${response.data.msg || '未知错误'}`);
      }

      return response.data;
    } catch (error) {
      console.error(`Tushare API ${apiName}调用失败:`, error.message);
      throw error;
    }
  }

  /**
   * 获取股票基本信息
   * @param {Object} options - 查询选项
   * @returns {Promise<Array>} 股票基本信息列表
   */
  async getStockBasic(options = {}) {
    const params = {
      exchange: options.exchange || '',
      list_status: options.list_status || 'L',
      limit: options.limit || 1000,
      offset: options.offset || 0
    };

    const fields = options.fields || 'ts_code,symbol,name,industry,area,market,exchange,list_date';
    const result = await this.callApi('stock_basic', params, fields);
    
    if (!result.data || !result.data.items) return [];
    
    return result.data.items.map((item, index) => {
      const fieldArray = result.data.fields;
      const stock = {};
      fieldArray.forEach((field, i) => {
        stock[field] = item[i];
      });
      return stock;
    });
  }

  /**
   * 获取股票实时行情
   * @param {string} tsCode - 股票代码（如：000001.SZ）
   * @returns {Promise<Object>} 股票行情数据
   */
  async getStockQuote(tsCode) {
    const params = { ts_code: tsCode };
    const fields = 'ts_code,name,open,high,low,close,pre_close,change,pct_chg,volume,amount,pe,pe_ttm,pb,total_mv';
    
    const result = await this.callApi('stock_quotation', params, fields);
    
    if (!result.data || !result.data.items || result.data.items.length === 0) {
      return null;
    }
    
    const fieldArray = result.data.fields;
    const quote = {};
    fieldArray.forEach((field, index) => {
      quote[field] = result.data.items[0][index];
    });
    
    return quote;
  }

  /**
   * 获取行业分类数据
   * @returns {Promise<Array>} 行业分类数据
   */
  async getIndustryClassification() {
    const params = { src: 'sw' }; // 默认使用申万行业分类
    const fields = 'code,name,industry';
    
    const result = await this.callApi('industry_classified', params, fields);
    
    if (!result.data || !result.data.items) return [];
    
    return result.data.items.map((item, index) => {
      const fieldArray = result.data.fields;
      const industry = {};
      fieldArray.forEach((field, i) => {
        industry[field] = item[i];
      });
      return industry;
    });
  }

  /**
   * 获取行业股票列表
   * @param {string} industry - 行业名称
   * @returns {Promise<Array>} 行业股票列表
   */
  async getIndustryStocks(industry) {
    const params = {
      src: 'sw',
      industry: industry
    };
    
    const fields = 'ts_code,symbol,name,industry,area,market';
    const result = await this.callApi('stock_basic', params, fields);
    
    if (!result.data || !result.data.items) return [];
    
    return result.data.items.map((item, index) => {
      const fieldArray = result.data.fields;
      const stock = {};
      fieldArray.forEach((field, i) => {
        stock[field] = item[i];
      });
      return stock;
    });
  }

  /**
   * 获取行业估值数据
   * @param {string} industry - 行业名称
   * @returns {Promise<Object>} 行业估值数据
   */
  async getIndustryValuation(industry) {
    const params = { industry: industry };
    const fields = 'industry,pe,pb,total_mv,total_share,float_mv,float_share,pe_ttm';
    
    const result = await this.callApi('industry_valuation', params, fields);
    
    if (!result.data || !result.data.items || result.data.items.length === 0) {
      return null;
    }
    
    const fieldArray = result.data.fields;
    const valuation = {};
    fieldArray.forEach((field, index) => {
      valuation[field] = result.data.items[0][index];
    });
    
    return valuation;
  }

  /**
   * 获取K线数据
   * @param {string} tsCode - 股票代码
   * @param {string} freq - 频率：D日线，W周线，M月线，5分钟线等
   * @param {string} startDate - 开始日期
   * @param {string} endDate - 结束日期
   * @returns {Promise<Array>} K线数据列表
   */
  async getKLineData(tsCode, freq = 'D', startDate, endDate) {
    const params = {
      ts_code: tsCode,
      freq: freq,
      start_date: startDate,
      end_date: endDate
    };
    
    const fields = 'ts_code,trade_date,open,high,low,close,volume,amount,pre_close,change,pct_chg';
    const result = await this.callApi('daily', params, fields);
    
    if (!result.data || !result.data.items) return [];
    
    return result.data.items.map((item, index) => {
      const fieldArray = result.data.fields;
      const kline = {};
      fieldArray.forEach((field, i) => {
        kline[field] = item[i];
      });
      return kline;
    });
  }

  /**
   * 验证Tushare Token
   * @returns {Promise<Object>} Token验证结果
   */
  async validateTushareToken() {
    try {
      // 使用callApi方法来验证token
      const response = await this.callApi('stock_basic', 
        { limit: 1 },
        'ts_code,name,market'
      );
      console.log('Tushare Token验证结果:', response);
      return response;
    } catch (error) {
      console.error('Tushare Token验证失败:', error.message);
      throw new Error(`Tushare Token验证失败: ${error.message}`);
    }
  }

  // validateToken方法已被validateTushareToken替代
}

export default new TushareApi();