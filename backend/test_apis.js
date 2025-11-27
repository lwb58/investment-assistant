// 测试所有API文件的功能
import { tushareApi, eastmoneyApi, sinacnApi, baostockApi, dtshareApi } from './apis/stockApi.js';

// 测试配置
const config = {
  testStockCode: '000001.SZ', // 平安银行
  testIndexCode: '000001.SH', // 上证指数
  maxRetries: 2
};

// 测试结果统计
const testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  errors: [],
  dtshare: {
    connect: false,
    functions: {
      getStockList: false,
      getStockQuote: false,
      getHistoricalData: false,
      getFinancialIndicators: false,
      getIndustryClassification: false
    }
  }
};

// 配置日志级别
const LOG_LEVEL = 'debug'; // 'debug', 'info', 'error'
function log(level, message) {
  if (['debug', 'info', 'error'].indexOf(level) >= ['debug', 'info', 'error'].indexOf(LOG_LEVEL)) {
    console[level === 'debug' ? 'log' : level === 'info' ? 'log' : 'error'](`[${level.toUpperCase()}] ${message}`);
  }
}

// 测试单个API方法
async function testApiMethod(apiName, methodName, api, method, params = []) {
  testResults.total++;
  const testId = `${apiName}.${methodName}`;
  
  log('info', `开始测试 ${apiName}.${methodName} 方法`);
  
  try {
    const startTime = Date.now();
    const result = await method(...params);
    const endTime = Date.now();
    
    // 验证结果
    const isValid = validateResult(result, methodName);
    
    if (isValid) {
      log('info', `✅ 测试 ${testId} 通过! (耗时: ${endTime - startTime}ms)`);
      log('debug', `  返回数据类型: ${typeof result}`);
      if (result && typeof result === 'object') {
        log('debug', `  返回数据大小: ${Array.isArray(result) ? result.length : Object.keys(result).length}`);
      }
      testResults.passed++;
      return true;
    } else {
      log('error', `❌ 测试 ${testId} 失败: 返回数据无效`);
      testResults.failed++;
      testResults.errors.push(`${testId}: 返回数据无效`);
      return false;
    }
  } catch (error) {
    log('error', `❌ 测试 ${testId} 失败: ${error.message}`);
    testResults.failed++;
    testResults.errors.push(`${testId}: ${error.message}`);
    return false;
  }
}

// 验证API返回结果
function validateResult(result, methodName) {
  if (result === null || result === undefined) {
    return false;
  }
  
  // 根据方法名进行特定验证
  switch (methodName) {
    case 'getStockQuote':
    case 'getIndexQuote':
      return result.price !== undefined && !isNaN(result.price);
    
    case 'getBatchStockQuotes':
      return typeof result === 'object' && Object.keys(result).length > 0;
    
    case 'getStockBasicInfo':
      return result.name !== undefined && result.code !== undefined;
    
    case 'getHistoricalData':
      return Array.isArray(result) && result.length > 0 && result[0].close !== undefined;
    
    case 'getIndustryClassification':
    case 'getIndustryStocks':
    case 'getStockBasic':
      return Array.isArray(result) && result.length > 0;
    
    default:
      return true;
  }
}

// 测试新浪财经API
async function testSinacnApi() {
  log('info', '开始测试新浪财经API');
  
  await testApiMethod('sinacn', 'getStockQuote', sinacnApi, sinacnApi.getStockQuote, [config.testStockCode]);
  await testApiMethod('sinacn', 'getIndexQuote', sinacnApi, sinacnApi.getIndexQuote, [config.testIndexCode]);
  await testApiMethod('sinacn', 'getBatchStockQuotes', sinacnApi, sinacnApi.getBatchStockQuotes, [[config.testStockCode, config.testIndexCode]]);
  await testApiMethod('sinacn', 'getStockBasicInfo', sinacnApi, sinacnApi.getStockBasicInfo, [config.testStockCode]);
  
  // 历史数据方法可能返回模拟数据
  await testApiMethod('sinacn', 'getHistoricalData', sinacnApi, sinacnApi.getHistoricalData, [config.testStockCode]);
  
  log('info', '新浪财经API测试完成');
}

// 测试东方财富API
async function testEastmoneyApi() {
  log('info', '开始测试东方财富API');
  
  await testApiMethod('eastmoney', 'getStockQuote', eastmoneyApi, eastmoneyApi.getStockQuote, [config.testStockCode]);
  await testApiMethod('eastmoney', 'getIndustryClassification', eastmoneyApi, eastmoneyApi.getIndustryClassification);
  
  // 行业股票列表可能需要有效的行业代码
  // 先获取行业分类，然后使用第一个行业代码
  try {
    const industries = await eastmoneyApi.getIndustryClassification();
    if (industries && industries.length > 0) {
      const industryCode = industries[0].industry;
      await testApiMethod('eastmoney', 'getIndustryStocks', eastmoneyApi, eastmoneyApi.getIndustryStocks, [industryCode]);
    } else {
      log('info', '⚠️  东方财富行业分类获取失败，跳过行业股票列表测试');
    }
  } catch (error) {
    log('info', `⚠️  东方财富行业股票列表测试跳过: ${error.message}`);
  }
  
  log('info', '东方财富API测试完成');
}

// 测试Tushare API
async function testTushareApi() {
  log('info', '开始测试Tushare API');
  
  // Tushare需要Token，这里只测试基本功能，可能会失败
  log('info', '⚠️  Tushare API需要有效的Token才能正常工作');
  log('info', '⚠️  请在实际使用前配置有效的Tushare Token');
  
  try {
    await testApiMethod('tushare', 'getStockBasic', tushareApi, tushareApi.getStockBasic, [{ limit: 5 }]);
    // 尝试测试其他方法
    try {
      await testApiMethod('tushare', 'validateTushareToken', tushareApi, tushareApi.validateTushareToken);
      await testApiMethod('tushare', 'getDailyData', tushareApi, tushareApi.getDailyData, ['000001.SZ', '20230101', '20230131']);
      await testApiMethod('tushare', 'getIndexDaily', tushareApi, tushareApi.getIndexDaily, ['000001.SH', '20230101', '20230131']);
    } catch (subError) {
      log('info', `部分Tushare方法测试失败: ${subError.message}`);
    }
  } catch (error) {
    log('error', `Tushare API测试遇到问题: ${error.message}`);
  }
  
  log('info', 'Tushare API测试完成');
}

// 显示测试结果总结
function showTestSummary() {
  log('info', '\n=========================================');
  log('info', '测试结果总结:');
  log('info', `总测试数: ${testResults.total}`);
  log('info', `通过数: ${testResults.passed}`);
  log('info', `失败数: ${testResults.failed}`);
  log('info', `通过率: ${((testResults.passed / testResults.total) * 100).toFixed(2)}%`);
  
  if (testResults.errors.length > 0) {
    log('info', '\n失败详情:');
    testResults.errors.forEach((error, index) => {
      log('error', `${index + 1}. ${error}`);
    });
  }
  
  log('info', '\n建议:');
  if (testResults.failed > 0) {
    log('info', '- 检查失败的API方法，可能需要调整参数或修复实现');
    log('info', '- 对于Tushare API，请确保配置了有效的Token');
    log('info', '- 考虑实现模拟数据作为备用方案');
  } else {
    log('info', '- 所有API测试通过，可以集成到项目中使用');
  }
  log('info', '=========================================');
}

// 测试Dtshare API
async function testDtshareApi() {
  log('info', '开始测试Dtshare API');
  
  try {
    // 测试获取股票列表
    await testApiMethod('dtshare', 'getStockList', dtshareApi, dtshareApi.getStockList);
    
    // 测试获取行情数据
    await testApiMethod('dtshare', 'getStockQuote', dtshareApi, dtshareApi.getStockQuote, [config.testStockCode]);
    
    // 测试获取历史数据
    try {
      await testApiMethod('dtshare', 'getHistoricalData', dtshareApi, dtshareApi.getHistoricalData, ['000001', '2024-01-01', '2024-01-31']);
    } catch (e) {
      log('info', `历史数据获取失败: ${e.message}`);
    }
    
    // 测试获取财务指标
    try {
      await testApiMethod('dtshare', 'getFinancialIndicators', dtshareApi, dtshareApi.getFinancialIndicators, ['000001', '2023', '4']);
    } catch (e) {
      log('info', `财务指标获取失败: ${e.message}`);
    }
    
    // 测试获取行业分类
    try {
      await testApiMethod('dtshare', 'getIndustryClassification', dtshareApi, dtshareApi.getIndustryClassification);
    } catch (e) {
      log('info', `行业分类获取失败: ${e.message}`);
    }
    
  } catch (error) {
    log('error', `Dtshare API测试遇到问题: ${error.message}`);
  }
  
  log('info', 'Dtshare API测试完成');
}

// 测试BaoStock API
async function testBaostockApi() {
  log('info', '开始测试BaoStock API');
  
  try {
    // 测试登录功能
    await testApiMethod('baostock', 'login', baostockApi, baostockApi.login);
    
    // 注意：由于BaoStock需要Python环境，其他方法可能会失败
    // 这里只测试基本连接功能，记录其他方法为预期失败
    log('info', 'BaoStock API其他方法需要Python环境支持，跳过详细测试');
    
    // 最后测试登出功能
    await testApiMethod('baostock', 'logout', baostockApi, baostockApi.logout);
  } catch (error) {
    log('error', `BaoStock API测试遇到问题: ${error.message}`);
  }
  
  log('info', 'BaoStock API测试完成');
}

// 主测试函数
async function runAllTests() {
  log('info', '开始测试所有股票API...');
  
  try {
    // 逐个测试各个API
    await testSinacnApi();
    await testEastmoneyApi();
    await testTushareApi();
    await testDtshareApi(); // 添加Dtshare API测试
    await testBaostockApi(); // 添加BaoStock API测试
  } catch (error) {
    log('error', `测试过程中发生错误: ${error.message}`);
  } finally {
    // 显示测试总结
    showTestSummary();
  }
}

// 运行测试
if (import.meta.url === new URL(process.argv[1], import.meta.url).href) {
  runAllTests().then(() => {
    process.exit(testResults.failed > 0 ? 1 : 0);
  });
}

export { runAllTests, testResults };