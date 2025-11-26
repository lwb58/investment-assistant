<template>
  <div class="market-data">
    <h2>市场数据中心</h2>
    
    <!-- 市场指数概览 -->
    <div class="index-overview">
      <h3>主要指数</h3>
      <div class="index-cards">
        <div class="index-card" v-for="index in marketIndices" :key="index.code">
          <div class="index-header">
            <h4>{{ index.name }}</h4>
            <span class="code">{{ index.code }}</span>
          </div>
          <div class="index-price">{{ index.price.toFixed(2) }}</div>
          <div class="index-change" :class="{ positive: index.change > 0, negative: index.change < 0 }">
            <span>{{ index.change > 0 ? '+' : '' }}{{ index.change.toFixed(2) }}</span>
            <span class="change-percent">{{ index.changePercent > 0 ? '+' : '' }}{{ index.changePercent.toFixed(2) }}%</span>
          </div>
          <div class="index-vol">
            <span>成交额: {{ (index.volume / 100000000).toFixed(2) }}亿</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 市场热力图 -->
    <div class="heatmap-container">
      <h3>行业板块热力图</h3>
      <div class="heatmap-grid">
        <div 
          v-for="sector in sectorHeatmap" 
          :key="sector.code"
          class="heatmap-item"
          :class="getSectorColorClass(sector.changePercent)"
          @click="showSectorDetail(sector)"
        >
          <div class="sector-name">{{ sector.name }}</div>
          <div class="sector-change">{{ sector.changePercent > 0 ? '+' : '' }}{{ sector.changePercent.toFixed(2) }}%</div>
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
            <el-table-column prop="change" label="涨跌额" :formatter="formatPriceChange" />
            <el-table-column prop="changePercent" label="涨跌幅" :formatter="formatPercentChange" />
            <el-table-column prop="volume" label="成交量(万手)" :formatter="formatVolume" />
            <el-table-column prop="amount" label="成交额(万元)" :formatter="formatAmount" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="跌幅榜" name="down">
          <el-table :data="hotStocks.downStocks" stripe style="width: 100%">
            <el-table-column type="index" width="50" />
            <el-table-column prop="name" label="名称" width="100" />
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="price" label="现价" />
            <el-table-column prop="change" label="涨跌额" :formatter="formatPriceChange" />
            <el-table-column prop="changePercent" label="涨跌幅" :formatter="formatPercentChange" />
            <el-table-column prop="volume" label="成交量(万手)" :formatter="formatVolume" />
            <el-table-column prop="amount" label="成交额(万元)" :formatter="formatAmount" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="换手率榜" name="turnover">
          <el-table :data="hotStocks.turnoverStocks" stripe style="width: 100%">
            <el-table-column type="index" width="50" />
            <el-table-column prop="name" label="名称" width="100" />
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="price" label="现价" />
            <el-table-column prop="change" label="涨跌额" :formatter="formatPriceChange" />
            <el-table-column prop="changePercent" label="涨跌幅" :formatter="formatPercentChange" />
            <el-table-column prop="turnoverRate" label="换手率" :formatter="formatTurnoverRate" />
            <el-table-column prop="amount" label="成交额(万元)" :formatter="formatAmount" />
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
            {{ capitalFlow.north > 0 ? '+' : '' }}{{ (capitalFlow.north / 10000).toFixed(2) }}亿
          </div>
        </div>
        <div class="flow-card">
          <h4>南向资金</h4>
          <div class="flow-value" :class="{ positive: capitalFlow.south > 0, negative: capitalFlow.south < 0 }">
            {{ capitalFlow.south > 0 ? '+' : '' }}{{ (capitalFlow.south / 10000).toFixed(2) }}亿
          </div>
        </div>
        <div class="flow-card">
          <h4>沪港通</h4>
          <div class="flow-value" :class="{ positive: capitalFlow.shanghai > 0, negative: capitalFlow.shanghai < 0 }">
            {{ capitalFlow.shanghai > 0 ? '+' : '' }}{{ (capitalFlow.shanghai / 10000).toFixed(2) }}亿
          </div>
        </div>
        <div class="flow-card">
          <h4>深港通</h4>
          <div class="flow-value" :class="{ positive: capitalFlow.shenzhen > 0, negative: capitalFlow.shenzhen < 0 }">
            {{ capitalFlow.shenzhen > 0 ? '+' : '' }}{{ (capitalFlow.shenzhen / 10000).toFixed(2) }}亿
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 模拟市场指数数据
const marketIndices = ref([
  { code: '000001.SH', name: '上证指数', price: 3087.24, change: 15.32, changePercent: 0.50, volume: 28000000000 },
  { code: '000002.SZ', name: '深证成指', price: 10123.45, change: -45.67, changePercent: -0.45, volume: 32000000000 },
  { code: '399006.SZ', name: '创业板指', price: 2045.67, change: -12.34, changePercent: -0.60, volume: 15000000000 },
  { code: '000016.SH', name: '上证50', price: 2456.78, change: 23.45, changePercent: 0.97, volume: 8000000000 },
  { code: '000905.SH', name: '中证500', price: 5678.90, change: -34.56, changePercent: -0.60, volume: 12000000000 },
  { code: '399001.SZ', name: '深证综指', price: 2134.56, change: -8.90, changePercent: -0.42, volume: 25000000000 }
])

// 模拟行业板块热力图数据
const sectorHeatmap = ref([
  { code: 'bank', name: '银行', changePercent: 1.23 },
  { code: 'tech', name: '科技', changePercent: -0.56 },
  { code: 'consumption', name: '消费', changePercent: 0.89 },
  { code: 'medicine', name: '医药', changePercent: -1.45 },
  { code: 'realestate', name: '地产', changePercent: 2.34 },
  { code: 'newEnergy', name: '新能源', changePercent: -0.23 },
  { code: 'semiconductor', name: '半导体', changePercent: 1.56 },
  { code: 'auto', name: '汽车', changePercent: 0.34 },
  { code: 'foodDrink', name: '食品饮料', changePercent: -0.78 },
  { code: 'media', name: '传媒', changePercent: 1.89 },
  { code: 'building', name: '建筑', changePercent: 0.45 },
  { code: 'chemical', name: '化工', changePercent: -0.67 }
])

// 模拟热点股票数据
const hotStocks = ref({
  upStocks: [
    { name: '贵州茅台', code: '600519', price: 1823.00, change: 18.23, changePercent: 1.01, volume: 123.45, amount: 225678.90, turnoverRate: 0.23 },
    { name: '宁德时代', code: '300750', price: 189.00, change: 17.18, changePercent: 10.00, volume: 456.78, amount: 83456.78, turnoverRate: 3.45 },
    { name: '比亚迪', code: '002594', price: 256.78, change: 23.34, changePercent: 10.00, volume: 567.89, amount: 140000.00, turnoverRate: 2.89 },
    { name: '隆基绿能', code: '601012', price: 45.67, change: 4.15, changePercent: 10.00, volume: 678.90, amount: 30000.00, turnoverRate: 4.56 },
    { name: '阳光电源', code: '300274', price: 89.01, change: 8.09, changePercent: 10.00, volume: 345.67, amount: 30000.00, turnoverRate: 5.67 }
  ],
  downStocks: [
    { name: '恒瑞医药', code: '600276', price: 45.67, change: -5.07, changePercent: -9.99, volume: 234.56, amount: 10000.00, turnoverRate: 1.23 },
    { name: '药明康德', code: '603259', price: 67.89, change: -7.54, changePercent: -9.99, volume: 123.45, amount: 8000.00, turnoverRate: 0.89 },
    { name: '爱尔眼科', code: '300015', price: 23.45, change: -2.60, changePercent: -9.98, volume: 345.67, amount: 8000.00, turnoverRate: 2.34 },
    { name: '智飞生物', code: '300122', price: 89.01, change: -9.89, changePercent: -9.98, volume: 98.76, amount: 8765.43, turnoverRate: 0.67 },
    { name: '迈瑞医疗', code: '300760', price: 289.01, change: -32.11, changePercent: -9.97, volume: 56.78, amount: 16000.00, turnoverRate: 0.45 }
  ],
  turnoverStocks: [
    { name: '中国中免', code: '601888', price: 123.45, change: 1.23, changePercent: 1.01, volume: 890.12, amount: 110000.00, turnoverRate: 15.67 },
    { name: '三峡能源', code: '600905', price: 5.67, change: 0.06, changePercent: 1.07, volume: 12345.67, amount: 70000.00, turnoverRate: 12.34 },
    { name: '京东方A', code: '000725', price: 4.56, change: 0.05, changePercent: 1.11, volume: 23456.78, amount: 107000.00, turnoverRate: 10.98 },
    { name: 'TCL科技', code: '000100', price: 3.45, change: 0.03, changePercent: 0.88, volume: 18901.23, amount: 65000.00, turnoverRate: 9.87 },
    { name: '包钢股份', code: '600010', price: 1.23, change: 0.01, changePercent: 0.82, volume: 34567.89, amount: 42500.00, turnoverRate: 8.76 }
  ]
})

// 模拟资金流向数据
const capitalFlow = ref({
  north: 567890000,
  south: -234567000,
  shanghai: 345678000,
  shenzhen: 222212000
})

const activeTab = ref('up')

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

// 格式化价格变化
const formatPriceChange = ({ row }: any) => {
  const change = row.change
  const className = change > 0 ? 'text-danger' : change < 0 ? 'text-success' : ''
  const sign = change > 0 ? '+' : ''
  return `<span class="${className}">${sign}${change.toFixed(2)}</span>`
}

// 格式化百分比变化
const formatPercentChange = ({ row }: any) => {
  const changePercent = row.changePercent
  const className = changePercent > 0 ? 'text-danger' : changePercent < 0 ? 'text-success' : ''
  const sign = changePercent > 0 ? '+' : ''
  return `<span class="${className}">${sign}${changePercent.toFixed(2)}%</span>`
}

// 格式化成交量
const formatVolume = ({ row }: any) => {
  return row.volume.toFixed(2)
}

// 格式化成交额
const formatAmount = ({ row }: any) => {
  return row.amount.toLocaleString()
}

// 格式化换手率
const formatTurnoverRate = ({ row }: any) => {
  return `${row.turnoverRate.toFixed(2)}%`
}

onMounted(() => {
  // 初始化数据
  console.log('市场数据中心页面已加载')
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
</style>