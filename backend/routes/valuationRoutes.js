import express from 'express';
import valuationService from '../services/valuationService.js';
import investmentService from '../services/investmentService.js';

const router = express.Router();

/**
 * 计算股票估值
 * POST /api/valuation/calculate
 */
router.post('/calculate', async (req, res) => {
  try {
    const { symbol, params } = req.body;
    
    if (!symbol) {
      return res.status(400).json({ error: '股票代码不能为空' });
    }

    const result = await valuationService.calculateValuation(symbol, params);
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 添加财务数据
 * POST /api/valuation/financial-data
 */
router.post('/financial-data', async (req, res) => {
  try {
    const financialData = req.body;
    
    if (!financialData.symbol || !financialData.fiscal_year) {
      return res.status(400).json({ error: '股票代码和财年不能为空' });
    }

    const result = await valuationService.addFinancialData(financialData);
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 获取估值历史
 * GET /api/valuation/history/:symbol
 */
router.get('/history/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const history = await valuationService.getValuationHistory(symbol);
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 获取股票基本信息
 * GET /api/valuation/stock/:symbol
 */
router.get('/stock/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const db = await valuationService.db;
    
    // 获取股票信息
    const stockInfo = await db.get('SELECT * FROM stock_basic_info WHERE symbol = ?', [symbol]);
    
    // 获取最新财务数据
    const financialData = await valuationService.getLatestFinancialData(symbol);
    
    // 获取最新价格
    const latestPrice = await valuationService.getLatestPrice(symbol);
    
    res.json({
      success: true,
      data: {
        stockInfo,
        financialData,
        latestPrice
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 保存股票基本信息
 * POST /api/valuation/stock
 */
router.post('/stock', async (req, res) => {
  try {
    const { symbol, name, market, industry, sector } = req.body;
    
    if (!symbol || !name) {
      return res.status(400).json({ error: '股票代码和名称不能为空' });
    }

    const db = await valuationService.db;
    await db.run(
      `INSERT OR REPLACE INTO stock_basic_info 
       (symbol, name, market, industry, sector) 
       VALUES (?, ?, ?, ?, ?)`,
      [symbol, name, market || '', industry || '', sector || '']
    );
    
    res.json({
      success: true,
      message: '股票信息已保存'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 获取所有股票列表
 * GET /api/valuation/stocks
 */
router.get('/stocks', async (req, res) => {
  try {
    const db = await valuationService.db;
    const stocks = await db.all('SELECT * FROM stock_basic_info ORDER BY symbol');
    
    res.json({
      success: true,
      data: stocks
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 生成投资建议
 * POST /api/valuation/investment-advice
 */
router.post('/investment-advice', async (req, res) => {
  try {
    const { symbol, valuationResult } = req.body;
    if (!symbol) {
      return res.status(400).json({ error: '股票代码不能为空' });
    }
    const advice = await investmentService.generateInvestmentAdvice(symbol, valuationResult);
    res.json({
      success: true,
      data: advice
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 获取股票投资建议历史
 * GET /api/valuation/investment-advice/:symbol
 */
router.get('/investment-advice/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const { limit = 10 } = req.query;
    const history = await investmentService.getHistoricalAdvice(symbol, parseInt(limit));
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 批量获取投资建议
 * POST /api/valuation/investment-advice/batch
 */
router.post('/investment-advice/batch', async (req, res) => {
  try {
    const { symbols } = req.body;
    if (!Array.isArray(symbols)) {
      return res.status(400).json({ error: 'symbols必须是数组' });
    }
    const adviceBatch = await investmentService.getBatchAdvice(symbols);
    res.json({
      success: true,
      data: adviceBatch
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 获取估值指标数据
 * GET /api/valuation/valuation/:symbol
 */
router.get('/valuation/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    if (!symbol) {
      return res.status(400).json({ success: false, error: '股票代码不能为空' });
    }
    const result = await valuationService.getValuationData(symbol);
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 获取基本面数据
 * GET /api/valuation/fundamental/:symbol
 */
router.get('/fundamental/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    if (!symbol) {
      return res.status(400).json({ success: false, error: '股票代码不能为空' });
    }
    const result = await valuationService.getFundamentalData(symbol);
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * 获取事件数据
 * GET /api/valuation/events/:symbol
 */
router.get('/events/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    if (!symbol) {
      return res.status(400).json({ success: false, error: '股票代码不能为空' });
    }
    const result = await valuationService.getEventsData(symbol);
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

export default router;