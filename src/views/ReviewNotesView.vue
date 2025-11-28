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
  try {
    loading.value = true
    error.value = null
    const response = await apiService.getReviewNotes()
    // 确保正确处理后端返回格式（假设后端返回 { data: [...] }）
    notes.value = response.data || response || []
    // 默认选中第一个笔记
    if (notes.value.length > 0 && !selectedNoteId.value) {
      selectedNoteId.value = notes.value[0].id
    }
  } catch (err) {
    error.value = '获取笔记列表失败: ' + (err.message || '未知错误')
    console.error('获取笔记列表失败:', err)
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
    const result = await apiService.getStockDetail(code)
    const stockDetail = result.data || result
    return stockDetail?.name || ''
  } catch (err) {
    console.error('获取股票名称失败:', err)
    return ''
  }
}
</script>

<style scoped>
/* 保持原有样式不变，此处省略重复样式 */
:root {
  --primary-color: #1890ff;
  --primary-light: #e6f7ff;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --danger-color: #f5222d;
  --text-primary: #333333;
  --text-regular: #666666;
  --text-secondary: #999999;
  --text-placeholder: #bfbfbf;
  --border-color: #d9d9d9;
  --border-light: #f0f0f0;
  --border-hover: #40a9ff;
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-disabled: #f5f5f5;
  --bg-hover: #fafafa;
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.09);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --transition-base: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-fast: all 0.2s ease;
}

.review-notes-container {
  padding: var(--space-lg);
  height: calc(100vh - 64px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-secondary);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-light);
}

.page-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.notes-stats {
  margin-top: var(--space-sm);
  color: var(--text-secondary);
  font-size: 14px;
}

.stats-item {
  margin-right: var(--space-md);
}

.notes-content {
  display: flex;
  gap: var(--space-lg);
  height: calc(100% - 60px);
}

.notes-sidebar {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.search-box {
  position: relative;
  margin-bottom: var(--space-md);
}

.search-input {
  width: 100%;
  padding: var(--space-sm) var(--space-md) var(--space-sm) 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: 14px;
  transition: var(--transition-base);
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
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
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.notes-list {
  flex: 1;
  overflow-y: auto;
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
  padding: var(--space-md);
}

.note-item {
  padding: var(--space-md);
  border-radius: var(--border-radius-sm);
  margin-bottom: var(--space-sm);
  cursor: pointer;
  transition: var(--transition-base);
  border-left: 3px solid transparent;
}

.note-item.active {
  background-color: var(--primary-light);
  border-left-color: var(--primary-color);
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
  box-shadow: var(--shadow-sm);
  overflow-y: auto;
  padding: var(--space-lg);
}

.note-detail {
  animation: fadeIn 0.3s ease;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-light);
}

.detail-title {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
}

.detail-meta {
  margin-bottom: var(--space-lg);
  padding: var(--space-md);
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  font-size: 13px;
}

.meta-item {
  margin-right: var(--space-lg);
  display: inline-block;
  margin-bottom: var(--space-xs);
}

.meta-label {
  color: var(--text-secondary);
}

.detail-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-primary);
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
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: var(--transition-base);
}

.modal-overlay.modal-open {
  opacity: 1;
  visibility: visible;
}

.modal {
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-md);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  transform: translateY(-20px);
  transition: var(--transition-base);
}

.modal-overlay.modal-open .modal {
  transform: translateY(0);
}

.modal-header {
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 18px;
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
  margin-bottom: var(--space-md);
}

.form-label {
  display: block;
  margin-bottom: var(--space-xs);
  color: var(--text-primary);
  font-weight: 500;
}

.required {
  color: var(--danger-color);
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  font-size: 14px;
  transition: var(--transition-base);
}

.form-input:focus {
  border-color: var(--border-hover);
  outline: none;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-input-error {
  border-color: var(--danger-color);
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  font-size: 14px;
  resize: none;
  transition: var(--transition-base);
}

.form-textarea:focus {
  border-color: var(--border-hover);
  outline: none;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.modal-footer {
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
}

.btn {
  padding: 8px 16px;
  border-radius: var(--border-radius-sm);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-base);
  border: 1px solid var(--border-color);
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.btn:hover {
  background-color: var(--bg-hover);
}

.btn.primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.btn.primary:hover {
  background-color: #40a9ff;
}

.btn.text {
  background-color: transparent;
  border-color: transparent;
  color: var(--text-primary);
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
  padding: var(--space-lg);
  color: var(--text-secondary);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(24, 144, 255, 0.2);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: var(--space-sm);
}

.loading-spinner.small {
  width: 16px;
  height: 16px;
  margin-right: 6px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  color: var(--text-secondary);
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--space-md);
  opacity: 0.5;
}

.empty-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  text-align: center;
  padding: var(--space-xl);
}

.empty-title {
  font-size: 18px;
  margin-bottom: var(--space-sm);
  color: var(--text-primary);
}

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
}

.tag {
  display: inline-block;
  padding: 2px 6px;
  background-color: var(--bg-secondary);
  border-radius: 4px;
  font-size: 12px;
  margin-right: 4px;
  color: var(--text-secondary);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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