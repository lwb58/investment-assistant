<template>
  <div class="transaction-analysis-container">
    <div class="page-header">
      <h1>交割单分析</h1>
    </div>

    <!-- 股票筛选区域 -->
    <div class="filter-section">
      <el-form :inline="true" size="small" class="search-form">
        <el-form-item label="股票代码/名称">
          <el-select
            v-model="selectedStock"
            placeholder="选择或输入股票代码/名称"
            filterable
            clearable
            allow-create
            @change="handleStockChange"
            style="width: 300px;"
          >
            <el-option
              v-for="stock in availableStocks"
              :key="stock.value || Math.random().toString()"
              :label="stock.label"
              :value="stock.value || ''"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="analyzeTransactions" :loading="loading">
            <i class="el-icon-search"></i>
            分析
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 分析结果展示区域 -->
    <div class="analysis-result" v-if="analysisData && analysisData.length > 0">
      <h2>{{ selectedStock }} 交割单分析</h2>
      <div class="chart-container">
        <div ref="transactionChart" style="width: 100%; height: 400px;"></div>
      </div>
      <div class="transaction-table">
        <h3>交易记录详情</h3>
        <el-table :data="analysisData" stripe style="width: 100%">
          <el-table-column prop="tradeDate" label="交易日期" width="180" />
          <el-table-column prop="stockCode" label="股票代码" width="120" />
          <el-table-column prop="stockName" label="股票名称" width="150" />
          <el-table-column prop="tradeType" label="交易类型" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.tradeType === '买入' ? 'success' : 'danger'">
                {{ scope.row.tradeType }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="交易价格" width="120" />
          <el-table-column prop="quantity" label="交易数量" width="120" />
          <el-table-column prop="amount" label="交易金额" width="150" />
        </el-table>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else-if="!loading">
      <el-empty description="请选择股票并点击分析按钮查看交割单分析结果" />
    </div>

    <!-- 加载状态 -->
    <div class="loading-state" v-else>
      <div v-loading.fullscreen="loading" element-loading-text="正在分析交割单数据..."></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import apiService from '../api/apiService'
import { ElMessage as elMessage } from 'element-plus'

// 状态管理
const selectedStock = ref('')
const loading = ref(false)
const analysisData = ref([])
const availableStocks = ref([])
const transactionChart = ref(null)
let chartInstance = null

// 获取可用股票列表
const fetchAvailableStocks = async () => {
  try {
    const result = await apiService.getTransactionStocks()
    console.log('Transaction stocks result:', result)
    availableStocks.value = result.stocks.map(stock => ({
      value: stock.code,
      label: `${stock.code} - ${stock.name}`
    }))
    console.log('Available stocks:', availableStocks.value)
  } catch (error) {
    console.error('获取股票列表失败:', error)
    elMessage.error('获取股票列表失败')
  }
}

// 股票选择变化处理
const handleStockChange = (value) => {
  selectedStock.value = value
}

// 分析交割单
const analyzeTransactions = async () => {
  if (!selectedStock.value) {
    elMessage.warning('请先选择股票')
    return
  }

  loading.value = true
  try {
    const response = await apiService.analyzeTransactions(selectedStock.value)
    analysisData.value = response.data
    renderChart()
  } catch (error) {
    console.error('分析交割单失败:', error)
    elMessage.error('分析交割单失败')
  } finally {
    loading.value = false
  }
}

// 渲染交易图表
const renderChart = () => {
  if (!analysisData.value || analysisData.value.length === 0) return

  if (!chartInstance) {
    chartInstance = echarts.init(transactionChart.value)
  }

  // 处理数据
  const dates = analysisData.value.map(item => item.tradeDate)
  const buyPrices = analysisData.value.map(item => item.tradeType === '买入' ? item.price : null)
  const sellPrices = analysisData.value.map(item => item.tradeType === '卖出' ? item.price : null)
  const quantities = analysisData.value.map(item => item.quantity)

  const option = {
    title: {
      text: '股票交易价格趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>'
        params.forEach(param => {
          if (param.value) {
            result += `${param.seriesName}: ${param.value}`
            if (param.seriesName.includes('价格')) {
              result += '元'
            } else if (param.seriesName.includes('数量')) {
              result += '股'
            }
            result += '<br/>'
          }
        })
        return result
      }
    },
    legend: {
      data: ['买入价格', '卖出价格', '交易数量'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '价格 (元)',
        position: 'left'
      },
      {
        type: 'value',
        name: '数量 (股)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '买入价格',
        type: 'line',
        data: buyPrices,
        symbol: 'circle',
        symbolSize: 8,
        color: '#52c41a',
        smooth: true
      },
      {
        name: '卖出价格',
        type: 'line',
        data: sellPrices,
        symbol: 'circle',
        symbolSize: 8,
        color: '#ff4d4f',
        smooth: true
      },
      {
        name: '交易数量',
        type: 'bar',
        data: quantities,
        yAxisIndex: 1,
        color: '#1890ff',
        opacity: 0.3
      }
    ]
  }

  chartInstance.setOption(option)
}

// 监听窗口大小变化，调整图表
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 生命周期钩子
onMounted(() => {
  fetchAvailableStocks()
  window.addEventListener('resize', handleResize)
})

// 组件卸载前清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
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