import { portfolioApi } from './apiService';

// 投资组合接口
export interface Portfolio {
  id: number;
  name: string;
  description: string;
  totalValue?: number;
  createdAt: string;
  updatedAt: string;
  holdings?: PortfolioHolding[];
}

// 投资组合持仓接口
export interface PortfolioHolding {
  id: number;
  portfolioId: number;
  stockCode: string;
  quantity: number;
  purchasePrice: number;
  currentPrice?: number;
  totalValue?: number;
  profitLoss?: number;
  profitLossPercentage?: number;
  createdAt: string;
  updatedAt: string;
  stockInfo?: {
    name?: string;
    symbol?: string;
  };
}

// 资产配置接口
export interface PortfolioAllocation {
  stockCode: string;
  stockName: string;
  allocation: number;
  value: number;
}

// 模拟数据
const mockPortfolios: Portfolio[] = [
  {
    id: 1,
    name: '我的投资组合',
    description: '长期价值投资组合',
    totalValue: 158750,
    createdAt: '2024-01-15T08:30:00Z',
    updatedAt: '2024-03-20T14:45:00Z',
    holdings: [
      {
        id: 1,
        portfolioId: 1,
        stockCode: 'AAPL',
        quantity: 50,
        purchasePrice: 180.5,
        currentPrice: 195.2,
        totalValue: 9760,
        profitLoss: 735,
        profitLossPercentage: 8.14,
        createdAt: '2024-01-15T08:30:00Z',
        updatedAt: '2024-03-20T14:45:00Z',
        stockInfo: {
          name: 'Apple Inc.',
          symbol: 'AAPL'
        }
      },
      {
        id: 2,
        portfolioId: 1,
        stockCode: 'MSFT',
        quantity: 30,
        purchasePrice: 350.75,
        currentPrice: 378.42,
        totalValue: 11352.6,
        profitLoss: 830.1,
        profitLossPercentage: 7.89,
        createdAt: '2024-01-20T10:15:00Z',
        updatedAt: '2024-03-20T14:45:00Z',
        stockInfo: {
          name: 'Microsoft Corporation',
          symbol: 'MSFT'
        }
      }
    ]
  },
  {
    id: 2,
    name: '成长股投资',
    description: '高增长潜力股票组合',
    totalValue: 89240,
    createdAt: '2024-02-05T16:20:00Z',
    updatedAt: '2024-03-18T09:10:00Z',
    holdings: [
      {
        id: 3,
        portfolioId: 2,
        stockCode: 'NVDA',
        quantity: 15,
        purchasePrice: 650.25,
        currentPrice: 720.80,
        totalValue: 10812,
        profitLoss: 1058.25,
        profitLossPercentage: 10.85,
        createdAt: '2024-02-05T16:20:00Z',
        updatedAt: '2024-03-18T09:10:00Z',
        stockInfo: {
          name: 'NVIDIA Corporation',
          symbol: 'NVDA'
        }
      }
    ]
  }
];

// 缓存
let cachedPortfolios: Portfolio[] | null = null;
let cachedCurrentPortfolio: Portfolio | null = null;

/**
 * 投资组合服务类
 */
export class PortfolioService {
  /**
   * 创建投资组合
   */
  async createPortfolio(name: string, description: string = ''): Promise<Portfolio> {
    try {
      // 调用API创建投资组合
      const newPortfolio = await portfolioApi.createPortfolio(name, description);
      // 清除缓存
      cachedPortfolios = null;
      return newPortfolio;
    } catch (error) {
      console.error('创建投资组合失败:', error);
      // 返回模拟数据
      const mockPortfolio: Portfolio = {
        id: Date.now(),
        name,
        description,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      mockPortfolios.push(mockPortfolio);
      cachedPortfolios = null;
      return mockPortfolio;
    }
  }

  /**
   * 获取所有投资组合
   */
  async getAllPortfolios(): Promise<Portfolio[]> {
    // 检查缓存
    if (cachedPortfolios) {
      return cachedPortfolios;
    }

    try {
      // 调用API获取投资组合列表
      const portfolios = await portfolioApi.getAllPortfolios();
      cachedPortfolios = portfolios;
      return portfolios;
    } catch (error) {
      console.error('获取投资组合列表失败:', error);
      // 返回模拟数据
      cachedPortfolios = mockPortfolios;
      return mockPortfolios;
    }
  }

  /**
   * 获取单个投资组合详情
   */
  async getPortfolioById(id: number): Promise<Portfolio> {
    // 如果缓存的当前投资组合ID匹配，直接返回
    if (cachedCurrentPortfolio && cachedCurrentPortfolio.id === id) {
      return cachedCurrentPortfolio;
    }

    try {
      // 调用API获取投资组合详情
      const portfolio = await portfolioApi.getPortfolioById(id);
      cachedCurrentPortfolio = portfolio;
      return portfolio;
    } catch (error) {
      console.error('获取投资组合详情失败:', error);
      // 返回模拟数据
      const mockPortfolio = mockPortfolios.find(p => p.id === id);
      if (!mockPortfolio) {
        throw new Error('投资组合不存在');
      }
      cachedCurrentPortfolio = mockPortfolio;
      return mockPortfolio;
    }
  }

  /**
   * 更新投资组合
   */
  async updatePortfolio(id: number, data: { name: string; description: string }): Promise<Portfolio> {
    try {
      // 调用API更新投资组合
      const updatedPortfolio = await portfolioApi.updatePortfolio(id, data);
      // 清除缓存
      cachedPortfolios = null;
      if (cachedCurrentPortfolio && cachedCurrentPortfolio.id === id) {
        cachedCurrentPortfolio = updatedPortfolio;
      }
      return updatedPortfolio;
    } catch (error) {
      console.error('更新投资组合失败:', error);
      // 更新模拟数据
      const portfolioIndex = mockPortfolios.findIndex(p => p.id === id);
      if (portfolioIndex === -1) {
        throw new Error('投资组合不存在');
      }
      mockPortfolios[portfolioIndex] = {
        ...mockPortfolios[portfolioIndex],
        ...data,
        updatedAt: new Date().toISOString()
      };
      cachedPortfolios = null;
      if (cachedCurrentPortfolio && cachedCurrentPortfolio.id === id) {
        cachedCurrentPortfolio = mockPortfolios[portfolioIndex];
      }
      return mockPortfolios[portfolioIndex];
    }
  }

  /**
   * 删除投资组合
   */
  async deletePortfolio(id: number): Promise<void> {
    try {
      // 调用API删除投资组合
      await portfolioApi.deletePortfolio(id);
      // 清除缓存
      cachedPortfolios = null;
      if (cachedCurrentPortfolio && cachedCurrentPortfolio.id === id) {
        cachedCurrentPortfolio = null;
      }
    } catch (error) {
      console.error('删除投资组合失败:', error);
      // 更新模拟数据
      const portfolioIndex = mockPortfolios.findIndex(p => p.id === id);
      if (portfolioIndex === -1) {
        throw new Error('投资组合不存在');
      }
      mockPortfolios.splice(portfolioIndex, 1);
      cachedPortfolios = null;
      if (cachedCurrentPortfolio && cachedCurrentPortfolio.id === id) {
        cachedCurrentPortfolio = null;
      }
    }
  }

  /**
   * 添加持仓
   */
  async addHolding(
    portfolioId: number,
    stockCode: string,
    quantity: number,
    purchasePrice: number
  ): Promise<PortfolioHolding> {
    try {
      // 调用API添加持仓
      const newHolding = await portfolioApi.addHolding(portfolioId, stockCode, quantity, purchasePrice);
      // 清除缓存
      cachedPortfolios = null;
      if (cachedCurrentPortfolio && cachedCurrentPortfolio.id === portfolioId) {
        if (!cachedCurrentPortfolio.holdings) {
          cachedCurrentPortfolio.holdings = [];
        }
        cachedCurrentPortfolio.holdings.push(newHolding);
      }
      return newHolding;
    } catch (error) {
      console.error('添加持仓失败:', error);
      // 更新模拟数据
      const portfolio = mockPortfolios.find(p => p.id === portfolioId);
      if (!portfolio) {
        throw new Error('投资组合不存在');
      }
      const mockHolding: PortfolioHolding = {
        id: Date.now(),
        portfolioId,
        stockCode,
        quantity,
        purchasePrice,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        stockInfo: {
          name: `${stockCode} Stock`,
          symbol: stockCode
        }
      };
      if (!portfolio.holdings) {
        portfolio.holdings = [];
      }
      portfolio.holdings.push(mockHolding);
      cachedPortfolios = null;
      if (cachedCurrentPortfolio && cachedCurrentPortfolio.id === portfolioId) {
        if (!cachedCurrentPortfolio.holdings) {
          cachedCurrentPortfolio.holdings = [];
        }
        cachedCurrentPortfolio.holdings.push(mockHolding);
      }
      return mockHolding;
    }
  }

  /**
   * 更新持仓
   */
  async updateHolding(
    holdingId: number,
    quantity: number,
    purchasePrice?: number
  ): Promise<PortfolioHolding> {
    try {
      // 调用API更新持仓
      const updatedHolding = await portfolioApi.updateHolding(holdingId, quantity, purchasePrice);
      // 清除缓存
      cachedPortfolios = null;
      if (cachedCurrentPortfolio && cachedCurrentPortfolio.holdings) {
        const holdingIndex = cachedCurrentPortfolio.holdings.findIndex(h => h.id === holdingId);
        if (holdingIndex !== -1) {
          cachedCurrentPortfolio.holdings[holdingIndex] = updatedHolding;
        }
      }
      return updatedHolding;
    } catch (error) {
      console.error('更新持仓失败:', error);
      // 更新模拟数据
      let updatedHolding: PortfolioHolding | null = null;
      for (const portfolio of mockPortfolios) {
        if (portfolio.holdings) {
          const holdingIndex = portfolio.holdings.findIndex(h => h.id === holdingId);
          if (holdingIndex !== -1) {
            const updates: Partial<PortfolioHolding> = { quantity, updatedAt: new Date().toISOString() };
            if (purchasePrice !== undefined) {
              updates.purchasePrice = purchasePrice;
            }
            portfolio.holdings[holdingIndex] = {
              ...portfolio.holdings[holdingIndex],
              ...updates
            };
            updatedHolding = portfolio.holdings[holdingIndex];
            break;
          }
        }
      }
      if (!updatedHolding) {
        throw new Error('持仓不存在');
      }
      cachedPortfolios = null;
      return updatedHolding;
    }
  }

  /**
   * 移除持仓
   */
  async removeHolding(holdingId: number): Promise<void> {
    try {
      // 调用API移除持仓
      await portfolioApi.removeHolding(holdingId);
      // 清除缓存
      cachedPortfolios = null;
      if (cachedCurrentPortfolio && cachedCurrentPortfolio.holdings) {
        cachedCurrentPortfolio.holdings = cachedCurrentPortfolio.holdings.filter(h => h.id !== holdingId);
      }
    } catch (error) {
      console.error('移除持仓失败:', error);
      // 更新模拟数据
      for (const portfolio of mockPortfolios) {
        if (portfolio.holdings) {
          portfolio.holdings = portfolio.holdings.filter(h => h.id !== holdingId);
        }
      }
      cachedPortfolios = null;
    }
  }

  /**
   * 获取投资组合资产配置
   */
  async getPortfolioAllocation(portfolioId: number): Promise<PortfolioAllocation[]> {
    try {
      // 调用API获取资产配置
      const allocation = await portfolioApi.getPortfolioAllocation(portfolioId);
      return allocation;
    } catch (error) {
      console.error('获取资产配置失败:', error);
      // 返回模拟数据
      const portfolio = mockPortfolios.find(p => p.id === portfolioId);
      if (!portfolio || !portfolio.holdings || portfolio.holdings.length === 0) {
        return [];
      }
      
      const totalValue = portfolio.holdings.reduce((sum, holding) => sum + (holding.totalValue || 0), 0);
      return portfolio.holdings.map(holding => ({
        stockCode: holding.stockCode,
        stockName: holding.stockInfo?.name || holding.stockCode,
        allocation: totalValue > 0 ? ((holding.totalValue || 0) / totalValue) * 100 : 0,
        value: holding.totalValue || 0
      }));
    }
  }

  /**
   * 清除缓存
   */
  clearCache(): void {
    cachedPortfolios = null;
    cachedCurrentPortfolio = null;
  }
}

// 导出单例实例
export default new PortfolioService();
