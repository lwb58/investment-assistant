import axios from 'axios';

/**
 * 东方财富API客户端
 * 封装东方财富网的股票数据接口
 */
class EastmoneyApi {
  constructor() {
    this.baseUrl = 'https://push2.eastmoney.com';
    this.axios = axios.create({
      timeout: 10000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://quote.eastmoney.com/',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9'
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
        console.log(`东方财富API请求: ${config.method?.toUpperCase()} ${config.url}`);
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
   * 获取股票实时行情
   * @param {string} stockCode - 股票代码
   * @returns {Promise<Object>} 股票行情数据
   */
  async getStockQuote(stockCode) {
    try {
      // 东方财富股票代码格式转换：000001.SZ -> 0000011，600000.SH -> 11600000
      const code = stockCode.endsWith('.SZ') ? 
        '00' + stockCode.replace('.SZ', '') + '1' : 
        '11' + stockCode.replace('.SH', '');
      
      // 使用更简洁的API调用，只获取必要的字段
      const url = `https://push2.eastmoney.com/api/qt/stock/get?fields=f2,f3,f4,f5,f6,f7,f8,f9,f10,f14,f17,f18,f43,f44,f39,f40,f205&fltt=2&invt=2&secid=${code}&ut=f8f9f95e`;
      
      // 设置合理的超时时间
      const response = await this.axios.get(url, { timeout: 15000 });
      
      // 解析JSONP响应
      const dataStr = response.data.match(/\((.*)\)/)?.[1];
      if (!dataStr) {
        throw new Error('东方财富API响应格式错误');
      }
      
      const data = JSON.parse(dataStr);
      
      if (data.data?.f14 && data.data?.f2) {
        return {
          name: data.data.f14,
          price: data.data.f2,
          open: data.data.f18,
          high: data.data.f39,
          low: data.data.f40,
          preClose: data.data.f17,
          change: data.data.f43,
          changePercent: data.data.f44,
          volume: data.data.f5,
          amount: data.data.f6,
          pe: data.data.f9,
          pb: data.data.f10,
          marketCap: data.data.f205,
          time: new Date().toISOString()
        };
      }
      
      return null;
    } catch (error) {
      console.error('东方财富获取股票行情失败:', error.message);
      throw error;
    }
  }

  /**
   * 获取行业分类数据
   * @returns {Promise<Array>} 行业分类列表
   */
  async getIndustryClassification() {
    try {
      // 简化fields参数，只保留必要的字段
      const url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f184&fs=m:90+t:2+f:!50&fields=f2,f9,f10,f12,f14,f107,f205,f44';
      
      const response = await this.axios.get(url);
      
      // 解析JSONP响应
      const dataStr = response.data.match(/\((.*)\)/)?.[1];
      if (!dataStr) {
        throw new Error('东方财富API响应格式错误');
      }
      
      const data = JSON.parse(dataStr);
      
      if (!data.data?.diff) {
        return [];
      }
      
      return data.data.diff.map(item => ({
        code: item.f12,
        name: item.f14,
        industry: item.f107,
        marketCap: item.f205,
        pe: item.f9,
        pb: item.f10,
        price: item.f2,
        changePercent: item.f44
      }));
    } catch (error) {
      console.error('东方财富获取行业分类失败:', error.message);
      throw error;
    }
  }

  /**
   * 获取行业股票列表
   * @param {string} industryCode - 行业代码
   * @returns {Promise<Array>} 行业股票列表
   */
  async getIndustryStocks(industryCode) {
    try {
      // 简化fields参数，只保留必要的字段
      const url = `https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f184&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f2,f5,f12,f13,f14,f107,f205,f44`;
      
      const response = await this.axios.get(url);
      
      // 解析JSONP响应
      const dataStr = response.data.match(/\((.*)\)/)?.[1];
      if (!dataStr) {
        throw new Error('东方财富API响应格式错误');
      }
      
      const data = JSON.parse(dataStr);
      
      if (!data.data?.diff) {
        return [];
      }
      
      return data.data.diff
        .filter(item => item.f107 === industryCode) // 过滤指定行业
        .map(item => ({
          symbol: item.f12 + (item.f13 === 1 ? '.SH' : '.SZ'),
          code: item.f12,
          name: item.f14,
          price: item.f2,
          changePercent: item.f44,
          volume: item.f5,
          marketCap: item.f205
        }));
    } catch (error) {
      console.error('东方财富获取行业股票列表失败:', error.message);
      throw error;
    }
  }
}

export default new EastmoneyApi();