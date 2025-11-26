// 示例财务数据
// 可用于导入测试或手动添加

export const sampleStocks = [
  {
    symbol: 'SH600519',
    name: '贵州茅台',
    market: 'SH',
    industry: '白酒',
    sector: '消费品'
  },
  {
    symbol: 'SZ000858',
    name: '五粮液',
    market: 'SZ',
    industry: '白酒',
    sector: '消费品'
  },
  {
    symbol: 'SH601318',
    name: '中国平安',
    market: 'SH',
    industry: '保险',
    sector: '金融'
  }
];

export const sampleFinancialData = [
  // 贵州茅台财务数据
  {
    symbol: 'SH600519',
    fiscal_year: 2023,
    fiscal_quarter: 4,
    total_revenue: 124100000000, // 1241亿
    net_income: 62600000000,      // 626亿
    free_cash_flow: 58000000000,  // 580亿
    total_equity: 205000000000,   // 2050亿
    roe: 30.5                    // 30.5%
  },
  // 五粮液财务数据
  {
    symbol: 'SZ000858',
    fiscal_year: 2023,
    fiscal_quarter: 4,
    total_revenue: 73900000000,   // 739亿
    net_income: 27200000000,      // 272亿
    free_cash_flow: 25000000000,  // 250亿
    total_equity: 135000000000,   // 1350亿
    roe: 20.1                    // 20.1%
  },
  // 中国平安财务数据
  {
    symbol: 'SH601318',
    fiscal_year: 2023,
    fiscal_quarter: 4,
    total_revenue: 1160000000000, // 1.16万亿
    net_income: 105000000000,     // 1050亿
    free_cash_flow: 98000000000,  // 980亿
    total_equity: 980000000000,   // 9800亿
    roe: 10.7                    // 10.7%
  }
];

export const sampleQuotes = [
  {
    symbol: 'SH600519',
    current: 1850.00,
    open: 1840.00,
    close: 1845.00,
    high: 1860.00,
    low: 1830.00,
    volume: 5000000,
    quote_date: '2024-11-26'
  },
  {
    symbol: 'SZ000858',
    current: 180.00,
    open: 178.50,
    close: 179.20,
    high: 181.50,
    low: 177.80,
    volume: 25000000,
    quote_date: '2024-11-26'
  },
  {
    symbol: 'SH601318',
    current: 45.50,
    open: 45.20,
    close: 45.35,
    high: 45.80,
    low: 44.90,
    volume: 50000000,
    quote_date: '2024-11-26'
  }
];

// 使用方法说明
/*
// 导入示例数据的代码示例
import valuationService from '../services/valuationService.js';
import { sampleStocks, sampleFinancialData, sampleQuotes } from './sample_data.js';
import { getDB } from '../config/db.js';

async function importSampleData() {
  try {
    const db = await getDB();
    
    // 导入股票基本信息
    for (const stock of sampleStocks) {
      await db.run(
        `INSERT OR REPLACE INTO stock_basic_info 
         (symbol, name, market, industry, sector) 
         VALUES (?, ?, ?, ?, ?)`,
        [stock.symbol, stock.name, stock.market, stock.industry, stock.sector]
      );
    }
    console.log('导入股票基本信息完成');
    
    // 导入财务数据
    await valuationService.importFinancialData(sampleFinancialData);
    console.log('导入财务数据完成');
    
    // 导入行情数据
    for (const quote of sampleQuotes) {
      await db.run(
        `INSERT OR REPLACE INTO stock_quotes 
         (symbol, open, close, current, high, low, volume, quote_date) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        [quote.symbol, quote.open, quote.close, quote.current, 
         quote.high, quote.low, quote.volume, quote.quote_date]
      );
    }
    console.log('导入行情数据完成');
    
    return { success: true, message: '示例数据导入完成' };
  } catch (error) {
    console.error('导入示例数据失败:', error);
    throw error;
  }
}
*/