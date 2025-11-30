<template>
  <div class="stock-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载股票数据...</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <p class="error-text">{{ error }}</p>
      <button class="btn primary retry-btn" @click="retryLoad">重试</button>
    </div>
    
    <!-- 正常内容 -->
    <template v-else>
      <!-- 股票核心信息栏（固定顶部） -->
      <div class="stock-header sticky top-0 z-10 bg-white/90 backdrop-blur-sm shadow-sm border-b">
        <div class="container mx-auto px-4 py-3 flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
          <div class="flex items-center gap-3">
            <button class="btn-icon-round" @click="goBack" title="返回">
              ←
            </button>
            <div class="stock-basic">
              <h1 class="stock-title flex items-center gap-2">
                {{ stockInfo.name }}
                <span class="stock-code text-gray-500 text-sm font-normal">{{ stockInfo.code }}</span>
              </h1>
              <div class="stock-industry text-sm text-gray-500">
                行业：{{ stockInfo.industry || '未知行业' }}
              </div>
            </div>
          </div>
          
          <div class="price-group flex items-center gap-4">
            <div class="price-display">
              <div class="current-price text-xl font-bold">
                {{ formatPrice(stockInfo.price) }}
              </div>
              <div 
                :class="['price-change flex items-center gap-1 mt-1 text-sm px-2 py-1 rounded-full', 
                  stockInfo.changeRate > 0 ? 'bg-red-50 text-red-600' : 
                  stockInfo.changeRate < 0 ? 'bg-green-50 text-green-600' : 'bg-gray-50 text-gray-600']"
              >
                <span v-if="stockInfo.changeRate > 0">↗️</span>
                <span v-else-if="stockInfo.changeRate < 0">↘️</span>
                <span v-else>➡️</span>
                {{ stockInfo.changeRate > 0 ? '+' : '' }}{{ stockInfo.changeRate.toFixed(2) }}%
              </div>
            </div>
            
            <!-- 新增笔记按钮 -->
            <button 
              class="btn primary btn-sm flex items-center gap-1"
              @click="openNoteModal('create')"
            >
              <i class="icon">✏️</i>
              新增笔记
            </button>
          </div>
        </div>
      </div>

      <div class="container mx-auto px-4 py-6">
        <!-- 快速指标卡片 -->
        <div class="quick-metrics card mb-6 grid grid-cols-2 md:grid-cols-4 gap-4 p-4">
          <div class="metric-item bg-gray-50 p-3 rounded-lg border">
            <div class="metric-label text-xs text-gray-500 mb-1">总市值</div>
            <div class="metric-value font-semibold">{{ formatNumber(stockInfo.marketCap) }}亿</div>
          </div>
          <div class="metric-item bg-gray-50 p-3 rounded-lg border">
            <div class="metric-label text-xs text-gray-500 mb-1">市盈率(TTM)</div>
            <div class="metric-value font-semibold">{{ currentFinancialData.pe || '--' }}</div>
          </div>
          <div class="metric-item bg-gray-50 p-3 rounded-lg border">
            <div class="metric-label text-xs text-gray-500 mb-1">净资产收益率</div>
            <div class="metric-value font-semibold">{{ currentFinancialData.roe || '--' }}%</div>
          </div>
          <div class="metric-item bg-gray-50 p-3 rounded-lg border">
            <div class="metric-label text-xs text-gray-500 mb-1">上市日期</div>
            <div class="metric-value font-semibold">{{ stockInfo.listDate || '--' }}</div>
          </div>
        </div>

        <!-- 主内容区域：分栏布局 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- 左侧：基础信息 + 股东信息 -->
          <div class="lg:col-span-1 space-y-6">
            <!-- 基本信息卡片 -->
            <div class="card p-5 border rounded-lg shadow-sm">
              <div class="card-header mb-4">
                <h3 class="card-title text-lg font-semibold flex items-center gap-2">
                  <i class="icon text-primary">📋</i> 基本信息
                </h3>
              </div>
              <div class="info-grid space-y-3">
                <div class="info-item flex justify-between">
                  <span class="info-label text-gray-500">公司全称</span>
                  <span class="info-value font-medium">{{ stockInfo.companyName || '--' }}</span>
                </div>
                <div class="info-item flex justify-between">
                  <span class="info-label text-gray-500">所属行业</span>
                  <span class="info-value font-medium">{{ stockInfo.industry || '--' }}</span>
                </div>
                <div class="info-item flex justify-between">
                  <span class="info-label text-gray-500">总股本</span>
                  <span class="info-value font-medium">{{ formatNumber(stockInfo.totalShares) }}亿股</span>
                </div>
                <div class="info-item flex justify-between">
                  <span class="info-label text-gray-500">流通股本</span>
                  <span class="info-value font-medium">{{ formatNumber(stockInfo.floatShares) }}亿股</span>
                </div>
                <div class="info-item flex justify-between">
                  <span class="info-label text-gray-500">总市值</span>
                  <span class="info-value font-medium">{{ formatNumber(stockInfo.marketCap) }}亿元</span>
                </div>
              </div>
            </div>

            <!-- 十大股东卡片 -->
            <div class="card p-5 border rounded-lg shadow-sm">
              <div class="card-header mb-4">
                <h3 class="card-title text-lg font-semibold flex items-center gap-2">
                  <i class="icon text-primary">👥</i> 十大股东
                </h3>
              </div>
              <div v-if="stockInfo.topShareholders && stockInfo.topShareholders.length > 0" class="shareholder-list space-y-3">
                <div 
                  class="shareholder-item p-3 bg-gray-50 rounded-lg border flex items-center gap-3"
                  v-for="(holder, index) in stockInfo.topShareholders" 
                  :key="index"
                >
                  <div class="shareholder-rank w-6 h-6 flex items-center justify-center bg-primary text-white rounded-full text-xs">
                    {{ index + 1 }}
                  </div>
                  <div class="shareholder-details flex-1 min-w-0">
                    <div class="holder-name font-medium truncate">{{ holder.name }}</div>
                    <div class="holder-type text-xs text-gray-500">{{ holder.type || '未知类型' }}</div>
                  </div>
                  <div class="shareholder-percentage text-right">
                    <div class="percent-value font-semibold">{{ holder.percentage }}%</div>
                    <div class="progress-container w-24 h-2 bg-gray-200 rounded-full mt-1">
                      <div 
                        class="progress-bar h-full bg-primary rounded-full" 
                        :style="{ width: holder.percentage + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state py-6 text-center">
                <div class="empty-icon text-4xl mb-2">👥</div>
                <p class="empty-text text-gray-500">暂无股东信息</p>
              </div>
            </div>

            <!-- 关联笔记卡片（核心新增功能） -->
            <div class="card p-5 border rounded-lg shadow-sm">
              <div class="card-header mb-4 flex justify-between items-center">
                <h3 class="card-title text-lg font-semibold flex items-center gap-2">
                  <i class="icon text-primary">📝</i> 关联笔记
                </h3>
                <button 
                  class="btn btn-sm bg-primary/10 text-primary hover:bg-primary/20"
                  @click="openNoteModal('create')"
                >
                  新增
                </button>
              </div>
              
              <!-- 笔记列表 -->
              <div v-if="stockNotes.length > 0" class="notes-list space-y-3 max-h-80 overflow-y-auto pr-1">
                <div 
                  class="note-item p-3 bg-gray-50 rounded-lg border cursor-pointer hover:bg-gray-100 transition-colors"
                  v-for="note in stockNotes" 
                  :key="note.id"
                  @click="openNoteModal('view', note)"
                >
                  <div class="note-title font-medium truncate">{{ note.title }}</div>
                  <div class="note-meta text-xs text-gray-500 mt-1 flex justify-between">
                    <span>创建时间: {{ formatDate(note.createTime) }}</span>
                    <span>更新时间: {{ formatDate(note.updateTime) }}</span>
                  </div>
                  <div class="note-content text-sm text-gray-600 mt-2 line-clamp-2">
                    {{ note.content }}
                  </div>
                </div>
              </div>
              
              <div v-else class="empty-state py-6 text-center">
                <div class="empty-icon text-4xl mb-2">📝</div>
                <p class="empty-text text-gray-500">暂无关联笔记</p>
                <button 
                  class="btn primary btn-sm mt-3"
                  @click="openNoteModal('create')"
                >
                  <i class="icon">✏️</i> 创建第一条笔记
                </button>
              </div>
            </div>
          </div>

          <!-- 右侧：财务数据 + 利润趋势图 -->
          <div class="lg:col-span-2 space-y-6">
            <!-- 利润趋势图卡片（核心新增功能） -->
            <div class="card p-5 border rounded-lg shadow-sm">
              <div class="card-header mb-4">
                <h3 class="card-title text-lg font-semibold flex items-center gap-2">
                  <i class="icon text-primary">📈</i> 利润趋势分析
                </h3>
              </div>
              
              <!-- 图表切换 -->
              <div class="chart-tabs flex gap-2 mb-4">
                <button 
                  class="chart-tab px-3 py-1 text-sm rounded-md"
                  :class="activeChartType === 'profit' ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700'"
                  @click="activeChartType = 'profit'"
                >
                  净利润趋势
                </button>
                <button 
                  class="chart-tab px-3 py-1 text-sm rounded-md"
                  :class="activeChartType === 'revenue' ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700'"
                  @click="activeChartType = 'revenue'"
                >
                  营业收入趋势
                </button>
              </div>
              
              <!-- 图表容器 -->
              <div class="chart-container h-80">
                <!-- 确保canvas元素有唯一ID且存在 -->
                <canvas id="profitTrendChart"></canvas>
              </div>
              
              <!-- 图表说明 -->
              <div class="chart-desc text-sm text-gray-500 mt-3">
                <p>数据来源：公司年度财务报告 | 单位：亿元</p>
              </div>
            </div>

            <!-- 财务数据卡片 -->
            <div class="card p-5 border rounded-lg shadow-sm">
              <div class="card-header mb-4">
                <h3 class="card-title text-lg font-semibold flex items-center gap-2">
                  <i class="icon text-primary">💰</i> 财务核心数据
                </h3>
              </div>
              
              <!-- 财务数据标签页 -->
              <div class="financial-tabs flex border-b border-gray-200 mb-4">
                <button 
                  v-for="year in financialYears" 
                  :key="year"
                  class="tab-btn py-2 px-4 text-sm font-medium"
                  :class="{ 
                    'text-primary border-b-2 border-primary': activeYear === year,
                    'text-gray-500 hover:text-gray-700': activeYear !== year
                  }"
                  @click="activeYear = year"
                >
                  {{ year }}年
                </button>
              </div>
              
              <!-- 财务数据加载状态 -->
              <div v-if="financeLoading" class="finance-loading flex items-center justify-center py-10">
                <div class="loading-spinner small mr-2"></div>
                <span class="text-gray-500">加载财务数据中...</span>
              </div>
              
              <div v-else class="financial-content">
                <!-- 主要财务指标 -->
                <div class="financial-highlights grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div class="highlight-item p-3 bg-gray-50 rounded-lg border">
                    <div class="highlight-label text-xs text-gray-500 mb-1">营业收入</div>
                    <div class="highlight-value font-semibold">{{ formatNumber(currentFinancialData.revenue) }}亿元</div>
                    <div 
                      class="highlight-growth text-xs mt-1"
                      :class="parseFloat(currentFinancialData.revenueGrowth) > 0 ? 'text-red-500' : 
                      parseFloat(currentFinancialData.revenueGrowth) < 0 ? 'text-green-500' : 'text-gray-500'"
                    >
                      {{ parseFloat(currentFinancialData.revenueGrowth) > 0 ? '+' : '' }}{{ currentFinancialData.revenueGrowth || '0.0' }}%
                    </div>
                  </div>
                  <div class="highlight-item p-3 bg-gray-50 rounded-lg border">
                    <div class="highlight-label text-xs text-gray-500 mb-1">净利润</div>
                    <div class="highlight-value font-semibold">{{ formatNumber(currentFinancialData.netProfit) }}亿元</div>
                    <div 
                      class="highlight-growth text-xs mt-1"
                      :class="parseFloat(currentFinancialData.netProfitGrowth) > 0 ? 'text-red-500' : 
                      parseFloat(currentFinancialData.netProfitGrowth) < 0 ? 'text-green-500' : 'text-gray-500'"
                    >
                      {{ parseFloat(currentFinancialData.netProfitGrowth) > 0 ? '+' : '' }}{{ currentFinancialData.netProfitGrowth || '0.0' }}%
                    </div>
                  </div>
                  <div class="highlight-item p-3 bg-gray-50 rounded-lg border">
                    <div class="highlight-label text-xs text-gray-500 mb-1">每股收益</div>
                    <div class="highlight-value font-semibold">{{ currentFinancialData.eps || '0.00' }}元</div>
                  </div>
                  <div class="highlight-item p-3 bg-gray-50 rounded-lg border">
                    <div class="highlight-label text-xs text-gray-500 mb-1">净资产收益率</div>
                    <div class="highlight-value font-semibold">{{ currentFinancialData.roe || '0.0' }}%</div>
                  </div>
                </div>
                
                <!-- 详细财务数据 -->
                <div class="info-grid grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div class="info-item p-3 bg-gray-50 rounded-lg border">
                    <div class="info-label text-xs text-gray-500 mb-1">每股净资产</div>
                    <div class="info-value font-medium">{{ currentFinancialData.navps || '0.00' }}元</div>
                  </div>
                  <div class="info-item p-3 bg-gray-50 rounded-lg border">
                    <div class="info-label text-xs text-gray-500 mb-1">市盈率（TTM）</div>
                    <div class="info-value font-medium">{{ currentFinancialData.pe || '0.0' }}</div>
                  </div>
                  <div class="info-item p-3 bg-gray-50 rounded-lg border">
                    <div class="info-label text-xs text-gray-500 mb-1">市净率</div>
                    <div class="info-value font-medium">{{ currentFinancialData.pb || '0.0' }}</div>
                  </div>
                  <div class="info-item p-3 bg-gray-50 rounded-lg border">
                    <div class="info-label text-xs text-gray-500 mb-1">毛利率</div>
                    <div class="info-value font-medium">{{ currentFinancialData.grossMargin || '0.0' }}%</div>
                  </div>
                  <div class="info-item p-3 bg-gray-50 rounded-lg border">
                    <div class="info-label text-xs text-gray-500 mb-1">净利率</div>
                    <div class="info-value font-medium">{{ currentFinancialData.netMargin || '0.0' }}%</div>
                  </div>
                  <div class="info-item p-3 bg-gray-50 rounded-lg border">
                    <div class="info-label text-xs text-gray-500 mb-1">负债率</div>
                    <div class="info-value font-medium">{{ currentFinancialData.debtRatio || '0.0' }}%</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 财务数据对比卡片（新增） -->
            <div class="card p-5 border rounded-lg shadow-sm">
              <div class="card-header mb-4">
                <h3 class="card-title text-lg font-semibold flex items-center gap-2">
                  <i class="icon text-primary">📊</i> 年度数据对比
                </h3>
              </div>
              <div class="comparison-table overflow-x-auto">
                <table class="w-full min-w-[600px]">
                  <thead>
                    <tr class="bg-gray-50 border-b">
                      <th class="py-3 px-4 text-left text-sm font-semibold text-gray-700">指标名称</th>
                      <th class="py-3 px-4 text-right text-sm font-semibold text-gray-700">2024年</th>
                      <th class="py-3 px-4 text-right text-sm font-semibold text-gray-700">2023年</th>
                      <th class="py-3 px-4 text-right text-sm font-semibold text-gray-700">2022年</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr class="border-b hover:bg-gray-50">
                      <td class="py-3 px-4 text-sm text-gray-700">营业收入（亿元）</td>
                      <td class="py-3 px-4 text-right text-sm">{{ formatNumber(financialData['2024'].revenue) }}</td>
                      <td class="py-3 px-4 text-right text-sm">{{ formatNumber(financialData['2023'].revenue) }}</td>
                      <td class="py-3 px-4 text-right text-sm">{{ formatNumber(financialData['2022'].revenue) }}</td>
                    </tr>
                    <tr class="border-b hover:bg-gray-50">
                      <td class="py-3 px-4 text-sm text-gray-700">净利润（亿元）</td>
                      <td class="py-3 px-4 text-right text-sm">{{ formatNumber(financialData['2024'].netProfit) }}</td>
                      <td class="py-3 px-4 text-right text-sm">{{ formatNumber(financialData['2023'].netProfit) }}</td>
                      <td class="py-3 px-4 text-right text-sm">{{ formatNumber(financialData['2022'].netProfit) }}</td>
                    </tr>
                    <tr class="border-b hover:bg-gray-50">
                      <td class="py-3 px-4 text-sm text-gray-700">每股收益（元）</td>
                      <td class="py-3 px-4 text-right text-sm">{{ financialData['2024'].eps || '0.00' }}</td>
                      <td class="py-3 px-4 text-right text-sm">{{ financialData['2023'].eps || '0.00' }}</td>
                      <td class="py-3 px-4 text-right text-sm">{{ financialData['2022'].eps || '0.00' }}</td>
                    </tr>
                    <tr class="border-b hover:bg-gray-50">
                      <td class="py-3 px-4 text-sm text-gray-700">净资产收益率（%）</td>
                      <td class="py-3 px-4 text-right text-sm">{{ financialData['2024'].roe || '0.0' }}</td>
                      <td class="py-3 px-4 text-right text-sm">{{ financialData['2023'].roe || '0.0' }}</td>
                      <td class="py-3 px-4 text-right text-sm">{{ financialData['2022'].roe || '0.0' }}</td>
                    </tr>
                    <tr class="hover:bg-gray-50">
                      <td class="py-3 px-4 text-sm text-gray-700">毛利率（%）</td>
                      <td class="py-3 px-4 text-right text-sm">{{ financialData['2024'].grossMargin || '0.0' }}</td>
                      <td class="py-3 px-4 text-right text-sm">{{ financialData['2023'].grossMargin || '0.0' }}</td>
                      <td class="py-3 px-4 text-right text-sm">{{ financialData['2022'].grossMargin || '0.0' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 笔记模态框（新增） -->
    <teleport to="body">
      <div v-if="noteModalOpen" class="modal-backdrop fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="modal-container bg-white rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] flex flex-col">
          <div class="modal-header p-4 border-b flex justify-between items-center">
            <h3 class="modal-title text-lg font-semibold">
              {{ noteModalType === 'create' ? '创建股票笔记' : '查看/编辑笔记' }}
            </h3>
            <button class="modal-close text-gray-500 hover:text-gray-700" @click="closeNoteModal">
              ✕
            </button>
          </div>
          <div class="modal-body p-4 flex-1 overflow-y-auto">
            <form @submit.prevent="saveNote">
              <div class="form-group mb-4">
                <label class="form-label block text-sm font-medium text-gray-700 mb-1">笔记标题</label>
                <input
                  v-model="noteForm.title"
                  type="text"
                  class="form-input w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="输入笔记标题（关联股票：{{ stockInfo.code }} {{ stockInfo.name }}）"
                  required
                >
              </div>
              <div class="form-group mb-4">
                <label class="form-label block text-sm font-medium text-gray-700 mb-1">笔记内容</label>
                <textarea
                  v-model="noteForm.content"
                  class="form-textarea w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  rows="8"
                  placeholder="输入笔记内容（可以记录对该股票的分析、操作计划等）"
                  required
                ></textarea>
              </div>
              <div class="form-group mb-4">
                <label class="form-label block text-sm font-medium text-gray-700 mb-1">关联股票</label>
                <div class="form-control bg-gray-50 px-3 py-2 border rounded-md text-gray-700">
                  {{ stockInfo.code }} {{ stockInfo.name }}
                </div>
              </div>
              <div class="form-actions flex justify-end gap-2 mt-6">
                <button type="button" class="btn btn-secondary px-4 py-2 rounded-md" @click="closeNoteModal">
                  取消
                </button>
                <button type="submit" class="btn primary px-4 py-2 rounded-md">
                  {{ noteModalType === 'create' ? '创建笔记' : '保存修改' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '../api/apiService.js'

// 关键修改：确保Chart对象可用（CDN引入方式）
const Chart = window.Chart || null

const route = useRoute()
const router = useRouter()

// 响应式状态
const stockInfo = ref({
  code: '',
  name: '',
  price: '0.00',
  changeRate: 0,
  industry: '',
  companyName: '',
  listDate: '',
  totalShares: '0',
  floatShares: '0',
  marketCap: '0',
  topShareholders: []
})

// 财务数据相关
const activeYear = ref('2024')
const financialYears = ref(['2024', '2023', '2022'])
const financialData = ref({
  '2024': {
    revenue: '0.00',
    revenueGrowth: '0.0',
    netProfit: '0.00',
    netProfitGrowth: '0.0',
    eps: '0.00',
    navps: '0.00',
    roe: '0.0',
    pe: '0.0',
    pb: '0.0',
    grossMargin: '0.0',
    netMargin: '0.0',
    debtRatio: '0.0'
  },
  '2023': {
    revenue: '0.00',
    revenueGrowth: '0.0',
    netProfit: '0.00',
    netProfitGrowth: '0.0',
    eps: '0.00',
    navps: '0.00',
    roe: '0.0',
    pe: '0.0',
    pb: '0.0',
    grossMargin: '0.0',
    netMargin: '0.0',
    debtRatio: '0.0'
  },
  '2022': {
    revenue: '0.00',
    revenueGrowth: '0.0',
    netProfit: '0.00',
    netProfitGrowth: '0.0',
    eps: '0.00',
    navps: '0.00',
    roe: '0.0',
    pe: '0.0',
    pb: '0.0',
    grossMargin: '0.0',
    netMargin: '0.0',
    debtRatio: '0.0'
  }
})

// 图表相关（新增）
const activeChartType = ref('profit') // profit: 净利润趋势, revenue: 营业收入趋势
const chartInstance = ref(null)

// 笔记相关（新增核心功能）
const stockNotes = ref([])
const noteModalOpen = ref(false)
const noteModalType = ref('create') // create: 创建, view: 查看/编辑
const noteForm = ref({
  id: '',
  title: '',
  content: ''
})

// 加载状态
const loading = ref(false)
const financeLoading = ref(false)
const error = ref(null)

// 当前年份的财务数据
const currentFinancialData = computed(() => {
  return financialData.value[activeYear.value] || financialData.value['2024']
})

// 获取股票代码
const stockCode = computed(() => route.params.code)

// 关键修改1：先定义initChart函数，再定义watch
const initChart = () => {
  // 容错处理：如果Chart未加载或canvas不存在，直接返回
  if (!Chart) {
    console.warn('Chart.js未加载完成')
    return
  }
  
  const ctx = document.getElementById('profitTrendChart')
  if (!ctx) {
    console.warn('图表DOM元素不存在')
    return
  }
  
  // 销毁已有图表
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
  
  // 准备图表数据（确保数据是数字类型）
  const labels = [...financialYears.value].reverse() // 倒序显示，最新年份在右边
  const revenueData = labels.map(year => {
    const value = parseFloat(financialData.value[year]?.revenue || '0')
    return isNaN(value) ? 0 : value
  })
  const profitData = labels.map(year => {
    const value = parseFloat(financialData.value[year]?.netProfit || '0')
    return isNaN(value) ? 0 : value
  })
  
  // 图表配置
  const config = {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: activeChartType.value === 'profit' ? '净利润（亿元）' : '营业收入（亿元）',
        data: activeChartType.value === 'profit' ? profitData : revenueData,
        borderColor: '#165DFF',
        backgroundColor: 'rgba(22, 93, 255, 0.1)',
        borderWidth: 2,
        pointBackgroundColor: '#165DFF',
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#333',
          bodyColor: '#666',
          borderColor: '#ddd',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ${context.raw.toFixed(2)} 亿元`
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            callback: function(value) {
              return value + ' 亿'
            }
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  }
  
  // 创建图表
  try {
    chartInstance.value = new Chart(ctx, config)
  } catch (err) {
    console.error('图表初始化失败:', err)
  }
}

// 关键修改2：移除immediate: true，只在图表类型变化时触发
watch(activeChartType, () => {
  // 延迟执行，确保DOM已更新
  setTimeout(initChart, 100)
})

// 监听路由参数变化
watch(stockCode, (newCode) => {
  if (newCode) {
    fetchStockData()
  }
})

// 监听年份变化
watch(activeYear, (newYear) => {
  fetchFinancialData(newYear)
})

// 返回上一页
const goBack = () => {
  router.back()
}

// 获取股票详细信息
const fetchStockData = async () => {
  if (!stockCode.value) {
    error.value = '未找到股票代码'
    loading.value = false
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    // 获取股票基础数据
    const data = await apiService.getStockDetail(stockCode.value)
    stockInfo.value = data || {
      code: stockCode.value,
      name: '未知股票',
      price: '0.00',
      changeRate: 0,
      industry: '未知',
      companyName: '未知公司',
      listDate: '--',
      totalShares: '0',
      floatShares: '0',
      marketCap: '0',
      topShareholders: []
    }
    
    // 初始化获取所有年份财务数据
    await Promise.all(financialYears.value.map(year => fetchFinancialData(year)))
    
    // 获取该股票关联的笔记（核心新增）
    await fetchStockNotes()
    
    // 关键修改3：数据加载完成后，在onMounted中初始化图表，这里不再重复调用
  } catch (err) {
    console.error('获取股票详细信息失败:', err)
    error.value = '加载股票信息失败，请稍后重试'
    
    // 使用默认数据作为fallback
    stockInfo.value = {
      code: stockCode.value,
      name: '未知股票',
      price: '0.00',
      changeRate: 0,
      industry: '未知',
      companyName: '未知公司',
      listDate: '--',
      totalShares: '0',
      floatShares: '0',
      marketCap: '0',
      topShareholders: []
    }
  } finally {
    loading.value = false
  }
}

// 获取财务数据
const fetchFinancialData = async (year) => {
  financeLoading.value = true
  
  try {
    const data = await apiService.getStockFinancial(stockCode.value, year)
    if (data) {
      financialData.value[year] = data
    }
  } catch (err) {
    console.error(`获取${year}年财务数据失败:`, err)
    // 保持默认值
  } finally {
    financeLoading.value = false
  }
}

// 获取股票关联的笔记（核心新增）
const fetchStockNotes = async () => {
  try {
    // 假设apiService有获取股票关联笔记的接口
    const notes = await apiService.getNotesByStockCode(stockCode.value)
    stockNotes.value = notes || []
  } catch (err) {
    console.error('获取股票关联笔记失败:', err)
    stockNotes.value = []
  }
}

// 打开笔记模态框（核心新增）
const openNoteModal = (type, note = null) => {
  noteModalType.value = type
  noteModalOpen.value = true
  
  if (type === 'create') {
    // 重置表单
    noteForm.value = {
      id: '',
      title: `【${stockInfo.value.code} ${stockInfo.value.name}】${new Date().toLocaleDateString()} 笔记`,
      content: ''
    }
  } else if (type === 'view' && note) {
    // 填充笔记数据
    noteForm.value = {
      id: note.id,
      title: note.title,
      content: note.content
    }
  }
}

// 关闭笔记模态框（核心新增）
const closeNoteModal = () => {
  noteModalOpen.value = false
  // 重置表单
  noteForm.value = {
    id: '',
    title: '',
    content: ''
  }
}

// 保存笔记（核心新增）
const saveNote = async () => {
  try {
    const noteData = {
      ...noteForm.value,
      stockCode: stockInfo.value.code, // 关联股票代码
      stockName: stockInfo.value.name  // 关联股票名称
    }
    
    if (noteModalType.value === 'create') {
      // 创建新笔记
      await apiService.createNote(noteData)
    } else {
      // 更新现有笔记
      await apiService.updateNote(noteForm.value.id, noteData)
    }
    
    // 重新获取笔记列表
    await fetchStockNotes()
    
    // 关闭模态框
    closeNoteModal()
    
    // 提示成功（建议使用更友好的toast组件）
    alert(noteModalType.value === 'create' ? '笔记创建成功！' : '笔记更新成功！')
  } catch (err) {
    console.error('保存笔记失败:', err)
    alert('保存笔记失败，请稍后重试！')
  }
}

// 重试加载
const retryLoad = () => {
  loading.value = true
  error.value = null
  fetchStockData()
}

// 格式化价格显示
const formatPrice = (price) => {
  if (typeof price === 'undefined' || price === null) return '--';
  const numPrice = parseFloat(price);
  return isNaN(numPrice) ? '--' : numPrice.toFixed(2);
}

// 格式化数字显示
const formatNumber = (num) => {
  if (typeof num === 'undefined' || num === null) return '--';
  const number = parseFloat(num);
  if (isNaN(number)) return '--';
  return number.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// 格式化日期显示
const formatDate = (dateStr) => {
  if (!dateStr) return '--';
  try {
    const date = new Date(dateStr);
    return date.toLocaleString();
  } catch (err) {
    return dateStr;
  }
}

// 关键修改4：在onMounted中初始化图表（确保DOM和数据都已准备好）
onMounted(() => {
  fetchStockData()
  // 延迟初始化图表，确保DOM已渲染
  setTimeout(() => {
    if (!loading.value && Chart) {
      initChart()
    }
  }, 500)
})

// 组件卸载时销毁图表
onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
})
</script>

<style scoped>
/* 保持原样式不变 */
.stock-detail-container {
  background-color: #f9fafb;
  min-height: 100vh;
  color: #111827;
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 500px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #165dff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
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

.loading-text,
.error-text {
  color: #6b7280;
  font-size: 1rem;
  margin-bottom: 1rem;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 1rem;
  color: #f59e0b;
}

/* 按钮样式 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn.primary {
  background-color: #165dff;
  color: white;
}

.btn.primary:hover {
  background-color: #0f4bdb;
}

.btn.secondary {
  background-color: #f3f4f6;
  color: #374151;
}

.btn.secondary:hover {
  background-color: #e5e7eb;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
}

.btn-icon-round {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f3f4f6;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #374151;
  font-size: 1rem;
}

.btn-icon-round:hover {
  background-color: #e5e7eb;
  color: #165dff;
}

/* 股票头部样式 */
.stock-header {
  border-bottom: 1px solid #e5e7eb;
}

.stock-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.stock-code {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 400;
}

.stock-industry {
  color: #6b7280;
}

.price-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.current-price {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.price-change {
  font-size: 0.875rem;
  font-weight: 500;
}

/* 卡片样式 */
.card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

/* 快速指标样式 */
.quick-metrics {
  display: grid;
  gap: 1rem;
}

.metric-item {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 0.75rem;
  transition: all 0.2s ease;
}

.metric-item:hover {
  background-color: #f3f4f6;
  border-color: #165dff;
}

.metric-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

/* 信息网格样式 */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.info-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
}

/* 财务数据样式 */
.financial-tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  background-color: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent;
}

.tab-btn:hover {
  color: #165dff;
}

.tab-btn.active {
  color: #165dff;
  border-bottom-color: #165dff;
}

.financial-highlights {
  display: grid;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.highlight-item {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 0.75rem;
}

.highlight-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.highlight-value {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.25rem;
}

.highlight-growth {
  font-size: 0.75rem;
  font-weight: 500;
}

/* 股东列表样式 */
.shareholder-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.shareholder-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.shareholder-item:hover {
  background-color: #f3f4f6;
  border-color: #165dff;
}

.shareholder-rank {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #165dff;
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
}

.holder-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.holder-type {
  font-size: 0.75rem;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
  display: inline-block;
}

.percent-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.25rem;
}

.progress-container {
  width: 100%;
  height: 4px;
  background-color: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: #165dff;
  border-radius: 2px;
}

/* 图表样式 */
.chart-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.chart-tab {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chart-container {
  position: relative;
  height: 320px;
  width: 100%;
}

/* 对比表格样式 */
.comparison-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

th {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

td {
  font-size: 0.875rem;
  color: #111827;
}

tr:hover {
  background-color: #f9fafb;
}

/* 笔记相关样式（核心新增） */
.notes-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.note-item {
  padding: 1rem;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.note-item:hover {
  background-color: #f3f4f6;
  border-color: #165dff;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.note-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.note-meta {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.note-content {
  font-size: 0.875rem;
  color: #4b5563;
  margin-top: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 模态框样式（核心新增） */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.2s ease;
}

.modal-close:hover {
  color: #111827;
}

.modal-body {
  padding: 1rem;
  flex: 1;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.25rem;
}

.form-input,
.form-textarea,
.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #165dff;
  box-shadow: 0 0 0 3px rgba(22, 93, 255, 0.1);
}

.form-textarea {
  min-height: 160px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

/* 空状态样式 */
.empty-state {
  padding: 2rem;
  text-align: center;
  background-color: #f9fafb;
  border-radius: 6px;
}

.empty-icon {
  font-size: 3rem;
  color: #d1d5db;
  margin-bottom: 0.75rem;
}

.empty-text {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

/* 响应式样式 */
@media (max-width: 1024px) {
  .detail-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stock-detail-container {
    padding: 0;
  }
  
  .container {
    padding: 0 1rem;
  }
  
  .stock-header {
    padding: 0.75rem 1rem;
  }
  
  .price-group {
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
  }
  
  .financial-highlights {
    grid-template-columns: 1fr 1fr;
  }
  
  .quick-metrics {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .stock-title {
    font-size: 1rem;
  }
  
  .current-price {
    font-size: 1.25rem;
  }
  
  .financial-highlights {
    grid-template-columns: 1fr;
  }
  
  .quick-metrics {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 240px;
  }
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* 工具类 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>