<template>
  <div class="container mt-3">
    <!-- 页面标题 -->
    <div class="page-header mb-2">
      <h1 class="text-xl font-semibold">市场概览</h1>
      <p class="text-tertiary mt-1">更新时间：{{ marketOverview.date || '加载中...' }}</p>
    </div>

    <!-- 加载/错误状态 -->
    <div v-if="loading" class="loading-state flex flex-col items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      <p class="mt-4 text-tertiary">加载市场数据中...</p>
    </div>
    <div v-else-if="error" class="error-state bg-error bg-opacity-10 border border-error border-opacity-20 text-error p-4 rounded-base mb-2 flex items-center">
      <span class="inline-block w-6 h-6 rounded-full bg-error bg-opacity-10 text-error flex items-center justify-center mr-2 font-bold">!</span>
      {{ error }}
    </div>

    <!-- 核心数据卡片区（复用全局 card 类） -->
    <div v-else class="stats-grid grid gap-2 mb-3">
      <!-- 上证指数 -->
      <div class="card hover:shadow-medium transition-all">
        <div class="flex justify-between items-start mb-3">
          <div>
            <p class="text-tertiary text-sm">上证指数</p>
            <h3 class="text-xl font-bold mt-1">{{ marketOverview.shIndex }}</h3>
          </div>
          <div class="w-10 h-10 rounded-full bg-primary bg-opacity-10 flex items-center justify-center text-primary">
            📈
          </div>
        </div>
        <div :class="['text-sm font-medium', marketOverview.shChangeRate > 0 ? 'text-error' : marketOverview.shChangeRate < 0 ? 'text-success' : 'text-tertiary']">
          <span :class="marketOverview.shChangeRate > 0 ? 'inline-block mr-1' : marketOverview.shChangeRate < 0 ? 'inline-block mr-1' : ''">
            {{ marketOverview.shChangeRate > 0 ? '⬆️' : marketOverview.shChangeRate < 0 ? '⬇️' : '' }}
          </span>
          {{ marketOverview.shChangeRate > 0 ? '+' : '' }}{{ marketOverview.shChangeRate }}%
          <span class="text-tertiary ml-2">({{ marketOverview.shChange > 0 ? '+' : '' }}{{ marketOverview.shChange }})</span>
        </div>
      </div>

      <!-- 深证成指 -->
      <div class="card hover:shadow-medium transition-all">
        <div class="flex justify-between items-start mb-3">
          <div>
            <p class="text-tertiary text-sm">深证成指</p>
            <h3 class="text-xl font-bold mt-1">{{ marketOverview.szIndex }}</h3>
          </div>
          <div class="w-10 h-10 rounded-full bg-primary bg-opacity-10 flex items-center justify-center text-primary">
            📊
          </div>
        </div>
        <div :class="['text-sm font-medium', marketOverview.szChangeRate > 0 ? 'text-error' : marketOverview.szChangeRate < 0 ? 'text-success' : 'text-tertiary']">
          <span :class="marketOverview.szChangeRate > 0 ? 'inline-block mr-1' : marketOverview.szChangeRate < 0 ? 'inline-block mr-1' : ''">
            {{ marketOverview.szChangeRate > 0 ? '⬆️' : marketOverview.szChangeRate < 0 ? '⬇️' : '' }}
          </span>
          {{ marketOverview.szChangeRate > 0 ? '+' : '' }}{{ marketOverview.szChangeRate }}%
          <span class="text-tertiary ml-2">({{ marketOverview.szChange > 0 ? '+' : '' }}{{ marketOverview.szChange }})</span>
        </div>
      </div>

      <!-- 创业板指 -->
      <div class="card hover:shadow-medium transition-all">
        <div class="flex justify-between items-start mb-3">
          <div>
            <p class="text-tertiary text-sm">创业板指</p>
            <h3 class="text-xl font-bold mt-1">{{ marketOverview.cyIndex }}</h3>
          </div>
          <div class="w-10 h-10 rounded-full bg-primary bg-opacity-10 flex items-center justify-center text-primary">
            🚀
          </div>
        </div>
        <div :class="['text-sm font-medium', marketOverview.cyChangeRate > 0 ? 'text-error' : marketOverview.cyChangeRate < 0 ? 'text-success' : 'text-tertiary']">
          <span :class="marketOverview.cyChangeRate > 0 ? 'inline-block mr-1' : marketOverview.cyChangeRate < 0 ? 'inline-block mr-1' : ''">
            {{ marketOverview.cyChangeRate > 0 ? '⬆️' : marketOverview.cyChangeRate < 0 ? '⬇️' : '' }}
          </span>
          {{ marketOverview.cyChangeRate > 0 ? '+' : '' }}{{ marketOverview.cyChangeRate }}%
          <span class="text-tertiary ml-2">({{ marketOverview.cyChange > 0 ? '+' : '' }}{{ marketOverview.cyChange }})</span>
        </div>
      </div>

      <!-- 涨幅中位数 -->
      <div class="card hover:shadow-medium transition-all">
        <div class="flex justify-between items-start mb-3">
          <div>
            <p class="text-tertiary text-sm">涨幅中位数</p>
            <h3 class="text-xl font-bold mt-1">{{ marketOverview.medianChangeRate }}%</h3>
          </div>
          <div class="w-10 h-10 rounded-full bg-primary bg-opacity-10 flex items-center justify-center text-primary">
            ⚖️
          </div>
        </div>
        <div :class="['text-sm font-medium', marketOverview.medianChangeRate > 0 ? 'text-error' : marketOverview.medianChangeRate < 0 ? 'text-success' : 'text-tertiary']">
          <span :class="marketOverview.medianChangeRate > 0 ? 'inline-block mr-1' : marketOverview.medianChangeRate < 0 ? 'inline-block mr-1' : ''">
            {{ marketOverview.medianChangeRate > 0 ? '⬆️' : marketOverview.medianChangeRate < 0 ? '⬇️' : '' }}
          </span>
          市场整体情绪
        </div>
      </div>
    </div>

    <!-- 市场统计+行业排行区（添加专属类） -->
    <div class="market-stats-grid grid gap-2">
      <!-- 市场统计（复用 card 类） -->
      <div class="card lg:col-span-1">
        <h2 class="card-title flex items-center">
          <span class="inline-block mr-2 text-primary">📊</span>
          市场统计
        </h2>
        <div class="card-body space-y-4">
          <!-- 涨跌平家数 -->
          <div class="space-y-2">
            <p class="text-tertiary text-sm">涨跌分布</p>
            <div class="grid grid-cols-3 gap-2">
              <div class="bg-error bg-opacity-5 rounded-base p-3 text-center">
                <p class="text-error font-bold text-xl">{{ marketOverview.upStocks }}</p>
                <p class="text-error text-opacity-80 text-xs mt-1">上涨</p>
              </div>
              <div class="bg-success bg-opacity-5 rounded-base p-3 text-center">
                <p class="text-success font-bold text-xl">{{ marketOverview.downStocks }}</p>
                <p class="text-success text-opacity-80 text-xs mt-1">下跌</p>
              </div>
              <div class="bg-text-tertiary bg-opacity-5 rounded-base p-3 text-center">
                <p class="text-tertiary font-bold text-xl">{{ marketOverview.flatStocks }}</p>
                <p class="text-tertiary text-opacity-80 text-xs mt-1">平盘</p>
              </div>
            </div>
          </div>

          <!-- 成交量+成交额 -->
          <div class="space-y-2">
            <p class="text-tertiary text-sm">量能数据</p>
            <div class="grid grid-cols-2 gap-2">
              <div class="bg-primary bg-opacity-5 rounded-base p-3">
                <p class="text-primary font-bold">{{ marketOverview.totalVolume }} 亿手</p>
                <p class="text-primary text-opacity-80 text-xs mt-1">总成交量</p>
              </div>
              <div class="bg-primary bg-opacity-5 rounded-base p-3">
                <p class="text-primary font-bold">{{ marketOverview.totalAmount }} 亿元</p>
                <p class="text-primary text-opacity-80 text-xs mt-1">总成交额</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 行业涨幅榜 -->
      <div class="card lg:col-span-1">
        <h2 class="card-title flex items-center">
          <span class="inline-block mr-2 text-error">⬆️</span>
          行业涨幅榜 TOP5
        </h2>
        <div class="card-body space-y-3">
          <div v-for="(item, index) in upIndustries" :key="index" class="flex items-center justify-between p-2 hover:bg-tertiary rounded-base transition-colors">
            <div class="flex items-center">
              <span class="w-6 h-6 rounded-full bg-error bg-opacity-10 text-error flex items-center justify-center text-xs font-bold mr-3">
                {{ index + 1 }}
              </span>
              <span class="text-text-primary">{{ item.industry }}</span>
            </div>
            <span class="text-error font-medium">+{{ item.changeRate }}%</span>
          </div>
          <div v-if="upIndustries.length === 0" class="text-center text-tertiary text-sm py-3">
            暂无数据
          </div>
        </div>
      </div>

      <!-- 行业跌幅榜 -->
      <div class="card lg:col-span-1">
        <h2 class="card-title flex items-center">
          <span class="inline-block mr-2 text-success">⬇️</span>
          行业跌幅榜 TOP5
        </h2>
        <div class="card-body space-y-3">
          <div v-for="(item, index) in downIndustries" :key="index" class="flex items-center justify-between p-2 hover:bg-tertiary rounded-base transition-colors">
            <div class="flex items-center">
              <span class="w-6 h-6 rounded-full bg-success bg-opacity-10 text-success flex items-center justify-center text-xs font-bold mr-3">
                {{ index + 1 }}
              </span>
              <span class="text-text-primary">{{ item.industry }}</span>
            </div>
            <span class="text-success font-medium">{{ item.changeRate }}%</span>
          </div>
          <div v-if="downIndustries.length === 0" class="text-center text-tertiary text-sm py-3">
            暂无数据
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import apiService from '../api/apiService.js'

// 状态管理
const marketOverview = ref({
  date: '',
  shIndex: '0.00',
  shChange: 0.00,
  shChangeRate: 0.00,
  szIndex: '0.00',
  szChange: 0.00,
  szChangeRate: 0.00,
  cyIndex: '0.00',
  cyChange: 0.00,
  cyChangeRate: 0.00,
  totalVolume: '0.00',
  totalAmount: '0.00',
  medianChangeRate: 0.00,
  upStocks: 0,
  downStocks: 0,
  flatStocks: 0,
  marketHotspots: []
})
const loading = ref(true)
const error = ref(null)

// 拆分涨幅/跌幅行业（添加数据容错）
const upIndustries = computed(() => {
  return marketOverview.value.marketHotspots
    .filter(item => item && item.type === 'up' && item.industry && typeof item.changeRate === 'number')
    .slice(0, 5)
})
const downIndustries = computed(() => {
  return marketOverview.value.marketHotspots
    .filter(item => item && item.type === 'down' && item.industry && typeof item.changeRate === 'number')
    .slice(0, 5)
})

// 获取市场概览数据
const fetchMarketOverview = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await apiService.getMarketOverview()
    marketOverview.value = { ...marketOverview.value, ...data }
    // 调试用：打印后端返回数据
    console.log('市场概览原始数据：', data)
    console.log('跌幅行业数据：', downIndustries.value)
  } catch (err) {
    error.value = '加载市场数据失败：' + (err.message || '未知错误')
    console.error('市场数据加载失败：', err)
  } finally {
    loading.value = false
  }
}

// 初始化加载 + 定时刷新（5分钟）
onMounted(() => {
  fetchMarketOverview()
  setInterval(fetchMarketOverview, 5 * 60 * 1000)
})
</script>

<style scoped>
/* 组件内私有样式 */
.loading-state {
  min-height: 300px;
}

/* 卡片基础样式 */
.card {
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-base);
  padding: var(--spacing-md);
  transition: var(--transition-base);
  min-width: 0; /* 解决网格布局内容溢出问题 */
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

.card-body {
  padding-top: 0;
}

/* 响应式布局 */
/* 小屏（手机，≤768px）：1列堆叠 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .market-stats-grid {
    grid-template-columns: 1fr;
  }
}

/* 中屏（平板，769px-1023px）：2列布局 */
@media (min-width: 769px) and (max-width: 1023px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .market-stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  .market-stats-grid .card:nth-child(2),
  .market-stats-grid .card:nth-child(3) {
    grid-column: 2 / 3;
  }
}

/* 大屏（电脑，≥1024px）：3列并列 */
@media (min-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  .market-stats-grid {
    grid-template-columns: 1fr 1fr 1fr;
    gap: var(--spacing-md);
  }
  .market-stats-grid .card {
    width: 100%;
    box-sizing: border-box;
  }
}
</style>