// 直接测试apiService的调用
import apiService from './apiService.js';

console.log('开始测试apiService直接调用...');

// 测试getStocks方法
async function testApiService() {
    try {
        console.log('apiService实例:', apiService);
        console.log('调用apiService.getStocks()...');
        const result = await apiService.getStocks();
        console.log('API调用成功，返回数据长度:', result.length);
        console.log('返回数据样例:', result.slice(0, 2));
    } catch (error) {
        console.error('API调用失败:', error);
    }
}

// 立即执行测试
testApiService();