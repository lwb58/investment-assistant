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
    <div v-if="loading" class="loading">加载中...</div>
<div v-else-if="selectedStock" class="company-overview">
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

const searchQuery = ref('')
const selectedStock = ref<any>(null)
const loading = ref(false)

const activeTab = ref('keyIndicators')
const trendChartRef = ref<HTMLElement>()
let trendChartInstance: ECharts | null = null

// 搜索股票
const searchStock = async () => {
  if (!searchQuery.value) {
    return
  }
  
  loading.value = true
  try {
    // 调用API获取股票数据
    const response = await fetch(`/api/stock/financial/${searchQuery.value}`)
    const data = await response.json()
    selectedStock.value = data
  } catch (error) {
    console.error('获取股票数据失败:', error)
    // 可以添加错误提示
  } finally {
    loading.value = false
  }
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
  if (!trendChartRef.value || !selectedStock.value) return
  
  trendChartInstance = echarts.init(trendChartRef.value)
  
  // 这里应该使用从API获取的真实趋势数据
  // 暂时使用空数据结构，实际应用中应从selectedStock.value获取
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
      data: [] // 将从API数据填充
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
        data: [] // 将从API数据填充
      },
      {
        name: '净利润',
        type: 'bar',
        data: [] // 将从API数据填充
      },
      {
        name: '营收同比增长',
        type: 'line',
        yAxisIndex: 1,
        data: [], // 将从API数据填充
        smooth: true
      },
      {
        name: '净利润同比增长',
        type: 'line',
        yAxisIndex: 1,
        data: [], // 将从API数据填充
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