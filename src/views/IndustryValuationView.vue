<template>
  <div class="industry-valuation">
    <h2>行业估值分析</h2>
    
    <!-- 行业选择器 -->
    <el-select v-model="selectedIndustry" placeholder="选择行业" class="industry-select">
      <el-option v-for="industry in industries" :key="industry.code" :label="industry.name" :value="industry.code" />
    </el-select>
    
    <!-- 估值概览卡片 -->
    <div class="overview-cards">
      <div class="card">
        <h3>当前PE</h3>
        <p class="value">{{ valuationData.pe || '--' }}</p>
        <p class="change" :class="{ positive: valuationData.peChange > 0, negative: valuationData.peChange < 0 }">
          {{ valuationData.peChange > 0 ? '+' : '' }}{{ valuationData.peChange }}%
        </p>
      </div>
      <div class="card">
        <h3>当前PB</h3>
        <p class="value">{{ valuationData.pb || '--' }}</p>
        <p class="change" :class="{ positive: valuationData.pbChange > 0, negative: valuationData.pbChange < 0 }">
          {{ valuationData.pbChange > 0 ? '+' : '' }}{{ valuationData.pbChange }}%
        </p>
      </div>
      <div class="card">
        <h3>PE-历史分位</h3>
        <p class="value">{{ valuationData.pePercentile || '--' }}%</p>
        <p class="status" :class="getPercentileStatus(valuationData.pePercentile)">{{ getPercentileText(valuationData.pePercentile) }}</p>
      </div>
      <div class="card">
        <h3>PB-历史分位</h3>
        <p class="value">{{ valuationData.pbPercentile || '--' }}%</p>
        <p class="status" :class="getPercentileStatus(valuationData.pbPercentile)">{{ getPercentileText(valuationData.pbPercentile) }}</p>
      </div>
    </div>
    
    <!-- 估值走势图 -->
    <div class="chart-container">
      <h3>估值历史走势</h3>
      <div ref="chartRef" class="chart"></div>
    </div>
    
    <!-- 估值对比表格 -->
    <div class="comparison-table">
      <h3>行业估值横向对比</h3>
      <el-table :data="industryComparison" stripe style="width: 100%">
        <el-table-column prop="industryName" label="行业" width="180" />
        <el-table-column prop="pe" label="PE" sortable />
        <el-table-column prop="pb" label="PB" sortable />
        <el-table-column prop="pePercentile" label="PE-分位" sortable />
        <el-table-column prop="pbPercentile" label="PB-分位" sortable />
        <el-table-column prop="valuationLevel" label="估值水平" :formatter="formatValuationLevel" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'

// 模拟数据
const industries = [
  { code: 'bank', name: '银行业' },
  { code: 'tech', name: '科技业' },
  { code: 'consumption', name: '消费品' },
  { code: 'medicine', name: '医药业' },
  { code: 'realestate', name: '房地产' }
]

const selectedIndustry = ref('bank')
const valuationData = ref({
  pe: 5.8,
  pb: 0.65,
  peChange: -2.3,
  pbChange: -1.5,
  pePercentile: 15,
  pbPercentile: 10
})

const industryComparison = ref([
  { industryName: '银行业', pe: 5.8, pb: 0.65, pePercentile: 15, pbPercentile: 10, valuationLevel: '低估' },
  { industryName: '科技业', pe: 35.2, pb: 4.2, pePercentile: 65, pbPercentile: 70, valuationLevel: '合理' },
  { industryName: '消费品', pe: 28.5, pb: 3.8, pePercentile: 45, pbPercentile: 50, valuationLevel: '合理' },
  { industryName: '医药业', pe: 22.3, pb: 3.1, pePercentile: 30, pbPercentile: 35, valuationLevel: '合理偏低' },
  { industryName: '房地产', pe: 12.5, pb: 0.9, pePercentile: 20, pbPercentile: 15, valuationLevel: '低估' }
])

const chartRef = ref<HTMLElement>()
let chartInstance: ECharts | null = null

// 获取分位状态
const getPercentileStatus = (percentile?: number) => {
  if (!percentile) return ''
  if (percentile < 30) return 'undervalued'
  if (percentile > 70) return 'overvalued'
  return 'reasonable'
}

// 获取分位文本
const getPercentileText = (percentile?: number) => {
  if (!percentile) return '--'
  if (percentile < 30) return '低估区间'
  if (percentile > 70) return '高估区间'
  return '合理区间'
}

// 格式化估值水平
const formatValuationLevel = ({ row }: any) => {
  const level = row.valuationLevel
  let className = ''
  switch (level) {
    case '低估': className = 'text-success'; break
    case '合理偏低': className = 'text-info'; break
    case '合理': className = 'text-primary'; break
    case '合理偏高': className = 'text-warning'; break
    case '高估': className = 'text-danger'; break
  }
  return `<span class="${className}">${level}</span>`
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: '行业估值历史走势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['PE', 'PB'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06', '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12']
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
        data: [6.2, 6.0, 5.9, 6.1, 5.9, 5.7, 5.6, 5.8, 5.7, 5.9, 5.8, 5.8],
        smooth: true
      },
      {
        name: 'PB',
        type: 'line',
        data: [0.72, 0.70, 0.68, 0.69, 0.67, 0.65, 0.64, 0.66, 0.65, 0.67, 0.66, 0.65],
        smooth: true
      }
    ]
  }
  
  chartInstance.setOption(option)
}

// 监听行业变化
watch(selectedIndustry, () => {
  // 在实际应用中，这里会根据选择的行业重新获取数据
  console.log('行业变化:', selectedIndustry.value)
  // 模拟数据更新
  setTimeout(() => {
    if (selectedIndustry.value === 'tech') {
      valuationData.value = {
        pe: 35.2,
        pb: 4.2,
        peChange: 1.2,
        pbChange: 0.8,
        pePercentile: 65,
        pbPercentile: 70
      }
    } else if (selectedIndustry.value === 'consumption') {
      valuationData.value = {
        pe: 28.5,
        pb: 3.8,
        peChange: -0.5,
        pbChange: -0.3,
        pePercentile: 45,
        pbPercentile: 50
      }
    } else if (selectedIndustry.value === 'medicine') {
      valuationData.value = {
        pe: 22.3,
        pb: 3.1,
        peChange: -1.2,
        pbChange: -0.8,
        pePercentile: 30,
        pbPercentile: 35
      }
    } else if (selectedIndustry.value === 'realestate') {
      valuationData.value = {
        pe: 12.5,
        pb: 0.9,
        peChange: 2.5,
        pbChange: 1.8,
        pePercentile: 20,
        pbPercentile: 15
      }
    } else {
      valuationData.value = {
        pe: 5.8,
        pb: 0.65,
        peChange: -2.3,
        pbChange: -1.5,
        pePercentile: 15,
        pbPercentile: 10
      }
    }
  }, 300)
})

onMounted(() => {
  initChart()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
})
</script>

<style scoped>
.industry-valuation {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #3059a7;
}

.industry-select {
  width: 200px;
  margin-bottom: 20px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.card {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.card h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #606266;
}

.card .value {
  margin: 0 0 5px 0;
  font-size: 24px;
  font-weight: bold;
  color: #3059a7;
}

.card .change {
  margin: 0;
  font-size: 14px;
}

.card .change.positive {
  color: #f56c6c;
}

.card .change.negative {
  color: #67c23a;
}

.card .status {
  margin: 0;
  font-size: 14px;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
}

.card .status.undervalued {
  background-color: #f0f9ff;
  color: #67c23a;
}

.card .status.reasonable {
  background-color: #f0f2f5;
  color: #3059a7;
}

.card .status.overvalued {
  background-color: #fef0f0;
  color: #f56c6c;
}

.chart-container {
  margin-bottom: 30px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
  margin: 0 0 20px 0;
  color: #3059a7;
}

.chart {
  width: 100%;
  height: 400px;
}

.comparison-table {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comparison-table h3 {
  margin: 0 0 20px 0;
  color: #3059a7;
}

.text-success {
  color: #67c23a;
}

.text-info {
  color: #909399;
}

.text-primary {
  color: #3059a7;
}

.text-warning {
  color: #e6a23c;
}

.text-danger {
  color: #f56c6c;
}
</style>