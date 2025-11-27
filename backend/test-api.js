import dotenv from 'dotenv';
dotenv.config();

// 导入API模块
import tushareApi from './apis/tushareApi.js';
import sinacnApi from './apis/sinacnApi.js';
import eastmoneyApi from './apis/eastmoneyApi.js';

console.log('开始测试API模块...');

// 测试结果对象
const testResults = {
  tushareApi: { status: 'pending', error: null },
  sinacnApi: { status: 'pending', error: null },
  eastmoneyApi: { status: 'pending', error: null }
};

// 测试Tushare API
async function testTushareApi() {
  try {
    console.log('\n测试Tushare API...');
    // 测试获取股票基本信息
    const stockBasic = await tushareApi.getStockBasic({ limit: 5 });
    console.log('Tushare股票基本信息:', stockBasic.slice(0, 2));
    testResults.tushareApi.status = 'success';
  } catch (error) {
    console.error('Tushare API测试失败:', error.message);
    testResults.tushareApi.status = 'failed';
    testResults.tushareApi.error = error.message;
  }
}

// 测试新浪财经API
async function testSinacnApi() {
  try {
    console.log('\n测试新浪财经API...');
    // 测试获取股票行情 - 使用正确的格式
    const stockQuote = await sinacnApi.getStockQuote('600000.SH');
    console.log('新浪股票行情:', stockQuote);
    testResults.sinacnApi.status = 'success';
  } catch (error) {
    console.error('新浪财经API测试失败:', error.message);
    testResults.sinacnApi.status = 'failed';
    testResults.sinacnApi.error = error.message;
  }
}

// 测试东方财富API
async function testEastmoneyApi() {
  try {
    console.log('\n测试东方财富API...');
    // 测试获取股票行情
    const stockQuote = await eastmoneyApi.getStockQuote('600000.SH');
    console.log('东方财富股票行情:', stockQuote);
    testResults.eastmoneyApi.status = 'success';
  } catch (error) {
    console.error('东方财富API测试失败:', error.message);
    testResults.eastmoneyApi.status = 'failed';
    testResults.eastmoneyApi.error = error.message;
  }
}

// 运行所有测试
async function runAllTests() {
  // 并发运行测试以节省时间
  await Promise.all([
    testTushareApi(),
    testSinacnApi(),
    testEastmoneyApi()
  ]);
  
  // 输出测试结果摘要
  console.log('\n========== 测试结果摘要 ==========');
  Object.entries(testResults).forEach(([apiName, result]) => {
    console.log(`${apiName}: ${result.status.toUpperCase()}`);
    if (result.error) {
      console.log(`  错误信息: ${result.error}`);
    }
  });
  
  // 检查是否所有测试都通过
  const allPassed = Object.values(testResults).every(r => r.status === 'success');
  console.log('\n测试结论:', allPassed ? '所有API测试通过！' : '部分API测试失败，请检查错误信息。');
}

// 执行测试
runAllTests().catch(err => {
  console.error('测试过程中发生错误:', err);
});