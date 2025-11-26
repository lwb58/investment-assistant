<template>
  <div class="valuation-decision">
    <h2>估值决策系统</h2>
    
    <!-- 股票选择器 -->
    <div class="stock-selector">
      <el-select v-model="selectedStockId" placeholder="选择股票" class="stock-select" @change="loadStockData">
        <el-option v-for="stock in stockList" :key="stock.id" :label="stock.name + '(' + stock.code + ')" :value="stock.id" />
      </el-select>
      <el-button type="primary" @click="addStockToList" v-if="showAddButton">添加到对比</el-button>
    </div>
    
    <!-- 估值对比列表 -->
    <div v-if="comparisonList.length > 0" class="comparison-section">
      <h3>对比列表</h3>
      <div class="comparison-stocks">
        <div 
          v-for="stock in comparisonList" 
          :key="stock.id"
          class="comparison-stock-item"
        >
          <span>{{ stock.name }}</span>
          <el-button type="text" danger @click="removeStockFromList(stock.id)">移除</el-button>
        </div>
      </div>
      <el-button type="success" @click="startComparison" :disabled="comparisonList.length < 2">开始对比分析</el-button>
    </div>
    
    <!-- 估值模型选择 -->
    <div v-if="selectedStock" class="valuation-models">
      <h3>估值模型</h3>
      <el-tabs v-model="activeModel">
        <el-tab-pane label="DCF估值" name="dcf">
          <div class="model-content">
            <div class="model-params">
              <h4>DCF模型参数设置</h4>
              <div class="param-grid">
                <div class="param-item">
                  <label>预测年限(年)</label>
                  <el-input-number v-model="dcfParams.forecastYears" :min="3" :max="10" :step="1" />
                </div>
                <div class="param-item">
                  <label>增长率(%)</label>
                  <el-input-number v-model="dcfParams.growthRate" :min="0" :max="50" :step="0.1" />
                </div>
                <div class="param-item">
                  <label>贴现率(%)</label>
                  <el-input-number v-model="dcfParams.discountRate" :min="1" :max="20" :step="0.1" />
                </div>
                <div class="param-item">
                  <label>终值增长率(%)</label>
                  <el-input-number v-model="dcfParams.terminalGrowthRate" :min="0" :max="5" :step="0.1" />
                </div>
              </div>
              <el-button type="primary" @click="calculateDCF">计算DCF估值</el-button>
            </div>
            
            <div v-if="dcfResult" class="model-result">
              <h4>DCF估值结果</h4>
              <div class="result-cards">
                <div class="result-card">
                  <label>企业价值(EV)</label>
                  <div class="result-value">{{ formatCurrency(dcfResult.enterpriseValue) }}</div>
                </div>
                <div class="result-card">
                  <label>股权价值</label>
                  <div class="result-value">{{ formatCurrency(dcfResult.equityValue) }}</div>
                </div>
                <div class="result-card">
                  <label>每股价值</label>
                  <div class="result-value">{{ formatCurrency(dcfResult.perShareValue) }}</div>
                </div>
                <div class="result-card">
                  <label>当前价格</label>
                  <div class="result-value current-price">{{ formatCurrency(selectedStock.currentPrice) }}</div>
                </div>
                <div class="result-card">
                  <label>高估/低估</label>
                  <div class="result-value" :class="{ undervalued: dcfResult.valuation === 'undervalued', overvalued: dcfResult.valuation === 'overvalued' }">
                    {{ dcfResult.valuation === 'undervalued' ? '低估' : '高估' }} {{ Math.abs(dcfResult.percentDiff).toFixed(2) }}%
                  </div>
                </div>
              </div>
              
              <div class="chart-container">
                <h5>自由现金流预测</h5>
                <div ref="dcfChartRef" class="chart"></div>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="相对估值" name="relative">
          <div class="model-content">
            <div class="model-params">
              <h4>相对估值参数</h4>
              <el-select v-model="relativeParams.benchmarkType" placeholder="选择对标类型">
                <el-option label="同行业公司" value="industry" />
                <el-option label="自定义组合" value="custom" />
              </el-select>
            </div>
            
            <div class="valuation-table">
              <el-table :data="relativeValuationData" stripe style="width: 100%">
                <el-table-column prop="company" label="公司" width="150" />
                <el-table-column prop="currentPrice" label="当前价格" />
                <el-table-column prop="pe" label="PE" sortable />
                <el-table-column prop="pb" label="PB" sortable />
                <el-table-column prop="ps" label="PS" sortable />
                <el-table-column prop="evToEbitda" label="EV/EBITDA" sortable />
                <el-table-column prop="peg" label="PEG" sortable />
              </el-table>
            </div>
            
            <div class="relative-summary">
              <h4>相对估值摘要</h4>
              <div class="summary-cards">
                <div class="summary-card">
                  <label>行业平均PE</label>
                  <div class="summary-value">{{ relativeSummary.avgPE.toFixed(2) }}</div>
                </div>
                <div class="summary-card">
                  <label>行业平均PB</label>
                  <div class="summary-value">{{ relativeSummary.avgPB.toFixed(2) }}</div>
                </div>
                <div class="summary-card">
                  <label>行业平均PS</label>
                  <div class="summary-value">{{ relativeSummary.avgPS.toFixed(2) }}</div>
                </div>
                <div class="summary-card">
                  <label>目标价(基于PE)</label>
                  <div class="summary-value target-price">{{ formatCurrency(relativeSummary.targetPricePE) }}</div>
                </div>
                <div class="summary-card">
                  <label>目标价(基于PB)</label>
                  <div class="summary-value target-price">{{ formatCurrency(relativeSummary.targetPricePB) }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="综合评分" name="score">
          <div class="model-content">
            <h4>估值综合评分</h4>
            <div class="score-matrix">
              <div class="score-row">
                <div class="score-item">
                  <span>基本面评分</span>
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: scoreData.fundamental + '%' }"></div>
                  </div>
                  <span class="score-value">{{ scoreData.fundamental }}/100</span>
                </div>
              </div>
              <div class="score-row">
                <div class="score-item">
                  <span>成长性评分</span>
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: scoreData.growth + '%' }"></div>
                  </div>
                  <span class="score-value">{{ scoreData.growth }}/100</span>
                </div>
              </div>
              <div class="score-row">
                <div class="score-item">
                  <span>估值水平评分</span>
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: scoreData.valuation + '%' }"></div>
                  </div>
                  <span class="score-value">{{ scoreData.valuation }}/100</span>
                </div>
              </div>
              <div class="score-row">
                <div class="score-item">
                  <span>技术面评分</span>
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: scoreData.technical + '%' }"></div>
                  </div>
                  <span class="score-value">{{ scoreData.technical }}/100</span>
                </div>
              </div>
              <div class="score-row total">
                <div class="score-item">
                  <span>综合评分</span>
                  <div class="score-bar">
                    <div class="score-fill total" :style="{ width: scoreData.total + '%' }"></div>
                  </div>
                  <span class="score-value total">{{ scoreData.total }}/100</span>
                </div>
              </div>
            </div>
            
            <div class="investment-suggestion">
              <h4>投资建议</h4>
              <div class="suggestion-box" :class="getSuggestionClass(scoreData.total)">
                <div class="suggestion-title">{{ getSuggestionTitle(scoreData.total) }}</div>
                <div class="suggestion-content">{{ getSuggestionContent(scoreData.total) }}</div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 历史估值走势 -->
    <div v-if="selectedStock" class="historical-valuation">
      <h3>历史估值走势</h3>
      <div ref="historicalChartRef" class="chart"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'

// 模拟数据
const stockList = ref([
  { id: '1', name: '贵州茅台', code: '600519' },
  { id: '2', name: '宁德时代', code: '300750' },
  { id: '3', name: '比亚迪', code: '002594' },
  { id: '4', name: '隆基绿能', code: '601012' },
  { id: '5', name: '阳光电源', code: '300274' }
])

const selectedStockId = ref('1')
const selectedStock = ref<any>({
  id: '1',
  name: '贵州茅台',
  code: '600519',
  currentPrice: 1823.00,
  pe: 25.6,
  pb: 9.8,
  ps: 13.2,
  evToEbitda: 20.5,
  peg: 1.2
})

const comparisonList = ref<any[]>([])
const showAddButton = ref(true)
const activeModel = ref('dcf')

// DCF参数
const dcfParams = ref({
  forecastYears: 5,
  growthRate: 15,
  discountRate: 9,
  terminalGrowthRate: 2.5
})

const dcfResult = ref<any>(null)

// 相对估值参数
const relativeParams = ref({
  benchmarkType: 'industry'
})

const relativeValuationData = ref([
  { company: '贵州茅台', currentPrice: 1823.00, pe: 25.6, pb: 9.8, ps: 13.2, evToEbitda: 20.5, peg: 1.2 },
  { company: '五粮液', currentPrice: 168.50, pe: 18.2, pb: 5.6, ps: 8.9, evToEbitda: 15.8, peg: 1.4 },
  { company: '泸州老窖', currentPrice: 145.20, pe: 21.3, pb: 7.8, ps: 10.5, evToEbitda: 18.2, peg: 1.3 },
  { company: '山西汾酒', currentPrice: 287.60, pe: 28.5, pb: 12.3, ps: 15.6, evToEbitda: 23.4, peg: 1.5 },
  { company: '洋河股份', currentPrice: 132.40, pe: 15.8, pb: 4.9, ps: 7.8, evToEbitda: 13.5, peg: 1.2 },
  { company: '行业平均', currentPrice: '-', pe: 22.5, pb: 8.1, ps: 11.2, evToEbitda: 18.3, peg: 1.3 }
])

const relativeSummary = ref({
  avgPE: 22.5,
  avgPB: 8.1,
  avgPS: 11.2,
  targetPricePE: 1598.40,
  targetPricePB: 1584.00
})

// 综合评分
const scoreData = ref({
  fundamental: 95,
  growth: 88,
  valuation: 75,
  technical: 82,
  total: 85
})

// 图表引用
const dcfChartRef = ref<HTMLElement>()
const historicalChartRef = ref<HTMLElement>()
let dcfChartInstance: ECharts | null = null
let historicalChartInstance: ECharts | null = null

// 加载股票数据
const loadStockData = (id: string) => {
  // 在实际应用中，这里会根据ID加载股票详细数据
  console.log('加载股票数据:', id)
  const stock = stockList.value.find(s => s.id === id)
  if (stock) {
    selectedStock.value = {
      ...selectedStock.value,
      id: stock.id,
      name: stock.name,
      code: stock.code
    }
    showAddButton.value = !comparisonList.value.some(s => s.id === id)
  }
}

// 添加到对比列表
const addStockToList = () => {
  if (!comparisonList.value.some(s => s.id === selectedStock.value.id)) {
    comparisonList.value.push({ ...selectedStock.value })
    showAddButton.value = false
  }
}

// 从对比列表移除
const removeStockFromList = (id: string) => {
  comparisonList.value = comparisonList.value.filter(s => s.id !== id)
  if (id === selectedStock.value.id) {
    showAddButton.value = true
  }
}

// 开始对比分析
const startComparison = () => {
  console.log('开始对比分析:', comparisonList.value)
  // 在实际应用中，这里会执行对比分析逻辑
}

// 计算DCF估值
const calculateDCF = () => {
  // 模拟DCF计算
  const freeCashFlow = 48422000000 // 484.22亿
  const shares = 12561978000 // 125.62亿股
  
  // 简化的DCF计算
  let enterpriseValue = 0
  let terminalValue = 0
  
  // 计算预测期现金流现值
  for (let i = 1; i <= dcfParams.value.forecastYears; i++) {
    const cashFlow = freeCashFlow * Math.pow((1 + dcfParams.value.growthRate / 100), i)
    const presentValue = cashFlow / Math.pow((1 + dcfParams.value.discountRate / 100), i)
    enterpriseValue += presentValue
  }
  
  // 计算终值
  const lastCashFlow = freeCashFlow * Math.pow((1 + dcfParams.value.growthRate / 100), dcfParams.value.forecastYears)
  terminalValue = lastCashFlow * (1 + dcfParams.value.terminalGrowthRate / 100) / 
                 ((dcfParams.value.discountRate / 100) - (dcfParams.value.terminalGrowthRate / 100))
  
  // 终值折现
  const terminalValuePresent = terminalValue / Math.pow((1 + dcfParams.value.discountRate / 100), dcfParams.value.forecastYears)
  enterpriseValue += terminalValuePresent
  
  // 计算股权价值（简化处理，假设无负债）
  const equityValue = enterpriseValue
  const perShareValue = equityValue / shares
  
  // 计算高估/低估百分比
  const percentDiff = ((perShareValue - selectedStock.value.currentPrice) / selectedStock.value.currentPrice) * 100
  const valuation = percentDiff > 0 ? 'undervalued' : 'overvalued'
  
  dcfResult.value = {
    enterpriseValue,
    equityValue,
    perShareValue,
    percentDiff,
    valuation
  }
  
  nextTick(() => {
    initDCFChart()
  })
}

// 格式化货币
const formatCurrency = (value: number) => {
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toFixed(2)
}

// 初始化DCF图表
const initDCFChart = () => {
  if (!dcfChartRef.value) return
  
  dcfChartInstance = echarts.init(dcfChartRef.value)
  
  const years = []
  const cashFlows = []
  const discountRates = []
  
  for (let i = 1; i <= dcfParams.value.forecastYears; i++) {
    years.push(`第${i}年`)
    const cashFlow = 48422000000 * Math.pow((1 + dcfParams.value.growthRate / 100), i)
    cashFlows.push((cashFlow / 100000000).toFixed(2))
    discountRates.push(dcfParams.value.discountRate)
  }
  
  const option = {
    title: {
      text: '自由现金流预测',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['自由现金流(亿)', '贴现率(%)'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: years
    },
    yAxis: [
      {
        type: 'value',
        name: '现金流(亿)',
        position: 'left'
      },
      {
        type: 'value',
        name: '贴现率(%)',
        position: 'right',
        max: dcfParams.value.discountRate * 2
      }
    ],
    series: [
      {
        name: '自由现金流(亿)',
        type: 'bar',
        data: cashFlows
      },
      {
        name: '贴现率(%)',
        type: 'line',
        yAxisIndex: 1,
        data: discountRates
      }
    ]
  }
  
  dcfChartInstance.setOption(option)
}

// 初始化历史估值图表
const initHistoricalChart = () => {
  if (!historicalChartRef.value) return
  
  historicalChartInstance = echarts.init(historicalChartRef.value)
  
  const option = {
    title: {
      text: '历史估值走势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['PE', 'PB', 'PS'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: ['2023-01', '2023-03', '2023-06', '2023-09', '2023-12', '2024-03', '2024-06', '2024-09']
    },
    yAxis: {
      type: 'value',
      splitLine: {
        show: true
      }
    },
    series: [
      {
        name: 'PE',
        type: 'line',
        data: [32.5, 30.2, 28.6, 26.8, 24.5, 23.2, 24.8, 25.6],
        smooth: true
      },
      {
        name: 'PB',
        type: 'line',
        data: [11.5, 10.8, 10.2, 9.5, 8.8, 8.5, 9.2, 9.8],
        smooth: true
      },
      {
        name: 'PS',
        type: 'line',
        data: [15.8, 14.5, 13.8, 13.2, 12.5, 12.0, 12.8, 13.2],
        smooth: true
      }
    ]
  }
  
  historicalChartInstance.setOption(option)
}

// 获取建议类名
const getSuggestionClass = (score: number) => {
  if (score >= 85) return 'strong-buy'
  if (score >= 75) return 'buy'
  if (score >= 65) return 'hold'
  if (score >= 55) return 'sell'
  return 'strong-sell'
}

// 获取建议标题
const getSuggestionTitle = (score: number) => {
  if (score >= 85) return '强烈买入'
  if (score >= 75) return '买入'
  if (score >= 65) return '持有'
  if (score >= 55) return '卖出'
  return '强烈卖出'
}

// 获取建议内容
const getSuggestionContent = (score: number) => {
  if (score >= 85) {
    return '该股票综合评分优秀，基本面稳健，估值合理，具有较高的投资价值，建议积极买入。'
  } else if (score >= 75) {
    return '该股票综合评分良好，具有一定的投资价值，可以考虑适量买入。'
  } else if (score >= 65) {
    return '该股票综合评分一般，暂时建议持有，密切关注公司基本面变化。'
  } else if (score >= 55) {
    return '该股票综合评分较差，存在一定风险，建议考虑减持。'
  }
  return '该股票综合评分很差，风险较高，建议尽快卖出。'
}

// 监听选项卡变化
watch(activeModel, (newModel) => {
  if (newModel === 'dcf' && dcfResult.value) {
    nextTick(() => {
      initDCFChart()
    })
  }
})

onMounted(() => {
  loadStockData(selectedStockId.value)
  
  // 初始化历史估值图表
  nextTick(() => {
    initHistoricalChart()
  })
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    dcfChartInstance?.resize()
    historicalChartInstance?.resize()
  })
})
</script>

<style scoped>
.valuation-decision {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #3059a7;
}

h3, h4, h5 {
  margin: 0 0 15px 0;
  color: #3059a7;
}

/* 股票选择器 */
.stock-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.stock-select {
  width: 250px;
}

/* 对比列表 */
.comparison-section {
  margin-bottom: 30px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comparison-stocks {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.comparison-stock-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 15px;
  background-color: #f5f7fa;
  border-radius: 20px;
}

/* 估值模型 */
.valuation-models {
  margin-bottom: 30px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.model-content {
  padding-top: 20px;
}

.model-params {
  margin-bottom: 30px;
}

.param-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.param-item label {
  font-size: 14px;
  color: #606266;
}

/* 模型结果 */
.model-result {
  margin-top: 30px;
}

.result-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.result-card {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  text-align: center;
}

.result-card label {
  display: block;
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.result-value {
  font-size: 24px;
  font-weight: bold;
  color: #3059a7;
}

.result-value.current-price {
  color: #606266;
}

.result-value.undervalued {
  color: #67c23a;
}

.result-value.overvalued {
  color: #f56c6c;
}

/* 图表容器 */
.chart-container {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.chart {
  width: 100%;
  height: 400px;
}

/* 相对估值 */
.valuation-table {
  margin-bottom: 30px;
}

.relative-summary {
  margin-top: 30px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.summary-card {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  text-align: center;
}

.summary-card label {
  display: block;
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
  color: #3059a7;
}

.summary-value.target-price {
  color: #67c23a;
}

/* 综合评分 */
.score-matrix {
  margin-bottom: 30px;
}

.score-row {
  margin-bottom: 15px;
}

.score-row.total {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #3059a7;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.score-item span {
  width: 100px;
  font-size: 14px;
  color: #606266;
}

.score-row.total .score-item span {
  font-weight: bold;
  color: #3059a7;
}

.score-bar {
  flex: 1;
  height: 20px;
  background-color: #e6f7ff;
  border-radius: 10px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background-color: #67c23a;
  transition: width 0.5s ease;
}

.score-fill.total {
  background-color: #3059a7;
}

.score-value {
  width: 60px;
  text-align: right;
  font-size: 14px;
  color: #606266;
}

.score-value.total {
  font-weight: bold;
  color: #3059a7;
}

/* 投资建议 */
.investment-suggestion {
  margin-top: 30px;
}

.suggestion-box {
  padding: 20px;
  border-radius: 8px;
  background-color: #f0f9ff;
  border-left: 4px solid #3059a7;
}

.suggestion-box.strong-buy {
  background-color: #f0f9ff;
  border-left-color: #3059a7;
}

.suggestion-box.buy {
  background-color: #f0f9ff;
  border-left-color: #67c23a;
}

.suggestion-box.hold {
  background-color: #fdf6ec;
  border-left-color: #e6a23c;
}

.suggestion-box.sell {
  background-color: #fef0f0;
  border-left-color: #f56c6c;
}

.suggestion-box.strong-sell {
  background-color: #fef0f0;
  border-left-color: #f56c6c;
}

.suggestion-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #3059a7;
}

.suggestion-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

/* 历史估值走势 */
.historical-valuation {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>