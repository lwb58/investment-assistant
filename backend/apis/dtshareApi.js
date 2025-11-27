import axios from 'axios';
import dotenv from 'dotenv';

// 加载环境变量
dotenv.config();

/**
 * Dtshare API 客户端
 * 封装dtshare的所有数据接口
 */
class DtshareApi {
  constructor() {
    this.baseUrl = process.env.DTSHARE_BASE_URL || 'http://api.dt-share.com';
    this.apiKey = process.env.DTSHARE_API_KEY || 'default_test_key'; // 添加默认测试密钥
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
   * 配置API密钥
   * @param {string} apiKey - Dtshare API密钥
   */
  configure(apiKey) {
    if (apiKey) {
      this.apiKey = apiKey;
      console.log('Dtshare API密钥已配置');
    }
  }

  /**
   * 设置请求和响应拦截器
   */
  setupInterceptors() {
    // 请求拦截器
    this.axios.interceptors.request.use(
      config => {
        console.log(`Dtshare API请求: ${config.method?.toUpperCase()} ${config.url}`);
        // 添加API密钥到请求头
        if (this.apiKey) {
          config.headers['Authorization'] = `Bearer ${this.apiKey}`;
        }
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
   * @param {string} endpoint - API端点路径
   * @param {Object} params - 请求参数
   * @returns {Promise<Object>} API响应数据
   */
  async callApi(endpoint, params = {}) {
    try {
      if (!this.apiKey) {
        throw new Error('Dtshare API密钥未配置');
      }

      const response = await this.axios.get(`${this.baseUrl}/${endpoint}`, {
        params: params
      });

      if (response.data.code !== 200) {
        throw new Error(`Dtshare API错误: ${response.data.msg || '未知错误'}`);
      }

      return response.data;
    } catch (error) {
      console.error(`Dtshare API ${endpoint}调用失败:`, error.message);
      throw error;
    }
  }

  /**
   * 获取A股股票列表
   * @returns {Promise<Array>} 股票列表
   */
  async getStockList() {
    return this.callApi('stock/a股列表', {});
  }

  /**
   * 获取股票实时行情
   * @param {string} code - 股票代码
   * @returns {Promise<Object>} 行情数据
   */
  async getStockQuote(code) {
    return this.callApi('stock/实时行情', { code });
  }

  /**
   * 获取股票历史K线数据
   * @param {string} code - 股票代码
   * @param {string} startDate - 开始日期 (YYYY-MM-DD)
   * @param {string} endDate - 结束日期 (YYYY-MM-DD)
   * @param {string} freq - 频率 (D-日K, W-周K, M-月K)
   * @returns {Promise<Array>} K线数据
   */
  async getHistoricalData(code, startDate, endDate, freq = 'D') {
    return this.callApi('stock/历史K线', {
      code,
      start_date: startDate,
      end_date: endDate,
      freq
    });
  }

  /**
   * 获取行业分类数据
   * @returns {Promise<Array>} 行业分类列表
   */
  async getIndustryClassification() {
    return this.callApi('industry/行业分类', {});
  }

  /**
   * 获取行业成分股
   * @param {string} industryCode - 行业代码
   * @returns {Promise<Array>} 成分股列表
   */
  async getIndustryStocks(industryCode) {
    return this.callApi('industry/成分股', { code: industryCode });
  }

  /**
   * 获取财务指标数据
   * @param {string} code - 股票代码
   * @param {string} year - 年份
   * @param {string} quarter - 季度
   * @returns {Promise<Object>} 财务指标
   */
  async getFinancialIndicators(code, year, quarter) {
    return this.callApi('finance/财务指标', {
      code,
      year,
      quarter
    });
  }
}

export default new DtshareApi();