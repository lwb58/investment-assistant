// 服务测试脚本
import externalDataService from './services/externalDataService.js';
import stockDataService from './services/stockDataService.js';

// 测试函数
async function runTests() {
  console.log('开始测试服务功能...');
  console.log('=======================================');
  
  try {
    // 1. 测试获取市场指数数据
    console.log('\n1. 测试获取市场指数数据...');
    const marketIndexResult = await stockDataService.getMarketIndex();
    console.log('市场指数数据获取结果:', marketIndexResult ? '成功' : '失败');
    if (marketIndexResult) {
      console.log('数据来源:', marketIndexResult.source || '未知');
      console.log('上证指数:', marketIndexResult.sh?.name, marketIndexResult.sh?.price);
      console.log('深证成指:', marketIndexResult.sz?.name, marketIndexResult.sz?.price);
      console.log('创业板指:', marketIndexResult.cy?.name, marketIndexResult.cy?.price);
    }
    
    // 2. 测试获取股票数据
    console.log('\n2. 测试获取股票数据...');
    const stockSymbol = '000001.SZ'; // 平安银行
    const stockDataResult = await stockDataService.getStockData(stockSymbol);
    console.log(`股票 ${stockSymbol} 数据获取结果:`, stockDataResult ? '成功' : '失败');
    if (stockDataResult) {
      console.log('数据来源:', stockDataResult.source || '未知');
      console.log('股票名称:', stockDataResult.name);
      console.log('价格:', stockDataResult.price);
      console.log('涨跌幅:', stockDataResult.pct_change + '%');
    }
    
    // 3. 直接测试模拟数据功能
    console.log('\n3. 测试模拟数据功能...');
    const mockMarketIndex = externalDataService.getMockMarketIndex();
    console.log('模拟市场指数数据:', mockMarketIndex ? '生成成功' : '失败');
    
    const mockStockData = externalDataService.getMockStockData('600036.SH');
    console.log('模拟股票数据:', mockStockData ? '生成成功' : '失败');
    if (mockStockData) {
      console.log('模拟股票名称:', mockStockData.name);
      console.log('模拟股票价格:', mockStockData.price);
    }
    
    // 4. 测试搜索股票功能
    console.log('\n4. 测试搜索股票功能...');
    const searchResult = await stockDataService.searchStocks('银行');
    console.log('股票搜索结果数量:', searchResult?.length || 0);
    if (searchResult && searchResult.length > 0) {
      console.log('前3个搜索结果:', searchResult.slice(0, 3).map(s => `${s.name}(${s.symbol})`));
    }
    
    console.log('\n=======================================');
    console.log('所有测试完成！');
    
  } catch (error) {
    console.error('测试过程中发生错误:', error.message);
    console.error(error.stack);
  }
}

// 执行测试
runTests().catch(err => {
  console.error('测试脚本执行失败:', err);
});