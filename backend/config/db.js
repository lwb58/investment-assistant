import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// 数据库文件路径
const DB_PATH = './database/investment_assistant.db';

// SQLite连接池管理
let db = null;

/**
 * 获取数据库连接
 * @returns {Promise<Object>} 数据库连接实例
 */
export async function getDB() {
  if (!db) {
    db = await open({
      filename: DB_PATH,
      driver: sqlite3.Database,
      mode: sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE,
    });
    
    // 自动初始化数据库表
    await initializeDatabase(db);
  }
  return db;
}

/**
 * 初始化数据库表结构
 * @param {Object} db - 数据库连接实例
 */
async function initializeDatabase(db) {
  try {
    // 创建股票基本信息表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS stock_basic_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL UNIQUE,
        name TEXT,
        market TEXT,
        industry TEXT,
        sector TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);
    
    // 创建股票行情数据表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS stock_quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        open REAL DEFAULT 0,
        close REAL DEFAULT 0,
        current REAL DEFAULT 0,
        high REAL DEFAULT 0,
        low REAL DEFAULT 0,
        volume INTEGER DEFAULT 0,
        amount REAL DEFAULT 0,
        quote_date DATE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(symbol, quote_date)
      );
    `);
    
    // 创建财务数据表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS company_financial_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        fiscal_year INTEGER,
        fiscal_quarter INTEGER,
        total_revenue REAL DEFAULT 0,
        net_income REAL DEFAULT 0,
        free_cash_flow REAL DEFAULT 0,
        total_equity REAL DEFAULT 0,
        roe REAL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(symbol, fiscal_year, fiscal_quarter)
      );
    `);
    
    // 创建估值结果表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS valuation_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        valuation_date DATE NOT NULL,
        dcf_value REAL DEFAULT 0,
        fcf_growth_rate REAL DEFAULT 0,
        discount_rate REAL DEFAULT 0,
        intrinsic_value REAL DEFAULT 0,
        margin_of_safety REAL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);
    
    // 创建投资建议表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS investment_advice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_code TEXT NOT NULL,
        total_score INTEGER,
        action TEXT,
        confidence TEXT,
        rationale TEXT,
        risk_level TEXT,
        holding_period TEXT,
        valuation_score INTEGER,
        growth_score INTEGER,
        financial_health_score INTEGER,
        market_sentiment_score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    
    // 创建投资组合表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS portfolios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    
    // 创建投资组合持仓表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS portfolio_holdings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        portfolio_id INTEGER NOT NULL,
        stock_code TEXT NOT NULL,
        quantity REAL NOT NULL,
        avg_price REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
        UNIQUE(portfolio_id, stock_code)
      );
    `);
    
    console.log('数据库初始化完成');
  } catch (error) {
    console.error('数据库初始化失败:', error);
    throw error;
  }
}

/**
 * 关闭数据库连接
 */
export async function closeDB() {
  if (db) {
    await db.close();
    db = null;
    console.log('数据库连接已关闭');
  }
}