<template>
  <div class="profile-page">
    <!-- 顶部导航栏 -->
    <header class="top-nav">
      <div class="logo-container">
        <h1 class="logo">Invest<span class="highlight">Pro</span></h1>
        <div class="nav-links">
          <a href="/" class="nav-link">首页</a>
          <a href="/stock/search" class="nav-link">股票搜索</a>
          <a href="#" class="nav-link">股票估值</a>
          <a href="/favorite-stocks" class="nav-link">我的关注</a>
          <a href="#" class="nav-link">投资组合</a>
          <a href="/market-data" class="nav-link">市场分析</a>
          <a href="/profile" class="nav-link active">个人中心</a>
        </div>
      </div>
    </header>
    
    <!-- 主要内容区 -->
    <main class="profile-content">
      <div class="profile-container">
        <h2 class="page-title">个人中心</h2>
        
        <div class="profile-section">
          <div class="profile-header">
            <div class="avatar">
              <div class="avatar-icon">👤</div>
            </div>
            <div class="user-info">
              <h3 class="username">{{ userInfo.username }}</h3>
              <p class="user-desc">{{ userInfo.description }}</p>
            </div>
          </div>
          
          <div class="profile-details">
            <div class="detail-group">
              <h4 class="group-title">基本信息</h4>
              <div class="detail-item">
                <span class="detail-label">昵称</span>
                <span class="detail-value">{{ userInfo.nickname }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">注册时间</span>
                <span class="detail-value">{{ userInfo.registerTime }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">上次登录</span>
                <span class="detail-value">{{ userInfo.lastLoginTime }}</span>
              </div>
            </div>
            
            <div class="detail-group">
              <h4 class="group-title">账户统计</h4>
              <div class="detail-item">
                <span class="detail-label">关注股票</span>
                <span class="detail-value">{{ userInfo.favoriteCount }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">分析历史</span>
                <span class="detail-value">{{ userInfo.analysisCount }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">投资记录</span>
                <span class="detail-value">{{ userInfo.investmentCount }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="settings-section">
          <h3 class="section-title">系统设置</h3>
          <div class="settings-list">
            <div class="setting-item">
              <span class="setting-label">通知提醒</span>
              <label class="switch">
                <input type="checkbox" v-model="settings.notificationEnabled" disabled>
                <span class="slider round"></span>
              </label>
            </div>
            <div class="setting-item">
              <span class="setting-label">自动刷新</span>
              <label class="switch">
                <input type="checkbox" v-model="settings.autoRefresh" disabled>
                <span class="slider round"></span>
              </label>
            </div>
            <div class="setting-item">
              <span class="setting-label">深色模式</span>
              <label class="switch">
                <input type="checkbox" v-model="settings.darkMode" disabled>
                <span class="slider round"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 页脚 -->
    <footer class="footer">
      <p>© 2024 InvestPro 智能投资助手 | 仅供参考，不构成投资建议</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';

// 用户信息（模拟数据）
const userInfo = reactive({
  username: 'invest_user',
  nickname: '投资达人',
  description: '欢迎使用智能投资助手',
  registerTime: '2024-01-15',
  lastLoginTime: new Date().toLocaleString('zh-CN'),
  favoriteCount: 12,
  analysisCount: 35,
  investmentCount: 8
});

// 系统设置
const settings = reactive({
  notificationEnabled: true,
  autoRefresh: true,
  darkMode: false
});
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 顶部导航样式（与HomeView保持一致） */
.top-nav {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
}

.logo .highlight {
  color: #ffd700;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 0.5rem 0;
}

.nav-link:hover,
.nav-link.active {
  color: #ffd700;
}

/* 个人中心内容样式 */
.profile-content {
  flex: 1;
  padding: 2rem;
}

.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.page-title {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
  padding: 1.5rem 0;
  border-bottom: 1px solid #eee;
}

/* 个人资料部分 */
.profile-section {
  padding: 2rem;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 2rem;
}

.avatar-icon {
  font-size: 3rem;
}

.user-info h3 {
  font-size: 1.5rem;
  margin: 0 0 0.5rem 0;
  color: #333;
}

.user-desc {
  color: #666;
  margin: 0;
}

/* 详细信息 */
.profile-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.detail-group h4 {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #667eea;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-label {
  color: #666;
  font-weight: 500;
}

.detail-value {
  color: #333;
  font-weight: 600;
}

/* 设置部分 */
.settings-section {
  padding: 2rem;
  background: #fafafa;
  border-top: 1px solid #eee;
}

.section-title {
  font-size: 1.3rem;
  color: #333;
  margin-bottom: 1.5rem;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
}

.setting-label {
  color: #333;
  font-weight: 500;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #667eea;
}

input:focus + .slider {
  box-shadow: 0 0 1px #667eea;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

/* 页脚样式 */
.footer {
  background: #333;
  color: white;
  text-align: center;
  padding: 1rem;
  margin-top: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .avatar {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  .profile-details {
    grid-template-columns: 1fr;
  }
}
</style>