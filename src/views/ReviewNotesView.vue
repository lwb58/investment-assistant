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
              v-for="(note, index) in filteredNotes" 
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
                {{ selectedNote.stockCode }} {{ selectedNote.stockName || '' }}
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

// 获取笔记列表（修复API调用逻辑）
const fetchNotes = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await apiService.getNotes()
    // 关键修复：后端直接返回数组，无需通过 response.data 提取
    notes.value = response || []
    if (notes.value.length > 0 && !selectedNoteId.value) {
      selectedNoteId.value = notes.value[0].id
    }
  } catch (err) {
    error.value = '加载笔记失败: ' + (err.message || '未知错误')
    console.error('加载笔记失败:', err)
  } finally {
    loading.value = false
  }
}

// 过滤后的笔记列表
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

// 初始化
onMounted(() => {
  fetchNotes()
})

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑由computed自动处理
}

// 清空搜索
const clearSearch = () => {
  searchKeyword.value = ''
  if (notes.value.length > 0) {
    selectedNoteId.value = notes.value[0].id
  }
}

// 选择笔记
const selectNote = (note) => {
  if (!note) return
  
  selectedNoteId.value = note.id
  // 滚动到顶部
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

// 删除笔记（修复删除后状态同步）
const deleteNote = async (id) => {
  if (!confirm('确定要删除这篇笔记吗？删除后将无法恢复。')) {
    return
  }

  try {
    submitting.value = true
    await apiService.deleteNote(id)
    
    // 从本地列表移除并更新选中状态
    const currentIndex = notes.value.findIndex(note => note.id === id)
    notes.value = notes.value.filter(note => note.id !== id)
    
    if (selectedNoteId.value === id) {
      if (notes.value.length > 0) {
        // 选择删除位置的下一个或最后一个笔记
        const newIndex = Math.min(currentIndex, notes.value.length - 1)
        selectedNoteId.value = notes.value[newIndex]?.id
      } else {
        selectedNoteId.value = null
      }
    }
  } catch (err) {
    error.value = '删除笔记失败: ' + (err.message || '未知错误')
    console.error('删除笔记失败:', err)
  } finally {
    submitting.value = false
  }
}

// 保存笔记（修复API调用和错误处理）
const saveNote = async () => {
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

    let result
    if (editingNote.value) {
      // 更新笔记
      result = await apiService.updateNote(editingNote.value.id, noteData)
      const updatedNote = result.data || result
      // 更新本地列表
      const index = notes.value.findIndex(note => note.id === editingNote.value.id)
      if (index > -1) {
        notes.value[index] = updatedNote
      }
    } else {
      // 创建新笔记
      result = await apiService.createReviewNote(noteData)
      const newNote = result.data || result
      notes.value.unshift(newNote)
      selectedNoteId.value = newNote.id
    }

    closeModal()
  } catch (err) {
    error.value = editingNote.value 
      ? '更新笔记失败: ' + (err.message || '未知错误')
      : '创建笔记失败: ' + (err.message || '未知错误')
    console.error('保存笔记失败:', err)
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
  const plainText = text.replace(/#|\*|\||\n|-|_/g, ' ').replace(/\s+/g, ' ').trim()
  return plainText.length > maxLength ? plainText.substring(0, maxLength) + '...' : plainText
}

// 格式化内容（Markdown渲染）
const formatContent = (content) => {
  if (!content) return ''
  
  return content
    .replace(/#{3}\s+([^\n]+)/g, '<h3 class="markdown-h3">$1</h3>')
    .replace(/#{2}\s+([^\n]+)/g, '<h2 class="markdown-h2">$1</h2>')
    .replace(/#\s+([^\n]+)/g, '<h1 class="markdown-h1">$1</h1>')
    .replace(/\n-\s+([^\n]+)/g, '<ul class="markdown-list"><li class="markdown-list-item">$1</li></ul>')
    .replace(/<\/ul>\s*<ul class="markdown-list">/g, '')
    .replace(/```([\s\S]*?)```/gm, '<pre class="markdown-code"><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="markdown-code-inline">$1</code>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="markdown-strong">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="markdown-em">$1</em>')
    .replace(/^(?!<h|<ul|<pre|<code)([^\n]+)/gm, '<p class="markdown-p">$1</p>')
    .replace(/\n/g, '<br>')
}

// 获取股票名称（新增错误处理）
const getStockName = async (code) => {
  if (!code) return ''
  try {
    // 关键修复：后端返回的是直接数据，无 data 字段
    const stockDetail = await apiService.getStockDetail(code)
    return stockDetail?.name || ''
  } catch (err) {
    console.error('获取股票名称失败:', err)
    return ''  // 失败时返回空字符串，避免页面报错
  }
}
</script>

<style scoped>
/* 保持原有样式不变，此处省略重复样式 */
:root {
  /* 更现代的颜色方案 */
  --primary-color: #3b82f6;
  --primary-light: #eff6ff;
  --primary-dark: #2563eb;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --text-primary: #1f2937;
  --text-regular: #4b5563;
  --text-secondary: #9ca3af;
  --text-placeholder: #d1d5db;
  --border-color: #e5e7eb;
  --border-light: #f3f4f6;
  --border-hover: #60a5fa;
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-tertiary: #f3f4f6;
  --bg-disabled: #f3f4f6;
  --bg-hover: #f9fafb;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --border-radius-sm: 6px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
  --border-radius-full: 9999px;
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --transition-base: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-fast: all 0.2s ease;
  --transition-slow: all 0.5s ease;
}

.review-notes-container {
  padding: var(--space-md);
  height: calc(100vh - 64px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-secondary);
  position: relative;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
  padding: var(--space-md);
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  background: linear-gradient(to right, var(--primary-color), var(--primary-dark));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.notes-stats {
  margin-top: var(--space-sm);
  color: var(--text-secondary);
  font-size: 14px;
  display: flex;
  gap: var(--space-md);
}

.stats-item {
  background-color: var(--bg-tertiary);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--border-radius-full);
  font-weight: 500;
}

.notes-content {
  display: flex;
  gap: var(--space-md);
  height: calc(100% - 60px);
  flex: 1;
}

.notes-sidebar {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .review-notes-container {
    padding: var(--space-sm);
  }
  
  .page-header {
    padding: var(--space-sm);
  }
  
  .notes-sidebar {
    width: 280px;
  }
  
  .notes-main {
    padding: var(--space-lg);
  }
}

@media (max-width: 768px) {
  .notes-content {
    flex-direction: column;
    height: auto;
  }
  
  .review-notes-container {
    height: auto;
    min-height: 100vh;
    padding-bottom: var(--space-xl);
  }
  
  .notes-sidebar {
    width: 100%;
    height: 40vh;
    margin-bottom: var(--space-md);
  }
  
  .notes-main {
    height: 50vh;
    padding: var(--space-md);
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-md);
  }
  
  .btn-group {
    display: flex;
    gap: var(--space-sm);
  }
  
  .page-title {
    justify-content: center;
    font-size: 18px;
  }
  
  .stats-item {
    font-size: 12px;
  }
  
  .detail-title {
    font-size: 22px;
  }
  
  .modal-content {
    width: 95%;
    margin: var(--space-md);
    max-height: 95vh;
  }
}

@media (max-width: 480px) {
  .note-item {
    padding: var(--space-sm);
  }
  
  .note-title {
    font-size: 14px;
  }
  
  .note-meta {
    font-size: 11px;
  }
  
  .note-preview {
    font-size: 12px;
  }
  
  .detail-content {
    font-size: 14px;
  }
  
  .modal-header,
  .modal-body {
    padding: var(--space-md);
  }
}

.search-box {
  position: relative;
  margin-bottom: var(--space-md);
  transition: var(--transition-base);
}

.search-input {
  width: 100%;
  padding: var(--space-md) var(--space-md) var(--space-md) 40px;
  border: 2px solid var(--border-light);
  border-radius: var(--border-radius-md);
  font-size: 14px;
  transition: var(--transition-base);
  font-weight: 500;
  color: var(--text-primary);
  background-color: var(--bg-primary);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  transform: translateY(-1px);
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 16px;
}

.clear-search {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: var(--transition-base);
}

.clear-search:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.notes-list {
  flex: 1;
  overflow-y: auto;
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--space-md);
  transition: var(--transition-base);
}

.note-item {
  padding: var(--space-md);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--space-md);
  cursor: pointer;
  transition: var(--transition-base);
  border-left: 4px solid transparent;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  position: relative;
  overflow: hidden;
  transform-origin: center left;
}

.note-item:hover {
  background-color: var(--bg-hover);
  transform: translateX(4px) translateY(-2px) scale(1.01);
  border-color: var(--primary-light);
  box-shadow: var(--shadow-md);
  z-index: 10;
}

.note-item.active {
  background-color: var(--primary-light);
  border-left-color: var(--primary-color);
  border-color: var(--primary-light);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1), var(--shadow-md);
  transform: translateX(4px);
}

/* 笔记卡片标签样式 */
.note-tags {
  display: flex;
  gap: var(--space-xs);
  margin-top: var(--space-xs);
  flex-wrap: wrap;
}

.note-tag {
  background-color: var(--primary-light);
  color: var(--primary-color);
  padding: 2px 8px;
  border-radius: var(--border-radius-full);
  font-size: 11px;
  font-weight: 500;
  transition: var(--transition-fast);
}

.note-item:hover .note-tag {
  transform: scale(1.05);
}

.note-title {
  font-weight: 500;
  margin-bottom: var(--space-xs);
  color: var(--text-primary);
}

.note-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: var(--space-xs);
}

.note-preview {
  font-size: 13px;
  color: var(--text-regular);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.notes-main {
  flex: 1;
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  overflow-y: auto;
  padding: var(--space-2xl);
  position: relative;
  transition: var(--transition-base);
}

.note-detail {
  animation: fadeIn 0.3s ease-out, slideInUp 0.3s ease-out;
  transition: var(--transition-base);
}

/* 增强动画效果 */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* 笔记状态指示器 */
.note-status {
  position: absolute;
  top: var(--space-md);
  right: var(--space-md);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--success-color);
  transition: var(--transition-base);
}

.note-item:hover .note-status {
  transform: scale(1.5);
}

/* 添加加载动画 */
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.shimmer {
  background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-secondary) 50%, var(--bg-tertiary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 2px solid var(--border-light);
  position: relative;
}

.detail-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
}

.detail-meta {
  margin-bottom: var(--space-lg);
  padding: var(--space-md);
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius-md);
  font-size: 14px;
  border-left: 4px solid var(--primary-color);
}

.meta-item {
  margin-right: var(--space-lg);
  display: inline-block;
  margin-bottom: var(--space-xs);
  font-weight: 500;
}

.meta-label {
  color: var(--text-secondary);
  margin-right: var(--space-xs);
}

.detail-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-regular);
  font-weight: 400;
  background-color: var(--bg-primary);
  padding: var(--space-md);
  border-radius: var(--border-radius-md);
}

/* 增强markdown内容的样式 */
.detail-content :deep(h1),
.detail-content :deep(h2),
.detail-content :deep(h3),
.detail-content :deep(h4),
.detail-content :deep(h5),
.detail-content :deep(h6) {
  color: var(--text-primary);
  margin-top: var(--space-lg);
  margin-bottom: var(--space-md);
  font-weight: 600;
}

.detail-content :deep(p) {
  margin-bottom: var(--space-md);
}

.detail-content :deep(blockquote) {
  border-left: 4px solid var(--primary-color);
  padding-left: var(--space-md);
  color: var(--text-secondary);
  margin-left: 0;
}

.detail-content :deep(pre) {
  background-color: var(--bg-tertiary);
  padding: var(--space-md);
  border-radius: var(--border-radius-md);
  overflow-x: auto;
  margin-bottom: var(--space-md);
}

.detail-content :deep(code) {
  background-color: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: var(--border-radius-sm);
  font-family: monospace;
}

.markdown-h1 {
  font-size: 20px;
  margin: 1.5em 0 0.5em;
  color: var(--text-primary);
}

.markdown-h2 {
  font-size: 18px;
  margin: 1.2em 0 0.5em;
  color: var(--text-primary);
}

.markdown-h3 {
  font-size: 16px;
  margin: 1em 0 0.5em;
  color: var(--text-primary);
}

.markdown-list {
  margin: 0.5em 0 0.5em 1.5em;
}

.markdown-list-item {
  margin-bottom: 0.3em;
}

.markdown-code {
  background-color: var(--bg-secondary);
  padding: var(--space-md);
  border-radius: var(--border-radius-sm);
  overflow-x: auto;
  margin: 0.5em 0;
}

.markdown-code-inline {
  background-color: var(--bg-secondary);
  padding: 2px 4px;
  border-radius: 2px;
  font-family: monospace;
}

.markdown-strong {
  font-weight: 600;
}

.markdown-em {
  font-style: italic;
}

.markdown-p {
  margin: 0.8em 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: var(--transition-base);
  animation: fadeIn 0.3s ease;
}

.modal-overlay.modal-open {
  opacity: 1;
  visibility: visible;
}

.modal {
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 650px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  transform: translateY(-20px);
  transition: var(--transition-base);
  animation: slideIn 0.3s ease;
  border: 1px solid var(--border-light);
}

.modal-overlay.modal-open .modal {
  transform: translateY(0);
}

.modal-header {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-secondary);
}

.modal-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-base);
}

.close-btn:hover {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

.modal-body {
  padding: var(--space-lg);
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: var(--space-lg);
  position: relative;
}

.form-label {
  display: block;
  margin-bottom: var(--space-sm);
  color: var(--text-primary);
  font-weight: 600;
  font-size: 14px;
}

.required {
  color: var(--danger-color);
}

.form-input {
  width: 100%;
  padding: var(--space-md) var(--space-md);
  border: 2px solid var(--border-light);
  border-radius: var(--border-radius-md);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  transition: var(--transition-base);
  font-weight: 500;
}

.form-input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  transform: translateY(-1px);
}

.form-input.error {
  border-color: var(--danger-color);
}

.form-input.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-input-error {
  border-color: var(--danger-color);
}

.form-textarea {
  width: 100%;
  padding: var(--space-md) var(--space-md);
  border: 2px solid var(--border-light);
  border-radius: var(--border-radius-md);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  resize: vertical;
  transition: var(--transition-base);
  font-weight: 500;
  height: 250px;
  min-height: 150px;
  font-family: inherit;
}

.form-textarea:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  transform: translateY(-1px);
}

.form-textarea.error {
  border-color: var(--danger-color);
}

.form-textarea.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* 表单验证和帮助文本 */
.form-error {
  color: var(--danger-color);
  font-size: 12px;
  margin-top: var(--space-xs);
  display: block;
}

.form-help {
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: var(--space-xs);
  display: block;
}

/* 标签输入增强 */
.tags-input-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  border: 2px solid var(--border-light);
  border-radius: var(--border-radius-md);
  min-height: 48px;
  transition: var(--transition-base);
}

.tags-input-container:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.tags-input {
  border: none;
  outline: none;
  flex: 1;
  min-width: 120px;
  padding: var(--space-xs) 0;
  font-size: 14px;
}

.tag {
  background-color: var(--primary-light);
  color: var(--primary-color);
  padding: 4px 10px;
  border-radius: var(--border-radius-full);
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  transition: var(--transition-fast);
}

.tag:hover {
  background-color: var(--primary-color);
  color: white;
  transform: scale(1.05);
}

.tag-remove {
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

.modal-footer {
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  background-color: var(--bg-secondary);
}

/* 提交按钮加载状态 */
.btn-loading {
  opacity: 0.7;
  cursor: not-allowed;
  position: relative;
  overflow: hidden;
}

.btn-loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  animation: loadingShine 1.5s infinite;
}

@keyframes loadingShine {
  100% {
    left: 100%;
  }
}

.btn {
  padding: var(--space-md) calc(var(--space-md) + 8px);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-base);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  position: relative;
  overflow: hidden;
}

.btn:hover {
  background-color: var(--bg-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.btn.primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  background-image: linear-gradient(45deg, var(--primary-color), var(--primary-dark));
}

.btn.primary:hover {
  background-color: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  background-image: linear-gradient(45deg, var(--primary-dark), var(--primary-color));
}

.btn.text {
  background-color: transparent;
  border-color: transparent;
  color: var(--text-primary);
  padding: var(--space-xs) var(--space-sm);
}

.btn.text.danger {
  color: var(--danger-color);
}

.btn.text:hover {
  background-color: var(--bg-hover);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  color: var(--text-secondary);
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(59, 130, 246, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: var(--space-md);
}

.loading-spinner.small {
  width: 16px;
  height: 16px;
  margin-right: 6px;
}

.empty-state, .empty-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  text-align: center;
  padding: var(--space-2xl);
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
  animation: fadeInUp 0.5s ease-out;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: var(--space-md);
  opacity: 0.3;
  color: var(--primary-light);
  transition: var(--transition-base);
}

.empty-icon:hover {
  opacity: 0.6;
  transform: scale(1.1);
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: var(--space-sm);
  color: var(--text-primary);
}

.empty-description {
  font-size: 14px;
  margin-bottom: var(--space-lg);
  max-width: 400px;
}

.error-message {
  background-color: rgba(239, 68, 68, 0.05);
  border: 1px solid var(--danger-light);
  border-radius: var(--border-radius-md);
  padding: var(--space-md);
  margin-bottom: var(--space-lg);
  display: flex;
  align-items: center;
  gap: var(--space-md);
  color: var(--danger-color);
  box-shadow: 0 1px 3px rgba(239, 68, 68, 0.1);
  animation: slideInRight 0.3s ease-out;
}

.error-close {
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  margin-left: auto;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
}

.error-close:hover {
  background-color: rgba(239, 68, 68, 0.1);
  transform: rotate(90deg);
}

/* 移除重复的标签样式定义，保留之前更现代的实现 */

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 确保CSS变量定义完整 */
:root {
  --primary-light: rgba(59, 130, 246, 0.1);
  --danger-light: rgba(239, 68, 68, 0.2);
  --space-2xl: 2rem;
}

@media (max-width: 768px) {
  .notes-content {
    flex-direction: column;
    height: auto;
  }
  
  .notes-sidebar {
    width: 100%;
    height: 300px;
    margin-bottom: var(--space-md);
  }
  
  .notes-main {
    height: 400px;
  }
}
</style>