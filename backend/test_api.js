// API调用测试脚本
import axios from 'axios';

// 测试函数
async function testApi() {
  console.log('开始测试API调用...');
  
  // 1. 测试新浪财经大盘指数API
  try {
    console.log('\n--- 测试新浪财经大盘指数API ---');
    const sinaUrl = 'https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006';
    console.log(`请求URL: ${sinaUrl}`);
    
    const response = await axios.get(sinaUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 10000
    });
    
    console.log('响应状态:', response.status);
    console.log('响应数据长度:', response.data.length, '字符');
    console.log('响应数据前100字符:', response.data.substring(0, 100), '...');
    
    // 验证响应数据格式
    if (response.data.includes('hq_str_s_sh000001')) {
      console.log('✓ 新浪财经API响应数据格式正确');
    } else {
      console.log('✗ 新浪财经API响应数据格式不正确');
    }
  } catch (error) {
    console.error('✗ 新浪财经API调用失败:', error.message);
    if (error.response) {
      console.log('响应状态:', error.response.status);
      console.log('响应数据:', error.response.data);
    } else if (error.request) {
      console.log('请求发送失败，未收到响应');
    }
  }
  
  // 2. 测试东方财富API
  try {
    console.log('\n--- 测试东方财富股票行情API ---');
    const eastMoneyUrl = 'https://push2.eastmoney.com/api/qt/stock/get?fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62&secid=0.000001&ut=fcea386e386d9c584928df10665e7bfb&forcect=1';
    console.log(`请求URL: ${eastMoneyUrl}`);
    
    const response = await axios.get(eastMoneyUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://quote.eastmoney.com/'
      },
      timeout: 10000
    });
    
    console.log('响应状态:', response.status);
    console.log('响应数据类型:', typeof response.data);
    
    // 东方财富返回的可能是JSONP格式
    try {
      const data = typeof response.data === 'string' && response.data.includes('(') 
        ? JSON.parse(response.data.match(/\((.*)\)/)[1])
        : response.data;
      
      console.log('✓ 东方财富API响应解析成功');
      console.log('数据结构包含data:', data.data !== undefined);
    } catch (parseError) {
      console.log('✗ 东方财富API响应解析失败:', parseError.message);
      console.log('响应数据前100字符:', String(response.data).substring(0, 100), '...');
    }
  } catch (error) {
    console.error('✗ 东方财富API调用失败:', error.message);
    if (error.response) {
      console.log('响应状态:', error.response.status);
    }
  }
  
  // 3. 测试网络连接
  try {
    console.log('\n--- 测试基本网络连接 ---');
    const testUrl = 'https://www.baidu.com';
    const response = await axios.get(testUrl, {
      timeout: 5000
    });
    console.log(`✓ 基本网络连接正常 (${testUrl})`);
  } catch (error) {
    console.error('✗ 基本网络连接失败，请检查网络设置:', error.message);
  }
  
  console.log('\nAPI测试完成');
}

// 执行测试
testApi().catch(err => {
  console.error('测试脚本执行失败:', err);
});