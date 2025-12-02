/**
 * 成本分析服务类
 * 处理股票成本分析相关的数据管理和计算
 */
class CostAnalysisService {
  constructor() {
    // 使用localStorage作为临时数据存储
    this.storageKey = 'stock_cost_analysis';
  }

  /**
   * 获取所有持仓股票数据
   * @returns {Promise<Array>} 持仓股票列表
   */
  async getStockPositions() {
    try {
      // 尝试从localStorage获取数据
      const storedData = localStorage.getItem(this.storageKey);
      if (storedData) {
        const positions = JSON.parse(storedData);
        // 为每个持仓计算盈亏信息
        return await Promise.all(positions.map(async (position) => {
          return await this.calculatePositionProfit(position);
        }));
      }
      return [];
    } catch (error) {
      console.error('获取持仓数据失败:', error);
      return [];
    }
  }

  /**
   * 保存股票持仓数据
   * @param {Object} positionData - 持仓数据
   * @returns {Promise<Object>} 保存后的持仓数据
   */
  async saveStockPosition(positionData) {
    try {
      const positions = await this.getStockPositions();
      const existingIndex = positions.findIndex(p => p.stockCode === positionData.stockCode);
      
      if (existingIndex >= 0) {
        // 更新现有持仓
        positions[existingIndex] = {
          ...positions[existingIndex],
          ...positionData,
          updatedAt: new Date().toISOString()
        };
      } else {
        // 添加新持仓
        positions.push({
          ...positionData,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        });
      }
      
      localStorage.setItem(this.storageKey, JSON.stringify(positions));
      // 重新计算盈亏并返回
      return await this.calculatePositionProfit(positions.find(p => p.stockCode === positionData.stockCode));
    } catch (error) {
      console.error('保存持仓数据失败:', error);
      throw error;
    }
  }

  /**
   * 删除股票持仓
   * @param {string} stockCode - 股票代码
   * @returns {Promise<boolean>} 删除成功返回true
   */
  async deleteStockPosition(stockCode) {
    try {
      const positions = await this.getStockPositions();
      const filteredPositions = positions.filter(p => p.stockCode !== stockCode);
      localStorage.setItem(this.storageKey, JSON.stringify(filteredPositions));
      return true;
    } catch (error) {
      console.error('删除持仓数据失败:', error);
      throw error;
    }
  }

  /**
   * 计算持仓盈亏信息
   * @param {Object} position - 持仓数据
   * @returns {Promise<Object>} 包含盈亏信息的持仓数据
   */
  async calculatePositionProfit(position) {
    try {
      // 获取股票实时价格（这里模拟，实际应调用接口）
      // 由于是模拟环境，我们使用随机价格进行演示
      const currentPrice = this.getMockStockPrice(position.stockCode);
      
      // 计算盈亏
      const totalCost = parseFloat(position.holdingQuantity) * parseFloat(position.currentCost);
      const currentValue = parseFloat(position.holdingQuantity) * currentPrice;
      const profitAmount = currentValue - totalCost;
      const profitRate = totalCost > 0 ? (profitAmount / totalCost) * 100 : 0;
      
      return {
        ...position,
        currentPrice,
        totalCost,
        currentValue,
        profitAmount,
        profitRate
      };
    } catch (error) {
      console.error('计算盈亏失败:', error);
      return position;
    }
  }

  /**
   * 计算补仓后的成本和盈亏预测
   * @param {Object} position - 当前持仓
   * @param {number} additionalPrice - 补仓价格
   * @param {number} additionalQuantity - 补仓数量
   * @returns {Promise<Object>} 补仓后的预测数据
   */
  async calculateAdditionalPurchase(position, additionalPrice, additionalQuantity) {
    try {
      // 获取当前价格用于计算盈亏
      const currentPrice = this.getMockStockPrice(position.stockCode);
      
      // 计算现有持仓
      const currentQuantity = parseFloat(position.holdingQuantity);
      const currentCost = parseFloat(position.currentCost);
      const totalCurrentCost = currentQuantity * currentCost;
      
      // 计算补仓
      const additionalCost = additionalPrice * additionalQuantity;
      
      // 计算新的总成本和平均成本
      const totalQuantityAfter = currentQuantity + additionalQuantity;
      const totalCostAfter = totalCurrentCost + additionalCost;
      const averageCostAfter = totalQuantityAfter > 0 ? totalCostAfter / totalQuantityAfter : 0;
      
      // 计算补仓后的盈亏
      const totalValueAfter = totalQuantityAfter * currentPrice;
      const profitAmountAfter = totalValueAfter - totalCostAfter;
      const profitRateAfter = totalCostAfter > 0 ? (profitAmountAfter / totalCostAfter) * 100 : 0;
      
      return {
        currentPrice,
        additionalPrice,
        additionalQuantity,
        totalQuantityAfter,
        totalCostAfter,
        averageCostAfter,
        totalValueAfter,
        profitAmountAfter,
        profitRateAfter
      };
    } catch (error) {
      console.error('计算补仓预测失败:', error);
      throw error;
    }
  }

  /**
   * 获取模拟股票价格
   * @param {string} stockCode - 股票代码
   * @returns {number} 模拟的当前价格
   */
  getMockStockPrice(stockCode) {
    // 使用股票代码生成相对稳定的随机价格
    const seed = stockCode.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const basePrice = (seed % 100) + 10; // 基础价格在10-110之间
    // 添加一些随机波动，但保持相对稳定
    const randomFactor = 0.9 + (Math.sin(Date.now() / 100000 + seed) + 1) * 0.1; // 0.9-1.1之间的波动因子
    return Number((basePrice * randomFactor).toFixed(2));
  }
}

// 导出单例实例
const costAnalysisService = new CostAnalysisService();
export default costAnalysisService;
