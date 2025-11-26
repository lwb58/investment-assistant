import express from 'express';
import stockDataService from '../services/stockDataService.js';

const router = express.Router();

/**
 * 获取大盘指数数据
 * GET /api/stock/market-index
 */
router.get('/market-index', async (req, res) => {
  try {
    const marketData = await stockDataService.getMarketIndex();
    res.json({
      success: true,
      data: marketData
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: '获取大盘数据失败',
      details: error.message
    });
  }
});

/**
 * 搜索股票
 * GET /api/stock/search?keyword=xxx
 */
router.get('/search', async (req, res) => {
  try {
    const { keyword } = req.query;
    
    if (!keyword || keyword.trim() === '') {
      return res.status(400).json({
        success: false,
        error: '搜索关键词不能为空'
      });
    }
    
    const stocks = await stockDataService.searchStocks(keyword);
    res.json({
      success: true,
      data: stocks,
      total: stocks.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: '搜索股票失败',
      details: error.message
    });
  }
});

/**
 * 获取股票详情数据
 * GET /api/stock/detail/:symbol
 */
router.get('/detail/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    
    if (!symbol) {
      return res.status(400).json({
        success: false,
        error: '股票代码不能为空'
      });
    }
    
    const stockDetail = await stockDataService.getStockDetail(symbol);
    res.json({
      success: true,
      data: stockDetail
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: '获取股票详情数据失败',
      details: error.message
    });
  }
});

/**
 * 获取个股数据
 * GET /api/stock/:symbol
 */
router.get('/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    
    if (!symbol) {
      return res.status(400).json({
        success: false,
        error: '股票代码不能为空'
      });
    }
    
    const stockData = await stockDataService.getStockData(symbol);
    res.json({
      success: true,
      data: stockData
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: '获取股票数据失败',
      details: error.message
    });
  }
});

/**
 * 获取行业数据
 * GET /api/stock/industry/list
 */
router.get('/industry/list', async (req, res) => {
  try {
    const industryData = await stockDataService.getIndustryData();
    res.json({
      success: true,
      data: industryData
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: '获取行业数据失败',
      details: error.message
    });
  }
});

/**
 * 获取股票财务数据
 * GET /api/stock/:symbol/financial
 */
router.get('/:symbol/financial', async (req, res) => {
  try {
    const { symbol } = req.params;
    
    if (!symbol) {
      return res.status(400).json({
        success: false,
        error: '股票代码不能为空'
      });
    }
    
    const financialData = await stockDataService.getFinancialData(symbol);
    res.json({
      success: true,
      data: financialData
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: '获取财务数据失败',
      details: error.message
    });
  }
});

export default router;
