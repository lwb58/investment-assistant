<template>
  <div class="stock-analysis-container">
    <div class="header">
      <button @click="goBack" class="back-button">返回</button>
      <h1>股票分析 - {{ stockInfo.name }}</h1>
      <div class="stock-info-header">
        <span class="stock-code">{{ stockInfo.code }}</span>
        <span class="stock-market">{{ stockInfo.market }}</span>
      </div>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else>
      <!-- 分析类型选择 -->
      <div class="analysis-tabs">
        <div 
          class="tab-item" 
          :class="activeTab === 'valuation' ? 'active' : ''"
          @click="activeTab = 'valuation'"
        >
          估值分析
        </div>
        <div 
          class="tab-item" 
          :class="activeTab === 'fundamental' ? 'active' : ''"
          @click="activeTab = 'fundamental'"
        >
          基本面分析
        </div>
        <div 
          class="tab-item" 
          :class="activeTab === 'events' ? 'active' : ''"
          @click="activeTab = 'events'"
        >
          事件分析
        </div>
      </div>
      
      <!-- 估值分析面板 -->
      <div v-if="activeTab === 'valuation'" class="tab-content">
        <div class="valuation-analysis">
          <div class="valuation-metrics">
            <h3>估值指标</h3>
            <div class="metrics-grid">
              <div class="metric-item">
                <span class="label">市盈率(TTM):</span>
                <span class="value">{{ valuationData.peTTM || '-' }}</span>
                <span class="status" :class="getPEStatus(valuationData.peTTM)">{{ getPEStatusText(valuationData.peTTM) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">市净率:</span>
                <span class="value">{{ valuationData.pbMRQ || '-' }}</span>
                <span class="status" :class="getPBStatus(valuationData.pbMRQ)">{{ getPBStatusText(valuationData.pbMRQ) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">市销率:</span>
                <span class="value">{{ valuationData.psTTM || '-' }}</span>
                <span class="status" :class="getPSStatus(valuationData.psTTM)">{{ getPSStatusText(valuationData.psTTM) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">股息率:</span>
                <span class="value">{{ valuationData.dividendRate || '-' }}%</span>
                <span class="status" :class="getDividendStatus(valuationData.dividendRate)">{{ getDividendStatusText(valuationData.dividendRate) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">PEG比率:</span>
                <span class="value">{{ valuationData.pegRatio || '-' }}</span>
                <span class="status" :class="getPEGStatus(valuationData.pegRatio)">{{ getPEGStatusText(valuationData.pegRatio) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">企业价值倍数:</span>
                <span class="value">{{ valuationData.evToEbitda || '-' }}</span>
                <span class="status" :class="getEVStatus(valuationData.evToEbitda)">{{ getEVStatusText(valuationData.evToEbitda) }}</span>
              </div>
            </div>
          </div>
          
          <div class="dcf-analysis">
            <h3>DCF估值模型</h3>
            <div class="dcf-params">
              <div class="param-group">
                <label>预期增长率 (%):</label>
                <input type="number" v-model.number="dcfParams.growthRate" @change="calculateDCF">
              </div>
              <div class="param-group">
                <label>折现率 (%):</label>
                <input type="number" v-model.number="dcfParams.discountRate" @change="calculateDCF">
              </div>
              <div class="param-group">
                <label>永续增长率 (%):</label>
                <input type="number" v-model.number="dcfParams.perpetualGrowth" @change="calculateDCF">
              </div>
            </div>
            
            <div class="dcf-results">
              <div class="result-item">
                <span class="label">内在价值:</span>
                <span class="value">¥{{ dcfResult.intrinsicValue || '-' }}</span>
              </div>
              <div class="result-item">
                <span class="label">当前价格:</span>
                <span class="value">¥{{ stockInfo.price }}</span>
              </div>
              <div class="result-item">
                <span class="label">低估/高估幅度:</span>
                <span class="value" :class="dcfResult.valuationGap > 0 ? 'undervalued' : 'overvalued'">
                  {{ dcfResult.valuationGap > 0 ? '+' : '' }}{{ dcfResult.valuationGap || 0 }}%
                </span>
              </div>
              <div class="result-item">
                <span class="label">估值结论:</span>
                <span class="value" :class="getValuationConclusionClass(dcfResult.valuationGap)">
                  {{ getValuationConclusion(dcfResult.valuationGap) }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="valuation-comparison">
            <h3>历史估值对比</h3>
            <div class="historical-data">
              <div class="chart-container">
                <!-- 这里可以集成图表组件，如ECharts或Chart.js -->
                <div class="chart-placeholder">历史PE/PB走势图</div>
              </div>
              <div class="percentiles">
                <div class="percentile-item">
                  <span class="label">PE当前分位点:</span>
                  <span class="value">{{ valuationData.pePercentile || '-' }}%</span>
                </div>
                <div class="percentile-item">
                  <span class="label">PB当前分位点:</span>
                  <span class="value">{{ valuationData.pbPercentile || '-' }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 基本面分析面板 -->
      <div v-if="activeTab === 'fundamental'" class="tab-content">
        <div class="fundamental-analysis">
          <div class="financial-growth">
            <h3>财务增长</h3>
            <div class="metrics-grid">
              <div class="metric-item">
                <span class="label">营收增长率:</span>
                <span class="value">{{ fundamentalData.revenueGrowth || '-' }}%</span>
                <span class="trend" :class="getTrendClass(fundamentalData.revenueGrowth)">{{ getTrendText(fundamentalData.revenueGrowth) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">净利润增长率:</span>
                <span class="value">{{ fundamentalData.netProfitGrowth || '-' }}%</span>
                <span class="trend" :class="getTrendClass(fundamentalData.netProfitGrowth)">{{ getTrendText(fundamentalData.netProfitGrowth) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">毛利率变化:</span>
                <span class="value">{{ fundamentalData.grossMarginChange || '-' }}%</span>
                <span class="trend" :class="getTrendClass(fundamentalData.grossMarginChange)">{{ getTrendText(fundamentalData.grossMarginChange) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">净利率变化:</span>
                <span class="value">{{ fundamentalData.netMarginChange || '-' }}%</span>
                <span class="trend" :class="getTrendClass(fundamentalData.netMarginChange)">{{ getTrendText(fundamentalData.netMarginChange) }}</span>
              </div>
            </div>
          </div>
          
          <div class="profitability">
            <h3>盈利能力</h3>
            <div class="metrics-grid">
              <div class="metric-item">
                <span class="label">净资产收益率(ROE):</span>
                <span class="value">{{ fundamentalData.roe || '-' }}%</span>
                <span class="status" :class="getROEStatus(fundamentalData.roe)">{{ getROEStatusText(fundamentalData.roe) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">总资产收益率(ROA):</span>
                <span class="value">{{ fundamentalData.roa || '-' }}%</span>
                <span class="status" :class="getROAStatus(fundamentalData.roa)">{{ getROAStatusText(fundamentalData.roa) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">投入资本回报率(ROIC):</span>
                <span class="value">{{ fundamentalData.roic || '-' }}%</span>
                <span class="status" :class="getROICStatus(fundamentalData.roic)">{{ getROICStatusText(fundamentalData.roic) }}</span>
              </div>
            </div>
          </div>
          
          <div class="financial-health">
            <h3>财务健康</h3>
            <div class="metrics-grid">
              <div class="metric-item">
                <span class="label">资产负债率:</span>
                <span class="value">{{ fundamentalData.debtToAsset || '-' }}%</span>
                <span class="status" :class="getDebtStatus(fundamentalData.debtToAsset)">{{ getDebtStatusText(fundamentalData.debtToAsset) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">流动比率:</span>
                <span class="value">{{ fundamentalData.currentRatio || '-' }}</span>
                <span class="status" :class="getCurrentRatioStatus(fundamentalData.currentRatio)">{{ getCurrentRatioStatusText(fundamentalData.currentRatio) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">速动比率:</span>
                <span class="value">{{ fundamentalData.quickRatio || '-' }}</span>
                <span class="status" :class="getQuickRatioStatus(fundamentalData.quickRatio)">{{ getQuickRatioStatusText(fundamentalData.quickRatio) }}</span>
              </div>
              <div class="metric-item">
                <span class="label">经营现金流:</span>
                <span class="value">¥{{ fundamentalData.operatingCashFlow || '-' }}亿</span>
                <span class="trend" :class="getTrendClass(fundamentalData.operatingCashFlowTrend)">{{ getTrendText(fundamentalData.operatingCashFlowTrend) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 事件分析面板 -->
      <div v-if="activeTab === 'events'" class="tab-content">
        <div class="events-analysis">
          <h3>最新事件</h3>
          <div v-if="eventsData.length === 0" class="no-events">暂无事件数据</div>
          <div v-else class="events-list">
            <div v-for="event in eventsData" :key="event.id" class="event-item">
              <div class="event-header">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-date">{{ formatDate(event.date) }}</div>
              </div>
              <div class="event-content">{{ event.content }}</div>
              <div class="event-impact" :class="event.impact">
                影响程度: {{ getImpactText(event.impact) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apiService } from '../services/apiService';

interface StockInfo {
  code: string;
  name: string;
  market: string;
  price: string;
}

interface ValuationData {
  peTTM?: string;
  pbMRQ?: string;
  psTTM?: string;
  dividendRate?: string;
  pegRatio?: string;
  evToEbitda?: string;
  pePercentile?: string;
  pbPercentile?: string;
}

interface FundamentalData {
  revenueGrowth?: string;
  netProfitGrowth?: string;
  grossMarginChange?: string;
  netMarginChange?: string;
  roe?: string;
  roa?: string;
  roic?: string;
  debtToAsset?: string;
  currentRatio?: string;
  quickRatio?: string;
  operatingCashFlow?: string;
  operatingCashFlowTrend?: number;
}

interface EventData {
  id: string;
  title: string;
  content: string;
  date: string;
  impact: 'high' | 'medium' | 'low';
}

interface DCFParams {
  growthRate: number;
  discountRate: number;
  perpetualGrowth: number;
}

interface DCFResult {
  intrinsicValue?: string;
  valuationGap?: number;
}

const route = useRoute();
const router = useRouter();
const stockCode = route.params.code as string;
const stockInfo = ref<StockInfo>({ code: stockCode, name: '', market: '', price: '0' });
const valuationData = ref<ValuationData>({});
const fundamentalData = ref<FundamentalData>({});
const eventsData = ref<EventData[]>([]);
const loading = ref(true);
const error = ref('');
const activeTab = ref('valuation');

// DCF模型参数
const dcfParams = ref<DCFParams>({
  growthRate: 15,
  discountRate: 12,
  perpetualGrowth: 3
});
const dcfResult = ref<DCFResult>({});

const fetchAnalysisData = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    // 获取股票基本信息
    const stockResponse = await apiService.stockApi.getStockDetail(stockCode);
    const stockData = stockResponse.data;
    stockInfo.value = {
      code: stockData.code,
      name: stockData.name,
      market: stockData.market,
      price: stockData.price
    };
    
    // 获取估值数据
    const valuationResponse = await apiService.valuationApi.getValuationData(stockCode);
    valuationData.value = valuationResponse.data;
    
    // 获取基本面数据
    const fundamentalResponse = await apiService.valuationApi.getFundamentalData(stockCode);
    fundamentalData.value = fundamentalResponse.data;
    
    // 获取事件数据
    const eventsResponse = await apiService.valuationApi.getEventsData(stockCode);
    eventsData.value = eventsResponse.data || [];
    
    // 初始化DCF计算
    calculateDCF();
  } catch (err) {
    error.value = '获取分析数据失败，请稍后重试';
    console.error('获取分析数据失败:', err);
  } finally {
    loading.value = false;
  }
};

const calculateDCF = () => {
  // 简化的DCF计算模型
  // 实际应用中应该使用更复杂的现金流预测
  const currentPrice = parseFloat(stockInfo.value.price);
  const growthRate = dcfParams.value.growthRate / 100;
  const discountRate = dcfParams.value.discountRate / 100;
  const perpetualGrowth = dcfParams.value.perpetualGrowth / 100;
  
  // 假设当前每股收益
  const eps = parseFloat(valuationData.value.peTTM || '20') ? currentPrice / parseFloat(valuationData.value.peTTM || '20') : 1;
  
  // 预测未来5年的EPS
  let presentValue = 0;
  for (let i = 1; i <= 5; i++) {
    const futureEPS = eps * Math.pow(1 + growthRate, i);
    presentValue += futureEPS / Math.pow(1 + discountRate, i);
  }
  
  // 计算终值
  const terminalValue = (eps * Math.pow(1 + growthRate, 5) * (1 + perpetualGrowth)) / (discountRate - perpetualGrowth);
  const presentTerminalValue = terminalValue / Math.pow(1 + discountRate, 5);
  
  // 计算内在价值
  const intrinsicValue = presentValue + presentTerminalValue;
  const valuationGap = ((intrinsicValue - currentPrice) / currentPrice) * 100;
  
  dcfResult.value = {
    intrinsicValue: intrinsicValue.toFixed(2),
    valuationGap: valuationGap.toFixed(2) as unknown as number
  };
};

// 辅助函数：获取估值指标状态
const getPEStatus = (pe: string | undefined) => {
  const peNum = parseFloat(pe || '');
  if (peNum > 0 && peNum < 15) return 'good';
  if (peNum >= 15 && peNum < 30) return 'fair';
  if (peNum >= 30) return 'poor';
  return '';
};

const getPEStatusText = (pe: string | undefined) => {
  const status = getPEStatus(pe);
  const statusMap = { good: '低估值', fair: '合理', poor: '高估值' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getPBStatus = (pb: string | undefined) => {
  const pbNum = parseFloat(pb || '');
  if (pbNum > 0 && pbNum < 2) return 'good';
  if (pbNum >= 2 && pbNum < 5) return 'fair';
  if (pbNum >= 5) return 'poor';
  return '';
};

const getPBStatusText = (pb: string | undefined) => {
  const status = getPBStatus(pb);
  const statusMap = { good: '低估值', fair: '合理', poor: '高估值' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getPSStatus = (ps: string | undefined) => {
  const psNum = parseFloat(ps || '');
  if (psNum > 0 && psNum < 1) return 'good';
  if (psNum >= 1 && psNum < 3) return 'fair';
  if (psNum >= 3) return 'poor';
  return '';
};

const getPSStatusText = (ps: string | undefined) => {
  const status = getPSStatus(ps);
  const statusMap = { good: '低估值', fair: '合理', poor: '高估值' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getDividendStatus = (dividend: string | undefined) => {
  const dividendNum = parseFloat(dividend || '');
  if (dividendNum > 4) return 'good';
  if (dividendNum >= 2 && dividendNum <= 4) return 'fair';
  if (dividendNum < 2) return 'poor';
  return '';
};

const getDividendStatusText = (dividend: string | undefined) => {
  const status = getDividendStatus(dividend);
  const statusMap = { good: '高股息', fair: '中等', poor: '低股息' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getPEGStatus = (peg: string | undefined) => {
  const pegNum = parseFloat(peg || '');
  if (pegNum > 0 && pegNum < 1) return 'good';
  if (pegNum >= 1 && pegNum < 2) return 'fair';
  if (pegNum >= 2) return 'poor';
  return '';
};

const getPEGStatusText = (peg: string | undefined) => {
  const status = getPEGStatus(peg);
  const statusMap = { good: '低估', fair: '合理', poor: '高估' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getEVStatus = (ev: string | undefined) => {
  const evNum = parseFloat(ev || '');
  if (evNum > 0 && evNum < 10) return 'good';
  if (evNum >= 10 && evNum < 20) return 'fair';
  if (evNum >= 20) return 'poor';
  return '';
};

const getEVStatusText = (ev: string | undefined) => {
  const status = getEVStatus(ev);
  const statusMap = { good: '低估值', fair: '合理', poor: '高估值' };
  return statusMap[status as keyof typeof statusMap] || '';
};

// 辅助函数：获取基本面指标状态
const getTrendClass = (value: string | number | undefined) => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (num === undefined || isNaN(num)) return '';
  return num > 0 ? 'positive' : num < 0 ? 'negative' : '';
};

const getTrendText = (value: string | number | undefined) => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (num === undefined || isNaN(num)) return '';
  return num > 0 ? '上升' : num < 0 ? '下降' : '持平';
};

const getROEStatus = (roe: string | undefined) => {
  const roeNum = parseFloat(roe || '');
  if (roeNum > 20) return 'excellent';
  if (roeNum >= 15 && roeNum <= 20) return 'good';
  if (roeNum >= 10 && roeNum < 15) return 'fair';
  if (roeNum < 10) return 'poor';
  return '';
};

const getROEStatusText = (roe: string | undefined) => {
  const status = getROEStatus(roe);
  const statusMap = { excellent: '优秀', good: '良好', fair: '一般', poor: '较差' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getROAStatus = (roa: string | undefined) => {
  const roaNum = parseFloat(roa || '');
  if (roaNum > 10) return 'excellent';
  if (roaNum >= 8 && roaNum <= 10) return 'good';
  if (roaNum >= 5 && roaNum < 8) return 'fair';
  if (roaNum < 5) return 'poor';
  return '';
};

const getROAStatusText = (roa: string | undefined) => {
  const status = getROAStatus(roa);
  const statusMap = { excellent: '优秀', good: '良好', fair: '一般', poor: '较差' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getROICStatus = (roic: string | undefined) => {
  const roicNum = parseFloat(roic || '');
  if (roicNum > 15) return 'excellent';
  if (roicNum >= 10 && roicNum <= 15) return 'good';
  if (roicNum >= 5 && roicNum < 10) return 'fair';
  if (roicNum < 5) return 'poor';
  return '';
};

const getROICStatusText = (roic: string | undefined) => {
  const status = getROICStatus(roic);
  const statusMap = { excellent: '优秀', good: '良好', fair: '一般', poor: '较差' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getDebtStatus = (debt: string | undefined) => {
  const debtNum = parseFloat(debt || '');
  if (debtNum < 40) return 'good';
  if (debtNum >= 40 && debtNum < 60) return 'fair';
  if (debtNum >= 60) return 'poor';
  return '';
};

const getDebtStatusText = (debt: string | undefined) => {
  const status = getDebtStatus(debt);
  const statusMap = { good: '低负债', fair: '中等', poor: '高负债' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getCurrentRatioStatus = (ratio: string | undefined) => {
  const ratioNum = parseFloat(ratio || '');
  if (ratioNum > 2) return 'good';
  if (ratioNum >= 1.5 && ratioNum <= 2) return 'fair';
  if (ratioNum < 1.5) return 'poor';
  return '';
};

const getCurrentRatioStatusText = (ratio: string | undefined) => {
  const status = getCurrentRatioStatus(ratio);
  const statusMap = { good: '流动性好', fair: '一般', poor: '流动性差' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getQuickRatioStatus = (ratio: string | undefined) => {
  const ratioNum = parseFloat(ratio || '');
  if (ratioNum > 1.5) return 'good';
  if (ratioNum >= 1 && ratioNum <= 1.5) return 'fair';
  if (ratioNum < 1) return 'poor';
  return '';
};

const getQuickRatioStatusText = (ratio: string | undefined) => {
  const status = getQuickRatioStatus(ratio);
  const statusMap = { good: '短期偿债能力强', fair: '一般', poor: '短期偿债能力弱' };
  return statusMap[status as keyof typeof statusMap] || '';
};

const getValuationConclusionClass = (gap: number | undefined) => {
  if (gap === undefined) return '';
  if (gap > 20) return 'strongly-undervalued';
  if (gap > 0) return 'undervalued';
  if (gap > -20) return 'overvalued';
  return 'strongly-overvalued';
};

const getValuationConclusion = (gap: number | undefined) => {
  if (gap === undefined) return '无法判断';
  if (gap > 20) return '显著低估';
  if (gap > 0) return '相对低估';
  if (gap > -20) return '相对高估';
  return '显著高估';
};

const getImpactText = (impact: string) => {
  const impactMap = { high: '高', medium: '中', low: '低' };
  return impactMap[impact as keyof typeof impactMap] || '未知';
};

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN');
};

const goBack = () => {
  router.go(-1);
};

onMounted(() => {
  fetchAnalysisData();
});
</script>

<style scoped>
.stock-analysis-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.back-button {
  position: absolute;
  left: 20px;
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: #e0e0e0;
}

.header h1 {
  color: #333;
  margin-bottom: 10px;
}

.stock-info-header {
  display: flex;
  justify-content: center;
  gap: 15px;
  color: #666;
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-message {
  text-align: center;
  padding: 20px;
  color: #e74c3c;
  background-color: #fdf2f2;
  border-radius: 4px;
}

.analysis-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
}

.tab-item {
  padding: 12px 24px;
  cursor: pointer;
  color: #666;
  transition: all 0.3s;
  border-bottom: 3px solid transparent;
}

.tab-item:hover {
  color: #4a6cf7;
}

.tab-item.active {
  color: #4a6cf7;
  border-bottom-color: #4a6cf7;
  font-weight: 600;
}

.tab-content {
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 估值分析样式 */
.valuation-analysis > div {
  margin-bottom: 30px;
}

.valuation-analysis h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 18px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.metric-item .label {
  color: #666;
  font-size: 14px;
  margin-bottom: 5px;
}

.metric-item .value {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.metric-item .status, .metric-item .trend {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 3px;
  align-self: flex-start;
}

.status.good, .trend.positive {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status.fair {
  background-color: #fff8e1;
  color: #ff8f00;
}

.status.poor, .trend.negative {
  background-color: #ffebee;
  color: #c62828;
}

.status.excellent {
  background-color: #e3f2fd;
  color: #1565c0;
}

/* DCF分析样式 */
.dcf-analysis {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
}

.dcf-params {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.param-group {
  display: flex;
  flex-direction: column;
}

.param-group label {
  margin-bottom: 5px;
  color: #666;
  font-size: 14px;
}

.param-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.dcf-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: #fff;
  border-radius: 4px;
}

.result-item .label {
  color: #666;
}

.result-item .value {
  font-weight: 600;
  color: #333;
}

.value.undervalued {
  color: #2ecc71;
}

.value.overvalued {
  color: #e74c3c;
}

.value.strongly-undervalued {
  color: #27ae60;
  font-weight: 700;
}

.value.strongly-overvalued {
  color: #c0392b;
  font-weight: 700;
}

/* 历史估值对比样式 */
.chart-container {
  height: 300px;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  color: #999;
  font-size: 16px;
}

.percentiles {
  display: flex;
  gap: 20px;
}

.percentile-item {
  display: flex;
  flex-direction: column;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  flex: 1;
}

.percentile-item .label {
  color: #666;
  font-size: 14px;
  margin-bottom: 5px;
}

.percentile-item .value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

/* 事件分析样式 */
.events-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.event-item {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 4px;
  border-left: 4px solid #4a6cf7;
}

.event-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.event-title {
  font-weight: 600;
  color: #333;
}

.event-date {
  color: #666;
  font-size: 14px;
}

.event-content {
  color: #555;
  margin-bottom: 10px;
  line-height: 1.6;
}

.event-impact {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.event-impact.high {
  background-color: #ffebee;
  color: #c62828;
}

.event-impact.medium {
  background-color: #fff8e1;
  color: #ff8f00;
}

.event-impact.low {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.no-events {
  text-align: center;
  padding: 40px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .dcf-params, .dcf-results {
    grid-template-columns: 1fr;
  }
  
  .percentiles {
    flex-direction: column;
  }
}
</style>