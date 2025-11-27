import axios from 'axios';

/**
 * 证券宝(BaoStock) API封装类
 * 注意：由于BaoStock主要提供Python API，此实现使用其HTTP接口或替代方案
 */
class BaostockApi {
  constructor() {
    this.client = axios.create({
      baseURL: 'http://api.baostock.com/v1', // 假设的API基础URL
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    this.setupInterceptors();
    this.sessionStarted = false;
  }

  /**
   * 设置请求和响应拦截器
   */
  setupInterceptors() {
    // 请求拦截器
    this.client.interceptors.request.use(
      async (config) => {
        // 如果会话未开始，先初始化会话
        if (!this.sessionStarted) {
          await this.login();
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        // 指数退避重试策略
        if (!originalRequest._retry) {
          originalRequest._retry = true;
          originalRequest._retryCount = originalRequest._retryCount || 0;
          
          if (originalRequest._retryCount < 3) {
            originalRequest._retryCount++;
            const delay = Math.pow(2, originalRequest._retryCount) * 1000;
            
            await new Promise(resolve => setTimeout(resolve, delay));
            return this.client(originalRequest);
          }
        }
        
        // 如果是会话过期，尝试重新登录
        if (error.response && error.response.status === 401) {
          this.sessionStarted = false;
          await this.login();
          return this.client(originalRequest);
        }
        
        return Promise.reject(error);
      }
    );
  }

  /**
   * 登录/初始化会话
   */
  async login() {
    try {
      // BaoStock无需注册，使用默认登录
      // 这里模拟登录过程，实际实现需要根据BaoStock的HTTP API规范
      this.sessionStarted = true;
      console.log('BaoStock API session initialized');
      return { success: true };
    } catch (error) {
      console.error('BaoStock login failed:', error);
      throw new Error('Failed to initialize BaoStock session');
    }
  }

  /**
   * 获取所有股票列表
   */
  async getAllStocks() {
    try {
      console.log('Fetching all stocks from BaoStock');
      
      // 创建Python脚本调用BaoStock API获取所有股票列表
      const pythonScript = `
import baostock as bs
import json

# 登录系统
lg = bs.login()
if lg.error_code != '0':
    print(json.dumps({"error": lg.error_msg}))
    exit(1)

# 获取股票列表
rs = bs.query_all_stock()
stocks_data = []
if rs.error_code == '0':
    while (rs.error_code == '0') & rs.next():
        stock = rs.get_row_data()
        stocks_data.append({
            "code": stock[0],  # 股票代码
            "tradeStatus": stock[1],  # 交易状态
            "code_name": stock[2]  # 股票名称
        })

# 登出系统
bs.logout()

# 转换为标准格式
result = []
for stock in stocks_data:
    # 转换代码格式为SZ/SH
    code = stock['code']
    if code.startswith('sh.'):
        symbol = code.replace('sh.', '') + '.SH'
    elif code.startswith('sz.'):
        symbol = code.replace('sz.', '') + '.SZ'
    else:
        symbol = code
    
    result.append({
        "symbol": symbol,
        "name": stock['code_name'],
        "code": code.split('.')[1] if '.' in code else code,
        "exchange": 'SH' if symbol.endswith('.SH') else 'SZ'
    })

print(json.dumps(result, ensure_ascii=False))
      `;
      
      const result = await this.executePythonScript(pythonScript);
      const stocks = JSON.parse(result);
      
      return stocks;
    } catch (error) {
      console.error('Failed to get all stocks from BaoStock:', error);
      throw error;
    }
  }

  /**
   * 获取历史K线数据
   * @param {string} code - 股票代码
   * @param {string} startDate - 开始日期，格式：YYYY-MM-DD
   * @param {string} endDate - 结束日期，格式：YYYY-MM-DD
   * @param {string} frequency - 数据类型，默认为d日线
   */
  async getHistoricalKData(code, startDate, endDate, frequency = 'd') {
    try {
      console.log(`Fetching historical K data for ${code} from ${startDate} to ${endDate}`);
      
      // 转换代码格式为BaoStock所需的格式
      let bsCode = code;
      if (code.includes('.SH')) {
        bsCode = 'sh.' + code.replace('.SH', '');
      } else if (code.includes('.SZ')) {
        bsCode = 'sz.' + code.replace('.SZ', '');
      }
      
      // 映射周期参数
      const frequencyMap = {
        'd': 'd',    // 日线
        'w': 'w',    // 周线
        'm': 'm',    // 月线
        '5': '5',    // 5分钟线
        '15': '15',  // 15分钟线
        '30': '30',  // 30分钟线
        '60': '60'   // 60分钟线
      };
      
      const bsFrequency = frequencyMap[frequency] || 'd';
      
      // 创建Python脚本调用BaoStock API获取K线数据
      const pythonScript = `
import baostock as bs
import json

# 登录系统
lg = bs.login()
if lg.error_code != '0':
    print(json.dumps({"error": lg.error_msg}))
    exit(1)

# 获取K线数据
rs = bs.query_history_k_data_plus(
    '${bsCode}',
    'date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST',
    start_date='${startDate}',
    end_date='${endDate}',
    frequency='${bsFrequency}',
    adjustflag='3'  # 3: 前复权
)

k_data = []
if rs.error_code == '0':
    while (rs.error_code == '0') & rs.next():
        row = rs.get_row_data()
        k_data.append({
            "date": row[0],
            "code": row[1],
            "open": float(row[2]) if row[2] else 0,
            "high": float(row[3]) if row[3] else 0,
            "low": float(row[4]) if row[4] else 0,
            "close": float(row[5]) if row[5] else 0,
            "preclose": float(row[6]) if row[6] else 0,
            "volume": float(row[7]) if row[7] else 0,
            "amount": float(row[8]) if row[8] else 0,
            "adjustflag": row[9],
            "turn": float(row[10]) if row[10] else 0,
            "tradestatus": row[11],
            "pctChg": float(row[12]) if row[12] else 0,
            "isST": row[13]
        })

# 登出系统
bs.logout()

# 转换为标准格式并返回
print(json.dumps(k_data))
      `;
      
      const result = await this.executePythonScript(pythonScript);
      const kData = JSON.parse(result);
      
      // 转换回原始股票代码格式
      return kData.map(item => ({
        ...item,
        symbol: code
      }));
    } catch (error) {
      console.error(`Failed to get historical K data for ${code}:`, error);
      throw error;
    }
  }

  /**
   * 获取股票基本信息
   * @param {string} code - 股票代码
   */
  async getStockBasicInfo(code) {
    try {
      console.log(`Fetching basic info for ${code}`);
      
      // 转换代码格式为BaoStock所需的格式
      let bsCode = code;
      if (code.includes('.SH')) {
        bsCode = 'sh.' + code.replace('.SH', '');
      } else if (code.includes('.SZ')) {
        bsCode = 'sz.' + code.replace('.SZ', '');
      }
      
      // 创建Python脚本调用BaoStock API获取基本信息
      const pythonScript = `
import baostock as bs
import json

# 登录系统
lg = bs.login()
if lg.error_code != '0':
    print(json.dumps({"error": lg.error_msg}))
    exit(1)

# 获取股票基本信息
rs = bs.query_stock_basic(code='${bsCode}', fields='code,code_name,ipoDate,outDate,type,status')

basic_info = None
if rs.error_code == '0' and rs.next():
    row = rs.get_row_data()
    basic_info = {
        "code": row[0],
        "code_name": row[1],
        "ipoDate": row[2],
        "outDate": row[3],
        "type": row[4],
        "status": row[5]
    }

# 获取行业信息
industry_info = None
rs_industry = bs.query_stock_industry(code='${bsCode}')
if rs_industry.error_code == '0' and rs_industry.next():
    row = rs_industry.get_row_data()
    industry_info = {
        "industry": row[2],  # 行业名称
        "industryClassification": row[1]  # 行业分类
    }

# 登出系统
bs.logout()

# 合并信息并返回
result = {}
if basic_info:
    result.update({
        "symbol": '${code}',
        "name": basic_info['code_name'],
        "code": basic_info['code'].split('.')[1] if '.' in basic_info['code'] else basic_info['code'],
        "exchange": 'SH' if '${code}'.endswith('.SH') else 'SZ',
        "ipoDate": basic_info['ipoDate'],
        "outDate": basic_info['outDate'],
        "type": basic_info['type'],
        "status": basic_info['status']
    })

if industry_info:
    result.update({
        "industry": industry_info['industry'],
        "industryClassification": industry_info['industryClassification']
    })

print(json.dumps(result))
      `;
      
      const result = await this.executePythonScript(pythonScript);
      return JSON.parse(result);
    } catch (error) {
      console.error(`Failed to get basic info for ${code}:`, error);
      throw error;
    }
  }

  /**
   * 获取行业分类
   */
  async getIndustryClassification() {
    try {
      console.log('Fetching industry classification');
      
      // 创建Python脚本调用BaoStock API获取行业分类
      const pythonScript = `
import baostock as bs
import json
from collections import defaultdict

# 登录系统
lg = bs.login()
if lg.error_code != '0':
    print(json.dumps({"error": lg.error_msg}))
    exit(1)

# 获取所有股票代码
rs_stocks = bs.query_all_stock()
stocks = []
if rs_stocks.error_code == '0':
    while (rs_stocks.error_code == '0') & rs_stocks.next():
        stocks.append(rs_stocks.get_row_data()[0])

# 获取每个股票的行业信息
industry_map = defaultdict(list)
for stock_code in stocks[:100]:  # 限制获取前100个股票，避免请求过多
    rs_industry = bs.query_stock_industry(code=stock_code)
    if rs_industry.error_code == '0' and rs_industry.next():
        row = rs_industry.get_row_data()
        industry = row[2]
        
        # 转换代码格式
        if stock_code.startswith('sh.'):
            symbol = stock_code.replace('sh.', '') + '.SH'
        elif stock_code.startswith('sz.'):
            symbol = stock_code.replace('sz.', '') + '.SZ'
        else:
            symbol = stock_code
        
        industry_map[industry].append(symbol)

# 登出系统
bs.logout()

# 转换为标准格式
result = []
for industry_name, stock_list in industry_map.items():
    if industry_name and stock_list:
        result.append({
            "industry": industry_name,
            "stocks": stock_list,
            "count": len(stock_list)
        })

print(json.dumps(result, ensure_ascii=False))
      `;
      
      const result = await this.executePythonScript(pythonScript);
      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get industry classification:', error);
      throw error;
    }
  }

  /**
   * 获取上证50成分股
   */
  async getSZ50Stocks() {
    try {
      console.log('Fetching SZ50 component stocks');
      
      // 实际实现应调用BaoStock的query_sz50_stocks接口
      throw new Error('BaoStock API requires Python integration, implementation pending');
    } catch (error) {
      console.error('Failed to get SZ50 stocks:', error);
      throw error;
    }
  }

  /**
   * 获取沪深300成分股
   */
  async getHS300Stocks() {
    try {
      console.log('Fetching HS300 component stocks');
      
      // 实际实现应调用BaoStock的query_hs300_stocks接口
      throw new Error('BaoStock API requires Python integration, implementation pending');
    } catch (error) {
      console.error('Failed to get HS300 stocks:', error);
      throw error;
    }
  }

  /**
   * 获取中证500成分股
   */
  async getZZ500Stocks() {
    try {
      console.log('Fetching ZZ500 component stocks');
      
      // 实际实现应调用BaoStock的query_zz500_stocks接口
      throw new Error('BaoStock API requires Python integration, implementation pending');
    } catch (error) {
      console.error('Failed to get ZZ500 stocks:', error);
      throw error;
    }
  }

  /**
   * 获取财务数据
   * @param {string} code - 股票代码
   * @param {string} year - 年份
   * @param {string} quarter - 季度
   */
  async getFinancialData(code, year, quarter) {
    try {
      console.log(`Fetching financial data for ${code} ${year} Q${quarter}`);
      
      // 转换代码格式为BaoStock所需的格式
      let bsCode = code;
      if (code.includes('.SH')) {
        bsCode = 'sh.' + code.replace('.SH', '');
      } else if (code.includes('.SZ')) {
        bsCode = 'sz.' + code.replace('.SZ', '');
      }
      
      // 创建Python脚本调用BaoStock API获取财务数据
      const pythonScript = `
import baostock as bs
import json

# 登录系统
lg = bs.login()
if lg.error_code != '0':
    print(json.dumps({"error": lg.error_msg}))
    exit(1)

# 获取利润表数据
rs_profit = bs.query_profit_data(
    code='${bsCode}',
    year=${year},
    quarter=${quarter}
)

profit_data = None
if rs_profit.error_code == '0' and rs_profit.next():
    row = rs_profit.get_row_data()
    profit_data = {
        "code": row[0],
        "pubDate": row[1],
        "statDate": row[2],
        "roeAvg": float(row[3]) if row[3] else 0,
        "netProfit": float(row[4]) if row[4] else 0,
        "epsTTM": float(row[5]) if row[5] else 0,
        "mbRevenue": float(row[6]) if row[6] else 0,
        "totalShare": float(row[7]) if row[7] else 0
    }

# 获取资产负债表数据
rs_balance = bs.query_balance_data(
    code='${bsCode}',
    year=${year},
    quarter=${quarter}
)

balance_data = None
if rs_balance.error_code == '0' and rs_balance.next():
    row = rs_balance.get_row_data()
    balance_data = {
        "totalAssets": float(row[2]) if row[2] else 0,
        "totalLiability": float(row[3]) if row[3] else 0,
        "totalShareHolderEquity": float(row[4]) if row[4] else 0,
        "liquidAssets": float(row[5]) if row[5] else 0,
        "fixedAssets": float(row[6]) if row[6] else 0
    }

# 获取现金流量表数据
rs_cashflow = bs.query_cash_flow_data(
    code='${bsCode}',
    year=${year},
    quarter=${quarter}
)

cashflow_data = None
if rs_cashflow.error_code == '0' and rs_cashflow.next():
    row = rs_cashflow.get_row_data()
    cashflow_data = {
        "netOperateCashFlow": float(row[2]) if row[2] else 0,
        "netInvestCashFlow": float(row[3]) if row[3] else 0,
        "netFinanCashFlow": float(row[4]) if row[4] else 0,
        "freeCashFlow": float(row[5]) if row[5] else 0
    }

# 登出系统
bs.logout()

# 合并数据
result = {"symbol": '${code}', "year": ${year}, "quarter": ${quarter}}
if profit_data:
    result.update(profit_data)
if balance_data:
    result.update(balance_data)
if cashflow_data:
    result.update(cashflow_data)

print(json.dumps(result))
      `;
      
      const result = await this.executePythonScript(pythonScript);
      return JSON.parse(result);
    } catch (error) {
      console.error(`Failed to get financial data for ${code}:`, error);
      throw error;
    }
  }

  /**
   * 登出/结束会话
   */
  async logout() {
    try {
      // 实际实现应调用BaoStock的logout接口
      this.sessionStarted = false;
      console.log('BaoStock session closed');
      return { success: true };
    } catch (error) {
      console.error('BaoStock logout failed:', error);
      throw error;
    }
  }

  /**
   * 创建Python子进程执行BaoStock脚本
   * @param {string} script - Python脚本内容
   */
  async executePythonScript(script) {
    const { exec } = require('child_process');
    
    // 处理脚本字符串，确保在Windows PowerShell中正确执行
    // 将引号转义，处理换行符
    const escapedScript = script
      .replace(/"/g, '\"')  // 转义双引号
      .replace(/\n/g, ' `n '); // 替换换行符为PowerShell的换行标记
    
    return new Promise((resolve, reject) => {
      // 在Windows环境中使用PowerShell执行Python
      const command = `powershell -Command "python -c \"${escapedScript}\""`;
      
      console.log('Executing Python script for BaoStock API...');
      
      exec(command, { timeout: 30000 }, (error, stdout, stderr) => {
        if (error) {
          // 检查是否是BaoStock未安装的错误
          if (stderr && stderr.includes('ModuleNotFoundError')) {
            console.error('BaoStock Python module not found. Please install it with: pip install baostock');
          }
          reject(new Error(`Python execution error: ${stderr || error.message}`));
          return;
        }
        
        // 清理输出，移除任何PowerShell额外的输出
        const cleanOutput = stdout.trim();
        resolve(cleanOutput);
      });
    });
  }
}

export default new BaostockApi();
