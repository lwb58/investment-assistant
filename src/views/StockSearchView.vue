<template>
  <div class="stock-search-container">
    <h1>股票搜索</h1>
    <div class="search-box">
      <input 
        v-model="searchKeyword" 
        @keyup.enter="searchStocks"
        placeholder="输入股票代码或名称搜索..." 
        class="search-input"
      />
      <button @click="searchStocks" class="search-button">搜索</button>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="stockResults.length > 0" class="search-results">
      <h2>搜索结果 ({{ stockResults.length }})</h2>
      <div class="stock-list">
        <div 
          v-for="stock in stockResults" 
          :key="stock.code"
          @click="viewStockDetail(stock.code)"
          class="stock-item"
        >
          <div class="stock-info">
            <div class="stock-name">{{ stock.name }}</div>
            <div class="stock-code">{{ stock.code }}</div>
            <div class="stock-market">{{ stock.market }}</div>
          </div>
          <div class="stock-price">
            <div class="price">{{ stock.price }}</div>
            <div class="change" :class="stock.change > 0 ? 'up' : 'down'">
              {{ stock.change > 0 ? '+' : '' }}{{ stock.change }} ({{ stock.changePercent }})
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="no-results">暂无搜索结果，请输入关键词搜索</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import apiService from '../services/apiService';

interface StockItem {
  code: string;
  name: string;
  market: string;
  price: string;
  change: number;
  changePercent: string;
}

const router = useRouter();
const searchKeyword = ref('');
const stockResults = ref<StockItem[]>([]);
const loading = ref(false);
const error = ref('');

const searchStocks = async () => {
  if (!searchKeyword.value.trim()) {
    error.value = '请输入搜索关键词';
    return;
  }
  
  loading.value = true;
  error.value = '';
  
  try {
    const response = await apiService.stockApi.searchStocks(searchKeyword.value);
    stockResults.value = response.data || [];
  } catch (err) {
    error.value = '搜索失败，请稍后重试';
    console.error('搜索股票失败:', err);
  } finally {
    loading.value = false;
  }
};

const viewStockDetail = (stockCode: string) => {
  router.push(`/stock/detail/${stockCode}`);
};
</script>

<style scoped>
.stock-search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.search-box {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  gap: 10px;
}

.search-input {
  width: 400px;
  padding: 12px 20px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 4px;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #4a6cf7;
}

.search-button {
  padding: 12px 24px;
  background-color: #4a6cf7;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-button:hover {
  background-color: #3a5be7;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error-message {
  text-align: center;
  padding: 20px;
  color: #e74c3c;
  background-color: #fdf2f2;
  border-radius: 4px;
}

.search-results {
  margin-top: 30px;
}

.search-results h2 {
  color: #333;
  margin-bottom: 20px;
}

.stock-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.stock-item:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stock-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.stock-code, .stock-market {
  font-size: 14px;
  color: #666;
}

.stock-price {
  text-align: right;
}

.price {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}

.change {
  font-size: 16px;
  font-weight: 500;
}

.change.up {
  color: #e74c3c;
}

.change.down {
  color: #2ecc71;
}

.no-results {
  text-align: center;
  padding: 40px;
  color: #666;
  background-color: #f9f9f9;
  border-radius: 4px;
}
</style>