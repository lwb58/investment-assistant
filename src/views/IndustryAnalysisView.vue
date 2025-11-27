<template>
  <div class="industry-analysis-container">
    <!-- 头部导航 -->
    <div class="industry-header">
      <button class="back-button" @click="goBack">
        <i class="icon-arrow-left"></i> 返回
      </button>
      <h1 class="page-title">行业分析</h1>
    </div>

    <!-- 行业分析标签页 -->
    <div class="industry-tabs">
      <div 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-item"
        :class="{ active: activeTab === tab.key }"
        @click="switchTab(tab.key)"
      >
        {{ tab.label }}
      </div>
    </div>

    <!-- 行业列表标签页内容 -->
    <div v-if="activeTab === 'list'" class="industry-list-content">
      <!-- 行业筛选 -->
      <div class="industry-filter">
        <input 
          type="text" 
          v-model="searchKeyword" 
          placeholder="搜索行业名称..."
          class="search-input"
        />
        <select v-model="selectedLevel" class="level-select">
          <option value="0">所有层级</option>
          <option value="1">一级行业</option>
          <option value="2">二级行业</option>
        </select>
      </div>

      <!-- 行业列表 -->
      <div class="industry-grid">
        <div 
          v-for="industry in filteredIndustries" 
          :key="industry.code"
          class="industry-card"
          @click="navigateToIndustryDetail(industry.code)"
        >
          <div class="industry-card-header">
            <h3 class="industry-name">{{ industry.name }}</h3>
            <span class="industry-level">Lv.{{ industry.level }}</span>
          </div>
          <div class="industry-card-body">
            <div class="industry-card-footer">
              <button class="view-detail-btn">查看详情</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 行业对比标签页内容 -->
    <div v-else-if="activeTab === 'compare'" class="industry-compare-content">
      <!-- 选择行业 -->
      <div class="compare-selector">
        <div class="selected-industries">
          <div 
            v-for="industry in selectedIndustries" 
            :key="industry.code"
            class="selected-industry-tag"
          >
            {{ industry.name }}
            <span class="remove-tag" @click.stop="removeIndustry(industry.code)">×</span>
          </div>
        </div>
        
        <select v-model="industryToAdd" class="industry-select" @change="addIndustry">
          <option value="">选择要对比的行业</option>
          <option 
            v-for="industry in industries.filter(i => !selectedIndustries.some(s => s.code === i.code))" 
            :key="industry.code"
            :value="industry.code"
          >
            {{ industry.name }}
          </option>
        </select>
        
        <button 
          class="compare-btn" 
          :disabled="selectedIndustries.length < 2"
          @click="compareIndustries"
        >
          开始对比
        </button>
      </div>

      <!-- 对比结果 -->
      <div v-if="comparisonResult" class="comparison-results">
        <!-- 估值对比 -->
        <div class="comparison-section">
          <h3>估值对比</h3>
          <div class="comparison-table">
            <table>
              <thead>
                <tr>
                  <th>行业</th>
                  <th>PE</th>
                  <th>PB</th>
                  <th>ROE</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in comparisonResult.comparison.valuation" :key="item.code">
                  <td>{{ item.name }}</td>
                  <td>{{ item.pe }}</td>
                  <td>{{ item.pb }}</td>
                  <td>{{ item.roe }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 表现对比 -->
        <div class="comparison-section">
          <h3>表现对比</h3>
          <div class="comparison-table">
            <table>
              <thead>
                <tr>
                  <th>行业</th>
                  <th>月涨跌幅</th>
                  <th>季度涨跌幅</th>
                  <th>年度涨跌幅</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in comparisonResult.comparison.performance" :key="item.code">
                  <td>{{ item.name }}</td>
                  <td :class="getChangeClass(item.month)">{{ item.month }}%</td>
                  <td :class="getChangeClass(item.quarter)">{{ item.quarter }}%</td>
                  <td :class="getChangeClass(item.year)">{{ item.year }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 行业估值排名标签页内容 -->
    <div v-else-if="activeTab === 'ranking'" class="industry-ranking-content">
      <!-- 排名筛选 -->
      <div class="ranking-filter">
        <select v-model="rankingMetric" class="metric-select" @change="fetchValuationRanking">
          <option value="pe">PE估值</option>
          <option value="pb">PB估值</option>
          <option value="roe">ROE</option>
          <option value="ps">PS估值</option>
          <option value="pcf">PCF估值</option>
        </select>
        <select v-model="rankingOrder" class="order-select" @change="fetchValuationRanking">
          <option value="asc">升序</option>
          <option value="desc">降序</option>
        </select>
      </div>

      <!-- 排名列表 -->
      <div class="ranking-table">
        <table>
          <thead>
            <tr>
              <th>排名</th>
              <th>行业名称</th>
              <th>{{ getMetricLabel(rankingMetric) }}</th>
              <th>涨跌幅</th>
              <th>历史分位数</th>
              <th>同业分位数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in valuationRanking" :key="item.code">
              <td class="rank-cell">{{ item.rank }}</td>
              <td>{{ item.name }}</td>
              <td>{{ item.value }}</td>
              <td :class="getChangeClass(item.change)">{{ item.change }}%</td>
              <td>
                <div class="percentile-bar">
                  <div class="percentile-fill" :style="{ width: item.percentiles.historical + '%' }"></div>
                  <span>{{ item.percentiles.historical }}%</span>
                </div>
              </td>
              <td>
                <div class="percentile-bar">
                  <div class="percentile-fill" :style="{ width: item.percentiles.peer + '%' }"></div>
                  <span>{{ item.percentiles.peer }}%</span>
                </div>
              </td>
              <td>
                <button class="view-detail-btn" @click="navigateToIndustryDetail(item.code)">详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 行业详情标签页内容 -->
    <div v-else-if="activeTab === 'detail' && currentIndustry" class="industry-detail-content">
      <!-- 行业概览 -->
      <div class="industry-overview">
        <h2>{{ currentIndustry.name }} ({{ currentIndustry.fullName }})</h2>
        <p class="industry-description">{{ currentIndustry.description }}</p>
      </div>

      <!-- 行业统计数据 -->
      <div class="industry-stats">
        <div class="stat-card">
          <div class="stat-label">股票数量</div>
          <div class="stat-value">{{ currentIndustry.statistics.totalStocks }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">总市值</div>
          <div class="stat-value">{{ currentIndustry.statistics.marketCap }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均PE</div>
          <div class="stat-value">{{ currentIndustry.statistics.avgPE }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均PB</div>
          <div class="stat-value">{{ currentIndustry.statistics.avgPB }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均ROE</div>
          <div class="stat-value">{{ currentIndustry.statistics.avgROE }}%</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均增长率</div>
          <div class="stat-value">{{ currentIndustry.statistics.avgGrowthRate }}%</div>
        </div>
      </div>

      <!-- 行业表现 -->
      <div class="industry-performance">
        <h3>行业表现</h3>
        <div class="performance-grid">
          <div class="performance-item">
            <div class="performance-label">今日</div>
            <div class="performance-value" :class="getChangeClass(currentIndustry.performance.today)">
              {{ currentIndustry.performance.today }}%
            </div>
          </div>
          <div class="performance-item">
            <div class="performance-label">一周</div>
            <div class="performance-value" :class="getChangeClass(currentIndustry.performance.week)">
              {{ currentIndustry.performance.week }}%
            </div>
          </div>
          <div class="performance-item">
            <div class="performance-label">一月</div>
            <div class="performance-value" :class="getChangeClass(currentIndustry.performance.month)">
              {{ currentIndustry.performance.month }}%
            </div>
          </div>
          <div class="performance-item">
            <div class="performance-label">一季</div>
            <div class="performance-value" :class="getChangeClass(currentIndustry.performance.quarter)">
              {{ currentIndustry.performance.quarter }}%
            </div>
          </div>
          <div class="performance-item">
            <div class="performance-label">一年</div>
            <div class="performance-value" :class="getChangeClass(currentIndustry.performance.year)">
              {{ currentIndustry.performance.year }}%
            </div>
          </div>
        </div>
      </div>

      <!-- 行业趋势图 -->
      <div class="industry-trend">
        <h3>行业趋势</h3>
        <div class="trend-period-selector">
          <button 
            v-for="period in trendPeriods" 
            :key="period.value"
            class="period-btn"
            :class="{ active: selectedTrendPeriod === period.value }"
            @click="changeTrendPeriod(period.value)"
          >
            {{ period.label }}
          </button>
        </div>
        <div class="trend-chart" ref="trendChart">
          <!-- 图表将通过Chart.js渲染 -->
        </div>
      </div>

      <!-- 行业内股票 -->
      <div class="industry-stocks">
        <h3>行业内股票</h3>
        <div class="stock-table">
          <table>
            <thead>
              <tr>
                <th>股票代码</th>
                <th>股票名称</th>
                <th>最新价</th>
                <th>涨跌幅</th>
                <th>PE</th>
                <th>PB</th>
                <th>市值</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="stock in industryStocks.list" :key="stock.code">
                <td>{{ stock.code }}</td>
                <td>{{ stock.name }}</td>
                <td>{{ stock.price }}</td>
                <td :class="getChangeClass(stock.changeRate)">{{ stock.changeRate }}%</td>
                <td>{{ stock.pe }}</td>
                <td>{{ stock.pb }}</td>
                <td>{{ stock.marketCap }}</td>
                <td>
                  <button class="view-stock-btn" @click="navigateToStockDetail(stock.code)">
                    详情
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页 -->
        <div class="pagination" v-if="industryStocks.pagination">
          <button 
            class="page-btn" 
            :disabled="industryStocks.pagination.page === 1"
            @click="changeStockPage(industryStocks.pagination.page - 1)"
          >
            上一页
          </button>
          <span class="page-info">
            {{ industryStocks.pagination.page }} / {{ industryStocks.pagination.totalPages }}
          </span>
          <button 
            class="page-btn" 
            :disabled="industryStocks.pagination.page === industryStocks.pagination.totalPages"
            @click="changeStockPage(industryStocks.pagination.page + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button class="retry-btn" @click="retry">重试</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { apiService } from '../services/apiService';

// 路由和状态
const router = useRouter();
const route = useRoute();
const loading = ref(false);
const error = ref('');

// 标签页
const activeTab = ref('list');
const tabs = [
  { key: 'list', label: '行业列表' },
  { key: 'compare', label: '行业对比' },
  { key: 'ranking', label: '估值排名' },
  { key: 'detail', label: '行业详情' }
];

// 行业列表数据
const industries = ref([]);
const searchKeyword = ref('');
const selectedLevel = ref('0');

// 行业对比数据
const selectedIndustries = ref([]);
const industryToAdd = ref('');
const comparisonResult = ref(null);

// 行业估值排名
const valuationRanking = ref([]);
const rankingMetric = ref('pe');
const rankingOrder = ref('asc');

// 行业详情数据
const currentIndustry = ref(null);
const industryStocks = ref({ list: [], pagination: null });

// 行业趋势数据
const trendPeriods = [
  { label: '1月', value: '1m' },
  { label: '3月', value: '3m' },
  { label: '6月', value: '6m' },
  { label: '1年', value: '1y' },
  { label: '3年', value: '3y' },
  { label: '5年', value: '5y' }
];
const selectedTrendPeriod = ref('1y');
const trendData = ref(null);
const trendChart = ref(null);
let chartInstance = null;

// 计算属性 - 过滤后的行业列表
const filteredIndustries = computed(() => {
  return industries.value.filter(industry => {
    const matchesSearch = industry.name.includes(searchKeyword.value) || 
                         industry.fullName.includes(searchKeyword.value);
    const matchesLevel = selectedLevel.value === '0' || industry.level === parseInt(selectedLevel.value);
    return matchesSearch && matchesLevel;
  });
});

// 获取指标标签
const getMetricLabel = (metric) => {
  const labels = {
    'pe': 'PE估值',
    'pb': 'PB估值',
    'roe': 'ROE(%)',
    'ps': 'PS估值',
    'pcf': 'PCF估值'
  };
  return labels[metric] || metric;
};

// 获取涨跌幅样式类
const getChangeClass = (value) => {
  const numValue = parseFloat(value);
  if (numValue > 0) return 'positive';
  if (numValue < 0) return 'negative';
  return 'neutral';
};

// 切换标签页
const switchTab = (tabKey) => {
  activeTab.value = tabKey;
  
  // 如果切换到详情页，但没有选择行业，则不显示
  if (tabKey === 'detail' && !currentIndustry.value) {
    activeTab.value = 'list';
  }
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 导航到行业详情
const navigateToIndustryDetail = async (industryCode) => {
  loading.value = true;
  error.value = '';
  
  try {
    // 获取行业详情
    const detailResponse = await apiService.industryApi.getIndustryDetail(industryCode);
    currentIndustry.value = detailResponse.data;
    
    // 获取行业内股票
    await fetchIndustryStocks(industryCode, 1);
    
    // 获取行业趋势
    await fetchIndustryTrend(industryCode, selectedTrendPeriod.value);
    
    // 切换到详情标签页
    activeTab.value = 'detail';
  } catch (err) {
    error.value = '获取行业详情失败';
    console.error('获取行业详情失败:', err);
  } finally {
    loading.value = false;
  }
};

// 导航到股票详情
const navigateToStockDetail = (stockCode) => {
  router.push({ name: 'StockDetail', params: { code: stockCode } });
};

// 添加行业到对比列表
const addIndustry = () => {
  if (!industryToAdd.value) return;
  
  const industry = industries.value.find(i => i.code === industryToAdd.value);
  if (industry && !selectedIndustries.value.some(i => i.code === industry.code)) {
    selectedIndustries.value.push(industry);
    industryToAdd.value = '';
  }
};

// 从对比列表中移除行业
const removeIndustry = (industryCode) => {
  const index = selectedIndustries.value.findIndex(i => i.code === industryCode);
  if (index > -1) {
    selectedIndustries.value.splice(index, 1);
  }
  
  // 如果没有行业了，清空对比结果
  if (selectedIndustries.value.length === 0) {
    comparisonResult.value = null;
  }
};

// 对比行业
const compareIndustries = async () => {
  if (selectedIndustries.value.length < 2) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    const codes = selectedIndustries.value.map(i => i.code).join(',');
    const response = await apiService.industryApi.compareIndustries(codes);
    comparisonResult.value = response.data;
  } catch (err) {
    error.value = '对比行业失败';
    console.error('对比行业失败:', err);
  } finally {
    loading.value = false;
  }
};

// 获取行业估值排名
const fetchValuationRanking = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const response = await apiService.industryApi.getIndustryValuationRanking(rankingMetric.value, rankingOrder.value);
    valuationRanking.value = response.data;
  } catch (err) {
    error.value = '获取行业估值排名失败';
    console.error('获取行业估值排名失败:', err);
  } finally {
    loading.value = false;
  }
};

// 获取行业内股票
const fetchIndustryStocks = async (industryCode, page) => {
  try {
    const response = await apiService.industryApi.getIndustryStocks(industryCode, page);
    industryStocks.value = response.data;
  } catch (err) {
    console.error('获取行业股票失败:', err);
  }
};

// 获取行业趋势
const fetchIndustryTrend = async (industryCode, period) => {
  try {
    const response = await apiService.industryApi.getIndustryTrend(industryCode, period);
    trendData.value = response.data;
    
    // 渲染趋势图
    await nextTick();
    renderTrendChart();
  } catch (err) {
    console.error('获取行业趋势失败:', err);
  }
};

// 渲染趋势图
const renderTrendChart = () => {
  if (!trendChart.value || !trendData.value) return;
  
  // 销毁旧图表
  if (chartInstance) {
    chartInstance.destroy();
  }
  
  // 确保Chart.js已加载
  if (typeof window.Chart === 'undefined') {
    // Chart.js未加载，动态加载
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = () => {
      createChart();
    };
    document.head.appendChild(script);
  } else {
    createChart();
  }
};

// 创建图表
const createChart = () => {
  if (!trendData.value) return;
  
  const ctx = trendChart.value.getContext('2d');
  const labels = trendData.value.data.map(item => item.date);
  const values = trendData.value.data.map(item => item.value);
  
  chartInstance = new window.Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: trendData.value.name + ' 趋势',
        data: values,
        borderColor: '#1890ff',
        backgroundColor: 'rgba(24, 144, 255, 0.1)',
        tension: 0.1,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: '日期'
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: '指数值'
          }
        }
      }
    }
  });
};

// 改变行业趋势时间周期
const changeTrendPeriod = async (period) => {
  selectedTrendPeriod.value = period;
  if (currentIndustry.value) {
    await fetchIndustryTrend(currentIndustry.value.code, period);
  }
};

// 改变行业股票页码
const changeStockPage = async (page) => {
  if (currentIndustry.value) {
    await fetchIndustryStocks(currentIndustry.value.code, page);
  }
};

// 重试操作
const retry = () => {
  error.value = '';
  // 根据当前标签页重新加载数据
  if (activeTab.value === 'list') {
    fetchIndustries();
  } else if (activeTab.value === 'ranking') {
    fetchValuationRanking();
  }
};

// 获取行业列表
const fetchIndustries = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const response = await apiService.industryApi.getIndustries();
    industries.value = response.data;
  } catch (err) {
    error.value = '获取行业列表失败';
    console.error('获取行业列表失败:', err);
  } finally {
    loading.value = false;
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchIndustries();
});
</script>

<style scoped>
.industry-analysis-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.industry-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.back-button {
  background: none;
  border: 1px solid #d9d9d9;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  margin-right: 16px;
  transition: all 0.3s;
}

.back-button:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.industry-tabs {
  display: flex;
  background-color: #fff;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
  font-size: 14px;
}

.tab-item.active {
  background-color: #1890ff;
  color: #fff;
}

.tab-item:hover:not(.active) {
  color: #1890ff;
}

/* 行业列表样式 */
.industry-list-content {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.industry-filter {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.level-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.industry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.industry-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.industry-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #1890ff;
}

.industry-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.industry-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.industry-level {
  background-color: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.industry-card-footer {
  text-align: right;
}

.view-detail-btn {
  background-color: #1890ff;
  color: #fff;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.view-detail-btn:hover {
  background-color: #40a9ff;
}

/* 行业对比样式 */
.industry-compare-content {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.compare-selector {
  margin-bottom: 20px;
}

.selected-industries {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.selected-industry-tag {
  background-color: #f0f0f0;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.remove-tag {
  margin-left: 8px;
  cursor: pointer;
  color: #999;
  font-size: 16px;
}

.remove-tag:hover {
  color: #ff4d4f;
}

.industry-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  margin-bottom: 12px;
}

.compare-btn {
  background-color: #1890ff;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.compare-btn:hover:not(:disabled) {
  background-color: #40a9ff;
}

.compare-btn:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.comparison-results {
  margin-top: 20px;
}

.comparison-section {
  margin-bottom: 24px;
}

.comparison-section h3 {
  margin-bottom: 12px;
  font-size: 18px;
  color: #333;
}

.comparison-table {
  overflow-x: auto;
}

.comparison-table table {
  width: 100%;
  border-collapse: collapse;
}

.comparison-table th,
.comparison-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

.comparison-table th {
  background-color: #fafafa;
  font-weight: 600;
}

/* 行业估值排名样式 */
.industry-ranking-content {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ranking-filter {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.metric-select,
.order-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.ranking-table {
  overflow-x: auto;
}

.ranking-table table {
  width: 100%;
  border-collapse: collapse;
}

.ranking-table th,
.ranking-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

.ranking-table th {
  background-color: #fafafa;
  font-weight: 600;
}

.rank-cell {
  font-weight: 600;
  color: #1890ff;
}

.percentile-bar {
  position: relative;
  width: 100px;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.percentile-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background-color: #1890ff;
  border-radius: 10px;
}

.percentile-bar span {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* 行业详情样式 */
.industry-detail-content {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.industry-overview h2 {
  margin-bottom: 12px;
  font-size: 24px;
  color: #333;
}

.industry-description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 24px;
}

.industry-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background-color: #fafafa;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.industry-performance h3 {
  margin-bottom: 16px;
  font-size: 18px;
  color: #333;
}

.performance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.performance-item {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  background-color: #fafafa;
}

.performance-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.performance-value {
  font-size: 20px;
  font-weight: 600;
}

.industry-trend h3 {
  margin-bottom: 16px;
  font-size: 18px;
  color: #333;
}

.trend-period-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.period-btn {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background-color: #fff;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.period-btn.active {
  background-color: #1890ff;
  color: #fff;
  border-color: #1890ff;
}

.period-btn:hover:not(.active) {
  border-color: #1890ff;
  color: #1890ff;
}

.trend-chart {
  height: 400px;
  margin-bottom: 24px;
}

.industry-stocks h3 {
  margin-bottom: 16px;
  font-size: 18px;
  color: #333;
}

.stock-table {
  overflow-x: auto;
  margin-bottom: 16px;
}

.stock-table table {
  width: 100%;
  border-collapse: collapse;
}

.stock-table th,
.stock-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

.stock-table th {
  background-color: #fafafa;
  font-weight: 600;
}

.view-stock-btn {
  background-color: #1890ff;
  color: #fff;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.view-stock-btn:hover {
  background-color: #40a9ff;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.page-btn {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background-color: #fff;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.page-btn:disabled {
  color: #d9d9d9;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

/* 通用样式 */
.positive {
  color: #52c41a;
}

.negative {
  color: #ff4d4f;
}

.neutral {
  color: #666;
}

/* 加载和错误状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 16px;
  font-size: 16px;
  color: #666;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  padding: 12px;
  color: #ff4d4f;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.retry-btn {
  background-color: #ff4d4f;
  color: #fff;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.retry-btn:hover {
  background-color: #ff7875;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .industry-analysis-container {
    padding: 15px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .industry-tabs {
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .el-tabs__nav {
    font-size: 12px;
  }
  
  .industry-card {
    margin-bottom: 15px;
    padding: 15px;
  }
  
  .metric-value {
    font-size: 16px;
  }
  
  .metric-label {
    font-size: 12px;
  }
  
  .stock-list {
    overflow-x: auto;
  }
  
  .el-table {
    min-width: 500px;
    font-size: 12px;
  }
  
  .el-table__header th,
  .el-table__body td {
    padding: 6px 4px !important;
  }
}

@media (max-width: 480px) {
  .industry-analysis-container {
    padding: 10px;
  }
  
  .page-title {
    font-size: 18px;
  }
  
  .industry-card {
    padding: 12px;
  }
  
  .metric-value {
    font-size: 14px;
  }
  
  .metric-label {
    font-size: 11px;
  }
}
</style>