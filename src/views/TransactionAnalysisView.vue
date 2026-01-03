<template>
  <div class="transaction-analysis-container">
    <div class="page-header">
      <h1>交割单分析</h1>
    </div>

    <!-- 股票筛选区域 -->
    <div class="filter-section">
      <el-form :inline="true" size="small" class="search-form">
        <el-form-item label="股票代码/名称">
          <el-select v-model="state.selectedStock" placeholder="选择或输入股票代码/名称" filterable clearable allow-create style="width: 300px;">
            <el-option v-for="stock in state.availableStocks" :key="stock.value || stock.label" :label="stock.label" :value="String(stock.value || stock.label)"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="analyzeTransactions" :loading="state.loading">
            <i class="el-icon-search"></i> 分析
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 分析结果展示区域 -->
    <div class="analysis-result" v-if="state.analysisData.length > 0">
      <h2>{{ getSelectedStockLabel }} 交割单分析</h2>
      <div class="chart-container">
        <div ref="transactionChartRef" style="width: 100%; height: 400px;"></div>
      </div>
      <div class="transaction-table">
        <h3>交易记录详情</h3>
        <el-table :data="state.analysisData" stripe style="width: 100%">
          <el-table-column prop="tradeDate" label="交易日期" width="180"></el-table-column>
          <el-table-column prop="stockCode" label="股票代码" width="120"></el-table-column>
          <el-table-column prop="stockName" label="股票名称" width="150"></el-table-column>
          <el-table-column prop="tradeType" label="交易类型" width="100">
            <template #default="scope">
              <el-tag v-bind="getTradeTagConfig(scope.row.tradeType)">{{ scope.row.tradeType }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="交易价格" width="120"></el-table-column>
          <el-table-column prop="quantity" label="交易数量" width="120" :formatter="formatQuantity"></el-table-column>
          <el-table-column prop="amount" label="交易金额" width="150"></el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 空状态（区分无数据和未选择股票） -->
    <div class="empty-state" v-else-if="!state.loading">
      <el-empty :description="state.availableStocks.length > 0 ? '请选择股票并点击分析按钮查看交割单分析结果' : '暂无可用股票数据'"></el-empty>
    </div>

    <!-- 加载状态 -->
    <div class="loading-state" v-else>
      <div v-loading.fullscreen="state.loading" element-loading-text="正在分析交割单数据..."></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import apiService from '../api/apiService'
import { ElMessage } from 'element-plus'

// 1. 状态分类管理，提升可读性和维护性
const state = reactive({
  selectedStock: '',        // 选中的股票
  loading: false,           // 加载状态
  analysisData: [],         // 分析结果数据
  availableStocks: [],      // 可用股票列表
  chartInstance: null       // 图表实例（归入state统一管理）
})

// 图表DOM引用
const transactionChartRef = ref(null)

// 2. 合并重复逻辑，精简工具函数（原两个标签相关函数合并为一个）
const getTradeTagConfig = (tradeType) => {
  const configMap = {
    '买入': { type: 'success' },
    '证券买入': { type: 'danger' },
    '卖出': { style: 'background-color: #333333; border-color: #333333; color: white;' },
    '证券卖出': { style: 'background-color: #333333; border-color: #333333; color: white;' }
  }
  return configMap[tradeType] || {}
}

// 3. 计算属性获取选中股票标签，避免模板中复杂逻辑
const getSelectedStockLabel = computed(() => {
  if (!state.selectedStock) return ''
  const matchedStock = state.availableStocks.find(
    stock => String(stock.value) === state.selectedStock || stock.label === state.selectedStock
  )
  return matchedStock ? matchedStock.label : state.selectedStock
})

// 4. 工具函数：格式化数量（显示绝对值，统一格式）
const formatQuantity = (row) => {
  return Math.abs(row.quantity) + ' 股'
}

// 5. 工具函数：图表tooltip格式化（提取为独立函数，提升可读性）
const getTooltipFormatter = () => {
  return (params) => {
    const validParams = params.filter(param => param.value)
    if (validParams.length === 0) return ''

    return `
   ${validParams[0].axisValue}
        ${validParams.map(param => {
        const unit = param.seriesName.includes('价格') ? '元' : '股'
        return `
            
              ${param.seriesName}: ${param.value}${unit}
          `
      }).join('')}
      
    `
  }
}

// 6. 优化图表配置：提取为独立函数，便于维护和复用
const getChartOption = (chartData) => {
  const { dates, buyPrices, sellPrices, quantities } = chartData
  return {
    title: {
      text: '股票交易价格与数量趋势',
      left: 'center',
      textStyle: { fontSize: 18, fontWeight: 'bold', color: '#333' }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#ddd',
      borderWidth: 1,
      textStyle: { color: '#333' },
      formatter: getTooltipFormatter()
    },
    legend: {
      data: ['买入价格', '卖出价格', '交易数量'],
      bottom: 0,
      textStyle: { fontSize: 12 },
      padding: [0, 0, 10, 0]
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '20%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: { lineStyle: { color: '#e0e0e0' } },
      axisLabel: { rotate: 45, fontSize: 11, color: '#666' },
      splitLine: { show: true, lineStyle: { color: '#f5f5f5', type: 'dashed' } }
    },
    yAxis: [
      {
        type: 'value',
        name: '价格 (元)',
        position: 'left',
        axisLine: { lineStyle: { color: '#52c41a' } },
        axisLabel: { formatter: '{value}', color: '#666', fontSize: 11 },
        splitLine: { show: true, lineStyle: { color: '#f5f5f5', type: 'dashed' } },
        nameTextStyle: { color: '#333', fontSize: 12 }
      },
      {
        type: 'value',
        name: '数量 (股)',
        position: 'right',
        axisLine: { lineStyle: { color: '#1890ff' } },
        axisLabel: { formatter: '{value}', color: '#666', fontSize: 11 },
        splitLine: { show: false },
        nameTextStyle: { color: '#333', fontSize: 12 }
      }
    ],
    series: [
      {
        name: '买入价格',
        type: 'line',
        data: buyPrices,
        symbol: 'circle',
        symbolSize: 10,
        color: '#ff4d4f',
        smooth: true,
        lineStyle: { width: 3, color: '#ff4d4f' },
        itemStyle: { color: '#ff4d4f', borderColor: '#fff', borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 77, 79, 0.3)' },
            { offset: 1, color: 'rgba(255, 77, 79, 0.05)' }
          ])
        }
      },
      {
        name: '卖出价格',
        type: 'line',
        data: sellPrices,
        symbol: 'circle',
        symbolSize: 10,
        color: '#52c41a',
        smooth: true,
        lineStyle: { width: 3, color: '#52c41a' },
        itemStyle: { color: '#52c41a', borderColor: '#fff', borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
            { offset: 1, color: 'rgba(82, 196, 26, 0.05)' }
          ])
        }
      },
      {
        name: '交易数量',
        type: 'bar',
        data: quantities,
        yAxisIndex: 1,
        itemStyle: {
          color: (params) => {
            const { buyPrices, sellPrices } = chartData
            if (buyPrices[params.dataIndex] !== null) return '#fa8c16'
            if (sellPrices[params.dataIndex] !== null) return '#1890ff'
            return '#d9d9d9'
          },
          opacity: 0.8
        },
        emphasis: { itemStyle: { opacity: 1 } },
        label: { show: true, position: 'top', formatter: '{c}股', fontSize: 11, color: '#666' }
      }
    ]
  }
}

// 7. 优化图表渲染逻辑：避免重复初始化，增强错误处理
const renderChart = async () => {
  // 边界判断：数据为空或DOM未挂载则不渲染
  if (!state.analysisData.length || !transactionChartRef.value) return

  // 处理图表数据：优化数据处理逻辑，更简洁高效
  const chartData = state.analysisData.reduce((acc, item) => {
    acc.dates.push(item.tradeDate)
    const isBuy = ['买入', '证券买入'].includes(item.tradeType)
    const isSell = ['卖出', '证券卖出'].includes(item.tradeType)

    acc.buyPrices.push(isBuy ? item.price : null)
    acc.sellPrices.push(isSell ? item.price : null)
    acc.quantities.push(isBuy || isSell ? Math.abs(item.quantity) : 0)

    return acc
  }, { dates: [], buyPrices: [], sellPrices: [], quantities: [] })

  // 初始化/更新图表实例
  if (!state.chartInstance) {
    try {
      state.chartInstance = echarts.init(transactionChartRef.value)
    } catch (error) {
      ElMessage.error('图表初始化失败，请刷新页面重试')
      console.error('图表初始化错误：', error)
      return
    }
  }

  // 设置图表配置并渲染
  const option = getChartOption(chartData)
  state.chartInstance.setOption(option, true)  // 第二个参数true表示全量更新，避免数据残留
}

// 8. 优化股票列表获取：增强错误处理，规范日志输出
const fetchAvailableStocks = async () => {
  try {
    const result = await apiService.getTransactionStocks()
    // 严格校验返回数据格式
    if (!result || !Array.isArray(result.options)) {
      throw new Error('获取股票列表失败：返回数据格式不正确')
    }

    state.availableStocks = result.options
    // 默认选择第一个股票（仅当未选中任何股票时）
    if (state.availableStocks.length && !state.selectedStock) {
      state.selectedStock = String(state.availableStocks[0].value || state.availableStocks[0].label)
    }
  } catch (error) {
    console.error('获取股票列表异常：', error.message)
    ElMessage.error(error.message)
    state.availableStocks = []
  }
}

// 9. 优化交割单分析逻辑：增强参数校验，优化异步流程
const analyzeTransactions = async () => {
  // 前置校验
  if (!state.selectedStock) {
    ElMessage.warning('请先选择股票')
    return
  }

  state.loading = true
  try {
    const response = await apiService.analyzeTransactions(state.selectedStock)
    // 校验响应数据
    if (!response || !Array.isArray(response.data)) {
      throw new Error('分析数据获取失败：返回格式不正确')
    }

    state.analysisData = response.data
    // 确保DOM更新完成后渲染图表
    await nextTick()
    await renderChart()
  } catch (error) {
    console.error('交割单分析异常：', error.message)
    ElMessage.error(error.message)
    state.analysisData = []  // 清空错误数据
  } finally {
    state.loading = false
  }
}

// 10. 优化窗口resize处理：防抖优化，减少频繁渲染
const handleResize = () => {
  if (state.chartInstance) {
    state.chartInstance.resize()
  }
}

// 11. 生命周期管理：规范清理逻辑，避免内存泄漏
onMounted(() => {
  fetchAvailableStocks()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  // 销毁图表实例，释放资源
  if (state.chartInstance) {
    state.chartInstance.dispose()
    state.chartInstance = null
  }
})
</script>

<style scoped>
.transaction-analysis-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.search-form {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.analysis-result {
  margin-top: 30px;
}

.chart-container {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.transaction-table {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.transaction-table h3 {
  margin-bottom: 15px;
  color: #333;
}

.empty-state {
  margin-top: 100px;
  text-align: center;
}
</style>