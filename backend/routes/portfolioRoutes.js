import express from 'express';
import portfolioService from '../services/portfolioService.js';

const router = express.Router();

/**
 * @route POST /api/portfolios
 * @description 创建新的投资组合
 */
router.post('/portfolios', async (req, res) => {
  try {
    const { name, description } = req.body;
    
    if (!name || name.trim() === '') {
      return res.status(400).json({
        success: false,
        error: '投资组合名称不能为空'
      });
    }
    
    const portfolio = await portfolioService.createPortfolio(name, description);
    
    return res.status(201).json({
      success: true,
      data: portfolio
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message || '创建投资组合失败'
    });
  }
});

/**
 * @route GET /api/portfolios
 * @description 获取所有投资组合列表
 */
router.get('/portfolios', async (req, res) => {
  try {
    const portfolios = await portfolioService.getAllPortfolios();
    
    return res.status(200).json({
      success: true,
      data: portfolios
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message || '获取投资组合列表失败'
    });
  }
});

/**
 * @route GET /api/portfolios/:id
 * @description 获取单个投资组合详情
 */
router.get('/portfolios/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const portfolioId = parseInt(id, 10);
    
    if (isNaN(portfolioId)) {
      return res.status(400).json({
        success: false,
        error: '无效的投资组合ID'
      });
    }
    
    const portfolio = await portfolioService.getPortfolioById(portfolioId);
    
    return res.status(200).json({
      success: true,
      data: portfolio
    });
  } catch (error) {
    if (error.message === '投资组合不存在') {
      return res.status(404).json({
        success: false,
        error: error.message
      });
    }
    
    return res.status(500).json({
      success: false,
      error: error.message || '获取投资组合详情失败'
    });
  }
});

/**
 * @route PUT /api/portfolios/:id
 * @description 更新投资组合信息
 */
router.put('/portfolios/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const portfolioId = parseInt(id, 10);
    const { name, description } = req.body;
    
    if (isNaN(portfolioId)) {
      return res.status(400).json({
        success: false,
        error: '无效的投资组合ID'
      });
    }
    
    if (!name || name.trim() === '') {
      return res.status(400).json({
        success: false,
        error: '投资组合名称不能为空'
      });
    }
    
    const updatedPortfolio = await portfolioService.updatePortfolio(portfolioId, { name, description });
    
    return res.status(200).json({
      success: true,
      data: updatedPortfolio
    });
  } catch (error) {
    if (error.message === '投资组合不存在') {
      return res.status(404).json({
        success: false,
        error: error.message
      });
    }
    
    return res.status(500).json({
      success: false,
      error: error.message || '更新投资组合失败'
    });
  }
});

/**
 * @route DELETE /api/portfolios/:id
 * @description 删除投资组合
 */
router.delete('/portfolios/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const portfolioId = parseInt(id, 10);
    
    if (isNaN(portfolioId)) {
      return res.status(400).json({
        success: false,
        error: '无效的投资组合ID'
      });
    }
    
    const success = await portfolioService.deletePortfolio(portfolioId);
    
    if (!success) {
      return res.status(404).json({
        success: false,
        error: '投资组合不存在'
      });
    }
    
    return res.status(200).json({
      success: true,
      message: '投资组合删除成功'
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message || '删除投资组合失败'
    });
  }
});

/**
 * @route POST /api/portfolios/:id/holdings
 * @description 向投资组合添加持仓
 */
router.post('/portfolios/:id/holdings', async (req, res) => {
  try {
    const { id } = req.params;
    const portfolioId = parseInt(id, 10);
    const { stockCode, quantity, purchasePrice } = req.body;
    
    if (isNaN(portfolioId)) {
      return res.status(400).json({
        success: false,
        error: '无效的投资组合ID'
      });
    }
    
    if (!stockCode || quantity <= 0 || purchasePrice <= 0) {
      return res.status(400).json({
        success: false,
        error: '股票代码、数量和购买价格不能为空且必须为正数'
      });
    }
    
    const updatedPortfolio = await portfolioService.addHolding(portfolioId, stockCode, quantity, purchasePrice);
    
    return res.status(200).json({
      success: true,
      data: updatedPortfolio
    });
  } catch (error) {
    if (error.message === '投资组合不存在') {
      return res.status(404).json({
        success: false,
        error: error.message
      });
    }
    
    return res.status(500).json({
      success: false,
      error: error.message || '添加持仓失败'
    });
  }
});

/**
 * @route PUT /api/portfolios/holdings/:id
 * @description 更新持仓信息
 */
router.put('/portfolios/holdings/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const holdingId = parseInt(id, 10);
    const { quantity, purchasePrice } = req.body;
    
    if (isNaN(holdingId)) {
      return res.status(400).json({
        success: false,
        error: '无效的持仓ID'
      });
    }
    
    if (quantity <= 0) {
      return res.status(400).json({
        success: false,
        error: '数量必须为正数'
      });
    }
    
    const updatedPortfolio = await portfolioService.updateHolding(holdingId, quantity, purchasePrice);
    
    return res.status(200).json({
      success: true,
      data: updatedPortfolio
    });
  } catch (error) {
    if (error.message === '持仓不存在') {
      return res.status(404).json({
        success: false,
        error: error.message
      });
    }
    
    return res.status(500).json({
      success: false,
      error: error.message || '更新持仓失败'
    });
  }
});

/**
 * @route DELETE /api/portfolios/holdings/:id
 * @description 从投资组合中移除持仓
 */
router.delete('/portfolios/holdings/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const holdingId = parseInt(id, 10);
    
    if (isNaN(holdingId)) {
      return res.status(400).json({
        success: false,
        error: '无效的持仓ID'
      });
    }
    
    const updatedPortfolio = await portfolioService.removeHolding(holdingId);
    
    return res.status(200).json({
      success: true,
      data: updatedPortfolio
    });
  } catch (error) {
    if (error.message === '持仓不存在') {
      return res.status(404).json({
        success: false,
        error: error.message
      });
    }
    
    return res.status(500).json({
      success: false,
      error: error.message || '移除持仓失败'
    });
  }
});

/**
 * @route GET /api/portfolios/:id/allocation
 * @description 获取投资组合的资产配置
 */
router.get('/portfolios/:id/allocation', async (req, res) => {
  try {
    const { id } = req.params;
    const portfolioId = parseInt(id, 10);
    
    if (isNaN(portfolioId)) {
      return res.status(400).json({
        success: false,
        error: '无效的投资组合ID'
      });
    }
    
    const allocation = await portfolioService.getPortfolioAllocation(portfolioId);
    
    return res.status(200).json({
      success: true,
      data: allocation
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message || '获取资产配置失败'
    });
  }
});

export default router;