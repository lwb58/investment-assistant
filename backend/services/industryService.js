/**
 * 行业服务 - 处理行业分析相关业务逻辑
 */
class IndustryService {
  /**
   * 获取所有行业列表
   * @returns {Promise<Array>} 行业列表
   */
  async getIndustries() {
    // 模拟数据，实际应用中应从数据库或外部API获取
    return [
      { code: 'INDU001', name: '科技', fullName: '信息技术', level: 1 },
      { code: 'INDU002', name: '金融', fullName: '金融服务', level: 1 },
      { code: 'INDU003', name: '消费', fullName: '消费行业', level: 1 },
      { code: 'INDU004', name: '医药', fullName: '医药生物', level: 1 },
      { code: 'INDU005', name: '能源', fullName: '能源行业', level: 1 },
      { code: 'INDU006', name: '材料', fullName: '材料行业', level: 1 },
      { code: 'INDU007', name: '工业', fullName: '工业制造', level: 1 },
      { code: 'INDU008', name: '公用', fullName: '公用事业', level: 1 },
      { code: 'INDU009', name: '房地产', fullName: '房地产开发', level: 1 },
      { code: 'INDU010', name: '电信', fullName: '电信服务', level: 1 }
    ];
  }

  /**
   * 获取行业详情
   * @param {string} industryCode - 行业代码
   * @returns {Promise<Object>} 行业详情
   */
  async getIndustryDetail(industryCode) {
    // 模拟数据
    const industry = {
      code: industryCode,
      name: this.getIndustryNameByCode(industryCode),
      fullName: this.getIndustryFullNameByCode(industryCode),
      description: `这是${this.getIndustryNameByCode(industryCode)}行业的详细描述，包含行业概况、发展趋势等信息。`,
      statistics: {
        totalStocks: Math.floor(Math.random() * 100) + 50,
        marketCap: this.formatNumber(Math.random() * 10000000000000),
        avgPE: (Math.random() * 50 + 5).toFixed(2),
        avgPB: (Math.random() * 10 + 1).toFixed(2),
        avgROE: (Math.random() * 30 + 2).toFixed(2),
        avgGrowthRate: (Math.random() * 50 + 5).toFixed(2)
      },
      performance: {
        today: (Math.random() * 10 - 5).toFixed(2),
        week: (Math.random() * 20 - 10).toFixed(2),
        month: (Math.random() * 30 - 15).toFixed(2),
        quarter: (Math.random() * 50 - 25).toFixed(2),
        year: (Math.random() * 100 - 50).toFixed(2)
      }
    };
    
    return industry;
  }

  /**
   * 获取行业内股票列表
   * @param {string} industryCode - 行业代码
   * @param {number} page - 页码
   * @param {number} pageSize - 每页数量
   * @returns {Promise<Object>} 股票列表和分页信息
   */
  async getIndustryStocks(industryCode, page = 1, pageSize = 20) {
    // 模拟数据
    const total = 50; // 模拟总股票数
    const stocks = [];
    
    // 生成模拟股票数据
    for (let i = (page - 1) * pageSize; i < Math.min(page * pageSize, total); i++) {
      const basePrice = Math.random() * 50 + 10;
      const change = (Math.random() * 10 - 5).toFixed(2);
      const changeRate = (Math.random() * 10 - 5).toFixed(2);
      
      stocks.push({
        code: `STOCK${industryCode}${i + 1}`,
        name: `${this.getIndustryNameByCode(industryCode)}股票${i + 1}`,
        price: (basePrice).toFixed(2),
        change: change,
        changeRate: changeRate,
        pe: (Math.random() * 40 + 5).toFixed(2),
        pb: (Math.random() * 8 + 1).toFixed(2),
        marketCap: this.formatNumber(Math.random() * 500000000000)
      });
    }
    
    return {
      list: stocks,
      pagination: {
        page,
        pageSize,
        total,
        totalPages: Math.ceil(total / pageSize)
      }
    };
  }

  /**
   * 比较多个行业
   * @param {Array<string>} industryCodes - 行业代码数组
   * @returns {Promise<Object>} 对比结果
   */
  async compareIndustries(industryCodes) {
    const result = {
      industries: [],
      comparison: {
        valuation: [],
        performance: [],
        growth: []
      }
    };
    
    // 获取每个行业的数据
    for (const code of industryCodes) {
      const industryDetail = await this.getIndustryDetail(code);
      
      result.industries.push(industryDetail);
      
      // 添加估值对比数据
      result.comparison.valuation.push({
        code: code,
        name: industryDetail.name,
        pe: parseFloat(industryDetail.statistics.avgPE),
        pb: parseFloat(industryDetail.statistics.avgPB),
        roe: parseFloat(industryDetail.statistics.avgROE)
      });
      
      // 添加表现对比数据
      result.comparison.performance.push({
        code: code,
        name: industryDetail.name,
        month: parseFloat(industryDetail.performance.month),
        quarter: parseFloat(industryDetail.performance.quarter),
        year: parseFloat(industryDetail.performance.year)
      });
      
      // 添加增长对比数据
      result.comparison.growth.push({
        code: code,
        name: industryDetail.name,
        growthRate: parseFloat(industryDetail.statistics.avgGrowthRate),
        marketCap: industryDetail.statistics.marketCap
      });
    }
    
    return result;
  }

  /**
   * 获取行业趋势数据
   * @param {string} industryCode - 行业代码
   * @param {string} period - 时间周期
   * @returns {Promise<Object>} 趋势数据
   */
  async getIndustryTrend(industryCode, period = '1y') {
    const dataPoints = this.getPeriodDataPoints(period);
    const trendData = [];
    
    // 生成模拟趋势数据
    let baseValue = Math.random() * 1000 + 500;
    for (let i = 0; i < dataPoints; i++) {
      // 生成有趋势性的随机波动
      const trend = i / dataPoints * 20 - 10; // -10% 到 +10% 的总趋势
      const volatility = (Math.random() * 10 - 5) / 100; // -5% 到 +5% 的随机波动
      
      baseValue = baseValue * (1 + trend / dataPoints + volatility);
      
      const date = this.getDateByIndex(period, i, dataPoints);
      
      trendData.push({
        date,
        value: baseValue.toFixed(2),
        change: (baseValue * volatility * 100).toFixed(2)
      });
    }
    
    return {
      code: industryCode,
      name: this.getIndustryNameByCode(industryCode),
      period,
      data: trendData
    };
  }

  /**
   * 获取行业估值排名
   * @param {string} metric - 估值指标 (pe, pb, roe等)
   * @param {string} order - 排序方向 (asc, desc)
   * @returns {Promise<Array>} 排名列表
   */
  async getIndustryValuationRanking(metric = 'pe', order = 'asc') {
    const industries = await this.getIndustries();
    const ranking = [];
    
    // 为每个行业生成估值数据
    for (const industry of industries) {
      let value;
      
      switch (metric) {
        case 'pe':
          value = (Math.random() * 50 + 5).toFixed(2);
          break;
        case 'pb':
          value = (Math.random() * 10 + 1).toFixed(2);
          break;
        case 'roe':
          value = (Math.random() * 30 + 2).toFixed(2);
          break;
        case 'ps':
          value = (Math.random() * 20 + 1).toFixed(2);
          break;
        case 'pcf':
          value = (Math.random() * 40 + 5).toFixed(2);
          break;
        default:
          value = (Math.random() * 50 + 5).toFixed(2);
      }
      
      ranking.push({
        code: industry.code,
        name: industry.name,
        value: parseFloat(value),
        change: (Math.random() * 10 - 5).toFixed(2),
        percentiles: {
          historical: Math.floor(Math.random() * 100),
          peer: Math.floor(Math.random() * 100)
        }
      });
    }
    
    // 排序
    ranking.sort((a, b) => {
      if (order === 'asc') {
        return a.value - b.value;
      } else {
        return b.value - a.value;
      }
    });
    
    // 添加排名
    ranking.forEach((item, index) => {
      item.rank = index + 1;
    });
    
    return ranking;
  }

  // 辅助方法
  getIndustryNameByCode(code) {
    const industryMap = {
      'INDU001': '科技',
      'INDU002': '金融',
      'INDU003': '消费',
      'INDU004': '医药',
      'INDU005': '能源',
      'INDU006': '材料',
      'INDU007': '工业',
      'INDU008': '公用',
      'INDU009': '房地产',
      'INDU010': '电信'
    };
    return industryMap[code] || '未知行业';
  }

  getIndustryFullNameByCode(code) {
    const industryMap = {
      'INDU001': '信息技术',
      'INDU002': '金融服务',
      'INDU003': '消费行业',
      'INDU004': '医药生物',
      'INDU005': '能源行业',
      'INDU006': '材料行业',
      'INDU007': '工业制造',
      'INDU008': '公用事业',
      'INDU009': '房地产开发',
      'INDU010': '电信服务'
    };
    return industryMap[code] || '未知行业';
  }

  formatNumber(num) {
    if (num >= 1e12) {
      return (num / 1e12).toFixed(2) + '万亿';
    } else if (num >= 1e8) {
      return (num / 1e8).toFixed(2) + '亿';
    } else if (num >= 1e4) {
      return (num / 1e4).toFixed(2) + '万';
    }
    return num.toFixed(2);
  }

  getPeriodDataPoints(period) {
    switch (period) {
      case '1d':
        return 24;
      case '1w':
        return 7;
      case '1m':
        return 30;
      case '3m':
        return 90;
      case '6m':
        return 180;
      case '1y':
        return 365;
      case '3y':
        return 3 * 365;
      case '5y':
        return 5 * 365;
      default:
        return 365;
    }
  }

  getDateByIndex(period, index, total) {
    const now = new Date();
    let date;
    
    switch (period) {
      case '1d':
        date = new Date(now.getTime() - (total - index - 1) * 60 * 60 * 1000);
        break;
      case '1w':
        date = new Date(now.getTime() - (total - index - 1) * 24 * 60 * 60 * 1000);
        break;
      case '1m':
        date = new Date(now.getTime() - (total - index - 1) * 24 * 60 * 60 * 1000);
        break;
      case '3m':
        date = new Date(now.getTime() - (total - index - 1) * 24 * 60 * 60 * 1000);
        break;
      case '6m':
        date = new Date(now.getFullYear(), now.getMonth() - Math.floor((total - index - 1) / 30), (total - index - 1) % 30);
        break;
      case '1y':
        date = new Date(now.getFullYear(), now.getMonth() - Math.floor((total - index - 1) / 30), (total - index - 1) % 30);
        break;
      case '3y':
      case '5y':
        date = new Date(now.getFullYear() - Math.floor((total - index - 1) / 365), now.getMonth(), now.getDate());
        break;
      default:
        date = new Date(now.getTime() - (total - index - 1) * 24 * 60 * 60 * 1000);
    }
    
    return date.toISOString().split('T')[0];
  }
}

module.exports = new IndustryService();