<template>
  <div class="app-container">
    <!-- 侧边栏导航 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-container">
          <span class="logo-icon">📈</span>
          <h1 class="app-title">投资助手</h1>
        </div>
      </div>
      <nav class="nav-menu">
        <router-link 
          to="/stock-list" 
          class="nav-item"
          active-class="active"
        >
          <span class="nav-icon">📋</span>
          <span class="nav-text">股票清单</span>
        </router-link>
        <router-link 
          to="/market-overview" 
          class="nav-item"
          active-class="active"
        >
          <span class="nav-icon">📈</span>
          <span class="nav-text">今日大盘</span>
        </router-link>
        <router-link 
          to="/review-notes" 
          class="nav-item"
          active-class="active"
        >
          <span class="nav-icon">📝</span>
          <span class="nav-text">复盘笔记</span>
        </router-link>
        <router-link to="/position-analysis" class="nav-item" active-class="active">
            <span class="nav-icon">📊</span>
            <span class="nav-text">持仓分析</span>
          </router-link>
        <!-- 添加系统配置菜单项 -->
        <router-link 
          to="/settings" 
          class="nav-item"
          active-class="active"
        >
          <span class="nav-icon">⚙️</span>
          <span class="nav-text">系统设置</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="app-version">v1.0.0</div>
      </div>
    </aside>
    
    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 顶部导航栏 -->
      <header class="header">
        <div class="header-left">
          <!-- 面包屑导航 -->
          <div class="breadcrumb">
            <span v-if="currentPath === '/stock-list'">股票清单</span>
            <span v-else-if="currentPath === '/review-notes'">复盘笔记</span>
            <span v-else-if="currentPath === '/position-analysis'">持仓分析</span>
            <span v-else-if="currentPath.includes('/stock-detail')">股票详情</span>
            <span v-else>首页</span>
          </div>
        </div>
        <div class="header-right">
          <div class="header-actions">
            <button class="action-btn" title="刷新数据">
              🔄
            </button>
            <button class="action-btn" title="切换主题">
              🌓
            </button>
          </div>
          <div class="header-user">
            <div class="user-avatar">投</div>
            <span class="user-name">投资者</span>
          </div>
        </div>
      </header>
      
      <!-- 页面内容区域 -->
      <div class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" v-if="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const currentPath = ref(route.path);

// 监听路由变化
watch(() => route.path, (newPath) => {
  currentPath.value = newPath;
});
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  background-color: var(--bg-secondary);
}

/* 侧边栏样式 */
.sidebar {
  width: 260px;
  background: linear-gradient(135deg, #001529 0%, #142945 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  transition: var(--transition-base);
  position: relative;
  overflow: hidden;
}

/* 侧边栏背景装饰 */
.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 120px;
  height: 120px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50% 0 0 50%;
  transform: translate(50%, -50%);
}

.sidebar-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.logo-icon {
  font-size: 24px;
  background: rgba(255, 255, 255, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: white;
  background: linear-gradient(90deg, #fff 0%, #e0f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  flex: 1;
  padding: var(--spacing-md) 0;
  overflow-y: auto;
  position: relative;
  z-index: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-lg);
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: var(--transition-base);
  border: none;
  border-radius: 0 var(--border-radius-base) var(--border-radius-base) 0;
  margin: 2px 0;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  transition: var(--transition-base);
}

.nav-item:hover {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
  padding-left: calc(var(--spacing-lg) + 4px);
}

.nav-item.active {
  color: white;
  background-color: rgba(24, 144, 255, 0.15);
  font-weight: 500;
}

.nav-item.active::before {
  background: var(--primary-color);
}

.nav-icon {
  font-size: 18px;
  margin-right: var(--spacing-sm);
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 16px;
}

.sidebar-footer {
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  position: relative;
  z-index: 1;
}

/* 主内容区域样式 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--bg-secondary);
}

.header {
  height: 64px;
  background: linear-gradient(90deg, #ffffff 0%, #fafafa 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
  flex-shrink: 0;
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
}

.breadcrumb {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  padding: 0;
  border: none;
  background-color: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.action-btn:hover {
  background-color: var(--bg-hover);
  color: var(--primary-color);
  transform: none;
  box-shadow: none;
}

.header-user {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-small);
  transition: var(--transition-base);
  cursor: pointer;
}

.header-user:hover {
  background-color: var(--bg-hover);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.user-name {
  color: var(--text-primary);
  font-weight: 500;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }
  
  .sidebar-header {
    padding: var(--spacing-md);
  }
  
  .logo-container {
    flex-direction: column;
    gap: var(--spacing-xs);
  }
  
  .app-title {
    font-size: 12px;
  }
  
  .nav-text {
    display: none;
  }
  
  .nav-item {
    justify-content: center;
    padding: var(--spacing-sm);
  }
  
  .nav-icon {
    margin-right: 0;
  }
  
  .sidebar-footer {
    padding: var(--spacing-sm);
    font-size: 10px;
  }
  
  .header {
    padding: 0 var(--spacing-md);
  }
  
  .breadcrumb {
    font-size: 14px;
  }
  
  .user-name {
    display: none;
  }
  
  .page-content {
    padding: var(--spacing-md);
  }
}

@media (max-width: 480px) {
  .header-right {
    gap: var(--spacing-sm);
  }
  
  .header-actions {
    gap: 4px;
  }
  
  .action-btn {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
}
</style>