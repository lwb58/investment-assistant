# 行业估值分析系统功能模块设计

## 1. 模块概述

行业估值分析系统是投资辅助系统的核心功能模块之一，旨在为投资者提供全面、深入的行业估值分析工具。该模块通过收集和分析各行业的基本面数据、估值指标、历史表现和市场预期等信息，帮助投资者识别被低估或高估的行业，发现潜在的投资机会，并为投资决策提供科学依据。

### 1.1 核心价值

- **行业对比分析**: 提供多维度、多指标的行业估值对比
- **历史趋势分析**: 追踪行业估值的历史变化趋势
- **估值合理区间判断**: 基于历史数据和行业特性判断当前估值水平
- **投资机会识别**: 自动标记潜在的投资机会和风险
- **数据可视化**: 通过丰富的图表直观展示行业估值数据

### 1.2 功能范围

- 行业列表与分类管理
- 行业基本信息展示
- 多维度估值指标分析
- 历史估值走势分析
- 行业对比分析
- 估值合理区间判断
- 投资机会预警
- 个性化设置与偏好管理

## 2. 功能模块详细设计

### 2.1 行业概览模块

#### 2.1.1 功能描述

行业概览模块提供所有行业的概览信息，包括行业分类、主要估值指标、涨跌幅等关键信息，用户可以快速浏览和筛选感兴趣的行业。

#### 2.1.2 详细功能点

1. **行业列表展示**
   - 显示所有行业列表，包含行业名称、代码、涨跌幅、总市值等基本信息
   - 支持按行业分类（证监会、申万、中信等分类标准）筛选
   - 支持按涨跌幅、总市值、PE、PB等指标排序
   - 支持搜索功能，快速定位特定行业

2. **估值指标概览**
   - 显示每个行业的核心估值指标：PE(TTM)、PB、PS、PCF、ROE等
   - 提供估值指标的历史分位点显示
   - 提供估值指标的行业间对比功能

3. **行业分类切换**
   - 支持多种行业分类标准的切换：证监会行业分类、申万行业分类、中信行业分类等
   - 提供行业层级结构展示

4. **快速筛选功能**
   - 提供基于估值水平的快速筛选：低估值、正常估值、高估值
   - 提供基于市场表现的快速筛选：涨幅榜、跌幅榜、换手率榜

#### 2.1.3 界面原型

```vue
<template>
  <div class="industry-overview">
    <!-- 筛选和搜索区域 -->
    <div class="filter-section">
      <el-select v-model="selectedClassification" placeholder="选择行业分类">
        <el-option label="申万行业" value="sw"></el-option>
        <el-option label="中信行业" value="zx"></el-option>
        <el-option label="证监会行业" value="zjh"></el-option>
      </el-select>
      
      <el-select v-model="sortBy" placeholder="排序方式">
        <el-option label="涨跌幅" value="changePercent"></el-option>
        <el-option label="PE(TTM)" value="pe"></el-option>
        <el-option label="PB" value="pb"></el-option>
        <el-option label="总市值" value="totalMarketCap"></el-option>
      </el-select>
      
      <el-input v-model="searchKeyword" placeholder="搜索行业" prefix-icon="el-icon-search"></el-input>
      
      <el-button-group>
        <el-button type="primary" size="small">低估值</el-button>
        <el-button size="small">正常估值</el-button>
        <el-button size="small">高估值</el-button>
      </el-button-group>
    </div>
    
    <!-- 行业列表表格 -->
    <el-table 
      :data="filteredIndustries" 
      style="width: 100%"
      @row-click="handleIndustryClick"
    >
      <el-table-column prop="name" label="行业名称" width="180"></el-table-column>
      <el-table-column prop="code" label="行业代码" width="100"></el-table-column>
      <el-table-column prop="changePercent" label="涨跌幅" width="100">
        <template #default="scope">
          <span :class="scope.row.changePercent >= 0 ? 'text-red' : 'text-green'">
            {{ scope.row.changePercent >= 0 ? '+' : '' }}{{ scope.row.changePercent.toFixed(2) }}%
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="pe" label="PE(TTM)" width="100"></el-table-column>
      <el-table-column prop="pePercentile" label="PE分位点" width="120">
        <template #default="scope">
          <div class="percentile-container">
            <div class="percentile-bar" :style="{ width: scope.row.pePercentile + '%' }"></div>
            <span>{{ scope.row.pePercentile }}%</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="pb" label="PB" width="100"></el-table-column>
      <el-table-column prop="pbPercentile" label="PB分位点" width="120">
        <template #default="scope">
          <div class="percentile-container">
            <div class="percentile-bar" :style="{ width: scope.row.pbPercentile + '%' }"></div>
            <span>{{ scope.row.pbPercentile }}%</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="totalMarketCap" label="总市值(亿)" width="120"></el-table-column>
      <el-table-column prop="valuationStatus" label="估值状态" width="100">
        <template #default="scope">
          <el-tag :type="getTagType(scope.row.valuationStatus)">
            {{ scope.row.valuationStatus }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
```

### 2.2 行业详情模块

#### 2.2.1 功能描述

行业详情模块提供单个行业的详细估值分析，包括行业基本信息、详细估值指标、历史估值走势、行业成分股表现等信息，帮助用户深入了解特定行业的估值状况。

#### 2.2.2 详细功能点

1. **行业基本信息**
   - 行业名称、代码、分类
   - 行业总市值、成交量、成交额
   - 行业涨跌幅及排名
   - 行业简介

2. **估值指标详情**
   - 详细展示各项估值指标：PE(TTM)、PE(LYR)、PB、PS、PCF、EV/EBITDA等
   - 提供估值指标的历史分位点（5年、10年）
   - 显示估值指标的行业平均值、中位数、最大值、最小值等统计数据
   - 提供估值指标的同业对比功能

3. **历史估值走势**
   - 展示行业主要估值指标的历史走势图表
   - 支持不同时间周期选择：1年、3年、5年、10年、全部
   - 支持多指标叠加显示
   - 支持与大盘估值走势对比

4. **行业成分股分析**
   - 展示行业内主要成分股列表
   - 显示成分股市值占比、估值分布
   - 支持成分股筛选和排序
   - 提供成分股估值对比功能

5. **行业估值评估**
   - 基于历史数据和行业特性，提供行业当前估值水平的评估
   - 给出估值合理区间建议
   - 提供投资风险提示

#### 2.2.3 界面原型

```vue
<template>
  <div class="industry-detail">
    <!-- 行业基本信息卡片 -->
    <el-card class="basic-info-card">
      <div class="industry-header">
        <h2>{{ industry.name }}</h2>
        <span class="industry-code">{{ industry.code }}</span>
      </div>
      <div class="industry-meta">
        <span class="classification">{{ industry.classification }}行业</span>
        <span class="update-time">更新时间: {{ industry.updateTime }}</span>
      </div>
      <div class="industry-summary">
        <div class="summary-item">
          <span class="label">总市值</span>
          <span class="value">{{ formatMarketCap(industry.totalMarketCap) }}亿元</span>
        </div>
        <div class="summary-item">
          <span class="label">涨跌幅</span>
          <span class="value" :class="industry.changePercent >= 0 ? 'text-red' : 'text-green'">
            {{ industry.changePercent >= 0 ? '+' : '' }}{{ industry.changePercent.toFixed(2) }}%
          </span>
        </div>
        <div class="summary-item">
          <span class="label">成交量</span>
          <span class="value">{{ formatVolume(industry.volume) }}</span>
        </div>
        <div class="summary-item">
          <span class="label">成交额</span>
          <span class="value">{{ formatAmount(industry.amount) }}亿元</span>
        </div>
      </div>
    </el-card>
    
    <!-- 估值指标卡片 -->
    <el-card class="valuation-indicators-card">
      <template #header>
        <div class="card-header">
          <span>估值指标</span>
        </div>
      </template>
      
      <div class="indicators-grid">
        <div class="indicator-item">
          <div class="indicator-name">PE(TTM)</div>
          <div class="indicator-value">{{ industry.pe.toFixed(2) }}</div>
          <div class="indicator-percentile">
            <div class="percentile-bar" :style="{ width: industry.pePercentile + '%' }"></div>
            <span>历史分位点: {{ industry.pePercentile }}%</span>
          </div>
        </div>
        <div class="indicator-item">
          <div class="indicator-name">PB</div>
          <div class="indicator-value">{{ industry.pb.toFixed(2) }}</div>
          <div class="indicator-percentile">
            <div class="percentile-bar" :style="{ width: industry.pbPercentile + '%' }"></div>
            <span>历史分位点: {{ industry.pbPercentile }}%</span>
          </div>
        </div>
        <div class="indicator-item">
          <div class="indicator-name">PS(TTM)</div>
          <div class="indicator-value">{{ industry.ps.toFixed(2) }}</div>
          <div class="indicator-percentile">
            <div class="percentile-bar" :style="{ width: industry.psPercentile + '%' }"></div>
            <span>历史分位点: {{ industry.psPercentile }}%</span>
          </div>
        </div>
        <div class="indicator-item">
          <div class="indicator-name">PCF(TTM)</div>
          <div class="indicator-value">{{ industry.pcf.toFixed(2) }}</div>
          <div class="indicator-percentile">
            <div class="percentile-bar" :style="{ width: industry.pcfPercentile + '%' }"></div>
            <span>历史分位点: {{ industry.pcfPercentile }}%</span>
          </div>
        </div>
        <div class="indicator-item">
          <div class="indicator-name">ROE(TTM)</div>
          <div class="indicator-value">{{ industry.roe.toFixed(2) }}%</div>
          <div class="indicator-percentile">
            <div class="percentile-bar" :style="{ width: industry.roePercentile + '%' }"></div>
            <span>历史分位点: {{ industry.roePercentile }}%</span>
          </div>
        </div>
        <div class="indicator-item">
          <div class="indicator-name">EV/EBITDA</div>
          <div class="indicator-value">{{ industry.evToEbitda.toFixed(2) }}</div>
          <div class="indicator-percentile">
            <div class="percentile-bar" :style="{ width: industry.evToEbitdaPercentile + '%' }"></div>
            <span>历史分位点: {{ industry.evToEbitdaPercentile }}%</span>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 估值评估卡片 -->
    <el-card class="valuation-assessment-card">
      <template #header>
        <div class="card-header">
          <span>估值评估</span>
        </div>
      </template>
      
      <div class="assessment-content">
        <div class="valuation-status">
          <h3>当前估值状态：</h3>
          <el-tag :type="getValuationTagType(industry.valuationStatus)" size="large">
            {{ industry.valuationStatus }}
          </el-tag>
        </div>
        
        <div class="valuation-range">
          <h3>合理估值区间：</h3>
          <div class="range-info">
            <span>PE合理区间：{{ industry.peReasonableMin.toFixed(2) }} - {{ industry.peReasonableMax.toFixed(2) }}</span>
            <span>PB合理区间：{{ industry.pbReasonableMin.toFixed(2) }} - {{ industry.pbReasonableMax.toFixed(2) }}</span>
          </div>
        </div>
        
        <div class="valuation-comments">
          <h3>估值分析：</h3>
          <p>{{ industry.valuationComments }}</p>
        </div>
        
        <div class="risk-tips">
          <h3>风险提示：</h3>
          <ul>
            <li v-for="tip in industry.riskTips" :key="tip">{{ tip }}</li>
          </ul>
        </div>
      </div>
    </el-card>
    
    <!-- 历史估值走势图 -->
    <el-card class="historical-trend-card">
      <template #header>
        <div class="card-header">
          <span>历史估值走势</span>
          <div class="time-range-selector">
            <el-radio-group v-model="timeRange" size="small">
              <el-radio-button label="1Y">1年</el-radio-button>
              <el-radio-button label="3Y">3年</el-radio-button>
              <el-radio-button label="5Y">5年</el-radio-button>
              <el-radio-button label="10Y">10年</el-radio-button>
              <el-radio-button label="ALL">全部</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      
      <div class="chart-container">
        <line-chart :data="historicalData" :options="chartOptions"></line-chart>
      </div>
    </el-card>
    
    <!-- 行业成分股列表 -->
    <el-card class="constituent-stocks-card">
      <template #header>
        <div class="card-header">
          <span>行业成分股</span>
          <span class="stock-count">(共{{ constituentStocks.length }}只)</span>
        </div>
      </template>
      
      <el-table 
        :data="constituentStocks" 
        style="width: 100%"
        @row-click="handleStockClick"
      >
        <el-table-column prop="code" label="股票代码" width="100"></el-table-column>
        <el-table-column prop="name" label="股票名称" width="120"></el-table-column>
        <el-table-column prop="price" label="价格" width="100"></el-table-column>
        <el-table-column prop="changePercent" label="涨跌幅" width="100">
          <template #default="scope">
            <span :class="scope.row.changePercent >= 0 ? 'text-red' : 'text-green'">
              {{ scope.row.changePercent >= 0 ? '+' : '' }}{{ scope.row.changePercent.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="pe" label="PE(TTM)" width="100"></el-table-column>
        <el-table-column prop="pb" label="PB" width="100"></el-table-column>
        <el-table-column prop="marketCap" label="市值(亿)" width="120"></el-table-column>
        <el-table-column prop="weight" label="权重(%)" width="100"></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
```

### 2.3 行业对比分析模块

#### 2.3.1 功能描述

行业对比分析模块允许用户选择多个行业进行多维度对比分析，通过表格、图表等方式直观展示各行业在不同估值指标上的差异，帮助用户识别行业间的相对估值水平和投资机会。

#### 2.3.2 详细功能点

1. **多行业选择**
   - 支持从行业列表中选择多个行业进行对比（最多支持8个行业）
   - 提供常用行业组合的快速选择
   - 支持保存和加载自定义的行业组合

2. **估值指标对比**
   - 表格形式展示各行业的估值指标对比
   - 支持自定义选择需要对比的指标
   - 提供指标排序和高亮显示功能

3. **估值走势对比图表**
   - 多行业估值走势折线图对比
   - 支持不同时间周期选择
   - 支持多指标切换显示

4. **估值热力图**
   - 以热力图形式直观展示多行业多指标的对比
   - 支持颜色深浅自定义
   - 支持指标权重调整

5. **对比报告生成**
   - 自动生成行业对比分析报告
   - 提供关键发现和投资建议
   - 支持导出PDF或Excel格式

#### 2.3.3 界面原型

```vue
<template>
  <div class="industry-comparison">
    <!-- 行业选择区域 -->
    <div class="industry-selection">
      <h3>选择对比行业</h3>
      <el-select 
        v-model="selectedIndustries" 
        multiple 
        collapse-tags 
        placeholder="请选择行业"
        style="width: 100%"
        @change="handleIndustriesChange"
      >
        <el-option 
          v-for="industry in allIndustries" 
          :key="industry.code" 
          :label="industry.name" 
          :value="industry"
        ></el-option>
      </el-select>
      
      <div class="quick-selections">
        <span class="quick-label">快速选择：</span>
        <el-button size="small" @click="selectTraditionalIndustries">传统行业</el-button>
        <el-button size="small" @click="selectEmergingIndustries">新兴行业</el-button>
        <el-button size="small" @click="selectFinancialIndustries">金融行业</el-button>
      </div>
    </div>
    
    <!-- 估值指标对比表格 -->
    <el-card v-if="selectedIndustries.length > 0" class="comparison-table-card">
      <template #header>
        <div class="card-header">
          <span>估值指标对比</span>
          <el-dropdown>
            <span class="el-dropdown-link">
              选择指标 <i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-checkbox-group v-model="selectedIndicators">
                  <el-dropdown-item><el-checkbox label="pe">PE(TTM)</el-checkbox></el-dropdown-item>
                  <el-dropdown-item><el-checkbox label="pb">PB</el-checkbox></el-dropdown-item>
                  <el-dropdown-item><el-checkbox label="ps">PS(TTM)</el-checkbox></el-dropdown-item>
                  <el-dropdown-item><el-checkbox label="pcf">PCF(TTM)</el-checkbox></el-dropdown-item>
                  <el-dropdown-item><el-checkbox label="roe">ROE(TTM)</el-checkbox></el-dropdown-item>
                  <el-dropdown-item><el-checkbox label="evToEbitda">EV/EBITDA</el-checkbox></el-dropdown-item>
                </el-checkbox-group>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>
      
      <el-table :data="comparisonData" style="width: 100%">
        <el-table-column prop="industryName" label="行业名称" width="150"></el-table-column>
        <el-table-column v-for="indicator in selectedIndicators" :key="indicator" :label="getIndicatorLabel(indicator)">
          <template #default="scope">
            <div class="comparison-cell">
              <span class="value">{{ formatValue(scope.row[indicator], indicator) }}</span>
              <span class="percentile" v-if="scope.row[indicator + 'Percentile'] !== undefined">
                ({{ scope.row[indicator + 'Percentile'] }}%)
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="估值状态">
          <template #default="scope">
            <el-tag :type="getValuationTagType(scope.row.valuationStatus)">
              {{ scope.row.valuationStatus }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 估值走势对比图表 -->
    <el-card v-if="selectedIndustries.length > 0" class="comparison-chart-card">
      <template #header>
        <div class="card-header">
          <span>估值走势对比</span>
          <div class="chart-controls">
            <el-select v-model="comparisonIndicator" placeholder="选择指标" size="small">
              <el-option label="PE(TTM)" value="pe"></el-option>
              <el-option label="PB" value="pb"></el-option>
              <el-option label="PS(TTM)" value="ps"></el-option>
              <el-option label="ROE(TTM)" value="roe"></el-option>
            </el-select>
            <el-select v-model="comparisonTimeRange" placeholder="时间范围" size="small">
              <el-option label="1年" value="1Y"></el-option>
              <el-option label="3年" value="3Y"></el-option>
              <el-option label="5年" value="5Y"></el-option>
            </el-select>
          </div>
        </div>
      </template>
      
      <div class="chart-container">
        <line-chart :data="comparisonChartData" :options="comparisonChartOptions"></line-chart>
      </div>
    </el-card>
    
    <!-- 估值热力图 -->
    <el-card v-if="selectedIndustries.length > 0" class="heatmap-card">
      <template #header>
        <div class="card-header">
          <span>估值热力图</span>
        </div>
      </template>
      
      <div class="chart-container">
        <heatmap-chart :data="heatmapData" :options="heatmapOptions"></heatmap-chart>
      </div>
    </el-card>
    
    <!-- 对比分析报告 -->
    <el-card v-if="selectedIndustries.length > 0" class="analysis-report-card">
      <template #header>
        <div class="card-header">
          <span>对比分析报告</span>
          <el-button size="small" @click="generateReport">生成报告</el-button>
        </div>
      </template>
      
      <div class="report-content" v-if="analysisReport">
        <h3>主要发现</h3>
        <ul>
          <li v-for="finding in analysisReport.keyFindings" :key="finding">{{ finding }}</li>
        </ul>
        
        <h3>行业排序</h3>
        <div v-for="(ranking, indicator) in analysisReport.rankings" :key="indicator" class="ranking-section">
          <h4>{{ getIndicatorLabel(indicator) }} 排序：</h4>
          <ul>
            <li v-for="(item, index) in ranking" :key="item.industryName">
              {{ index + 1 }}. {{ item.industryName }} ({{ formatValue(item.value, indicator) }})
            </li>
          </ul>
        </div>
        
        <h3>投资建议</h3>
        <div class="investment-suggestions">
          <p>{{ analysisReport.investmentSuggestions }}</p>
        </div>
      </div>
    </el-card>
  </div>
</template>
```

### 2.4 估值预警模块

#### 2.4.1 功能描述

估值预警模块监控用户关注行业的估值变化，当行业估值达到用户设定的阈值或出现异常波动时，系统自动发出预警通知，帮助用户及时把握投资机会或规避风险。

#### 2.4.2 详细功能点

1. **关注行业管理**
   - 用户可以添加和删除关注的行业
   - 显示关注行业列表及其当前估值状态
   - 支持批量管理关注行业

2. **预警规则设置**
   - 支持设置多种预警规则：估值突破历史分位点、估值达到合理区间边界、估值异常波动等
   - 支持为每个行业设置不同的预警阈值
   - 提供常用预警规则模板

3. **预警通知**
   - 实时监控行业估值变化
   - 当满足预警条件时，系统自动发送通知
   - 支持多种通知方式：站内信、邮件、短信（后续扩展）

4. **预警历史记录**
   - 记录所有预警历史
   - 提供预警历史查询和筛选功能
   - 支持查看预警触发时的行业状态详情

#### 2.4.3 界面原型

```vue
<template>
  <div class="valuation-alert">
    <!-- 预警设置面板 -->
    <el-card class="alert-settings-card">
      <template #header>
        <div class="card-header">
          <span>预警设置</span>
        </div>
      </template>
      
      <div class="settings-content">
        <h3>关注行业</h3>
        <div class="watched-industries">
          <el-select 
            v-model="watchedIndustries" 
            multiple 
            collapse-tags 
            placeholder="请选择要关注的行业"
            style="width: 100%"
          >
            <el-option 
              v-for="industry in allIndustries" 
              :key="industry.code" 
              :label="industry.name" 
              :value="industry"
            ></el-option>
          </el-select>
          <el-button type="primary" size="small" @click="saveWatchedIndustries">保存</el-button>
        </div>
        
        <h3>预警规则</h3>
        <div class="alert-rules">
          <el-collapse v-model="activeRules">
            <el-collapse-item title="估值分位点预警" name="percentile">
              <el-form :model="percentileAlertRule">
                <el-form-item label="PE分位点下限">
                  <el-slider v-model="percentileAlertRule.peLowerBound" :min="0" :max="100" show-stops></el-slider>
                  <span>{{ percentileAlertRule.peLowerBound }}%</span>
                </el-form-item>
                <el-form-item label="PE分位点上限">
                  <el-slider v-model="percentileAlertRule.peUpperBound" :min="0" :max="100" show-stops></el-slider>
                  <span>{{ percentileAlertRule.peUpperBound }}%</span>
                </el-form-item>
                <el-form-item label="PB分位点下限">
                  <el-slider v-model="percentileAlertRule.pbLowerBound" :min="0" :max="100" show-stops></el-slider>
                  <span>{{ percentileAlertRule.pbLowerBound }}%</span>
                </el-form-item>
                <el-form-item label="PB分位点上限">
                  <el-slider v-model="percentileAlertRule.pbUpperBound" :min="0" :max="100" show-stops></el-slider>
                  <span>{{ percentileAlertRule.pbUpperBound }}%</span>
                </el-form-item>
              </el-form>
            </el-collapse-item>
            
            <el-collapse-item title="估值波动预警" name="volatility">
              <el-form :model="volatilityAlertRule">
                <el-form-item label="日波动幅度阈值">
                  <el-input-number v-model="volatilityAlertRule.dailyChangeThreshold" :min="0" :max="100" :step="0.1"></el-input-number>
                  <span>%</span>
                </el-form-item>
                <el-form-item label="周波动幅度阈值">
                  <el-input-number v-model="volatilityAlertRule.weeklyChangeThreshold" :min="0" :max="100" :step="0.1"></el-input-number>
                  <span>%</span>
                </el-form-item>
              </el-form>
            </el-collapse-item>
            
            <el-collapse-item title="估值状态变化预警" name="status">
              <el-form :model="statusAlertRule">
                <el-form-item label="状态变化通知">
                  <el-checkbox-group v-model="statusAlertRule.statusChanges">
                    <el-checkbox label="低估值→正常估值">低估值→正常估值</el-checkbox>
                    <el-checkbox label="正常估值→低估值">正常估值→低估值</el-checkbox>
                    <el-checkbox label="正常估值→高估值">正常估值→高估值</el-checkbox>
                    <el-checkbox label="高估值→正常估值">高估值→正常估值</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </el-form>
            </el-collapse-item>
          </el-collapse>
          
          <el-button type="primary" size="small" @click="saveAlertRules">保存预警规则</el-button>
        </div>
        
        <h3>通知方式</h3>
        <div class="notification-settings">
          <el-checkbox-group v-model="notificationMethods">
            <el-checkbox label="站内信">站内信</el-checkbox>
            <el-checkbox label="邮件">邮件</el-checkbox>
            <el-checkbox label="短信">短信 (未启用)</el-checkbox>
          </el-checkbox-group>
          <el-button type="primary" size="small" @click="saveNotificationSettings">保存通知设置</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 预警历史记录 -->
    <el-card class="alert-history-card">
      <template #header>
        <div class="card-header">
          <span>预警历史记录</span>
          <div class="history-filters">
            <el-date-picker
              v-model="alertDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              size="small"
            ></el-date-picker>
            <el-select v-model="alertTypeFilter" placeholder="预警类型" size="small">
              <el-option label="全部" value=""></el-option>
              <el-option label="估值分位点预警" value="percentile"></el-option>
              <el-option label="估值波动预警" value="volatility"></el-option>
              <el-option label="估值状态变化预警" value="status"></el-option>
            </el-select>
          </div>
        </div>
      </template>
      
      <el-table :data="filteredAlertHistory" style="width: 100%">
        <el-table-column prop="time" label="预警时间" width="180"></el-table-column>
        <el-table-column prop="industryName" label="行业名称" width="120"></el-table-column>
        <el-table-column prop="type" label="预警类型" width="150"></el-table-column>
        <el-table-column prop="message" label="预警消息"></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '已读' ? 'success' : 'warning'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="text" size="small" @click="viewAlertDetails(scope.row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="alertHistory.length"
        ></el-pagination>
      </div>
    </el-card>
  </div>
</template>
```

## 3. 数据模型设计

### 3.1 核心数据结构

#### 3.1.1 行业基本信息

```typescript
interface IndustryBaseInfo {
  id: string;              // 行业唯一标识
  code: string;            // 行业代码
  name: string;            // 行业名称
  classification: string;  // 分类标准（申万、中信、证监会等）
  level: number;           // 行业层级（一级、二级、三级）
  parentCode?: string;     // 父行业代码
  description?: string;    // 行业描述
  createTime: string;      // 创建时间
  updateTime: string;      // 更新时间
}
```

#### 3.1.2 行业估值数据

```typescript
interface IndustryValuationData {
  industryId: string;           // 行业ID
  date: string;                 // 数据日期
  pe: number;                   // 市盈率(TTM)
  peLyr: number;                // 市盈率(LYR)
  pb: number;                   // 市净率
  ps: number;                   // 市销率(TTM)
  pcf: number;                  // 市现率(TTM)
  evToEbitda: number;           // EV/EBITDA
  roe: number;                  // 净资产收益率(TTM)
  dividendYield: number;        // 股息率
  totalMarketCap: number;       // 总市值(亿元)
  circulationMarketCap: number; // 流通市值(亿元)
  volume: number;               // 成交量(万手)
  amount: number;               // 成交额(亿元)
  changePercent: number;        // 涨跌幅(%)
  pePercentile: number;         // PE历史分位点(%)
  pbPercentile: number;         // PB历史分位点(%)
  psPercentile: number;         // PS历史分位点(%)
  pcfPercentile: number;        // PCF历史分位点(%)
  roePercentile: number;        // ROE历史分位点(%)
  evToEbitdaPercentile: number; // EV/EBITDA历史分位点(%)
  valuationStatus: '低估值' | '正常估值' | '高估值'; // 估值状态
  peReasonableMin: number;      // PE合理区间下限
  peReasonableMax: number;      // PE合理区间上限
  pbReasonableMin: number;      // PB合理区间下限
  pbReasonableMax: number;      // PB合理区间上限
  valuationComments?: string;   // 估值分析评论
  riskTips?: string[];          // 风险提示
}
```

#### 3.1.3 行业成分股数据

```typescript
interface IndustryConstituentStock {
  industryId: string;   // 行业ID
  stockCode: string;    // 股票代码
  stockName: string;    // 股票名称
  weight: number;       // 权重(%)
  price: number;        // 最新价格
  changePercent: number;// 涨跌幅(%)
  pe: number;           // 市盈率(TTM)
  pb: number;           // 市净率
  marketCap: number;    // 市值(亿元)
  isCore: boolean;      // 是否为核心成分股
}
```

#### 3.1.4 行业历史估值数据

```typescript
interface IndustryHistoricalValuation {
  industryId: string;  // 行业ID
  date: string;        // 日期
  pe: number;          // PE(TTM)
  pb: number;          // PB
  ps: number;          // PS(TTM)
  pcf: number;         // PCF(TTM)
  roe: number;         // ROE(TTM)
  evToEbitda: number;  // EV/EBITDA
  marketCap: number;   // 总市值(亿元)
}
```

#### 3.1.5 预警规则数据

```typescript
interface AlertRule {
  id: string;                    // 规则ID
  userId: string;                // 用户ID
  type: 'percentile' | 'volatility' | 'status'; // 规则类型
  name: string;                  // 规则名称
  description?: string;          // 规则描述
  settings: {
    // 根据type不同，这里的字段会有所不同
    peLowerBound?: number;       // PE分位点下限
    peUpperBound?: number;       // PE分位点上限
    pbLowerBound?: number;       // PB分位点下限
    pbUpperBound?: number;       // PB分位点上限
    dailyChangeThreshold?: number; // 日波动幅度阈值
    weeklyChangeThreshold?: number; // 周波动幅度阈值
    statusChanges?: string[];    // 状态变化类型
  };
  watchedIndustries: string[];   // 监控的行业ID列表
  notificationMethods: string[]; // 通知方式
  isEnabled: boolean;            // 是否启用
  createTime: string;            // 创建时间
  updateTime: string;            // 更新时间
}
```

#### 3.1.6 预警历史数据

```typescript
interface AlertHistory {
  id: string;              // 预警ID
  ruleId: string;          // 触发的规则ID
  industryId: string;      // 相关行业ID
  industryName: string;    // 行业名称
  type: string;            // 预警类型
  message: string;         // 预警消息
  details?: any;           // 详细信息
  status: '已读' | '未读';  // 状态
  createTime: string;      // 创建时间
  readTime?: string;       // 阅读时间
}
```

### 3.2 数据存储方案

#### 3.2.1 MySQL存储

- **industry_basic_info**: 存储行业基本信息
- **industry_classifications**: 存储行业分类标准
- **user_watched_industries**: 存储用户关注的行业
- **alert_rules**: 存储用户设置的预警规则
- **alert_history**: 存储预警历史记录

#### 3.2.2 MongoDB存储

- **industry_valuation_daily**: 存储行业每日估值数据
- **industry_historical_valuations**: 存储行业历史估值数据，用于趋势分析
- **industry_constituent_stocks**: 存储行业成分股信息
- **industry_comparison_reports**: 存储生成的行业对比分析报告

#### 3.2.3 Redis缓存

- **industry:valuation:latest**: 缓存最新的行业估值数据，TTL为1小时
- **industry:constituent:latest**: 缓存最新的行业成分股数据，TTL为1小时
- **industry:comparison:result**: 缓存行业对比结果，TTL为24小时
- **alert:trigger:queue**: 预警触发队列

## 4. API接口设计

### 4.1 行业基本信息接口

#### 4.1.1 获取行业分类列表

```http
GET /api/v1/industries/classifications
Description: 获取支持的行业分类标准列表
Parameters: 无
Response:
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "code": "sw",
      "name": "申万行业",
      "levels": 3
    },
    {
      "code": "zx",
      "name": "中信行业",
      "levels": 3
    },
    {
      "code": "zjh",
      "name": "证监会行业",
      "levels": 2
    }
  ]
}
```

#### 4.1.2 获取行业列表

```http
GET /api/v1/industries
Description: 获取行业列表
Parameters:
  - classification: string (optional) 行业分类标准
  - level: number (optional) 行业层级
  - parentCode: string (optional) 父行业代码
  - keyword: string (optional) 搜索关键词
Response:
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "1",
      "code": "801010",
      "name": "农林牧渔",
      "classification": "sw",
      "level": 1,
      "description": "..."
    },
    ...
  ]
}
```

#### 4.1.3 获取行业详情

```http
GET /api/v1/industries/{industryId}
Description: 获取行业详细信息
Parameters: 无
Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "1",
    "code": "801010",
    "name": "农林牧渔",
    "classification": "sw",
    "level": 1,
    "description": "...",
    "updateTime": "2024-01-01 15:00:00"
  }
}
```

### 4.2 行业估值数据接口

#### 4.2.1 获取行业估值概览

```http
GET /api/v1/industries/valuation/overview
Description: 获取行业估值概览数据
Parameters:
  - classification: string (optional) 行业分类标准
  - sortBy: string (optional) 排序字段 (pe, pb, changePercent, etc.)
  - order: string (optional) 排序方向 (asc, desc)
  - keyword: string (optional) 搜索关键词
Response:
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "industryId": "1",
      "code": "801010",
      "name": "农林牧渔",
      "pe": 25.67,
      "pePercentile": 65,
      "pb": 2.13,
      "pbPercentile": 55,
      "totalMarketCap": 12345.67,
      "changePercent": 1.23,
      "valuationStatus": "正常估值"
    },
    ...
  ]
}
```

#### 4.2.2 获取行业估值详情

```http
GET /api/v1/industries/{industryId}/valuation
Description: 获取行业详细估值数据
Parameters: 无
Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "industryId": "1",
    "code": "801010",
    "name": "农林牧渔",
    "date": "2024-01-01",
    "pe": 25.67,
    "peLyr": 23.45,
    "pb": 2.13,
    "ps": 1.23,
    "pcf": 15.67,
    "evToEbitda": 12.34,
    "roe": 8.32,
    "dividendYield": 1.56,
    "totalMarketCap": 12345.67,
    "circulationMarketCap": 10234.56,
    "volume": 1234.56,
    "amount": 123.45,
    "changePercent": 1.23,
    "pePercentile": 65,
    "pbPercentile": 55,
    "psPercentile": 60,
    "pcfPercentile": 50,
    "roePercentile": 45,
    "evToEbitdaPercentile": 55,
    "valuationStatus": "正常估值",
    "peReasonableMin": 15.0,
    "peReasonableMax": 30.0,
    "pbReasonableMin": 1.5,
    "pbReasonableMax": 3.0,
    "valuationComments": "...",
    "riskTips": ["...", "..."]
  }
}
```

#### 4.2.3 获取行业历史估值数据

```http
GET /api/v1/industries/{industryId}/valuation/historical
Description: 获取行业历史估值数据
Parameters:
  - startDate: string (required) 开始日期，格式YYYY-MM-DD
  - endDate: string (required) 结束日期，格式YYYY-MM-DD
  - indicators: string (optional) 指标列表，逗号分隔 (pe,pb,ps,pcf,roe,evToEbitda)
Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "industryId": "1",
    "industryName": "农林牧渔",
    "dates": ["2023-01-01", "2023-01-02", ...],
    "series": [
      {
        "name": "PE(TTM)",
        "data": [23.45, 23.56, ...]
      },
      {
        "name": "PB",
        "data": [2.01, 2.02, ...]
      }
    ]
  }
}
```

### 4.3 行业成分股接口

#### 4.3.1 获取行业成分股列表

```http
GET /api/v1/industries/{industryId}/constituents
Description: 获取行业成分股列表
Parameters:
  - sortBy: string (optional) 排序字段 (marketCap, weight, pe, changePercent, etc.)
  - order: string (optional) 排序方向 (asc, desc)
Response:
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "stockCode": "600598",
      "stockName": "北大荒",
      "weight": 8.56,
      "price": 12.34,
      "changePercent": 2.34,
      "pe": 15.67,
      "pb": 1.89,
      "marketCap": 234.56,
      "isCore": true
    },
    ...
  ]
}
```

### 4.4 行业对比分析接口

#### 4.4.1 行业估值对比

```http
POST /api/v1/industries/comparison/valuation
Description: 对比多个行业的估值数据
Parameters:
  - industryIds: string[] (required) 行业ID列表
  - indicators: string[] (optional) 要对比的指标列表
Response:
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "industryId": "1",
      "industryName": "农林牧渔",
      "pe": 25.67,
      "pePercentile": 65,
      "pb": 2.13,
      "pbPercentile": 55,
      "ps": 1.23,
      "psPercentile": 60,
      "valuationStatus": "正常估值"
    },
    {
      "industryId": "2",
      "industryName": "采掘",
      "pe": 15.67,
      "pePercentile": 35,
      "pb": 1.89,
      "pbPercentile": 45,
      "ps": 1.45,
      "psPercentile": 40,
      "valuationStatus": "低估值"
    }
  ]
}
```

#### 4.4.2 行业历史估值对比

```http
POST /api/v1/industries/comparison/historical
Description: 对比多个行业的历史估值走势
Parameters:
  - industryIds: string[] (required) 行业ID列表
  - indicator: string (required) 对比指标 (pe, pb, ps, roe, etc.)
  - startDate: string (required) 开始日期
  - endDate: string (required) 结束日期
Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "dates": ["2023-01-01", "2023-01-02", ...],
    "series": [
      {
        "name": "农林牧渔",
        "data": [23.45, 23.56, ...]
      },
      {
        "name": "采掘",
        "data": [14.56, 14.67, ...]
      }
    ]
  }
}
```

#### 4.4.3 生成行业对比报告

```http
POST /api/v1/industries/comparison/report/generate
Description: 生成行业对比分析报告
Parameters:
  - industryIds: string[] (required) 行业ID列表
Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "reportId": "123456",
    "title": "行业估值对比分析报告",
    "generationTime": "2024-01-01 15:00:00",
    "keyFindings": [
      "农林牧渔行业当前PE为25.67，处于历史65%分位点，估值处于合理偏高水平",
      "采掘行业当前PE为15.67，处于历史35%分位点，估值处于较低水平"
    ],
    "rankings": {
      "pe": [
        { "industryId": "2", "industryName": "采掘", "value": 15.67 },
        { "industryId": "1", "industryName": "农林牧渔", "value": 25.67 }
      ],
      "pb": [
        { "industryId": "2", "industryName": "采掘", "value": 1.89 },
        { "industryId": "1", "industryName": "农林牧渔", "value": 2.13 }
      ]
    },
    "investmentSuggestions": "根据当前估值水平，采掘行业可能存在较好的投资机会，而农林牧渔行业估值相对较高，建议谨慎配置。"
  }
}
```

### 4.5 预警相关接口

#### 4.5.1 获取用户关注的行业

```http
GET /api/v1/user/industries/watched
Description: 获取用户关注的行业列表
Parameters: 无
Response:
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "industryId": "1",
      "code": "801010",
      "name": "农林牧渔",
      "valuationStatus": "正常估值",
      "pe": 25.67,
      "pePercentile": 65
    },
    ...
  ]
}
```

#### 4.5.2 设置用户关注的行业

```http
POST /api/v1/user/industries/watched
Description: 设置用户关注的行业
Parameters:
  - industryIds: string[] (required) 行业ID列表
Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 5
  }
}
```

#### 4.5.3 获取用户的预警规则

```http
GET /api/v1/user/alert/rules
Description: 获取用户设置的预警规则列表
Parameters: 无
Response:
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "1",
      "name": "低估值行业预警",
      "type": "percentile",
      "description": "当关注行业PE或PB分位点低于30%时预警",
      "settings": {
        "peLowerBound": 30,
        "pbLowerBound": 30
      },
      "watchedIndustries": ["1", "2", "3"],
      "notificationMethods": ["站内信", "邮件"],
      "isEnabled": true,
      "createTime": "2024-01-01 10:00:00",
      "updateTime": "2024-01-01 10:00:00"
    },
    ...
  ]
}
```

#### 4.5.4 创建预警规则

```http
POST /api/v1/user/alert/rules
Description: 创建新的预警规则
Parameters:
  - name: string (required) 规则名称
  - type: string (required) 规则类型
  - description: string (optional) 规则描述
  - settings: object (required) 规则设置
  - watchedIndustries: string[] (required) 监控的行业ID列表
  - notificationMethods: string[] (required) 通知方式
Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "2",
    "name": "高估值行业预警",
    "type": "percentile",
    "isEnabled": true
  }
}
```

#### 4.5.5 更新预警规则

```http
PUT /api/v1/user/alert/rules/{ruleId}
Description: 更新预警规则
Parameters:
  - name: string (optional) 规则名称
  - description: string (optional) 规则描述
  - settings: object (optional) 规则设置
  - watchedIndustries: string[] (optional) 监控的行业ID列表
  - notificationMethods: string[] (optional) 通知方式
  - isEnabled: boolean (optional) 是否启用
Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "2",
    "updateTime": "2024-01-01 16:00:00"
  }
}
```

#### 4.5.6 获取预警历史记录

```http
GET /api/v1/user/alert/history
Description: 获取用户的预警历史记录
Parameters:
  - startDate: string (optional) 开始日期
  - endDate: string (optional) 结束日期
  - type: string (optional) 预警类型
  - status: string (optional) 状态 (已读/未读)
  - page: number (optional) 页码
  - pageSize: number (optional) 每页大小
Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "1",
        "ruleId": "1",
        "industryId": "1",
        "industryName": "农林牧渔",
        "type": "估值分位点预警",
        "message": "农林牧渔行业PE分位点达到25%，低于设定阈值30%",
        "status": "已读",
        "createTime": "2024-01-01 14:30:00",
        "readTime": "2024-01-01 15:00:00"
      },
      ...
    ],
    "total": 25,
    "page": 1,
    "pageSize": 10
  }
}
```

## 5. 交互与用户体验设计

### 5.1 用户交互流程

#### 5.1.1 行业概览浏览流程

1. 用户进入行业估值分析系统主页
2. 系统默认展示申万一级行业的估值概览表格
3. 用户可以选择不同的行业分类标准
4. 用户可以根据需要选择排序字段和排序方向
5. 用户可以使用搜索功能快速定位特定行业
6. 用户可以点击快速筛选按钮（低估值、正常估值、高估值）快速筛选行业
7. 用户点击表格中的行业，进入行业详情页面

#### 5.1.2 行业详情查看流程

1. 用户从行业概览页面点击特定行业进入详情页面
2. 系统加载并展示行业基本信息、估值指标、估值评估等内容
3. 用户可以选择不同的时间周期查看历史估值走势
4. 用户可以浏览行业成分股列表，点击成分股可查看详细信息
5. 用户可以点击页面上的关注按钮，将该行业添加到关注列表

#### 5.1.3 行业对比分析流程

1. 用户从左侧菜单进入行业对比分析页面
2. 用户从行业选择器中选择要对比的行业（最多8个）
3. 用户可以使用快速选择功能，选择预设的行业组合
4. 系统实时更新对比表格和图表
5. 用户可以选择不同的估值指标进行对比
6. 用户可以调整时间范围查看历史估值对比
7. 用户可以点击生成报告按钮，获取详细的对比分析报告

#### 5.1.4 预警设置与管理流程

1. 用户从左侧菜单进入估值预警页面
2. 用户在关注行业部分选择要监控的行业
3. 用户设置预警规则，包括估值分位点预警、估值波动预警、估值状态变化预警等
4. 用户选择通知方式（站内信、邮件等）
5. 系统保存设置并开始监控
6. 当满足预警条件时，系统发送预警通知
7. 用户可以在预警历史记录中查看所有触发的预警

### 5.2 用户体验优化

#### 5.2.1 响应式设计

- 桌面端：完整展示所有功能模块，多列布局，充分利用屏幕空间
- 平板端：适当调整布局，保持核心功能，优化图表显示
- 移动端：简化布局，单列显示，优化触摸交互，保持核心数据可见

#### 5.2.2 数据可视化优化

- 使用直观的图表类型展示不同的数据特征
- 提供图表交互功能：缩放、平移、提示框、图例切换等
- 优化色彩选择，使用一致的配色方案
- 提供图表导出功能，支持PNG、JPG、PDF等格式

#### 5.2.3 加载与缓存优化

- 使用骨架屏减少加载等待感
- 实现分页加载和虚拟滚动，优化大数据量展示
- 缓存常用数据，减少重复请求
- 实现增量更新，只获取变化的数据

#### 5.2.4 个性化定制

- 允许用户自定义显示的估值指标
- 支持自定义行业组合和保存
- 允许用户设置个性化的预警规则
- 提供深色/浅色主题切换

## 6. 部署与集成方案

### 6.1 前端部署

- 使用Nginx作为静态资源服务器
- 前端构建产物部署到CDN加速访问
- 支持多环境配置：开发环境、测试环境、生产环境
- 使用Docker容器化部署，便于扩展和维护

### 6.2 后端集成

- 与用户认证系统集成，确保数据访问安全
- 与数据采集系统集成，定时获取最新的行业数据
- 与数据分析引擎集成，提供估值分析和预警功能
- 与通知系统集成，提供多渠道的预警通知

### 6.3 性能优化

- 使用Redis缓存热点数据，减少数据库查询压力
- 优化数据库查询，添加适当的索引
- 使用异步处理非实时任务，如报告生成、数据同步等
- 实现API接口限流，保护后端服务

### 6.4 监控与告警

- 集成Prometheus和Grafana监控系统性能
- 监控API调用情况，及时发现异常
- 监控数据更新情况，确保数据及时性
- 设置系统告警，在异常情况下及时通知运维人员

## 7. 安全性考虑

### 7.1 数据安全

- 敏感数据加密存储
- 数据传输使用HTTPS加密
- 实现细粒度的数据访问控制
- 定期进行数据备份

### 7.2 应用安全

- 防止SQL注入、XSS攻击等常见Web安全问题
- 实现CSRF防护
- 对API接口进行认证和授权
- 实施输入验证和数据清洗

### 7.3 用户隐私

- 遵守数据隐私保护法规
- 明确告知用户数据使用方式
- 提供用户数据管理功能（如删除个人数据）
- 匿名化处理统计数据

## 8. 后续扩展规划

### 8.1 功能扩展

- **智能估值分析**: 基于机器学习算法，提供更精准的估值分析和预测
- **行业景气度分析**: 整合宏观经济数据，分析行业景气度变化
- **产业链分析**: 提供产业链上下游分析，把握行业间关联关系
- **国际化支持**: 支持全球主要市场的行业估值分析
- **多维度对比**: 支持行业与大盘、行业与主题等多维度对比

### 8.2 技术升级

- **实时数据更新**: 使用WebSocket实现估值数据实时更新
- **大数据分析**: 引入大数据分析框架，处理更复杂的行业数据
- **增强现实(AR)展示**: 探索使用AR技术展示行业数据和趋势
- **语音交互**: 支持语音查询和分析行业数据
- **AI助手集成**: 集成AI助手，提供智能问答和分析建议

### 8.3 用户体验提升

- **个性化仪表盘**: 提供可自定义的行业监控仪表盘
- **协作功能**: 支持用户间共享分析结果和投资观点
- **移动应用**: 开发专用的移动应用，提供更好的移动体验
- **离线功能**: 支持部分功能离线使用
- **社交分享**: 支持分析结果分享到社交媒体平台