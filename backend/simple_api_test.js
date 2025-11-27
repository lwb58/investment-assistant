// 简单的API测试脚本
import { tushareApi, eastmoneyApi, sinacnApi, baostockApi, dtshareApi } from './apis/stockApi.js';

async function testAllApis() {
  console.log('开始API测试...');
  
  const testStockCode = '000001.SZ';
  
  // 测试新浪财经API
  console.log('\n=== 测试新浪财经API ===');
  try {
    const quote = await sinacnApi.getStockQuote(testStockCode);
    console.log('新浪财经行情数据:', quote);
    
    // 测试批量行情
    console.log('\n测试新浪财经批量行情...');
    const batchQuotes = await sinacnApi.getBatchStockQuotes([testStockCode, '600000.SH']);
    console.log('批量行情数据数量:', batchQuotes ? batchQuotes.length : '未知');
  } catch (error) {
    console.error('新浪财经API错误:', error.message);
  }
  
  // 测试东方财富API
  console.log('\n=== 测试东方财富API ===');
  try {
    const quote = await eastmoneyApi.getStockQuote(testStockCode);
    console.log('东方财富行情数据:', quote);
  } catch (error) {
    console.error('东方财富API错误:', error.message);
  }
  
  // 测试Tushare API
  console.log('\n=== 测试Tushare API ===');
  try {
    console.log('Tushare验证Token...');
    const result = await tushareApi.validateTushareToken();
    console.log('Tushare验证结果:', result ? '成功' : '失败');
  } catch (error) {
    console.error('Tushare API错误:', error.message);
  }
  
  // 测试Dtshare API
  console.log('\n=== 测试Dtshare API ===');
  try {
    console.log('Dtshare配置API密钥...');
    dtshareApi.configure('default_test_key');
    
    // 尝试获取股票列表（如果API允许）
    console.log('Dtshare获取股票列表...');
    try {
      const stocks = await dtshareApi.getStockList();
      console.log('Dtshare股票列表数量:', stocks ? stocks.length : '未知');
    } catch (e) {
      console.log('Dtshare股票列表可能需要有效的API密钥，错误信息:', e.message);
    }
  } catch (error) {
    console.error('Dtshare API错误:', error.message);
  }
  
  // 测试BaoStock API
  console.log('\n=== 测试BaoStock API ===');
  try {
    console.log('BaoStock登录...');
    await baostockApi.login();
    console.log('BaoStock登录成功');
    
    // 测试获取股票基本信息
    console.log('获取股票基本信息...');
    const stockInfo = await baostockApi.getStockBasicInfo(testStockCode);
    console.log('股票基本信息:', stockInfo);
  } catch (error) {
    console.error('BaoStock API错误:', error.message);
  } finally {
    try {
      await baostockApi.logout();
      console.log('BaoStock已登出');
    } catch (e) {
      // 忽略登出错误
    }
  }
  
  console.log('\nAPI测试完成!');
}

testAllApis().catch(console.error);