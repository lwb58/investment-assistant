import axios from 'axios';

/**
 * 持仓分析服务类
 * 用于处理持仓数据的获取、保存、删除等操作
 */
class PositionAnalysisService {
  constructor() {
    // 后端API基础URL
    this.baseURL = 'http://localhost:8000/api/position-analysis';
    // 创建axios实例
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
    });
  }

  /**
   * 获取所有持仓记录
   * @returns {Promise<Array>} 持仓记录数组
   */
  async getStockPositions() {
    try {
      const response = await this.api.get('/positions');
      // 数据转换：将后端返回的字段转换为前端期望的格式
      return response.data.map(position => ({
        stockCode: position.stockCode,
        stockName: position.stockName,
        holdingQuantity: position.quantity || 0,
        currentCost: position.costPrice || 0,
        currentPrice: position.currentPrice || 0,
        totalCost: position.totalCost || 0,
        currentValue: position.marketValue || 0,
        profitAmount: position.profit || 0,
        profitRate: position.profitRate || 0,
        remark: position.remark || '',
        id: position.id
      }));
    } catch (error) {
      console.error('从API获取持仓数据失败:', error);
      throw error;
    }
  }

  /**
   * 保存持仓记录（新增或更新）
   * @param {Object} position - 持仓数据
   * @returns {Promise<Object>} 保存结果
   */
  async saveStockPosition(position) {
    try {
      // 准备发送给后端的数据，确保符合后端模型要求
      // 注意：前端表单使用的是holdingQuantity和currentCost字段
      const preparedData = {
        stockCode: position.stockCode || position.code || '',
        stockName: position.stockName || position.name || '',
        quantity: typeof position.holdingQuantity === 'string' ? parseFloat(position.holdingQuantity) : position.holdingQuantity,
        costPrice: typeof position.currentCost === 'string' ? parseFloat(position.currentCost) : position.currentCost,
        remark: position.remark || ''
      };
      
      // 进行基本验证
      if (!preparedData.stockCode) {
        throw new Error('股票代码不能为空');
      }
      if (!preparedData.stockName) {
        throw new Error('股票名称不能为空');
      }
      if (!preparedData.quantity || preparedData.quantity <= 0) {
        throw new Error('持有数量必须大于0');
      }
      if (!preparedData.costPrice || preparedData.costPrice <= 0) {
        throw new Error('成本价必须大于0');
      }
      
      // 检查是否有id来判断是新增还是更新
      if (position.id) {
        // 更新持仓
        const response = await this.api.put(`/positions/${position.id}`, preparedData);
        return response.data;
      } else {
        // 新增持仓
        const response = await this.api.post('/positions', preparedData);
        return response.data;
      }
    } catch (error) {
      console.error('保存持仓数据失败:', error);
      throw error;
    }
  }

  /**
   * 删除持仓记录
   * @param {string} stockCode - 股票代码
   * @returns {Promise<Object>} 删除结果
   */
  async deleteStockPosition(positionId) {
    try {
      const response = await this.api.delete(`/positions/${positionId}`);
      return response.data;
    } catch (error) {
      console.error('删除持仓数据失败:', error);
      throw error;
    }
  }

  /**
   * 获取持仓分析概览
   * @returns {Promise<Object>} 概览数据
   */
  async getPositionOverview() {
    try {
      const response = await this.api.get('/overview');
      return response.data;
    } catch (error) {
      console.error('获取持仓分析概览失败:', error);
      throw error;
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
const positionAnalysisService = new PositionAnalysisService();
export default positionAnalysisService;
