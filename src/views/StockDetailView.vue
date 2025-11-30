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
      <!-- 股票核心信息栏（固定顶部，紧凑布局） -->
      <div class="stock-header sticky top-0 z-10 bg-white/95 backdrop-blur-sm shadow-sm border-b border-gray-200">
        <div class="container mx-auto px-3 py-2 flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
          <div class="flex items-center gap-2">
            <button class="btn-icon-round" @click="goBack" title="返回">
              ←
            </button>
            <div class="stock-basic">
              <h1 class="stock-title flex items-center gap-1.5 text-lg md:text-xl font-semibold">
                {{ stockInfo.name }}
                <span class="stock-code text-gray-500 text-xs md:text-sm font-normal">{{ stockInfo.code }}</span>
              </h1>
              <div class="stock-industry text-xs md:text-sm text-gray-500 mt-0.5">
                行业：{{ stockInfo.industry || '未知行业' }}
              </div>
            </div>
          </div>
          
          <div class="price-group flex items-center gap-3">
            <div class="price-display">
              <div class="current-price text-lg md:text-xl font-bold">
                {{ formatPrice(stockInfo.price) }}
              </div>
              <div 
                :class="['price-change flex items-center gap-1 mt-0.5 text-xs px-1.5 py-0.5 rounded-full', 
                  stockInfo.changeRate > 0 ? 'bg-red-50 text-red-600' : 
                  stockInfo.changeRate < 0 ? 'bg-green-50 text-green-600' : 'bg-gray-50 text-gray-600']"
              >
                <span v-if="stockInfo.changeRate > 0">↗️</span>
                <span v-else-if="stockInfo.changeRate < 0">↘️</span>
                <span v-else>➡️</span>
                {{ stockInfo.changeRate > 0 ? '+' : '' }}{{ stockInfo.changeRate.toFixed(2) }}%
              </div>
            </div>
            
            <!-- 新增笔记按钮（紧凑样式） -->
            <button 
              class="btn primary btn-xs md:btn-sm flex items-center gap-1"
              @click="openNoteModal('create')"
            >
              <i class="icon">✏️</i>
              新增笔记
            </button>
          </div>
        </div>
      </div>

      <div class="container mx-auto px-3 py-4">
        <!-- 快速指标卡片（紧凑网格） -->
        <div class="quick-metrics card mb-3 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5 p-2.5 border border-gray-200 rounded-lg shadow-sm bg-white">
          <div class="metric-item bg-gray-50 p-1.5 rounded-lg border border-gray-200 hover:bg-gray-100 transition-all duration-200">
            <div class="metric-label text-xs text-gray-600 mb-0.5">总市值</div>
            <div class="metric-value font-semibold text-gray-800 text-sm">{{ formatNumber(stockInfo.marketCap) }}亿</div>
          </div>
          <div class="metric-item bg-gray-50 p-1.5 rounded-lg border border-gray-200 hover:bg-gray-100 transition-all duration-200">
            <div class="metric-label text-xs text-gray-600 mb-0.5">市盈率(TTM)</div>
            <div class="metric-value font-semibold text-gray-800 text-sm">{{ currentFinancialData.pe || '--' }}</div>
          </div>
          <div class="metric-item bg-gray-50 p-1.5 rounded-lg border border-gray-200 hover:bg-gray-100 transition-all duration-200">
            <div class="metric-label text-xs text-gray-600 mb-0.5">净资产收益率</div>
            <div class="metric-value font-semibold text-gray-800 text-sm">{{ currentFinancialData.roe || '--' }}%</div>
          </div>
          <div class="metric-item bg-gray-50 p-1.5 rounded-lg border border-gray-200 hover:bg-gray-100 transition-all duration-200">
            <div class="metric-label text-xs text-gray-600 mb-0.5">上市日期</div>
            <div class="metric-value font-semibold text-gray-800 text-sm">{{ stockInfo.listDate || '--' }}</div>
          </div>
        </div>

        <!-- 主内容区域：紧凑分栏布局 -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3">
          <!-- 左侧：占4列，紧凑排列 -->
          <div class="lg:col-span-4 space-y-3">
            <!-- 基本信息卡片 -->
            <div class="card p-2.5 border border-gray-200 rounded-lg shadow-sm bg-white">
              <div class="card-header mb-1.5">
                <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                  <i class="icon text-primary">📋</i> 基本信息
                </h3>
              </div>
              <div class="info-grid space-y-1.5">
                <div class="info-item flex justify-between">
                  <span class="info-label text-xs text-gray-600">公司全称</span>
                  <span class="info-value text-xs font-medium text-gray-800 truncate">{{ stockInfo.companyName || '--' }}</span>
                </div>
                <div class="info-item flex justify-between">
                  <span class="info-label text-xs text-gray-600">所属行业</span>
                  <span class="info-value text-xs font-medium text-gray-800">{{ stockInfo.industry || '--' }}</span>
                </div>
                <div class="info-item flex justify-between">
                  <span class="info-label text-xs text-gray-600">总股本</span>
                  <span class="info-value text-xs font-medium text-gray-800">{{ formatNumber(stockInfo.totalShares) }}亿股</span>
                </div>
                <div class="info-item flex justify-between">
                  <span class="info-label text-xs text-gray-600">流通股本</span>
                  <span class="info-value text-xs font-medium text-gray-800">{{ formatNumber(stockInfo.floatShares) }}亿股</span>
                </div>
                <div class="info-item flex justify-between">
                  <span class="info-label text-xs text-gray-600">总市值</span>
                  <span class="info-value text-xs font-medium text-gray-800">{{ formatNumber(stockInfo.marketCap) }}亿元</span>
                </div>
              </div>
            </div>

            <!-- 关联笔记卡片 -->
            <div class="card p-2.5 border border-gray-200 rounded-lg shadow-sm bg-white">
              <div class="card-header mb-1.5 flex justify-between items-center">
                <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                  <i class="icon text-primary">📝</i> 关联笔记
                </h3>
                <button 
                  class="btn btn-xs bg-primary/10 text-primary hover:bg-primary/20"
                  @click="openNoteModal('create')"
                >
                  新增
                </button>
              </div>
              
              <!-- 笔记列表（紧凑间距） -->
              <div v-if="stockNotes.length > 0" class="notes-list space-y-1.5 max-h-64 overflow-y-auto pr-1">
                <div 
                  class="note-item p-2 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                  v-for="note in stockNotes" 
                  :key="note.id"
                  @click="openNoteModal('view', note)"
                >
                  <div class="note-title font-medium text-sm truncate">{{ note.title }}</div>
                  <div class="note-meta text-xs text-gray-500 mt-0.5 flex justify-between">
                    <span>{{ formatDate(note.createTime) }}</span>
                    <span>{{ formatDate(note.updateTime) }}</span>
                  </div>
                  <div class="note-content text-xs text-gray-600 mt-1 line-clamp-2">
                    {{ note.content }}
                  </div>
                </div>
              </div>
              
              <div v-else class="empty-state py-3 text-center">
                <div class="empty-icon text-2xl mb-1">📝</div>
                <p class="empty-text text-xs text-gray-500">暂无关联笔记</p>
                <button 
                  class="btn primary btn-xs mt-2"
                  @click="openNoteModal('create')"
                >
                  <i class="icon">✏️</i> 创建第一条
                </button>
              </div>
            </div>

            <!-- 估值逻辑记录卡片 -->
            <div class="card p-2.5 border border-gray-200 rounded-lg shadow-sm bg-white">
              <div class="card-header mb-1.5">
                <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                  <i class="icon text-primary">💡</i> 估值逻辑
                </h3>
              </div>
              <div class="valuation-container">
                <textarea
                  v-model="valuationLogic"
                  class="form-textarea w-full px-2 py-1.5 border border-gray-200 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent mb-2 text-sm"
                  rows="3"
                  placeholder="记录估值逻辑（行业中枢、增长预期等）"
                ></textarea>
                <button 
                  class="btn primary btn-xs w-full py-1.5"
                  @click="saveValuationLogic"
                >
                  保存估值逻辑
                </button>
              </div>
            </div>

            <!-- 买卖点与盈亏预期卡片 -->
            <div class="card p-2.5 border border-gray-200 rounded-lg shadow-sm bg-white">
              <div class="card-header mb-1.5">
                <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                  <i class="icon text-primary">📊</i> 买卖点与盈亏预期
                </h3>
              </div>
              <div class="trading-form grid grid-cols-1 gap-1.5 mb-2">
                <div class="form-group">
                  <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">目标买入点（元）</label>
                  <input
                    v-model="buyPoint"
                    type="number"
                    step="0.01"
                    class="form-input w-full px-2 py-1.5 border border-gray-200 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                    placeholder="输入买入价"
                  >
                </div>
                <div class="grid grid-cols-2 gap-1.5">
                  <div class="form-group">
                    <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">最大亏损点位（元）</label>
                    <input
                      v-model="maxLossPoint"
                      type="number"
                      step="0.01"
                      class="form-input w-full px-2 py-1.5 border border-gray-200 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                      placeholder="止损价"
                    >
                  </div>
                  <div class="form-group">
                    <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">最大亏损跌幅（%）</label>
                    <input
                      v-model="maxLossRate"
                      type="number"
                      step="0.1"
                      class="form-input w-full px-2 py-1.5 border border-gray-200 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                      placeholder="可接受跌幅"
                    >
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-1.5">
                  <div class="form-group">
                    <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">预期涨幅（%）</label>
                    <input
                      v-model="expectedGrowthRate"
                      type="number"
                      step="0.1"
                      class="form-input w-full px-2 py-1.5 border border-gray-200 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                      placeholder="预期涨幅"
                    >
                  </div>
                  <div class="form-group">
                    <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">预期目标点位（元）</label>
                    <input
                      v-model="expectedPoint"
                      type="number"
                      step="0.01"
                      class="form-input w-full px-2 py-1.5 border border-gray-200 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                      placeholder="目标卖出价"
                    >
                  </div>
                </div>
              </div>
              <button 
                class="btn primary btn-xs w-full py-1.5"
                @click="saveTradingPlan"
              >
                保存交易计划
              </button>
            </div>

            <!-- 竞争对手卡片 -->
            <div class="card p-2.5 border border-gray-200 rounded-lg shadow-sm bg-white">
              <div class="card-header mb-1.5">
                <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                  <i class="icon text-primary">🤝</i> 竞争对手
                </h3>
              </div>
              <div v-if="competitors.length > 0" class="competitor-list space-y-1.5">
                <div 
                  class="competitor-item p-2 bg-gray-50 rounded-lg border border-gray-200 flex items-center justify-between cursor-pointer hover:bg-gray-100 transition-colors"
                  v-for="(competitor, index) in competitors" 
                  :key="index"
                  @click="goToCompetitorDetail(competitor.code)"
                >
                  <div class="competitor-info flex items-center gap-1.5">
                    <div class="competitor-rank w-5 h-5 flex items-center justify-center bg-primary/10 text-primary rounded-full text-xs">
                      {{ index + 1 }}
                    </div>
                    <div class="competitor-details min-w-0">
                      <div class="competitor-name font-medium text-sm truncate">{{ competitor.name }}</div>
                      <div class="competitor-code text-xs text-gray-500">{{ competitor.code }}</div>
                    </div>
                  </div>
                  <div class="competitor-action text-primary text-xs">
                    查看详情 →
                  </div>
                </div>
              </div>
              <div v-else class="empty-state py-3 text-center">
                <div class="empty-icon text-2xl mb-1">🤝</div>
                <p class="empty-text text-xs text-gray-500">暂无竞争对手数据</p>
              </div>
            </div>
          </div>

          <!-- 右侧：占8列，紧凑布局 -->
          <div class="lg:col-span-8 space-y-3">
            <!-- 财务趋势图表组 -->
            <div class="card p-2.5 border border-gray-200 rounded-lg shadow-sm bg-white">
              <div class="card-header mb-1.5">
                <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                  <i class="icon text-primary">📈</i> 财务趋势分析（{{ financialYears.length }}年）
                </h3>
              </div>
              
              <!-- 图表容器：上下紧凑布局 -->
              <div class="chart-group space-y-2.5">
                <!-- 扣非净利润趋势图 -->
                <div>
                  <h4 class="chart-subtitle text-sm font-medium mb-1">扣非净利润趋势（单位：亿元）</h4>
                  <div class="chart-container h-56">
                    <canvas id="nonProfitTrendChart"></canvas>
                  </div>
                </div>
                
                <!-- 应收账款趋势图 -->
                <div>
                  <h4 class="chart-subtitle text-sm font-medium mb-1">应收账款趋势（单位：亿元）</h4>
                  <div class="chart-container h-56">
                    <canvas id="receivablesTrendChart"></canvas>
                  </div>
                </div>
              </div>
              
              <!-- 图表说明 -->
              <div class="chart-desc text-xs text-gray-500 mt-2">
                <p>数据来源：公司年度财务报告 | 自动适配{{ financialYears.length }}年数据</p>
              </div>
            </div>

            <!-- 财务核心数据对比 -->
            <div class="card p-2.5 border border-gray-200 rounded-lg shadow-sm bg-white">
              <div class="card-header mb-1.5">
                <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                  <i class="icon text-primary">💰</i> 财务核心数据对比
                </h3>
              </div>
              
              <div class="comparison-table overflow-x-auto">
                <table class="w-full min-w-[500px] text-sm">
                  <thead>
                    <tr class="bg-gray-50 border-b border-gray-200">
                      <th class="py-2 px-3 text-left text-xs font-semibold text-gray-600">指标名称</th>
                      <th v-for="year in financialYears" :key="year" class="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                        {{ year }}年
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                      <td class="py-2 px-3 text-xs text-gray-700">营业收入（亿元）</td>
                      <td v-for="year in financialYears" :key="year" class="py-2 px-3 text-right text-xs">
                        {{ formatNumber(financialData[year].revenue) }}
                      </td>
                    </tr>
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                      <td class="py-2 px-3 text-xs text-gray-700">净利润（亿元）</td>
                      <td v-for="year in financialYears" :key="year" class="py-2 px-3 text-right text-xs">
                        {{ formatNumber(financialData[year].netProfit) }}
                      </td>
                    </tr>
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                      <td class="py-2 px-3 text-xs text-gray-700">扣非净利润（亿元）</td>
                      <td v-for="year in financialYears" :key="year" class="py-2 px-3 text-right text-xs">
                        {{ formatNumber(financialData[year].nonNetProfit) }}
                      </td>
                    </tr>
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                      <td class="py-2 px-3 text-xs text-gray-700">应收账款（亿元）</td>
                      <td v-for="year in financialYears" :key="year" class="py-2 px-3 text-right text-xs">
                        {{ formatNumber(financialData[year].receivables) }}
                      </td>
                    </tr>
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                      <td class="py-2 px-3 text-xs text-gray-700">每股收益（元）</td>
                      <td v-for="year in financialYears" :key="year" class="py-2 px-3 text-right text-xs">
                        {{ financialData[year].eps || '0.00' }}
                      </td>
                    </tr>
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                      <td class="py-2 px-3 text-xs text-gray-700">净资产收益率（%）</td>
                      <td v-for="year in financialYears" :key="year" class="py-2 px-3 text-right text-xs">
                        {{ financialData[year].roe || '0.0' }}
                      </td>
                    </tr>
                    <tr class="hover:bg-gray-50">
                      <td class="py-2 px-3 text-xs text-gray-700">毛利率（%）</td>
                      <td v-for="year in financialYears" :key="year" class="py-2 px-3 text-right text-xs">
                        {{ financialData[year].grossMargin || '0.0' }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 详细财务指标卡片（紧凑网格） -->
            <div class="card p-2.5 border border-gray-200 rounded-lg shadow-sm bg-white">
              <div class="card-header mb-1.5">
                <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                  <i class="icon text-primary">📋</i> 最新年度详细财务指标
                </h3>
              </div>
              
              <div class="info-grid grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5">
                <div class="info-item p-1.5 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="info-label text-xs text-gray-600 mb-0.5">每股净资产</div>
                  <div class="info-value font-medium text-sm">{{ currentFinancialData.navps || '0.00' }}元</div>
                </div>
                <div class="info-item p-1.5 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="info-label text-xs text-gray-600 mb-0.5">市盈率（TTM）</div>
                  <div class="info-value font-medium text-sm">{{ currentFinancialData.pe || '0.0' }}</div>
                </div>
                <div class="info-item p-1.5 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="info-label text-xs text-gray-600 mb-0.5">市净率</div>
                  <div class="info-value font-medium text-sm">{{ currentFinancialData.pb || '0.0' }}</div>
                </div>
                <div class="info-item p-1.5 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="info-label text-xs text-gray-600 mb-0.5">毛利率</div>
                  <div class="info-value font-medium text-sm">{{ currentFinancialData.grossMargin || '0.0' }}%</div>
                </div>
                <div class="info-item p-1.5 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="info-label text-xs text-gray-600 mb-0.5">净利率</div>
                  <div class="info-value font-medium text-sm">{{ currentFinancialData.netMargin || '0.0' }}%</div>
                </div>
                <div class="info-item p-1.5 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="info-label text-xs text-gray-600 mb-0.5">负债率</div>
                  <div class="info-value font-medium text-sm">{{ currentFinancialData.debtRatio || '0.0' }}%</div>
                </div>
                <div class="info-item p-1.5 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="info-label text-xs text-gray-600 mb-0.5">营收增长率</div>
                  <div class="info-value font-medium text-sm">{{ currentFinancialData.revenueGrowth || '0.0' }}%</div>
                </div>
                <div class="info-item p-1.5 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="info-label text-xs text-gray-600 mb-0.5">净利润增长率</div>
                  <div class="info-value font-medium text-sm">{{ currentFinancialData.netProfitGrowth || '0.0' }}%</div>
                </div>
                <div class="info-item p-1.5 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="info-label text-xs text-gray-600 mb-0.5">扣非净利润增长率</div>
                  <div class="info-value font-medium text-sm">{{ currentFinancialData.nonNetProfitGrowth || '0.0' }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 笔记模态框（紧凑样式） -->
    <teleport to="body">
      <div v-if="noteModalOpen" class="modal-backdrop fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-3">
        <div class="modal-container bg-white rounded-lg shadow-lg w-full max-w-md max-h-[85vh] flex flex-col">
          <div class="modal-header p-2.5 border-b border-gray-200 flex justify-between items-center">
            <h3 class="modal-title text-base font-semibold">
              {{ noteModalType === 'create' ? '创建股票笔记' : '查看/编辑笔记' }}
            </h3>
            <button class="modal-close text-gray-500 hover:text-gray-700" @click="closeNoteModal">
              ✕
            </button>
          </div>
          <div class="modal-body p-2.5 flex-1 overflow-y-auto">
            <form @submit.prevent="saveNote">
              <div class="form-group mb-2.5">
                <label class="form-label block text-sm font-medium text-gray-700 mb-0.5">笔记标题</label>
                <input
                  v-model="noteForm.title"
                  type="text"
                  class="form-input w-full px-2.5 py-1.5 border border-gray-200 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                  placeholder="输入笔记标题（关联股票：{{ stockInfo.code }} {{ stockInfo.name }}）"
                  required
                >
              </div>
              <div class="form-group mb-2.5">
                <label class="form-label block text-sm font-medium text-gray-700 mb-0.5">笔记内容</label>
                <textarea
                  v-model="noteForm.content"
                  class="form-textarea w-full px-2.5 py-1.5 border border-gray-200 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                  rows="6"
                  placeholder="输入笔记内容（分析、操作计划等）"
                  required
                ></textarea>
              </div>
              <div class="form-group mb-2.5">
                <label class="form-label block text-sm font-medium text-gray-700 mb-0.5">关联股票</label>
                <div class="form-control bg-gray-50 px-2.5 py-1.5 border border-gray-200 rounded-md text-gray-700 text-sm">
                  {{ stockInfo.code }} {{ stockInfo.name }}
                </div>
              </div>
              <div class="form-actions flex justify-end gap-1.5 mt-3">
                <button type="button" class="btn btn-secondary btn-xs px-3 py-1.5 rounded-md" @click="closeNoteModal">
                  取消
                </button>
                <button type="submit" class="btn primary btn-xs px-3 py-1.5 rounded-md">
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

// 响应式状态（新增估值、买卖点、竞争对手字段）
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
  topShareholders: [],
  competitors: [] // 新增：竞争对手列表（{code: string, name: string}）
})

// 财务数据相关（新增扣非净利润、应收账款字段，自适应年份）
const financialData = ref({})
const financialYears = ref([]) // 动态存储可用年份（3-5年）
const currentFinancialData = computed(() => {
  // 默认取最新年份数据
  if (financialYears.value.length === 0) return {}
  const latestYear = financialYears.value[0]
  return financialData.value[latestYear] || {}
})

// 新增：估值与交易计划相关状态
const valuationLogic = ref('') // 估值逻辑
const buyPoint = ref('') // 买入点
const maxLossPoint = ref('') // 最大亏损点位
const maxLossRate = ref('') // 最大亏损跌幅
const expectedGrowthRate = ref('') // 预期涨幅
const expectedPoint = ref('') // 预期点位
const competitors = ref([]) // 竞争对手

// 图表实例（新增扣非净利润、应收账款图表）
const nonProfitChartInstance = ref(null)
const receivablesChartInstance = ref(null)

// 笔记相关
const stockNotes = ref([])
const noteModalOpen = ref(false)
const noteModalType = ref('create')
const noteForm = ref({
  id: '',
  title: '',
  content: ''
})

// 加载状态
const loading = ref(false)
const error = ref(null)

// 获取股票代码
const stockCode = computed(() => route.params.code)

// 初始化财务趋势图表（自适应3-5年数据）
const initFinancialCharts = () => {
  if (!Chart || financialYears.value.length === 0) return
  
  // 准备基础数据
  const labels = [...financialYears.value].reverse() // 最新年份在右侧
  const nonProfitData = labels.map(year => {
    const value = parseFloat(financialData.value[year]?.nonNetProfit || '0')
    return isNaN(value) ? 0 : value
  })
  const receivablesData = labels.map(year => {
    const value = parseFloat(financialData.value[year]?.receivables || '0')
    return isNaN(value) ? 0 : value
  })

  // 扣非净利润图表
  const nonProfitCtx = document.getElementById('nonProfitTrendChart')
  if (nonProfitCtx) {
    if (nonProfitChartInstance.value) nonProfitChartInstance.value.destroy()
    nonProfitChartInstance.value = new Chart(nonProfitCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: '扣非净利润（亿元）',
          data: nonProfitData,
          borderColor: '#165DFF',
          backgroundColor: 'rgba(22, 93, 255, 0.1)',
          borderWidth: 1.5,
          pointBackgroundColor: '#165DFF',
          pointRadius: 3,
          pointHoverRadius: 4,
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            padding: 8,
            callbacks: {
              label: (context) => `${context.dataset.label}: ${context.raw.toFixed(2)} 亿元`
            }
          }
        },
        scales: {
          x: { 
            grid: { display: false },
            ticks: { font: { size: 10 } }
          },
          y: { 
            beginAtZero: true,
            grid: { color: 'rgba(0, 0, 0, 0.03)' },
            ticks: { 
              font: { size: 10 },
              callback: (value) => `${value} 亿` 
            }
          }
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false
        },
        animation: {
          duration: 800,
          easing: 'easeOutQuart'
        }
      }
    })
  }

  // 应收账款图表
  const receivablesCtx = document.getElementById('receivablesTrendChart')
  if (receivablesCtx) {
    if (receivablesChartInstance.value) receivablesChartInstance.value.destroy()
    receivablesChartInstance.value = new Chart(receivablesCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: '应收账款（亿元）',
          data: receivablesData,
          borderColor: '#FF7D00',
          backgroundColor: 'rgba(255, 125, 0, 0.1)',
          borderWidth: 1.5,
          pointBackgroundColor: '#FF7D00',
          pointRadius: 3,
          pointHoverRadius: 4,
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            padding: 8,
            callbacks: {
              label: (context) => `${context.dataset.label}: ${context.raw.toFixed(2)} 亿元`
            }
          }
        },
        scales: {
          x: { 
            grid: { display: false },
            ticks: { font: { size: 10 } }
          },
          y: { 
            beginAtZero: true,
            grid: { color: 'rgba(0, 0, 0, 0.03)' },
            ticks: { 
              font: { size: 10 },
              callback: (value) => `${value} 亿` 
            }
          }
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false
        },
        animation: {
          duration: 800,
          easing: 'easeOutQuart'
        }
      }
    })
  }
}

// 监听股票代码变化
watch(stockCode, (newCode) => {
  if (newCode) fetchStockData()
})

// 返回上一页
const goBack = () => router.back()

// 跳转到竞争对手详情页
const goToCompetitorDetail = (code) => {
  router.push(`/stock/${code}/detail`)
}

// 获取股票所有数据（单接口）
const fetchStockData = async () => {
  if (!stockCode.value) {
    error.value = '未找到股票代码'
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    // 单接口获取所有数据
    const data = await apiService.getStockDetail(stockCode.value)
    if (!data) throw new Error('数据返回为空')

    // 基础信息赋值
    stockInfo.value = {
      code: data.baseInfo.stockCode || stockCode.value,
      name: data.baseInfo.stockName || '未知股票',
      price: data.coreQuotes.currentPrice || '0.00',
      changeRate: data.coreQuotes.changeRate || 0,
      industry: data.baseInfo.industry || '未知行业',
      companyName: data.baseInfo.companyName || '未知公司',
      listDate: data.baseInfo.listDate || '--',
      totalShares: data.baseInfo.totalShares || '0',
      floatShares: data.baseInfo.floatShares || '0',
      marketCap: data.baseInfo.marketCap || '0',
      topShareholders: data.topShareholders || [],
      competitors: data.competitors || [] // 竞争对手数据
    }

    // 财务数据处理（自适应3-5年）
    const financeData = data.financialData || {}
    financialData.value = financeData
    // 提取年份并按降序排序（最新年份在前）
    financialYears.value = Object.keys(financeData).sort((a, b) => b - a)

    // 估值与交易计划数据（从接口获取已保存的数据）
    valuationLogic.value = data.valuationLogic || ''
    buyPoint.value = data.tradingPlan?.buyPoint || ''
    maxLossPoint.value = data.tradingPlan?.maxLossPoint || ''
    maxLossRate.value = data.tradingPlan?.maxLossRate || ''
    expectedGrowthRate.value = data.tradingPlan?.expectedGrowthRate || ''
    expectedPoint.value = data.tradingPlan?.expectedPoint || ''

    // 竞争对手数据
    competitors.value = data.competitors || []

    // 获取关联笔记
    await fetchStockNotes()

  } catch (err) {
    console.error('获取股票数据失败:', err)
    error.value = '加载股票信息失败，请稍后重试'
  } finally {
    loading.value = false
    // 初始化图表（数据加载完成后）
    setTimeout(initFinancialCharts, 300)
  }
}

// 获取关联笔记
const fetchStockNotes = async () => {
  try {
    const notes = await apiService.getNotesByStockCode(stockCode.value)
    stockNotes.value = notes || []
  } catch (err) {
    console.error('获取笔记失败:', err)
    stockNotes.value = []
  }
}

// 保存估值逻辑
const saveValuationLogic = async () => {
  try {
    await apiService.saveStockValuation({
      stockCode: stockCode.value,
      valuationLogic: valuationLogic.value
    })
    alert('估值逻辑保存成功！')
  } catch (err) {
    console.error('保存估值逻辑失败:', err)
    alert('保存失败，请稍后重试')
  }
}

// 保存交易计划
const saveTradingPlan = async () => {
  try {
    const tradingPlan = {
      buyPoint: buyPoint.value,
      maxLossPoint: maxLossPoint.value,
      maxLossRate: maxLossRate.value,
      expectedGrowthRate: expectedGrowthRate.value,
      expectedPoint: expectedPoint.value
    }
    await apiService.saveStockTradingPlan({
      stockCode: stockCode.value,
      tradingPlan
    })
    alert('交易计划保存成功！')
  } catch (err) {
    console.error('保存交易计划失败:', err)
    alert('保存失败，请稍后重试')
  }
}

// 笔记模态框操作
const openNoteModal = (type, note = null) => {
  noteModalType.value = type
  noteModalOpen.value = true
  if (type === 'create') {
    noteForm.value = {
      id: '',
      title: `【${stockInfo.value.code} ${stockInfo.value.name}】${new Date().toLocaleDateString()} 笔记`,
      content: ''
    }
  } else if (note) {
    noteForm.value = { ...note }
  }
}

const closeNoteModal = () => {
  noteModalOpen.value = false
  noteForm.value = { id: '', title: '', content: '' }
}

const saveNote = async () => {
  try {
    const noteData = {
      ...noteForm.value,
      stockCode: stockInfo.value.code,
      stockName: stockInfo.value.name
    }
    noteModalType.value === 'create' 
      ? await apiService.createNote(noteData)
      : await apiService.updateNote(noteForm.value.id, noteData)
    await fetchStockNotes()
    closeNoteModal()
    alert('笔记保存成功！')
  } catch (err) {
    console.error('保存笔记失败:', err)
    alert('保存失败，请稍后重试')
  }
}

// 重试加载
const retryLoad = () => {
  loading.value = true
  fetchStockData()
}

// 格式化工具函数
const formatPrice = (price) => {
  const num = parseFloat(price)
  return isNaN(num) ? '--' : num.toFixed(2)
}

const formatNumber = (num) => {
  const number = parseFloat(num)
  if (isNaN(number)) return '--'
  return number.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString()
  } catch (err) {
    return dateStr
  }
}

// 组件挂载时加载数据
onMounted(() => {
  if (stockCode.value) fetchStockData()
})

// 组件卸载时销毁图表
onUnmounted(() => {
  if (nonProfitChartInstance.value) nonProfitChartInstance.value.destroy()
  if (receivablesChartInstance.value) receivablesChartInstance.value.destroy()
})
</script>

<style scoped>
/* 基础样式：紧凑布局核心配置 */
.stock-detail-container {
  background-color: #f8f9fa;
  min-height: 100vh;
  color: #111827;
  font-size: 14px;
}

/* 加载和错误状态（紧凑样式） */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  text-align: center;
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #165dff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.75rem;
}

.loading-spinner.small {
  width: 16px;
  height: 16px;
  border-width: 1.5px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text,
.error-text {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.error-icon {
  font-size: 36px;
  margin-bottom: 0.75rem;
  color: #f59e0b;
}

/* 按钮样式（现代化） */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  gap: 0.5rem;
}

.btn.primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.btn.primary:hover {
  background-color: var(--primary-dark);
  border-color: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.btn.secondary {
  background-color: var(--bg-card);
  color: var(--text-primary);
  border-color: var(--gray-300);
}

.btn.secondary:hover {
  background-color: var(--bg-secondary);
  border-color: var(--gray-400);
}

.btn-xs {
  padding: 0.25rem 0.5rem;
  font-size: 0.7rem;
}

.btn-sm {
  padding: 0.3rem 0.6rem;
  font-size: 0.75rem;
}

.btn-icon-round {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f3f4f6;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #374151;
  font-size: 0.875rem;
}

.btn-icon-round:hover {
  background-color: #e5e7eb;
  color: #165dff;
}

/* 股票头部样式（现代化） */
.stock-header {
  background-color: var(--bg-card);
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--gray-200);
  box-shadow: var(--shadow-sm);
}

.stock-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.stock-code {
  font-size: 0.875rem;
  color: var(--text-tertiary);
  font-weight: 500;
  margin-left: 0.5rem;
}

.stock-industry {
  font-size: 0.875rem;
  color: var(--text-tertiary);
  background-color: var(--gray-100);
  padding: 0.125rem 0.5rem;
  border-radius: var(--border-radius-sm);
  margin-top: 0.25rem;
  display: inline-block;
}

.price-group {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.current-price {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.price-change {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.125rem 0.5rem;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* 卡片样式（现代化精致） */
.card {
  background-color: var(--bg-card);
  border: 1px solid var(--gray-200);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  transition: all 0.2s ease;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--gray-200);
  margin-bottom: 0;
}

.card-body {
  padding: 1rem;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

/* 快速指标样式（现代化网格） */
.quick-metrics {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(2, 1fr);
  margin-bottom: 1.5rem;
}

@media (min-width: 640px) {
  .quick-metrics {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 768px) {
  .quick-metrics {
    grid-template-columns: repeat(4, 1fr);
  }
}

.metric-item {
  background-color: var(--bg-card);
  border: 1px solid var(--gray-200);
  border-radius: var(--border-radius);
  padding: 1.25rem;
  transition: all 0.2s ease;
  box-shadow: var(--shadow);
}

.metric-item:hover {
  background-color: var(--bg-card);
  border-color: var(--gray-300);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.metric-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  font-weight: 500;
  text-transform: none;
  letter-spacing: normal;
}

.metric-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

/* 信息网格样式（现代化） */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--gray-100);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.info-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* 表格样式（紧凑） */
.comparison-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.5rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

th {
  font-size: 0.7rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

td {
  font-size: 0.75rem;
  color: #111827;
}

tr:hover {
  background-color: #f9fafb;
}

/* 笔记相关样式（紧凑） */
.notes-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 256px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.note-item {
  padding: 0.75rem;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.note-item:hover {
  background-color: #f3f4f6;
  border-color: #d1d5db;
  transform: translateY(-1px);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}

.note-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.note-meta {
  font-size: 0.7rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.note-content {
  font-size: 0.75rem;
  color: #4b5563;
  margin-top: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 模态框样式（紧凑） */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 0.75rem;
}

.modal-container {
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 480px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1rem;
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

/* 表单样式（紧凑） */
.form-group {
  margin-bottom: 0.75rem;
}

.form-label {
  display: block;
  font-size: 0.75rem;
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
  border-radius: 4px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #165dff;
  box-shadow: 0 0 0 2px rgba(22, 93, 255, 0.1);
}

.form-textarea {
  min-height: 120px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
}

/* 空状态样式（紧凑） */
.empty-state {
  padding: 1rem;
  text-align: center;
  background-color: #f9fafb;
  border-radius: 4px;
}

.empty-icon {
  font-size: 1.5rem;
  color: #d1d5db;
  margin-bottom: 0.5rem;
}

.empty-text {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
}

/* 竞争对手样式（现代化） */
.competitor-list {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.competitor-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background-color: var(--bg-card);
  border: 1px solid var(--gray-200);
  border-radius: var(--border-radius);
  transition: all 0.2s ease;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
}

.competitor-item:hover {
  background-color: var(--bg-secondary);
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.competitor-rank {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-light);
  color: var(--primary-color);
  border-radius: 50%;
  font-size: 0.875rem;
  font-weight: 700;
  margin-right: 0.75rem;
}

.competitor-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.competitor-code {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  margin-left: 0.5rem;
}

.competitor-action {
  font-size: 0.875rem;
  color: var(--primary-color);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* 图表样式（现代化） */
.chart-group {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chart-subtitle {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chart-subtitle::before {
  content: '';
  width: 3px;
  height: 1.25rem;
  background-color: var(--primary-color);
  border-radius: 1.5px;
}

.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
  background-color: var(--bg-card);
  border-radius: var(--border-radius);
  border: 1px solid var(--gray-200);
  padding: 1rem;
  box-shadow: var(--shadow);
}

.chart-desc {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  margin-top: 0.75rem;
  padding: 0.75rem;
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  border-left: 3px solid var(--gray-300);
}

/* 响应式调整（现代化适配） */
@media (max-width: 1024px) {
  .lg:col-span-4, .lg:col-span-8 {
    grid-column: span 12 !important;
  }
  
  .chart-container {
    height: 250px;
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
    padding: 1rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .price-group {
    align-items: flex-start;
    width: 100%;
  }
  
  /* 修复错误：用原生CSS替换grid-cols-1 */
  .trading-form .grid {
    grid-template-columns: 1fr !important;
  }
  
  .quick-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 220px !important;
    padding: 0.75rem;
  }
  
  .competitor-item {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .competitor-rank {
    margin-right: 0.5rem;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 0.75rem;
  }
  
  .stock-title {
    font-size: 0.9375rem;
  }
  
  .current-price {
    font-size: 1rem;
  }
  
  .quick-metrics {
    grid-template-columns: 1fr;
  }
  
  .metric-item {
    padding: 1rem;
  }
  
  .financial-highlights {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 160px !important;
  }
}

/* 自定义滚动条（现代化） */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
}

::-webkit-scrollbar-thumb {
  background: var(--gray-300);
  border-radius: var(--border-radius);
  border: 2px solid var(--bg-secondary);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--gray-400);
}

/* 工具类（紧凑） */
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

/* 估值逻辑与交易计划样式（紧凑） */
.valuation-container {
  margin-bottom: 0.75rem;
}

.trading-form .grid {
  display: grid;
  gap: 0.75rem;
}

/* 双列布局（默认） */
.trading-form .grid.cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

/* 现代化颜色系统 */
:root {
  --primary-color: #3b82f6; /* 蓝色主题 - 更现代友好 */
  --primary-dark: #2563eb;
  --primary-light: rgba(59, 130, 246, 0.1);
  --success-color: #10b981; /* 成功/增长 - 绿色 */
  --warning-color: #f59e0b; /* 警告/中性 - 橙色 */
  --danger-color: #ef4444;  /* 危险/下跌 - 红色 */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-card: #ffffff;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  --text-primary: var(--gray-900);
  --text-secondary: var(--gray-600);
  --text-tertiary: var(--gray-500);
  --border-radius-sm: 0.375rem; /* 6px */
  --border-radius: 0.5rem;     /* 8px */
  --border-radius-lg: 0.75rem; /* 12px */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.text-primary {
  color: var(--primary-color);
}

.bg-primary\/10 {
  background-color: var(--primary-light);
}

/* 字体系统统一 */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: var(--text-primary);
  line-height: 1.5;
}

/* 标题样式 */
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  line-height: 1.25;
  color: var(--text-primary);
}

h1 { font-size: 1.5rem; } /* 24px */
h2 { font-size: 1.25rem; } /* 20px */
h3 { font-size: 1.125rem; } /* 18px */
h4 { font-size: 1rem; } /* 16px */

/* 文本样式 */
.text-sm { font-size: 0.875rem; } /* 14px */
.text-xs { font-size: 0.75rem; } /* 12px */
.text-lg { font-size: 1.125rem; } /* 18px */
.text-xl { font-size: 1.25rem; } /* 20px */
.text-2xl { font-size: 1.5rem; } /* 24px */

/* 间距系统 */
.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 0.75rem; }
.mt-4 { margin-top: 1rem; }

.mb-1 { margin-bottom: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-5 { margin-bottom: 1.25rem; }

.p-1 { padding: 0.25rem; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 0.75rem; }
.p-4 { padding: 1rem; }

/* 卡片通用样式 */
.card {
  background-color: var(--bg-card);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--gray-200);
  overflow: hidden;
  transition: box-shadow 0.2s ease-in-out, transform 0.1s ease-in-out;
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.card-header {
  padding: 1rem;
  border-bottom: 1px solid var(--gray-200);
  background-color: var(--bg-secondary);
}

.card-body {
  padding: 1rem;
}

.card-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--gray-200);
  background-color: var(--bg-secondary);
}

/* 按钮通用样式 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-sm);
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  cursor: pointer;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.btn-primary:hover {
  background-color: var(--primary-dark);
  border-color: var(--primary-dark);
}

.btn-secondary {
  background-color: var(--gray-200);
  color: var(--text-primary);
  border-color: var(--gray-200);
}

.btn-secondary:hover {
  background-color: var(--gray-300);
  border-color: var(--gray-300);
}

/* 输入框样式 */
.form-input, .form-textarea {
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--gray-300);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 标签样式 */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: var(--border-radius-sm);
  line-height: 1.25;
}

.badge-primary {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

.badge-success {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.badge-danger {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}
</style>