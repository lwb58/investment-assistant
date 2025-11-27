<template>
  <div class="favorite-stocks-view">
    <header class="page-header">
      <h1>我的关注股票</h1>
      <p class="subtitle">管理您关注的股票，随时了解最新行情</p>
    </header>
    
    <div class="content-wrapper">
      <FavoriteStocksList />
    </div>
  </div>
</template>

<script lang="ts" setup>
import FavoriteStocksList from '../components/FavoriteStocksList.vue';
</script>

<style scoped>
.favorite-stocks-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 20px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 32px;
  font-weight: 700;
}

.subtitle {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

@media (max-width: 768px) {
  .page-header {
    padding: 30px 15px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .content-wrapper {
    padding: 15px;
  }
}
</style>
