<template>
  <div class="investment-record-container">
    <h1>投资记录管理</h1>
    
    <!-- 添加投资记录按钮 -->
    <div class="action-bar">
      <button @click="showAddForm = true" class="add-button">添加投资记录</button>
      <button @click="exportData" class="export-button">导出数据</button>
    </div>
    
    <!-- 投资记录列表 -->
    <div class="records-section">
      <h2>投资记录列表</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error-message">{{ error }}</div>
      <div v-else-if="investmentRecords.length === 0" class="empty-state">
        暂无投资记录，点击"添加投资记录"开始记录您的投资
      </div>
      <div v-else class="records-table-wrapper">
        <table class="records-table">
          <thead>
            <tr>
              <th>股票代码</th>
              <th>股票名称</th>
              <th>交易类型</th>
              <th>交易日期</th>
              <th>成交价格</th>
              <th>交易数量</th>
              <th>交易金额</th>
              <th>当前市值</th>
              <th>盈亏金额</th>
              <th>盈亏比例</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in investmentRecords" :key="record.id">
              <td>{{ record.stockCode }}</td>
              <td>{{ record.stockName }}</td>
              <td :class="record.transactionType === 'buy' ? 'buy-type' : 'sell-type'">
                {{ record.transactionType === 'buy' ? '买入' : '卖出' }}
              </td>
              <td>{{ formatDate(record.transactionDate) }}</td>
              <td>¥{{ record.price }}</td>
              <td>{{ record.quantity }}</td>
              <td>¥{{ record.amount }}</td>
              <td>¥{{ calculateCurrentValue(record) }}</td>
              <td :class="calculateProfit(record) >= 0 ? 'profit-positive' : 'profit-negative'">
                ¥{{ calculateProfit(record).toFixed(2) }}
              </td>
              <td :class="calculateProfitPercentage(record) >= 0 ? 'profit-positive' : 'profit-negative'">
                {{ calculateProfitPercentage(record) >= 0 ? '+' : '' }}{{ calculateProfitPercentage(record).toFixed(2) }}%
              </td>
              <td class="actions">
                <button @click="editRecord(record)" class="edit-button">编辑</button>
                <button @click="deleteRecord(record.id)" class="delete-button">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 投资组合分析 -->
    <div class="analysis-section">
      <h2>投资组合分析</h2>
      <div class="analysis-cards">
        <div class="analysis-card">
          <h3>总投资额</h3>
          <p class="amount">¥{{ totalInvestment }}</p>
        </div>
        <div class="analysis-card">
          <h3>当前市值</h3>
          <p class="amount">¥{{ totalCurrentValue }}</p>
        </div>
        <div class="analysis-card" :class="totalProfit >= 0 ? 'profit-positive' : 'profit-negative'">
          <h3>总盈亏</h3>
          <p class="amount">¥{{ totalProfit.toFixed(2) }}</p>
          <p class="percentage">{{ totalProfitPercentage >= 0 ? '+' : '' }}{{ totalProfitPercentage.toFixed(2) }}%</p>
        </div>
        <div class="analysis-card">
          <h3>最大回撤</h3>
          <p class="amount">{{ maxDrawdown.toFixed(2) }}%</p>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑投资记录对话框 -->
    <div v-if="showAddForm" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingRecord ? '编辑投资记录' : '添加投资记录' }}</h3>
          <button @click="closeModal" class="close-button">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveRecord">
            <div class="form-group">
              <label for="stockCode">股票代码:</label>
              <input type="text" id="stockCode" v-model="formData.stockCode" required>
            </div>
            <div class="form-group">
              <label for="stockName">股票名称:</label>
              <input type="text" id="stockName" v-model="formData.stockName" required>
            </div>
            <div class="form-group">
              <label>交易类型:</label>
              <div class="radio-group">
                <label>
                  <input type="radio" value="buy" v-model="formData.transactionType" required>
                  买入
                </label>
                <label>
                  <input type="radio" value="sell" v-model="formData.transactionType" required>
                  卖出
                </label>
              </div>
            </div>
            <div class="form-group">
              <label for="transactionDate">交易日期:</label>
              <input type="date" id="transactionDate" v-model="formData.transactionDate" required>
            </div>
            <div class="form-group">
              <label for="price">成交价格 (¥):</label>
              <input type="number" id="price" v-model.number="formData.price" step="0.01" required>
            </div>
            <div class="form-group">
              <label for="quantity">交易数量:</label>
              <input type="number" id="quantity" v-model.number="formData.quantity" min="1" required>
            </div>
            <div class="form-group">
              <label for="amount">交易金额 (¥):</label>
              <input type="number" id="amount" v-model.number="formData.amount" step="0.01" required>
            </div>
            <div class="form-actions">
              <button type="submit" class="save-button">保存</button>
              <button type="button" @click="closeModal" class="cancel-button">取消</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { apiService } from '../services/apiService';

interface InvestmentRecord {
  id: string;
  stockCode: string;
  stockName: string;
  transactionType: 'buy' | 'sell';
  transactionDate: string;
  price: number;
  quantity: number;
  amount: number;
  currentPrice?: number;
}

interface FormData {
  stockCode: string;
  stockName: string;
  transactionType: 'buy' | 'sell';
  transactionDate: string;
  price: number;
  quantity: number;
  amount: number;
}

// 响应式数据
const investmentRecords = ref<InvestmentRecord[]>([]);
const loading = ref(false);
const error = ref('');
const showAddForm = ref(false);
const editingRecord = ref<InvestmentRecord | null>(null);
const formData = ref<FormData>({
  stockCode: '',
  stockName: '',
  transactionType: 'buy',
  transactionDate: (new Date().toISOString().split('T')[0]) || '',
  price: 0,
  quantity: 0,
  amount: 0
});

// 计算属性
const totalInvestment = computed(() => {
  return investmentRecords.value
    .filter(record => record.transactionType === 'buy')
    .reduce((sum, record) => sum + record.amount, 0)
    .toFixed(2);
});

const totalCurrentValue = computed(() => {
  return investmentRecords.value
    .filter(record => record.transactionType === 'buy')
    .reduce((sum, record) => {
      const currentPrice = record.currentPrice || record.price;
      return sum + (currentPrice * record.quantity);
    }, 0)
    .toFixed(2);
});

const totalProfit = computed(() => {
  const investment = investmentRecords.value
    .filter(record => record.transactionType === 'buy')
    .reduce((sum, record) => sum + record.amount, 0);
    
  const value = investmentRecords.value
    .filter(record => record.transactionType === 'buy')
    .reduce((sum, record) => {
      const currentPrice = record.currentPrice || record.price;
      return sum + (currentPrice * record.quantity);
    }, 0);
    
  return value - investment;
});

const totalProfitPercentage = computed(() => {
  const investment = investmentRecords.value
    .filter(record => record.transactionType === 'buy')
    .reduce((sum, record) => sum + record.amount, 0);
    
  if (investment === 0) return 0;
  return (totalProfit.value / investment) * 100;
});

const maxDrawdown = computed(() => {
  // 从API获取的历史数据计算最大回撤
  // 目前返回0，实际应在API可用后实现正确计算
  return 0;
});

// 生命周期
onMounted(() => {
  loadInvestmentRecords();
});

// 方法
const loadInvestmentRecords = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    // 调用API获取投资记录
    const response = await apiService.investmentApi.getInvestmentRecords();
    const typedResponse = response as any;
    if (typedResponse.success && typedResponse.data) {
      investmentRecords.value = typedResponse.data as any;
    }
    // 更新股票当前价格
    await updateCurrentPrices();
  } catch (err) {
    console.error('加载投资记录失败:', err);
    error.value = '加载投资记录失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

const updateCurrentPrices = async () => {
    for (const record of investmentRecords.value) {
      try {
        // 暂时使用模拟数据，避免api调用错误
        record.currentPrice = record.price; // 使用购买价格作为默认值
      } catch (err) {
        console.error(`获取${record.stockCode}当前价格失败:`, err);
      }
  }
};

// 移除模拟数据，使用Tushare API真实数据源

const calculateCurrentValue = (record: InvestmentRecord): number => {
  const currentPrice = record.currentPrice || record.price;
  return currentPrice * record.quantity;
};

const calculateProfit = (record: InvestmentRecord): number => {
  if (record.transactionType === 'sell') {
    // 简化处理，实际应考虑买入成本
    return 0;
  }
  const currentValue = calculateCurrentValue(record);
  return currentValue - record.amount;
};

const calculateProfitPercentage = (record: InvestmentRecord): number => {
  if (record.amount === 0) return 0;
  return (calculateProfit(record) / record.amount) * 100;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

// 表单数据初始化 - 暂时注释掉未使用的函数
// const initializeForm = () => {
//   formData.value = {
//     stockCode: '',
//     stockName: '',
//     transactionType: 'buy',
//     transactionDate: (new Date().toISOString().split('T')[0]) || '',
//     price: 0,
//     quantity: 0,
//     amount: 0
//   };
// };

// const openAddForm = () => {
//   editingRecord.value = null;
//   showAddForm.value = true;
//   initializeForm();
// };

const editRecord = (record: InvestmentRecord) => {
  editingRecord.value = record;
  formData.value = {
    stockCode: record.stockCode,
    stockName: record.stockName,
    transactionType: record.transactionType,
    transactionDate: record.transactionDate,
    price: record.price,
    quantity: record.quantity,
    amount: record.amount
  };
  showAddForm.value = true;
};

const closeModal = () => {
  showAddForm.value = false;
  editingRecord.value = null;
};

const saveRecord = async () => {
  try {
    // 计算金额
    if (formData.value.amount === 0) {
      formData.value.amount = formData.value.price * formData.value.quantity;
    }
    
    const recordData = {
      ...formData.value,
      amount: formData.value.amount
    };
    
    let response;
    if (editingRecord.value) {
      // 编辑现有记录
      response = await apiService.investmentApi.updateInvestmentRecord(editingRecord.value.id, recordData);
    } else {
      // 添加新记录
      response = await apiService.investmentApi.addInvestmentRecord(recordData);
    }
    
    if ((response as any).success) {
      closeModal();
      await loadInvestmentRecords(); // 重新加载数据
    }
  } catch (err) {
    console.error('保存投资记录失败:', err);
    error.value = '保存投资记录失败，请稍后重试';
  }
};

const deleteRecord = async (id: string) => {
  if (confirm('确定要删除这条投资记录吗？')) {
    try {
      const response = await apiService.investmentApi.deleteInvestmentRecord(id);
      if ((response as any).success) {
        await loadInvestmentRecords(); // 重新加载数据
      }
    } catch (err) {
      console.error('删除投资记录失败:', err);
      error.value = '删除投资记录失败，请稍后重试';
    }
  }
};

const exportData = () => {
  // 导出功能实现
  alert('数据导出功能即将实现');
};
</script>

<style scoped>
.investment-record-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

h2 {
  color: #444;
  margin-top: 30px;
  margin-bottom: 15px;
}

.action-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.add-button, .export-button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.add-button {
  background-color: #4a6cf7;
  color: white;
}

.add-button:hover {
  background-color: #3a5be7;
}

.export-button {
  background-color: #28a745;
  color: white;
}

.export-button:hover {
  background-color: #218838;
}

.records-table-wrapper {
  overflow-x: auto;
}

.records-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.records-table th, .records-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.records-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.records-table tr:hover {
  background-color: #f5f5f5;
}

.buy-type {
  color: #28a745;
  font-weight: 600;
}

.sell-type {
  color: #dc3545;
  font-weight: 600;
}

.profit-positive {
  color: #28a745;
  font-weight: 600;
}

.profit-negative {
  color: #dc3545;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 5px;
}

.edit-button, .delete-button {
  padding: 5px 10px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.edit-button {
  background-color: #007bff;
  color: white;
}

.edit-button:hover {
  background-color: #0056b3;
}

.delete-button {
  background-color: #dc3545;
  color: white;
}

.delete-button:hover {
  background-color: #c82333;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-message {
  padding: 15px;
  background-color: #f8d7da;
  color: #721c24;
  border-radius: 4px;
  margin-bottom: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #666;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px dashed #ddd;
}

.analysis-section {
  margin-top: 40px;
}

.analysis-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.analysis-card {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  text-align: center;
  transition: transform 0.3s;
}

.analysis-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.analysis-card h3 {
  color: #666;
  font-size: 16px;
  margin-bottom: 10px;
  font-weight: normal;
}

.analysis-card .amount {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.analysis-card .percentage {
  font-size: 16px;
  margin-top: 5px;
}

/* 模态框样式 */
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
}

.modal-content {
  background-color: white;
  padding: 0;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ddd;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="date"] {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-group label {
  font-weight: normal;
  display: flex;
  align-items: center;
  gap: 5px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.save-button, .cancel-button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.save-button {
  background-color: #4a6cf7;
  color: white;
}

.save-button:hover {
  background-color: #3a5be7;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
}

.cancel-button:hover {
  background-color: #5a6268;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .analysis-cards {
    grid-template-columns: 1fr;
  }
  
  .action-bar {
    flex-direction: column;
  }
  
  .records-table {
    font-size: 12px;
  }
  
  .records-table th, .records-table td {
    padding: 8px;
  }
}
</style>