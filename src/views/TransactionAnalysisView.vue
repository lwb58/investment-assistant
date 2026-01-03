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
              :value="String(stock.value || '')"
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
              <el-tag 
                :type="getTradeTypeTagType(scope.row.tradeType)"
                :style="getTradeTypeTagStyle(scope.row.tradeType)"
              >
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
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
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

// 根据交易类型获取标签类型
const getTradeTypeTagType = (tradeType) => {
  switch(tradeType) {
    case '买入':
      return 'success'; // 绿色
    case '证券买入':
      return 'danger'; // 红色
    default:
      return ''; // 默认不使用预定义类型
  }
}

// 根据交易类型获取标签样式
const getTradeTypeTagStyle = (tradeType) => {
  switch(tradeType) {
    case '证券卖出':
      return 'background-color: #333333; border-color: #333333; color: white;'; // 黑色背景
    case '卖出':
      return 'background-color: #333333; border-color: #333333; color: white;'; // 黑色背景
    default:
      return ''; // 默认不使用自定义样式
  }
}

// 获取可用股票列表
const fetchAvailableStocks = async () => {
  try {
    console.log('开始调用getTransactionStocks API')
    const result = await apiService.getTransactionStocks()
    console.log('Transaction stocks result:', result)
    console.log('Options data:', result.options)
    console.log('Options data length:', result.options ? result.options.length : 0)
    
    if (result.options && Array.isArray(result.options)) {
      availableStocks.value = result.options
      console.log('Available stocks:', availableStocks.value)
      console.log('Available stocks length:', availableStocks.value.length)
      
      // 如果有股票数据，默认选择第一个
      if (availableStocks.value.length > 0 && !selectedStock.value) {
        selectedStock.value = availableStocks.value[0].value
        console.log('默认选择第一个股票:', selectedStock.value)
      }
    } else {
      console.error('API返回的数据格式不正确:', result)
      availableStocks.value = []
    }
  } catch (error) {
    console.error('获取股票列表失败:', error)
    console.error('Error details:', error.response ? error.response.data : error.message)
    elMessage.error('获取股票列表失败')
    availableStocks.value = []
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
    // 使用nextTick确保DOM更新完成后再渲染图表
    nextTick(() => {
      renderChart()
    })
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
  
  // 确保DOM已经完全加载
  if (!transactionChart.value) {
    console.error('交易图表DOM元素未找到')
    return
  }

  if (!chartInstance) {
    chartInstance = echarts.init(transactionChart.value)
  }

  // 处理数据
  const dates = analysisData.value.map(item => item.tradeDate)
  
  // 分离买入和卖出数据，并处理负数量
  const buyPrices = []
  const sellPrices = []
  const quantities = []
  
  analysisData.value.forEach(item => {
    if (item.tradeType === '买入' || item.tradeType === '证券买入') {
      buyPrices.push(item.price)
      sellPrices.push(null)
      quantities.push(item.quantity)
    } else if (item.tradeType === '卖出' || item.tradeType === '证券卖出') {
      buyPrices.push(null)
      sellPrices.push(item.price)
      quantities.push(Math.abs(item.quantity)) // 显示卖出数量的绝对值
    } else {
      buyPrices.push(null)
      sellPrices.push(null)
      quantities.push(0)
    }
  })

  const option = {
    title: {
      text: '股票交易价格与数量趋势',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#ddd',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      formatter: function(params) {
        const validParams = params.filter(param => param.value)
        if (validParams.length === 0) return ''
        
        return `
          <div style="padding: 8px;">
            <strong>${validParams[0].axisValue}</strong><br/>
            ${validParams.map(param => {
              const unit = param.seriesName.includes('价格') ? '元' : '股'
              return `
                <div style="margin-top: 4px;">
                  <span style="display: inline-block; width: 10px; height: 10px; background: ${param.color}; border-radius: 50%; margin-right: 5px;"></span>
                  ${param.seriesName}: <strong>${param.value}${unit}</strong>
                </div>
              `
            }).join('')}
          </div>
        `
      }
    },
    legend: {
      data: ['买入价格', '卖出价格', '交易数量'],
      bottom: 0,
      textStyle: {
        fontSize: 12
      },
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
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        rotate: 45,
        fontSize: 11,
        color: '#666'
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#f5f5f5',
          type: 'dashed'
        }
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '价格 (元)',
        position: 'left',
        axisLine: {
          lineStyle: {
            color: '#52c41a'
          }
        },
        axisLabel: {
          formatter: '{value}',
          color: '#666',
          fontSize: 11
        },
        splitLine: {
          show: true,
          lineStyle: {
            color: '#f5f5f5',
            type: 'dashed'
          }
        },
        nameTextStyle: {
          color: '#333',
          fontSize: 12
        }
      },
      {
        type: 'value',
        name: '数量 (股)',
        position: 'right',
        axisLine: {
          lineStyle: {
            color: '#1890ff'
          }
        },
        axisLabel: {
          formatter: '{value}',
          color: '#666',
          fontSize: 11
        },
        splitLine: {
          show: false
        },
        nameTextStyle: {
          color: '#333',
          fontSize: 12
        }
      }
    ],
    series: [
      {
        name: '买入价格',
        type: 'line',
        data: buyPrices,
        symbol: 'circle',
        symbolSize: 10,
        color: '#52c41a',
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#52c41a'
        },
        itemStyle: {
          color: '#52c41a',
          borderColor: '#fff',
          borderWidth: 2
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
            { offset: 1, color: 'rgba(82, 196, 26, 0.05)' }
          ])
        }
      },
      {
        name: '卖出价格',
        type: 'line',
        data: sellPrices,
        symbol: 'circle',
        symbolSize: 10,
        color: '#ff4d4f',
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#ff4d4f'
        },
        itemStyle: {
          color: '#ff4d4f',
          borderColor: '#fff',
          borderWidth: 2
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 77, 79, 0.3)' },
            { offset: 1, color: 'rgba(255, 77, 79, 0.05)' }
          ])
        }
      },
      {
        name: '交易数量',
        type: 'bar',
        data: quantities,
        yAxisIndex: 1,
        itemStyle: {
          color: function(params) {
            // 为买入和卖出数量设置不同颜色
            const index = params.dataIndex
            if (buyPrices[index] !== null) {
              return '#1890ff' // 买入数量为蓝色
            } else if (sellPrices[index] !== null) {
              return '#fa8c16' // 卖出数量为橙色
            } else {
              return '#d9d9d9' // 其他为灰色
            }
          },
          opacity: 0.8
        },
        emphasis: {
          itemStyle: {
            opacity: 1
          }
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}股',
          fontSize: 11,
          color: '#666'
        }
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