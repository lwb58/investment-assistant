import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// 定义API响应格式
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:3000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求重试配置
const retryConfig = {
  maxRetries: 3,
  retryDelay: (retryCount: number) => Math.min(1000 * Math.pow(2, retryCount), 30000), // 指数退避
};

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // 统一处理响应数据
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message || '请求失败');
    }
  },
  async (error: AxiosError) => {
    const config = error.config;
    
    // 请求被取消不重试
    if (axios.isCancel(error)) {
      return Promise.reject(error);
    }

    // 配置重试逻辑
    config._retryCount = config._retryCount || 0;
    
    if (config._retryCount < retryConfig.maxRetries) {
      config._retryCount += 1;
      
      // 等待一段时间后重试
      await new Promise((resolve) => 
        setTimeout(resolve, retryConfig.retryDelay(config._retryCount))
      );
      
      return apiClient(config);
    }

    // 处理特定错误码
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 处理未授权错误
          console.error('未授权访问，请重新登录');
          break;
        case 403:
          console.error('没有权限访问该资源');
          break;
        case 404:
          console.error('请求的资源不存在');
          break;
        case 500:
          console.error('服务器内部错误');
          break;
        default:
          console.error(`请求错误: ${error.response.status}`);
      }
    } else if (error.request) {
      console.error('网络错误，请检查您的网络连接');
    } else {
      console.error('请求配置错误:', error.message);
    }

    return Promise.reject(error);
  }
);

// 估值API
export const valuationApi = {
  // 获取股票估值数据
  getStockValuation: async (stockCode: string) => {
    try {
      return await apiClient.get(`/valuation/${stockCode}`);
    } catch (error) {
      console.error('获取股票估值数据失败:', error);
      throw error;
    }
  },

  // 获取股票历史估值数据
  getHistoricalValuation: async (stockCode: string, period: string = '1y') => {
    try {
      return await apiClient.get(`/valuation/${stockCode}/history`, {
        params: { period },
      });
    } catch (error) {
      console.error('获取历史估值数据失败:', error);
      throw error;
    }
  },

  // 获取行业估值对比
  getIndustryValuation: async (industry: string) => {
    try {
      return await apiClient.get(`/valuation/industry/${industry}`);
    } catch (error) {
      console.error('获取行业估值数据失败:', error);
      throw error;
    }
  },

  // 获取估值决策建议
  getValuationDecision: async (stockCode: string) => {
    try {
      return await apiClient.get(`/valuation/${stockCode}/decision`);
    } catch (error) {
      console.error('获取估值决策建议失败:', error);
      throw error;
    }
  },
  
  // 计算估值（valuationService使用的方法）
  calculateValuation: async (stockCode: string, params: any) => {
    try {
      return await apiClient.post(`/valuation/${stockCode}/calculate`, params);
    } catch (error) {
      console.error('计算估值失败:', error);
      throw error;
    }
  },
  
  // 获取估值历史（valuationService使用的方法）
  getValuationHistory: async (stockCode: string) => {
    try {
      return await apiClient.get(`/valuation/${stockCode}/history`);
    } catch (error) {
      console.error('获取估值历史失败:', error);
      throw error;
    }
  },
  
  // 添加财务数据（valuationService使用的方法）
  addFinancialData: async (data: any) => {
    try {
      return await apiClient.post('/valuation/financials', data);
    } catch (error) {
      console.error('添加财务数据失败:', error);
      throw error;
    }
  },
  
  // 获取历史财务数据（valuationService使用的方法）
  getHistoricalFinancialData: async (stockCode: string, years: number) => {
    try {
      return await apiClient.get(`/valuation/${stockCode}/financials`, {
        params: { years }
      });
    } catch (error) {
      console.error('获取历史财务数据失败:', error);
      throw error;
    }
  },
  
  // 获取股票信息（valuationService间接使用）
  getStockInfo: async (stockCode: string) => {
    try {
      return await apiClient.get(`/stock/${stockCode}/info`);
    } catch (error) {
      console.error('获取股票信息失败:', error);
      throw error;
    }
  },
  
  // 获取相对估值数据
  getRelativeValuation: async (stockCode: string) => {
    try {
      return await apiClient.get(`/valuation/${stockCode}/relative`);
    } catch (error) {
      console.error('获取相对估值数据失败:', error);
      throw error;
    }
  },
  
  // 获取评分数据
  getScoreData: async (stockCode: string) => {
    try {
      return await apiClient.get(`/valuation/${stockCode}/score`);
    } catch (error) {
      console.error('获取评分数据失败:', error);
      throw error;
    }
  },
};

// 股票数据API
export const stockApi = {
  // 搜索股票
  searchStocks: async (keyword: string) => {
    try {
      return await apiClient.get('/stock/search', {
        params: { keyword },
      });
    } catch (error) {
      console.error('搜索股票失败:', error);
      throw error;
    }
  },

  // 获取股票基本信息
  getStockInfo: async (stockCode: string) => {
    try {
      return await apiClient.get(`/stock/${stockCode}/info`);
    } catch (error) {
      console.error('获取股票基本信息失败:', error);
      throw error;
    }
  },

  // 获取股票市场数据
  getStockMarketData: async (stockCode: string) => {
    try {
      return await apiClient.get(`/stock/${stockCode}/market`);
    } catch (error) {
      console.error('获取股票市场数据失败:', error);
      throw error;
    }
  },

  // 获取热门股票
  getHotStocks: async () => {
    try {
      return await apiClient.get('/stock/hot');
    } catch (error) {
      console.error('获取热门股票失败:', error);
      throw error;
    }
  },

  // 获取市场指数
  getMarketIndices: async () => {
    try {
      return await apiClient.get('/stock/market-index');
    } catch (error) {
      console.error('获取市场指数失败:', error);
      throw error;
    }
  },
};

// 投资分析API
export const investmentApi = {
  // 获取投资记录
  getInvestmentRecords: async () => {
    try {
      return await apiClient.get('/investment/records');
    } catch (error) {
      console.error('获取投资记录失败:', error);
      throw error;
    }
  },

  // 添加投资记录
  addInvestmentRecord: async (recordData: any) => {
    try {
      return await apiClient.post('/investment/records', recordData);
    } catch (error) {
      console.error('添加投资记录失败:', error);
      throw error;
    }
  },

  // 更新投资记录
  updateInvestmentRecord: async (recordId: string, recordData: any) => {
    try {
      return await apiClient.put(`/investment/records/${recordId}`, recordData);
    } catch (error) {
      console.error('更新投资记录失败:', error);
      throw error;
    }
  },

  // 删除投资记录
  deleteInvestmentRecord: async (recordId: string) => {
    try {
      return await apiClient.delete(`/investment/records/${recordId}`);
    } catch (error) {
      console.error('删除投资记录失败:', error);
      throw error;
    }
  },
};

// 投资组合API
export const portfolioApi = {
  // 获取投资组合
  getPortfolio: async () => {
    try {
      return await apiClient.get('/portfolio');
    } catch (error) {
      console.error('获取投资组合失败:', error);
      throw error;
    }
  },

  // 添加股票到投资组合
  addToPortfolio: async (stockCode: string, shares: number, price: number) => {
    try {
      return await apiClient.post('/portfolio', { stockCode, shares, price });
    } catch (error) {
      console.error('添加股票到投资组合失败:', error);
      throw error;
    }
  },

  // 更新投资组合中的股票
  updatePortfolioItem: async (stockCode: string, shares: number, price: number) => {
    try {
      return await apiClient.put(`/portfolio/${stockCode}`, { shares, price });
    } catch (error) {
      console.error('更新投资组合中的股票失败:', error);
      throw error;
    }
  },

  // 从投资组合中移除股票
  removeFromPortfolio: async (stockCode: string) => {
    try {
      return await apiClient.delete(`/portfolio/${stockCode}`);
    } catch (error) {
      console.error('从投资组合中移除股票失败:', error);
      throw error;
    }
  },
};

// 投资记录API
export const investmentRecordApi = {
  // 获取所有投资记录
  getAllRecords: async () => {
    try {
      return await apiClient.get('/investment/records/all');
    } catch (error) {
      console.error('获取所有投资记录失败:', error);
      throw error;
    }
  },

  // 获取投资记录统计
  getRecordsStats: async (period: string = 'all') => {
    try {
      return await apiClient.get('/investment/records/stats', {
        params: { period },
      });
    } catch (error) {
      console.error('获取投资记录统计失败:', error);
      throw error;
    }
  },
};

// 健康检查API
export const healthApi = {
  // 检查系统健康状态
  checkHealth: async () => {
    try {
      return await apiClient.get('/health');
    } catch (error) {
      console.error('检查系统健康状态失败:', error);
      throw error;
    }
  },
};

// 行业分析API
export const industryApi = {
  // 获取所有行业列表
  getAllIndustries: async () => {
    try {
      return await apiClient.get('/industry/list');
    } catch (error) {
      console.error('获取行业列表失败:', error);
      throw error;
    }
  },

  // 获取行业详情
  getIndustryDetails: async (industryCode: string) => {
    try {
      return await apiClient.get(`/industry/${industryCode}`);
    } catch (error) {
      console.error('获取行业详情失败:', error);
      throw error;
    }
  },

  // 获取行业排名
  getIndustryRanking: async (metric: string = 'marketCap') => {
    try {
      return await apiClient.get('/industry/ranking', {
        params: { metric },
      });
    } catch (error) {
      console.error('获取行业排名失败:', error);
      throw error;
    }
  },
};

// 收藏股票API
export const favoriteStockApi = {
  // 获取收藏股票列表
  getFavorites: async () => {
    try {
      return await apiClient.get('/favorite/stocks');
    } catch (error) {
      console.error('获取收藏股票列表失败:', error);
      throw error;
    }
  },

  // 添加收藏股票
  addFavorite: async (stockCode: string) => {
    try {
      return await apiClient.post('/favorite/stocks', { stockCode });
    } catch (error) {
      console.error('添加收藏股票失败:', error);
      throw error;
    }
  },

  // 移除收藏股票
  removeFavorite: async (stockCode: string) => {
    try {
      return await apiClient.delete(`/favorite/stocks/${stockCode}`);
    } catch (error) {
      console.error('移除收藏股票失败:', error);
      throw error;
    }
  },
};

// 导出所有API模块
// 市场数据API模块
const marketApi = {
  // 获取市场指数数据
  getIndexData: async () => {
    try {
      const response = await apiClient.get('/stock/market-index');
      // 由于后端API已经通过响应拦截器处理，直接返回即可
      return response;
    } catch (error) {
      console.error('获取市场指数数据失败:', error);
      throw error;
    }
  }
};

export default {
  valuation: valuationApi,
  stock: stockApi,
  investment: investmentApi,
  portfolio: portfolioApi,
  investmentRecord: investmentRecordApi,
  health: healthApi,
  industry: industryApi,
  favoriteStock: favoriteStockApi,
  market: marketApi
};