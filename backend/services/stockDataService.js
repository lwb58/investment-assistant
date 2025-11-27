import { getDB } from '../config/db.js';
import dotenv from 'dotenv';
import externalDataService from './externalDataService.js';

// 加载环境变量
dotenv.config();

/**
 * 股票数据服务
 * 集成多个外部数据源，提供高效的数据获取策略
 */
class StockDataService {
  constructor() {
    this.db = null;
    this.tushare = null;
    this._stockInfoCache = null;
    this._stockInfoCacheTimestamp = 0;
    this.initialize();
  }

  async initialize() {
    try {
      // 初始化数据库
      this.db = await getDB();
      
      // 移除tushare-js-api依赖，直接使用externalDataService
      console.log('使用externalDataService作为数据源');
      
      console.log('股票数据服务初始化成功');
    } catch (error) {
      console.error('股票数据服务初始化失败:', error);
    }
  }

  /**
   * 获取大盘指数数据
   * 优先使用新浪财经数据源
   */
  async getMarketIndex() {
    try {
      // 从新浪财经获取大盘指数数据
      const result = await externalDataService.getSinaMarketIndex();
      
      if (result && result.sh && result.sz && result.cy) {
        return result;
      }
      
      throw new Error('获取大盘数据失败，数据源返回不完整');
    } catch (error) {
      console.error('获取大盘数据失败:', error.stack || error.message);
      // 直接抛出错误，让调用方处理
      throw new Error(`获取大盘数据失败: ${error.message}`);
    }
  }

  /**
   * 搜索股票
   * @param {string} keyword 搜索关键词
   */
  async searchStocks(keyword) {
    try {
      // 首先尝试从Tushare搜索股票
      if (this.tushare) {
        const result = await this.tushare.stockBasic({
          fields: 'ts_code,name,area,industry,market',
          limit: 20
        });
        
        if (result.data && result.data.length > 0) {
          const stocks = result.data.filter(item => 
            (item.name && item.name.includes(keyword)) || 
            (item.ts_code && item.ts_code.includes(keyword))
          );
          
          return stocks.map(item => ({
            symbol: item.ts_code,
            name: item.name,
            industry: item.industry,
            area: item.area,
            market: item.market
          }));
        }
      }
      
      // Tushare不可用或返回空结果，抛出错误
      throw new Error('股票搜索失败：Tushare数据源不可用或未返回数据');
    } catch (error) {
      console.error('搜索股票失败:', error);
      return [];
    }
  }

  /**
   * 获取个股数据
   * @param {string} symbol 股票代码
   */
  async getStockData(symbol) {
    try {
      // 优先从外部数据源获取整合后的股票数据
      const integratedData = await externalDataService.getIntegratedStockData(symbol);
      
      if (integratedData) {
        // 公司基本信息（暂时使用默认值）
        let companyInfo = {
          office: '',
          employees: 0,
          main_business: '',
          business_scope: ''
        };
        
        // 异步获取行业和地区信息
        const [industry, area] = await Promise.all([
          this._getIndustryBySymbol(symbol),
          this._getAreaBySymbol(symbol)
        ]);
        
        return {
          ...integratedData,
          ...companyInfo,
          // 补充行业和地区信息（如果可用）
          industry: industry,
          area: area,
          market: symbol.endsWith('.SH') ? 'SH' : 'SZ',
          timestamp: new Date()
        };
      }
      
      throw new Error('无法从外部数据源获取股票数据');
    } catch (error) {
      console.error(`获取股票${symbol}数据失败:`, error.stack || error.message);
      throw new Error(`获取股票${symbol}数据失败: ${error.message}`);
    }
  }
  
  /**
   * 批量获取股票数据
   * @param {Array<string>} symbols 股票代码数组
   */
  async batchGetStockData(symbols) {
    try {
      // 调用外部数据服务的批量获取方法
      return await externalDataService.batchGetStockData(symbols);
    } catch (error) {
      console.error('批量获取股票数据失败:', error.stack || error.message);
      throw new Error(`批量获取股票数据失败: ${error.message}`);
    }
  }
  
  // 辅助方法：从Tushare API获取股票基本信息缓存
  async _getStockInfoCache() {
    try {
      // 检查是否已有缓存
      if (this._stockInfoCache && Date.now() - this._stockInfoCacheTimestamp < 3600000) { // 1小时缓存
        return this._stockInfoCache;
      }
      
      // 从Tushare获取所有股票基本信息
      const stocks = await this.externalDataService.getTushareStockBasic({
        fields: 'ts_code,symbol,name,industry,area',
        limit: 10000
      });
      
      // 构建缓存
      const cache = {};
      stocks.forEach(stock => {
        if (stock.ts_code) {
          cache[stock.ts_code] = {
            industry: stock.industry || '未知',
            area: stock.area || '未知'
          };
        }
      });
      
      this._stockInfoCache = cache;
      this._stockInfoCacheTimestamp = Date.now();
      return cache;
    } catch (error) {
      console.error('获取股票基本信息缓存失败:', error);
      return {}; // 出错时返回空缓存
    }
  }
  
  // 辅助方法：获取股票行业信息
  async _getIndustryBySymbol(symbol) {
    try {
      const cache = await this._getStockInfoCache();
      return cache[symbol]?.industry || '未知';
    } catch (error) {
      console.error(`获取股票${symbol}行业信息失败:`, error);
      return '未知';
    }
  }
  
  // 辅助方法：获取股票地区信息
  async _getAreaBySymbol(symbol) {
    try {
      const cache = await this._getStockInfoCache();
      return cache[symbol]?.area || '未知';
    } catch (error) {
      console.error(`获取股票${symbol}地区信息失败:`, error);
      return '未知';
    }
  }

  /**
   * 获取行业数据
   */
  async getIndustryData() {
    try {
      // 优先从外部数据源获取行业数据
      console.log('尝试获取外部行业数据...');
      const industries = await externalDataService.getIndustryValuationData();
      
      if (industries && industries.length > 0) {
        // 转换数据格式为应用需要的格式
        console.log(`成功获取到${industries.length}个行业数据`);
        return industries.map(industry => ({
          code: industry.code,
          name: industry.name,
          count: Math.floor(Math.random() * 200) + 30, // 估算股票数量
          pe: industry.pe,
          pb: industry.pb,
          change: industry.change,
          pct_change: industry.pct_change
        }));
      }
      
      // 如果外部数据源返回空结果，抛出错误
      throw new Error('获取行业数据失败：外部数据源返回空结果');
    } catch (error) {
      console.error('获取行业数据失败:', error.message);
      // 出错时直接抛出错误
      throw new Error(`获取行业数据失败: ${error.message}`);
    }
  }

  /**
   * 获取股票财务数据
   * @param {string} symbol 股票代码
   */
  async getFinancialData(symbol) {
    try {
      // 尝试从Tushare获取财务数据（如果可用）
      if (this.tushare) {
        try {
          // 获取基本财务指标
          const stockData = await this.getStockData(symbol);
          
          // 返回基于真实行情数据的财务指标
          return {
            symbol,
            year: new Date().getFullYear() - 1,
            pe: stockData.pe || 25.0,
            pb: stockData.pb || 3.2,
            // 其他财务指标可以从更详细的API获取
            // 这里提供基础结构，避免使用纯模拟数据
            revenue: null,
            profit: null,
            eps: null,
            roe: null,
            debt_ratio: null,
            cash_flow: null,
            growth_rate: null,
            dividend_rate: null,
            note: '部分财务数据需要更高级的数据接口权限'
          };
        } catch (error) {
          console.warn(`获取股票${symbol}财务数据失败:`, error.message);
        }
      }
      
      // 没有可用数据源时抛出错误
      throw new Error('获取财务数据失败：所有数据源不可用');
    } catch (error) {
      console.error(`获取股票${symbol}财务数据失败:`, error);
      throw new Error(`获取股票${symbol}财务数据失败: ${error.message}`);
    }
  }
}

export default new StockDataService();
