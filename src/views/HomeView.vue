<template>
  <div class="home">
    <!-- 顶部导航栏 -->
    <header class="top-nav">
      <div class="logo-container">
        <h1 class="logo">Invest<span class="highlight">Pro</span></h1>
        <div class="nav-links">
          <a href="/" class="nav-link active">首页</a>
          <a href="/stock/search" class="nav-link">股票搜索</a>
          <a href="#" class="nav-link">股票估值</a>
          <a href="#" class="nav-link">投资组合</a>
          <a href="#" class="nav-link">市场分析</a>
          <a href="#" class="nav-link">个人中心</a>
        </div>
      </div>
    </header>
    
    <!-- 主要内容区 -->
    <main class="content">
      <!-- 欢迎区域 -->
      <section class="welcome-section">
        <div class="welcome-content">
          <h2>智能投资助手</h2>
          <p>专业的个人投资分析与决策平台</p>
        </div>
      </section>
      
      <!-- 功能列表区域 -->
      <section class="features-section">
        <h3 class="section-title">核心功能</h3>
        <div class="feature-list">
          <div class="feature-item" @click="handleFeatureClick('stock-valuation')">
            <div class="feature-icon">📊</div>
            <div class="feature-details">
              <h4 class="feature-title">股票估值分析</h4>
              <p class="feature-desc">基于基本面数据的股票估值计算与分析</p>
            </div>
            <div class="feature-arrow">→</div>
          </div>
          
          <div class="feature-item" @click="handleFeatureClick('portfolio')">
            <div class="feature-icon">📈</div>
            <div class="feature-details">
              <h4 class="feature-title">投资组合管理</h4>
              <p class="feature-desc">实时追踪投资组合表现与收益分析</p>
            </div>
            <div class="feature-arrow">→</div>
          </div>
          
          <div class="feature-item" @click="handleFeatureClick('market-data')">
            <div class="feature-icon">📉</div>
            <div class="feature-details">
              <h4 class="feature-title">市场行情查看</h4>
              <p class="feature-desc">实时股票行情与市场趋势分析</p>
            </div>
            <div class="feature-arrow">→</div>
          </div>
          
          <div class="feature-item" @click="handleFeatureClick('investment-advice')">
            <div class="feature-icon">💡</div>
            <div class="feature-details">
              <h4 class="feature-title">投资建议生成</h4>
              <p class="feature-desc">基于数据分析的个性化投资建议</p>
            </div>
            <div class="feature-arrow">→</div>
          </div>
        </div>
      </section>
      
      <!-- 市场概览卡片 -->
      <section class="market-section">
        <h3 class="section-title">
          市场概览 
          <span v-if="marketData" class="update-time">
            (更新时间: {{ new Date(marketData.timestamp).toLocaleTimeString('zh-CN') }})
          </span>
          <button v-if="!loading" class="refresh-btn" @click="loadMarketData">刷新</button>
        </h3>
        
        <div v-if="loading" class="loading-state">
          <p>正在加载市场数据...</p>
        </div>
        
        <div v-else-if="error" class="error-state">
          <p class="error-text">{{ error }}</p>
        </div>
        
        <div v-else class="market-card">
          <div class="market-item" v-for="index in [marketData?.sh, marketData?.sz, marketData?.cy]" :key="index?.code" v-if="index">
            <div class="market-name">{{ index.name }}</div>
            <div class="market-value">{{ formatNumber(index.close) }}</div>
            <div class="market-change" :class="getChangeClass(index.change)">
              {{ formatPercent(index.pct_change) }}
              <span class="change-value">({{ formatNumber(index.change) }})</span>
            </div>
            <div class="market-volume">
              成交量: {{ (index.volume / 100000000).toFixed(2) }}亿
            </div>
          </div>
        </div>
      </section>
      
      <!-- 市场详情展开区域 -->
      <section v-if="marketData" class="market-details-section">
        <h4 class="details-title">详细行情</h4>
        <div class="market-details">
          <div class="detail-row" v-for="index in [marketData.sh, marketData.sz, marketData.cy]" :key="index.code">
            <div class="detail-index-name">{{ index.name }}</div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">开盘价</span>
                <span class="detail-value">{{ formatNumber(index.open) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">最高价</span>
                <span class="detail-value">{{ formatNumber(index.high) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">最低价</span>
                <span class="detail-value">{{ formatNumber(index.low) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">成交额</span>
                <span class="detail-value">{{ (index.amount / 100000000).toFixed(2) }}亿</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
    
    <!-- 页脚 -->
    <footer class="footer">
      <p>© 2024 InvestPro 智能投资助手 | 仅供参考，不构成投资建议</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { stockApi } from '@/services/apiService';

// 定义市场数据类型
interface MarketIndex {
  code: string;
  name: string;
  open: number;
  close: number;
  high: number;
  low: number;
  volume: number;
  amount: number;
  change: number;
  pct_change: number;
}

interface MarketData {
  sh: MarketIndex;
  sz: MarketIndex;
  cy: MarketIndex;
  timestamp: Date;
}

// 市场数据响应式变量
const marketData = ref<MarketData | null>(null);
const loading = ref(false);
const error = ref('');

// 格式化数字
const formatNumber = (num: number): string => {
  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

// 格式化百分比
const formatPercent = (pct: number): string => {
  const sign = pct >= 0 ? '+' : '';
  return `${sign}${pct.toFixed(2)}%`;
};

// 判断涨跌颜色
const getChangeClass = (change: number): string => {
  if (change > 0) return 'up';
  if (change < 0) return 'down';
  return '';
};

// 加载市场数据
const loadMarketData = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const response = await stockApi.getMarketIndex();
    if (response.success && response.data) {
      marketData.value = response.data;
    } else {
      error.value = '获取市场数据失败';
      // 使用默认数据作为备选
      useDefaultMarketData();
    }
  } catch (err) {
    console.error('加载市场数据出错:', err);
    error.value = '网络错误，请稍后重试';
    // 使用默认数据作为备选
    useDefaultMarketData();
  } finally {
    loading.value = false;
  }
};

// 使用默认市场数据
const useDefaultMarketData = () => {
  marketData.value = {
    sh: {
      code: 'sh',
      name: '上证指数',
      open: 3150.0,
      close: 3178.5,
      high: 3185.0,
      low: 3145.0,
      volume: 280000000000,
      amount: 350000000000,
      change: 28.5,
      pct_change: 0.91
    },
    sz: {
      code: 'sz',
      name: '深证成指',
      open: 10200.0,
      close: 10350.0,
      high: 10380.0,
      low: 10180.0,
      volume: 320000000000,
      amount: 410000000000,
      change: 150.0,
      pct_change: 1.47
    },
    cy: {
      code: 'cy',
      name: '创业板指',
      open: 2050.0,
      close: 2095.0,
      high: 2100.0,
      low: 2045.0,
      volume: 150000000000,
      amount: 220000000000,
      change: 45.0,
      pct_change: 2.19
    },
    timestamp: new Date()
  };
};

// 功能点击处理函数
const handleFeatureClick = (featureType: string) => {
  console.log(`点击了功能: ${featureType}`);
  // 这里可以根据不同的功能类型跳转到对应的页面
  // 例如：router.push(`/${featureType}`);
  alert(`您点击了 ${featureType} 功能，该功能即将上线！`);
};

// 组件挂载时加载数据
onMounted(() => {
  loadMarketData();
  // 设置定时刷新（每30秒刷新一次）
  const intervalId = setInterval(loadMarketData, 30000);
  
  // 组件卸载时清除定时器
  const cleanup = () => {
    clearInterval(intervalId);
  };
  
  // 在Vue 3中，可以使用onUnmounted钩子
  import('vue').then(({ onUnmounted }) => {
    onUnmounted(cleanup);
  });
});
</script>

<style scoped>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 主页容器 */
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 顶部导航 */
.top-nav {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1.2rem 2rem;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo-container {
  max-width: 1200px;
  margin: 0 auto;
}

.logo {
  font-size: 1.8rem;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.logo .highlight {
  color: #667eea;
}

/* 主要内容区 */
.content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  margin-bottom: 3rem;
  padding: 3rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  color: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.welcome-content h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.welcome-content p {
  font-size: 1.2rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
}

/* 功能区域 */
.features-section {
  margin-bottom: 3rem;
}

.section-title {
  color: white;
  font-size: 1.8rem;
  margin-bottom: 2rem;
  text-align: center;
  font-weight: 600;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.feature-item {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  padding: 1.5rem 2rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 1);
}

.feature-icon {
  font-size: 2.5rem;
  margin-right: 1.5rem;
  width: 60px;
  text-align: center;
}

.feature-details {
  flex: 1;
}

.feature-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.feature-desc {
  color: #666;
  font-size: 1rem;
}

.feature-arrow {
  color: #667eea;
  font-size: 1.5rem;
  font-weight: bold;
  transition: transform 0.3s ease;
}

.feature-item:hover .feature-arrow {
  transform: translateX(5px);
}

/* 市场概览区域 */
.market-section {
  margin-bottom: 2rem;
}

.market-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.market-item {
  background: rgba(255, 255, 255, 0.95);
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.market-name {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.market-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.5rem;
}

.market-change {
  font-size: 1rem;
  font-weight: 600;
  padding: 0.2rem 0.8rem;
  border-radius: 20px;
  display: inline-block;
}

.market-change.up {
  color: #2ecc71;
  background: rgba(46, 204, 113, 0.1);
}

.market-change.down {
  color: #e74c3c;
  background: rgba(231, 76, 60, 0.1);
}

/* 页脚 */
.footer {
  background: rgba(255, 255, 255, 0.95);
  padding: 1.5rem 2rem;
  text-align: center;
  color: #666;
  font-size: 0.9rem;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
  }
  
  .welcome-content h2 {
    font-size: 2rem;
  }
  
  .feature-item {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }
  
  .feature-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  .feature-arrow {
    margin-top: 1rem;
  }
  
  .market-card {
    grid-template-columns: 1fr;
  }
}
<style scoped>
/* 顶部导航栏样式 */
.top-nav {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.logo-container {
  max-width: 1200px;
  margin: 0 auto;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.highlight {
  color: #ffd700;
}

/* 主要内容区 */
.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  flex: 1;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.welcome-content h2 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.welcome-content p {
  color: #666;
  font-size: 1.1rem;
}

/* 功能列表区域 */
.features-section {
  margin-bottom: 3rem;
}

.section-title {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #333;
  position: relative;
  padding-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100px;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.feature-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.feature-item {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 2.5rem;
}

.feature-details {
  flex: 1;
}

.feature-title {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.feature-desc {
  color: #666;
  font-size: 0.95rem;
}

.feature-arrow {
  color: #667eea;
  font-size: 1.5rem;
}

/* 市场概览样式 */
.market-section {
  margin-bottom: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.update-time {
  font-size: 0.8rem;
  color: #666;
  font-weight: normal;
}

.refresh-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s ease;
}

.refresh-btn:hover {
  background: #5a67d8;
}

.market-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.market-item {
  text-align: center;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.market-name {
  font-size: 1rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.market-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.5rem;
}

.market-change {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.market-change.up {
  color: #e74c3c;
}

.market-change.down {
  color: #2ecc71;
}

.change-value {
  font-size: 0.9rem;
  margin-left: 0.5rem;
}

.market-volume {
  font-size: 0.85rem;
  color: #666;
}

/* 市场详情样式 */
.market-details-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.details-title {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #333;
}

.market-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.detail-index-name {
  background: #f8f9fa;
  padding: 0.75rem 1rem;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #e9ecef;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  padding: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.detail-label {
  color: #666;
  font-size: 0.9rem;
}

.detail-value {
  font-weight: 600;
  color: #333;
}

/* 加载和错误状态 */
.loading-state,
.error-state {
  text-align: center;
  padding: 2rem;
}

.error-text {
  color: #e74c3c;
}

/* 页脚样式 */
.footer {
  background: #333;
  color: white;
  text-align: center;
  padding: 1.5rem;
  margin-top: auto;
}

.footer p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
  }
  
  .section-title {
    font-size: 1.3rem;
  }
  
  .feature-list {
    grid-template-columns: 1fr;
  }
  
  .market-card {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>