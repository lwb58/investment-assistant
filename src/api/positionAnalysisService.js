import axios from 'axios';
import apiService from './apiService.js';

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
      const positions = response.data;
      
      // 并行获取所有股票的行情数据
      const enhancedPositions = await Promise.all(
        positions.map(async (position) => {
          let currentPrice, changeRate, changeAmount, openingPrice;
          
          try {
            // 尝试从API获取股票实时行情数据
            const quoteData = await apiService.getStockQuotes(position.stockCode);
            if (quoteData && quoteData.coreQuotes) {
              // 从API获取的真实数据
              currentPrice = quoteData.coreQuotes.currentPrice || 0;
              
              // 直接使用API返回的涨跌幅数据（避免重复计算）
              // 优先使用changeRate字段，如果不存在则使用changePercent
              changeRate = quoteData.coreQuotes.changeRate || quoteData.coreQuotes.changePercent || 0;
              changeAmount = quoteData.coreQuotes.priceChange || (currentPrice - (quoteData.coreQuotes.prevClosePrice || 0));
              
              // 获取开盘价（如果API提供）
              openingPrice = quoteData.coreQuotes.openPrice || currentPrice;
            } else {
              // 如果API调用失败，使用模拟数据作为后备
              currentPrice = position.currentPrice || this.getMockStockPrice(position.stockCode);
              const basePrice = currentPrice * 0.95; // 模拟昨收价
              changeAmount = currentPrice - basePrice;
              changeRate = (changeAmount / basePrice) * 100;
              openingPrice = this.getMockOpeningPrice(position.stockCode, currentPrice);
            }
          } catch (error) {
            console.warn(`获取股票 ${position.stockCode} 行情数据失败，使用模拟数据:`, error);
            // 出错时使用模拟数据
            currentPrice = position.currentPrice || this.getMockStockPrice(position.stockCode);
            const basePrice = currentPrice * 0.95; // 模拟昨收价
            changeAmount = currentPrice - basePrice;
            changeRate = (changeAmount / basePrice) * 100;
            openingPrice = this.getMockOpeningPrice(position.stockCode, currentPrice);
          }
          
          // 计算基本字段
          const currentValue = position.marketValue || (position.quantity * currentPrice);
          const totalCost = position.totalCost || (position.quantity * (position.costPrice || 0));
          const profitAmount = position.profit || (currentValue - totalCost);
          const profitRate = position.profitRate || (totalCost > 0 ? (profitAmount / totalCost) * 100 : 0);
          
          // 使用涨跌幅计算当日盈亏金额
          const todayProfit = position.quantity * changeAmount;
          
          return {
            stockCode: position.stockCode,
            stockName: position.stockName,
            holdingQuantity: position.quantity || 0,
            currentCost: position.costPrice || 0,
            currentPrice,
            totalCost,
            currentValue,
            profitAmount,
            profitRate,
            openingPrice,
            todayProfit, // 当日盈亏金额
            todayProfitRate: changeRate, // 使用涨跌幅作为当日涨幅
            remark: position.remark || '',
            id: position.id
          };
        })
      );
      
      return enhancedPositions;
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
      // 获取当前价格（保留，可能用于其他计算）
      const currentPrice = parseFloat(position.currentPrice) || this.getMockStockPrice(position.stockCode);
      
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
      
      // 计算补仓后的盈亏 - 使用补仓价格而非当前价格计算
      const totalValueAfter = totalQuantityAfter * additionalPrice;
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
  
  /**
   * 获取模拟开盘价
   * @param {string} stockCode - 股票代码
   * @param {number} currentPrice - 当前价格
   * @returns {number} 模拟的开盘价
   */
  getMockOpeningPrice(stockCode, currentPrice) {
    // 使用股票代码生成相对稳定的开盘价
    // 确保开盘价与当前价格有一定关联但不完全相同
    const seed = stockCode.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    // 创建一个基于股票代码的随机因子，但与当前价格相关联
    const dayRandom = 0.98 + (Math.sin(Date.now() / 1000000 + seed) + 1) * 0.02; // 0.98-1.02之间的因子
    // 基于当前价格计算开盘价，添加一定波动
    const openingPrice = currentPrice * dayRandom;
    return Number(openingPrice.toFixed(2));
  }
}

// 导出单例实例
const positionAnalysisService = new PositionAnalysisService();
export default positionAnalysisService;
