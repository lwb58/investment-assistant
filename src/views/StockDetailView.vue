<template>
  <div class="stock-detail-container">
    <div class="header">
      <button @click="goBack" class="back-button">返回</button>
      <h1>{{ stockData.name || '股票详情' }}</h1>
      <div class="stock-info-header">
        <span class="stock-code">{{ stockData.code }}</span>
        <span class="stock-market">{{ stockData.market }}</span>
      </div>
    </div>
    <button @click="goToAnalysis" class="analysis-button">查看分析</button>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="Object.keys(stockData).length > 0">
      <!-- 股价信息 -->
      <div class="price-section">
        <div class="current-price">¥{{ stockData.price }}</div>
        <div class="price-change" :class="stockData.change > 0 ? 'up' : 'down'">
          {{ stockData.change > 0 ? '+' : '' }}{{ stockData.change }} ({{ stockData.changePercent }})
        </div>
        <div class="update-time">更新时间: {{ stockData.updateTime }}</div>
      </div>
      
      <!-- 股票基本信息选项卡 -->
      <div class="tabs">
        <div 
          class="tab-item" 
          :class="activeTab === 'basic' ? 'active' : ''"
          @click="activeTab = 'basic'"
        >
          基本信息
        </div>
        <div 
          class="tab-item" 
          :class="activeTab === 'financial' ? 'active' : ''"
          @click="activeTab = 'financial'"
        >
          财务数据
        </div>
        <div 
          class="tab-item" 
          :class="activeTab === 'industry' ? 'active' : ''"
          @click="activeTab = 'industry'"
        >
          行业对比
        </div>
      </div>
      
      <!-- 基本信息面板 -->
      <div v-if="activeTab === 'basic'" class="tab-content">
        <div class="info-grid">
          <div class="info-item">
            <span class="label">开盘价:</span>
            <span class="value">¥{{ stockData.open || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">最高价:</span>
            <span class="value">¥{{ stockData.high || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">最低价:</span>
            <span class="value">¥{{ stockData.low || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">昨收价:</span>
            <span class="value">¥{{ stockData.preClose || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">成交量:</span>
            <span class="value">{{ formatVolume(stockData.volume || 0) }}</span>
          </div>
          <div class="info-item">
            <span class="label">成交额:</span>
            <span class="value">¥{{ formatAmount(stockData.amount || 0) }}</span>
          </div>
          <div class="info-item">
            <span class="label">换手率:</span>
            <span class="value">{{ stockData.turnoverRate || '-' }}%</span>
          </div>
          <div class="info-item">
            <span class="label">市盈率(TTM):</span>
            <span class="value">{{ stockData.peTTM || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">市净率:</span>
            <span class="value">{{ stockData.pbMRQ || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">总市值:</span>
            <span class="value">¥{{ formatAmount(stockData.totalMarketCap || 0) }}</span>
          </div>
          <div class="info-item">
            <span class="label">流通市值:</span>
            <span class="value">¥{{ formatAmount(stockData.circulatingMarketCap || 0) }}</span>
          </div>
          <div class="info-item">
            <span class="label">所属行业:</span>
            <span class="value">{{ stockData.industry || '-' }}</span>
          </div>
        </div>
      </div>
      
      <!-- 财务数据面板 -->
      <div v-if="activeTab === 'financial'" class="tab-content">
        <div v-if="!financialData || financialData.length === 0" class="no-data">暂无财务数据</div>
        <div v-else>
          <h3>最新财务数据</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">营业收入:</span>
              <span class="value">¥{{ formatAmount(financialData[0]?.revenue || 0) }}亿</span>
            </div>
            <div class="info-item">
              <span class="label">净利润:</span>
              <span class="value">¥{{ formatAmount(financialData[0]?.netProfit || 0) }}亿</span>
            </div>
            <div class="info-item">
              <span class="label">每股收益:</span>
              <span class="value">¥{{ financialData[0]?.eps || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">净资产收益率:</span>
              <span class="value">{{ financialData[0]?.roe || '-' }}%</span>
            </div>
            <div class="info-item">
              <span class="label">毛利率:</span>
              <span class="value">{{ financialData[0]?.grossMargin || '-' }}%</span>
            </div>
            <div class="info-item">
              <span class="label">净利率:</span>
              <span class="value">{{ financialData[0]?.netMargin || '-' }}%</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 行业对比面板 -->
      <div v-if="activeTab === 'industry'" class="tab-content">
        <div v-if="!industryData || industryData.length === 0" class="no-data">暂无行业数据</div>
        <div v-else>
          <h3>行业对比</h3>
          <div class="industry-comparison">
            <div class="industry-stats">
              <div class="stat-item">
                <span class="label">行业平均市盈率:</span>
                <span class="value">{{ industryData.avgPE || '-' }}</span>
              </div>
              <div class="stat-item">
                <span class="label">行业平均市净率:</span>
                <span class="value">{{ industryData.avgPB || '-' }}</span>
              </div>
              <div class="stat-item">
                <span class="label">行业平均净利率:</span>
                <span class="value">{{ industryData.avgNetMargin || '-' }}%</span>
              </div>
              <div class="stat-item">
                <span class="label">行业平均净资产收益率:</span>
                <span class="value">{{ industryData.avgROE || '-' }}%</span>
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
import apiService from '../services/apiService';

interface StockDetail {
  code: string;
  name: string;
  market: string;
  price: string;
  change: number;
  changePercent: string;
  open?: string;
  high?: string;
  low?: string;
  preClose?: string;
  volume?: number;
  amount?: number;
  turnoverRate?: string;
  peTTM?: string;
  pbMRQ?: string;
  totalMarketCap?: number;
  circulatingMarketCap?: number;
  industry?: string;
  updateTime?: string;
}

interface FinancialData {
  revenue: number;
  netProfit: number;
  eps: string;
  roe: string;
  grossMargin: string;
  netMargin: string;
  reportDate?: string;
}

interface IndustryData {
  avgPE: string;
  avgPB: string;
  avgNetMargin: string;
  avgROE: string;
}

const route = useRoute();
const router = useRouter();
const stockCode = route.params.code as string;
const stockData = ref<StockDetail>({} as StockDetail);
const financialData = ref<FinancialData[]>([]);
const industryData = ref<IndustryData>({} as IndustryData);
const loading = ref(true);
const error = ref('');
const activeTab = ref('basic');

const fetchStockData = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    // 获取股票基本数据
    const stockResponse = await apiService.stockApi.getStockDetail(stockCode);
    stockData.value = stockResponse.data;
    
    // 获取财务数据
    const financialResponse = await apiService.stockApi.getFinancialData(stockCode);
    financialData.value = financialResponse.data || [];
    
    // 获取行业数据
    if (stockData.value.industry) {
      const industryResponse = await apiService.stockApi.getIndustryData(stockData.value.industry);
      industryData.value = industryResponse.data;
    }
  } catch (err) {
    error.value = '获取股票数据失败，请稍后重试';
    console.error('获取股票数据失败:', err);
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  router.go(-1);
};

const goToAnalysis = () => {
  router.push(`/stock/analysis/${stockCode}`);
};

const formatVolume = (volume: number): string => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿';
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万';
  }
  return volume.toString();
};

const formatAmount = (amount: number): string => {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2);
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2);
  }
  return amount.toString();
};

onMounted(() => {
  fetchStockData();
});
</script>

<style scoped>
.stock-detail-container {
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

.analysis-button {
  display: block;
  margin: 20px auto;
  padding: 12px 24px;
  background-color: #4a6cf7;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.analysis-button:hover {
  background-color: #3a5be7;
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

.price-section {
  text-align: center;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 30px;
}

.current-price {
  font-size: 36px;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.price-change {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 10px;
}

.price-change.up {
  color: #e74c3c;
}

.price-change.down {
  color: #2ecc71;
}

.update-time {
  color: #666;
  font-size: 14px;
}

.tabs {
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.info-item .label {
  color: #666;
}

.info-item .value {
  font-weight: 600;
  color: #333;
}

.industry-comparison {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 4px;
}

.industry-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #fff;
  border-radius: 4px;
}

.stat-item .label {
  color: #666;
}

.stat-item .value {
  font-weight: 600;
  color: #333;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #666;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .industry-stats {
    grid-template-columns: 1fr;
  }
  
  .search-input {
    width: 100%;
  }
}
</style>