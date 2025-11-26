# 估值决策系统功能模块设计文档

## 1. 模块概述

估值决策系统是投资辅助系统的核心模块之一，负责基于多维度数据对上市公司进行科学、系统的估值分析，并提供投资决策支持。该模块整合市场数据、财务分析和行业估值等信息，应用多种估值模型，为投资者提供全面、客观的估值参考和决策建议。

### 1.1 设计目标

1. **多模型支持**：集成多种经典和现代估值模型
2. **数据驱动**：基于真实市场数据和财务数据进行计算
3. **灵活性**：支持参数自定义和模型调整
4. **决策辅助**：提供明确的投资建议和风险提示
5. **易用性**：复杂计算简单呈现，专业结果通俗解释

### 1.2 核心功能

1. **多模型估值分析**
   - 相对估值模型（PE、PB、PS等）
   - 绝对估值模型（DCF、DDM等）
   - 行业特定估值模型
   - 自定义估值模型

2. **投资决策支持**
   - 估值结果解读
   - 投资机会识别
   - 风险评估与提示
   - 投资建议生成

3. **投资组合管理**
   - 模拟投资组合构建
   - 组合风险收益分析
   - 组合优化建议
   - 投资组合回测

4. **投资策略研究**
   - 估值因子研究
   - 策略有效性分析
   - 策略回测与优化
   - 策略监控与调整

## 2. 功能模块设计

### 2.1 多模型估值分析

#### 2.1.1 功能描述

该模块支持多种估值模型的计算和分析，包括相对估值法、绝对估值法以及行业特定估值模型。用户可以选择单一模型或多种模型组合使用，系统将自动计算估值结果并进行对比分析。

#### 2.1.2 功能点

1. **相对估值模型**
   - PE估值法（市盈率）
   - PB估值法（市净率）
   - PS估值法（市销率）
   - PEG估值法（市盈率相对盈利增长比率）
   - EV/EBITDA估值法（企业价值倍数）
   - 相对估值模型横向对比

2. **绝对估值模型**
   - DCF估值法（自由现金流折现模型）
   - DDM估值法（股息贴现模型）
   - EVA估值法（经济增加值模型）
   - 绝对估值参数配置与敏感性分析

3. **行业特定估值模型**
   - 金融行业特定模型（PB、ROE结合）
   - 周期性行业特定模型（重置成本法）
   - 高科技行业特定模型（DCF+实物期权）
   - 医药行业特定模型（管线价值评估）

4. **自定义估值模型**
   - 模型参数配置
   - 模型组合与权重设置
   - 自定义公式支持
   - 模型保存与复用

5. **估值结果分析**
   - 多模型估值结果对比
   - 历史估值区间分析
   - 行业估值水平对比
   - 估值偏离度分析

#### 2.1.3 界面原型

```vue
<template>
  <div class="valuation-models">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>多模型估值分析</span>
          <el-select v-model="selectedStock" placeholder="选择股票" size="small">
            <el-option v-for="item in stockList" :key="item.code" :label="item.name" :value="item.code"></el-option>
          </el-select>
          <el-button type="primary" size="small" @click="calculateValuation">计算估值</el-button>
        </div>
      </template>
      
      <el-tabs>
        <el-tab-pane label="相对估值">
          <div class="valuation-params">
            <el-form :model="relativeValuationParams" label-width="100px">
              <el-form-item label="预测PE">
                <el-input-number v-model="relativeValuationParams.forecastPE" :min="0" :step="0.1" size="small"></el-input-number>
              </el-form-item>
              <el-form-item label="预测PB">
                <el-input-number v-model="relativeValuationParams.forecastPB" :min="0" :step="0.1" size="small"></el-input-number>
              </el-form-item>
              <el-form-item label="预测PS">
                <el-input-number v-model="relativeValuationParams.forecastPS" :min="0" :step="0.1" size="small"></el-input-number>
              </el-form-item>
              <el-form-item>
                <el-checkbox-group v-model="relativeValuationParams.selectedModels">
                  <el-checkbox label="PE模型" border></el-checkbox>
                  <el-checkbox label="PB模型" border></el-checkbox>
                  <el-checkbox label="PS模型" border></el-checkbox>
                  <el-checkbox label="PEG模型" border></el-checkbox>
                  <el-checkbox label="EV/EBITDA模型" border></el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-form>
          </div>
          
          <div class="valuation-results">
            <div class="result-chart">
              <div id="relativeValuationChart"></div>
            </div>
            
            <el-table :data="relativeValuationResults" border>
              <el-table-column prop="model" label="估值模型"></el-table-column>
              <el-table-column prop="fairValue" label="合理价值"></el-table-column>
              <el-table-column prop="currentPrice" label="当前价格"></el-table-column>
              <el-table-column prop="discountRate" label="偏离度(%)">
                <template #default="scope">
                  <span :class="scope.row.discountRate < 0 ? 'undervalued' : 'overvalued'">
                    {{ scope.row.discountRate.toFixed(2) }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="suggestion" label="投资建议"></el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="绝对估值">
          <div class="valuation-params">
            <el-form :model="dcfParams" label-width="120px">
              <el-form-item label="预测年限">
                <el-input-number v-model="dcfParams.forecastYears" :min="3" :max="10" size="small"></el-input-number>
              </el-form-item>
              <el-form-item label="加权平均资本成本(WACC)">
                <el-input-number v-model="dcfParams.wacc" :min="0" :max="1" :step="0.001" size="small"></el-input-number>
              </el-form-item>
              <el-form-item label="永续增长率">
                <el-input-number v-model="dcfParams.perpetualGrowthRate" :min="0" :max="0.1" :step="0.001" size="small"></el-input-number>
              </el-form-item>
              <el-form-item label="预测增长率">
                <el-input v-model="dcfParams.forecastGrowthRates" placeholder="逗号分隔，如：0.15,0.12,0.10,0.08" size="small"></el-input>
              </el-form-item>
            </el-form>
          </div>
          
          <div class="valuation-results">
            <div class="result-chart">
              <div id="dcfValuationChart"></div>
            </div>
            
            <el-table :data="dcfValuationResults" border>
              <el-table-column prop="item" label="项目"></el-table-column>
              <el-table-column prop="value" label="数值"></el-table-column>
              <el-table-column prop="explanation" label="说明" show-overflow-tooltip></el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="行业特定估值">
          <!-- 行业特定估值内容 -->
        </el-tab-pane>
        
        <el-tab-pane label="自定义估值">
          <!-- 自定义估值内容 -->
        </el-tab-pane>
        
        <el-tab-pane label="综合分析">
          <!-- 综合分析内容 -->
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>
```

### 2.2 投资决策支持

#### 2.2.1 功能描述

该模块基于估值分析结果，提供专业的投资决策支持，包括估值结果解读、投资机会识别、风险评估和投资建议生成，帮助投资者做出明智的投资决策。

#### 2.2.2 功能点

1. **估值结果解读**
   - 估值结果专业解读
   - 估值影响因素分析
   - 估值结果可信度评估
   - 估值方法论说明

2. **投资机会识别**
   - 低估股票筛选
   - 成长价值双优识别
   - 行业轮动机会分析
   - 特殊事件驱动机会

3. **风险评估与提示**
   - 估值风险分析
   - 下行风险测算
   - 敏感性分析
   - 风险因素清单

4. **投资建议生成**
   - 买入/持有/卖出建议
   - 目标价格区间
   - 建仓策略建议
   - 止损止盈建议

5. **决策报告生成**
   - 投资决策报告自动生成
   - 关键决策点标记
   - 报告导出与分享

#### 2.2.3 界面原型

```vue
<template>
  <div class="investment-decision">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>投资决策支持</span>
          <el-select v-model="selectedStock" placeholder="选择股票" size="small">
            <el-option v-for="item in stockList" :key="item.code" :label="item.name" :value="item.code"></el-option>
          </el-select>
          <el-button type="primary" size="small" @click="generateDecision">生成决策</el-button>
        </div>
      </template>
      
      <div class="decision-summary">
        <div class="overall-rating">
          <div class="rating-score">{{ overallRating.score }}</div>
          <div class="rating-label">综合评分</div>
          <div class="rating-grade" :class="getGradeClass(overallRating.grade)">{{ overallRating.grade }}</div>
          <div class="investment-recommendation">
            <el-tag :type="getRecommendationType(investmentRecommendation)" size="large">{{ investmentRecommendation }}</el-tag>
          </div>
        </div>
        
        <div class="target-price">
          <div class="price-item">
            <div class="price-label">目标价格区间</div>
            <div class="price-range">
              <span class="price-low">{{ targetPrice.low }}</span>
              <span class="price-separator">-</span>
              <span class="price-high">{{ targetPrice.high }}</span>
            </div>
          </div>
          <div class="price-item">
            <div class="price-label">上涨空间</div>
            <div class="upside-potential" :class="upsidePotential > 0 ? 'positive' : 'negative'">
              {{ upsidePotential > 0 ? '+' : '' }}{{ upsidePotential.toFixed(2) }}%
            </div>
          </div>
        </div>
      </div>
      
      <el-tabs>
        <el-tab-pane label="估值解读">
          <div class="interpretation-content">
            <div class="interpretation-paragraph">{{ valuationInterpretation.paragraph1 }}</div>
            <div class="interpretation-paragraph">{{ valuationInterpretation.paragraph2 }}</div>
            <div class="interpretation-chart">
              <div id="valuationInterpretationChart"></div>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="投资机会">
          <el-table :data="investmentOpportunities" border>
            <el-table-column prop="opportunityType" label="机会类型"></el-table-column>
            <el-table-column prop="description" label="描述" show-overflow-tooltip></el-table-column>
            <el-table-column prop="strength" label="强度" width="100">
              <template #default="scope">
                <el-progress :percentage="scope.row.strength" :color="getOpportunityColor(scope.row.strength)"></el-progress>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="风险评估">
          <el-table :data="riskFactors" border>
            <el-table-column prop="riskType" label="风险类型"></el-table-column>
            <el-table-column prop="description" label="描述" show-overflow-tooltip></el-table-column>
            <el-table-column prop="level" label="风险等级" width="100">
              <template #default="scope">
                <el-tag :type="getRiskLevelType(scope.row.level)">{{ scope.row.level }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div class="risk-chart">
            <div id="riskMatrixChart"></div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="投资建议">
          <div class="recommendation-content">
            <div class="recommendation-point">{{ investmentSuggestions.point1 }}</div>
            <div class="recommendation-point">{{ investmentSuggestions.point2 }}</div>
            <div class="recommendation-point">{{ investmentSuggestions.point3 }}</div>
            <div class="recommendation-point">{{ investmentSuggestions.point4 }}</div>
          </div>
          
          <el-card class="position-sizing">
            <template #header>
              <div class="card-header">
                <span>仓位建议</span>
              </div>
            </template>
            <div class="position-chart">
              <div id="positionSizingChart"></div>
            </div>
            <div class="position-details">
              <div class="position-item">
                <span class="position-label">建议仓位占比:</span>
                <span class="position-value">{{ positionSuggestion.percentage }}%</span>
              </div>
              <div class="position-item">
                <span class="position-label">建议买入价格:</span>
                <span class="position-value">{{ positionSuggestion.buyPrice }}</span>
              </div>
              <div class="position-item">
                <span class="position-label">建议止损价格:</span>
                <span class="position-value">{{ positionSuggestion.stopLossPrice }}</span>
              </div>
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>
```

### 2.3 投资组合管理

#### 2.3.1 功能描述

该模块允许用户构建和管理模拟投资组合，进行组合风险收益分析，并提供优化建议和回测功能，帮助用户实现投资组合的科学管理。

#### 2.3.2 功能点

1. **模拟投资组合构建**
   - 新建/编辑投资组合
   - 投资组合持仓管理（买入/卖出/调整）
   - 投资组合分类与标签
   - 组合模板管理

2. **组合风险收益分析**
   - 组合收益计算（绝对收益/相对收益）
   - 风险指标分析（波动率/夏普比率/最大回撤）
   - 风险敞口分析
   - 收益归因分析

3. **组合优化建议**
   - 基于均值方差优化
   - 基于风险平价优化
   - 基于因子暴露优化
   - 行业/风格均衡建议

4. **投资组合回测**
   - 历史表现回测
   - 情景模拟分析
   - 压力测试
   - 极端事件影响分析

5. **组合监控与调整**
   - 实时组合监控
   - 异常提醒
   - 定期再平衡建议
   - 组合绩效评估

#### 2.3.3 界面原型

```vue
<template>
  <div class="portfolio-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>投资组合管理</span>
          <el-button type="primary" size="small" @click="createPortfolio">新建组合</el-button>
          <el-select v-model="selectedPortfolioId" placeholder="选择组合" size="small">
            <el-option v-for="item in portfolioList" :key="item.id" :label="item.name" :value="item.id"></el-option>
          </el-select>
        </div>
      </template>
      
      <div class="portfolio-overview">
        <div class="performance-summary">
          <el-statistic title="组合市值" :value="portfolioStats.totalValue" suffix="元" :precision="2"></el-statistic>
          <el-statistic title="总收益率" :value="portfolioStats.totalReturn" suffix="%" :precision="2" :value-style="portfolioStats.totalReturn >= 0 ? { color: '#3f8600' } : { color: '#cf1322' }"></el-statistic>
          <el-statistic title="年化收益率" :value="portfolioStats.annualizedReturn" suffix="%" :precision="2" :value-style="portfolioStats.annualizedReturn >= 0 ? { color: '#3f8600' } : { color: '#cf1322' }"></el-statistic>
          <el-statistic title="最大回撤" :value="portfolioStats.maxDrawdown" suffix="%" :precision="2" :value-style="{ color: '#cf1322' }"></el-statistic>
          <el-statistic title="夏普比率" :value="portfolioStats.sharpeRatio" :precision="2" :value-style="portfolioStats.sharpeRatio >= 0 ? { color: '#3f8600' } : { color: '#cf1322' }"></el-statistic>
        </div>
        
        <div class="portfolio-chart">
          <div id="portfolioPerformanceChart"></div>
        </div>
      </div>
      
      <el-tabs>
        <el-tab-pane label="持仓明细">
          <div class="position-management">
            <el-button type="primary" size="small" @click="addPosition">添加持仓</el-button>
            <el-button size="small" @click="adjustPosition">调整持仓</el-button>
            <el-button size="small" @click="removePosition">移除持仓</el-button>
          </div>
          
          <el-table :data="portfolioPositions" border>
            <el-table-column type="selection" width="55"></el-table-column>
            <el-table-column prop="stockCode" label="股票代码"></el-table-column>
            <el-table-column prop="stockName" label="股票名称"></el-table-column>
            <el-table-column prop="quantity" label="持仓数量"></el-table-column>
            <el-table-column prop="avgCost" label="平均成本"></el-table-column>
            <el-table-column prop="currentPrice" label="当前价格"></el-table-column>
            <el-table-column prop="marketValue" label="市值"></el-table-column>
            <el-table-column prop="weight" label="权重(%)"></el-table-column>
            <el-table-column prop="profit" label="盈亏金额">
              <template #default="scope">
                <span :class="scope.row.profit >= 0 ? 'profit-positive' : 'profit-negative'">
                  {{ scope.row.profit >= 0 ? '+' : '' }}{{ scope.row.profit.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="profitRate" label="盈亏率(%)">
              <template #default="scope">
                <span :class="scope.row.profitRate >= 0 ? 'profit-positive' : 'profit-negative'">
                  {{ scope.row.profitRate >= 0 ? '+' : '' }}{{ scope.row.profitRate.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="风险分析">
          <div class="risk-analysis-content">
            <div class="risk-metrics">
              <el-statistic title="波动率" :value="riskMetrics.volatility" suffix="%" :precision="2"></el-statistic>
              <el-statistic title="贝塔系数" :value="riskMetrics.beta" :precision="2"></el-statistic>
              <el-statistic title="阿尔法" :value="riskMetrics.alpha" suffix="%" :precision="2"></el-statistic>
              <el-statistic title="信息比率" :value="riskMetrics.informationRatio" :precision="2"></el-statistic>
            </div>
            <div class="risk-charts">
              <div class="risk-chart">
                <div id="riskExposureChart"></div>
              </div>
              <div class="risk-chart">
                <div id="drawdownChart"></div>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="组合优化">
          <div class="optimization-params">
            <el-form :model="optimizationParams" label-width="120px">
              <el-form-item label="优化目标">
                <el-radio-group v-model="optimizationParams.target">
                  <el-radio label="最大化夏普比率"></el-radio>
                  <el-radio label="最小化波动率"></el-radio>
                  <el-radio label="风险平价"></el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="目标收益率">
                <el-input-number v-model="optimizationParams.targetReturn" :min="0" :step="0.1" size="small"></el-input-number>
              </el-form-item>
              <el-form-item label="最大波动率">
                <el-input-number v-model="optimizationParams.maxVolatility" :min="0" :step="0.1" size="small"></el-input-number>
              </el-form-item>
              <el-form-item label="个股最大权重">
                <el-input-number v-model="optimizationParams.maxStockWeight" :min="0" :max="100" :step="1" size="small"></el-input-number>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" size="small" @click="runOptimization">执行优化</el-button>
                <el-button size="small" @click="applyOptimization">应用优化结果</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <div class="optimization-results">
            <div class="result-chart">
              <div id="optimizationChart"></div>
            </div>
            
            <el-table :data="optimizationResults" border>
              <el-table-column prop="stockCode" label="股票代码"></el-table-column>
              <el-table-column prop="stockName" label="股票名称"></el-table-column>
              <el-table-column prop="currentWeight" label="当前权重(%)"></el-table-column>
              <el-table-column prop="optimizedWeight" label="优化后权重(%)"></el-table-column>
              <el-table-column prop="change" label="变动(%)">
                <template #default="scope">
                  <span :class="scope.row.change >= 0 ? 'positive' : 'negative'">
                    {{ scope.row.change >= 0 ? '+' : '' }}{{ scope.row.change.toFixed(2) }}%
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="回测分析">
          <!-- 回测分析内容 -->
        </el-tab-pane>
        
        <el-tab-pane label="交易记录">
          <!-- 交易记录内容 -->
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>
```

### 2.4 投资策略研究

#### 2.4.1 功能描述

该模块提供投资策略研究和分析功能，支持估值因子研究、策略有效性分析、策略回测与优化，以及策略监控与调整，帮助投资者开发和优化自己的投资策略。

#### 2.4.2 功能点

1. **估值因子研究**
   - 常见估值因子分析（PE、PB、PS等）
   - 因子表现历史回测
   - 因子相关性分析
   - 因子有效性评估

2. **策略有效性分析**
   - 多因子策略分析
   - 价值投资策略分析
   - 成长投资策略分析
   - 动量投资策略分析

3. **策略回测与优化**
   - 策略回测框架
   - 历史表现回测
   - 参数优化与调优
   - 策略组合测试

4. **策略监控与调整**
   - 策略实时监控
   - 异常情况预警
   - 策略绩效归因
   - 策略调整建议

5. **策略模板库**
   - 经典投资策略模板
   - 用户策略保存与分享
   - 策略排行榜
   - 策略订阅与推送

#### 2.4.3 界面原型

```vue
<template>
  <div class="strategy-research">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>投资策略研究</span>
          <el-button type="primary" size="small" @click="createStrategy">新建策略</el-button>
          <el-select v-model="selectedStrategy" placeholder="选择策略" size="small">
            <el-option v-for="item in strategyList" :key="item.id" :label="item.name" :value="item.id"></el-option>
          </el-select>
        </div>
      </template>
      
      <el-tabs>
        <el-tab-pane label="因子研究">
          <div class="factor-selection">
            <el-select v-model="selectedFactors" placeholder="选择因子" multiple collapse-tags size="small">
              <el-option label="PE(市盈率)" value="pe"></el-option>
              <el-option label="PB(市净率)" value="pb"></el-option>
              <el-option label="PS(市销率)" value="ps"></el-option>
              <el-option label="PEG" value="peg"></el-option>
              <el-option label="EV/EBITDA" value="ev_ebitda"></el-option>
              <el-option label="股息率" value="dividend_yield"></el-option>
              <el-option label="ROE" value="roe"></el-option>
              <el-option label="净利率" value="net_margin"></el-option>
            </el-select>
            <el-select v-model="factorAnalysisPeriod" placeholder="分析周期" size="small">
              <el-option label="近1年" value="1y"></el-option>
              <el-option label="近3年" value="3y"></el-option>
              <el-option label="近5年" value="5y"></el-option>
              <el-option label="近10年" value="10y"></el-option>
            </el-select>
            <el-button type="primary" size="small" @click="analyzeFactors">分析因子</el-button>
          </div>
          
          <div class="factor-analysis-results">
            <div class="factor-chart">
              <div id="factorPerformanceChart"></div>
            </div>
            
            <el-table :data="factorAnalysisResults" border>
              <el-table-column prop="factor" label="因子"></el-table-column>
              <el-table-column prop="averageReturn" label="平均收益率(%)" width="120">
                <template #default="scope">
                  <span :class="scope.row.averageReturn >= 0 ? 'positive' : 'negative'">
                    {{ scope.row.averageReturn >= 0 ? '+' : '' }}{{ scope.row.averageReturn.toFixed(2) }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="volatility" label="波动率(%)" width="100"></el-table-column>
              <el-table-column prop="sharpeRatio" label="夏普比率" width="100"></el-table-column>
              <el-table-column prop="maxDrawdown" label="最大回撤(%)" width="120"></el-table-column>
              <el-table-column prop="winRate" label="胜率(%)" width="100"></el-table-column>
              <el-table-column prop="description" label="描述" show-overflow-tooltip></el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="策略回测">
          <div class="strategy-editor">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>策略编辑器</span>
                  <el-button size="small" @click="saveStrategy">保存策略</el-button>
                </div>
              </template>
              <el-form :model="strategyParams">
                <el-form-item label="策略名称">
                  <el-input v-model="strategyParams.name" size="small"></el-input>
                </el-form-item>
                <el-form-item label="策略描述">
                  <el-input v-model="strategyParams.description" type="textarea" size="small"></el-input>
                </el-form-item>
                <el-form-item label="选股条件">
                  <div class="condition-editor">
                    <el-select v-model="newCondition.factor" placeholder="选择因子" size="small">
                      <el-option label="PE < 行业平均" value="pe_lt_industry"></el-option>
                      <el-option label="PB < 历史50%分位数" value="pb_lt_hist_median"></el-option>
                      <el-option label="ROE > 15%" value="roe_gt_15"></el-option>
                      <el-option label="净利润同比增长 > 20%" value="profit_growth_gt_20"></el-option>
                    </el-select>
                    <el-button type="primary" size="small" @click="addCondition">添加条件</el-button>
                  </div>
                  <el-tag v-for="(condition, index) in strategyParams.conditions" :key="index" closable @close="removeCondition(index)">
                    {{ condition }}
                  </el-tag>
                </el-form-item>
                <el-form-item label="调仓周期">
                  <el-select v-model="strategyParams.rebalancePeriod" placeholder="选择调仓周期" size="small">
                    <el-option label="每月" value="monthly"></el-option>
                    <el-option label="每季度" value="quarterly"></el-option>
                    <el-option label="每半年" value="semi_annual"></el-option>
                    <el-option label="每年" value="annual"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="持仓数量限制">
                  <el-input-number v-model="strategyParams.maxStocks" :min="1" size="small"></el-input-number>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" size="small" @click="runStrategyBacktest">运行回测</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </div>
          
          <div class="backtest-results">
            <div class="backtest-summary">
              <el-statistic title="回测区间" :value="backtestStats.period"></el-statistic>
              <el-statistic title="累计收益率" :value="backtestStats.totalReturn" suffix="%" :precision="2" :value-style="backtestStats.totalReturn >= 0 ? { color: '#3f8600' } : { color: '#cf1322' }"></el-statistic>
              <el-statistic title="年化收益率" :value="backtestStats.annualizedReturn" suffix="%" :precision="2" :value-style="backtestStats.annualizedReturn >= 0 ? { color: '#3f8600' } : { color: '#cf1322' }"></el-statistic>
              <el-statistic title="夏普比率" :value="backtestStats.sharpeRatio" :precision="2" :value-style="backtestStats.sharpeRatio >= 0 ? { color: '#3f8600' } : { color: '#cf1322' }"></el-statistic>
              <el-statistic title="最大回撤" :value="backtestStats.maxDrawdown" suffix="%" :precision="2" :value-style="{ color: '#cf1322' }"></el-statistic>
            </div>
            
            <div class="backtest-charts">
              <div class="backtest-chart">
                <div id="backtestPerformanceChart"></div>
              </div>
              <div class="backtest-chart">
                <div id="backtestDrawdownChart"></div>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="策略库">
          <!-- 策略库内容 -->
        </el-tab-pane>
        
        <el-tab-pane label="策略监控">
          <!-- 策略监控内容 -->
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>
```

## 3. 数据模型设计

### 3.1 核心数据结构

#### 3.1.1 估值模型数据

```typescript
interface ValuationModel {
  id: string;                    // 唯一标识符
  stockCode: string;             // 股票代码
  stockName: string;             // 股票名称
  modelType: 'relative' | 'absolute' | 'industry' | 'custom'; // 模型类型
  modelName: string;             // 具体模型名称(如PE, DCF等)
  valuationDate: string;         // 估值日期
  
  // 模型参数
  parameters: {
    [key: string]: number | string | boolean; // 具体参数
  };
  
  // 估值结果
  results: {
    fairValue: number;           // 合理价值
    currentPrice: number;        // 当前价格
    discountRate: number;        // 偏离度(%)
    targetPriceRange: {
      low: number;               // 目标价格下限
      high: number;              // 目标价格上限
    };
    upsidePotential: number;     // 上涨空间(%)
    valuationGrade: 'undervalued' | 'fair' | 'overvalued'; // 估值评级
    confidenceLevel: 'high' | 'medium' | 'low'; // 置信度
  };
  
  // 敏感性分析
  sensitivityAnalysis: {
    parameter: string;           // 敏感性参数
    scenarios: {
      name: string;              // 情景名称
      value: number;             // 参数值
      impact: number;            // 对合理价值的影响(%)
    }[];
  };
  
  createdAt: string;             // 创建时间
  updatedAt: string;             // 更新时间
}
```

#### 3.1.2 投资决策数据

```typescript
interface InvestmentDecision {
  id: string;                    // 唯一标识符
  stockCode: string;             // 股票代码
  stockName: string;             // 股票名称
  decisionDate: string;          // 决策日期
  
  // 综合评分
  overallRating: {
    score: number;               // 评分(0-100)
    grade: 'A' | 'B' | 'C' | 'D' | 'E'; // 评级
  };
  
  // 投资建议
  recommendation: {
    action: 'buy' | 'hold' | 'sell' | 'underweight' | 'overweight'; // 操作建议
    targetPrice: {
      low: number;               // 目标价格下限
      high: number;              // 目标价格上限
    };
    holdingPeriod: string;       // 建议持有期限
    positionSizing: number;      // 建议仓位占比(%)
    entryPrice: number;          // 建议买入价格
    stopLossPrice: number;       // 建议止损价格
  };
  
  // 支持理由
  supportingReasons: string[];   // 支持理由列表
  
  // 风险因素
  riskFactors: RiskFactor[];     // 风险因素列表
  
  // 决策依据
  decisionBasis: {
    valuationModels: string[];   // 使用的估值模型
    financialAnalysis: boolean;  // 是否基于财务分析
    industryAnalysis: boolean;   // 是否基于行业分析
    technicalAnalysis: boolean;  // 是否基于技术分析
  };
  
  // 跟踪记录
  tracking: {
    isTracked: boolean;          // 是否跟踪
    alerts: boolean;             // 是否开启提醒
    reviewDate: string;          // 下次回顾日期
  };
  
  createdAt: string;             // 创建时间
  updatedAt: string;             // 更新时间
}

interface RiskFactor {
  factorType: string;            // 风险类型
  description: string;           // 风险描述
  severity: 'high' | 'medium' | 'low'; // 严重程度
  probability: 'high' | 'medium' | 'low'; // 发生概率
  impact: string;                // 潜在影响
  mitigation: string;            // 缓解措施
}
```

#### 3.1.3 投资组合数据

```typescript
interface InvestmentPortfolio {
  id: string;                    // 唯一标识符
  name: string;                  // 组合名称
  description: string;           // 组合描述
  riskProfile: 'conservative' | 'moderate' | 'aggressive'; // 风险偏好
  targetReturn: number;          // 目标收益率(%)
  benchmark: string;             // 基准指数
  
  // 组合统计信息
  statistics: {
    totalValue: number;          // 组合总市值
    totalReturn: number;         // 总收益率(%)
    annualizedReturn: number;    // 年化收益率(%)
    volatility: number;          // 波动率(%)
    sharpeRatio: number;         // 夏普比率
    maxDrawdown: number;         // 最大回撤(%)
    beta: number;                // 贝塔系数
    alpha: number;               // 阿尔法收益(%)
    informationRatio: number;    // 信息比率
  };
  
  // 持仓列表
  positions: PortfolioPosition[];
  
  // 行业分布
  industryDistribution: {
    industryCode: string;        // 行业代码
    industryName: string;        // 行业名称
    weight: number;              // 权重(%)
    value: number;               // 市值
  }[];
  
  // 历史业绩
  historicalPerformance: {
    date: string;                // 日期
    value: number;               // 组合价值
    dailyReturn: number;         // 日收益率(%)
    benchmarkReturn: number;     // 基准收益率(%)
  }[];
  
  // 交易记录
  transactions: PortfolioTransaction[];
  
  createdAt: string;             // 创建时间
  updatedAt: string;             // 更新时间
}

interface PortfolioPosition {
  id: string;                    // 持仓ID
  stockCode: string;             // 股票代码
  stockName: string;             // 股票名称
  quantity: number;              // 持仓数量
  avgCost: number;               // 平均成本
  currentPrice: number;          // 当前价格
  marketValue: number;           // 市值
  weight: number;                // 权重(%)
  profit: number;                // 盈亏金额
  profitRate: number;            // 盈亏率(%)
  purchaseDate: string;          // 购买日期
  lastUpdated: string;           // 最后更新时间
}

interface PortfolioTransaction {
  id: string;                    // 交易ID
  transactionType: 'buy' | 'sell'; // 交易类型
  stockCode: string;             // 股票代码
  stockName: string;             // 股票名称
  quantity: number;              // 交易数量
  price: number;                 // 交易价格
  totalAmount: number;           // 交易金额
  transactionDate: string;       // 交易日期
  commission: number;            // 佣金费用
  notes: string;                 // 交易备注
}
```

#### 3.1.4 投资策略数据

```typescript
interface InvestmentStrategy {
  id: string;                    // 唯一标识符
  name: string;                  // 策略名称
  description: string;           // 策略描述
  strategyType: 'value' | 'growth' | 'momentum' | 'multi_factor' | 'custom'; // 策略类型
  
  // 策略参数
  parameters: {
    selectionCriteria: string[]; // 选股条件
    rebalancePeriod: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'semi_annual' | 'annual'; // 调仓周期
    maxStocks: number;           // 最大持仓数量
    positionSizing: number;      // 单个持仓最大权重(%)
    stopLoss: number;            // 止损比例(%)
    takeProfit: number;          // 止盈比例(%)
  };
  
  // 回测结果
  backtestResults: {
    period: {
      startDate: string;         // 回测开始日期
      endDate: string;           // 回测结束日期
    };
    performance: {
      totalReturn: number;       // 总收益率(%)
      annualizedReturn: number;  // 年化收益率(%)
      volatility: number;        // 波动率(%)
      sharpeRatio: number;       // 夏普比率
      maxDrawdown: number;       // 最大回撤(%)
      winRate: number;           // 胜率(%)
      beta: number;              // 贝塔系数
      alpha: number;             // 阿尔法收益(%)
      benchmarkReturn: number;   // 基准收益率(%)
    };
    equityCurve: {
      date: string;              // 日期
      value: number;             // 净值
      benchmark: number;         // 基准净值
    }[];
    trades: {
      stockCode: string;         // 股票代码
      entryDate: string;         // 买入日期
      exitDate: string;          // 卖出日期
      entryPrice: number;        // 买入价格
      exitPrice: number;         // 卖出价格
      return: number;            // 收益率(%)
    }[];
  };
  
  // 策略监控
  monitoring: {
    isActive: boolean;           // 是否激活监控
    lastChecked: string;         // 最后检查时间
    alerts: StrategyAlert[];     // 告警列表
    currentHoldings: string[];   // 当前持仓
  };
  
  createdAt: string;             // 创建时间
  updatedAt: string;             // 更新时间
}

interface StrategyAlert {
  id: string;                    // 告警ID
  type: 'rebalance' | 'stop_loss' | 'take_profit' | 'signal' | 'error'; // 告警类型
  stockCode?: string;            // 相关股票代码
  message: string;               // 告警消息
  severity: 'high' | 'medium' | 'low'; // 严重程度
  timestamp: string;             // 告警时间
  isRead: boolean;               // 是否已读
}
```

### 3.2 数据库表结构

#### 3.2.1 估值模型表(valuation_models)

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
| :--- | :--- | :--- | :--- | :--- |
| id | VARCHAR | 36 | PRIMARY KEY | 唯一标识符(UUID) |
| stock_code | VARCHAR | 20 | NOT NULL | 股票代码 |
| stock_name | VARCHAR | 100 | NOT NULL | 股票名称 |
| model_type | VARCHAR | 20 | NOT NULL | 模型类型 |
| model_name | VARCHAR | 50 | NOT NULL | 具体模型名称 |
| valuation_date | DATETIME | - | NOT NULL | 估值日期 |
| parameters | JSON | - | NOT NULL | 模型参数(JSON格式) |
| results | JSON | - | NOT NULL | 估值结果(JSON格式) |
| sensitivity_analysis | JSON | - | NULL | 敏感性分析(JSON格式) |
| created_at | DATETIME | - | NOT NULL | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | 更新时间 |
| INDEX | - | - | (stock_code, valuation_date) | 索引 |

#### 3.2.2 投资决策表(investment_decisions)

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
| :--- | :--- | :--- | :--- | :--- |
| id | VARCHAR | 36 | PRIMARY KEY | 唯一标识符(UUID) |
| stock_code | VARCHAR | 20 | NOT NULL | 股票代码 |
| stock_name | VARCHAR | 100 | NOT NULL | 股票名称 |
| decision_date | DATETIME | - | NOT NULL | 决策日期 |
| overall_rating | JSON | - | NOT NULL | 综合评分(JSON格式) |
| recommendation | JSON | - | NOT NULL | 投资建议(JSON格式) |
| supporting_reasons | TEXT | - | NULL | 支持理由(JSON数组字符串) |
| risk_factors | JSON | - | NULL | 风险因素(JSON格式) |
| decision_basis | JSON | - | NOT NULL | 决策依据(JSON格式) |
| tracking | JSON | - | NOT NULL | 跟踪记录(JSON格式) |
| created_at | DATETIME | - | NOT NULL | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | 更新时间 |
| INDEX | - | - | (stock_code, decision_date) | 索引 |

#### 3.2.3 投资组合表(investment_portfolios)

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
| :--- | :--- | :--- | :--- | :--- |
| id | VARCHAR | 36 | PRIMARY KEY | 唯一标识符(UUID) |
| name | VARCHAR | 100 | NOT NULL | 组合名称 |
| description | TEXT | - | NULL | 组合描述 |
| risk_profile | VARCHAR | 20 | NOT NULL | 风险偏好 |
| target_return | DECIMAL | 5,2 | NULL | 目标收益率(%) |
| benchmark | VARCHAR | 50 | NULL | 基准指数 |
| statistics | JSON | - | NOT NULL | 组合统计信息(JSON格式) |
| industry_distribution | JSON | - | NULL | 行业分布(JSON格式) |
| created_at | DATETIME | - | NOT NULL | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | 更新时间 |

#### 3.2.4 组合持仓表(portfolio_positions)

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
| :--- | :--- | :--- | :--- | :--- |
| id | VARCHAR | 36 | PRIMARY KEY | 唯一标识符(UUID) |
| portfolio_id | VARCHAR | 36 | NOT NULL | 投资组合ID |
| stock_code | VARCHAR | 20 | NOT NULL | 股票代码 |
| stock_name | VARCHAR | 100 | NOT NULL | 股票名称 |
| quantity | DECIMAL | 18,6 | NOT NULL | 持仓数量 |
| avg_cost | DECIMAL | 15,2 | NOT NULL | 平均成本 |
| current_price | DECIMAL | 15,2 | NOT NULL | 当前价格 |
| market_value | DECIMAL | 18,2 | NOT NULL | 市值 |
| weight | DECIMAL | 8,4 | NOT NULL | 权重(%) |
| profit | DECIMAL | 18,2 | NOT NULL | 盈亏金额 |
| profit_rate | DECIMAL | 8,4 | NOT NULL | 盈亏率(%) |
| purchase_date | DATETIME | - | NOT NULL | 购买日期 |
| last_updated | DATETIME | - | NOT NULL | 最后更新时间 |
| FOREIGN KEY | - | - | (portfolio_id) REFERENCES investment_portfolios(id) | 外键约束 |
| INDEX | - | - | (portfolio_id) | 索引 |

#### 3.2.5 投资策略表(investment_strategies)

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
| :--- | :--- | :--- | :--- | :--- |
| id | VARCHAR | 36 | PRIMARY KEY | 唯一标识符(UUID) |
| name | VARCHAR | 100 | NOT NULL | 策略名称 |
| description | TEXT | - | NULL | 策略描述 |
| strategy_type | VARCHAR | 20 | NOT NULL | 策略类型 |
| parameters | JSON | - | NOT NULL | 策略参数(JSON格式) |
| backtest_results | JSON | - | NULL | 回测结果(JSON格式) |
| monitoring | JSON | - | NOT NULL | 策略监控(JSON格式) |
| created_at | DATETIME | - | NOT NULL | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | 更新时间 |

## 4. API接口设计

### 4.1 估值模型接口

#### 4.1.1 计算股票估值

- **接口路径**: `/api/valuation/models/calculate`
- **请求方法**: POST
- **请求体**:
  ```json
  {
    "stockCode": "600519.SH",
    "modelType": "relative",
    "models": ["PE", "PB", "PS"],
    "parameters": {
      "forecastPE": 30,
      "forecastPB": 9,
      "industryAverageAdjustment": true
    }
  }
  ```
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "stockCode": "600519.SH",
      "stockName": "贵州茅台",
      "valuationDate": "2024-01-15T10:30:00Z",
      "results": [
        {
          "modelName": "PE模型",
          "fairValue": 1336.8,
          "currentPrice": 1150.0,
          "discountRate": -13.98,
          "valuationGrade": "undervalued",
          "confidenceLevel": "high"
        },
        {
          "modelName": "PB模型",
          "fairValue": 1425.6,
          "currentPrice": 1150.0,
          "discountRate": -19.33,
          "valuationGrade": "undervalued",
          "confidenceLevel": "medium"
        },
        {
          "modelName": "PS模型",
          "fairValue": 1280.5,
          "currentPrice": 1150.0,
          "discountRate": -10.19,
          "valuationGrade": "undervalued",
          "confidenceLevel": "medium"
        }
      ],
      "averageFairValue": 1347.63,
      "weightedFairValue": 1358.25,
      "overallValuation": {
        "grade": "undervalued",
        "confidenceLevel": "high",
        "explanation": "综合三种估值模型，该股票当前价格较合理价值有14.9%的折扣，处于低估状态。"
      }
    }
  }
  ```

#### 4.1.2 执行DCF估值

- **接口路径**: `/api/valuation/models/dcf`
- **请求方法**: POST
- **请求体**:
  ```json
  {
    "stockCode": "600519.SH",
    "wacc": 0.085,
    "perpetualGrowthRate": 0.03,
    "forecastYears": 5,
    "forecastGrowthRates": [0.15, 0.12, 0.10, 0.08, 0.07],
    "terminalValueMethod": "perpetual_growth"
  }
  ```
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "stockCode": "600519.SH",
      "stockName": "贵州茅台",
      "valuationDate": "2024-01-15T10:30:00Z",
      "modelName": "DCF估值模型",
      "results": {
        "fairValue": 1458.32,
        "currentPrice": 1150.0,
        "discountRate": -21.14,
        "valuationGrade": "undervalued",
        "confidenceLevel": "medium"
      },
      "dcfDetails": {
        "forecastCashFlows": [
          { "year": 2024, "fcff": 68500000000, "presentValue": 63133640553 },
          { "year": 2025, "fcff": 76720000000, "presentValue": 64706745124 },
          { "year": 2026, "fcff": 84392000000, "presentValue": 64639909470 },
          { "year": 2027, "fcff": 91143360000, "presentValue": 63582991486 },
          { "year": 2028, "fcff": 97523395200, "presentValue": 61985415341 }
        ],
        "terminalValue": 1773152640000,
        "presentValueOfTerminal": 1198199338526,
        "enterpriseValue": 1511258000000,
        "equityValue": 1423758000000,
        "perShareValue": 1458.32
      },
      "sensitivityAnalysis": {
        "parameter": "WACC",
        "scenarios": [
          { "name": "WACC -1%", "value": 0.075, "impact": 18.2, "fairValue": 1723.25 },
          { "name": "WACC +1%", "value": 0.095, "impact": -13.5, "fairValue": 1258.32 }
        ]
      }
    }
  }
  ```

### 4.2 投资决策接口

#### 4.2.1 生成投资决策

- **接口路径**: `/api/decision/generate`
- **请求方法**: POST
- **请求体**:
  ```json
  {
    "stockCode": "600519.SH",
    "analysisTypes": ["valuation", "financial", "industry", "technical"],
    "considerRisk": true,
    "investmentHorizon": "long_term"
  }
  ```
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "id": "12345678-1234-1234-1234-123456789012",
      "stockCode": "600519.SH",
      "stockName": "贵州茅台",
      "decisionDate": "2024-01-15T14:30:00Z",
      "overallRating": {
        "score": 85,
        "grade": "A"
      },
      "recommendation": {
        "action": "buy",
        "targetPrice": {
          "low": 1350.0,
          "high": 1500.0
        },
        "holdingPeriod": "3-5年",
        "positionSizing": 10,
        "entryPrice": 1150.0,
        "stopLossPrice": 1035.0
      },
      "supportingReasons": [
        "公司具有强大的品牌价值和市场垄断地位",
        "财务指标健康，ROE持续保持在30%以上",
        "产品具有稀缺性，抗通胀能力强",
        "当前估值处于历史较低水平"
      ],
      "riskFactors": [
        {
          "factorType": "宏观经济风险",
          "description": "经济下行可能影响高端消费品需求",
          "severity": "medium",
          "probability": "medium",
          "impact": "短期业绩波动",
          "mitigation": "分散投资，长期持有"
        },
        {
          "factorType": "政策风险",
          "description": "可能面临消费税政策调整",
          "severity": "high",
          "probability": "low",
          "impact": "可能影响利润率",
          "mitigation": "关注政策动向，适时调整持仓"
        }
      ],
      "decisionBasis": {
        "valuationModels": ["PE", "PB", "DCF"],
        "financialAnalysis": true,
        "industryAnalysis": true,
        "technicalAnalysis": false
      },
      "summary": "综合分析表明，贵州茅台具有长期投资价值，当前估值合理，建议中长期配置，可考虑分批建仓。"
    }
  }
  ```

#### 4.2.2 获取投资决策历史

- **接口路径**: `/api/decision/history/{stockCode}`
- **请求方法**: GET
- **路径参数**:
  | 参数名 | 类型 | 描述 |
  | :--- | :--- | :--- |
  | stockCode | String | 股票代码 |
- **查询参数**:
  | 参数名 | 类型 | 是否必选 | 描述 |
  | :--- | :--- | :--- | :--- |
  | limit | Integer | 否 | 返回条数，默认10 |
  | page | Integer | 否 | 页码，默认1 |
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "list": [
        {
          "id": "12345678-1234-1234-1234-123456789012",
          "decisionDate": "2024-01-15T14:30:00Z",
          "recommendation": {
            "action": "buy",
            "targetPrice": { "low": 1350.0, "high": 1500.0 }
          },
          "overallRating": { "score": 85, "grade": "A" },
          "currentStatus": {
            "priceAtDecision": 1150.0,
            "currentPrice": 1250.0,
            "returnSinceDecision": 8.70,
            "daysSinceDecision": 30
          }
        }
      ],
      "total": 25,
      "page": 1,
      "pageSize": 10
    }
  }
  ```

### 4.3 投资组合接口

#### 4.3.1 创建投资组合

- **接口路径**: `/api/portfolio/create`
- **请求方法**: POST
- **请求体**:
  ```json
  {
    "name": "价值投资组合",
    "description": "主要投资于低估值、高质量的蓝筹股",
    "riskProfile": "moderate",
    "targetReturn": 12,
    "benchmark": "沪深300"
  }
  ```
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "id": "12345678-1234-1234-1234-123456789012",
      "name": "价值投资组合",
      "description": "主要投资于低估值、高质量的蓝筹股",
      "riskProfile": "moderate",
      "targetReturn": 12,
      "benchmark": "沪深300",
      "totalValue": 0,
      "createdAt": "2024-01-15T10:00:00Z"
    }
  }
  ```

#### 4.3.2 添加组合持仓

- **接口路径**: `/api/portfolio/{portfolioId}/positions/add`
- **请求方法**: POST
- **路径参数**:
  | 参数名 | 类型 | 描述 |
  | :--- | :--- | :--- |
  | portfolioId | String | 组合ID |
- **请求体**:
  ```json
  {
    "stockCode": "600519.SH",
    "stockName": "贵州茅台",
    "quantity": 100,
    "purchasePrice": 1150.0,
    "purchaseDate": "2024-01-15",
    "notes": "长期持有"
  }
  ```
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "positionId": "23456789-2345-2345-2345-234567890123",
      "portfolioId": "12345678-1234-1234-1234-123456789012",
      "stockCode": "600519.SH",
      "stockName": "贵州茅台",
      "quantity": 100,
      "avgCost": 1150.0,
      "currentPrice": 1175.5,
      "marketValue": 117550.0,
      "weight": 100.0,
      "profit": 2550.0,
      "profitRate": 2.22,
      "lastUpdated": "2024-01-15T10:15:00Z"
    }
  }
  ```

#### 4.3.3 获取组合分析

- **接口路径**: `/api/portfolio/{portfolioId}/analysis`
- **请求方法**: GET
- **路径参数**:
  | 参数名 | 类型 | 描述 |
  | :--- | :--- | :--- |
  | portfolioId | String | 组合ID |
- **查询参数**:
  | 参数名 | 类型 | 是否必选 | 描述 |
  | :--- | :--- | :--- | :--- |
  | analysisType | String | 否 | 分析类型：'performance', 'risk', 'all' |
  | period | String | 否 | 分析周期：'1m', '3m', '6m', '1y', '3y', '5y', 'all' |
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "portfolioId": "12345678-1234-1234-1234-123456789012",
      "portfolioName": "价值投资组合",
      "analysisDate": "2024-01-15T14:30:00Z",
      "statistics": {
        "totalValue": 1000000.0,
        "totalReturn": 15.20,
        "annualizedReturn": 18.50,
        "volatility": 12.35,
        "sharpeRatio": 1.48,
        "maxDrawdown": -18.50,
        "beta": 0.85,
        "alpha": 3.20
      },
      "performance": {
        "equityCurve": [
          { "date": "2023-01-15", "value": 1000000, "benchmark": 1000000 },
          { "date": "2023-02-15", "value": 1025000, "benchmark": 1015000 },
          { "date": "2023-03-15", "value": 1052000, "benchmark": 1030000 }
        ],
        "monthlyReturns": [
          { "month": "2023-01", "return": 2.5, "benchmarkReturn": 1.5 },
          { "month": "2023-02", "return": 2.63, "benchmarkReturn": 1.47 }
        ]
      },
      "risk": {
        "factorExposure": [
          { "factor": "value", "exposure": 0.75 },
          { "factor": "growth", "exposure": 0.35 },
          { "factor": "size", "exposure": -0.25 }
        ],
        "drawdowns": [
          { "startDate": "2023-05-10", "endDate": "2023-07-15", "peak": 1085000, "trough": 992500, "drawdown": -8.52 }
        ],
        "stressTests": [
          { "scenario": "市场下跌10%", "impact": -8.5 },
          { "scenario": "利率上升1%", "impact": -3.2 },
          { "scenario": "通胀上升2%", "impact": -2.5 }
        ]
      },
      "industryDistribution": [
        { "industryCode": "Food&Beverage", "industryName": "食品饮料", "weight": 30, "value": 300000 },
        { "industryCode": "Finance", "industryName": "金融", "weight": 25, "value": 250000 },
        { "industryCode": "Healthcare", "industryName": "医药", "weight": 20, "value": 200000 },
        { "industryCode": "Technology", "industryName": "科技", "weight": 15, "value": 150000 },
        { "industryCode": "Other", "industryName": "其他", "weight": 10, "value": 100000 }
      ]
    }
  }
  ```

#### 4.3.4 优化投资组合

- **接口路径**: `/api/portfolio/{portfolioId}/optimize`
- **请求方法**: POST
- **路径参数**:
  | 参数名 | 类型 | 描述 |
  | :--- | :--- | :--- |
  | portfolioId | String | 组合ID |
- **请求体**:
  ```json
  {
    "optimizationTarget": "max_sharpe",
    "constraints": {
      "maxVolatility": 15,
      "maxStockWeight": 20,
      "minDiversification": true
    },
    "availableStocks": ["600519.SH", "601318.SH", "000858.SZ", "002594.SZ", "300750.SZ"],
    "riskFreeRate": 2.5
  }
  ```
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "portfolioId": "12345678-1234-1234-1234-123456789012",
      "optimizationDate": "2024-01-15T15:00:00Z",
      "optimizationTarget": "max_sharpe",
      "currentStatistics": {
        "sharpeRatio": 1.48,
        "volatility": 12.35,
        "expectedReturn": 18.50
      },
      "optimizedStatistics": {
        "sharpeRatio": 1.75,
        "volatility": 11.20,
        "expectedReturn": 18.00
      },
      "optimizedAllocations": [
        {
          "stockCode": "600519.SH",
          "stockName": "贵州茅台",
          "currentWeight": 25.0,
          "optimizedWeight": 20.0,
          "change": -5.0,
          "action": "reduce",
          "quantityChange": -50
        },
        {
          "stockCode": "601318.SH",
          "stockName": "中国平安",
          "currentWeight": 15.0,
          "optimizedWeight": 18.0,
          "change": 3.0,
          "action": "increase",
          "quantityChange": 2000
        },
        {
          "stockCode": "000858.SZ",
          "stockName": "五粮液",
          "currentWeight": 20.0,
          "optimizedWeight": 20.0,
          "change": 0.0,
          "action": "hold",
          "quantityChange": 0
        }
      ],
      "explanation": "优化后的投资组合通过调整权重分配，在保持相似预期收益率的情况下，降低了组合的波动率，从而提高了夏普比率。建议将贵州茅台的权重从25%降至20%，同时增加中国平安的权重从15%增至18%。"
    }
  }
  ```

### 4.4 投资策略接口

#### 4.4.1 创建投资策略

- **接口路径**: `/api/strategy/create`
- **请求方法**: POST
- **请求体**:
  ```json
  {
    "name": "低估值成长策略",
    "description": "投资于PE低于行业平均且业绩增长良好的股票",
    "strategyType": "multi_factor",
    "parameters": {
      "selectionCriteria": [
        "PE < 行业平均 * 0.8",
        "ROE > 15%",
        "净利润同比增长 > 20%",
        "市值 > 100亿"
      ],
      "rebalancePeriod": "monthly",
      "maxStocks": 20,
      "positionSizing": 10,
      "stopLoss": 15,
      "takeProfit": 50
    }
  }
  ```
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "id": "12345678-1234-1234-1234-123456789012",
      "name": "低估值成长策略",
      "description": "投资于PE低于行业平均且业绩增长良好的股票",
      "strategyType": "multi_factor",
      "parameters": {
        "selectionCriteria": [
          "PE < 行业平均 * 0.8",
          "ROE > 15%",
          "净利润同比增长 > 20%",
          "市值 > 100亿"
        ],
        "rebalancePeriod": "monthly",
        "maxStocks": 20,
        "positionSizing": 10,
        "stopLoss": 15,
        "takeProfit": 50
      },
      "createdAt": "2024-01-15T10:00:00Z"
    }
  }
  ```

#### 4.4.2 执行策略回测

- **接口路径**: `/api/strategy/{strategyId}/backtest`
- **请求方法**: POST
- **路径参数**:
  | 参数名 | 类型 | 描述 |
  | :--- | :--- | :--- |
  | strategyId | String | 策略ID |
- **请求体**:
  ```json
  {
    "startDate": "2021-01-01",
    "endDate": "2024-01-15",
    "initialCapital": 1000000,
    "benchmark": "沪深300",
    "transactionCost": 0.0015,
    "slippage": 0.001
  }
  ```
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "strategyId": "12345678-1234-1234-1234-123456789012",
      "strategyName": "低估值成长策略",
      "backtestPeriod": {
        "startDate": "2021-01-01",
        "endDate": "2024-01-15"
      },
      "performance": {
        "initialCapital": 1000000,
        "finalCapital": 1857250,
        "totalReturn": 85.73,
        "annualizedReturn": 23.25,
        "volatility": 16.80,
        "sharpeRatio": 1.27,
        "maxDrawdown": -28.50,
        "beta": 0.85,
        "alpha": 8.50,
        "informationRatio": 1.12,
        "winRate": 62.30,
        "benchmarkReturn": 25.30,
        "excessReturn": 60.43
      },
      "tradingStats": {
        "totalTrades": 156,
        "avgHoldingPeriod": 63,
        "turnoverRate": 2.8,
        "winLossRatio": 1.5
      },
      "equityCurve": [
        { "date": "2021-01-01", "value": 1000000, "benchmark": 1000000 },
        { "date": "2021-02-01", "value": 1085000, "benchmark": 1032000 },
        { "date": "2021-03-01", "value": 1152000, "benchmark": 1058000 }
      ],
      "topPerformers": [
        { "stockCode": "002594.SZ", "stockName": "比亚迪", "return": 185.5, "holdingPeriod": 215 },
        { "stockCode": "300750.SZ", "stockName": "宁德时代", "return": 156.8, "holdingPeriod": 185 }
      ],
      "drawdowns": [
        { "startDate": "2022-04-15", "endDate": "2022-10-20", "peak": 1650000, "trough": 1178500, "drawdown": -28.50 }
      ]
    }
  }
  ```

#### 4.4.3 获取因子分析

- **接口路径**: `/api/strategy/factor-analysis`
- **请求方法**: POST
- **请求体**:
  ```json
  {
    "factors": ["PE", "PB", "PS", "ROE", "MarketCap"],
    "period": "5y",
    "universe": "A_share",
    "groupByQuantile": true,
    "quantiles": 5
  }
  ```
- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "analysisPeriod": "5年",
      "universe": "A股市场",
      "factorResults": [
        {
          "factor": "PE",
          "description": "市盈率",
          "performanceByQuantile": [
            { "quantile": "最低1/5", "annualizedReturn": 18.5, "volatility": 18.2, "sharpeRatio": 1.02 },
            { "quantile": "次低1/5", "annualizedReturn": 15.2, "volatility": 17.8, "sharpeRatio": 0.85 },
            { "quantile": "中等1/5", "annualizedReturn": 12.3, "volatility": 16.5, "sharpeRatio": 0.75 },
            { "quantile": "次高1/5", "annualizedReturn": 9.8, "volatility": 17.2, "sharpeRatio": 0.57 },
            { "quantile": "最高1/5", "annualizedReturn": 5.2, "volatility": 18.5, "sharpeRatio": 0.28 }
          ],
          "factorDecay": [
            { "month": 1, "factorEffect": 0.85 },
            { "month": 3, "factorEffect": 0.72 },
            { "month": 6, "factorEffect": 0.58 },
            { "month": 12, "factorEffect": 0.35 }
          ],
          "conclusion": "PE因子在A股市场表现出明显的价值溢价效应，低PE股票长期表现优于高PE股票。"
        },
        {
          "factor": "ROE",
          "description": "净资产收益率",
          "performanceByQuantile": [
            { "quantile": "最高1/5", "annualizedReturn": 16.8, "volatility": 17.5, "sharpeRatio": 0.96 },
            { "quantile": "次高1/5", "annualizedReturn": 14.5, "volatility": 16.8, "sharpeRatio": 0.86 },
            { "quantile": "中等1/5", "annualizedReturn": 12.1, "volatility": 16.2, "sharpeRatio": 0.75 },
            { "quantile": "次低1/5", "annualizedReturn": 9.2, "volatility": 17.5, "sharpeRatio": 0.52 },
            { "quantile": "最低1/5", "annualizedReturn": 6.5, "volatility": 19.8, "sharpeRatio": 0.33 }
          ],
          "factorDecay": [
            { "month": 1, "factorEffect": 0.82 },
            { "month": 3, "factorEffect": 0.75 },
            { "month": 6, "factorEffect": 0.62 },
            { "month": 12, "factorEffect": 0.45 }
          ],
          "conclusion": "高ROE股票表现出良好的长期收益能力，投资者可以将ROE作为选股的重要指标。"
        }
      ],
      "factorCorrelations": {
        "PE-PB": 0.75,
        "PE-ROE": -0.35,
        "PB-ROE": 0.45,
        "ROE-Growth": 0.52
      }
    }
  }
  ```

## 5. 交互与用户体验设计

### 5.1 用户交互流程

#### 5.1.1 估值模型使用流程

1. **选择股票与模型**：
   - 用户从股票搜索框中输入股票代码或名称进行搜索
   - 系统展示匹配的股票列表，用户选择目标股票
   - 用户从模型选择面板中选择一个或多个估值模型
   - 系统根据选择的模型类型，展示相应的参数配置界面

2. **参数配置**：
   - 用户可选择使用系统默认参数或手动调整参数
   - 对于相对估值模型，可配置PE、PB等估值倍数
   - 对于DCF等绝对估值模型，可配置WACC、增长率、预测年限等
   - 系统提供参数的行业参考值和历史范围提示

3. **执行计算**：
   - 用户确认参数配置后，点击"计算估值"按钮
   - 系统显示加载状态，执行估值计算
   - 计算完成后，系统展示估值结果和分析图表

4. **结果分析**：
   - 系统展示多模型估值结果对比表格
   - 提供估值历史趋势图和行业对比图
   - 显示估值评级和置信度评估
   - 提供估值结果的专业解读文本

5. **参数敏感性分析**：
   - 用户可选择进行敏感性分析，了解不同参数对估值结果的影响
   - 系统提供参数变动对估值结果影响的可视化展示
   - 用户可自定义敏感参数和变动范围

#### 5.1.2 投资决策支持流程

1. **决策生成**：
   - 用户选择目标股票
   - 系统提供多种分析维度选项（估值分析、财务分析、行业分析、技术分析）
   - 用户可选择决策时间范围（短期、中期、长期）
   - 系统综合分析后生成投资决策报告

2. **决策报告查看**：
   - 系统展示决策摘要（综合评分、投资建议、目标价格）
   - 提供详细的决策依据和支持理由
   - 展示风险因素和缓解措施
   - 提供投资组合配置建议

3. **决策执行与跟踪**：
   - 用户可将投资决策添加到投资组合
   - 设置决策提醒和跟踪计划
   - 系统定期更新决策执行情况
   - 当股价达到预设目标或止损点时，系统发出提醒

#### 5.1.3 投资组合管理流程

1. **组合创建与配置**：
   - 用户创建新的投资组合，设置基本信息
   - 配置组合的风险偏好、目标收益率和基准
   - 可选择导入现有组合或使用模板创建

2. **持仓管理**：
   - 用户可添加、删除、调整组合中的个股持仓
   - 系统实时计算持仓权重和盈亏情况
   - 提供持仓分析视图（行业分布、因子暴露等）

3. **组合分析**：
   - 系统展示组合的业绩和风险指标
   - 提供历史表现图表和基准对比
   - 进行风险敞口和压力测试分析

4. **组合优化**：
   - 用户选择优化目标（最大化收益、最小化风险、风险平价等）
   - 设置优化约束条件
   - 系统生成优化方案和调整建议
   - 用户可选择接受优化建议或手动调整

### 5.2 响应式设计

系统采用响应式设计，确保在不同设备上都能提供良好的用户体验：

- **桌面端**：完整展示所有功能，多列布局，详细数据展示
- **平板端**：优化布局，适当简化某些复杂图表，保持核心功能可用性
- **移动端**：单列布局，折叠复杂功能，重点突出关键数据和操作

### 5.3 实时数据更新策略

- **股票价格**：实时推送更新，确保数据时效性
- **估值模型参数**：定期更新，确保估值结果准确性
- **市场指标**：分钟级别更新，保持市场数据的实时性
- **投资组合数据**：持仓数据实时更新，统计指标定期计算
- **策略回测数据**：每日更新，确保回测结果的时效性

### 5.4 个性化设置

- **用户偏好设置**：允许用户配置常用估值模型和参数
- **自定义仪表盘**：用户可自定义首页展示内容和布局
- **提醒设置**：配置价格提醒、定期报告提醒等
- **主题设置**：支持浅色/深色主题切换，满足不同使用场景需求
- **数据展示格式**：用户可选择数据显示格式（如百分比、小数点位数等）

## 6. 部署与集成方案

### 6.1 微服务架构部署

估值决策系统作为投资辅助系统的核心模块，采用微服务架构部署，确保系统的高可用性、可扩展性和可维护性：

- **估值服务**：负责各类估值模型的计算和管理
- **决策服务**：负责投资决策的生成和管理
- **组合服务**：负责投资组合的管理和分析
- **策略服务**：负责投资策略的管理和回测
- **数据服务**：负责数据的存储、检索和管理
- **API网关**：统一接口管理，权限控制，流量限制
- **配置中心**：集中管理配置信息，支持动态配置更新
- **服务注册与发现**：实现服务的自动注册和发现
- **负载均衡**：确保服务的负载均衡和高可用性

### 6.2 与其他系统集成接口

#### 6.2.1 与市场数据中心集成

- **数据同步接口**：定期同步最新的股票行情、板块数据
- **实时数据推送接口**：接收市场数据的实时推送
- **历史数据查询接口**：查询历史行情和市场指标数据

#### 6.2.2 与行业估值分析系统集成

- **行业数据接口**：获取行业分类、行业估值水平等数据
- **行业对比接口**：获取个股与行业的对比分析数据

#### 6.2.3 与财务分析引擎集成

- **财务数据接口**：获取财务报表、财务指标等数据
- **财务分析结果接口**：获取财务分析结果和评级数据

#### 6.2.4 与用户认证系统集成

- **用户认证接口**：实现用户登录、注册、认证
- **权限管理接口**：实现基于角色的权限控制
- **用户偏好接口**：管理用户的个性化设置和偏好

### 6.3 部署环境要求

- **服务器**：至少4台高性能服务器，支持负载均衡
- **内存**：每台服务器至少16GB内存
- **存储**：SSD存储，至少500GB可用空间
- **网络**：千兆网络，确保服务间通信高效稳定
- **操作系统**：Linux CentOS 7.0+或Ubuntu 18.04+
- **容器化**：使用Docker进行容器化部署
- **编排工具**：使用Kubernetes进行容器编排和管理
- **监控系统**：Prometheus + Grafana监控系统性能
- **日志系统**：ELK Stack集中管理日志

## 7. 安全性考虑

### 7.1 数据安全

1. **数据加密**：
   - 所有敏感数据在传输和存储过程中进行加密处理
   - 使用HTTPS确保API通信安全
   - 数据库敏感字段加密存储

2. **数据访问控制**：
   - 实现严格的基于角色的访问控制(RBAC)
   - 对数据访问进行审计和日志记录
   - 限制数据查询范围，防止数据泄露

3. **数据备份与恢复**：
   - 制定完善的数据备份策略，定期进行数据备份
   - 备份数据异地存储，确保数据安全
   - 定期进行恢复演练，确保数据可恢复性

### 7.2 系统安全

1. **认证与授权**：
   - 实现多因素认证机制
   - 严格的会话管理，定期更新令牌
   - 细粒度的权限控制，最小权限原则

2. **接口安全**：
   - API接口限流，防止恶意请求
   - 请求参数严格验证，防止注入攻击
   - 接口调用审计日志记录

3. **漏洞管理**：
   - 定期进行安全漏洞扫描
   - 及时更新系统组件和依赖库
   - 建立安全事件响应机制

## 8. 性能优化

### 8.1 前端优化

1. **资源优化**：
   - 代码压缩和合并，减少网络传输量
   - 使用CDN加速静态资源加载
   - 图片优化和懒加载

2. **渲染优化**：
   - 组件按需加载，减少初始加载时间
   - 虚拟滚动处理大量数据展示
   - 避免不必要的DOM操作和重绘

3. **数据处理优化**：
   - 前端缓存常用数据
   - 分页加载和数据分批处理
   - 合理使用WebWorker处理复杂计算

### 8.2 后端优化

1. **数据库优化**：
   - 合理设计索引，优化查询性能
   - 数据库读写分离
   - 数据分片和分区
   - 定期进行数据库维护和优化

2. **缓存优化**：
   - 使用Redis等缓存技术缓存热点数据
   - 合理设置缓存策略和过期时间
   - 缓存预热和缓存穿透防护

3. **计算优化**：
   - 优化复杂计算算法，提高计算效率
   - 使用异步计算处理耗时操作
   - 计算结果缓存，避免重复计算

4. **服务优化**：
   - 服务拆分，提高服务独立性和可扩展性
   - 使用连接池管理数据库连接
   - 异步处理非核心业务逻辑

## 9. 监控与告警

### 9.1 系统监控

1. **性能监控**：
   - 服务响应时间监控
   - 系统资源使用率监控（CPU、内存、磁盘、网络）
   - 数据库性能监控
   - API调用次数和延迟监控

2. **业务监控**：
   - 估值模型计算成功率监控
   - 决策生成质量监控
   - 组合管理操作监控
   - 策略回测性能监控

3. **数据监控**：
   - 数据更新及时性监控
   - 数据完整性监控
   - 数据准确性校验

### 9.2 告警机制

1. **告警级别**：
   - 紧急告警：系统不可用或关键功能异常
   - 重要告警：性能异常或业务数据异常
   - 一般告警：需要关注的异常情况

2. **告警渠道**：
   - 邮件告警
   - 短信告警
   - 企业微信/钉钉告警
   - 告警平台集中管理

3. **告警策略**：
   - 多级阈值告警
   - 告警抑制和聚合，避免告警风暴
   - 告警升级机制
   - 告警自动恢复通知

## 10. 后续扩展规划

### 10.1 功能扩展

1. **AI辅助估值**：
   - 引入机器学习模型，提高估值准确性
   - 自动参数优化和模型选择
   - 基于历史数据的估值偏差修正

2. **多资产类别支持**：
   - 扩展至债券、基金等多资产类别
   - 资产配置优化功能增强
   - 跨资产类别比较分析

3. **社交功能**：
   - 投资决策分享
   - 策略社区建设
   - 专家观点互动

4. **知识图谱集成**：
   - 公司关联关系分析
   - 产业链全景展示
   - 风险传导路径分析

### 10.2 技术升级

1. **架构升级**：
   - 微服务架构进一步优化
   - 引入服务网格技术
   - 探索Serverless架构应用

2. **数据处理能力提升**：
   - 引入大数据处理框架
   - 实时计算能力增强
   - 数据湖技术应用

3. **前端技术升级**：
   - 探索WebAssembly提升前端计算能力
   - 增强数据可视化交互体验
   - 提升移动端适配能力

4. **安全技术升级**：
   - 区块链技术在数据安全中的应用
   - 更高级的数据加密技术
   - AI驱动的安全威胁检测

## 11. 总结

估值决策系统作为投资辅助系统的核心模块，通过整合多维度数据、应用多种估值模型和投资理论，为投资者提供全面、科学的估值分析和投资决策支持。系统设计采用现代微服务架构，确保了高可用性、可扩展性和安全性，同时注重用户体验，提供直观、易用的界面交互。

未来，系统将持续优化估值模型的准确性和稳定性，扩展更多资产类别和分析维度，并探索AI、大数据等新技术在投资分析中的应用，不断提升系统的智能化水平和服务能力，为投资者提供更专业、更全面的投资决策支持。