// 测试前端API请求
import axios from 'axios';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

// 为ES模块添加__filename和__dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 测试配置
const CONFIG = {
  backendUrl: 'http://localhost:8000/api',
  testEndpoints: [
    { name: 'stocks', path: '/stocks' },
    { name: 'stocks search', path: '/stocks?search=茅台' }
  ]
};

async function testApiEndpoints() {
  console.log('开始测试API端点...');
  console.log(`测试环境: Node.js ${process.version}`);
  console.log(`后端基础URL: ${CONFIG.backendUrl}`);
  console.log('=' * 50);

  let successCount = 0;
  let failedCount = 0;

  for (const endpoint of CONFIG.testEndpoints) {
    const fullUrl = `${CONFIG.backendUrl}${endpoint.path}`;
    console.log(`\n测试: ${endpoint.name}`);
    console.log(`URL: ${fullUrl}`);
    
    try {
      const response = await axios.get(fullUrl, {
        timeout: 5000,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log(`✅ 成功: 状态码 ${response.status}`);
      console.log(`响应时间: ${response.headers['x-response-time'] || 'N/A'}ms`);
      console.log(`返回数据类型: ${typeof response.data}`);
      console.log(`数据长度: ${Array.isArray(response.data) ? response.data.length : 'N/A'}`);
      
      if (Array.isArray(response.data) && response.data.length > 0) {
        console.log('样本数据:', JSON.stringify(response.data[0], null, 2));
      }
      
      successCount++;
    } catch (error) {
      console.log(`❌ 失败:`);
      if (error.response) {
        console.log(`  状态码: ${error.response.status}`);
        console.log(`  响应数据:`, error.response.data);
      } else if (error.request) {
        console.log(`  请求已发送但未收到响应: ${error.message}`);
      } else {
        console.log(`  请求配置错误: ${error.message}`);
      }
      failedCount++;
    }
  }

  console.log('\n' + '=' * 50);
  console.log(`测试结果: 成功 ${successCount}, 失败 ${failedCount}`);
  
  if (failedCount > 0) {
    console.log('\n建议检查:');
    console.log('1. 后端服务是否正在运行');
    console.log('2. 防火墙设置是否阻止了连接');
    console.log('3. API路由配置是否正确');
  } else {
    console.log('\n🎉 所有API端点测试成功!');
  }
}

// 检查axios是否可用
async function checkDependencies() {
  try {
    // axios已在顶部导入，这里只需要确认模块正常加载
    return true;
  } catch (error) {
    console.log('安装axios...');
    try {
      execSync('npm install axios --no-save', { stdio: 'inherit' });
      return true;
    } catch (execError) {
      console.log('无法安装axios，请手动安装后再运行测试');
      return false;
    }
  }
}

// 主函数
async function main() {
  if (await checkDependencies()) {
    await testApiEndpoints();
  }
}

main().catch(err => {
  console.error('测试执行出错:', err);
  process.exit(1);
});