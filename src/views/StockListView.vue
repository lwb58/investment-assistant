<template>
  <div class="stock-list-container">
    <!-- 页面头部（无修改） -->
    <div class="card mb-3">
      <div class="card-header">
        <h2 class="card-title">股票清单</h2>
        <div class="header-actions flex items-center gap-2">
          <div class="search-box relative">
            <span class="search-icon absolute left-3 top-1/2 transform -translate-y-1/2 text-tertiary">🔍</span>
            <input 
              type="text" 
              placeholder="搜索股票代码、名称或行业"
              v-model="searchKeyword"
              @input="handleSearch"
              class="pl-10 pr-4 py-2 w-64 focus:outline-none"
            />
          </div>
          <button 
            class="btn primary"
            @click="showAddModal = true"
            :class="{ 'loading': saving }"
          >
            <span class="btn-icon">➕</span>
            添加股票
          </button>
        </div>
      </div>
    </div>

    <!-- 统计信息卡片（无修改） -->
    <div class="stats-cards grid grid-cols-3 gap-3 mb-3">
      <div class="stat-card card flex flex-col items-center justify-center p-4">
        <div class="stat-value text-2xl font-bold text-primary">{{ totalStocks }}</div>
        <div class="stat-label text-secondary">总股票数</div>
      </div>
      <div class="stat-card card flex flex-col items-center justify-center p-4">
        <div class="stat-value text-2xl font-bold text-success">{{ holdingStocks }}</div>
        <div class="stat-label text-secondary">持仓数量</div>
      </div>
      <div class="stat-card card flex flex-col items-center justify-center p-4">
        <div class="stat-value text-2xl font-bold text-warning">{{ watchingStocks }}</div>
        <div class="stat-label text-secondary">关注数量</div>
      </div>
    </div>

    <!-- 加载状态（无修改） -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">加载股票数据中...</p>
    </div>
    
    <!-- 错误信息（无修改） -->
    <div v-else-if="error" class="error-message bg-red-50 border border-red-200 text-red-600 p-4 rounded-lg flex items-center">
      <span class="error-icon mr-2">⚠️</span>
      {{ error }}
    </div>

    <!-- 股票列表（无修改） -->
    <div v-else class="card">
      <div class="table-responsive">
        <table class="stock-table">
          <thead>
            <tr>
              <th>股票代码</th>
              <th>股票名称</th>
              <th>最新价格</th>
              <th>涨跌幅</th>
              <th>所属行业</th>
              <th>持仓状态</th>
              <th class="text-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="stock in filteredStocks" 
              :key="stock.code"
              class="table-row"
            >
              <td>
                <router-link 
                  :to="'/stock-detail/' + stock.code" 
                  class="stock-code hover:text-primary transition-colors font-medium"
                >
                  {{ stock.code }}
                </router-link>
              </td>
              <td class="font-medium">{{ stock.name }}</td>
              <td class="price font-semibold">{{ formatPrice(stock.price) }}</td>
              <td>
                <span 
                  :class="[
                    'change-rate', 
                    'inline-flex items-center px-2 py-1 rounded-full text-sm font-medium',
                    stock.changeRate > 0 ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'
                  ]"
                >
                  <span :class="['change-icon', stock.changeRate > 0 ? 'up' : 'down']">
                    {{ stock.changeRate > 0 ? '↗️' : '↘️' }}
                  </span>
                  {{ stock.changeRate > 0 ? '+' : '' }}{{ stock.changeRate }}%
                </span>
              </td>
              <td>
                <span class="industry-badge px-2 py-1 bg-blue-50 text-blue-600 rounded-full text-xs">
                  {{ stock.industry }}
                </span>
              </td>
              <td>
                <div class="status-container flex items-center">
                  <label class="switch">
                    <input 
                      type="checkbox" 
                      :checked="stock.holding" 
                      @change="updateHoldingStatus(stock.code, !stock.holding)"
                    />
                    <span class="slider"></span>
                  </label>
                  <span 
                    :class="[
                      'status-text ml-2 text-sm',
                      stock.holding ? 'text-primary font-medium' : 'text-secondary'
                    ]"
                  >
                    {{ stock.holding ? '持有' : '关注' }}
                  </span>
                </div>
              </td>
              <td class="actions text-right">
                <div class="inline-flex gap-1">
                  <button 
                    class="action-btn edit-btn" 
                    @click="editStock(stock)"
                    title="编辑"
                  >
                    ✏️
                  </button>
                  <button 
                    class="action-btn delete-btn" 
                    @click="deleteStock(stock.code)"
                    title="删除"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="filteredStocks.length === 0" class="empty-state py-16">
        <div class="empty-icon text-6xl mb-4">📊</div>
        <h3 class="text-lg font-medium text-secondary mb-2">暂无股票数据</h3>
        <p class="text-tertiary mb-6">点击"添加股票"按钮开始管理您的投资组合</p>
        <button 
          class="btn primary"
          @click="showAddModal = true"
        >
          添加第一支股票
        </button>
      </div>
    </div>

    <!-- 添加/编辑股票弹窗（核心修复：搜索相关语法错误） -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal" :class="{ 'scale-up': true }">
        <div class="modal-header">
          <h3 class="text-xl font-semibold">{{ editingStock ? '编辑股票' : '添加股票' }}</h3>
          <button class="close-btn" @click="closeModal" aria-label="关闭">
            ✕
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveStock">
            <div class="form-group">
              <label class="block text-secondary mb-1 font-medium">股票选择 <span class="text-xs text-tertiary">(输入关键词查询后选择)</span></label>
              <div class="relative flex space-x-2">
                <input 
                  type="text" 
                  v-model="modalSearchKeyword"
                  :disabled="!!editingStock || fetchingDetail"
                  placeholder="输入股票代码或名称"
                  class="flex-1 p-2 border rounded"
                  @focus="handleSearchFocus"
                  @blur="handleSearchBlur"
                  required
                />
                <button 
                  type="button" 
                  class="btn primary whitespace-nowrap"
                  @click="handleStockSearch"
                  :disabled="!modalSearchKeyword.trim() || !!editingStock || fetchingDetail"
                >
                  {{ searching ? '查询中...' : '查询' }}
                </button>
                
                <!-- 修复：移除hover:bg-gray-100，改用普通CSS类避免解析冲突 -->
                <div 
                  v-if="showSearchResults && searchResults.length > 0" 
                  class="search-results absolute z-10 top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded shadow-lg max-h-60 overflow-y-auto cursor-pointer"
                >
                  <div 
                    v-for="item in searchResults" 
                    :key="item.stockCode"
                    class="search-item p-3 bg-hover-gray flex justify-between items-center"
                    @mousedown.prevent="selectSearchResult(item)"
                  >
                    <div>
                      <div class="font-medium">{{ item.stockName }}</div>
                      <div class="text-xs text-gray-500">{{ item.stockCode }}</div>
                    </div>
                    <span class="text-xs px-2 py-1 bg-blue-50 text-blue-600 rounded-full">{{ item.market }}</span>
                  </div>
                </div>
                
                <!-- 详情查询加载状态 -->
                <div v-if="fetchingDetail" class="search-loading absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                  <span class="inline-block animate-spin"></span>
                  <span class="ml-1 text-xs">获取详情中...</span>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label class="block text-secondary mb-1 font-medium">股票代码</label>
              <input 
                type="text" 
                v-model="formData.code"
                disabled
                class="w-full p-2 border rounded bg-gray-50"
                required
              />
            </div>
            <div class="form-group">
              <label class="block text-secondary mb-1 font-medium">股票名称</label>
              <input 
                type="text" 
                v-model="formData.name"
                disabled
                class="w-full p-2 border rounded bg-gray-50"
                required
              />
            </div>
            <div class="form-group">
              <label class="block text-secondary mb-1 font-medium">所属行业</label>
              <input 
                type="text" 
                v-model="formData.industry"
                disabled
                class="w-full p-2 border rounded bg-gray-50"
              />
            </div>
            <div class="form-group">
              <label class="block text-secondary mb-1 font-medium">持仓状态</label>
              <select 
                v-model="formData.holding"
                class="w-full p-2 border rounded"
              >
                <option :value="false">关注</option>
                <option :value="true">持有</option>
              </select>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="closeModal">取消</button>
          <button 
            class="btn primary" 
            @click="saveStock" 
            :disabled="saving || !formData.code || !formData.name || !formData.industry"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../api/apiService.js'
import axios from 'axios'

const router = useRouter()
const showAddModal = ref(false)
const editingStock = ref(null)
const stocks = ref([])
const loading = ref(false)
const saving = ref(false)
const error = ref(null)

// 表单数据
const formData = ref({
  code: '',
  name: '',
  industry: '',
  holding: false
})

// 搜索相关状态
const searchResults = ref([])
const showSearchResults = ref(false)
const searching = ref(false)
const fetchingDetail = ref(false)
const searchKeyword = ref('')
const modalSearchKeyword = ref('')

// 计算过滤后的股票列表
const filteredStocks = computed(() => {
  if (!searchKeyword.value) {
    return stocks.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return stocks.value.filter(stock => 
    stock.code.toLowerCase().includes(keyword) || 
    stock.name.toLowerCase().includes(keyword) ||
    stock.industry.toLowerCase().includes(keyword)
  )
})

// 统计信息
const totalStocks = computed(() => stocks.value.length)
const holdingStocks = computed(() => stocks.value.filter(s => s.holding).length)
const watchingStocks = computed(() => stocks.value.filter(s => !s.holding).length)

// 初始化数据
onMounted(() => {
  fetchStocks()
})

// 获取股票列表
const fetchStocks = async () => {
  loading.value = true
  error.value = null
  try {
    stocks.value = await apiService.getStocks()
  } catch (err) {
    error.value = '加载股票数据失败'
    console.error('获取股票列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = async () => {
  loading.value = true
  error.value = null
  try {
    stocks.value = await apiService.getStocks(searchKeyword.value)
  } catch (err) {
    error.value = '搜索失败'
    console.error('搜索股票失败:', err)
  } finally {
    loading.value = false
  }
}

// 格式化价格
const formatPrice = (price) => {
  return typeof price === 'number' ? price.toFixed(2) : price
}

// 编辑股票
const editStock = (stock) => {
  editingStock.value = stock
  formData.value = { ...stock }
  modalSearchKeyword.value = `${stock.name} (${stock.code})`
  showAddModal.value = true
}

// 删除股票
const deleteStock = async (code) => {
  if (confirm('确定要删除这支股票吗？')) {
    try {
      await apiService.deleteStock(code)
      stocks.value = stocks.value.filter(stock => stock.code !== code)
    } catch (err) {
      alert('删除股票失败')
      console.error('删除股票失败:', err)
      await fetchStocks()
    }
  }
}

// 保存股票
const saveStock = async () => {
  if (!formData.value.code || !formData.value.name || !formData.industry) {
    alert('请先查询并选择股票（需包含行业信息）')
    return
  }

  saving.value = true
  try {
    if (editingStock.value) {
      const updatedStock = await apiService.updateStock(
        editingStock.value.code,
        formData.value
      )
      const index = stocks.value.findIndex(stock => stock.code === updatedStock.code)
      if (index > -1) {
        stocks.value[index] = updatedStock
      }
    } else {
      const newStock = await apiService.addStock(formData.value)
      stocks.value.push(newStock)
    }

    closeModal()
  } catch (err) {
    alert(editingStock.value ? '更新股票失败' : '添加股票失败')
    console.error(editingStock.value ? '更新股票失败:' : '添加股票失败:', err)
  } finally {
    saving.value = false
  }
}

// 更新持仓状态
const updateHoldingStatus = async (code, holding) => {
  try {
    await apiService.updateStock(code, { holding })
    const stock = stocks.value.find(s => s.code === code)
    if (stock) {
      stock.holding = holding
    }
  } catch (err) {
    alert('更新持仓状态失败')
    console.error('更新持仓状态失败:', err)
    await fetchStocks()
  }
}

// 关闭弹窗
const closeModal = () => {
  showAddModal.value = false
  editingStock.value = null
  resetForm()
}

// 核心修复1：改用字符串拼接URL，避免模板字符串解析错误
const handleStockSearch = async () => {
  const keyword = modalSearchKeyword.value.trim()
  if (!keyword) {
    searchResults.value = []
    showSearchResults.value = false
    return
  }
  
  searching.value = true
  try {
    // 修复：用字符串拼接替代模板字符串，规避解析异常
    const requestUrl = '/api/stocks/search/' + encodeURIComponent(keyword)
    const response = await axios.get(requestUrl)
    searchResults.value = response.data.stocks || []
    showSearchResults.value = true
  } catch (error) {
    console.error('搜索股票失败:', error)
    searchResults.value = []
    alert('搜索股票失败，请重试')
  } finally {
    searching.value = false
  }
}

// 核心修复2：确保函数语法正确，无括号/引号问题
const fetchStockBaseInfo = async (stockCode) => {
  try {
    const requestUrl = '/api/stocks/baseInfo/' + encodeURIComponent(stockCode)
    const response = await axios.get(requestUrl)
    return response.data
  } catch (err) {
    console.error(`获取股票${stockCode}详情失败:`, err)
    throw new Error('获取股票行业信息失败')
  }
}

// 选择股票后获取详情
const selectSearchResult = async (item) => {
  showSearchResults.value = false
  fetchingDetail.value = true
  try {
    const stockDetail = await fetchStockBaseInfo(item.stockCode)
    formData.value = {
      code: item.stockCode,
      name: item.stockName,
      industry: stockDetail.industry || '未获取到行业信息',
      holding: formData.value.holding
    }
    modalSearchKeyword.value = item.stockName + ' (' + item.stockCode + ')'
  } catch (err) {
    alert(err.message)
    formData.value.code = ''
    formData.value.name = ''
    formData.value.industry = ''
  } finally {
    fetchingDetail.value = false
  }
}

// 处理搜索框聚焦/失焦
const handleSearchFocus = () => {
  if (searchResults.value.length > 0) {
    showSearchResults.value = true
  }
}
const handleSearchBlur = () => {
  setTimeout(() => {
    showSearchResults.value = false
  }, 200)
}

// 重置表单
const resetForm = () => {
  formData.value = {
    code: '',
    name: '',
    industry: '',
    holding: false
  }
  modalSearchKeyword.value = ''
  searchResults.value = []
  showSearchResults.value = false
}
</script>

<style scoped>
.stock-list-container {
  height: 100%;
  overflow-y: auto;
}

/* 网格布局 */
.grid {
  display: grid;
}

.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

/* 头部样式 */
.card-header {
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.card-title {
  font-size: 24px;
  color: var(--text-primary);
}

/* 搜索框 */
.search-box {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
}

.search-box input {
  width: 300px;
  padding: 8px 16px 8px 36px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-base);
  font-size: 14px;
  transition: var(--transition-base);
  background-color: var(--bg-secondary);
}

.search-box input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
  background-color: var(--bg-primary);
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.stat-card {
  text-align: center;
  transition: var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: var(--spacing-xs);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 按钮样式 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--border-radius-base);
  font-size: 14px;
  font-weight: 500;
  transition: var(--transition-base);
  border: 1px solid transparent;
  cursor: pointer;
  outline: none;
  min-width: 80px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn.primary {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  box-shadow: 0 2px 4px rgba(24, 144, 255, 0.2);
}

.btn.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.btn-icon {
  font-size: 16px;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(24, 144, 255, 0.2);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
}

/* 表格样式 */
.table-responsive {
  overflow-x: auto;
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.stock-table th {
  background-color: var(--bg-tertiary);
  font-weight: 600;
  color: var(--text-primary);
  text-align: left;
  padding: 12px 16px;
  border-bottom: 2px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 10;
  white-space: nowrap;
}

.stock-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

.table-row {
  transition: var(--transition-base);
}

.table-row:hover {
  background-color: var(--bg-tertiary);
}

/* 价格和涨跌幅 */
.price {
  font-weight: 600;
  font-size: 15px;
}

.change-rate {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: var(--border-radius-small);
  font-size: 12px;
  font-weight: 500;
}

/* 行业标签 */
.industry-badge {
  display: inline-block;
  padding: 4px 8px;
  background-color: rgba(24, 144, 255, 0.1);
  color: var(--primary-color);
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
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
  transition: var(--transition-fast);
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: var(--transition-fast);
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--primary-color);
}

input:checked + .slider:before {
  transform: translateX(20px);
}

/* 状态容器 */
.status-container {
  display: flex;
  align-items: center;
}

.status-text {
  margin-left: 8px;
}

/* 操作按钮 */
.actions {
  text-align: right;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: var(--border-radius-base);
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-base);
}

.edit-btn:hover {
  background-color: rgba(24, 144, 255, 0.1);
  color: var(--primary-color);
}

.delete-btn:hover {
  background-color: rgba(245, 34, 45, 0.1);
  color: var(--error-color);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* 弹窗样式 */
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
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease;
}

.modal {
  background: var(--bg-primary);
  border-radius: var(--border-radius-large);
  width: 520px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: scaleIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-tertiary);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: var(--transition-base);
}

.close-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  max-height: calc(90vh - 150px);
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

/* 优化后的搜索结果下拉框样式 */
.search-results {
  scrollbar-width: thin;
  scrollbar-color: #d1d5db #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-top: 2px;
  position: absolute;
  z-index: 10;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  max-height: 60vh;
  overflow-y: auto;
}

.search-results::-webkit-scrollbar {
  width: 6px;
}

.search-results::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.search-item {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.15s ease;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
}

.search-item:last-child {
  border-bottom: none;
}

.search-item:hover {
  background-color: rgba(24, 144, 255, 0.05);
}

.search-item .font-medium {
  font-size: 15px;
  color: #111827;
  font-weight: 500;
}

.search-item .text-xs.text-gray-500 {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.search-item .text-xs.px-2.py-1 {
  padding: 3px 8px;
  font-size: 11px;
  border-radius: 12px;
  background-color: rgba(24, 144, 255, 0.1);
  color: #1890ff;
}

.search-loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: translateY(-50%) rotate(0deg); }
  to { transform: translateY(-50%) rotate(360deg); }
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 14px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-base);
  font-size: 14px;
  transition: var(--transition-base);
  background-color: var(--bg-primary);
}

.form-group input:focus,
.form-group select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  gap: 12px;
  background-color: var(--bg-tertiary);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stats-cards {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .stock-table {
    font-size: 12px;
  }
  
  .stock-table th,
  .stock-table td {
    padding: 8px 12px;
  }
  
  .modal {
    width: 95vw;
    margin: 20px;
  }
}

@media (max-width: 480px) {
  .empty-icon {
    font-size: 48px;
  }
  
  .modal-body {
    padding: 16px;
  }
}
</style>