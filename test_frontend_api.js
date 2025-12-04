// 模拟前端API调用测试
import fetch from 'node-fetch';

console.log('测试前端API调用...');

async function testApiCall() {
    try {
        // 测试股票详情API
        const response = await fetch('http://localhost:8000/api/stocks/600036/detail');
        
        console.log(`响应状态码: ${response.status}`);
        
        if (response.ok) {
            const data = await response.json();
            console.log('股票详情数据:', JSON.stringify(data, null, 2));
            console.log('基础信息:', JSON.stringify(data.baseInfo, null, 2));
            console.log('核心行情:', JSON.stringify(data.coreQuotes, null, 2));
        } else {
            const errorText = await response.text();
            console.log(`API调用失败: ${errorText}`);
        }
    } catch (error) {
        console.error('测试API调用时出错:', error);
    }
}

testApiCall();