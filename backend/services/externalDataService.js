import axios from 'axios';
import { getDB } from '../config/db.js';
import dotenv from 'dotenv';

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
      timeout: 15000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
      }
    });
    this.cache = new Map();
    this.cacheTTL = 5 * 60 * 1000; // 5分钟缓存
    this.initialize();
  }

  async initialize() {
    try {
      this.db = await getDB();
      console.log('外部数据源服务初始化成功');
    } catch (error) {
      console.error('外部数据源服务初始化失败:', error);
    }
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
      // 东方财富股票行情接口
      const market = symbol.endsWith('.SH') ? 'sh' : 'sz';
      const stockCode = symbol.split('.')[0];
      const url = `https://push2.eastmoney.com/api/qt/stock/get?fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f148,f152,f168,f177,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f207,f208,f209,f222,f223,f224,f225,f226,f227,f228,f229,f230,f231,f232,f233,f234,f235,f236,f237,f238,f239,f240,f241,f242,f243,f244,f245,f246,f247,f248,f249,f250,f251,f252,f253,f254,f255,f256,f257,f258,f259,f260,f261,f262,f263,f264,f265,f266,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f277,f278,f279,f280,f281,f282,f283,f284,f285,f286,f287,f288,f289,f290,f291,f292,f293,f294,f295,f296,f297,f298,f299,f300,f301,f302,f303,f304,f305,f306,f307,f308,f309,f310,f311,f312,f313,f314,f315,f316,f317,f318,f319,f320,f321,f322,f323,f324,f325,f326,f327,f328,f329,f330,f331,f332,f333,f334,f335,f336,f337,f338,f339,f340,f341,f342,f343,f344,f345,f346,f347,f348,f349,f350,f351,f352,f353,f354,f355,f356,f357,f358,f359,f360,f361,f362,f363,f364,f365,f366,f367,f368,f369,f370,f371,f372,f373,f374,f375,f376,f377,f378,f379,f380,f381,f382,f383,f384,f385,f386,f387,f388,f389,f390,f391,f392,f393,f394,f395,f396,f397,f398,f399,f400,f401,f402,f403,f404,f405,f406,f407,f408,f409,f410,f411,f412,f413,f414,f415,f416,f417,f418,f419,f420,f421,f422,f423,f424,f425,f426,f427,f428,f429,f430,f431,f432,f433,f434,f435,f436,f437,f438,f439,f440,f441,f442,f443,f444,f445,f446,f447,f448,f449,f450,f451,f452,f453,f454,f455,f456,f457,f458,f459,f460,f461,f462,f463,f464,f465,f466,f467,f468,f469,f470,f471,f472,f473,f474,f475,f476,f477,f478,f479,f480,f481,f482,f483,f484,f485,f486,f487,f488,f489,f490,f491,f492,f493,f494,f495,f496,f497,f498,f499,f500,f501,f502,f503,f504,f505,f506,f507,f508,f509,f510,f511,f512,f513,f514,f515,f516,f517,f518,f519,f520,f521,f522,f523,f524,f525,f526,f527,f528,f529,f530,f531,f532,f533,f534,f535,f536,f537,f538,f539,f540,f541,f542,f543,f544,f545,f546,f547,f548,f549,f550,f551,f552,f553,f554,f555,f556,f557,f558,f559,f560,f561,f562,f563,f564,f565,f566,f567,f568,f569,f570,f571,f572,f573,f574,f575,f576,f577,f578,f579,f580,f581,f582,f583,f584,f585,f586,f587,f588,f589,f590,f591,f592,f593,f594,f595,f596,f597,f598,f599,f600,f601,f602,f603,f604,f605,f606,f607,f608,f609,f610,f611,f612,f613,f614,f615,f616,f617,f618,f619,f620,f621,f622,f623,f624,f625,f626,f627,f628,f629,f630,f631,f632,f633,f634,f635,f636,f637,f638,f639,f640,f641,f642,f643,f644,f645,f646,f647,f648,f649,f650,f651,f652,f653,f654,f655,f656,f657,f658,f659,f660,f661,f662,f663,f664,f665,f666,f667,f668,f669,f670,f671,f672,f673,f674,f675,f676,f677,f678,f679,f680,f681,f682,f683,f684,f685,f686,f687,f688,f689,f690,f691,f692,f693,f694,f695,f696,f697,f698,f699,f700&secid=${market}.${stockCode}&ut=fcea386e386d9c584928df10665e7bfb&forcect=1&fields2=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f148,f152,f168,f177,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f207,f208,f209,f222,f223,f224,f225,f226,f227,f228,f229,f230,f231,f232,f233,f234,f235,f236,f237,f238,f239,f240,f241,f242,f243,f244,f245,f246,f247,f248,f249,f250,f251,f252,f253,f254,f255,f256,f257,f258,f259,f260,f261,f262,f263,f264,f265,f266,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f277,f278,f279,f280,f281,f282,f283,f284,f285,f286,f287,f288,f289,f290,f291,f292,f293,f294,f295,f296,f297,f298,f299,f300,f301,f302,f303,f304,f305,f306,f307,f308,f309,f310,f311,f312,f313,f314,f315,f316,f317,f318,f319,f320,f321,f322,f323,f324,f325,f326,f327,f328,f329,f330,f331,f332,f333,f334,f335,f336,f337,f338,f339,f340,f341,f342,f343,f344,f345,f346,f347,f348,f349,f350,f351,f352,f353,f354,f355,f356,f357,f358,f359,f360,f361,f362,f363,f364,f365,f366,f367,f368,f369,f370,f371,f372,f373,f374,f375,f376,f377,f378,f379,f380,f381,f382,f383,f384,f385,f386,f387,f388,f389,f390,f391,f392,f393,f394,f395,f396,f397,f398,f399,f400,f401,f402,f403,f404,f405,f406,f407,f408,f409,f410,f411,f412,f413,f414,f415,f416,f417,f418,f419,f420,f421,f422,f423,f424,f425,f426,f427,f428,f429,f430,f431,f432,f433,f434,f435,f436,f437,f438,f439,f440,f441,f442,f443,f444,f445,f446,f447,f448,f449,f450,f451,f452,f453,f454,f455,f456,f457,f458,f459,f460,f461,f462,f463,f464,f465,f466,f467,f468,f469,f470,f471,f472,f473,f474,f475,f476,f477,f478,f479,f480,f481,f482,f483,f484,f485,f486,f487,f488,f489,f490,f491,f492,f493,f494,f495,f496,f497,f498,f499,f500,f501,f502,f503,f504,f505,f506,f507,f508,f509,f510,f511,f512,f513,f514,f515,f516,f517,f518,f519,f520,f521,f522,f523,f524,f525,f526,f527,f528,f529,f530,f531,f532,f533,f534,f535,f536,f537,f538,f539,f540,f541,f542,f543,f544,f545,f546,f547,f548,f549,f550,f551,f552,f553,f554,f555,f556,f557,f558,f559,f560,f561,f562,f563,f564,f565,f566,f567,f568,f569,f570,f571,f572,f573,f574,f575,f576,f577,f578,f579,f580,f581,f582,f583,f584,f585,f586,f587,f588,f589,f590,f591,f592,f593,f594,f595,f596,f597,f598,f599,f600,f601,f602,f603,f604,f605,f606,f607,f608,f609,f610,f611,f612,f613,f614,f615,f616,f617,f618,f619,f620,f621,f622,f623,f624,f625,f626,f627,f628,f629,f630,f631,f632,f633,f634,f635,f636,f637,f638,f639,f640,f641,f642,f643,f644,f645,f646,f647,f648,f649,f650,f651,f652,f653,f654,f655,f656,f657,f658,f659,f660,f661,f662,f663,f664,f665,f666,f667,f668,f669,f670,f671,f672,f673,f674,f675,f676,f677,f678,f679,f680,f681,f682,f683,f684,f685,f686,f687,f688,f689,f690,f691,f692,f693,f694,f695,f696,f697,f698,f699,f700&ut=fcea386e386d9c584928df10665e7bfb&forcect=1&cb=jQuery183013480495686887644_1688444444444&_=1688444444445`;
      
      const response = await this.axios.get(url);
      // 解析JSONP响应
      const jsonpData = response.data;
      const jsonStr = jsonpData.match(/\(({.*})\)/)[1];
      const data = JSON.parse(jsonStr);
      
      if (data.data) {
        const quote = data.data;
        const result = {
          symbol: `${quote.f12}.${market === 'sh' ? 'SH' : 'SZ'}`,
          name: quote.f14,
          price: quote.f2,
          open: quote.f17,
          high: quote.f15,
          low: quote.f16,
          pre_close: quote.f18,
          change: quote.f3,
          pct_change: quote.f4,
          volume: quote.f5,
          amount: quote.f6,
          pe: quote.f8,
          pb: quote.f9,
          market_cap: quote.f20,
          timestamp: new Date()
        };
        
        this.setCachedData(cacheKey, result);
        return result;
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
      const market = symbol.endsWith('.SH') ? 'sh' : 'sz';
      const stockCode = symbol.split('.')[0];
      const url = `https://hq.sinajs.cn/list=${market}${stockCode}`;
      
      const response = await this.axios.get(url);
      const dataStr = response.data;
      
      // 解析新浪财经的数据格式
      const match = dataStr.match(/var hq_str_\w+="([^"]+)"/);
      if (match && match[1]) {
        const data = match[1].split(',');
        
        const result = {
          symbol: symbol,
          name: data[0],
          open: parseFloat(data[1]),
          pre_close: parseFloat(data[2]),
          price: parseFloat(data[3]),
          high: parseFloat(data[4]),
          low: parseFloat(data[5]),
          volume: parseFloat(data[8]),
          amount: parseFloat(data[9]),
          timestamp: new Date()
        };
        
        result.change = result.price - result.pre_close;
        result.pct_change = (result.change / result.pre_close) * 100;
        
        this.setCachedData(cacheKey, result);
        return result;
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
    const cacheKey = 'sina_market_index';
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      // 一次性获取多个指数数据
      const url = 'https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006';
      
      const response = await this.axios.get(url);
      const dataStr = response.data;
      
      // 解析上证指数
      const shMatch = dataStr.match(/var hq_str_s_sh000001="([^"]+)"/);
      // 解析深证成指
      const szMatch = dataStr.match(/var hq_str_s_sz399001="([^"]+)"/);
      // 解析创业板指
      const cyMatch = dataStr.match(/var hq_str_s_sz399006="([^"]+)"/);
      
      const parseIndex = (match, name) => {
        if (match && match[1]) {
          const data = match[1].split(',');
          return {
            name: name,
            open: parseFloat(data[1]),
            pre_close: parseFloat(data[2]),
            price: parseFloat(data[3]),
            high: parseFloat(data[4]),
            low: parseFloat(data[5]),
            volume: parseFloat(data[8]),
            amount: parseFloat(data[9]),
            change: parseFloat(data[3]) - parseFloat(data[2]),
            pct_change: ((parseFloat(data[3]) - parseFloat(data[2])) / parseFloat(data[2])) * 100
          };
        }
        return null;
      };
      
      const result = {
        sh: parseIndex(shMatch, '上证指数'),
        sz: parseIndex(szMatch, '深证成指'),
        cy: parseIndex(cyMatch, '创业板指'),
        timestamp: new Date()
      };
      
      this.setCachedData(cacheKey, result);
      return result;
    } catch (error) {
      console.error('获取新浪财经大盘指数失败:', error);
    }
    return null;
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
      // 并行请求多个数据源
      const [eastMoneyData, sinaData] = await Promise.all([
        this.getEastMoneyStockQuote(symbol),
        this.getSinaStockQuote(symbol)
      ]);
      
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
      console.error(`获取整合股票数据失败:`, error);
      return null;
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
      // 从东方财富获取行业数据
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
}

export default new ExternalDataService();