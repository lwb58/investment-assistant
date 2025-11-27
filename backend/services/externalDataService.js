import axios from 'axios';
import dotenv from 'dotenv';

// 导入修复后的API模块
import sinacnApi from '../apis/sinacnApi.js';
import eastmoneyApi from '../apis/eastmoneyApi.js';
import tushareApi from '../apis/tushareApi.js';
import baostockApi from '../apis/baostockApi.js';
import dtshareApi from '../apis/dtshareApi.js';

// 加载环境变量
dotenv.config();

/**
 * 外部数据源服务
 * 集成东方财富、新浪财经和集思录的API接口
 */
class ExternalDataService {
  constructor() {
    this.db = null;
    this.axios = axios.create({
      timeout: 10000, // 设置超时时间
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    this.cache = new Map();
    this.cacheTTL = 5 * 60 * 1000; // 5分钟缓存
    
    // 配置多个数据源，使用环境变量或默认值
    this.config = {
      tushare: {
        baseUrl: 'http://api.tushare.pro',
        token: process.env.TUSHARE_TOKEN || '' // 不再硬编码token
      },
      publicAPIs: {
        baseUrl: 'https://api.example.com/v1' // 示例公共API
      }
    };
    
    this.setupInterceptors();
  }
  
  // 设置拦截器
  setupInterceptors() {
    // 请求拦截器
    this.axios.interceptors.request.use(
      config => {
        console.log(`请求API: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      error => Promise.reject(error)
    );
    
    // 响应拦截器
    this.axios.interceptors.response.use(
      response => response,
      async error => {
        const config = error.config || {};
        
        // 初始化重试配置
        config.retry = config.retry || 2;
        config.retryCount = config.retryCount || 0;
        
        // 如果重试次数未达到上限
        if (config.retryCount < config.retry) {
          config.retryCount++;
          
          // 指数退避策略
          const delay = Math.pow(2, config.retryCount) * 1000;
          console.log(`请求失败，${delay}ms后重试 (${config.retryCount}/${config.retry})`);
          
          await new Promise(resolve => setTimeout(resolve, delay));
          return this.axios(config);
        }
        
        return Promise.reject(error);
      }
    );
    this.initialize();
  }

  async initialize() {
    try {
      this.db = await getDB();
      // 验证Tushare token是否有效
      const validateResult = await this.validateTushareToken();
      if (validateResult) {
        console.log('Tushare API连接成功');
      } else {
        console.warn('Tushare API连接失败，请检查token是否有效');
      }
      console.log('外部数据源服务初始化成功');
    } catch (error) {
      console.error('外部数据源服务初始化失败:', error);
    }
  }
  
  /**
   * 验证Tushare token是否有效
   */
  async validateTushareToken() {
    try {
      const response = await this.callTushareAPI('stock_basic', {
        exchange: '',
        list_status: 'L',
        fields: 'ts_code,symbol,name,industry',
        limit: 1
      });
      return response && response.data && response.data.items && response.data.items.length > 0;
    } catch (error) {
      console.error('验证Tushare Token失败:', error);
      return false;
    }
  }
  
  /**
   * 调用Tushare API
   * @param {string} apiName API名称
   * @param {Object} params 请求参数
   */
  async callTushareAPI(apiName, params = {}) {
    try {
      console.log(`调用Tushare API: ${apiName}`);
      const response = await this.axios.post(this.tushare.baseUrl, {
        api_name: apiName,
        token: this.tushare.token,
        params: params,
        fields: params.fields || ''
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 15000
      });
      
      if (response.data && response.data.code === 0) {
        return response.data;
      } else {
        console.error(`Tushare API ${apiName} 调用失败: ${response.data?.msg || '未知错误'}`);
        return null;
      }
    } catch (error) {
      console.error(`Tushare API ${apiName} 请求异常:`, error.message);
      // 网络错误时返回null，允许调用方继续尝试其他数据源
      return null;
    }
  }
  
  /**
   * Tushare API - 获取股票基本信息
   * @param {Object} options 查询选项
   */
  async getTushareStockBasic(options = {}) {
    const cacheKey = `tushare_stock_basic_${JSON.stringify(options)}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      console.log(`使用修复的Tushare API模块获取股票基本信息`);
      const stocks = await tushareApi.getStockBasic(options);
      
      if (stocks && Array.isArray(stocks)) {
        // 确保返回的数据格式符合服务层期望
        const formattedStocks = stocks.map(stock => ({
          symbol: stock.ts_code,
          code: stock.symbol,
          name: stock.name,
          industry: stock.industry,
          area: stock.area,
          market: stock.market,
          exchange: stock.exchange
        }));
        
        this.setCachedData(cacheKey, formattedStocks);
        return formattedStocks;
      }
    } catch (error) {
      console.error('获取Tushare股票基本信息失败:', error);
    }
    return [];
  }
  
  /**
   * Tushare API - 获取股票实时行情
   * @param {string} symbol 股票代码 (如: 000001.SZ, 600000.SH)
   */
  async getTushareStockQuote(symbol) {
    const cacheKey = `tushare_quote_${symbol}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      // Tushare的行情API需要使用ts_code格式
      const params = {
        ts_code: symbol,
        fields: 'ts_code,name,open,high,low,close,pre_close,change,pct_chg,volume,amount,pe,pe_ttm,pb,total_mv'
      };
      
      // 使用stock_quotation API获取实时行情
      const result = await this.callTushareAPI('stock_quotation', params);
      
      if (result && result.data && result.data.items && result.data.items.length > 0) {
        const quote = result.data.items[0];
        
        const formattedData = {
          symbol: quote.ts_code,
          name: quote.name,
          price: quote.close,
          open: quote.open,
          high: quote.high,
          low: quote.low,
          pre_close: quote.pre_close,
          change: quote.change,
          pct_change: quote.pct_chg,
          volume: quote.volume,
          amount: quote.amount,
          pe: quote.pe || quote.pe_ttm || 0,
          pb: quote.pb || 0,
          market_cap: quote.total_mv || 0,
          timestamp: new Date()
        };
        
        this.setCachedData(cacheKey, formattedData);
        return formattedData;
      }
    } catch (error) {
      console.error(`获取Tushare股票${symbol}行情失败:`, error);
    }
    return null;
  }
  
  /**
   * Tushare API - 获取行业分类数据
   */
  async getTushareIndustries() {
    const cacheKey = 'tushare_industries';
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      // 使用stock_basic API获取所有股票，然后按行业分组
      const stocks = await this.getTushareStockBasic({
        fields: 'ts_code,name,industry',
        limit: 10000
      });
      
      // 按行业分组并统计
      const industryMap = {};
      stocks.forEach(stock => {
        if (stock.industry && stock.industry.trim()) {
          if (!industryMap[stock.industry]) {
            industryMap[stock.industry] = {
              name: stock.industry,
              count: 0,
              stocks: []
            };
          }
          industryMap[stock.industry].count++;
          industryMap[stock.industry].stocks.push({
            symbol: stock.symbol,
            name: stock.name
          });
        }
      });
      
      // 转换为数组格式
      const industries = Object.values(industryMap);
      
      this.setCachedData(cacheKey, industries);
      return industries;
    } catch (error) {
      console.error('获取Tushare行业数据失败:', error);
    }
    return [];
  }
  
  /**
   * Tushare API - 获取行业股票列表
   * @param {string} industry 行业名称
   */
  async getTushareIndustryStocks(industry) {
    const cacheKey = `tushare_industry_stocks_${industry}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      const stocks = await this.getTushareStockBasic({
        fields: 'ts_code,symbol,name,industry,area,market',
        limit: 10000
      });
      
      // 筛选指定行业的股票
      const industryStocks = stocks.filter(stock => 
        stock.industry && stock.industry.trim() === industry
      );
      
      // 获取每只股票的行情数据
      const detailedStocks = await Promise.all(
        industryStocks.map(async stock => {
          const quote = await this.getTushareStockQuote(stock.symbol);
          return {
            ...stock,
            price: quote?.price || 0,
            change: quote?.change || 0,
            pct_change: quote?.pct_change || 0,
            pe: quote?.pe || 0,
            pb: quote?.pb || 0,
            market_cap: quote?.market_cap || 0
          };
        })
      );
      
      this.setCachedData(cacheKey, detailedStocks);
      return detailedStocks;
    } catch (error) {
      console.error(`获取Tushare行业${industry}股票列表失败:`, error);
    }
    return [];
  }
  
  /**
   * Tushare API - 获取行业估值数据
   */
  async getTushareIndustryValuations() {
    const cacheKey = 'tushare_industry_valuations';
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      // 1. 获取所有股票的基本信息和行业分类
      const stocks = await this.getTushareStockBasic({
        fields: 'ts_code,symbol,name,industry',
        limit: 10000
      });
      
      // 2. 获取所有股票的估值数据
      const tsCodes = stocks.map(stock => stock.ts_code).join(',');
      const valuationResult = await this.callTushareAPI('stock_valuation', {
        ts_code: tsCodes,
        fields: 'ts_code,pe,pe_ttm,pb,total_mv',
        limit: 10000
      });
      
      if (!valuationResult || !valuationResult.data || !valuationResult.data.items) {
        return [];
      }
      
      // 3. 创建股票代码到估值数据的映射
      const valuationMap = {};
      valuationResult.data.items.forEach(item => {
        valuationMap[item.ts_code] = {
          pe: item.pe || item.pe_ttm || 0,
          pb: item.pb || 0,
          market_cap: item.total_mv || 0
        };
      });
      
      // 4. 按行业分组计算平均估值
      const industryValuations = {};
      
      stocks.forEach(stock => {
        if (stock.industry && stock.industry.trim() && valuationMap[stock.symbol]) {
          const industry = stock.industry;
          const valuation = valuationMap[stock.symbol];
          
          if (!industryValuations[industry]) {
            industryValuations[industry] = {
              name: industry,
              stockCount: 0,
              totalPE: 0,
              totalPB: 0,
              totalMarketCap: 0,
              avgPE: 0,
              avgPB: 0,
              totalMarketCap: 0
            };
          }
          
          industryValuations[industry].stockCount++;
          industryValuations[industry].totalPE += valuation.pe;
          industryValuations[industry].totalPB += valuation.pb;
          industryValuations[industry].totalMarketCap += valuation.market_cap;
        }
      });
      
      // 5. 计算行业平均估值
      const result = Object.values(industryValuations).map(ind => ({
        name: ind.name,
        stockCount: ind.stockCount,
        avgPE: ind.stockCount > 0 ? ind.totalPE / ind.stockCount : 0,
        avgPB: ind.stockCount > 0 ? ind.totalPB / ind.stockCount : 0,
        totalMarketCap: ind.totalMarketCap
      }));
      
      this.setCachedData(cacheKey, result);
      return result;
    } catch (error) {
      console.error('获取Tushare行业估值数据失败:', error);
    }
    return [];
  }

  /**
   * 缓存管理
   */
  getCachedData(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
      return cached.data;
    }
    this.cache.delete(key);
    return null;
  }

  setCachedData(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  /**
   * 东方财富API - 获取股票实时行情
   * @param {string} symbol 股票代码 (如: 000001.SZ, 600000.SH)
   */
  async getEastMoneyStockQuote(symbol) {
    const cacheKey = `eastmoney_quote_${symbol}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      console.log(`使用eastmoneyApi获取股票${symbol}行情`);
      const result = await eastmoneyApi.getStockQuote(symbol);
      
      if (result) {
        // 确保返回的数据格式符合要求
        const formattedResult = {
          symbol: result.symbol || symbol,
          name: result.name,
          price: result.price,
          open: result.open,
          high: result.high,
          low: result.low,
          pre_close: result.pre_close,
          change: result.change,
          pct_change: result.pct_change,
          volume: result.volume,
          amount: result.amount,
          pe: result.pe,
          pb: result.pb,
          market_cap: result.market_cap,
          timestamp: result.timestamp || new Date()
        };
        
        this.setCachedData(cacheKey, formattedResult);
        return formattedResult;
      }
    } catch (error) {
      console.error(`获取东方财富股票${symbol}行情失败:`, error);
    }
    return null;
  }

  /**
   * 东方财富API - 获取行业数据
   */
  async getEastMoneyIndustries() {
    const cacheKey = 'eastmoney_industries';
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      // 东方财富行业分类接口
      const url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f3&fs=m:90+t:2&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f148,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61';
      
      const response = await this.axios.get(url);
      const data = response.data;
      
      if (data.data && data.data.diff) {
        const industries = data.data.diff.map(item => ({
          code: item.f12,
          name: item.f14,
          price: item.f2,
          change: item.f3,
          pct_change: item.f4,
          volume: item.f5,
          amount: item.f6,
          pe: item.f8,
          pb: item.f9
        }));
        
        this.setCachedData(cacheKey, industries);
        return industries;
      }
    } catch (error) {
      console.error('获取东方财富行业数据失败:', error);
    }
    return [];
  }

  /**
   * 新浪财经API - 获取股票实时行情
   * @param {string} symbol 股票代码 (如: 000001.SZ, 600000.SH)
   */
  async getSinaStockQuote(symbol) {
    const cacheKey = `sina_quote_${symbol}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      console.log(`使用修复的新浪财经API模块获取${symbol}行情`);
      const result = await sinacnApi.getStockQuote(symbol);
      
      if (result) {
        // 转换为服务层期望的格式
        const formattedResult = {
          symbol: result.symbol,
          name: result.name,
          open: result.open,
          pre_close: result.preClose,
          price: result.price,
          high: result.high,
          low: result.low,
          volume: result.volume,
          amount: result.amount,
          change: parseFloat(result.change),
          pct_change: parseFloat(result.changePercent),
          timestamp: new Date(result.timestamp)
        };
        
        this.setCachedData(cacheKey, formattedResult);
        return formattedResult;
      }
    } catch (error) {
      console.error(`获取新浪财经股票${symbol}行情失败:`, error);
    }
    return null;
  }

  /**
   * 新浪财经API - 获取大盘指数
   */
  async getSinaMarketIndex() {
    // 强制不使用缓存，确保每次都验证API可用性
    const cacheKey = 'sina_market_index';
    
    // 清除任何可能存在的缓存数据
    this.cache.delete(cacheKey);
    
    try {
      // 新浪财经大盘指数URL
      const url = 'https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006';
      
      console.log(`[${new Date().toISOString()}] 正在调用新浪财经API获取大盘指数数据`);
      
      // 添加请求头以模拟浏览器请求
      const response = await this.axios.get(url, {
        headers: {
          'Referer': 'https://finance.sina.com.cn/',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'zh-CN,zh;q=0.9',
          'Connection': 'keep-alive'
        },
        timeout: 8000 // 设置较短的超时时间
      });

      // 验证响应状态
      if (response.status !== 200) {
        const errorMsg = `获取新浪财经大盘指数失败: HTTP状态码 ${response.status}`;
        console.error(`[${new Date().toISOString()}] ${errorMsg}`);
        throw new Error(errorMsg);
      }

      // 验证响应内容
      if (!response.data || typeof response.data !== 'string') {
        const errorMsg = '获取新浪财经大盘指数失败: 响应数据为空或格式错误';
        console.error(`[${new Date().toISOString()}] ${errorMsg}`);
        throw new Error(errorMsg);
      }

      const dataStr = response.data;
      
      // 提取各个指数数据
      const shMatch = dataStr.match(/var hq_str_s_sh000001="([^"]+)"/);
      const szMatch = dataStr.match(/var hq_str_s_sz399001="([^"]+)"/);
      const cyMatch = dataStr.match(/var hq_str_s_sz399006="([^"]+)"/);
      
      // 验证数据是否成功解析
      if (!shMatch || !shMatch[1] || !szMatch || !szMatch[1] || !cyMatch || !cyMatch[1]) {
        const errorMsg = '获取新浪财经大盘指数失败: 返回数据格式不正确，无法提取指数数据';
        console.error(`[${new Date().toISOString()}] ${errorMsg}`);
        console.error('响应数据示例:', dataStr.substring(0, 100) + '...');
        throw new Error(errorMsg);
      }

      // 解析指数数据
      const parseIndex = (match, name) => {
        const values = match[1].split(',');
        if (values.length < 10) {
          throw new Error(`解析${name}失败: 数据字段不完整`);
        }
        
        const open = parseFloat(values[1]);
        const pre_close = parseFloat(values[2]);
        const price = parseFloat(values[3]);
        const high = parseFloat(values[4]);
        const low = parseFloat(values[5]);
        const volume = parseInt(values[8]);
        const amount = parseFloat(values[9]);
        
        // 验证数值有效性
        if (isNaN(open) || isNaN(price) || isNaN(pre_close)) {
          throw new Error(`解析${name}失败: 关键数值字段无效`);
        }
        
        return {
          name,
          open,
          pre_close,
          price,
          high,
          low,
          volume,
          amount,
          change: price - pre_close,
          pct_change: ((price - pre_close) / pre_close * 100).toFixed(2)
        };
      };

      try {
        // 解析各个指数数据
        const shData = parseIndex(shMatch, '上证指数');
        const szData = parseIndex(szMatch, '深证成指');
        const cyData = parseIndex(cyMatch, '创业板指');
        
        const result = {
          sh: shData,
          sz: szData,
          cy: cyData,
          timestamp: new Date()
        };
        
        // 设置缓存
        this.setCachedData(cacheKey, result);
        return result;
      } catch (parseError) {
        const errorMsg = `获取新浪财经大盘指数失败: ${parseError.message}`;
        console.error(`[${new Date().toISOString()}] ${errorMsg}`);
        throw new Error(errorMsg);
      }
    } catch (error) {
      // 确保所有错误都被正确抛出
      const errorMsg = `获取新浪财经大盘指数失败: ${error.message}`;
      console.error(`[${new Date().toISOString()}] ${errorMsg}`, error.stack || '');
      throw new Error(errorMsg);
    }
  }
  


  /**
   * 集思录API - 获取可转债数据
   */
  async getJisiluCBData(page = 1, pageSize = 20) {
    const cacheKey = `jisilu_cb_${page}_${pageSize}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      const url = 'https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t=1688444444444';
      const data = {
        fprice: '',
        tprice: '',
        qprice: '',
       scode: '',
        sname: '',
        btype: 'C',
        market: '',
        minbond_id: '',
        maxbond_id: '',
        minprice: '',
        maxprice: '',
        min_today_incr: '',
        max_today_incr: '',
        minvolume: '',
        maxvolume: '',
        min_mv: '',
        max_mv: '',
        min_issuer_mv: '',
        max_issuer_mv: '',
        min_amount: '',
        max_amount: '',
        min_ratio: '',
        max_ratio: '',
        min_ytm: '',
        max_ytm: '',
        min_ytm_aft_tax: '',
        max_ytm_aft_tax: '',
        min_ytm_call: '',
        max_ytm_call: '',
        min_stock_price: '',
        max_stock_price: '',
        min_stock_pct: '',
        max_stock_pct: '',
        min_pb: '',
        max_pb: '',
        min_pe: '',
        max_pe: '',
        min_diluted_pe: '',
        max_diluted_pe: '',
        min_turnover_rt: '',
        max_turnover_rt: '',
        min_score: '',
        max_score: '',
        min_price_aft_tax: '',
        max_price_aft_tax: '',
        min_holder_num: '',
        max_holder_num: '',
        min_stock_incr_rt: '',
        max_stock_incr_rt: '',
        min_stock_daily_incr_rt: '',
        max_stock_daily_incr_rt: '',
        min_put_back_price: '',
        max_put_back_price: '',
        put_back_year: '',
        min_future_price: '',
        max_future_price: '',
        min_future_pct: '',
        max_future_pct: '',
        min_volatility: '',
        max_volatility: '',
        min_delta: '',
        max_delta: '',
        min_vega: '',
        max_vega: '',
        min_theta: '',
        max_theta: '',
        min_gamma: '',
        max_gamma: '',
        min_implied_volatility: '',
        max_implied_volatility: '',
        min_stock_pe_ttm: '',
        max_stock_pe_ttm: '',
        min_stock_pb_lf: '',
        max_stock_pb_lf: '',
        min_stock_industry_pe: '',
        max_stock_industry_pe: '',
        min_stock_industry_pb: '',
        max_stock_industry_pb: '',
        order: 'price',
        order_type: 'desc',
        page: page,
        rp: pageSize
      };
      
      const response = await this.axios.post(url, data, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
      });
      
      const result = response.data;
      if (result.rows) {
        const cbData = result.rows.map(row => ({
          code: row.cell.bond_id,
          name: row.cell.bond_nm,
          price: parseFloat(row.cell.price),
          change: parseFloat(row.cell.today_incr),
          pct_change: parseFloat(row.cell.today_volume),
          stock_code: row.cell.stock_code,
          stock_name: row.cell.stock_nm,
          stock_price: parseFloat(row.cell.stock_price),
          stock_pct: parseFloat(row.cell.stock_pct),
          pb: parseFloat(row.cell.pb),
          pe: parseFloat(row.cell.pe),
          ytm: parseFloat(row.cell.ytm),
          volume: parseFloat(row.cell.volume),
          market_cap: parseFloat(row.cell.mv),
          conversion_price: parseFloat(row.cell.conv_price),
          conversion_value: parseFloat(row.cell.conv_value),
          premium_rate: parseFloat(row.cell.premium_rt),
          delta: parseFloat(row.cell.delta)
        }));
        
        this.setCachedData(cacheKey, {
          list: cbData,
          total: result.total
        });
        
        return {
          list: cbData,
          total: result.total
        };
      }
    } catch (error) {
      console.error('获取集思录可转债数据失败:', error);
    }
    return { list: [], total: 0 };
  }

  /**
   * 批量获取股票数据 - 优化请求策略
   * @param {Array<string>} symbols 股票代码数组
   */
  async batchGetStockData(symbols) {
    const results = {};
    const promises = [];
    
    // 分批处理，避免一次性请求过多
    const batchSize = 10;
    for (let i = 0; i < symbols.length; i += batchSize) {
      const batch = symbols.slice(i, i + batchSize);
      const batchPromises = batch.map(symbol => 
        this.getEastMoneyStockQuote(symbol).then(data => {
          if (data) {
            results[symbol] = data;
          }
        })
      );
      
      // 等待当前批次完成后再进行下一批次
      await Promise.all(batchPromises);
    }
    
    return results;
  }

  /**
   * 获取综合数据 - 从多个数据源整合信息
   * @param {string} symbol 股票代码
   */
  async getIntegratedStockData(symbol) {
    try {
      // 并行获取多个数据源的数据，但添加错误处理以确保一个失败不影响其他
      let eastMoneyData = null;
      let sinaData = null;
      let eastMoneyError = null;
      let sinaError = null;
      const timestamp = new Date().toISOString();
      
      try {
        eastMoneyData = await this.getEastMoneyStockQuote(symbol);
      } catch (error) {
        eastMoneyError = error;
        console.error(`[${timestamp}] 获取东方财富数据失败 (${symbol}):`, error.stack || error.message);
      }
      
      try {
        sinaData = await this.getSinaStockQuote(symbol);
      } catch (error) {
        sinaError = error;
        console.error(`[${timestamp}] 获取新浪数据失败 (${symbol}):`, error.stack || error.message);
      }
      
      // 如果所有数据源都失败，抛出错误
      if (!eastMoneyData && !sinaData) {
        const errorMsg = `所有股票数据源获取失败 (${symbol}) - 东方财富错误: ${eastMoneyError?.message || '无'}, 新浪错误: ${sinaError?.message || '无'}`;
        console.error(`[${timestamp}] ${errorMsg}`);
        throw new Error(`[${timestamp}] ${errorMsg}`);
      }
      
      // 整合数据，优先使用非空的数据
      const integratedData = {
        symbol: symbol,
        name: eastMoneyData?.name || sinaData?.name || '未知',
        price: eastMoneyData?.price || sinaData?.price || 0,
        open: eastMoneyData?.open || sinaData?.open || 0,
        high: eastMoneyData?.high || sinaData?.high || 0,
        low: eastMoneyData?.low || sinaData?.low || 0,
        pre_close: eastMoneyData?.pre_close || sinaData?.pre_close || 0,
        change: eastMoneyData?.change || sinaData?.change || 0,
        pct_change: eastMoneyData?.pct_change || sinaData?.pct_change || 0,
        volume: eastMoneyData?.volume || sinaData?.volume || 0,
        amount: eastMoneyData?.amount || sinaData?.amount || 0,
        pe: eastMoneyData?.pe || 0,
        pb: eastMoneyData?.pb || 0,
        market_cap: eastMoneyData?.market_cap || 0,
        timestamp: new Date(),
        data_sources: []
      };
      
      if (eastMoneyData) integratedData.data_sources.push('eastmoney');
      if (sinaData) integratedData.data_sources.push('sina');
      
      return integratedData;
    } catch (error) {
      console.error(`获取整合股票数据失败:`, error.message);
      throw error;
    }
  }
  


  /**
   * 获取行业估值数据
   */
  async getIndustryValuationData() {
    const cacheKey = 'industry_valuation_data';
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      // 优先使用Tushare API获取行业估值数据
      const tushareData = await this.getTushareIndustryValuations();
      
      if (tushareData && tushareData.length > 0) {
        this.setCachedData(cacheKey, tushareData);
        return tushareData;
      }
      
      // 如果Tushare API失败，回退到东方财富数据源
      console.warn('Tushare行业估值数据获取失败，回退到东方财富数据源');
      const industries = await this.getEastMoneyIndustries();
      
      // 为每个行业获取详细的估值指标
      const valuationData = await Promise.all(
        industries.map(async industry => {
          try {
            // 这里可以根据需要添加更多的估值指标获取逻辑
            return {
              code: industry.code,
              name: industry.name,
              pe: industry.pe,
              pb: industry.pb,
              price: industry.price,
              change: industry.change,
              pct_change: industry.pct_change,
              market_cap: industry.market_cap
            };
          } catch (error) {
            console.error(`获取行业${industry.name}估值数据失败:`, error);
            return industry;
          }
        })
      );
      
      this.setCachedData(cacheKey, valuationData);
      return valuationData;
    } catch (error) {
      console.error('获取行业估值数据失败:', error);
      return [];
    }
  }
  
  /**
   * 获取综合行业股票列表
   * @param {string} industry 行业名称
   * @param {Object} options 查询选项
   */
  async getIndustryStocks(industry, options = {}) {
    const cacheKey = `industry_stocks_${industry}_${JSON.stringify(options)}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      // 优先使用Tushare API
      const tushareData = await this.getTushareIndustryStocks(industry);
      
      if (tushareData && tushareData.length > 0) {
        // 应用分页
        const page = options.page || 1;
        const limit = options.limit || 50;
        const start = (page - 1) * limit;
        const end = start + limit;
        const paginatedData = tushareData.slice(start, end);
        
        const result = {
          list: paginatedData,
          total: tushareData.length,
          page: page,
          limit: limit,
          source: 'tushare'
        };
        
        this.setCachedData(cacheKey, result);
        return result;
      }
      
      // 如果Tushare API失败，可以添加其他数据源的回退逻辑
      console.warn(`Tushare行业${industry}股票数据获取失败，返回空数据`);
      return { list: [], total: 0, page: options.page || 1, limit: options.limit || 50, source: 'none' };
    } catch (error) {
      console.error(`获取行业${industry}股票数据失败:`, error);
      return { list: [], total: 0, page: options.page || 1, limit: options.limit || 50, source: 'error' };
    }
  }
  
  /**
   * 综合获取股票数据 - 从多个数据源整合信息
   * @param {string} symbol 股票代码
   * @param {Object} options 查询选项
   */
  async getStockData(symbol, options = {}) {
    try {
      // 构建数据源优先级列表
      const dataSources = options.dataSources || ['tushare', 'eastmoney', 'sina'];
      
      // 依次尝试各个数据源
      for (const source of dataSources) {
        try {
          let data = null;
          
          switch (source) {
            case 'tushare':
              data = await this.getTushareStockQuote(symbol);
              break;
            case 'eastmoney':
              data = await this.getEastMoneyStockQuote(symbol);
              break;
            case 'sina':
              data = await this.getSinaStockQuote(symbol);
              break;
          }
          
          if (data) {
            return {
              ...data,
              source: source
            };
          }
        } catch (error) {
          console.warn(`从${source}获取${symbol}数据失败，尝试下一个数据源`, error);
        }
      }
      
      // 如果所有数据源都失败，返回默认数据
      console.error(`从所有数据源获取${symbol}数据都失败`);
      return null;
    } catch (error) {
      console.error(`获取股票${symbol}数据失败:`, error);
      return null;
    }
  }
}

export default new ExternalDataService();