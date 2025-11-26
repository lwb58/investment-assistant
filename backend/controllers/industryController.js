const IndustryService = require('../services/industryService');

/**
 * 行业分析控制器
 */
const industryController = {
  /**
   * 获取所有行业列表
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async getIndustries(req, res) {
    try {
      const industries = await IndustryService.getIndustries();
      
      res.json({
        success: true,
        data: industries
      });
    } catch (error) {
      console.error('获取行业列表失败:', error);
      res.status(500).json({
        success: false,
        error: '获取行业列表失败，请稍后重试'
      });
    }
  },

  /**
   * 获取行业详情
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async getIndustryDetail(req, res) {
    try {
      const { industryCode } = req.params;
      const industryDetail = await IndustryService.getIndustryDetail(industryCode);
      
      if (!industryDetail) {
        return res.status(404).json({
          success: false,
          error: '行业不存在'
        });
      }
      
      res.json({
        success: true,
        data: industryDetail
      });
    } catch (error) {
      console.error('获取行业详情失败:', error);
      res.status(500).json({
        success: false,
        error: '获取行业详情失败，请稍后重试'
      });
    }
  },

  /**
   * 获取行业内股票列表
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async getIndustryStocks(req, res) {
    try {
      const { industryCode } = req.params;
      const { page = 1, pageSize = 20 } = req.query;
      
      const stocks = await IndustryService.getIndustryStocks(industryCode, parseInt(page), parseInt(pageSize));
      
      res.json({
        success: true,
        data: stocks
      });
    } catch (error) {
      console.error('获取行业股票列表失败:', error);
      res.status(500).json({
        success: false,
        error: '获取行业股票列表失败，请稍后重试'
      });
    }
  },

  /**
   * 比较多个行业
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async compareIndustries(req, res) {
    try {
      const { industryCodes } = req.query;
      
      if (!industryCodes || typeof industryCodes !== 'string') {
        return res.status(400).json({
          success: false,
          error: '请提供要比较的行业代码，格式为: industryCodes=code1,code2,code3'
        });
      }
      
      const codes = industryCodes.split(',').map(code => code.trim());
      const comparisonResult = await IndustryService.compareIndustries(codes);
      
      res.json({
        success: true,
        data: comparisonResult
      });
    } catch (error) {
      console.error('行业对比失败:', error);
      res.status(500).json({
        success: false,
        error: '行业对比失败，请稍后重试'
      });
    }
  },

  /**
   * 获取行业趋势数据
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async getIndustryTrend(req, res) {
    try {
      const { industryCode } = req.params;
      const { period = '1y' } = req.query;
      
      const trendData = await IndustryService.getIndustryTrend(industryCode, period);
      
      res.json({
        success: true,
        data: trendData
      });
    } catch (error) {
      console.error('获取行业趋势失败:', error);
      res.status(500).json({
        success: false,
        error: '获取行业趋势失败，请稍后重试'
      });
    }
  },

  /**
   * 获取行业估值排名
   * @param {Object} req - Express请求对象
   * @param {Object} res - Express响应对象
   */
  async getIndustryValuationRanking(req, res) {
    try {
      const { metric = 'pe', order = 'asc' } = req.query;
      
      const ranking = await IndustryService.getIndustryValuationRanking(metric, order);
      
      res.json({
        success: true,
        data: ranking
      });
    } catch (error) {
      console.error('获取行业估值排名失败:', error);
      res.status(500).json({
        success: false,
        error: '获取行业估值排名失败，请稍后重试'
      });
    }
  }
};

module.exports = industryController;