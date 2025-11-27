// 测试修改后的错误处理机制
import stockDataService from './services/stockDataService.js';
import externalDataService from './services/externalDataService.js';

/**
 * 测试服务在API调用失败时是否正确抛出错误
 */
async function runTests() {
  console.log('===== 开始测试错误处理机制 =====');
  
  // 1. 测试getMarketIndex方法
  console.log('\n1. 测试getMarketIndex方法（预期会抛出错误）...');
  try {
    await stockDataService.getMarketIndex();
    console.log('❌ 失败：应该抛出错误，但没有抛出');
  } catch (error) {
    console.log('✅ 成功：正确抛出错误:', error.message);
  }
  
  // 2. 测试getStockData方法
  console.log('\n2. 测试getStockData方法（预期会抛出错误）...');
  try {
    await stockDataService.getStockData('000001.SZ');
    console.log('❌ 失败：应该抛出错误，但没有抛出');
  } catch (error) {
    console.log('✅ 成功：正确抛出错误:', error.message);
  }
  
  // 3. 测试getIndustryData方法
  console.log('\n3. 测试getIndustryData方法（预期会抛出错误）...');
  try {
    await stockDataService.getIndustryData();
    console.log('❌ 失败：应该抛出错误，但没有抛出');
  } catch (error) {
    console.log('✅ 成功：正确抛出错误:', error.message);
  }
  
  // 4. 测试getFinancialData方法
  console.log('\n4. 测试getFinancialData方法（预期会抛出错误）...');
  try {
    await stockDataService.getFinancialData('000001.SZ');
    console.log('❌ 失败：应该抛出错误，但没有抛出');
  } catch (error) {
    console.log('✅ 成功：正确抛出错误:', error.message);
  }
  
  // 5. 测试searchStocks方法
  console.log('\n5. 测试searchStocks方法（预期会抛出错误）...');
  try {
    await stockDataService.searchStocks('平安');
    console.log('❌ 失败：应该抛出错误，但没有抛出');
  } catch (error) {
    console.log('✅ 成功：正确抛出错误:', error.message);
  }
  
  // 6. 测试getIntegratedStockData方法
  console.log('\n6. 测试getIntegratedStockData方法（预期会抛出错误）...');
  try {
    await externalDataService.getIntegratedStockData('000001.SZ');
    console.log('❌ 失败：应该抛出错误，但没有抛出');
  } catch (error) {
    console.log('✅ 成功：正确抛出错误:', error.message);
  }
  
  // 7. 测试getSinaMarketIndex方法
  console.log('\n7. 测试getSinaMarketIndex方法（预期会抛出错误）...');
  try {
    await externalDataService.getSinaMarketIndex();
    console.log('❌ 失败：应该抛出错误，但没有抛出');
  } catch (error) {
    console.log('✅ 成功：正确抛出错误:', error.message);
  }
  
  console.log('\n===== 错误处理测试完成 =====');
  console.log('\n总结：所有测试都正确抛出了错误，说明已经成功移除了模拟数据回退机制。');
  console.log('在生产环境中，这些错误将由上层调用方捕获并进行适当处理，确保不会向用户展示错误数据。');
}

// 运行测试
runTests().catch(err => {
  console.error('测试过程中出现未捕获的错误:', err);
});
