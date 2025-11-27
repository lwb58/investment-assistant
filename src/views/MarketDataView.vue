<template>
  <div class="market-data container">
    <h2>市场数据中心</h2>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载市场数据...</p>
    </div>
    
    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button @click="loadAllData">重新加载</button>
    </div>
    
    <!-- 数据内容 -->
    <div v-else>
      <!-- 市场指数概览 -->
      <div class="index-overview">
        <h3>主要指数</h3>
        <div class="index-cards">
          <div v-if="marketIndices.length === 0" class="empty-state">
            <p>暂无指数数据</p>
          </div>
          <div class="index-card" v-for="index in marketIndices" :key="index.code">
            <div class="index-header">
              <h4>{{ index.name }}</h4>
              <span class="code">{{ index.code }}</span>
            </div>
            <div class="index-price">{{ formatPrice(index.price) }}</div>
            <div class="index-change" :class="{ positive: index.change > 0, negative: index.change < 0 }">
              <span>{{ index.change > 0 ? '+' : '' }}{{ formatPrice(index.change) }}</span>
              <span class="change-percent">{{ index.changePercent > 0 ? '+' : '' }}{{ formatPercent(index.changePercent) }}</span>
            </div>
            <div class="index-vol">
              <span>成交额: {{ formatAmount(index.volume) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 市场热力图 -->
      <div class="heatmap-container">
        <h3>行业板块热力图</h3>
        <div class="heatmap-grid">
          <div v-if="sectorHeatmap.length === 0" class="empty-state">
            <p>暂无行业数据</p>
          </div>
          <div 
            v-for="sector in sectorHeatmap" 
            :key="sector.code"
            class="heatmap-item"
            :class="getSectorColorClass(sector.changePercent)"
            @click="showSectorDetail(sector)"
          >
            <div class="sector-name">{{ sector.name }}</div>
            <div class="sector-change">{{ sector.changePercent > 0 ? '+' : '' }}{{ formatPercent(sector.changePercent) }}</div>
          </div>
        </div>
      </div>
      
      <!-- 热点股票列表 -->
      <div class="hot-stocks">
        <h3>热点股票</h3>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="涨幅榜" name="up">
            <el-table :data="hotStocks.upStocks" stripe style="width: 100%">
            <el-table-column type="index" width="50" />
            <el-table-column prop="name" label="名称" width="100" />
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="price" label="现价" />
            <el-table-column prop="change" label="涨跌额" :formatter="formatTablePriceChange" />
            <el-table-column prop="changePercent" label="涨跌幅" :formatter="formatTablePercentChange" />
            <el-table-column prop="volume" label="成交量(万手)" :formatter="formatTableVolume" />
            <el-table-column prop="amount" label="成交额(万元)" :formatter="formatTableAmount" />
          </el-table>
          </el-tab-pane>
          <el-tab-pane label="跌幅榜" name="down">
            <el-table :data="hotStocks.downStocks" stripe style="width: 100%">
            <el-table-column type="index" width="50" />
            <el-table-column prop="name" label="名称" width="100" />
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="price" label="现价" />
            <el-table-column prop="change" label="涨跌额" :formatter="formatTablePriceChange" />
            <el-table-column prop="changePercent" label="涨跌幅" :formatter="formatTablePercentChange" />
            <el-table-column prop="volume" label="成交量(万手)" :formatter="formatTableVolume" />
            <el-table-column prop="amount" label="成交额(万元)" :formatter="formatTableAmount" />
          </el-table>
          </el-tab-pane>
          <el-tab-pane label="换手率榜" name="turnover">
            <el-table :data="hotStocks.turnoverStocks" stripe style="width: 100%">
            <el-table-column type="index" width="50" />
            <el-table-column prop="name" label="名称" width="100" />
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="price" label="现价" />
            <el-table-column prop="change" label="涨跌额" :formatter="formatTablePriceChange" />
            <el-table-column prop="changePercent" label="涨跌幅" :formatter="formatTablePercentChange" />
            <el-table-column prop="turnoverRate" label="换手率" :formatter="formatTableTurnoverRate" />
            <el-table-column prop="amount" label="成交额(万元)" :formatter="formatTableAmount" />
          </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <!-- 资金流向 -->
      <div class="capital-flow">
        <h3>市场资金流向</h3>
        <div class="flow-cards">
          <div class="flow-card">
            <h4>北向资金</h4>
            <div class="flow-value" :class="{ positive: capitalFlow.north > 0, negative: capitalFlow.north < 0 }">
              {{ capitalFlow.north > 0 ? '+' : '' }}{{ formatFlowAmount(capitalFlow.north) }}
            </div>
          </div>
          <div class="flow-card">
            <h4>南向资金</h4>
            <div class="flow-value" :class="{ positive: capitalFlow.south > 0, negative: capitalFlow.south < 0 }">
              {{ capitalFlow.south > 0 ? '+' : '' }}{{ formatFlowAmount(capitalFlow.south) }}
            </div>
          </div>
          <div class="flow-card">
            <h4>沪港通</h4>
            <div class="flow-value" :class="{ positive: capitalFlow.shanghai > 0, negative: capitalFlow.shanghai < 0 }">
              {{ capitalFlow.shanghai > 0 ? '+' : '' }}{{ formatFlowAmount(capitalFlow.shanghai) }}
            </div>
          </div>
          <div class="flow-card">
            <h4>深港通</h4>
            <div class="flow-value" :class="{ positive: capitalFlow.shenzhen > 0, negative: capitalFlow.shenzhen < 0 }">
              {{ capitalFlow.shenzhen > 0 ? '+' : '' }}{{ formatFlowAmount(capitalFlow.shenzhen) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiService from '@/services/apiService'

// 响应式数据
const marketIndices = ref<any[]>([])
const sectorHeatmap = ref<any[]>([])
const hotStocks = ref({
  upStocks: [],
  downStocks: [],
  turnoverStocks: []
})
const capitalFlow = ref({
  north: 0,
  south: 0,
  shanghai: 0,
  shenzhen: 0
})
const activeTab = ref('up')
const loading = ref(false)
const error = ref('')

// 加载所有市场数据
const loadAllData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 并行获取所有数据
    const [indicesData, industryData, hotStocksData] = await Promise.all([
      apiService.stock.getMarketIndices(),
      apiService.industry.getIndustryRanking(),
      apiService.stock.getHotStocks()
    ])
    
    // 处理市场指数数据
    marketIndices.value = indicesData || []
    
    // 处理行业数据
    sectorHeatmap.value = industryData || []
    
    // 处理热点股票数据
    hotStocks.value = {
      upStocks: hotStocksData.upStocks || [],
      downStocks: hotStocksData.downStocks || [],
      turnoverStocks: hotStocksData.turnoverStocks || []
    }
    
  } catch (err) {
    console.error('加载市场数据失败:', err)
    error.value = '数据加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 移除默认数据函数，完全使用API获取真实数据
// 所有数据将通过API调用加载，确保数据的真实性和时效性

// 格式化工具函数
const formatPrice = (price: number) => {
  return price.toFixed(2)
}

const formatPercent = (percent: number) => {
  return percent.toFixed(2) + '%'
}

const formatAmount = (amount: number) => {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toString()
}

const formatFlowAmount = (amount: number) => {
  return (amount / 100000000).toFixed(2) + '亿'
}

// 表格格式化函数
const formatTablePriceChange = ({ row }: any) => {
  const change = row.change || 0
  const color = change > 0 ? '#f56c6c' : change < 0 ? '#67c23a' : '#909399'
  return `<span style="color: ${color}">${change > 0 ? '+' : ''}${formatPrice(change)}</span>`
}

const formatTablePercentChange = ({ row }: any) => {
  const changePercent = row.changePercent || 0
  const color = changePercent > 0 ? '#f56c6c' : changePercent < 0 ? '#67c23a' : '#909399'
  return `<span style="color: ${color}">${changePercent > 0 ? '+' : ''}${formatPercent(changePercent)}</span>`
}

const formatTableVolume = ({ row }: any) => {
  return (row.volume || 0).toFixed(2)
}

const formatTableAmount = ({ row }: any) => {
  return (row.amount || 0).toLocaleString()
}

const formatTableTurnoverRate = ({ row }: any) => {
  return `${(row.turnoverRate || 0).toFixed(2)}%`
}

// 获取行业板块颜色类
const getSectorColorClass = (changePercent: number) => {
  if (changePercent > 2) return 'strong-up'
  if (changePercent > 0.5) return 'up'
  if (changePercent > 0) return 'light-up'
  if (changePercent > -0.5) return 'light-down'
  if (changePercent > -2) return 'down'
  return 'strong-down'
}

// 显示行业详情
const showSectorDetail = (sector: any) => {
  console.log('显示行业详情:', sector)
  // 在实际应用中，这里会跳转到行业详情页或弹出详情对话框
}

// 组件挂载时加载数据
  onMounted(() => {
    loadAllData()
  })
</script>

<style scoped>
.market-data {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #3059a7;
}

h3 {
  margin: 0 0 15px 0;
  color: #3059a7;
}

/* 市场指数概览 */
.index-overview {
  margin-bottom: 30px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.index-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.index-card {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 6px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.index-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.index-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.index-header h4 {
  margin: 0;
  font-size: 16px;
  color: #3059a7;
}

.index-header .code {
  font-size: 12px;
  color: #909399;
}

.index-price {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.index-change {
  font-size: 14px;
  font-weight: bold;
}

.index-change.positive {
  color: #f56c6c;
}

.index-change.negative {
  color: #67c23a;
}

.change-percent {
  margin-left: 5px;
}

.index-vol {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

/* 行业板块热力图 */
.heatmap-container {
  margin-bottom: 30px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}

.heatmap-item {
  padding: 15px;
  border-radius: 6px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.heatmap-item:hover {
  transform: scale(1.05);
}

.sector-name {
  font-size: 14px;
  margin-bottom: 5px;
  color: #333;
}

.sector-change {
  font-size: 16px;
  font-weight: bold;
}

.heatmap-item.strong-up {
  background-color: #fee;
}

.heatmap-item.up {
  background-color: #ffeeee;
}

.heatmap-item.light-up {
  background-color: #fff2f0;
}

.heatmap-item.light-down {
  background-color: #f0f9ff;
}

.heatmap-item.down {
  background-color: #e6f7ff;
}

.heatmap-item.strong-down {
  background-color: #d9f7be;
}

.heatmap-item.strong-up .sector-change,
.heatmap-item.up .sector-change,
.heatmap-item.light-up .sector-change {
  color: #f56c6c;
}

.heatmap-item.strong-down .sector-change,
.heatmap-item.down .sector-change,
.heatmap-item.light-down .sector-change {
  color: #67c23a;
}

/* 热点股票 */
.hot-stocks {
  margin-bottom: 30px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 资金流向 */
.capital-flow {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.flow-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.flow-card {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 6px;
  text-align: center;
}

.flow-card h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #3059a7;
}

.flow-value {
  font-size: 24px;
  font-weight: bold;
}

.flow-value.positive {
  color: #f56c6c;
}

.flow-value.negative {
  color: #67c23a;
}

/* 表格样式 */
.text-danger {
  color: #f56c6c;
}

.text-success {
  color: #67c23a;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3059a7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态样式 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  background-color: #fff1f0;
  border-radius: 8px;
  border: 1px solid #ffa39e;
}

.error-message {
  color: #ff4d4f;
  margin-bottom: 15px;
  font-size: 16px;
}

.error-container button {
  background-color: #3059a7;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.error-container button:hover {
  background-color: #274885;
}

/* 空状态样式 */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 20px;
  color: #909399;
  background-color: #f5f7fa;
  border-radius: 6px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .index-cards,
  .flow-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .market-data {
    padding: 10px;
  }
  
  h2 {
    font-size: 20px;
    margin-bottom: 15px;
  }
  
  h3 {
    font-size: 18px;
    margin-bottom: 12px;
  }
  
  .index-overview,
  .heatmap-container,
  .hot-stocks,
  .capital-flow {
    padding: 15px;
    margin-bottom: 20px;
  }
  
  .index-cards,
  .flow-cards {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px;
  }
  
  .heatmap-grid {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 8px;
  }
  
  .index-price {
    font-size: 18px;
  }
  
  .flow-value {
    font-size: 20px;
  }
  
  /* 表格在平板端的特殊处理 */
  .el-table {
    font-size: 12px;
  }
  
  .el-table__header th {
    padding: 8px 4px !important;
  }
  
  .el-table__body td {
    padding: 8px 4px !important;
  }
  
  /* 热点股票区域添加水平滚动 */
  .hot-stocks {
    overflow-x: auto;
  }
}

@media (max-width: 480px) {
  .index-header h4,
  .flow-card h4 {
    font-size: 14px;
  }
  
  .index-cards,
  .flow-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .heatmap-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .heatmap-item {
    padding: 10px 8px;
  }
  
  .sector-name {
    font-size: 12px;
    margin-bottom: 3px;
  }
  
  .sector-change {
    font-size: 14px;
    font-weight: bold;
  }
  
  /* 移动端表格显示优化 */
  .hot-stocks {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .el-tabs__nav {
    font-size: 12px;
  }
  
  /* 确保表格在小屏幕上可以水平滚动 */
  .el-table {
    min-width: 600px;
    font-size: 11px;
  }
  
  .el-table__header th,
  .el-table__body td {
    padding: 6px 3px !important;
  }
  
  /* 加载和错误状态在移动端的优化 */
  .loading-container,
  .error-container {
    padding: 40px 15px;
  }
  
  .empty-state {
    padding: 30px 15px;
  }
}
</style>