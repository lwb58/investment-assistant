// 模拟前端API调用测试
import fetch from 'node-fetch';

console.log('测试前端API调用...');

async function testApiCall() {
    try {
        // 直接调用后端API（模拟前端通过代理的调用）
        const response = await fetch('http://localhost:8000/api/stocks');
        
        console.log(`响应状态码: ${response.status}`);
        
        if (response.ok) {
            const data = await response.json();
            console.log(`获取到的股票数量: ${data.length}`);
            console.log('股票数据:', JSON.stringify(data, null, 2));
        } else {
            const errorText = await response.text();
            console.log(`API调用失败: ${errorText}`);
        }
    } catch (error) {
        console.error('测试API调用时出错:', error);
    }
}

testApiCall();