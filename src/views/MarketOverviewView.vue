<template>
  <div class="market-overview-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">
        <span class="title-icon">📈</span>
        今日大盘情况
      </h2>
      <div class="header-actions">
        <button 
          class="btn primary"
          @click="refreshData"
          :disabled="loading"
        >
          <span v-if="loading" class="loading-spinner small"></span>
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      {{ error }}
      <button class="error-close" @click="error = null" aria-label="关闭错误提示">×</button>
    </div>

    <!-- 主要内容区域 -->
    <div class="content-section">
      <!-- 大盘指数卡片 -->
      <div class="index-cards grid grid-cols-3 gap-lg">
        <div v-for="index in marketIndices" :key="index.code" class="index-card">
          <div class="index-header">
            <h3 class="index-name">{{ index.name }}</h3>
            <span class="index-code">{{ index.code }}</span>
          </div>
          <div class="index-price">
            <span class="price-value">{{ formatNumber(index.price) }}</span>
            <span 
              class="change-rate" 
              :class="{
                'positive': index.changeRate > 0,
                'negative': index.changeRate < 0
              }"
            >
              <span class="change-icon">{{ index.changeRate > 0 ? '↗' : index.changeRate < 0 ? '↘' : '→' }}</span>
              <span>{{ index.changeRate > 0 ? '+' : '' }}{{ index.changeRate }}%</span>
            </span>
          </div>
          <div class="index-change">
            <span 
              class="change-value" 
              :class="{
                'positive': index.changeAmount > 0,
                'negative': index.changeAmount < 0
              }"
            >
              {{ index.changeAmount > 0 ? '+' : '' }}{{ formatNumber(index.changeAmount) }}
            </span>
          </div>
          <div class="index-vol">
            <span class="vol-label">成交量：</span>
            <span class="vol-value">{{ formatVolume(index.volume) }}</span>
          </div>
        </div>
      </div>

      <!-- 市场概况 -->
      <div class="market-summary">
        <h3 class="section-title">市场概况</h3>
        <div class="summary-stats grid grid-cols-4 gap-md">
          <div class="stat-item">
            <div class="stat-label">上涨家数</div>
            <div class="stat-value positive">{{ marketSummary.upCount }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">下跌家数</div>
            <div class="stat-value negative">{{ marketSummary.downCount }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">平盘家数</div>
            <div class="stat-value">{{ marketSummary.flatCount }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">市场换手率</div>
            <div class="stat-value">{{ marketSummary.turnoverRate }}%</div>
          </div>
        </div>
      </div>

      <!-- 行业板块涨幅榜 -->
      <div class="industry-sectors">
        <h3 class="section-title">行业板块涨跌幅</h3>
        <div class="sector-tabs">
          <button 
            v-for="tab in sectorTabs" 
            :key="tab.value"
            :class="['tab-btn', { active: activeSectorTab === tab.value }]"
            @click="activeSectorTab = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>
        <div class="sector-table-container">
          <table class="sector-table">
            <thead>
              <tr>
                <th>排名</th>
                <th>板块名称</th>
                <th>涨跌幅</th>
                <th>领涨股</th>
                <th>涨跌幅</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(sector, index) in filteredSectors" :key="sector.name">
                <td class="rank">{{ index + 1 }}</td>
                <td class="sector-name">{{ sector.name }}</td>
                <td 
                  class="sector-change-rate" 
                  :class="{
                    'positive': sector.changeRate > 0,
                    'negative': sector.changeRate < 0
                  }"
                >
                  {{ sector.changeRate > 0 ? '+' : '' }}{{ sector.changeRate }}%
                </td>
                <td class="leading-stock">{{ sector.leadingStock }}</td>
                <td 
                  class="leading-stock-change" 
                  :class="{
                    'positive': sector.leadingStockChange > 0,
                    'negative': sector.leadingStockChange < 0
                  }"
                >
                  {{ sector.leadingStockChange > 0 ? '+' : '' }}{{ sector.leadingStockChange }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import apiService from '../api/apiService.js'

// 状态管理
const loading = ref(false)
const error = ref(null)
const marketIndices = ref([])
const marketSummary = ref({
  upCount: 0,
  downCount: 0,
  flatCount: 0,
  turnoverRate: 0
})
const industrySectors = ref([])
const activeSectorTab = ref('up') // 'up' 涨幅榜, 'down' 跌幅榜

// 板块标签
const sectorTabs = [
  { label: '涨幅榜', value: 'up' },
  { label: '跌幅榜', value: 'down' }
]

// 根据当前选中的标签过滤行业板块
const filteredSectors = computed(() => {
  const sorted = [...industrySectors.value].sort((a, b) => {
    if (activeSectorTab.value === 'up') {
      return b.changeRate - a.changeRate // 涨幅榜，降序
    } else {
      return a.changeRate - b.changeRate // 跌幅榜，升序
    }
  })
  return sorted.slice(0, 10) // 只显示前10名
})

// 获取大盘数据
const fetchMarketData = async () => {
  loading.value = true
  error.value = null
  try {
    // 调用后端接口获取大盘数据
    const data = await apiService.getMarketOverview()
    
    // 根据API返回的数据结构更新状态
    marketIndices.value = [
      { 
        code: '000001', 
        name: '上证指数', 
        price: parseFloat(data.shIndex), 
        changeRate: parseFloat(data.shChangeRate), 
        changeAmount: parseFloat(data.shChange), 
        volume: parseFloat(data.totalVolume) * 100000000
      },
      { 
        code: '399001', 
        name: '深证成指', 
        price: parseFloat(data.szIndex), 
        changeRate: parseFloat(data.szChangeRate), 
        changeAmount: parseFloat(data.szChange), 
        volume: parseFloat(data.totalVolume) * 100000000 * 1.4
      },
      { 
        code: '399006', 
        name: '创业板指', 
        price: parseFloat(data.cyIndex), 
        changeRate: parseFloat(data.cyChangeRate), 
        changeAmount: parseFloat(data.cyChange), 
        volume: parseFloat(data.totalVolume) * 100000000 * 0.8
      }
    ]
    
    marketSummary.value = {
      upCount: data.upStocks,
      downCount: data.downStocks,
      flatCount: data.flatStocks,
      turnoverRate: 1.28 // 模拟换手率
    }
    
    // 如果返回了热点板块，使用返回的数据，否则使用模拟数据
    if (data.marketHotspots && data.marketHotspots.length > 0) {
      industrySectors.value = data.marketHotspots.map(hotspot => ({
        name: hotspot.industry,
        changeRate: hotspot.changeRate,
        leadingStock: '龙头股', // 模拟数据
        leadingStockChange: hotspot.changeRate * 1.1 // 模拟数据
      }))
    } else {
      // 如果没有热点板块数据，使用默认模拟数据
      setMockData()
    }
  } catch (err) {
    error.value = '获取大盘数据失败，请稍后重试'
    console.error('获取大盘数据失败:', err)
    // 设置默认模拟数据，避免页面空白
    setMockData()
  } finally {
    loading.value = false
  }
}

// 设置模拟数据
const setMockData = () => {
  marketIndices.value = [
    { code: '000001', name: '上证指数', price: 3250.68, changeRate: 0.82, changeAmount: 26.41, volume: 286500000000 },
    { code: '399001', name: '深证成指', price: 10982.45, changeRate: 1.23, changeAmount: 133.76, volume: 389200000000 },
    { code: '399006', name: '创业板指', price: 2285.36, changeRate: 1.56, changeAmount: 35.21, volume: 198600000000 }
  ]
  
  marketSummary.value = {
    upCount: 2345,
    downCount: 1234,
    flatCount: 456,
    turnoverRate: 1.28
  }
  
  industrySectors.value = [
    { name: '新能源汽车', changeRate: 3.56, leadingStock: '比亚迪', leadingStockChange: 4.23 },
    { name: '半导体', changeRate: 2.89, leadingStock: '中芯国际', leadingStockChange: 3.78 },
    { name: '医疗健康', changeRate: 1.98, leadingStock: '恒瑞医药', leadingStockChange: 2.15 },
    { name: '人工智能', changeRate: 2.34, leadingStock: '科大讯飞', leadingStockChange: 3.12 },
    { name: '光伏设备', changeRate: 2.11, leadingStock: '隆基绿能', leadingStockChange: 2.89 },
    { name: '消费电子', changeRate: -0.56, leadingStock: '立讯精密', leadingStockChange: -0.34 },
    { name: '房地产', changeRate: -1.23, leadingStock: '万科A', leadingStockChange: -1.56 },
    { name: '银行', changeRate: -0.89, leadingStock: '招商银行', leadingStockChange: -0.78 },
    { name: '保险', changeRate: -1.05, leadingStock: '中国平安', leadingStockChange: -1.12 },
    { name: '证券', changeRate: -0.76, leadingStock: '中信证券', leadingStockChange: -0.98 },
    { name: '食品饮料', changeRate: 0.67, leadingStock: '贵州茅台', leadingStockChange: 0.45 },
    { name: '国防军工', changeRate: 1.45, leadingStock: '中航沈飞', leadingStockChange: 2.34 }
  ]
}

// 刷新数据
const refreshData = () => {
  fetchMarketData()
}

// 格式化数字
const formatNumber = (num) => {
  if (typeof num !== 'number') return '0'
  return num.toFixed(2)
}

// 格式化成交量
const formatVolume = (volume) => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

// 页面加载时获取数据
onMounted(() => {
  fetchMarketData()
})
</script>

<style scoped>
.market-overview-container {
  padding: var(--space-lg);
  height: calc(100vh - 64px);
  overflow-y: auto;
  background-color: var(--bg-secondary);
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-light);
}

.page-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.title-icon {
  font-size: 24px;
}

/* 错误消息 */
.error-message {
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: var(--border-radius-md);
  padding: var(--space-md);
  margin-bottom: var(--space-lg);
  display: flex;
  align-items: center;
  gap: var(--space-md);
  color: var(--danger-color);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.error-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.error-close {
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  font-size: 16px;
  padding: var(--space-xs);
  border-radius: 50%;
  margin-left: auto;
}

.error-close:hover {
  background-color: rgba(245, 34, 45, 0.1);
}

/* 网格布局 */
.grid {
  display: grid;
}

.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-lg);
}

.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
}

/* 大盘指数卡片 */
.index-cards {
  margin-bottom: var(--space-xl);
}

.index-card {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow-sm);
  transition: var(--transition-base);
  border: 1px solid var(--border-color);
}

.index-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.index-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.index-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.index-code {
  font-size: 12px;
  color: var(--text-secondary);
  background-color: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 12px;
}

.index-price {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: var(--space-sm);
}

.price-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.change-rate {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
}

.change-rate.positive {
  color: var(--danger-color);
  background-color: rgba(245, 34, 45, 0.08);
}

.change-rate.negative {
  color: var(--success-color);
  background-color: rgba(82, 196, 26, 0.08);
}

.change-icon {
  font-size: 16px;
}

.index-change {
  margin-bottom: var(--space-sm);
}

.change-value {
  font-size: 14px;
  font-weight: 500;
}

.change-value.positive {
  color: var(--danger-color);
}

.change-value.negative {
  color: var(--success-color);
}

.index-vol {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 12px;
  color: var(--text-secondary);
}

.vol-label {
  color: var(--text-tertiary);
}

.vol-value {
  font-weight: 500;
}

/* 市场概况 */
.market-summary {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--space-lg);
  margin-bottom: var(--space-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--space-lg) 0;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-md);
}

.stat-item {
  background: var(--bg-secondary);
  border-radius: var(--border-radius-md);
  padding: var(--space-md);
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: var(--space-xs);
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-value.positive {
  color: var(--danger-color);
}

.stat-value.negative {
  color: var(--success-color);
}

/* 行业板块 */
.industry-sectors {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.sector-tabs {
  display: flex;
  margin-bottom: var(--space-lg);
  border-bottom: 2px solid var(--border-light);
}

.tab-btn {
  padding: var(--space-sm) var(--space-md);
  background: none;
  border: none;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-base);
  position: relative;
  margin-right: var(--space-lg);
}

.tab-btn:hover {
  color: var(--primary-color);
}

.tab-btn.active {
  color: var(--primary-color);
  font-weight: 600;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--primary-color);
}

/* 行业板块表格 */
.sector-table-container {
  overflow-x: auto;
}

.sector-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.sector-table th {
  background-color: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
  text-align: left;
  padding: var(--space-sm) var(--space-md);
  border-bottom: 2px solid var(--border-color);
}

.sector-table td {
  padding: var(--space-sm) var(--space-md);
  border-bottom: 1px solid var(--border-light);
}

.sector-table tbody tr:hover {
  background-color: var(--bg-secondary);
}

.rank {
  font-weight: 600;
  color: var(--text-secondary);
  width: 50px;
}

.sector-name {
  font-weight: 500;
  color: var(--text-primary);
}

.sector-change-rate,
.leading-stock-change {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.sector-change-rate.positive,
.leading-stock-change.positive {
  color: var(--danger-color);
}

.sector-change-rate.negative,
.leading-stock-change.negative {
  color: var(--success-color);
}

.leading-stock {
  color: var(--text-primary);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .grid-cols-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .market-overview-container {
    padding: var(--space-md);
    height: 100vh;
  }
  
  .grid-cols-3 {
    grid-template-columns: 1fr;
  }
  
  .summary-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-md);
  }
}
</style>