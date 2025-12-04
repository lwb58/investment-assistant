// 测试杜邦分析接口，查看返回数据格式和时间颗粒度

import fetch from 'node-fetch';

// 测试股票ID，使用一个已知存在的股票ID
const testStockId = '600036';
const apiUrl = `http://localhost:5174/api/stocks/dubang/${testStockId}`;

async function testDupontApi() {
  try {
    console.log(`正在调用杜邦分析接口: ${apiUrl}`);
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      console.error(`请求失败: ${response.status}`);
      const errorText = await response.text();
      console.error(`错误信息: ${errorText}`);
      return;
    }
    
    const data = await response.json();
    console.log('接口返回数据:');
    console.log(JSON.stringify(data, null, 2));
    
    // 分析数据结构
    if (Array.isArray(data)) {
      console.log(`\n数据包含 ${data.length} 条记录`);
      
      // 检查时间字段
      if (data.length > 0) {
        const firstItem = data[0];
        console.log('\n第一条记录的字段:');
        console.log(Object.keys(firstItem));
        
        // 查找时间相关字段
        const timeFields = Object.keys(firstItem).filter(key => 
          key.includes('年份') || key.includes('year') || key.includes('报告期') || key.includes('period')
        );
        
        if (timeFields.length > 0) {
          console.log('\n找到时间相关字段:', timeFields);
          
          // 显示所有时间值
          console.log('\n所有时间值:');
          data.forEach((item, index) => {
            const timeValue = item[timeFields[0]];
            console.log(`${index + 1}. ${timeValue}`);
          });
          
          // 分析时间颗粒度
          const timeValues = data.map(item => item[timeFields[0]]);
          const uniqueTimeValues = [...new Set(timeValues)];
          console.log(`\n时间值去重后: ${uniqueTimeValues.length} 个独特值`);
          console.log(uniqueTimeValues);
        }
      }
    } else {
      console.log('返回数据不是数组格式');
      console.log('数据类型:', typeof data);
    }
  } catch (error) {
    console.error('调用接口时发生错误:', error);
  }
}

testDupontApi();