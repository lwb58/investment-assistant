import externalDataService from './services/externalDataService.js';
import { getDB } from './config/db.js';

// 测试脚本
async function runTests() {
  console.log('开始测试外部数据服务...');
  
  try {
    // 1. 测试新浪财经大盘指数API (问题最多的部分)
    console.log('\n测试新浪财经大盘指数API...');
    try {
      const indexData = await externalDataService.getSinaMarketIndex();
      console.log('新浪财经大盘指数API测试成功!');
      console.log('上证指数:', indexData.sh.price);
      console.log('深证成指:', indexData.sz.price);
      console.log('创业板指:', indexData.cy.price);
    } catch (error) {
      console.error('新浪财经大盘指数API测试失败:', error.message);
    }
    
    // 2. 测试东方财富股票行情API
    console.log('\n测试东方财富股票行情API...');
    try {
      const eastMoneyData = await externalDataService.getEastMoneyStockQuote('600000.SH');
      if (eastMoneyData) {
        console.log('东方财富股票行情API测试成功!');
        console.log('股票名称:', eastMoneyData.name);
        console.log('当前价格:', eastMoneyData.price);
      } else {
        console.error('东方财富股票行情API返回空数据');
      }
    } catch (error) {
      console.error('东方财富股票行情API测试失败:', error.message);
    }
    
    // 3. 测试新浪财经股票行情API
    console.log('\n测试新浪财经股票行情API...');
    try {
      const sinaData = await externalDataService.getSinaStockQuote('600000.SH');
      if (sinaData) {
        console.log('新浪财经股票行情API测试成功!');
        console.log('股票名称:', sinaData.name);
        console.log('当前价格:', sinaData.price);
      } else {
        console.error('新浪财经股票行情API返回空数据');
      }
    } catch (error) {
      console.error('新浪财经股票行情API测试失败:', error.message);
    }
    
    // 4. 测试Tushare API (可能需要有效的token)
    console.log('\n测试Tushare股票行情API...');
    try {
      const tushareData = await externalDataService.getTushareStockQuote('600000.SH');
      if (tushareData) {
        console.log('Tushare股票行情API测试成功!');
        console.log('股票名称:', tushareData.name);
        console.log('当前价格:', tushareData.price);
      } else {
        console.warn('Tushare股票行情API返回空数据，可能是token无效或API有变化');
      }
    } catch (error) {
      console.error('Tushare股票行情API测试失败:', error.message);
    }
    
    // 5. 测试综合数据获取
    console.log('\n测试综合数据获取...');
    try {
      const integratedData = await externalDataService.getIntegratedStockData('600000.SH');
      console.log('综合数据获取测试成功!');
      console.log('数据来源:', integratedData.data_sources);
      console.log('股票名称:', integratedData.name);
      console.log('当前价格:', integratedData.price);
    } catch (error) {
      console.error('综合数据获取测试失败:', error.message);
    }
    
    // 6. 测试批量数据获取
    console.log('\n测试批量数据获取...');
    try {
      const batchData = await externalDataService.batchGetStockData(['600000.SH', '000001.SZ']);
      console.log('批量数据获取测试完成!');
      console.log('成功获取的数据数量:', Object.keys(batchData).length);
    } catch (error) {
      console.error('批量数据获取测试失败:', error.message);
    }
    
  } catch (error) {
    console.error('测试过程中发生未知错误:', error);
  } finally {
    console.log('\n测试完成!');
  }
}

// 运行测试
runTests();
