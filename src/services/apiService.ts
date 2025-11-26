import axios from 'axios';

// 创建axios实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
  timeout: 15000, // 增加超时时间以减少临时网络问题导致的失败
  headers: {
    'Content-Type': 'application/json'
  }
});

// 重试配置
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 基础重试延迟时间（毫秒）
const RETRYABLE_STATUS_CODES = [429, 500, 502, 503, 504]; // 可重试的HTTP状态码

// 指数退避重试函数
const retryWithBackoff = async (fn, retries = 0) => {
  try {
    return await fn();
  } catch (error) {
    // 检查是否应该重试
    if (retries < MAX_RETRIES && 
        error.response && 
        RETRYABLE_STATUS_CODES.includes(error.response.status)) {
      
      const delay = RETRY_DELAY * Math.pow(2, retries) + Math.random() * 1000; // 指数退避 + 随机抖动
      console.log(`请求失败，${delay}ms后重试 (${retries + 1}/${MAX_RETRIES})...`);
      
      // 等待延迟时间
      await new Promise(resolve => setTimeout(resolve, delay));
      
      // 递归重试
      return retryWithBackoff(fn, retries + 1);
    }
    
    // 达到最大重试次数或不需要重试的错误，直接抛出
    throw error;
  }
};

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('auth_token');
    
    // 如果存在token，则添加到请求头
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 为请求添加时间戳以避免缓存问题
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      };
    }
    
    // 记录请求开始时间（用于性能监控）
    config.meta = {
      startTime: Date.now()
    };
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 包含重试逻辑
apiClient.interceptors.response.use(
  (response) => {
    // 计算响应时间并记录（用于性能监控）
    if (response.config.meta) {
      const responseTime = Date.now() - response.config.meta.startTime;
      
      // 如果响应时间较长，记录警告日志
      if (responseTime > 2000) {
        console.warn(`请求响应时间较长: ${responseTime}ms - ${response.config.method?.toUpperCase()} ${response.config.url}`);
      }
    }
    
    return response;
  },
  async (error) => {
    // 处理错误响应
    if (error.config) {
      // 计算响应时间并记录（用于性能监控）
      if (error.config.meta) {
        const responseTime = Date.now() - error.config.meta.startTime;
        console.error(`请求失败 (${responseTime}ms): ${error.config.method?.toUpperCase()} ${error.config.url}`);
      }
      
      // 检查是否已经重试过
      if (!error.config._retry) {
        // 标记为已重试
        error.config._retry = true;
        
        // 对于可重试的错误，使用重试函数
        if (error.response && RETRYABLE_STATUS_CODES.includes(error.response.status)) {
          try {
            // 使用指数退避重试
            return await retryWithBackoff(() => apiClient(error.config));
          } catch (retryError) {
            error = retryError; // 更新为最后一次重试的错误
          }
        }
      }
    }
    
    // 处理不同类型的错误
    if (error.response) {
      // 服务器返回了错误状态码
      const status = error.response.status;
      
      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('auth_token');
          console.error('认证失败，请重新登录');
          // 这里可以添加跳转登录页的逻辑
          break;
        case 403:
          console.error('没有权限访问此资源');
          break;
        case 404:
          console.error('请求的资源不存在');
          break;
        case 429:
          console.error('请求过于频繁，请稍后再试');
          break;
        case 500:
        case 502:
        case 503:
        case 504:
          console.error('服务器错误，请稍后再试');
          break;
        default:
          console.error(`请求失败: ${status}`);
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('网络错误，请检查您的网络连接');
    } else {
      // 请求配置出错
      console.error('请求配置错误:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// 估值相关API
export const valuationApi = {
  /**
   * 计算股票估值
   * @param symbol 股票代码
   * @param params 估值参数
   */
  calculateValuation: (symbol: string, params: any = {}) => {
    return apiClient.post('/valuation/calculate', { symbol, params });
  },
  
  /**
   * 获取估值历史记录
   * @param symbol 股票代码
   */
  getValuationHistory: (symbol: string) => {
    return apiClient.get(`/valuation/history/${symbol}`);
  },
  
  /**
   * 添加财务数据
   * @param data 财务数据
   */
  addFinancialData: (data: any) => {
    return apiClient.post('/valuation/financial-data', data);
  },
  
  /**
   * 批量导入财务数据
   * @param data 财务数据数组
   */
  importFinancialData: (data: any[]) => {
    return apiClient.post('/valuation/import-financials', data);
  },
  
  /**
   * 获取历史财务数据
   * @param symbol 股票代码
   * @param years 年数
   */
  getHistoricalFinancialData: (symbol: string, years: number = 5) => {
    return apiClient.get(`/valuation/financial-history/${symbol}?years=${years}`);
  },
  
  /**
   * 获取估值指标数据
   * @param symbol 股票代码
   */
  getValuationData: (symbol: string) => {
    return apiClient.get(`/api/valuation/metrics/${symbol}`);
  },
  
  /**
   * 获取基本面数据
   * @param symbol 股票代码
   */
  getFundamentalData: (symbol: string) => {
    return apiClient.get(`/api/valuation/fundamental/${symbol}`);
  },
  
  /**
   * 获取事件数据
   * @param symbol 股票代码
   */
  getEventsData: (symbol: string) => {
    return apiClient.get(`/api/valuation/events/${symbol}`);
  }
};

// 股票数据相关API
export const stockApi = {
  /**
   * 获取股票列表
   */
  getStockList: () => {
    return apiClient.get('/stock/stocks');
  },
  
  /**
   * 获取股票基本信息
   * @param symbol 股票代码
   */
  getStockInfo: (symbol: string) => {
    return apiClient.get(`/stock/${symbol}`);
  },
  
  /**
   * 获取股票详情
   * @param symbol 股票代码
   */
  getStockDetail: (symbol: string) => {
    return apiClient.get(`/api/stock/detail/${symbol}`);
  },
  
  /**
   * 获取股票行情
   * @param symbol 股票代码
   */
  getStockQuote: (symbol: string) => {
    return apiClient.get(`/stock/${symbol}/quote`);
  },
  
  /**
   * 获取大盘指数数据
   */
  getMarketIndex: () => {
    return apiClient.get('/stock/market-index');
  },
  
  /**
   * 搜索股票
   * @param keyword 搜索关键词
   */
  searchStocks: (keyword: string) => {
    return apiClient.get(`/stock/search?keyword=${encodeURIComponent(keyword)}`);
  },
  
  /**
   * 获取行业数据
   */
  getIndustryData: () => {
    return apiClient.get('/stock/industry/list');
  },
  
  /**
   * 获取股票财务数据
   * @param symbol 股票代码
   */
  getFinancialData: (symbol: string) => {
    return apiClient.get(`/stock/${symbol}/financial`);
  }
};

// 投资建议相关API
export const investmentApi = {
  /**
   * 生成投资建议
   * @param symbol 股票代码
   * @param valuationResult 估值结果
   */
  generateInvestmentAdvice: (symbol: string, valuationResult?: any) => {
    return apiClient.post('/valuation/investment-advice', { symbol, valuationResult });
  },

  /**
   * 获取投资建议历史
   * @param symbol 股票代码
   * @param limit 限制数量
   */
  getInvestmentAdviceHistory: (symbol: string, limit?: number) => {
    return apiClient.get(`/valuation/investment-advice/${symbol}`, { params: { limit } });
  },

  /**
   * 批量获取投资建议
   * @param symbols 股票代码数组
   */
  getBatchInvestmentAdvice: (symbols: string[]) => {
    return apiClient.post('/valuation/investment-advice/batch', { symbols });
  }
};

// 投资组合相关API
const portfolioApi = {
  /**
   * 创建投资组合
   * @param name 投资组合名称
   * @param description 投资组合描述
   */
  createPortfolio: async (name: string, description: string = '') => {
    const response = await axios.post(`/api/portfolios`, {
      name,
      description
    });
    return response.data;
  },

  /**
   * 获取所有投资组合
   */
  getAllPortfolios: async () => {
    const response = await axios.get(`/api/portfolios`);
    return response.data;
  },

  /**
   * 获取单个投资组合详情
   * @param id 投资组合ID
   */
  getPortfolioById: async (id: number) => {
    const response = await axios.get(`/api/portfolios/${id}`);
    return response.data;
  },

  /**
   * 更新投资组合
   * @param id 投资组合ID
   * @param data 更新数据
   */
  updatePortfolio: async (id: number, data: { name: string; description: string }) => {
    const response = await axios.put(`/api/portfolios/${id}`, data);
    return response.data;
  },

  /**
   * 删除投资组合
   * @param id 投资组合ID
   */
  deletePortfolio: async (id: number) => {
    const response = await axios.delete(`/api/portfolios/${id}`);
    return response.data;
  },

  /**
   * 添加持仓
   * @param portfolioId 投资组合ID
   * @param stockCode 股票代码
   * @param quantity 数量
   * @param purchasePrice 购买价格
   */
  addHolding: async (portfolioId: number, stockCode: string, quantity: number, purchasePrice: number) => {
    const response = await axios.post(`/api/portfolios/${portfolioId}/holdings`, {
      stockCode,
      quantity,
      purchasePrice
    });
    return response.data;
  },

  /**
   * 更新持仓
   * @param holdingId 持仓ID
   * @param quantity 数量
   * @param purchasePrice 购买价格（可选）
   */
  updateHolding: async (holdingId: number, quantity: number, purchasePrice?: number) => {
    const data: any = { quantity };
    if (purchasePrice !== undefined) {
      data.purchasePrice = purchasePrice;
    }
    const response = await axios.put(`/api/portfolios/holdings/${holdingId}`, data);
    return response.data;
  },

  /**
   * 移除持仓
   * @param holdingId 持仓ID
   */
  removeHolding: async (holdingId: number) => {
    const response = await axios.delete(`/api/portfolios/holdings/${holdingId}`);
    return response.data;
  },

  /**
   * 获取投资组合资产配置
   * @param portfolioId 投资组合ID
   */
  getPortfolioAllocation: async (portfolioId: number) => {
    const response = await axios.get(`/api/portfolios/${portfolioId}/allocation`);
    return response.data;
  }
};

// 投资记录相关API
export const investmentRecordApi = {
  /**
   * 获取投资记录
   */
  getInvestmentRecords: () => {
    return apiClient.get('/investment-records');
  },
  
  /**
   * 添加投资记录
   * @param recordData 投资记录数据
   */
  addInvestmentRecord: (recordData: any) => {
    return apiClient.post('/investment-records', recordData);
  },
  
  /**
   * 更新投资记录
   * @param id 记录ID
   * @param recordData 更新数据
   */
  updateInvestmentRecord: (id: string, recordData: any) => {
    return apiClient.put(`/investment-records/${id}`, recordData);
  },
  
  /**
   * 删除投资记录
   * @param id 记录ID
   */
  deleteInvestmentRecord: (id: string) => {
    return apiClient.delete(`/investment-records/${id}`);
  },
  
  /**
   * 获取投资分析数据
   */
  getInvestmentAnalysis: () => {
    return apiClient.get('/investment-records/analysis');
  },
  
  /**
   * 导出投资记录
   */
  exportInvestmentRecords: () => {
    return apiClient.get('/investment-records/export', {
      responseType: 'blob'
    });
  }
};

// 健康检查API
export const healthApi = {
  /**
   * 检查服务状态
   */
  checkHealth: () => {
    return apiClient.get('/health');
  }
};

// 行业分析API接口
export const industryApi = {
  // 获取所有行业列表
  getIndustries: async () => {
    return await apiClient.get('/api/industry');
  },
  
  // 获取行业详情
  getIndustryDetail: async (industryCode: string) => {
    return await apiClient.get(`/api/industry/${industryCode}`);
  },
  
  // 获取行业内股票列表
  getIndustryStocks: async (industryCode: string, page = 1, pageSize = 20) => {
    return await apiClient.get(`/api/industry/${industryCode}/stocks`, {
      params: { page, pageSize }
    });
  },
  
  // 比较多个行业
  compareIndustries: async (industryCodes: string) => {
    return await apiClient.get('/api/industry/analysis/compare', {
      params: { industryCodes }
    });
  },
  
  // 获取行业趋势数据
  getIndustryTrend: async (industryCode: string, period = '1y') => {
    return await apiClient.get(`/api/industry/${industryCode}/trend`, {
      params: { period }
    });
  },
  
  // 获取行业估值排名
  getIndustryValuationRanking: async (metric = 'pe', order = 'asc') => {
    return await apiClient.get('/api/industry/valuation/ranking', {
      params: { metric, order }
    });
  }
};

// API服务类
class ApiService {
  // 投资记录API
  get investmentApi() {
    return investmentRecordApi;
  }
  
  // 行业分析API
  get industryApi() {
    return industryApi;
  }
}

// API服务实例
export const apiService = new ApiService();

export default {
  valuation: valuationApi,
  stock: stockApi,
  investment: investmentApi,
  portfolio: portfolioApi,
  investmentRecord: investmentRecordApi,
  health: healthApi,
  industry: industryApi
};