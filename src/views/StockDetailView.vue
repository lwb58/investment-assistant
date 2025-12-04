<template>
  <div class="stock-detail-container" id="top">
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
      <!-- 浮动返回顶部按钮 -->
      <button 
        id="floating-back-to-top" 
        class="fixed bottom-8 right-8 bg-primary text-white p-3 rounded-full shadow-lg hover:bg-primary/90 transition-all duration-300 hover:scale-110 z-500 cursor-pointer"
        title="返回顶部"
        @click="scrollToTop"
      >
        <i class="text-xl">🔝</i>
      </button>
      <!-- 股票核心信息栏（固定顶部，现代化设计） -->
      <div class="stock-header sticky top-0 z-20 bg-gradient-to-r from-white to-gray-50/95 backdrop-blur-md shadow-lg border-b border-gray-200">
        <div class="container mx-auto px-3 py-3 flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
          <div class="flex items-center gap-3">
            <button class="btn-icon-round hover:bg-gray-200 transition-all duration-300 p-2 rounded-full" @click="goBack" title="返回">
              <i class="text-lg">←</i>
            </button>
            <div class="stock-basic">
              <h1 class="stock-title flex items-center gap-2 text-xl md:text-2xl font-bold">
                {{ stockInfo.name }}
                <span class="stock-code text-gray-500 text-sm md:text-base font-medium px-2 py-0.5 bg-gray-100 rounded-full">
                  {{ stockInfo.code }}
                </span>
              </h1>
              <div class="stock-industry text-sm md:text-base text-gray-600 mt-1 flex items-center gap-1">
                <i class="icon">🏢</i>
                {{ stockInfo.industry || '未知行业' }}
              </div>
            </div>
          </div>

          <div class="price-group flex items-center gap-4">
            <div class="price-display text-center">
              <div class="current-price text-2xl md:text-3xl font-bold tracking-tight">
                {{ formatPrice(stockInfo.price) }}
              </div>
              <div :class="['price-change flex items-center justify-center gap-1.5 mt-1 text-sm px-3 py-1 rounded-full font-medium',
                stockInfo.changeRate > 0 ? 'bg-red-50 text-red-600 hover:bg-red-100' :
                  stockInfo.changeRate < 0 ? 'bg-green-50 text-green-600 hover:bg-green-100' : 'bg-gray-50 text-gray-600']" 
                  class="transition-all duration-300">
                <span v-if="stockInfo.changeRate > 0" class="text-lg">↗️</span>
                <span v-else-if="stockInfo.changeRate < 0" class="text-lg">↘️</span>
                <span v-else class="text-lg">➡️</span>
                {{ stockInfo.changeRate > 0 ? '+' : '' }}{{ stockInfo.changeRate.toFixed(2) }}%
              </div>
            </div>

            <!-- 新增笔记按钮（现代化样式） -->
            <button class="btn primary flex items-center gap-2 px-4 py-2 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5">
              <i class="icon text-lg">✏️</i>
              新增笔记
            </button>
          </div>
        </div>
      </div>

      <div class="container mx-auto px-2 py-4 max-w-7xl">
        <!-- 左侧导航栏 -->
        <div class="flex flex-col md:flex-row gap-2">
          <!-- 固定导航栏 -->
          <div class="md:w-1/6 lg:w-1/7">
            <div class="sticky top-5 bg-white/95 border border-gray-200 rounded-xl shadow-lg p-3 backdrop-filter backdrop-blur-md">
              <h3 class="nav-title text-sm font-semibold text-gray-800 mb-3 px-2 flex items-center gap-2">
                <i class="icon text-xl">📋</i> 快速导航
              </h3>
              <ul class="nav-list space-y-2">
                <li>
                  <a href="#top" @click.prevent="scrollToTop" class="nav-item block px-3 py-2 text-sm rounded-lg hover:bg-primary/10 hover:text-primary transition-all duration-300 flex items-center gap-2">
                    <i class="icon">🔝</i> 返回顶部
                  </a>
                </li>
                <li>
                  <a href="#financial-indicators" class="nav-item block px-3 py-2 text-sm rounded-lg hover:bg-primary/10 hover:text-primary transition-all duration-300 flex items-center gap-2">
                    <i class="icon">📋</i> 财务指标
                  </a>
                </li>
                <li>
                  <a href="#financial-trends" class="nav-item block px-3 py-2 text-sm rounded-lg hover:bg-primary/10 hover:text-primary transition-all duration-300 flex items-center gap-2">
                    <i class="icon">📊</i> 财务趋势
                  </a>
                </li>
                <li>
                  <a href="#dupont-analysis" class="nav-item block px-3 py-2 text-sm rounded-lg hover:bg-primary/10 hover:text-primary transition-all duration-300 flex items-center gap-2">
                    <i class="icon">📈</i> 杜邦分析
                  </a>
                </li>
                <li>
                  <a href="#related-notes" class="nav-item block px-3 py-2 text-sm rounded-lg hover:bg-primary/10 hover:text-primary transition-all duration-300 flex items-center gap-2">
                    <i class="icon">📝</i> 关联笔记
                  </a>
                </li>
                <li>
                  <a href="#pros-cons-analysis" class="nav-item block px-3 py-2 text-sm rounded-lg hover:bg-primary/10 hover:text-primary transition-all duration-300 flex items-center gap-2">
                    <i class="icon">👍</i> 利好利空
                  </a>
                </li>
                <li>
                  <a href="#valuation-logic" class="nav-item block px-3 py-2 text-sm rounded-lg hover:bg-primary/10 hover:text-primary transition-all duration-300 flex items-center gap-2">
                    <i class="icon">💡</i> 估值逻辑
                  </a>
                </li>
                <li>
                  <a href="#competitor-analysis" class="nav-item block px-3 py-2 text-sm rounded-lg hover:bg-primary/10 hover:text-primary transition-all duration-300 flex items-center gap-2">
                    <i class="icon">🏢</i> 竞争对手
                  </a>
                </li>
                <li>
                  <a href="#investment-forecast" class="nav-item block px-3 py-2 text-sm rounded-lg hover:bg-primary/10 hover:text-primary transition-all duration-300 flex items-center gap-2">
                    <i class="icon">🎯</i> 投资预测
                  </a>
                </li>
              </ul>
            </div>
          </div>
          
          <!-- 主要内容区域 -->
          <div class="md:w-5/6 lg:w-6/7">
            <!-- 快速指标卡片（现代化网格布局） -->
            <div id="financial-indicators"
              class="quick-metrics card mb-6 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 p-4 border border-gray-200 rounded-xl shadow-md bg-white hover:shadow-lg transition-all duration-300">
              <div
                class="metric-item bg-gradient-to-br from-white to-gray-50 p-3 rounded-lg border border-gray-200 hover:border-primary/30 hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
                <div class="metric-label text-sm text-gray-600 mb-1 font-medium">总市值</div>
                <div class="metric-value font-bold text-xl text-gray-800">{{ formatNumber(stockInfo.marketCap) }}亿</div>
              </div>
              <div
                class="metric-item bg-gradient-to-br from-white to-gray-50 p-3 rounded-lg border border-gray-200 hover:border-primary/30 hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
                <div class="metric-label text-sm text-gray-600 mb-1 font-medium">市盈率(TTM)</div>
                <div class="metric-value font-bold text-xl text-gray-800">{{ currentFinancialData.pe || '--' }}</div>
              </div>
              <div
                class="metric-item bg-gradient-to-br from-white to-gray-50 p-3 rounded-lg border border-gray-200 hover:border-primary/30 hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
                <div class="metric-label text-sm text-gray-600 mb-1 font-medium">净资产收益率</div>
                <div class="metric-value font-bold text-xl text-gray-800">{{ currentFinancialData.roe || '--' }}%</div>
              </div>
              <div
                class="metric-item bg-gradient-to-br from-white to-gray-50 p-3 rounded-lg border border-gray-200 hover:border-primary/30 hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
                <div class="metric-label text-sm text-gray-600 mb-1 font-medium">所属行业</div>
                <div class="metric-value font-bold text-xl text-gray-800">{{ stockInfo.industry || '--' }}</div>
              </div>
              <div
                class="metric-item bg-gradient-to-br from-white to-gray-50 p-3 rounded-lg border border-gray-200 hover:border-primary/30 hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
                <div class="metric-label text-sm text-gray-600 mb-1 font-medium">总股本</div>
                <div class="metric-value font-bold text-xl text-gray-800">{{ formatNumber(stockInfo.totalShares) }}亿股
                </div>
              </div>
              <div
                class="metric-item bg-gradient-to-br from-white to-gray-50 p-3 rounded-lg border border-gray-200 hover:border-primary/30 hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
                <div class="metric-label text-sm text-gray-600 mb-1 font-medium">流通股本</div>
                <div class="metric-value font-bold text-xl text-gray-800">{{ formatNumber(stockInfo.floatShares) }}亿股
                </div>
              </div>
            </div>

            <!-- 财务数据与趋势图表（现代化设计） -->
            <div class="grid grid-cols-1 gap-4 mb-6">
              <!-- 财务趋势图表组 -->
              <div id="financial-trends" class="card p-5 border border-gray-200 rounded-xl shadow-lg bg-white hover:shadow-xl transition-all duration-300">
                <div class="card-header mb-4">
                  <h3 class="card-title text-xl font-bold flex items-center gap-2 text-gray-800">
                    <i class="icon text-primary text-2xl">📊</i> 财务趋势（{{ financialYears.length }}年）
                  </h3>
                </div>

                <!-- 图表容器：上下布局 -->
                <div class="chart-group space-y-6">
                  <!-- 总营收趋势图 -->
                  <div class="chart-section bg-gradient-to-r from-white to-gray-50 p-4 rounded-lg border border-gray-200">
                    <h4 class="chart-subtitle text-lg font-semibold mb-3 text-gray-700 flex items-center gap-1.5">
                      <i class="icon">📈</i> 总营收趋势（单位：亿元）
                    </h4>
                    <div class="chart-container h-64 rounded-lg border border-gray-200 overflow-hidden bg-white">
                      <canvas id="revenueTrendChart"></canvas>
                    </div>
                  </div>
                  <!-- 归母净利润趋势图 -->
                  <div class="chart-section bg-gradient-to-r from-white to-gray-50 p-4 rounded-lg border border-gray-200">
                    <h4 class="chart-subtitle text-lg font-semibold mb-3 text-gray-700 flex items-center gap-1.5">
                      <i class="icon">💰</i> 归母净利润趋势（单位：亿元）
                    </h4>
                    <div class="chart-container h-64 rounded-lg border border-gray-200 overflow-hidden bg-white">
                      <canvas id="netProfitTrendChart"></canvas>
                    </div>
                  </div>
                  <!-- 扣非净利润趋势图 -->
                  <div class="chart-section bg-gradient-to-r from-white to-gray-50 p-4 rounded-lg border border-gray-200">
                    <h4 class="chart-subtitle text-lg font-semibold mb-3 text-gray-700 flex items-center gap-1.5">
                      <i class="icon">📊</i> 扣非净利润趋势（单位：亿元）
                    </h4>
                    <div class="chart-container h-64 rounded-lg border border-gray-200 overflow-hidden bg-white">
                      <canvas id="nonProfitTrendChart"></canvas>
                    </div>
                  </div>
                </div>

                <!-- 图表说明 -->
                <div class="chart-desc text-sm text-gray-600 mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p class="flex items-center gap-1.5"><i class="icon">📋</i> 数据来源：公司年度财务报告 | 自动适配{{ financialYears.length }}年数据</p>
                </div>
              </div>
            </div>
            <!-- 杜邦分析数据表格 -->
            <div id="dupont-analysis" class="card p-4 border border-gray-200 rounded-xl shadow-md bg-white hover:shadow-lg transition-all duration-300 mb-6">
              <h3 class="text-lg font-semibold mb-3">杜邦分析数据</h3>
              <div v-if="dupontLoading" class="flex items-center justify-center py-8">
                <div class="loading-spinner"></div>
              </div>
              <div v-else-if="dupontData && dupontData.full_data && dupontData.full_data.length > 0">
                <div class="overflow-x-auto">
                  <table class="min-w-full border-collapse">
                    <thead>
                      <tr class="bg-gray-50">
                        <th class="border border-gray-200 px-4 py-2 text-left text-sm font-medium text-gray-600">报告期</th>
                        <th class="border border-gray-200 px-4 py-2 text-left text-sm font-medium text-gray-600">周期类型</th>
                        <th class="border border-gray-200 px-4 py-2 text-right text-sm font-medium text-gray-600">净资产收益率</th>
                        <th class="border border-gray-200 px-4 py-2 text-right text-sm font-medium text-gray-600">销售净利率</th>
                        <th class="border border-gray-200 px-4 py-2 text-right text-sm font-medium text-gray-600">资产周转率(次)</th>
                        <th class="border border-gray-200 px-4 py-2 text-right text-sm font-medium text-gray-600">权益乘数</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, index) in dupontData.full_data" :key="index" :class="index % 2 === 0 ? 'bg-white' : 'bg-gray-50'">
                        <td class="border border-gray-200 px-4 py-2 text-sm text-gray-800">{{ item['报告期'] }}</td>
                        <td class="border border-gray-200 px-4 py-2 text-sm text-gray-800">{{ item['周期类型'] }}</td>
                        <td class="border border-gray-200 px-4 py-2 text-sm text-right text-gray-800">{{ item['净资产收益率'] || '-' }}</td>
                        <td class="border border-gray-200 px-4 py-2 text-sm text-right text-gray-800">{{ item['归属母公司股东的销售净利率'] || '-' }}</td>
                        <td class="border border-gray-200 px-4 py-2 text-sm text-right text-gray-800">{{ item['资产周转率(次)'] || '-' }}</td>
                        <td class="border border-gray-200 px-4 py-2 text-sm text-right text-gray-800">{{ item['权益乘数'] || '-' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div v-else>
                <div class="text-center text-gray-500 py-8">未获取到杜邦分析数据</div>
              </div>
            </div>

            <!-- 杜邦分析图表区域 -->
            <div class="card p-4 border border-gray-200 rounded-xl shadow-md bg-white hover:shadow-lg transition-all duration-300 mb-6">
              <h3 class="text-lg font-semibold mb-3">杜邦分析法趋势</h3>

              <!-- 三因素分析 -->
              <div class="mb-6">
                <h4 class="text-sm text-gray-600 mb-2">三因素分析（ROE = 销售净利率 × 资产周转率 × 权益乘数）</h4>
                <div class="h-64 bg-gray-50 rounded relative">
                  <!-- 加载状态 -->
                  <div v-if="dupontLoading" class="absolute inset-0 flex items-center justify-center bg-white/80 z-10">
                    <div class="loading-spinner"></div>
                  </div>
                  
                  <!-- 图表容器 -->
                  <canvas id="threeFactorChart" class="h-full w-full"></canvas>
                  
                  <!-- 错误提示 -->
                  <div v-if="!dupontLoading && threeFactorError" class="absolute inset-0 flex items-center justify-center text-red-500 text-sm">
                    {{ threeFactorError }}
                  </div>
                </div>
              </div>

              <!-- 五因素分析 -->
              <div>
                <h4 class="text-sm text-gray-600 mb-2">五因素分析（ROE = 经营利润率 × 资产周转率 × 权益乘数 × 税负因素 × 利息负担）</h4>
                <div class="h-64 bg-gray-50 rounded relative">
                  <!-- 加载状态 -->
                  <div v-if="dupontLoading" class="absolute inset-0 flex items-center justify-center bg-white/80 z-10">
                    <div class="loading-spinner"></div>
                  </div>
                  
                  <!-- 图表容器 -->
                  <canvas id="fiveFactorChart" class="h-full w-full"></canvas>
                  
                  <!-- 错误提示 -->
                  <div v-if="!dupontLoading && fiveFactorError" class="absolute inset-0 flex items-center justify-center text-red-500 text-sm">
                    {{ fiveFactorError }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 主内容区域：左右并列布局 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-2">
              <!-- 左侧：占6列 -->
              <div class="space-y-2">
                <!-- 关联笔记卡片 -->
                <div id="related-notes" class="card p-4 border border-gray-200 rounded-xl shadow-md bg-white hover:shadow-lg transition-all duration-300 mb-6">
                  <div class="card-header mb-1 flex justify-between items-center">
                    <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                      <i class="icon text-primary">📝</i> 关联笔记
                    </h3>
                    <button class="btn bg-primary/10 text-primary hover:bg-primary/20 py-1.5 px-3"
                      @click="openNoteModal('create')">
                      新增
                    </button>
                  </div>

                  <!-- 笔记列表（紧凑间距） -->
                  <div v-if="stockNotes.length > 0" class="notes-list space-y-2 max-h-48 overflow-y-auto pr-1">
                    <div
                      class="note-item p-2 bg-gray-50 rounded-lg border border-gray-100 cursor-pointer hover:bg-gray-100 transition-colors"
                      v-for="(note, index) in stockNotes" :key="note.id" @click="openNoteModal('view', note)">
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

                  <div v-else class="empty-state py-4 text-center">
                    <div class="empty-icon text-2xl mb-1">📝</div>
                    <p class="empty-text text-xs text-gray-500">暂无关联笔记</p>
                    <button class="btn primary mt-2 py-1.5 px-3" @click="openNoteModal('create')">
                      <i class="icon">✏️</i> 创建第一条
                    </button>
                  </div>
                </div>

                <!-- 利好利空点卡片 -->
                <div id="pros-cons-analysis" class="card p-5 bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300 mb-6">
                  <div class="card-header mb-5">
                    <h3 class="card-title text-lg font-semibold text-gray-800 flex items-center gap-2">
                      <i class="text-primary">📊</i> 利好利空分析
                    </h3>
                  </div>
                  <div class="pros-cons-container grid grid-cols-1 md:grid-cols-2 gap-5">
                    <!-- 利好点区域 -->
                    <div class="pros-section">
                      <div class="section-header flex items-center mb-4">
                        <div class="flex items-center gap-2">
                          <div class="bg-red-300 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium">
                            ✓
                          </div>
                          <span class="text-base font-semibold text-red-700">利好点</span>
                        </div>
                      </div>
                      <div class="pros-area p-3 bg-red-50 rounded-lg hover:bg-red-100/70 transition-all duration-200">
                        <textarea v-model="prosPoints"
                                  v-auto-resize
                                  class="form-textarea w-full px-2 py-2 border-none bg-transparent focus:outline-none text-xl resize-y"
                                  placeholder="输入利好因素..."
                                  style="min-height: 80px; height: auto; overflow-y: hidden;"></textarea>
                      </div>
                    </div>

                    <!-- 利空点区域 -->
                    <div class="cons-section">
                      <div class="section-header flex items-center mb-4">
                        <div class="flex items-center gap-2">
                          <div class="bg-green-300 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium">
                            ✗
                          </div>
                          <span class="text-base font-semibold text-green-700">利空点</span>
                        </div>
                      </div>
                      <div class="cons-area p-3 bg-green-50 rounded-lg hover:bg-green-100/70 transition-all duration-200">
                        <textarea v-model="consPoints"
                                  v-auto-resize
                                  class="form-textarea w-full px-2 py-2 border-none bg-transparent focus:outline-none text-xl resize-y"
                                  placeholder="输入利空因素..."
                                  style="min-height: 80px; height: auto; overflow-y: hidden;"></textarea>
                      </div>
                    </div>
                  </div>
                  <div class="save-section mt-6">
                    <button class="btn primary w-full py-2.5 rounded-lg font-medium hover:shadow-md transition-all duration-300"
                            @click="saveProsConsSummary">
                      保存利好利空分析
                    </button>
                  </div>
                </div>

                <!-- 估值逻辑记录卡片 -->
                <div id="valuation-logic" class="card p-4 border border-gray-200 rounded-xl shadow-md bg-white hover:shadow-lg transition-all duration-300 mb-6">
                  <div class="card-header mb-1">
                    <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                      <i class="icon text-primary">💡</i> 估值逻辑
                    </h3>
                  </div>
                  <div class="valuation-container">
                    <textarea v-model="valuationLogic"
                      class="form-textarea w-full px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent mb-2 text-sm"
                      rows="3" placeholder="记录估值逻辑（行业中枢、增长预期等）"></textarea>
                    <button class="btn primary w-full py-2" @click="saveValuationLogic">
                      保存估值逻辑
                    </button>
                  </div>
                </div>
              </div>

              <!-- 右侧：占6列 -->
              <div class="space-y-2">
                <!-- 友商录入卡片 -->
                <div id="competitor-analysis" class="card p-4 border border-gray-200 rounded-xl shadow-md bg-white hover:shadow-lg transition-all duration-300 mb-6">
                  <div class="card-header mb-1">
                    <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
                      <i class="icon text-primary">🤝</i> 友商录入
                    </h3>
                  </div>
                  <div class="competitors-container space-y-2">
                    <div v-if="competitors.length > 0" class="competitor-list space-y-2 max-h-48 overflow-y-auto pr-1">
                      <div
                        class="competitor-item p-2 bg-gray-50 rounded-lg border border-gray-100 flex items-center justify-between cursor-pointer hover:bg-gray-100 transition-colors"
                        v-for="(competitor, index) in competitors" :key="index"
                        @click="goToCompetitorDetail(competitor.code)">
                        <div class="competitor-info flex items-center gap-1.5">
                          <div
                            class="competitor-rank w-5 h-5 flex items-center justify-center bg-primary/10 text-primary rounded-full text-xs">
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
                      <p class="empty-text text-xs text-gray-500">暂无友商数据</p>
                    </div>
                    <div class="add-competitor-form grid grid-cols-2 gap-2">
                      <input v-model="newCompetitor.name" type="text"
                        class="form-input px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                        placeholder="友商名称">
                      <input v-model="newCompetitor.code" type="text"
                        class="form-input px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                        placeholder="友商代码">
                      <button class="btn primary col-span-2 py-2" @click="addCompetitor"
                        :disabled="!newCompetitor.name || !newCompetitor.code">
                        添加友商
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div> <!-- 修复：闭合主要内容区域的外层div -->
        </div>
      </div>

      <!-- 笔记模态框（紧凑样式） -->
      <teleport to="body">
        <div v-if="noteModalOpen"
          class="modal-backdrop fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-3">
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
                  <input v-model="noteForm.title" type="text"
                    class="form-input w-full px-2.5 py-1.5 border border-gray-200 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                    placeholder="输入笔记标题（关联股票：{{ stockInfo.code }} {{ stockInfo.name }}）" required>
                </div>
                <div class="form-group mb-2.5">
                  <label class="form-label block text-sm font-medium text-gray-700 mb-0.5">笔记内容</label>
                  <textarea v-model="noteForm.content"
                    class="form-textarea w-full px-2.5 py-1.5 border border-gray-200 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                    rows="6" placeholder="输入笔记内容（分析、操作计划等）" required></textarea>
                </div>
                <div class="form-group mb-2.5">
                  <label class="form-label block text-sm font-medium text-gray-700 mb-0.5">关联股票</label>
                  <div
                    class="form-control bg-gray-50 px-2.5 py-1.5 border border-gray-200 rounded-md text-gray-700 text-sm">
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
      

      
      <!-- 投资预测与交易计划卡片（移动到页面底部） -->
      <div id="investment-forecast" class="card p-4 border border-gray-200 rounded-xl shadow-md bg-white hover:shadow-lg transition-all duration-300 mb-6">
        <div class="card-header mb-1">
          <h3 class="card-title text-sm font-semibold flex items-center gap-1.5 text-gray-800">
            <i class="icon text-primary">📈</i> 投资预测与交易计划
          </h3> <!-- 修复：闭合h3标签，删除多余文字 -->
        </div>
        <div class="trading-form grid grid-cols-1 gap-2 mb-2">
          <div class="grid grid-cols-2 gap-2">
            <div class="form-group">
              <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">目标买入点（元）</label>
              <input v-model="buyPoint" type="number" step="0.01"
                class="form-input w-full px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                placeholder="输入买入价">
            </div>
            <div class="form-group">
              <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">预期涨幅（%）</label>
              <input v-model="expectedGrowthRate" type="number" step="0.1"
                class="form-input w-full px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                placeholder="预期涨幅">
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div class="form-group">
              <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">预期目标点位（元）</label>
              <input v-model="expectedPoint" type="number" step="0.01"
                class="form-input w-full px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm bg-gray-50"
                placeholder="自动计算" readonly>
            </div>
            <div class="form-group">
              <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">预期市值（亿元）</label>
              <input v-model="expectedMarketCap" type="number" step="0.1"
                class="form-input w-full px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm bg-gray-50"
                placeholder="自动计算" readonly>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div class="form-group">
              <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">最大跌幅（%）</label>
              <input v-model="maxLossRate" type="number" step="0.1"
                class="form-input w-full px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                placeholder="可接受跌幅">
            </div>
            <div class="form-group">
              <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">最大亏损点位（元）</label>
              <input v-model="maxLossPoint" type="number" step="0.01"
                class="form-input w-full px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm bg-gray-50"
                placeholder="自动计算" readonly>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div class="form-group">
              <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">最大上涨幅度（%）</label>
              <input v-model="maxUpwardRange" type="number" step="0.1"
                class="form-input w-full px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                placeholder="预期最大涨幅">
            </div>
            <div class="form-group">
              <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">最大下跌幅度（%）</label>
              <input v-model="maxDownwardRange" type="number" step="0.1"
                class="form-input w-full px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
                placeholder="预期最大跌幅">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label block text-xs font-medium text-gray-600 mb-0.5">投资时长（月）</label>
            <input v-model="investmentDuration" type="number" step="1"
              class="form-input w-full px-2 py-2 border border-gray-100 rounded-md focus:outline-none focus:ring-1.5 focus:ring-primary focus:border-transparent text-sm"
              placeholder="预期投资时长">
          </div>
          <button class="btn primary py-2" @click="saveInvestmentPlan">
            保存投资计划
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '../api/apiService.js'
import Chart from 'chart.js/auto'
import ChartDataLabels from 'chartjs-plugin-datalabels'

// 注册数据标签插件
Chart.register(ChartDataLabels)

const route = useRoute()
const router = useRouter()

// 浮动返回顶部按钮引用
const floatingBackToTopBtn = ref(null);

// 滚动到顶部函数
const scrollToTop = () => {
  if (typeof window !== 'undefined') {
    // 优先使用page-content容器（真正的滚动容器）
    const scrollContainer = document.querySelector('.page-content') || 
                          document.querySelector('.app-container') || 
                          window;
    
    scrollContainer.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
};

const threeFactorError = ref('')
const fiveFactorError = ref('')

// 杜邦分析相关状态
const dupontData = ref(null)
const dupontLoading = ref(false)
const threeFactorChartInstance = ref(null)
const fiveFactorChartInstance = ref(null)

// 响应式状态（新增估值、买卖点、竞争对手字段）
const stockInfo = ref({
  code: '',
  name: '',
  price: '0.00',
  changeRate: 0,
  industry: '',
  companyName: '',
  companyProfile: '',
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

// 处理图表加载错误
const handleChartError = (type) => {
  if (type === 'three') {
    threeFactorError.value = '三因素图表加载失败'
  } else {
    fiveFactorError.value = '五因素图表加载失败'
  }
}

// 组件挂载时执行
onMounted(() => {
  fetchStockData()
  fetchStockNotes()
  // fetchValuationLogic()
  fetchDupontData() // 新增：加载杜邦分析数据
  
  // 初始化导航
  initNavigation()
  
  // 初始调整文本框高度
  nextTick(() => {
    autoResizeTextarea('prosPointsTextarea')
    autoResizeTextarea('consPointsTextarea')
  })
  
  // 获取浮动返回顶部按钮
  floatingBackToTopBtn.value = document.getElementById('floating-back-to-top')
  
  // 初始隐藏按钮（仅在页面滚动位置大于100px时显示）
  if (floatingBackToTopBtn.value) {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    if (scrollTop <= 100) {
      floatingBackToTopBtn.value.style.opacity = '0';
      floatingBackToTopBtn.value.style.visibility = 'hidden';
    }
  }
  
  // 监听滚动事件
  window.addEventListener('scroll', handleScroll)
  
  // 窗口大小变化时重新渲染图表
  window.addEventListener('resize', handleResize)
})

// 处理窗口大小变化
const handleResize = () => {
  if (dupontData.value && dupontData.value.full_data) {
    setTimeout(() => {
      initThreeFactorChart()
      initFiveFactorChart()
    }, 100)
  }
}

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('scroll', handleScroll) // 清理滚动事件监听器
  
  // 销毁图表实例
  if (threeFactorChartInstance.value) {
    threeFactorChartInstance.value.destroy()
  }
  if (fiveFactorChartInstance.value) {
    fiveFactorChartInstance.value.destroy()
  }
})

// 获取杜邦分析数据
const fetchDupontData = async () => {
  if (!stockCode.value) return
  
  dupontLoading.value = true
  try {
    const data = await apiService.getStockDupontAnalysis(stockCode.value)
    if (data && data.full_data) {
      dupontData.value = data
      // 数据加载完成后初始化图表
      setTimeout(() => {
        initThreeFactorChart()
        initFiveFactorChart()
      }, 100)
    }
  } catch (error) {
    console.error('获取杜邦分析数据失败:', error)
  } finally {
    dupontLoading.value = false
  }
}

// 初始化三因素杜邦分析图表
const initThreeFactorChart = () => {
  if (!Chart || !dupontData.value || !dupontData.value.full_data) return
  
  const ctx = document.getElementById('threeFactorChart')
  if (!ctx) return
  
  // 销毁现有图表实例
  if (threeFactorChartInstance.value) {
    threeFactorChartInstance.value.destroy()
  }
  
  // 准备数据 - 从最新到最旧排序
  const sortedData = [...dupontData.value.full_data].reverse()
  const labels = sortedData.map(item => item['报告期'])
  
  // 提取ROE数据（去掉%号并转换为数字）
  const roeData = sortedData.map(item => {
    const value = parseFloat(item['净资产收益率']?.replace('%', '') || 0)
    return isNaN(value) ? 0 : value
  })
  
  // 提取销售净利率数据
  const profitMarginData = sortedData.map(item => {
    const value = parseFloat(item['归属母公司股东的销售净利率']?.replace('%', '') || 0)
    return isNaN(value) ? 0 : value
  })
  
  // 提取资产周转率数据
  const assetTurnoverData = sortedData.map(item => {
    const value = parseFloat(item['资产周转率(次)'] || 0)
    return isNaN(value) ? 0 : value
  })
  
  // 提取权益乘数数据
  const equityMultiplierData = sortedData.map(item => {
    const value = parseFloat(item['权益乘数'] || 0)
    return isNaN(value) ? 0 : value
  })
  
  // 创建图表
  threeFactorChartInstance.value = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'ROE (%)',
          data: roeData,
          borderColor: '#165DFF',
          backgroundColor: 'rgba(22, 93, 255, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#165DFF',
          pointRadius: 4,
          tension: 0.3
        },
        {
          label: '销售净利率 (%)',
          data: profitMarginData,
          borderColor: '#52C41A',
          backgroundColor: 'rgba(82, 196, 26, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#52C41A',
          pointRadius: 4,
          tension: 0.3
        },
        {
          label: '资产周转率 (次)',
          data: assetTurnoverData,
          borderColor: '#FAAD14',
          backgroundColor: 'rgba(250, 173, 20, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#FAAD14',
          pointRadius: 4,
          tension: 0.3,
          yAxisID: 'y1'
        },
        {
          label: '权益乘数',
          data: equityMultiplierData,
          borderColor: '#F5222D',
          backgroundColor: 'rgba(245, 34, 45, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#F5222D',
          pointRadius: 4,
          tension: 0.3,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            font: { size: 12 },
            boxWidth: 15
          }
        },
        tooltip: {
          padding: 10,
          mode: 'index',
          intersect: false
        },
        // 添加数据点标签
        datalabels: {
          display: true,
          color: '#333',
          font: {
            size: 10
          },
          formatter: function(value, context) {
            // 根据数据类型显示不同格式
            if (context.dataset.label.includes('(%)')) {
              return value.toFixed(2) + '%';
            } else {
              return value.toFixed(2);
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            font: { size: 11 },
            maxRotation: 45,
            minRotation: 45
          }
        },
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(0, 0, 0, 0.05)' },
          ticks: {
            font: { size: 11 },
            callback: (value) => `${value}%`
          },
          title: {
            display: true,
            text: '百分比 (%)',
            font: { size: 12 }
          }
        },
        y1: {
          position: 'right',
          beginAtZero: true,
          grid: { display: false },
          ticks: {
            font: { size: 11 }
          },
          title: {
            display: true,
            text: '倍数',
            font: { size: 12 }
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  })
}

// 初始化五因素杜邦分析图表
const initFiveFactorChart = () => {
  if (!Chart || !dupontData.value || !dupontData.value.full_data) return
  
  const ctx = document.getElementById('fiveFactorChart')
  if (!ctx) return
  
  // 销毁现有图表实例
  if (fiveFactorChartInstance.value) {
    fiveFactorChartInstance.value.destroy()
  }
  
  // 准备数据 - 从最新到最旧排序
  const sortedData = [...dupontData.value.full_data].reverse()
  const labels = sortedData.map(item => item['报告期'])
  
  // 提取ROE数据
  const roeData = sortedData.map(item => {
    const value = parseFloat(item['净资产收益率']?.replace('%', '') || 0)
    return isNaN(value) ? 0 : value
  })
  
  // 提取经营利润率数据
  const operatingMarginData = sortedData.map(item => {
    const value = parseFloat(item['经营利润率']?.replace('%', '') || 0)
    return isNaN(value) ? 0 : value
  })
  
  // 提取考虑税负因素数据
  const taxFactorData = sortedData.map(item => {
    const value = parseFloat(item['考虑税负因素']?.replace('%', '') || 0)
    return isNaN(value) ? 0 : value
  })
  
  // 提取考虑利息负担数据
  const interestFactorData = sortedData.map(item => {
    const value = parseFloat(item['考虑利息负担']?.replace('%', '') || 0)
    return isNaN(value) ? 0 : value
  })
  
  // 提取资产周转率数据（新增）
  const assetTurnoverData = sortedData.map(item => {
    const value = parseFloat(item['资产周转率(次)'] || 0)
    return isNaN(value) ? 0 : value
  })
  
  // 创建图表
  fiveFactorChartInstance.value = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'ROE (%)',
          data: roeData,
          borderColor: '#165DFF',
          backgroundColor: 'rgba(22, 93, 255, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#165DFF',
          pointRadius: 4,
          tension: 0.3
        },
        {
          label: '经营利润率 (%)',
          data: operatingMarginData,
          borderColor: '#52C41A',
          backgroundColor: 'rgba(82, 196, 26, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#52C41A',
          pointRadius: 4,
          tension: 0.3
        },
        {
          label: '税负因素 (%)',
          data: taxFactorData,
          borderColor: '#FAAD14',
          backgroundColor: 'rgba(250, 173, 20, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#FAAD14',
          pointRadius: 4,
          tension: 0.3
        },
        {
          label: '利息负担 (%)',
          data: interestFactorData,
          borderColor: '#F5222D',
          backgroundColor: 'rgba(245, 34, 45, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#F5222D',
          pointRadius: 4,
          tension: 0.3
        },
        {
          label: '资产周转率 (次)',
          data: assetTurnoverData,
          borderColor: '#95DE64',
          backgroundColor: 'rgba(149, 222, 100, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#95DE64',
          pointRadius: 4,
          tension: 0.3,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            font: { size: 12 },
            boxWidth: 15
          }
        },
        tooltip: {
          padding: 10,
          mode: 'index',
          intersect: false
        },
        // 添加数据点标签
        datalabels: {
          display: true,
          color: '#333',
          font: {
            size: 10
          },
          formatter: function(value, context) {
            // 根据数据类型显示不同格式
            if (context.dataset.label.includes('(%)')) {
              return value.toFixed(2) + '%';
            } else {
              return value.toFixed(2);
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            font: { size: 11 },
            maxRotation: 45,
            minRotation: 45
          }
        },
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(0, 0, 0, 0.05)' },
          ticks: {
            font: { size: 11 },
            callback: (value) => `${value}%`
          },
          title: {
            display: true,
            text: '百分比 (%)',
            font: { size: 12 }
          }
        },
        // 添加右侧Y轴用于资产周转率
        y1: {
          position: 'right',
          beginAtZero: true,
          grid: { display: false },
          ticks: {
            font: { size: 11 }
          },
          title: {
            display: true,
            text: '倍数/次',
            font: { size: 12 }
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  })
}

// 新增：估值与交易计划相关状态
const valuationLogic = ref('') // 估值逻辑
const buyPoint = ref('') // 买入点
const maxLossRate = ref('') // 最大亏损跌幅
const expectedGrowthRate = ref('') // 预期涨幅
const competitors = ref([]) // 竞争对手

// 新增：利好利空与总结
const prosPoints = ref('') // 利好点
const consPoints = ref('') // 利空点

// 新增：预测数据
const maxUpwardRange = ref('') // 最大上涨幅度
const maxDownwardRange = ref('') // 最大下跌幅度
const investmentDuration = ref('') // 投资时长

// 友商录入
const newCompetitor = ref({ name: '', code: '' }) // 新友商表单

// 计算属性：自动计算预期目标点位
const expectedPoint = computed(() => {
  const buyPrice = parseFloat(buyPoint.value)
  const growthRate = parseFloat(expectedGrowthRate.value)
  if (isNaN(buyPrice) || isNaN(growthRate)) return ''
  const result = buyPrice * (1 + growthRate / 100)
  return result.toFixed(2)
})

// 计算属性：自动计算预期市值
const expectedMarketCap = computed(() => {
  const targetPoint = parseFloat(expectedPoint.value)
  const totalShares = parseFloat(stockInfo.value.totalShares)
  if (isNaN(targetPoint) || isNaN(totalShares)) return ''
  const result = targetPoint * totalShares
  return result.toFixed(2)
})

// 计算属性：自动计算最大亏损点位
const maxLossPoint = computed(() => {
  const buyPrice = parseFloat(buyPoint.value)
  const lossRate = parseFloat(maxLossRate.value)
  if (isNaN(buyPrice) || isNaN(lossRate)) return ''
  const result = buyPrice * (1 - lossRate / 100)
  return result.toFixed(2)
})

// 图表实例（新增扣非净利润、应收账款图表）
const nonProfitChartInstance = ref(null)
const receivablesChartInstance = ref(null)
const revenueChartInstance = ref(null)
const netProfitChartInstance = ref(null)

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
  const revenueData = labels.map(year => {
    const value = parseFloat(financialData.value[year]?.totalRevenue || '0')
    return isNaN(value) ? 0 : value
  })
  const netProfitData = labels.map(year => {
    const value = parseFloat(financialData.value[year]?.netProfitAttribution || '0')
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

  // 总营收图表
  const revenueCtx = document.getElementById('revenueTrendChart')
  if (revenueCtx) {
    if (revenueChartInstance.value) revenueChartInstance.value.destroy()
    revenueChartInstance.value = new Chart(revenueCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: '总营收（亿元）',
          data: revenueData,
          borderColor: '#2EC7C9',
          backgroundColor: 'rgba(46, 199, 201, 0.1)',
          borderWidth: 1.5,
          pointBackgroundColor: '#2EC7C9',
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

  // 归母净利润图表
  const netProfitCtx = document.getElementById('netProfitTrendChart')
  if (netProfitCtx) {
    if (netProfitChartInstance.value) netProfitChartInstance.value.destroy()
    netProfitChartInstance.value = new Chart(netProfitCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: '归母净利润（亿元）',
          data: netProfitData,
          borderColor: '#5AB1EF',
          backgroundColor: 'rgba(90, 177, 239, 0.1)',
          borderWidth: 1.5,
          pointBackgroundColor: '#5AB1EF',
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
      companyProfile: data.baseInfo.companyProfile || '',
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

    // 利好利空数据处理：由fetchStockNotes()从笔记API加载，这里不做处理
    // prosPoints.value = data.prosCons?.prosPoints || ''
    // consPoints.value = data.prosCons?.consPoints || ''

    // 预测数据
    maxUpwardRange.value = data.prediction?.maxUpwardRange || ''
    maxDownwardRange.value = data.prediction?.maxDownwardRange || ''
    investmentDuration.value = data.prediction?.investmentDuration || ''

    // 竞争对手数据
    competitors.value = data.competitors || []

  } catch (err) {
    console.error('获取股票数据失败:', err)
    error.value = '加载股票信息失败，请稍后重试'
  } finally {
    loading.value = false
    // 初始化图表（数据加载完成后）
    setTimeout(initFinancialCharts, 300)
  }
}

// 存储现有的利好利空笔记ID
const prosConsNoteId = ref(null)
// 自定义指令：自动调整文本框高度
const vAutoResize = {
  mounted: (el) => {
    // 设置初始高度
    el.style.height = 'auto'
    el.style.height = el.scrollHeight + 'px'
    
    // 监听输入事件
    el.addEventListener('input', () => {
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 'px'
    })
    
    // 监听窗口大小变化
    window.addEventListener('resize', () => {
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 'px'
    })
  },
  updated: (el) => {
    // 当内容通过v-model更新时，也调整高度
    el.style.height = 'auto'
    el.style.height = el.scrollHeight + 'px'
  },
  unmounted: (el) => {
    // 清理事件监听
    window.removeEventListener('resize', () => {
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 'px'
    })
  }
}

// 获取关联笔记
const fetchStockNotes = async () => {
  try {
    const notes = await apiService.getNotesByStockCode(stockCode.value)
    
    // 过滤掉利好利空类型的笔记，只显示其他笔记
    stockNotes.value = (notes || []).filter(note => !note.title.startsWith('[利好利空]'))
    
    // 查找利好利空类型的笔记并加载数据
    const prosConsNote = notes.find(note => note.title.startsWith('[利好利空]'))
    if (prosConsNote) {
      try {
        const prosConsData = JSON.parse(prosConsNote.content)
        prosPoints.value = prosConsData.prosPoints || ''
        consPoints.value = prosConsData.consPoints || ''
        // 保存现有的利好利空笔记ID
        prosConsNoteId.value = prosConsNote.id
        
        // 数据加载完成后立即调整文本框高度
        nextTick(() => {
          autoResizeTextarea('prosPointsTextarea')
          autoResizeTextarea('consPointsTextarea')
        })
      } catch (parseError) {
        console.error('解析利好利空数据失败:', parseError)
      }
    } else {
      // 如果没有找到利好利空笔记，重置ID
    prosConsNoteId.value = null
    // 调整文本框高度
    nextTick(() => {
      autoResizeTextarea('prosPointsTextarea')
      autoResizeTextarea('consPointsTextarea')
    })
    }
  } catch (err) {
    console.error('获取笔记失败:', err)
    stockNotes.value = []
    prosConsNoteId.value = null
    // 调整文本框高度
    nextTick(() => {
      autoResizeTextarea('prosPointsTextarea')
      autoResizeTextarea('consPointsTextarea')
    })
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

// 保存投资计划（合并交易计划和预测数据）
const saveInvestmentPlan = async () => {
  try {
    // 保存交易计划
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

    // 保存预测数据
    await apiService.savePrediction({
      stockCode: stockCode.value,
      maxUpwardRange: maxUpwardRange.value,
      maxDownwardRange: maxDownwardRange.value,
      investmentDuration: investmentDuration.value
    })

    alert('投资计划保存成功！')
  } catch (err) {
    console.error('保存投资计划失败:', err)
    alert('保存失败，请稍后重试')
  }
}

// 保存利好利空与总结
const saveProsConsSummary = async () => {
  try {
    await apiService.saveProsConsSummary({
      stockCode: stockCode.value,
      prosPoints: prosPoints.value,
      consPoints: consPoints.value,
      investmentSummary: '' // 移除投资总结
    }, prosConsNoteId.value) // 传递现有的利好利空笔记ID，避免重复请求
    alert('利好利空分析保存成功！')
    // 保存成功后，重新获取笔记数据以更新最新状态
    await fetchStockNotes()
  } catch (err) {
    console.error('保存利好利空分析失败:', err)
    alert('保存失败，请稍后重试')
  }
}

// 导航功能优化
const initNavigation = () => {
  // 为非#top的导航锚点添加平滑滚动
  document.querySelectorAll('.nav-list a:not([href="#top"])').forEach(item => {
    // 先移除可能存在的旧事件监听器
    item.removeEventListener('click', handleNavClick);
    item.addEventListener('click', handleNavClick);
  });

  // 初始化导航状态
  handleScroll();
};

// 导航点击处理函数
const handleNavClick = function(e) {
  e.preventDefault();
  const targetId = this.getAttribute('href');
  const targetElement = document.querySelector(targetId);
  if (targetElement) {
    targetElement.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  }
};

// 滚动到顶部已移动到script setup内部

// 监听滚动事件，控制浮动返回顶部按钮的显示/隐藏
let lastScrollTop = 0;



const handleScroll = () => {
  if (typeof window === 'undefined') return;
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  
  // 处理浮动返回顶部按钮的显示/隐藏
  if (floatingBackToTopBtn.value) {
    // 确保按钮始终可见，便于测试
    floatingBackToTopBtn.value.style.opacity = '1';
    floatingBackToTopBtn.value.style.visibility = 'visible';
    floatingBackToTopBtn.value.style.pointerEvents = 'auto'; // 确保按钮可以接收点击事件
    floatingBackToTopBtn.value.style.zIndex = '9999'; // 确保按钮在最顶层
  }
  
  // 更新导航激活状态
  const sections = [
    { id: '#top', offset: 0 },
    { id: '#financial-trends', offset: 200 },
    { id: '#dupont-analysis', offset: 200 },
    { id: '#competitor-analysis', offset: 200 },
    { id: '#financial-indicators', offset: 200 },
    { id: '#investment-forecast', offset: 200 },
    { id: '#related-notes', offset: 200 }
  ];

  let currentSection = '#top';
  const scrollPosition = scrollTop + 100;

  // 找到当前滚动位置对应的区域
  for (const section of sections) {
    const element = document.querySelector(section.id);
    if (element) {
      const sectionTop = element.offsetTop;
      if (scrollPosition >= sectionTop) {
        currentSection = section.id;
      }
    }
  }

  // 更新导航项的激活状态
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (href === currentSection) {
      item.classList.add('bg-primary/20', 'text-primary', 'font-medium');
    } else {
      item.classList.remove('bg-primary/20', 'text-primary', 'font-medium');
    }
  });
  
  lastScrollTop = scrollTop;
};

// 添加友商
const addCompetitor = async () => {
  try {
    if (!newCompetitor.value.name || !newCompetitor.value.code) {
      alert('请填写友商名称和代码')
      return
    }

    await apiService.addCompetitor({
      stockCode: stockCode.value,
      competitor: newCompetitor.value
    })

    // 更新友商列表
    competitors.value.push({ ...newCompetitor.value })
    newCompetitor.value = { name: '', code: '' }
    alert('友商添加成功！')
  } catch (err) {
    console.error('添加友商失败:', err)
    alert('添加失败，请稍后重试')
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



// 组件卸载时清理资源
onUnmounted(() => {
  // 清理图表实例
  if (nonProfitChartInstance.value) nonProfitChartInstance.value.destroy()
  if (receivablesChartInstance.value) receivablesChartInstance.value.destroy()
  if (threeFactorChartInstance.value) threeFactorChartInstance.value.destroy()
  if (fiveFactorChartInstance.value) fiveFactorChartInstance.value.destroy()
  
  // 清理事件监听器
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* 基础样式：现代化设计核心配置 */
.stock-detail-container {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  min-height: 100vh;
  color: #111827;
  font-size: 14px;
  --primary-color: #667eea;
  --primary-dark: #5a67d8;
  --primary-light: #e9d8fd;
  --secondary-color: #48bb78;
  --accent-color: #ed8936;
  --bg-card: #ffffff;
  --bg-secondary: #f7fafc;
  --gray-100: #f7fafc;
  --gray-200: #edf2f7;
  --gray-300: #e2e8f0;
  --gray-400: #cbd5e0;
  --text-primary: #2d3748;
  --text-secondary: #4a5568;
  --text-tertiary: #718096;
  --border-radius: 12px;
  --border-radius-sm: 6px;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 1rem;
}

/* 加载和错误状态（现代化样式） */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  padding: 2rem;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
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
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
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

/* 按钮样式（现代化，美观设计） */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.5rem;
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  gap: 0.5rem;
  min-height: 42px;
  box-shadow: var(--shadow);
  text-transform: none;
  letter-spacing: normal;
  position: relative;
  overflow: hidden;
}

.btn.primary {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
  border-color: var(--primary-color);
}

.btn.primary:hover {
  background: linear-gradient(135deg, var(--primary-dark), #434190);
  border-color: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.btn.primary:active {
  transform: translateY(0);
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.2);
}

.btn-xs {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  min-height: 32px;
  border-radius: 6px;
}

.btn-icon-round {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f3f4f6;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #374151;
  font-size: 1rem;
  font-weight: 500;
}

.btn-icon-round:hover {
  background-color: #e5e7eb;
  color: #165dff;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 股票头部样式（现代化，渐变背景） */
.stock-header {
  background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--gray-200);
  box-shadow: var(--shadow-md);
  border-radius: var(--border-radius) var(--border-radius) 0 0;
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

/* 卡片样式（现代化精致，玻璃态效果） */
.card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(10px);
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-3px);
  border-color: rgba(255, 255, 255, 0.4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
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

/* 快速指标样式（现代化网格，悬浮效果） */
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
    grid-template-columns: repeat(6, 1fr);
  }
}

.metric-item {
  background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
  border: 1px solid var(--gray-200);
  border-radius: var(--border-radius);
  padding: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.metric-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.metric-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.metric-item:hover::before {
  transform: scaleX(1);
}

.metric-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
  font-weight: 500;
  text-transform: none;
  letter-spacing: normal;
}

.metric-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

/* 信息网格样式（现代化） */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  padding: 0.375rem 0;
  border-bottom: 1px solid var(--gray-100);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  font-weight: 500;
  margin-bottom: 0.125rem;
}

.info-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}



/* 笔记相关样式（紧凑） */
.notes-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 220px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.note-item {
  padding: 0.625rem;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
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
  font-size: 0.8125rem;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.note-meta {
  font-size: 0.6875rem;
  color: #6b7280;
  margin-top: 0.125rem;
  display: flex;
  justify-content: space-between;
}

.note-content {
  font-size: 0.75rem;
  color: #4b5563;
  margin-top: 0.375rem;
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
  padding: 0.625rem 0.75rem;
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
    min-height: 80px;
    resize: vertical;
  }
  
  /* 为利好利空分析区域的文本框设置更大的字体 */
  .pros-area .form-textarea,
  .cons-area .form-textarea {
    font-size: 1.25rem; /* text-xl 对应的大小 */
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

/* 竞争对手样式（现代化，卡片式） */
.competitor-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.competitor-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
  border: 1px solid var(--gray-200);
  border-radius: var(--border-radius);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  box-shadow: var(--shadow-sm);
}

.competitor-item:hover {
  background: linear-gradient(135deg, var(--primary-light), var(--bg-card));
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.competitor-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.competitor-rank {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-light);
  color: var(--primary-color);
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
}

.competitor-details {
  min-width: 0;
}

.competitor-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.competitor-code {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  margin-top: 0.125rem;
}

.competitor-action {
  font-size: 0.75rem;
  color: var(--primary-color);
  font-weight: 500;
}

/* 财务趋势图表样式（现代化） */
.chart-group {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chart-container {
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 1rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--gray-200);
  position: relative;
  height: 200px;
  width: 100%;
}

.chart-subtitle {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

/* 利好利空与总结样式 */
.pros-cons-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
</style>