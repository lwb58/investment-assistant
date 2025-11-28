<template>
  <div class="review-notes-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">
          <span class="title-icon">📝</span>
          复盘笔记
        </h2>
        <div class="notes-stats" v-if="!loading && notes.length > 0">
          <span class="stats-item">
            <span class="stats-label">总计笔记:</span>
            <span class="stats-value">{{ notes.length }}</span>
          </span>
          <span class="stats-separator">|</span>
          <span class="stats-item">
            <span class="stats-label">筛选后:</span>
            <span class="stats-value">{{ filteredNotes.length }}</span>
          </span>
        </div>
      </div>
      <button 
        class="btn primary" 
        @click="showAddModal = true" 
        :disabled="submitting"
        :class="{ 'btn-loading': submitting }"
      >
        <span v-if="submitting" class="loading-spinner small"></span>
        {{ submitting ? '处理中...' : '新建笔记' }}
      </button>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      {{ error }}
      <button class="error-close" @click="error = null" aria-label="关闭错误提示">×</button>
    </div>

    <!-- 主要内容区域 -->
    <div class="notes-content">
      <!-- 左侧笔记列表 -->
      <div class="notes-sidebar">
        <div class="search-box">
          <div class="search-icon">🔍</div>
          <input 
            type="text" 
            placeholder="搜索笔记标题或内容"
            v-model="searchKeyword"
            @input="handleSearch"
            :disabled="loading"
            :class="{ 'search-input-loading': loading }"
          />
          <button 
            v-if="searchKeyword" 
            class="clear-search" 
            @click="clearSearch"
            aria-label="清空搜索"
          >
            ×
          </button>
        </div>
        <div class="notes-list">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
          </div>
          
          <!-- 笔记列表 -->
          <div v-else>
            <div 
              v-for="note in filteredNotes" 
              :key="note.id"
              class="note-item"
              :class="{ active: selectedNoteId === note.id }"
              @click="selectNote(note)"
              :style="{ animationDelay: `${Math.min(index, 20) * 0.05}s` }"
            >
              <div class="note-header">
                <div class="note-title">{{ note.title }}</div>
                <div v-if="note.tags" class="note-tags">
                  <span 
                    v-for="tag in note.tags.split(',')" 
                    :key="tag"
                    class="tag"
                  >
                    {{ tag.trim() }}
                  </span>
                </div>
              </div>
              <div class="note-meta">
                <span class="note-date">{{ formatDate(note.createTime) }}</span>
                <span v-if="note.stockCode" class="note-stock">
                  <span class="stock-icon">📊</span>
                  {{ note.stockCode }}
                </span>
              </div>
              <div class="note-preview">{{ truncateText(note.content, 60) }}</div>
              <div class="note-indicator" :class="{ active: selectedNoteId === note.id }"></div>
            </div>
            <div v-if="filteredNotes.length === 0" class="empty-state">
              <div class="empty-icon">{{ searchKeyword ? '🔍' : '📝' }}</div>
              <p>{{ searchKeyword ? '没有找到匹配的笔记' : '暂无笔记' }}</p>
              <button 
                v-if="searchKeyword" 
                class="btn text" 
                @click="clearSearch"
              >
                清空搜索
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧笔记详情 -->
      <div class="notes-main">
        <div v-if="selectedNote" class="note-detail">
          <div class="detail-header">
            <h3 class="detail-title">{{ selectedNote.title }}</h3>
            <div class="detail-actions">
              <button 
                class="btn text" 
                @click="editNote(selectedNote)" 
                :disabled="submitting"
                title="编辑笔记"
              >
                ✏️ 编辑
              </button>
              <button 
                class="btn text danger" 
                @click="deleteNote(selectedNote.id)" 
                :disabled="submitting"
                title="删除笔记"
              >
                🗑️ 删除
              </button>
            </div>
          </div>
          <div class="detail-meta">
            <span class="meta-item">
              <span class="meta-label">创建时间：</span>
              <span class="meta-value">{{ formatDate(selectedNote.createTime) }}</span>
            </span>
            <span v-if="selectedNote.updateTime" class="meta-item">
              <span class="meta-label">更新时间：</span>
              <span class="meta-value">{{ formatDate(selectedNote.updateTime) }}</span>
            </span>
            <span v-if="selectedNote.stockCode" class="meta-item">
              <span class="meta-label">关联股票：</span>
              <router-link 
                :to="'/stock-detail/' + selectedNote.stockCode"
                class="stock-link"
                target="_blank"
              >
                <span class="stock-icon">📊</span>
                {{ selectedNote.stockCode }} {{ selectedNote.stockName }}
              </router-link>
            </span>
            <span v-if="selectedNote.tags" class="meta-item">
              <span class="meta-label">标签：</span>
              <span 
                v-for="tag in selectedNote.tags.split(',')" 
                :key="tag"
                class="tag"
              >
                {{ tag.trim() }}
              </span>
            </span>
          </div>
          <div class="detail-content" v-html="formatContent(selectedNote.content)"></div>
        </div>
        <div v-else class="empty-detail">
          <div class="empty-icon">📝</div>
          <h3 class="empty-title">还没有选择笔记</h3>
          <p class="empty-description">选择左侧列表中的笔记，或创建一个新的笔记开始记录</p>
          <button 
            v-if="error && !loading" 
            class="retry-btn" 
            @click="fetchNotes"
          >
            重试加载
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑笔记弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal large" :class="{ 'modal-open': showAddModal }">
        <div class="modal-header">
          <h3 class="modal-title">{{ editingNote ? '编辑笔记' : '新建笔记' }}</h3>
          <button 
            class="close-btn" 
            @click="closeModal" 
            :disabled="submitting"
            aria-label="关闭"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">
              笔记标题 
              <span class="required">*</span>
            </label>
            <input 
              type="text" 
              v-model="formData.title"
              placeholder="请输入笔记标题"
              class="form-input title-input"
              :disabled="submitting"
              :class="{ 'form-input-error': !formData.title.trim() && submitting }"
            />
          </div>
          <div class="form-group">
            <label class="form-label">关联股票代码（可选）</label>
            <input 
              type="text" 
              v-model="formData.stockCode"
              placeholder="例如：600519"
              class="form-input"
              :disabled="submitting"
            />
          </div>
          <div class="form-group">
            <label class="form-label">笔记内容</label>
            <textarea 
              v-model="formData.content"
              placeholder="请输入笔记内容...\n\n支持简单的Markdown语法:\n# 标题\n- 列表项\n\n段落分隔"
              class="form-textarea"
              rows="15"
              :disabled="submitting"
            ></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">标签（用逗号分隔，可选）</label>
            <input 
              type="text" 
              v-model="formData.tags"
              placeholder="例如：技术分析, 基本面, 操作策略"
              class="form-input"
              :disabled="submitting"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button 
            class="btn" 
            @click="closeModal" 
            :disabled="submitting"
          >
            取消
          </button>
          <button 
            class="btn primary" 
            @click="saveNote" 
            :disabled="submitting || !formData.title.trim()"
            :class="{ 'btn-loading': submitting }"
          >
            <span v-if="submitting" class="loading-spinner small"></span>
            {{ submitting ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../api/apiService.js';

const router = useRouter()
const notes = ref([])
const selectedNoteId = ref(null)
const searchKeyword = ref('')
const showAddModal = ref(false)
const editingNote = ref(null)
// 添加加载状态和错误状态
const loading = ref(false)
const error = ref(null)
const submitting = ref(false)

// 表单数据
const formData = ref({
  title: '',
  content: '',
  stockCode: '',
  stockName: '',
  tags: ''
})

// 获取笔记列表的方法
const fetchNotes = async () => {
  try {
    loading.value = true
    error.value = null
    // 注意：apiService.getReviewNotes直接返回笔记数组，不需要访问response.data
    notes.value = await apiService.getReviewNotes() || []
    // 默认选中第一个笔记
    if (notes.value.length > 0 && !selectedNoteId.value) {
      selectedNoteId.value = notes.value[0].id
    }
  } catch (err) {
    error.value = '获取笔记列表失败，请稍后重试'
    console.error('Failed to fetch notes:', err)
  } finally {
    loading.value = false
  }
}

// 计算过滤后的笔记列表
const filteredNotes = computed(() => {
  if (!searchKeyword.value) {
    return notes.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return notes.value.filter(note => 
    note.title.toLowerCase().includes(keyword) || 
    note.content.toLowerCase().includes(keyword) ||
    (note.stockCode && note.stockCode.toLowerCase().includes(keyword))
  )
})

// 当前选中的笔记
const selectedNote = computed(() => {
  return notes.value.find(note => note.id === selectedNoteId.value)
})

// 初始化数据
onMounted(() => {
  fetchNotes()
})

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
}

// 清空搜索
const clearSearch = () => {
  searchKeyword.value = ''
  // 搜索清空后可以考虑重新选择第一条笔记
  if (notes.value.length > 0) {
    selectedNoteId.value = notes.value[0].id
  }
}

// 选择笔记
const selectNote = (note) => {
  if (!note) return
  
  selectedNoteId.value = note.id
  
  // 滚动到顶部，提供更好的阅读体验
  setTimeout(() => {
    const detailElement = document.querySelector('.note-detail')
    if (detailElement) {
      detailElement.scrollTop = 0
    }
  }, 0)
}

// 编辑笔记
const editNote = (note) => {
  editingNote.value = note
  formData.value = {
    title: note.title,
    content: note.content,
    stockCode: note.stockCode || '',
    stockName: note.stockName || '',
    tags: note.tags || ''
  }
  showAddModal.value = true
}

// 删除笔记
const deleteNote = async (id) => {
  if (confirm('确定要删除这篇笔记吗？删除后将无法恢复。')) {
    try {
      submitting.value = true
      // 调用实际API删除笔记
      await apiService.deleteNote(id)
      
      // 从本地列表中移除（保持UI同步）
      const index = notes.value.findIndex(note => note.id === id)
      if (index > -1) {
        notes.value.splice(index, 1)
        // 如果删除的是当前选中的笔记，选中合适的替代笔记
        if (selectedNoteId.value === id) {
          if (notes.value.length > 0) {
            // 找到删除的笔记的索引，选择合适的新笔记
            const newIndex = Math.min(index, notes.value.length - 1)
            selectedNoteId.value = notes.value[newIndex]?.id || notes.value[0]?.id
          } else {
            selectedNoteId.value = null
          }
        }
      }
    } catch (err) {
      error.value = '删除笔记失败，请稍后重试'
      console.error('Failed to delete note:', err)
    } finally {
      submitting.value = false
    }
  }
}

// 保存笔记
const saveNote = async () => {
  // 表单验证
  if (!formData.value.title.trim()) {
    alert('请输入笔记标题')
    return
  }

  try {
    submitting.value = true
    error.value = null
    
    const noteData = {
      title: formData.value.title.trim(),
      content: formData.value.content.trim(),
      stockCode: formData.value.stockCode.trim(),
      tags: formData.value.tags.trim()
    }

    let savedNote
    if (editingNote.value) {
      // 编辑现有笔记
      savedNote = await apiService.updateReviewNote(editingNote.value.id, noteData)
      // 更新本地列表
      const index = notes.value.findIndex(note => note.id === editingNote.value.id)
      if (index > -1) {
        // 注意：apiService.updateReviewNote直接返回更新后的笔记对象，不需要访问savedNote.data
        notes.value[index] = savedNote
      }
    } else {
      // 添加新笔记
      savedNote = await apiService.createReviewNote(noteData)
      // 注意：apiService.createReviewNote直接返回新建的笔记对象，不需要访问savedNote.data
      notes.value.unshift(savedNote) // 新笔记添加到最前面
      selectedNoteId.value = savedNote.id // 选中新笔记
    }

    closeModal()
  } catch (err) {
    error.value = editingNote.value ? '更新笔记失败' : '创建笔记失败'
    console.error('Failed to save note:', err)
  } finally {
    submitting.value = false
  }
}

// 关闭弹窗
const closeModal = () => {
  showAddModal.value = false
  editingNote.value = null
  resetForm()
}

// 重置表单
const resetForm = () => {
  formData.value = {
    title: '',
    content: '',
    stockCode: '',
    stockName: '',
    tags: ''
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateString
  }
}

// 截断文本
const truncateText = (text, maxLength = 60) => {
  if (!text) return ''
  // 移除Markdown标记并清理多余空格
  const plainText = text.replace(/#|\*|\||\n|-|_/g, ' ').replace(/\s+/g, ' ').trim()
  return plainText.length > maxLength ? plainText.substring(0, maxLength) + '...' : plainText
}

// 格式化内容显示（增强的Markdown渲染）
const formatContent = (content) => {
  if (!content) return ''
  
  let formatted = content
    // 标题处理
    .replace(/#{3}\s+([^\n]+)/g, '<h3 class="markdown-h3">$1</h3>')
    .replace(/#{2}\s+([^\n]+)/g, '<h2 class="markdown-h2">$1</h2>')
    .replace(/#\s+([^\n]+)/g, '<h1 class="markdown-h1">$1</h1>')
    // 无序列表处理
    .replace(/\n-\s+([^\n]+)/g, '<ul class="markdown-list"><li class="markdown-list-item">$1</li></ul>')
    // 移除多余的ul标签
    .replace(/<\/ul>\s*<ul class="markdown-list">/g, '')
    // 代码块处理
    .replace(/```([\s\S]*?)```/gm, '<pre class="markdown-code"><code>$1</code></pre>')
    // 行内代码处理
    .replace(/`([^`]+)`/g, '<code class="markdown-code-inline">$1</code>')
    // 强调处理
    .replace(/\*\*(.*?)\*\*/g, '<strong class="markdown-strong">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="markdown-em">$1</em>')
    // 段落处理
    .replace(/^(?!<h|<ul|<pre|<code)([^\n]+)/gm, '<p class="markdown-p">$1</p>')
    .replace(/\n/g, '<br>')
  
  return formatted
}

// 获取股票名称
const getStockName = async (code) => {
  if (!code) return ''
  try {
    const stockDetail = await apiService.getStockDetail(code)
    return stockDetail?.name || ''
  } catch (err) {
    console.error('Failed to get stock name:', err)
    return ''
  }
}
</script>

<style scoped>
/* CSS变量系统 */
:root {
  /* 主题色 */
  --primary-color: #1890ff;
  --primary-light: #e6f7ff;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --danger-color: #f5222d;
  
  /* 文字色 */
  --text-primary: #333333;
  --text-regular: #666666;
  --text-secondary: #999999;
  --text-placeholder: #bfbfbf;
  
  /* 边框色 */
  --border-color: #d9d9d9;
  --border-light: #f0f0f0;
  --border-hover: #40a9ff;
  
  /* 背景色 */
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-disabled: #f5f5f5;
  --bg-hover: #fafafa;
  
  /* 阴影 */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.09);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);
  
  /* 圆角 */
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
  
  /* 间距 */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  
  /* 过渡 */
  --transition-base: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-fast: all 0.2s ease;
}

/* 全局重置 */
* {
  box-sizing: border-box;
}

/* 主容器 */
.review-notes-container {
  padding: var(--space-lg);
  height: calc(100vh - 64px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-secondary);
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-light);
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.header-icon {
  color: var(--primary-color);
  font-size: 24px;
}

/* 统计信息 */
.stats-container {
  display: flex;
  gap: var(--space-md);
  background-color: var(--bg-primary);
  padding: var(--space-md);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-lg);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: var(--space-xs);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 错误消息样式 */
.error-message {
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: var(--border-radius-md);
  padding: var(--space-md);
  margin-bottom: var(--space-lg);
  display: flex;
  align-items: center;
  gap: var(--space-md);
  color: var(--danger-color);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: var(--transition-fast);
  animation: shake 0.3s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-3px); }
  75% { transform: translateX(3px); }
}

.error-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.error-text {
  flex: 1;
  font-size: 14px;
}

.error-close {
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  font-size: 16px;
  padding: var(--space-xs);
  border-radius: 50%;
  transition: var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.error-close:hover {
  background-color: rgba(245, 34, 45, 0.1);
  transform: scale(1.1);
}

/* 主内容区域 */
.notes-content {
  flex: 1;
  display: flex;
  gap: var(--space-lg);
  overflow: hidden;
}

/* 左侧笔记列表 */
.notes-sidebar {
  width: 360px;
  display: flex;
  flex-direction: column;
  border-radius: var(--border-radius-md);
  background: var(--bg-primary);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: var(--transition-base);
}

.notes-sidebar:hover {
  box-shadow: var(--shadow-md);
}

/* 搜索框增强 */
.search-box {
  padding: var(--space-md);
  border-bottom: 1px solid var(--border-light);
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-placeholder);
  font-size: 14px;
  pointer-events: none;
  transition: var(--transition-fast);
}

.search-box input {
  width: 100%;
  padding: 10px 40px 10px 36px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: 14px;
  transition: var(--transition-fast);
}

.search-box input:focus {
  border-color: var(--border-hover);
  outline: none;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.search-box input:focus + .search-icon {
  color: var(--primary-color);
}

.search-box input:disabled {
  background-color: var(--bg-disabled);
  cursor: not-allowed;
}

.clear-search-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: var(--text-placeholder);
  cursor: pointer;
  font-size: 14px;
  padding: 4px;
  border-radius: 50%;
  transition: var(--transition-fast);
  opacity: 0;
  pointer-events: none;
}

.clear-search-btn.visible {
  opacity: 1;
  pointer-events: all;
}

.clear-search-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-secondary);
}

/* 加载状态样式 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  color: var(--text-regular);
  gap: var(--space-md);
  height: 200px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-light);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-spinner.small {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
}

/* 笔记列表 */
.notes-list {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) var(--bg-secondary);
}

.notes-list::-webkit-scrollbar {
  width: 6px;
}

.notes-list::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

.notes-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
  transition: var(--transition-fast);
}

.notes-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

.note-item {
  padding: var(--space-md);
  border-bottom: 1px solid var(--border-light);
  cursor: pointer;
  transition: var(--transition-base);
  position: relative;
  overflow: hidden;
}

.note-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: transparent;
  transition: var(--transition-fast);
}

.note-item:hover {
  background-color: var(--bg-hover);
  transform: translateX(2px);
}

.note-item:hover::before {
  background-color: var(--primary-color);
}

.note-item.active {
  background-color: var(--primary-light);
  border-left: 4px solid var(--primary-color);
  transform: translateX(0);
}

.note-item.active::before {
  background-color: var(--primary-color);
}

.note-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
  font-size: 12px;
  color: var(--text-secondary);
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.note-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: var(--space-xs);
}

.note-tag {
  background-color: var(--primary-light);
  color: var(--primary-color);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  transition: var(--transition-fast);
}

.note-stock {
  background-color: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  transition: var(--transition-fast);
}

.note-stock:hover {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

.note-date {
  font-family: monospace;
}

.note-preview {
  font-size: 13px;
  color: var(--text-regular);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  transition: var(--transition-fast);
}

/* 空状态 */
.empty-state {
  padding: var(--space-xl);
  text-align: center;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: var(--space-md);
  color: var(--text-placeholder);
  opacity: 0.5;
  transition: var(--transition-base);
}

.empty-state:hover .empty-state-icon {
  opacity: 0.8;
  transform: scale(1.1) rotate(5deg);
}

.empty-state-text {
  font-size: 14px;
  margin-bottom: var(--space-md);
}

/* 右侧笔记详情 */
.notes-main {
  flex: 1;
  background: var(--bg-primary);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: var(--transition-base);
}

.notes-main:hover {
  box-shadow: var(--shadow-md);
}

.note-detail {
  flex: 1;
  padding: var(--space-lg);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) var(--bg-secondary);
  transition: var(--transition-base);
}

.note-detail::-webkit-scrollbar {
  width: 6px;
}

.note-detail::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

.note-detail::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
  transition: var(--transition-fast);
}

.note-detail::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-light);
  gap: var(--space-md);
}

.detail-header h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
  line-height: 1.4;
  word-break: break-word;
}

.detail-actions {
  display: flex;
  gap: var(--space-sm);
  flex-shrink: 0;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
  font-size: 14px;
  color: var(--text-regular);
}

.detail-meta-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.detail-meta-label {
  color: var(--text-secondary);
  font-size: 13px;
}

.detail-stock a {
  color: var(--primary-color);
  text-decoration: none;
  transition: var(--transition-fast);
  font-weight: 500;
}

.detail-stock a:hover {
  text-decoration: underline;
  color: var(--border-hover);
}

.detail-tags {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
  margin: var(--space-md) 0;
}

.detail-tag {
  background-color: var(--primary-light);
  color: var(--primary-color);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  transition: var(--transition-fast);
}

.detail-tag:hover {
  background-color: var(--primary-color);
  color: white;
  transform: translateY(-1px);
}

/* Markdown 增强样式 */
.detail-content {
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-primary);
  padding: var(--space-md) 0;
}

/* 标题样式 */
.detail-content h1,
.detail-content h2,
.detail-content h3,
.detail-content h4,
.detail-content h5,
.detail-content h6,
.markdown-h1,
.markdown-h2,
.markdown-h3 {
  margin: 28px 0 16px 0;
  color: var(--text-primary);
  font-weight: 600;
  line-height: 1.4;
}

.markdown-h1,
.detail-content h1 {
  font-size: 28px;
  border-bottom: 2px solid var(--border-light);
  padding-bottom: 8px;
}

.markdown-h2,
.detail-content h2 {
  font-size: 24px;
  position: relative;
  padding-left: 12px;
}

.markdown-h2::before,
.detail-content h2::before {
  content: '';
  position: absolute;
  left: 0;
  top: 5px;
  bottom: 5px;
  width: 3px;
  background-color: var(--primary-color);
  border-radius: 3px;
}

.markdown-h3,
.detail-content h3 {
  font-size: 20px;
  color: var(--text-primary);
}

/* 段落样式 */
.markdown-p,
.detail-content p {
  margin-bottom: 16px;
  line-height: 1.7;
  color: var(--text-regular);
  word-break: break-word;
}

/* 列表样式 */
.markdown-list,
.detail-content ul,
.detail-content ol {
  padding-left: 28px;
  margin: 16px 0;
}

.markdown-list-item,
.detail-content li {
  margin-bottom: 8px;
  line-height: 1.6;
  color: var(--text-regular);
}

.markdown-list-item::marker,
.detail-content ul li::marker {
  color: var(--primary-color);
  font-size: 16px;
}

/* 代码样式 */
.markdown-code,
.detail-content pre {
  background-color: #f6f8fa;
  padding: 16px;
  border-radius: var(--border-radius-md);
  margin: 16px 0;
  overflow-x: auto;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  border: 1px solid #e1e4e8;
  transition: var(--transition-fast);
}

.markdown-code:hover,
.detail-content pre:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.markdown-code code,
.detail-content pre code {
  color: #e96900;
  background-color: transparent;
  padding: 0;
  font-size: inherit;
}

.markdown-code-inline,
.detail-content code {
  background-color: #f6f8fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  color: #e96900;
  transition: var(--transition-fast);
}

.markdown-code-inline:hover,
.detail-content code:hover {
  background-color: #e9ecef;
}

/* 强调样式 */
.markdown-strong,
.detail-content strong {
  font-weight: 600;
  color: var(--text-primary);
}

.markdown-em,
.detail-content em {
  font-style: italic;
  color: var(--text-regular);
}

/* 链接样式 */
.detail-content a {
  color: var(--primary-color);
  text-decoration: none;
  transition: var(--transition-fast);
  border-bottom: 1px solid transparent;
}

.detail-content a:hover {
  color: var(--border-hover);
  border-bottom-color: var(--primary-color);
}

/* 空详情状态 */
.empty-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  gap: var(--space-md);
  padding: var(--space-xl);
  text-align: center;
}

.empty-detail-icon {
  font-size: 80px;
  color: var(--text-placeholder);
  opacity: 0.3;
  margin-bottom: var(--space-md);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.empty-detail-text {
  font-size: 16px;
  margin-bottom: var(--space-md);
  color: var(--text-regular);
}

.empty-detail-subtext {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: var(--space-lg);
}

.retry-btn {
  padding: 10px 20px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: var(--transition-base);
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.retry-btn:hover {
  background-color: var(--border-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

/* 弹窗样式增强 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(2px);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  width: 90vw;
  max-width: 640px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideIn {
  from { transform: translateY(-30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal.large {
  max-width: 800px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--border-light);
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.modal-title-icon {
  color: var(--primary-color);
  font-size: 16px;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: var(--transition-base);
  flex-shrink: 0;
}

.close-btn:hover:not(:disabled) {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  transform: scale(1.1);
}

.close-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.modal-body {
  padding: var(--space-lg);
  overflow-y: auto;
  flex: 1;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) var(--bg-secondary);
}

.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

.modal-body::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

/* 表单样式增强 */
.form-group {
  margin-bottom: var(--space-lg);
}

.form-group label {
  display: block;
  margin-bottom: var(--space-xs);
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
}

.form-group label .required {
  color: var(--danger-color);
  margin-left: 4px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: 14px;
  font-family: inherit;
  transition: var(--transition-fast);
  background-color: var(--bg-primary);
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: var(--border-hover);
  outline: none;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-group input:disabled,
.form-group textarea:disabled {
  background-color: var(--bg-disabled);
  cursor: not-allowed;
}

.title-input {
  font-size: 16px;
  font-weight: 500;
}

.content-textarea {
  resize: vertical;
  min-height: 320px;
  line-height: 1.6;
  font-size: 14px;
}

.form-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* 底部按钮区域 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--border-light);
  flex-shrink: 0;
  gap: var(--space-md);
  background-color: #fafafa;
}

/* 按钮样式增强 */
.btn {
  padding: 10px 18px;
  border: 1px solid var(--border-color);
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  min-width: 80px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
  transform: none;
}

.btn:hover:not(:disabled) {
  border-color: var(--border-hover);
  color: var(--primary-color);
  transform: translateY(-1px);
}

.btn.primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.btn.primary:hover:not(:disabled) {
  background-color: var(--border-hover);
  border-color: var(--border-hover);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

.btn.text {
  border: none;
  background: transparent;
  color: var(--primary-color);
  padding: 8px 16px;
  min-width: auto;
}

.btn.text:hover:not(:disabled) {
  background-color: var(--primary-light);
  color: var(--primary-color);
  transform: none;
}

.btn.text.danger {
  color: var(--danger-color);
}

.btn.text.danger:hover:not(:disabled) {
  background-color: #fff2f0;
  color: var(--danger-color);
}

/* 响应式设计增强 */
@media (max-width: 1200px) {
  .review-notes-container {
    padding: var(--space-md);
  }
  
  .notes-sidebar {
    width: 320px;
  }
  
  .modal.large {
    max-width: 90vw;
  }
}

@media (max-width: 1024px) {
  .notes-sidebar {
    width: 280px;
  }
  
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .detail-actions {
    width: 100%;
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .review-notes-container {
    height: 100vh;
    padding: var(--space-sm);
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-md);
  }
  
  .stats-container {
    flex-wrap: wrap;
    gap: var(--space-sm);
  }
  
  .stat-item {
    min-width: calc(50% - 8px);
  }
  
  .notes-content {
    flex-direction: column;
    gap: var(--space-md);
  }
  
  .notes-sidebar {
    width: 100%;
    height: 40%;
    max-height: 300px;
  }
  
  .notes-main {
    height: 60%;
  }
  
  .note-detail {
    padding: var(--space-md);
  }
  
  .detail-header h3 {
    font-size: 20px;
  }
  
  .detail-meta {
    flex-direction: column;
    gap: var(--space-sm);
  }
  
  .modal {
    width: calc(100vw - 20px);
    margin: 10px;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: var(--space-md);
  }
  
  .modal-footer {
    flex-direction: column-reverse;
    gap: var(--space-sm);
  }
  
  .modal-footer .btn {
    width: 100%;
  }
  
  .content-textarea {
    min-height: 240px;
  }
}

@media (max-width: 480px) {
  .review-notes-container {
    padding: var(--space-xs);
  }
  
  .page-header h2 {
    font-size: 18px;
  }
  
  .stat-item {
    min-width: 100%;
  }
  
  .search-box input {
    padding: 8px 36px 8px 32px;
  }
  
  .note-item {
    padding: var(--space-sm);
  }
  
  .note-title {
    font-size: 15px;
  }
  
  .detail-content {
    font-size: 14px;
  }
  
  .form-group input,
  .form-group textarea {
    padding: 8px 12px;
  }
}
</style>
</style>