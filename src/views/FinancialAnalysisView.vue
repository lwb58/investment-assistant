<template>
  <div class="financial-analysis">
    <h2>财务分析引擎</h2>
    
    <!-- 股票搜索器 -->
    <div class="search-container">
      <el-input
        v-model="searchQuery"
        placeholder="请输入股票代码或名称"
        class="search-input"
        @keyup.enter="searchStock"
      >
        <template #append>
          <el-button type="primary" @click="searchStock">搜索</el-button>
        </template>
      </el-input>
    </div>
    
    <!-- 公司概览 -->
    <div v-if="selectedStock" class="company-overview">
      <div class="company-header">
        <h3>{{ selectedStock.name }}</h3>
        <span class="stock-code">{{ selectedStock.code }}</span>
        <span class="stock-price" :class="{ positive: selectedStock.priceChange > 0, negative: selectedStock.priceChange < 0 }">
          ¥{{ selectedStock.currentPrice }} {{ selectedStock.priceChange > 0 ? '+' : '' }}{{ selectedStock.priceChange.toFixed(2) }} ({{ selectedStock.priceChangePercent > 0 ? '+' : '' }}{{ selectedStock.priceChangePercent.toFixed(2) }}%)
        </span>
      </div>
      <div class="company-info">
        <div class="info-item">
          <span class="label">行业：</span>
          <span class="value">{{ selectedStock.industry }}</span>
        </div>
        <div class="info-item">
          <span class="label">市值：</span>
          <span class="value">{{ formatMarketCap(selectedStock.marketCap) }}</span>
        </div>
        <div class="info-item">
          <span class="label">市盈率(TTM)：</span>
          <span class="value">{{ selectedStock.peTTM.toFixed(2) }}</span>
        </div>
        <div class="info-item">
          <span class="label">市净率：</span>
          <span class="value">{{ selectedStock.pb.toFixed(2) }}</span>
        </div>
      </div>
    </div>
    
    <!-- 财务指标选项卡 -->
    <el-tabs v-model="activeTab" v-if="selectedStock">
      <!-- 关键财务指标 -->
      <el-tab-pane label="关键指标" name="keyIndicators">
        <div class="indicator-cards">
          <div class="indicator-card">
            <h4>盈利能力</h4>
            <div class="indicator-item">
              <span class="label">营业总收入(亿)</span>
              <div class="value-row">
                <span class="value">{{ selectedStock.indicators.revenue }}</span>
                <span class="change" :class="{ positive: selectedStock.indicators.revenueYoY > 0, negative: selectedStock.indicators.revenueYoY < 0 }">
                  {{ selectedStock.indicators.revenueYoY > 0 ? '+' : '' }}{{ selectedStock.indicators.revenueYoY }}%
                </span>
              </div>
            </div>
            <div class="indicator-item">
              <span class="label">净利润(亿)</span>
              <div class="value-row">
                <span class="value">{{ selectedStock.indicators.netProfit }}</span>
                <span class="change" :class="{ positive: selectedStock.indicators.netProfitYoY > 0, negative: selectedStock.indicators.netProfitYoY < 0 }">
                  {{ selectedStock.indicators.netProfitYoY > 0 ? '+' : '' }}{{ selectedStock.indicators.netProfitYoY }}%
                </span>
              </div>
            </div>
            <div class="indicator-item">
              <span class="label">毛利率(%)</span>
              <span class="value">{{ selectedStock.indicators.grossMargin }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">净利率(%)</span>
              <span class="value">{{ selectedStock.indicators.netMargin }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">ROE(%)</span>
              <span class="value">{{ selectedStock.indicators.roe }}</span>
            </div>
          </div>
          
          <div class="indicator-card">
            <h4>偿债能力</h4>
            <div class="indicator-item">
              <span class="label">资产负债率(%)</span>
              <span class="value">{{ selectedStock.indicators.debtRatio }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">流动比率</span>
              <span class="value">{{ selectedStock.indicators.currentRatio }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">速动比率</span>
              <span class="value">{{ selectedStock.indicators.quickRatio }}</span>
            </div>
          </div>
          
          <div class="indicator-card">
            <h4>运营能力</h4>
            <div class="indicator-item">
              <span class="label">应收账款周转率</span>
              <span class="value">{{ selectedStock.indicators.arTurnover }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">存货周转率</span>
              <span class="value">{{ selectedStock.indicators.inventoryTurnover }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">总资产周转率</span>
              <span class="value">{{ selectedStock.indicators.assetTurnover }}</span>
            </div>
          </div>
          
          <div class="indicator-card">
            <h4>成长能力</h4>
            <div class="indicator-item">
              <span class="label">营收同比增长(%)</span>
              <span class="value">{{ selectedStock.indicators.revenueYoY }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">净利润同比增长(%)</span>
              <span class="value">{{ selectedStock.indicators.netProfitYoY }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">营收环比增长(%)</span>
              <span class="value">{{ selectedStock.indicators.revenueQoq }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">净利润环比增长(%)</span>
              <span class="value">{{ selectedStock.indicators.netProfitQoq }}</span>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- 资产负债表 -->
      <el-tab-pane label="资产负债表" name="balanceSheet">
        <div class="financial-table">
          <el-table :data="selectedStock.balanceSheet" stripe style="width: 100%">
            <el-table-column prop="item" label="项目" width="200" />
            <el-table-column prop="latest" label="最新季度(亿元)" sortable />
            <el-table-column prop="previous" label="上季度(亿元)" sortable />
            <el-table-column prop="yearAgo" label="去年同期(亿元)" sortable />
            <el-table-column prop="yoyChange" label="同比增长(%)" :formatter="formatPercent" sortable />
          </el-table>
        </div>
      </el-tab-pane>
      
      <!-- 利润表 -->
      <el-tab-pane label="利润表" name="incomeStatement">
        <div class="financial-table">
          <el-table :data="selectedStock.incomeStatement" stripe style="width: 100%">
            <el-table-column prop="item" label="项目" width="200" />
            <el-table-column prop="latest" label="最新季度(亿元)" sortable />
            <el-table-column prop="previous" label="上季度(亿元)" sortable />
            <el-table-column prop="yearAgo" label="去年同期(亿元)" sortable />
            <el-table-column prop="yoyChange" label="同比增长(%)" :formatter="formatPercent" sortable />
          </el-table>
        </div>
      </el-tab-pane>
      
      <!-- 现金流量表 -->
      <el-tab-pane label="现金流量表" name="cashFlow">
        <div class="financial-table">
          <el-table :data="selectedStock.cashFlow" stripe style="width: 100%">
            <el-table-column prop="item" label="项目" width="200" />
            <el-table-column prop="latest" label="最新季度(亿元)" sortable />
            <el-table-column prop="previous" label="上季度(亿元)" sortable />
            <el-table-column prop="yearAgo" label="去年同期(亿元)" sortable />
            <el-table-column prop="yoyChange" label="同比增长(%)" :formatter="formatPercent" sortable />
          </el-table>
        </div>
      </el-tab-pane>
      
      <!-- 财务趋势图 -->
      <el-tab-pane label="趋势分析" name="trendAnalysis">
        <div class="chart-container">
          <h4>营收与利润趋势</h4>
          <div ref="trendChartRef" class="chart"></div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 财务评分 -->
    <div v-if="selectedStock" class="financial-score">
      <h3>财务健康评分</h3>
      <div class="score-cards">
        <div class="score-card">
          <h4>盈利能力</h4>
          <div class="score-value">{{ selectedStock.scores.profitability }}</div>
          <div class="score-desc">{{ getScoreDescription(selectedStock.scores.profitability) }}</div>
        </div>
        <div class="score-card">
          <h4>偿债能力</h4>
          <div class="score-value">{{ selectedStock.scores.solvency }}</div>
          <div class="score-desc">{{ getScoreDescription(selectedStock.scores.solvency) }}</div>
        </div>
        <div class="score-card">
          <h4>运营能力</h4>
          <div class="score-value">{{ selectedStock.scores.operation }}</div>
          <div class="score-desc">{{ getScoreDescription(selectedStock.scores.operation) }}</div>
        </div>
        <div class="score-card">
          <h4>成长能力</h4>
          <div class="score-value">{{ selectedStock.scores.growth }}</div>
          <div class="score-desc">{{ getScoreDescription(selectedStock.scores.growth) }}</div>
        </div>
        <div class="score-card total">
          <h4>综合评分</h4>
          <div class="score-value">{{ selectedStock.scores.overall }}</div>
          <div class="score-desc">{{ getScoreDescription(selectedStock.scores.overall) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'

// 模拟数据
const searchQuery = ref('')
const selectedStock = ref<any>({
  name: '贵州茅台',
  code: '600519',
  currentPrice: 1823.00,
  priceChange: 18.23,
  priceChangePercent: 1.01,
  industry: '白酒',
  marketCap: 22900,
  peTTM: 25.6,
  pb: 9.8,
  indicators: {
    revenue: 1062.75,
    revenueYoY: 16.85,
    revenueQoq: 4.32,
    netProfit: 484.22,
    netProfitYoY: 19.49,
    netProfitQoq: 5.16,
    grossMargin: 91.87,
    netMargin: 45.56,
    roe: 31.25,
    debtRatio: 17.68,
    currentRatio: 3.87,
    quickRatio: 3.65,
    arTurnover: 12.34,
    inventoryTurnover: 0.32,
    assetTurnover: 0.68
  },
  balanceSheet: [
    { item: '货币资金', latest: 1356.78, previous: 1234.56, yearAgo: 1123.45, yoyChange: 20.76 },
    { item: '应收账款', latest: 45.67, previous: 42.34, yearAgo: 38.90, yoyChange: 17.40 },
    { item: '存货', latest: 3256.78, previous: 3123.45, yearAgo: 2987.65, yoyChange: 8.94 },
    { item: '流动资产合计', latest: 5678.90, previous: 5432.10, yearAgo: 5123.45, yoyChange: 10.84 },
    { item: '固定资产', latest: 432.10, previous: 412.34, yearAgo: 398.76, yoyChange: 8.36 },
    { item: '总资产', latest: 21345.67, previous: 20123.45, yearAgo: 18987.65, yoyChange: 12.42 },
    { item: '短期借款', latest: 0.00, previous: 0.00, yearAgo: 0.00, yoyChange: 0.00 },
    { item: '应付账款', latest: 123.45, previous: 118.90, yearAgo: 112.34, yoyChange: 9.89 },
    { item: '流动负债合计', latest: 1467.89, previous: 1401.23, yearAgo: 1324.56, yoyChange: 10.82 },
    { item: '总负债', latest: 3773.45, previous: 3556.78, yearAgo: 3367.89, yoyChange: 12.04 },
    { item: '股东权益', latest: 17572.22, previous: 16566.67, yearAgo: 15619.76, yoyChange: 12.50 }
  ],
  incomeStatement: [
    { item: '营业收入', latest: 267.89, previous: 256.78, yearAgo: 229.24, yoyChange: 16.86 },
    { item: '营业成本', latest: 21.56, previous: 20.45, yearAgo: 19.23, yoyChange: 12.12 },
    { item: '营业利润', latest: 135.67, previous: 128.90, yearAgo: 113.56, yoyChange: 19.47 },
    { item: '净利润', latest: 108.90, previous: 103.56, yearAgo: 90.99, yoyChange: 19.68 },
    { item: '基本每股收益', latest: 8.71, previous: 8.28, yearAgo: 7.28, yoyChange: 19.64 }
  ],
  cashFlow: [
    { item: '经营活动现金流净额', latest: 123.45, previous: 118.90, yearAgo: 102.34, yoyChange: 20.63 },
    { item: '投资活动现金流净额', latest: -56.78, previous: -52.34, yearAgo: -48.90, yoyChange: -16.11 },
    { item: '筹资活动现金流净额', latest: -67.89, previous: -65.43, yearAgo: -62.34, yoyChange: -8.90 },
    { item: '现金及等价物净增加额', latest: -1.22, previous: 1.13, yearAgo: -8.90, yoyChange: 86.30 }
  ],
  scores: {
    profitability: 95,
    solvency: 90,
    operation: 85,
    growth: 88,
    overall: 92
  }
})

const activeTab = ref('keyIndicators')
const trendChartRef = ref<HTMLElement>()
let trendChartInstance: ECharts | null = null

// 搜索股票
const searchStock = () => {
  if (!searchQuery.value) {
    return
  }
  console.log('搜索股票:', searchQuery.value)
  // 在实际应用中，这里会根据搜索词获取股票数据
}

// 格式化市值
const formatMarketCap = (marketCap: number) => {
  return `${marketCap.toLocaleString()}亿`
}

// 格式化百分比
const formatPercent = ({ row }: any) => {
  const value = row.yoyChange
  const className = value > 0 ? 'text-danger' : value < 0 ? 'text-success' : ''
  const sign = value > 0 ? '+' : ''
  return `<span class="${className}">${sign}${value.toFixed(2)}%</span>`
}

// 获取评分描述
const getScoreDescription = (score: number) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '一般'
  if (score >= 60) return '较差'
  return '很差'
}

// 初始化趋势图
const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  trendChartInstance = echarts.init(trendChartRef.value)
  
  const option = {
    title: {
      text: '营收与净利润趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['营业收入', '净利润'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: ['2023-Q1', '2023-Q2', '2023-Q3', '2023-Q4', '2024-Q1', '2024-Q2']
    },
    yAxis: [
      {
        type: 'value',
        name: '亿元',
        position: 'left'
      },
      {
        type: 'value',
        name: '同比增长(%)',
        position: 'right',
        axisLabel: {
          formatter: '{value}%'
        }
      }
    ],
    series: [
      {
        name: '营业收入',
        type: 'bar',
        data: [218.29, 237.68, 251.87, 263.51, 232.43, 267.89]
      },
      {
        name: '净利润',
        type: 'bar',
        data: [95.39, 105.55, 113.09, 116.19, 96.32, 108.90]
      },
      {
        name: '营收同比增长',
        type: 'line',
        yAxisIndex: 1,
        data: [18.25, 16.51, 17.20, 16.82, 6.48, 16.86],
        smooth: true
      },
      {
        name: '净利润同比增长',
        type: 'line',
        yAxisIndex: 1,
        data: [23.92, 20.85, 19.87, 18.24, 1.15, 19.68],
        smooth: true
      }
    ]
  }
  
  trendChartInstance.setOption(option)
}

// 监听选项卡变化
watch(activeTab, (newTab) => {
  if (newTab === 'trendAnalysis') {
    nextTick(() => {
      initTrendChart()
    })
  }
})

onMounted(() => {
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (trendChartInstance) {
      trendChartInstance.resize()
    }
  })
})
</script>

<style scoped>
.financial-analysis {
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

h4 {
  margin: 0 0 10px 0;
  color: #3059a7;
}

/* 搜索容器 */
.search-container {
  margin-bottom: 20px;
}

.search-input {
  width: 400px;
}

/* 公司概览 */
.company-overview {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.company-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.company-header h3 {
  margin: 0;
  margin-right: 15px;
}

.stock-code {
  color: #909399;
  margin-right: 15px;
}

.stock-price {
  font-size: 18px;
  font-weight: bold;
}

.stock-price.positive {
  color: #f56c6c;
}

.stock-price.negative {
  color: #67c23a;
}

.company-info {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.info-item {
  display: flex;
}

.info-item .label {
  color: #909399;
  margin-right: 5px;
}

.info-item .value {
  color: #333;
  font-weight: 500;
}

/* 指标卡片 */
.indicator-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.indicator-card {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
}

.indicator-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.indicator-item:last-child {
  margin-bottom: 0;
}

.indicator-item .label {
  color: #606266;
}

.indicator-item .value {
  font-weight: 500;
  color: #333;
}

.value-row {
  display: flex;
  align-items: center;
  gap: 5px;
}

.indicator-item .change {
  font-size: 12px;
}

.indicator-item .change.positive {
  color: #f56c6c;
}

.indicator-item .change.negative {
  color: #67c23a;
}

/* 财务表格 */
.financial-table {
  margin-top: 20px;
}

/* 图表容器 */
.chart-container {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.chart {
  width: 100%;
  height: 400px;
}

/* 财务评分 */
.financial-score {
  margin-top: 30px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.score-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.score-card {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  transition: transform 0.2s;
}

.score-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.score-card.total {
  background-color: #e6f7ff;
  border: 2px solid #3059a7;
}

.score-value {
  font-size: 32px;
  font-weight: bold;
  color: #3059a7;
  margin: 10px 0;
}

.score-desc {
  color: #606266;
}

/* 表格样式 */
.text-danger {
  color: #f56c6c;
}

.text-success {
  color: #67c23a;
}
</style>