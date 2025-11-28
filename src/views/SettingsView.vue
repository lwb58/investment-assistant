<template>
  <div class="settings-container">
    <div class="settings-header">
      <h2 class="page-title">⚙️ 系统设置</h2>
    </div>
    
    <div class="settings-content">
      <!-- API设置 -->
      <div class="setting-section">
        <h3 class="section-title">API设置</h3>
        <div class="setting-card">
          <div class="setting-item">
            <label class="setting-label">
              <input 
                type="checkbox" 
                v-model="settings.useMockData" 
                @change="saveSettings"
              >
              使用模拟数据
            </label>
            <p class="setting-description">
              启用后将使用本地模拟数据，不连接后端API
            </p>
          </div>
          
          <div class="setting-item" v-if="!settings.useMockData">
            <label class="setting-label">API基础地址</label>
            <input 
              type="text" 
              v-model="settings.apiBaseUrl" 
              class="setting-input"
              @change="saveSettings"
            >
          </div>
        </div>
      </div>
      
      <!-- 界面设置 -->
      <div class="setting-section">
        <h3 class="section-title">界面设置</h3>
        <div class="setting-card">
          <div class="setting-item">
            <label class="setting-label">默认页面</label>
            <select v-model="settings.defaultPage" class="setting-select" @change="saveSettings">
              <option value="stock-list">股票清单</option>
              <option value="review-notes">复盘笔记</option>
            </select>
          </div>
          
          <div class="setting-item">
            <label class="setting-label">
              <input 
                type="checkbox" 
                v-model="settings.showSidebar" 
                @change="saveSettings"
              >
              显示侧边栏
            </label>
          </div>
        </div>
      </div>
      
      <!-- 关于 -->
      <div class="setting-section">
        <h3 class="section-title">关于</h3>
        <div class="setting-card">
          <div class="about-info">
            <div class="about-item">
              <span class="about-label">版本</span>
              <span class="about-value">v1.0.0</span>
            </div>
            <div class="about-item">
              <span class="about-label">开发团队</span>
              <span class="about-value">投资助手团队</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 保存成功提示 -->
    <transition name="fade">
      <div class="save-success" v-if="showSaveSuccess">
        ✓ 设置已保存
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 设置数据
const settings = ref({
  useMockData: true,
  apiBaseUrl: '/api',
  defaultPage: 'stock-list',
  showSidebar: true
})

// 保存成功提示
const showSaveSuccess = ref(false)

// 加载设置
const loadSettings = () => {
  try {
    const savedSettings = localStorage.getItem('appSettings')
    if (savedSettings) {
      settings.value = { ...settings.value, ...JSON.parse(savedSettings) }
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 保存设置
const saveSettings = () => {
  try {
    localStorage.setItem('appSettings', JSON.stringify(settings.value))
    showSaveSuccess.value = true
    
    // 3秒后隐藏提示
    setTimeout(() => {
      showSaveSuccess.value = false
    }, 3000)
  } catch (error) {
    console.error('保存设置失败:', error)
  }
}

// 组件挂载时加载设置
onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-container {
  padding: 24px;
  min-height: 100vh;
  background-color: var(--bg-secondary);
  position: relative;
}

.settings-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.settings-content {
  max-width: 800px;
  margin: 0 auto;
}

.setting-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 20px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.setting-card {
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-base);
  padding: 20px;
  box-shadow: var(--shadow-light);
  transition: var(--transition-base);
}

.setting-card:hover {
  box-shadow: var(--shadow-base);
}

.setting-item {
  margin-bottom: 20px;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
  cursor: pointer;
}

.setting-input,
.setting-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-small);
  font-size: 14px;
  transition: var(--transition-fast);
  background-color: var(--bg-primary);
}

.setting-input:focus,
.setting-select:focus {
  outline: none;
  border-color: var(--border-color-hover);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.setting-description {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 4px 0 0 0;
  line-height: 1.4;
}

.about-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.about-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.about-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.about-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.save-success {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: var(--success-color);
  color: white;
  padding: 12px 20px;
  border-radius: var(--border-radius-small);
  font-size: 14px;
  font-weight: 500;
  box-shadow: var(--shadow-base);
  z-index: 1000;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .setting-card {
    padding: 16px;
  }
  
  .save-success {
    bottom: 16px;
    right: 16px;
    padding: 10px 16px;
    font-size: 13px;
  }
}
</style>