<template>
  <div class="valuation-decision">
    <h2>估值决策系统</h2>
    
    <!-- 股票选择器 -->
    <div class="stock-selector">
      <el-select v-model="selectedStockId" placeholder="选择股票" class="stock-select" @change="loadStockData">
        <el-option v-for="stock in stockList" :key="stock.id" :label="stock.name + '(' + stock.code + ')'" :value="stock.id" />
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
import valuationService from '../services/valuationService';

// 初始空数据
const stockList = ref<any[]>([])
const selectedStockId = ref('')
const selectedStock = ref<any>(null)

const comparisonList = ref<any[]>([])  
const showAddButton = ref(true)
const activeModel = ref('dcf')
const loading = ref(false)
const error = ref<string | null>(null)

// 图表引用
const dcfChartRef = ref<HTMLElement | null>(null)
const historicalChartRef = ref<HTMLElement | null>(null)
let dcfChartInstance: ECharts | undefined
let historicalChartInstance: ECharts | undefined

// 评分数据
const scoreData = ref({
  total: 0,
  fundamental: 0,
  growth: 0,
  valuation: 0,
  technical: 0
})

// 相对估值汇总
const relativeSummary = ref({
  avgPE: 0,
  avgPB: 0,
  avgPS: 0,
  avgEVToEbitda: 0,
  targetPricePE: 0,
  targetPricePB: 0
})

// 相对估值参数
const relativeParams = ref({
  benchmarkType: 'industry',
  benchmark: ''
})

// 相对估值数据
const relativeValuationData = ref<any[]>([])

// DCF参数 - 使用小数形式而不是百分比
const dcfParams = ref({
  forecastYears: 10,
  growthRate: 0.12, // 12%
  discountRate: 0.15, // 15%
  terminalGrowthRate: 0.03 // 3%
})

const dcfResult = ref<any>(null)
const valuationResult = ref<any>(null)
const historicalValuation = ref<any[]>([])

// 加载股票数据
const loadStockData = async (symbol: string) => {
  try {
    loading.value = true;
    error.value = null;
    
    // 重置之前的结果
    dcfResult.value = null;
    valuationResult.value = null;
    
    // 从API获取股票详细信息
    const stockData = await valuationService.getStockInfo(symbol);
    selectedStock.value = stockData;
    
    // 获取历史估值数据
    await loadHistoricalValuation(symbol);
    
    // 获取相对估值数据
    await loadRelativeValuation(symbol);
    
    // 获取评分数据
    await loadScoreData(symbol);
  } catch (err) {
    console.error('加载股票数据失败:', err);
    error.value = '加载股票数据失败，请重试';
  } finally {
    loading.value = false;
  }
}

// 加载相对估值数据
const loadRelativeValuation = async (symbol: string) => {
  try {
    const data = await valuationService.getRelativeValuation(symbol);
    relativeValuationData.value = data.comparisonCompanies || [];
    relativeSummary.value = {
      avgPE: data.industryAverages?.pe || 0,
      avgPB: data.industryAverages?.pb || 0,
      avgPS: data.industryAverages?.ps || 0,
      avgEVToEbitda: data.industryAverages?.evToEbitda || 0,
      targetPricePE: data.targetPrices?.peBased || 0,
      targetPricePB: data.targetPrices?.pbBased || 0
    };
  } catch (err) {
    console.error('加载相对估值失败:', err);
  }
}

// 加载评分数据
const loadScoreData = async (symbol: string) => {
  try {
    const data = await valuationService.getScoreData(symbol);
    scoreData.value = data || {
      total: 0,
      fundamental: 0,
      growth: 0,
      valuation: 0,
      technical: 0
    };
  } catch (err) {
    console.error('加载评分数据失败:', err);
  }
}

// 加载历史估值数据
const loadHistoricalValuation = async (symbol: string) => {
  try {
    const history = await valuationService.getValuationHistory(symbol);
    historicalValuation.value = history || [];
    await nextTick();
    renderHistoricalChart();
  } catch (err) {
    console.error('加载历史估值失败:', err);
    historicalValuation.value = [];
  }
}

// 计算估值
const calculateValuation = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    // 转换参数格式
    const params = {
      growthRate: dcfParams.value.growthRate,
      discountRate: dcfParams.value.discountRate,
      terminalGrowthRate: dcfParams.value.terminalGrowthRate,
      years: dcfParams.value.forecastYears,
      weights: {
        dcf: 0.4,
        fcf: 0.3,
        buffett: 0.3
      }
    };
    
    // 调用估值服务
    const result = await valuationService.calculateValuation(selectedStockId.value, params);
    valuationResult.value = result;
    
    // 添加类型断言以避免TypeScript错误
    const typedResult = result as any;
    
    // 更新DCF结果显示
    if (typedResult.dcf) {
      dcfResult.value = {
        enterpriseValue: typedResult.dcf.intrinsicValue,
        equityValue: typedResult.dcf.intrinsicValue,
        perShareValue: typedResult.intrinsicValue,
        valuation: typedResult.marginOfSafety > 0 ? 'undervalued' : 'overvalued',
        percentDiff: typedResult.marginOfSafety
      };
    }
    
    // 更新当前股价
    if (typedResult.currentPrice) {
      selectedStock.value.currentPrice = typedResult.currentPrice;
    }
    
    // 刷新历史数据
    await loadHistoricalValuation(selectedStockId.value);
    
    // 更新图表
    await nextTick();
    renderDCFChart();
  } catch (err) {
    console.error('计算估值失败:', err);
    error.value = '计算估值失败，请检查参数或重试';
  } finally {
    loading.value = false;
  }
}

// 计算DCF估值（保持原方法名称兼容性）
const calculateDCF = calculateValuation;

// 格式化货币
const formatCurrency = (value: number | undefined) => {
  if (value === undefined || value === null) return '-';
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

// 获取建议类名
const getSuggestionClass = (score: number) => {
  if (score >= 80) return 'excellent';
  if (score >= 70) return 'good';
  if (score >= 60) return 'fair';
  return 'poor';
};

// 获取建议标题
const getSuggestionTitle = (score: number) => {
  if (score >= 80) return '强烈推荐';
  if (score >= 70) return '推荐';
  if (score >= 60) return '谨慎推荐';
  return '不推荐';
};

// 获取建议内容
const getSuggestionContent = (score: number) => {
  if (score >= 80) return '该股票在基本面、成长性、估值和技术面表现优异，具备较高的投资价值。';
  if (score >= 70) return '该股票整体表现良好，基本面稳定，建议考虑适量配置。';
  if (score >= 60) return '该股票表现一般，存在一定风险，建议谨慎考虑，等待更合适的入场时机。';
  return '该股票表现不佳，建议暂不考虑投资，可继续观察。';
};

// 渲染DCF图表
const renderDCFChart = () => {
  if (!dcfChartRef.value || !valuationResult.value?.dcf?.cashFlows) return;
  
  if (dcfChartInstance) {
    dcfChartInstance.dispose();
  }
  
  dcfChartInstance = echarts.init(dcfChartRef.value);
  const cashFlows = valuationResult.value.dcf.cashFlows;
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['自由现金流', '现值']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: cashFlows.map((item: any) => `第${item.year}年`)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '自由现金流',
        type: 'bar',
        data: cashFlows.map((item: any) => item.fcf.toFixed(2)),
        itemStyle: {
          color: '#5470c6'
        }
      },
      {
        name: '现值',
        type: 'bar',
        data: cashFlows.map((item: any) => item.presentValue.toFixed(2)),
        itemStyle: {
          color: '#91cc75'
        }
      }
    ]
  };
  
  dcfChartInstance.setOption(option);
};

// 渲染历史估值图表
const renderHistoricalChart = () => {
  if (!historicalChartRef.value || historicalValuation.value.length === 0) return;
  
  if (historicalChartInstance) {
    historicalChartInstance.dispose();
  }
  
  historicalChartInstance = echarts.init(historicalChartRef.value);
  
  const dates = historicalValuation.value.map(item => 
    new Date(item.valuation_date).toLocaleDateString('zh-CN')
  );
  const intrinsicValues = historicalValuation.value.map(item => item.intrinsic_value);
  const currentPrices = historicalValuation.value.map(item => item.current_price);
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['内在价值', '市场价格']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '内在价值',
        type: 'line',
        data: intrinsicValues,
        itemStyle: {
          color: '#5470c6'
        },
        smooth: true
      },
      {
        name: '市场价格',
        type: 'line',
        data: currentPrices,
        itemStyle: {
          color: '#ee6666'
        },
        smooth: true
      }
    ]
  };
  
  historicalChartInstance.setOption(option);
};

// 组件挂载时初始化
onMounted(async () => {
  // 组件挂载后加载股票列表
  try {
    loading.value = true;
    const stocks = await valuationService.getStockList();
    stockList.value = stocks || [];
  } catch (err) {
    console.error('加载股票列表失败:', err);
    stockList.value = [];
  } finally {
    loading.value = false;
  }
  
  // 初始化图表
  window.addEventListener('resize', () => {
    dcfChartInstance?.resize();
    historicalChartInstance?.resize();
  });
});

// 监听历史估值数据变化，重新渲染图表
watch(historicalValuation, () => {
  nextTick(() => {
    renderHistoricalChart();
  });
});

// 监听估值结果变化，重新渲染DCF图表
watch(valuationResult, () => {
  nextTick(() => {
    renderDCFChart();
  });
});

// 添加到对比列表
const addStockToList = () => {
  if (comparisonList.value.find(item => item.id === selectedStock.value.id)) {
    return;
  }
  
  comparisonList.value.push({ ...selectedStock.value });
  showAddButton.value = false;
};

// 从对比列表移除
const removeStockFromList = (id: string) => {
  comparisonList.value = comparisonList.value.filter(item => item.id !== id);
  showAddButton.value = true;
};

// 开始对比分析
const startComparison = () => {
  // 对比分析逻辑
  console.log('开始对比分析:', comparisonList.value);
};
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