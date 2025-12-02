<template>
  <div class="position-analysis-container">
    <div class="page-header">
      <h2 class="page-title">持仓分析</h2>
    </div>

    <!-- 总体盈亏概览 -->
    <div class="overview-cards">
      <div class="card overview-card">
        <div class="card-title">总投入成本</div>
        <div class="card-value">¥{{ totalCost.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
      </div>
      <div class="card overview-card">
        <div class="card-title">当前市值</div>
        <div class="card-value">¥{{ totalValue.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
      </div>
      <div class="card overview-card" :class="{ 'profit': totalProfit >= 0, 'loss': totalProfit < 0 }">
        <div class="card-title">总盈亏</div>
        <div class="card-value">
          {{ totalProfit >= 0 ? '+' : '' }}¥{{ Math.abs(totalProfit).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </div>
        <div class="card-subtitle">{{ totalProfitRate >= 0 ? '+' : '' }}{{ totalProfitRate.toFixed(2) }}%</div>
      </div>
    </div>

    <!-- 持仓列表 -->
    <div class="positions-table-container">
      <h3 class="section-title">持仓明细</h3>
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>
      <div v-else-if="positions.length === 0" class="empty-state">
        <i class="icon">📊</i>
        <p>暂无持仓数据</p>
        <button class="btn primary" @click="openAddPositionModal">添加持仓</button>
      </div>
      <table v-else class="positions-table">
        <thead>
          <tr>
            <th>股票名称</th>
            <th>股票代码</th>
            <th>持有数量</th>
            <th>当前成本(元)</th>
            <th>当前价格(元)</th>
            <th>总成本(元)</th>
            <th>当前市值(元)</th>
            <th>盈亏金额(元)</th>
            <th>盈亏比例(%)</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="position in positions" :key="position.stockCode">
            <td>{{ position.stockName }}</td>
            <td>{{ position.stockCode }}</td>
            <td>{{ position.holdingQuantity }}</td>
            <td>{{ position.currentCost.toFixed(2) }}</td>
            <td>{{ position.currentPrice.toFixed(2) }}</td>
            <td>{{ position.totalCost.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
            <td>{{ position.currentValue.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
            <td :class="{ 'profit': position.profitAmount >= 0, 'loss': position.profitAmount < 0 }">
              {{ position.profitAmount >= 0 ? '+' : '' }}{{ position.profitAmount.toFixed(2) }}
            </td>
            <td :class="{ 'profit': position.profitRate >= 0, 'loss': position.profitRate < 0 }">
              {{ position.profitRate >= 0 ? '+' : '' }}{{ position.profitRate.toFixed(2) }}
            </td>
            <td>
              <div class="action-buttons">
                <button class="btn btn-secondary btn-sm" @click="openEditPositionModal(position)">编辑</button>
                <button class="btn btn-danger btn-sm" @click="deletePosition(position.stockCode)">删除</button>
                <button class="btn btn-primary btn-sm" @click="openAdditionalPurchaseModal(position)">补仓测算</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 添加/编辑持仓模态框 -->
    <teleport to="body">
      <div v-if="positionModalOpen" class="modal-backdrop" @click.self="closePositionModal">
        <div class="modal-container">
          <div class="modal-header">
            <h3 class="modal-title">{{ isEditing ? '编辑持仓' : '添加持仓' }}</h3>
            <button class="modal-close" @click="closePositionModal">✕</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="savePosition">
              <div class="form-group">
                <label>股票名称</label>
                <input v-model="positionForm.stockName" type="text" placeholder="请输入股票名称" required>
              </div>
              <div class="form-group">
                <label>股票代码</label>
                <input v-model="positionForm.stockCode" type="text" placeholder="请输入股票代码" required>
              </div>
              <div class="form-group">
                <label>持有数量</label>
                <input v-model.number="positionForm.holdingQuantity" type="number" min="1" placeholder="请输入持有数量" required>
              </div>
              <div class="form-group">
                <label>当前成本(元)</label>
                <input v-model.number="positionForm.currentCost" type="number" step="0.01" min="0" placeholder="请输入当前成本" required>
              </div>
              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="closePositionModal">取消</button>
                <button type="submit" class="btn primary">{{ isEditing ? '保存修改' : '添加' }}</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </teleport>

    <!-- 补仓测算模态框 -->
    <teleport to="body">
      <div v-if="additionalModalOpen" class="modal-backdrop" @click.self="closeAdditionalPurchaseModal">
        <div class="modal-container">
          <div class="modal-header">
            <h3 class="modal-title">补仓测算 - {{ selectedPosition?.stockName }}({{ selectedPosition?.stockCode }})</h3>
            <button class="modal-close" @click="closeAdditionalPurchaseModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="current-info">
              <h4>当前持仓信息</h4>
              <div class="info-grid">
                <div>持有数量: {{ selectedPosition?.holdingQuantity }} 股</div>
                <div>当前成本: ¥{{ selectedPosition?.currentCost.toFixed(2) }}</div>
                <div>当前价格: ¥{{ selectedPosition?.currentPrice.toFixed(2) }}</div>
                <div>总成本: ¥{{ selectedPosition?.totalCost.toFixed(2) }}</div>
              </div>
            </div>
            
            <div class="additional-form">
              <h4>补仓信息</h4>
              <form @submit.prevent="calculateAdditionalPurchase">
                <div class="form-group">
                  <label>补仓价格(元)</label>
                  <input v-model.number="additionalForm.price" type="number" step="0.01" min="0" placeholder="请输入补仓价格" required>
                </div>
                <div class="form-group">
                  <label>补仓数量(股)</label>
                  <input v-model.number="additionalForm.quantity" type="number" min="1" placeholder="请输入补仓数量" required>
                </div>
                <div class="form-actions">
                  <button type="submit" class="btn primary">计算</button>
                </div>
              </form>
            </div>
            
            <div v-if="additionalResult" class="result-section">
              <h4>补仓后预测结果</h4>
              <div class="result-grid">
                <div class="result-item">
                  <span class="result-label">总持仓数量:</span>
                  <span class="result-value">{{ additionalResult.totalQuantityAfter }} 股</span>
                </div>
                <div class="result-item">
                  <span class="result-label">总成本:</span>
                  <span class="result-value">¥{{ additionalResult.totalCostAfter.toFixed(2) }}</span>
                </div>
                <div class="result-item">
                  <span class="result-label">平均成本:</span>
                  <span class="result-value">¥{{ additionalResult.averageCostAfter.toFixed(2) }}</span>
                </div>
                <div class="result-item">
                  <span class="result-label">总市值:</span>
                  <span class="result-value">¥{{ additionalResult.totalValueAfter.toFixed(2) }}</span>
                </div>
                <div class="result-item" :class="{ 'profit': additionalResult.profitAmountAfter >= 0, 'loss': additionalResult.profitAmountAfter < 0 }">
                  <span class="result-label">总盈亏:</span>
                  <span class="result-value">
                    {{ additionalResult.profitAmountAfter >= 0 ? '+' : '' }}¥{{ additionalResult.profitAmountAfter.toFixed(2) }}
                  </span>
                </div>
                <div class="result-item" :class="{ 'profit': additionalResult.profitRateAfter >= 0, 'loss': additionalResult.profitRateAfter < 0 }">
                  <span class="result-label">盈亏比例:</span>
                  <span class="result-value">
                    {{ additionalResult.profitRateAfter >= 0 ? '+' : '' }}{{ additionalResult.profitRateAfter.toFixed(2) }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import positionAnalysisService from '../api/positionAnalysisService.js';

// 状态定义
const positions = ref([]);
const loading = ref(false);
const positionModalOpen = ref(false);
const additionalModalOpen = ref(false);
const isEditing = ref(false);
const selectedPosition = ref(null);
const additionalResult = ref(null);

// 表单数据
const positionForm = ref({
  stockName: '',
  stockCode: '',
  holdingQuantity: 0,
  currentCost: 0
});

const additionalForm = ref({
  price: 0,
  quantity: 0
});

// 计算总览数据
const totalCost = computed(() => {
  return positions.value.reduce((sum, pos) => sum + (pos.totalCost || 0), 0);
});

const totalValue = computed(() => {
  return positions.value.reduce((sum, pos) => sum + (pos.currentValue || 0), 0);
});

const totalProfit = computed(() => {
  return totalValue.value - totalCost.value;
});

const totalProfitRate = computed(() => {
  return totalCost.value > 0 ? (totalProfit.value / totalCost.value) * 100 : 0;
});

// 获取持仓数据
const fetchPositions = async () => {
  loading.value = true;
  try {
    positions.value = await positionAnalysisService.getStockPositions();
  } catch (error) {
    console.error('获取持仓数据失败:', error);
    alert('获取数据失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 保存持仓数据
const savePosition = async () => {
  try {
    await positionAnalysisService.saveStockPosition(positionForm.value);
    await fetchPositions();
    closePositionModal();
    alert(isEditing.value ? '持仓更新成功' : '持仓添加成功');
  } catch (error) {
    console.error('保存持仓失败:', error);
    alert('保存失败，请稍后重试');
  }
};

// 删除持仓
const deletePosition = async (positionId) => {
  if (!confirm('确定要删除这个持仓吗？')) return;
  
  try {
    await positionAnalysisService.deleteStockPosition(positionId);
    await fetchPositions();
    alert('持仓删除成功');
  } catch (error) {
    console.error('删除持仓失败:', error);
    alert('删除失败，请稍后重试');
  }
};

// 计算补仓结果
const calculateAdditionalPurchase = async () => {
  try {
    additionalResult.value = await positionAnalysisService.calculateAdditionalPurchase(
      selectedPosition.value,
      additionalForm.value.price,
      additionalForm.value.quantity
    );
  } catch (error) {
    console.error('计算补仓预测失败:', error);
    alert('计算失败，请稍后重试');
  }
};

// 模态框控制方法
const openAddPositionModal = () => {
  isEditing.value = false;
  positionForm.value = {
    stockName: '',
    stockCode: '',
    holdingQuantity: 0,
    currentCost: 0
  };
  positionModalOpen.value = true;
};

const openEditPositionModal = (position) => {
  isEditing.value = true;
  positionForm.value = {
    stockName: position.stockName,
    stockCode: position.stockCode,
    holdingQuantity: position.holdingQuantity,
    currentCost: position.currentCost
  };
  positionModalOpen.value = true;
};

const closePositionModal = () => {
  positionModalOpen.value = false;
};

const openAdditionalPurchaseModal = (position) => {
  selectedPosition.value = position;
  additionalForm.value = {
    price: 0,
    quantity: 0
  };
  additionalResult.value = null;
  additionalModalOpen.value = true;
};

const closeAdditionalPurchaseModal = () => {
  additionalModalOpen.value = false;
};

// 组件挂载时获取数据
onMounted(() => {
  fetchPositions();
});
</script>

<style scoped>
.position-analysis-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.overview-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.overview-card .card-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.overview-card .card-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.overview-card .card-subtitle {
  font-size: 14px;
  margin-top: 4px;
}

.overview-card.profit {
  border-left: 4px solid #F5222D;
}

.overview-card.loss {
  border-left: 4px solid #52C41A;
}

.profit {
  color: #F5222D;
}

.loss {
  color: #52C41A;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

.positions-table-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading-container {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #165DFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #666;
}

.empty-state .icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.positions-table {
  width: 100%;
  border-collapse: collapse;
}

.positions-table th {
  background-color: #f7f8fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #e8e8e8;
}

.positions-table td {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.positions-table tr:hover {
  background-color: #fafafa;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.primary {
  background-color: #165DFF;
  color: white;
}

.primary:hover {
  background-color: #4080FF;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.btn-danger {
  background-color: #F5222D;
  color: white;
}

.btn-danger:hover {
  background-color: #ff4d4f;
}

/* 模态框样式 */
.modal-backdrop {
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
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
}

.modal-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #165DFF;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

/* 补仓测算相关样式 */
.current-info,
.additional-form,
.result-section {
  margin-bottom: 24px;
}

.current-info h4,
.additional-form h4,
.result-section h4 {
  margin-bottom: 12px;
  color: #333;
  font-size: 16px;
}

.info-grid,
.result-grid {
  background-color: #f7f8fa;
  padding: 16px;
  border-radius: 4px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.result-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e8e8e8;
}

.result-item:last-child {
  border-bottom: none;
}

.result-label {
  color: #666;
}

.result-value {
  font-weight: 500;
  color: #333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .positions-table {
    font-size: 14px;
  }
  
  .positions-table th,
  .positions-table td {
    padding: 8px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
