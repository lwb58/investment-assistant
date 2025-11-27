import axios from 'axios';
import querystring from 'querystring';

/**
 * 新浪财经API客户端
 * 封装新浪财经的股票数据接口
 */
class SinacnApi {
  constructor() {
    this.baseUrl = 'http://hq.sinajs.cn';
    this.axios = axios.create({
      timeout: 10000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://finance.sina.com.cn/',
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
        console.log(`新浪财经API请求: ${config.method?.toUpperCase()} ${config.url}`);
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
   * 获取股票实时行情数据
   * @param {string} stockCode - 股票代码 (格式: 000001.SZ 或 600000.SH)
   * @returns {Promise<Object>} 股票行情数据
   */
  async getStockQuote(stockCode) {
    try {
      // 新浪财经股票代码转换
      let sinaCode;
      if (stockCode.endsWith('.SZ')) {
        sinaCode = 'sz' + stockCode.replace('.SZ', '');
      } else if (stockCode.endsWith('.SH')) {
        sinaCode = 'sh' + stockCode.replace('.SH', '');
      } else {
        throw new Error('股票代码格式错误，请使用 000001.SZ 或 600000.SH 格式');
      }

      const url = `${this.baseUrl}/list=${sinaCode}`;
      const response = await this.axios.get(url);
      const data = response.data;

      // 解析新浪财经的行情数据
      const match = data.match(/var hq_str_\w+="([^"]+)"/);
      if (!match || !match[1]) {
        throw new Error('获取股票行情失败，未找到数据');
      }

      const hqData = match[1].split(',');
      if (hqData.length < 33) {
        throw new Error('股票行情数据格式错误');
      }

      // 新浪财经行情数据格式说明
      // 0: 股票名称, 1: 今开, 2: 昨收, 3: 现价, 4: 最高价, 5: 最低价
      // 6: 买入价, 7: 卖出价, 8: 成交量, 9: 成交额
      // 10-23: 买一到买五, 24-37: 卖一到卖五
      // 38: 日期, 39: 时间

      // 安全地创建时间戳，添加格式验证
      let timestamp;
      try {
        const dateStr = hqData[38] && hqData[39] ? `${hqData[38]} ${hqData[39]}` : new Date().toISOString();
        const dateObj = new Date(dateStr);
        if (isNaN(dateObj.getTime())) {
          timestamp = new Date().toISOString(); // 使用当前时间作为备选
        } else {
          timestamp = dateObj.toISOString();
        }
      } catch (dateError) {
        timestamp = new Date().toISOString(); // 使用当前时间作为备选
      }

      return {
        symbol: stockCode,
        name: hqData[0],
        open: parseFloat(hqData[1]),
        preClose: parseFloat(hqData[2]),
        price: parseFloat(hqData[3]),
        high: parseFloat(hqData[4]),
        low: parseFloat(hqData[5]),
        change: (parseFloat(hqData[3]) - parseFloat(hqData[2])).toFixed(2),
        changePercent: ((parseFloat(hqData[3]) - parseFloat(hqData[2])) / parseFloat(hqData[2]) * 100).toFixed(2),
        volume: parseInt(hqData[8]),
        amount: parseFloat(hqData[9]),
        buyPrice1: parseFloat(hqData[10]),
        buyVolume1: parseInt(hqData[11]),
        sellPrice1: parseFloat(hqData[24]),
        sellVolume1: parseInt(hqData[25]),
        timestamp: timestamp
      };
    } catch (error) {
      console.error('新浪财经获取股票行情失败:', error.message);
      throw error;
    }
  }

  /**
   * 批量获取股票行情
   * @param {Array<string>} stockCodes - 股票代码数组
   * @returns {Promise<Object>} 股票行情对象，键为股票代码
   */
  async getBatchStockQuotes(stockCodes) {
    try {
      if (!stockCodes || stockCodes.length === 0) {
        return {};
      }

      // 将股票代码转换为新浪格式并拼接
      const sinaCodes = stockCodes.map(code => {
        if (code.endsWith('.SZ')) {
          return 'sz' + code.replace('.SZ', '');
        } else if (code.endsWith('.SH')) {
          return 'sh' + code.replace('.SH', '');
        }
        return null;
      }).filter(Boolean);

      if (sinaCodes.length === 0) {
        return {};
      }

      const url = `${this.baseUrl}/list=${sinaCodes.join(',')}`;
      const response = await this.axios.get(url);
      const data = response.data;

      // 解析批量数据
      const result = {};
      const lines = data.split('\n');
      
      for (const line of lines) {
        if (!line || line.trim() === '') continue;
        
        const codeMatch = line.match(/var hq_str_(\w+)="([^"]*)"/);
        if (codeMatch && codeMatch[1] && codeMatch[2]) {
          const sinaCode = codeMatch[1];
          const hqData = codeMatch[2].split(',');
          
          if (hqData.length >= 33) {
            // 转换回标准代码格式
            let standardCode;
            if (sinaCode.startsWith('sz')) {
              standardCode = sinaCode.substring(2) + '.SZ';
            } else if (sinaCode.startsWith('sh')) {
              standardCode = sinaCode.substring(2) + '.SH';
            } else {
              continue;
            }

            // 安全地创建时间戳
            let timestamp;
            try {
              const dateStr = hqData[38] && hqData[39] ? `${hqData[38]} ${hqData[39]}` : new Date().toISOString();
              const dateObj = new Date(dateStr);
              if (isNaN(dateObj.getTime())) {
                timestamp = new Date().toISOString();
              } else {
                timestamp = dateObj.toISOString();
              }
            } catch (dateError) {
              timestamp = new Date().toISOString();
            }

            result[standardCode] = {
              symbol: standardCode,
              name: hqData[0],
              open: parseFloat(hqData[1]),
              preClose: parseFloat(hqData[2]),
              price: parseFloat(hqData[3]),
              high: parseFloat(hqData[4]),
              low: parseFloat(hqData[5]),
              change: (parseFloat(hqData[3]) - parseFloat(hqData[2])).toFixed(2),
              changePercent: ((parseFloat(hqData[3]) - parseFloat(hqData[2])) / parseFloat(hqData[2]) * 100).toFixed(2),
              volume: parseInt(hqData[8]),
              amount: parseFloat(hqData[9]),
              timestamp: timestamp
            };
          }
        }
      }

      return result;
    } catch (error) {
      console.error('新浪财经批量获取股票行情失败:', error.message);
      throw error;
    }
  }

  /**
   * 获取大盘指数数据
   * @param {string} indexCode - 指数代码 (例如: 000001.SH 上证指数)
   * @returns {Promise<Object>} 指数数据
   */
  async getIndexQuote(indexCode) {
    try {
      return this.getStockQuote(indexCode);
    } catch (error) {
      console.error('新浪财经获取大盘指数失败:', error.message);
      throw error;
    }
  }

  // getHistoricalData 方法已移除，该方法依赖于可能不存在的API端点
  // getStockBasicInfo 方法已移除，该方法依赖于可能不存在的API端点
}

export default new SinacnApi();