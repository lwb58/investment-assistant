<template>
  <div class="stock-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载股票数据...</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <p class="error-text">{{ error }}</p>
      <button class="btn primary retry-btn" @click="retryLoad">重试</button>
    </div>
    
    <!-- 正常内容 -->
    <template v-else>
      <!-- 股票概览卡片 -->
      <div class="overview-card card mb-6">
        <div class="overview-header">
          <div class="header-left flex items-center">
            <button class="btn-icon-round" @click="goBack" title="返回">
              ←
            </button>
            <div class="stock-info">
              <h1 class="stock-title">{{ stockInfo.name }}</h1>
              <div class="stock-code">{{ stockInfo.code }}</div>
            </div>
          </div>
          <div class="header-right">
            <div class="price-display">
              <div class="current-price">{{ formatPrice(stockInfo.price) }}</div>
              <div 
                :class="['price-change', 'inline-flex items-center px-3 py-1 rounded-full', 
                  stockInfo.changeRate > 0 ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600']"
              >
                <span :class="['change-icon mr-1', stockInfo.changeRate > 0 ? 'up' : 'down']">
                  {{ stockInfo.changeRate > 0 ? '↗️' : '↘️' }}
                </span>
                {{ stockInfo.changeRate > 0 ? '+' : '' }}{{ stockInfo.changeRate }}%
              </div>
            </div>
          </div>
        </div>
        
        <!-- 快捷指标 -->
        <div class="quick-metrics grid grid-cols-4 gap-4">
          <div class="metric-item">
            <div class="metric-label">行业</div>
            <div class="metric-value industry">{{ stockInfo.industry || '--' }}</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">总市值</div>
            <div class="metric-value">{{ formatNumber(stockInfo.marketCap) }}亿</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">市盈率</div>
            <div class="metric-value">{{ currentFinancialData.pe || '--' }}</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">净资产收益率</div>
            <div class="metric-value">{{ currentFinancialData.roe || '--' }}%</div>
          </div>
        </div>
      </div>

      <!-- 主内容区域 -->
      <div class="detail-content">
        <!-- 基本信息卡片 -->
        <div class="card mb-6">
          <div class="card-header">
            <h3 class="card-title">基本信息</h3>
          </div>
          <div class="card-body">
            <div class="info-grid grid grid-cols-2 gap-6">
              <div class="info-item">
                <div class="info-label">公司全称</div>
                <div class="info-value">{{ stockInfo.companyName || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">所属行业</div>
                <div class="info-value">{{ stockInfo.industry || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">上市日期</div>
                <div class="info-value">{{ stockInfo.listDate || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">总股本</div>
                <div class="info-value">{{ formatNumber(stockInfo.totalShares) }}亿股</div>
              </div>
              <div class="info-item">
                <div class="info-label">流通股本</div>
                <div class="info-value">{{ formatNumber(stockInfo.floatShares) }}亿股</div>
              </div>
              <div class="info-item">
                <div class="info-label">总市值</div>
                <div class="info-value">{{ formatNumber(stockInfo.marketCap) }}亿元</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 财务数据卡片 -->
        <div class="card mb-6">
          <div class="card-header">
            <h3 class="card-title">财务数据</h3>
          </div>
          <div class="card-body">
            <!-- 财务数据标签页 -->
            <div class="financial-tabs">
              <button 
                v-for="year in financialYears" 
                :key="year"
                class="tab-btn"
                :class="{ active: activeYear === year, disabled: financeLoading }"
                @click="activeYear = year"
                :disabled="financeLoading"
              >
                {{ year }}年
              </button>
            </div>
            
            <!-- 财务数据加载状态 -->
            <div v-if="financeLoading" class="finance-loading">
              <div class="loading-spinner small"></div>
              <span>加载中...</span>
            </div>
            
            <div v-else class="financial-content">
              <!-- 主要财务指标 -->
              <div class="financial-highlights grid grid-cols-4 gap-4 mb-6">
                <div class="highlight-item">
                  <div class="highlight-label">营业收入</div>
                  <div class="highlight-value">{{ formatNumber(currentFinancialData.revenue) }}亿元</div>
                  <div 
                    class="highlight-growth"
                    :class="parseFloat(currentFinancialData.revenueGrowth) > 0 ? 'positive' : parseFloat(currentFinancialData.revenueGrowth) < 0 ? 'negative' : ''"
                  >
                    {{ parseFloat(currentFinancialData.revenueGrowth) > 0 ? '+' : '' }}{{ currentFinancialData.revenueGrowth || '0.0' }}%
                  </div>
                </div>
                <div class="highlight-item">
                  <div class="highlight-label">净利润</div>
                  <div class="highlight-value">{{ formatNumber(currentFinancialData.netProfit) }}亿元</div>
                  <div 
                    class="highlight-growth"
                    :class="parseFloat(currentFinancialData.netProfitGrowth) > 0 ? 'positive' : parseFloat(currentFinancialData.netProfitGrowth) < 0 ? 'negative' : ''"
                  >
                    {{ parseFloat(currentFinancialData.netProfitGrowth) > 0 ? '+' : '' }}{{ currentFinancialData.netProfitGrowth || '0.0' }}%
                  </div>
                </div>
                <div class="highlight-item">
                  <div class="highlight-label">每股收益</div>
                  <div class="highlight-value">{{ currentFinancialData.eps || '0.00' }}元</div>
                </div>
                <div class="highlight-item">
                  <div class="highlight-label">净资产收益率</div>
                  <div class="highlight-value">{{ currentFinancialData.roe || '0.0' }}%</div>
                </div>
              </div>
              
              <!-- 详细财务数据 -->
              <div class="info-grid grid grid-cols-3 gap-6">
                <div class="info-item">
                  <div class="info-label">每股净资产</div>
                  <div class="info-value">{{ currentFinancialData.navps || '0.00' }}元</div>
                </div>
                <div class="info-item">
                  <div class="info-label">市盈率（TTM）</div>
                  <div class="info-value">{{ currentFinancialData.pe || '0.0' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">市净率</div>
                  <div class="info-value">{{ currentFinancialData.pb || '0.0' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">毛利率</div>
                  <div class="info-value">{{ currentFinancialData.grossMargin || '0.0' }}%</div>
                </div>
                <div class="info-item">
                  <div class="info-label">净利率</div>
                  <div class="info-value">{{ currentFinancialData.netMargin || '0.0' }}%</div>
                </div>
                <div class="info-item">
                  <div class="info-label">负债率</div>
                  <div class="info-value">{{ currentFinancialData.debtRatio || '0.0' }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 股东信息卡片 -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">十大股东</h3>
          </div>
          <div class="card-body">
            <div v-if="stockInfo.topShareholders && stockInfo.topShareholders.length > 0" class="shareholder-list">
              <div 
                class="shareholder-item" 
                v-for="(holder, index) in stockInfo.topShareholders" 
                :key="index"
              >
                <div class="shareholder-rank">
                  <span class="rank-number">{{ index + 1 }}</span>
                </div>
                <div class="shareholder-details">
                  <div class="holder-name">{{ holder.name }}</div>
                  <div class="holder-type">{{ holder.type }}</div>
                </div>
                <div class="shareholder-percentage">
                  <div class="percent-value">{{ holder.percentage }}%</div>
                  <div class="progress-container">
                    <div 
                      class="progress-bar" 
                      :style="{ width: holder.percentage + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <div class="empty-icon">👥</div>
              <p class="empty-text">暂无股东信息</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '../api/apiService.js'

const route = useRoute()
const router = useRouter()

// 响应式状态
const stockInfo = ref({
  code: '',
  name: '',
  price: '0.00',
  changeRate: 0,
  industry: '',
  companyName: '',
  listDate: '',
  totalShares: '0',
  floatShares: '0',
  marketCap: '0',
  topShareholders: []
})

const activeYear = ref('2024')
const financialYears = ref(['2024', '2023', '2022'])
const financialData = ref({
  '2024': {
    revenue: '0.00',
    revenueGrowth: '0.0',
    netProfit: '0.00',
    netProfitGrowth: '0.0',
    eps: '0.00',
    navps: '0.00',
    roe: '0.0',
    pe: '0.0',
    pb: '0.0',
    grossMargin: '0.0',
    netMargin: '0.0',
    debtRatio: '0.0'
  }
})

// 加载状态
const loading = ref(false)
const financeLoading = ref(false)
const error = ref(null)

// 当前年份的财务数据
const currentFinancialData = computed(() => {
  return financialData.value[activeYear.value] || financialData.value['2024']
})

// 获取股票代码
const stockCode = computed(() => route.params.code)

// 监听路由参数变化
watch(stockCode, (newCode) => {
  if (newCode) {
    fetchStockData()
  }
})

// 监听年份变化
watch(activeYear, (newYear) => {
  fetchFinancialData(newYear)
})

// 返回上一页
const goBack = () => {
  router.back()
}

// 获取股票详细信息
const fetchStockData = async () => {
  if (!stockCode.value) {
    error.value = '未找到股票代码'
    loading.value = false
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    // apiService直接返回数据，不需要从data属性获取
    const data = await apiService.getStockDetail(stockCode.value)
    stockInfo.value = data || {
      code: stockCode.value,
      name: '未知股票',
      price: '0.00',
      changeRate: 0,
      industry: '未知',
      companyName: '未知公司',
      listDate: '--',
      totalShares: '0',
      floatShares: '0',
      marketCap: '0',
      topShareholders: []
    }
    // 初始化获取当前年份的财务数据
    fetchFinancialData(activeYear.value)
  } catch (err) {
    console.error('获取股票详细信息失败:', err)
    error.value = '加载股票信息失败，请稍后重试'
    
    // 使用默认数据作为fallback
    stockInfo.value = {
      code: stockCode.value,
      name: '未知股票',
      price: '0.00',
      changeRate: 0,
      industry: '未知',
      companyName: '未知公司',
      listDate: '--',
      totalShares: '0',
      floatShares: '0',
      marketCap: '0',
      topShareholders: []
    }
  } finally {
    loading.value = false
  }
}

// 获取财务数据
const fetchFinancialData = async (year) => {
  financeLoading.value = true
  
  try {
    // apiService直接返回数据，不需要从data属性获取
    const data = await apiService.getStockFinancial(stockCode.value, year)
    financialData.value[year] = data || {
      revenue: '0.00',
      revenueGrowth: '0.0',
      netProfit: '0.00',
      netProfitGrowth: '0.0',
      eps: '0.00',
      navps: '0.00',
      roe: '0.0',
      pe: '0.0',
      pb: '0.0',
      grossMargin: '0.0',
      netMargin: '0.0',
      debtRatio: '0.0'
    }
  } catch (err) {
    console.error(`获取${year}年财务数据失败:`, err)
    
    // 如果获取失败，使用默认值
    if (!financialData.value[year]) {
      financialData.value[year] = {
        revenue: '0.00',
        revenueGrowth: '0.0',
        netProfit: '0.00',
        netProfitGrowth: '0.0',
        eps: '0.00',
        navps: '0.00',
        roe: '0.0',
        pe: '0.0',
        pb: '0.0',
        grossMargin: '0.0',
        netMargin: '0.0',
        debtRatio: '0.0'
      }
    }
  } finally {
    financeLoading.value = false
  }
}

// 重试加载
const retryLoad = () => {
  loading.value = true;
  error.value = null;
  fetchStockData();
}

// 格式化价格显示 - 增强版本，支持数字和字符串输入
const formatPrice = (price) => {
  if (typeof price === 'undefined' || price === null) return '--';
  const numPrice = parseFloat(price);
  return isNaN(numPrice) ? '--' : numPrice.toFixed(2);
}

// 格式化数字显示 - 增强版本，支持数字和字符串输入，更好的错误处理
const formatNumber = (num) => {
  if (typeof num === 'undefined' || num === null) return '--';
  const number = parseFloat(num);
  if (isNaN(number)) return '--';
  return number.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// 初始化数据
onMounted(() => {
  fetchStockData()
})
</script>

<style scoped>
/* 基础容器样式 */
.stock-detail-container {
  padding: var(--spacing-lg);
  min-height: calc(100vh - 64px);
  overflow-y: auto;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 500px;
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-lg);
  text-align: center;
  transition: all var(--transition-fast);
  border: 1px solid var(--border-color);
}

.loading-container:hover,
.error-container:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--bg-tertiary);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-lg);
}

.loading-spinner.small {
  width: 24px;
  height: 24px;
  border-width: 3px;
  margin-right: var(--spacing-sm);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text,
.error-text {
  color: var(--text-secondary);
  font-size: var(--text-base);
  margin-bottom: var(--spacing-md);
  line-height: 1.5;
}

.error-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-lg);
  opacity: 0.8;
}

/* 按钮样式 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--border-radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
  text-decoration: none;
  white-space: nowrap;
}

.btn.primary {
  background-color: var(--primary-color);
  color: white;
}

.btn.primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.retry-btn {
  padding: var(--spacing-sm) var(--spacing-xl);
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.retry-btn:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* 页面头部样式 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
  border: 1px solid var(--border-color);
  gap: var(--spacing-lg);
}

.page-header:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex: 1;
}

.back-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-tertiary);
  border-radius: 50%;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: var(--text-lg);
}

.back-icon:hover {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  transform: scale(1.05);
}

.stock-title {
  margin: 0;
  font-size: var(--text-2xl);
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.2;
}

.header-right {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.price-info {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-md);
  background-color: var(--bg-tertiary);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
}

.current-price {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}

.price-change {
  font-size: var(--text-lg);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 9999px;
  font-size: var(--text-sm);
}

.price-change.up {
  color: var(--error-color);
  background-color: rgba(255, 59, 48, 0.1);
}

.price-change.down {
  color: var(--success-color);
  background-color: rgba(52, 199, 89, 0.1);
}

/* 主内容区域 */
.detail-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--spacing-xl);
}

/* 卡片样式 */
.card {
  background: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-lg);
  overflow: hidden;
  transition: all var(--transition-fast);
  border: 1px solid var(--border-color);
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-color);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.card-title::before {
  content: '';
  width: 4px;
  height: 20px;
  background-color: var(--primary-color);
  border-radius: 2px;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  padding: var(--spacing-md);
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
}

.info-item:hover {
  transform: translateY(-1px);
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
}

.info-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.info-value {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
  font-variant-numeric: tabular-nums;
}

.info-value.positive {
  color: var(--error-color);
}

.info-value.negative {
  color: var(--success-color);
}

/* 财务数据标签页 */
.financial-tabs {
  display: flex;
  border-bottom: 2px solid var(--border-color);
  margin-bottom: var(--spacing-lg);
  overflow-x: auto;
  scrollbar-width: none;
}

.financial-tabs::-webkit-scrollbar {
  display: none;
}

.tab-btn {
  padding: var(--spacing-sm) var(--spacing-xl);
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: var(--text-base);
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
  white-space: nowrap;
  flex-shrink: 0;
  position: relative;
}

.tab-btn:hover:not(.disabled) {
  color: var(--primary-color);
  background-color: var(--bg-tertiary);
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
  border-radius: 2px 2px 0 0;
}

.tab-btn.disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* 财务数据加载状态 */
.finance-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius-md);
  border: 1px dashed var(--border-color);
}

/* 股东信息列表 */
.shareholder-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.shareholder-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
  border: 1px solid var(--border-color);
  gap: var(--spacing-md);
}

.shareholder-item:hover {
  background-color: var(--bg-secondary);
  border-color: var(--primary-color);
  transform: translateX(3px);
  box-shadow: var(--shadow-sm);
}

.shareholder-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: var(--primary-color);
  color: white;
  border-radius: 6px;
  margin-right: var(--spacing-sm);
  flex-shrink: 0;
  font-weight: 600;
}

.rank-number {
  font-size: var(--text-xs);
  font-weight: 600;
}

.shareholder-details {
  flex: 1;
  min-width: 0;
}

.holder-name {
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
  font-size: var(--text-sm);
}

.holder-type {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  background-color: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 3px;
  display: inline-block;
}

.shareholder-percentage {
  text-align: right;
  flex-shrink: 0;
  margin-left: var(--spacing-md);
  min-width: 120px;
}

.percent-value {
  font-weight: 600;
  color: var(--primary-color);
  font-size: var(--text-lg);
  margin-bottom: 6px;
  font-variant-numeric: tabular-nums;
}

.progress-container {
  width: 100%;
  height: 8px;
  background-color: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  transition: width var(--transition-fast);
  border-radius: 4px;
  position: relative;
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* 空数据状态 */
.empty-data {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-tertiary);
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius-md);
  border: 1px dashed var(--border-color);
  margin-top: var(--spacing-lg);
  transition: all var(--transition-fast);
}

.empty-data:hover {
  border-color: var(--primary-color);
  background-color: var(--bg-secondary);
}

.empty-data::before {
  content: '📊';
  display: block;
  font-size: 48px;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .detail-content {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-lg);
  }
  
  .header-right {
    width: 100%;
  }
  
  .price-info {
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 768px) {
  .stock-detail-container {
    padding: var(--spacing-md);
  }
  
  .card {
    padding: var(--spacing-md);
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  
  .stock-title {
    font-size: var(--text-xl);
  }
  
  .current-price {
    font-size: var(--text-xl);
  }
  
  .loading-container,
  .error-container {
    height: 300px;
    padding: var(--spacing-md);
  }
  
  .financial-tabs {
    justify-content: flex-start;
  }
  
  .shareholder-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .shareholder-percentage {
    width: 100%;
    margin-left: 0;
    text-align: left;
  }
  
  .progress-container {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .stock-detail-container {
    padding: var(--spacing-sm);
  }
  
  .page-header {
    padding: var(--spacing-sm);
  }
  
  .card {
    padding: var(--spacing-sm);
  }
  
  .back-icon {
    width: 32px;
    height: 32px;
  }
  
  .stock-title {
    font-size: var(--text-lg);
  }
  
  .tab-btn {
    padding: var(--spacing-sm) var(--spacing-md);
  }
}
</style>