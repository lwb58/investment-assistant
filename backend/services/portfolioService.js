import { getDB } from '../config/db.js';

/**
 * 投资组合服务类
 * 提供投资组合管理的核心功能
 */
class PortfolioService {
  /**
   * 创建投资组合
   * @param {string} name 投资组合名称
   * @param {string} description 投资组合描述
   * @returns {Promise<Object>} 创建的投资组合
   */
  async createPortfolio(name, description = '') {
    try {
      const db = await getDB();
      const result = await db.run(
        'INSERT INTO portfolios (name, description, created_at, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)',
        [name, description]
      );
      
      return this.getPortfolioById(result.lastID);
    } catch (error) {
      console.error('创建投资组合失败:', error);
      throw new Error('创建投资组合失败');
    }
  }

  /**
   * 获取所有投资组合
   * @returns {Promise<Array>} 投资组合列表
   */
  async getAllPortfolios() {
    try {
      const db = await getDB();
      const portfolios = await db.all(
        'SELECT * FROM portfolios ORDER BY created_at DESC'
      );
      
      // 为每个投资组合获取持仓信息
      for (const portfolio of portfolios) {
        portfolio.holdings = await this.getPortfolioHoldings(portfolio.id);
        portfolio.performance = await this.calculatePortfolioPerformance(portfolio.id);
      }
      
      return portfolios;
    } catch (error) {
      console.error('获取投资组合列表失败:', error);
      throw new Error('获取投资组合列表失败');
    }
  }

  /**
   * 根据ID获取投资组合
   * @param {number} portfolioId 投资组合ID
   * @returns {Promise<Object>} 投资组合详情
   */
  async getPortfolioById(portfolioId) {
    try {
      const db = await getDB();
      const portfolio = await db.get(
        'SELECT * FROM portfolios WHERE id = ?',
        [portfolioId]
      );
      
      if (!portfolio) {
        throw new Error('投资组合不存在');
      }
      
      portfolio.holdings = await this.getPortfolioHoldings(portfolioId);
      portfolio.performance = await this.calculatePortfolioPerformance(portfolioId);
      
      return portfolio;
    } catch (error) {
      console.error('获取投资组合详情失败:', error);
      throw error;
    }
  }

  /**
   * 更新投资组合
   * @param {number} portfolioId 投资组合ID
   * @param {Object} data 更新数据
   * @returns {Promise<Object>} 更新后的投资组合
   */
  async updatePortfolio(portfolioId, data) {
    try {
      const db = await getDB();
      const { name, description } = data;
      await db.run(
        'UPDATE portfolios SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        [name, description, portfolioId]
      );
      
      return this.getPortfolioById(portfolioId);
    } catch (error) {
      console.error('更新投资组合失败:', error);
      throw new Error('更新投资组合失败');
    }
  }

  /**
   * 删除投资组合
   * @param {number} portfolioId 投资组合ID
   * @returns {Promise<boolean>} 是否删除成功
   */
  async deletePortfolio(portfolioId) {
    try {
      const db = await getDB();
      // 先删除相关的持仓记录
      await db.run('DELETE FROM portfolio_holdings WHERE portfolio_id = ?', [portfolioId]);
      // 再删除投资组合
      const result = await db.run('DELETE FROM portfolios WHERE id = ?', [portfolioId]);
      
      return result.changes > 0;
    } catch (error) {
      console.error('删除投资组合失败:', error);
      throw new Error('删除投资组合失败');
    }
  }

  /**
   * 添加持仓到投资组合
   * @param {number} portfolioId 投资组合ID
   * @param {string} stockCode 股票代码
   * @param {number} quantity 数量
   * @param {number} purchasePrice 购买价格
   * @returns {Promise<Object>} 更新后的投资组合
   */
  async addHolding(portfolioId, stockCode, quantity, purchasePrice) {
    try {
      const db = await getDB();
      // 检查投资组合是否存在
      const portfolioExists = await db.get('SELECT 1 FROM portfolios WHERE id = ?', [portfolioId]);
      if (!portfolioExists) {
        throw new Error('投资组合不存在');
      }
      
      // 检查是否已有该股票的持仓
      const existingHolding = await db.get(
        'SELECT * FROM portfolio_holdings WHERE portfolio_id = ? AND stock_code = ?',
        [portfolioId, stockCode]
      );
      
      if (existingHolding) {
        // 更新持仓数量和平均价格
        const totalCost = existingHolding.quantity * existingHolding.avg_price + quantity * purchasePrice;
        const totalQuantity = existingHolding.quantity + quantity;
        const newAvgPrice = totalCost / totalQuantity;
        
        await db.run(
          'UPDATE portfolio_holdings SET quantity = ?, avg_price = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
          [totalQuantity, newAvgPrice, existingHolding.id]
        );
      } else {
        // 添加新持仓
        await db.run(
          'INSERT INTO portfolio_holdings (portfolio_id, stock_code, quantity, avg_price, created_at, updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)',
          [portfolioId, stockCode, quantity, purchasePrice]
        );
      }
      
      return this.getPortfolioById(portfolioId);
    } catch (error) {
      console.error('添加持仓失败:', error);
      throw new Error('添加持仓失败');
    }
  }

  /**
   * 更新持仓
   * @param {number} holdingId 持仓ID
   * @param {number} quantity 新数量
   * @param {number} purchasePrice 新购买价格
   * @returns {Promise<Object>} 更新后的投资组合
   */
  async updateHolding(holdingId, quantity, purchasePrice = null) {
    try {
      const db = await getDB();
      const holding = await db.get('SELECT * FROM portfolio_holdings WHERE id = ?', [holdingId]);
      if (!holding) {
        throw new Error('持仓不存在');
      }
      
      if (purchasePrice !== null) {
        await db.run(
          'UPDATE portfolio_holdings SET quantity = ?, avg_price = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
          [quantity, purchasePrice, holdingId]
        );
      } else {
        await db.run(
          'UPDATE portfolio_holdings SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
          [quantity, holdingId]
        );
      }
      
      return this.getPortfolioById(holding.portfolio_id);
    } catch (error) {
      console.error('更新持仓失败:', error);
      throw new Error('更新持仓失败');
    }
  }

  /**
   * 从投资组合中移除持仓
   * @param {number} holdingId 持仓ID
   * @returns {Promise<Object>} 更新后的投资组合
   */
  async removeHolding(holdingId) {
    try {
      const db = await getDB();
      const holding = await db.get('SELECT * FROM portfolio_holdings WHERE id = ?', [holdingId]);
      if (!holding) {
        throw new Error('持仓不存在');
      }
      
      await db.run('DELETE FROM portfolio_holdings WHERE id = ?', [holdingId]);
      
      return this.getPortfolioById(holding.portfolio_id);
    } catch (error) {
      console.error('移除持仓失败:', error);
      throw new Error('移除持仓失败');
    }
  }

  /**
   * 获取投资组合的所有持仓
   * @param {number} portfolioId 投资组合ID
   * @returns {Promise<Array>} 持仓列表
   */
  async getPortfolioHoldings(portfolioId) {
    try {
      const db = await getDB();
      const holdings = await db.all(
        'SELECT * FROM portfolio_holdings WHERE portfolio_id = ? ORDER BY created_at DESC',
        [portfolioId]
      );
      
      // 为每个持仓获取当前价格（这里使用模拟价格，实际应从API获取）
      for (const holding of holdings) {
        // 模拟当前价格（可以扩展为从市场数据API获取）
        holding.current_price = this.getMockPrice(holding.stock_code);
        holding.total_cost = holding.quantity * holding.avg_price;
        holding.current_value = holding.quantity * holding.current_price;
        holding.profit = holding.current_value - holding.total_cost;
        holding.profit_percentage = (holding.profit / holding.total_cost) * 100;
      }
      
      return holdings;
    } catch (error) {
      console.error('获取持仓列表失败:', error);
      return [];
    }
  }

  /**
   * 计算投资组合绩效
   * @param {number} portfolioId 投资组合ID
   * @returns {Promise<Object>} 绩效数据
   */
  async calculatePortfolioPerformance(portfolioId) {
    try {
      const db = await getDB();
      const holdings = await this.getPortfolioHoldings(portfolioId);
      
      let totalCost = 0;
      let totalValue = 0;
      let totalProfit = 0;
      
      holdings.forEach(holding => {
        totalCost += holding.total_cost;
        totalValue += holding.current_value;
        totalProfit += holding.profit;
      });
      
      const totalProfitPercentage = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0;
      
      return {
        total_cost: totalCost,
        total_value: totalValue,
        total_profit: totalProfit,
        total_profit_percentage: totalProfitPercentage,
        holdings_count: holdings.length,
        // 模拟风险指标（实际应基于历史数据计算）
        risk_metrics: {
          volatility: Math.random() * 0.15 + 0.1, // 10%-25%的波动率
          sharpe_ratio: Math.random() * 1.5 + 0.5, // 0.5-2.0的夏普比率
          max_drawdown: Math.random() * 0.2 + 0.1 // 10%-30%的最大回撤
        }
      };
    } catch (error) {
      console.error('计算投资组合绩效失败:', error);
      return {
        total_cost: 0,
        total_value: 0,
        total_profit: 0,
        total_profit_percentage: 0,
        holdings_count: 0,
        risk_metrics: {
          volatility: 0,
          sharpe_ratio: 0,
          max_drawdown: 0
        }
      };
    }
  }

  /**
   * 获取投资组合的资产配置
   * @param {number} portfolioId 投资组合ID
   * @returns {Promise<Object>} 资产配置数据
   */
  async getPortfolioAllocation(portfolioId) {
    try {
      const db = await getDB();
      const holdings = await this.getPortfolioHoldings(portfolioId);
      const totalValue = holdings.reduce((sum, holding) => sum + holding.current_value, 0);
      
      const allocation = holdings.map(holding => ({
        stock_code: holding.stock_code,
        value: holding.current_value,
        percentage: totalValue > 0 ? (holding.current_value / totalValue) * 100 : 0,
        quantity: holding.quantity
      }));
      
      return {
        total_value: totalValue,
        allocation: allocation
      };
    } catch (error) {
      console.error('获取资产配置失败:', error);
      return {
        total_value: 0,
        allocation: []
      };
    }
  }

  /**
   * 生成模拟当前价格
   * @private
   */
  getMockPrice(stockCode) {
    // 生成随机价格，基于股票代码的哈希值确保一致性
    const hash = stockCode.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const basePrice = (hash % 1000) + 10; // 生成10-1010之间的价格
    const volatility = 0.05; // 5%的波动范围
    const randomFactor = 1 + (Math.random() * 2 - 1) * volatility;
    return parseFloat((basePrice * randomFactor).toFixed(2));
  }
}

// 导出单例实例
export default new PortfolioService();