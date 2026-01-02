<template>
  <div class="notes-container">
    <div class="page-header">
      <h1>投资笔记</h1>
      <div class="header-actions">
        <div class="view-switcher">
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button label="card">
              <i class="el-icon-s-grid"></i>
              卡片视图
            </el-radio-button>
            <el-radio-button label="list">
              <i class="el-icon-menu"></i>
              列表视图
            </el-radio-button>
          </el-radio-group>
        </div>
        <button class="add-note-btn" @click="showNoteModal = true">
          <i class="el-icon-plus"></i>
          新建笔记
        </button>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="search-filter-section">
      <el-form :inline="true" size="small">
        <el-form-item label="搜索内容">
          <el-input
            v-model="searchKeyword"
            placeholder="输入关键词搜索笔记"
            clearable
            @input="handleSearch"
            style="width: 300px;"
          >
            <template #prefix>
              <i class="el-icon-search"></i>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="关联股票">
          <el-select
            v-model="selectedStock"
            placeholder="选择关联股票"
            filterable
            clearable
            allow-create
            @change="handleSearch"
            style="width: 200px;"
          >
            <el-option
              v-for="stock in availableStocks"
              :key="stock.value"
              :label="stock.label"
              :value="stock.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 笔记列表 - 卡片视图 -->
    <div class="notes-grid" v-if="viewMode === 'card'" v-loading="loading">
      <div
          v-for="note in filteredNotes"
          :key="note.id"
          class="note-card"
          @click="viewNote(note)"
        >
        <div class="note-header">
          <h3 class="note-title">{{ truncateText(note.title, 20) }}</h3>
          <div class="note-actions">
            <el-button
              type="text"
              size="small"
              @click.stop="editNote(note)"
            >
              编辑
            </el-button>
            <el-button
              type="text"
              size="small"
              @click.stop="confirmDelete(note)"
              class="delete-btn"
            >
              删除
            </el-button>
          </div>
        </div>
        <p class="note-content">{{ truncateText(note.content, 100) }}</p>
        <div class="note-footer">
          <span v-if="note.stockCode" class="stock-tag">
            <i class="el-icon-finished"></i>
            {{ getStockLabel(note.stockCode) }}
          </span>
          <span class="update-time">{{ formatDate(note.updateTime) }}</span>
        </div>
      </div>
      
      <div v-if="!loading && filteredNotes.length === 0" class="empty-notes">
        <i class="el-icon-document"></i>
        <p>暂无笔记，点击上方按钮新建</p>
      </div>
    </div>

    <!-- 笔记列表 - 表格视图 -->
    <div class="notes-table-container" v-else-if="viewMode === 'list'" v-loading="loading">
      <el-table
        :data="filteredNotes"
        style="width: 100%"
        @row-click="handleTableRowClick"
      >
        <el-table-column
          prop="title"
          label="标题"
          min-width="200"
          show-overflow-tooltip
        >
          <template #default="scope">
            <span class="note-title-text">{{ scope.row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="content"
          label="内容"
          min-width="300"
        >
          <template #default="scope">
            <span class="note-content-text">
              <!-- 直接处理原始内容，确保没有HTML标签 -->
              {{ truncateText(scope.row.content, 100) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          label="关联股票"
          width="200"
        >
          <template #default="scope">
            <div v-if="scope.row.stockCode" class="stock-tags">
              <el-tag v-for="code in scope.row.stockCode.split(',')" :key="code" size="small" type="primary" effect="plain" class="mr-1 mb-1">
                {{ getStockLabel(code) }}
              </el-tag>
            </div>
            <span v-else class="text-gray-400">无</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="createTime"
          label="创建时间"
          width="160"
          sortable
        >
          <template #default="scope">
            <span>{{ formatDate(scope.row.createTime) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="updateTime"
          label="更新时间"
          width="160"
          sortable
        >
          <template #default="scope">
            <span>{{ formatDate(scope.row.updateTime) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="source"
          label="来源"
          width="120"
        >
          <template #default="scope">
            <el-tag size="small" type="info" effect="plain">
              {{ scope.row.source || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="180"
          fixed="right"
        >
          <template #default="scope">
            <div class="table-actions">
              <el-button
                type="primary"
                size="small"
                round
                @click.stop="viewNote(scope.row)"
              >
                查看
              </el-button>
              <el-button
                type="success"
                size="small"
                round
                @click.stop="editNote(scope.row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                round
                @click.stop="confirmDelete(scope.row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="!loading && notes.length === 0" class="empty-notes">
        <i class="el-icon-document"></i>
        <p>暂无笔记，点击上方按钮新建</p>
      </div>
    </div>

    <!-- 笔记详情弹窗 -->
    <el-dialog
      v-model="showNoteDetail"
      :title="selectedNote?.title || '笔记详情'"
      width="700px"
      :before-close="closeNoteDetail"
    >
      <div class="note-detail">
        <div class="note-meta">
          <span>创建时间: {{ formatDate(selectedNote?.createTime) }}</span>
          <span>更新时间: {{ formatDate(selectedNote?.updateTime) }}</span>
        </div>
        <div class="note-content-detail">
          <div v-if="selectedNote?.stockCode" class="related-stock-info">
            <el-tag
              v-for="stockCode in selectedNote.stockCode.split(',')"
              :key="stockCode"
              size="small"
              effect="plain"
              type="primary"
              class="mr-1 mb-1"
            >
              <i class="el-icon-finished"></i>
              {{ getStockLabel(stockCode) }}
            </el-tag>
          </div>
          <div class="note-content-rendered" v-html="renderNoteContent(selectedNote?.content || '')"></div>
        </div>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <el-button @click="closeNoteDetail">关闭</el-button>
        <el-button type="primary" @click="editCurrentNote">编辑</el-button>
      </div>
    </el-dialog>

    <!-- 添加/编辑笔记弹窗 -->
    <!-- 添加/编辑笔记弹窗 - 增加宽度百分比, 更好适应不同屏幕 -->
    <el-dialog
      v-model="showNoteModal"
      :title="editingNote ? '编辑笔记' : '新建笔记'"
      width="85%"
      :fullscreen="false"
      append-to-body
    >
      <el-form
        ref="noteFormRef"
        :model="noteForm"
        :rules="noteFormRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="noteForm.title" placeholder="请输入笔记标题" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="关联股票" prop="relatedStock">
          <div class="stock-search-container">
            <!-- 股票搜索 -->
            <div class="relative">
              <div class="flex items-center space-x-2">
                <div class="flex-1">
                  <!-- 带标签的输入框 -->
                  <div class="flex flex-wrap items-center border border-gray-300 rounded-md px-3 py-2 bg-white focus-within:border-transparent">
                    <!-- 已选股票标签 -->
                    <div
                      v-for="stock in selectedStocks"
                      :key="stock.stockCode"
                      class="inline-flex items-center px-1.5 py-1.5 rounded-md bg-[#e6f7ff] text-[#9370db] text-sm font-medium mr-2 mb-0.5 border border-[#91d5ff]"
                    >
                      {{ stock.stockCode }} {{ stock.stockName }}
                      <button
                        @click="removeStock(stock.stockCode)"
                        class="ml-1 text-[#7b68ee] hover:text-white focus:outline-none w-4 h-4 flex items-center justify-center text-xs rounded-full hover:bg-[#7b68ee] transition-colors duration-150"
                      >
                        ×
                      </button>
                    </div>
                    <!-- 输入框 -->
                    <input
                v-model="searchKeyword"
                placeholder="输入股票代码或名称，点击查询按钮搜索"
                class="flex-1 min-w-0 outline-none text-gray-700 text-sm py-1"
                @focus="handleSearchFocus"
              />
                  </div>
                </div>
                <button
                  type="button"
                  class="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-4 py-2 rounded-md hover:from-purple-700 hover:to-purple-800 transition-all shadow-md hover:shadow-lg whitespace-nowrap"
                  @click="handleStockSearch"
                  :disabled="!searchKeyword.trim()"
                >
                  查询
                </button>
              </div>
              <!-- 搜索结果下拉框 -->
              <div
                v-if="showSearchResults && searchResults.length > 0"
                class="absolute z-50 left-0 mt-1 bg-white rounded-md shadow-lg max-h-60 overflow-y-auto"
                style="width: calc(100% - 120px); max-height: 200px; overflow-y: auto; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); top: 100%; background-color: white; opacity: 1; border: none;"
              >
                <div
                  v-for="stock in searchResults"
                  :key="stock.stockCode"
                  class="px-4 py-2 hover:bg-purple-50 cursor-pointer transition-colors"
                  @mousedown.prevent="selectSearchResult(stock)"
                >
                  <div class="flex items-center">
                    <span class="font-medium text-purple-700">{{ stock.stockCode }}</span>
                    <span class="ml-2 text-gray-700">{{ stock.stockName }}</span>
                    <span v-if="stock.industry" class="ml-2 text-xs text-gray-500">{{ stock.industry }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <MarkdownEditor
            ref="markdownEditorRef"
            v-model="noteForm.content"
            height="400px"
            placeholder="请输入笔记内容，可直接粘贴图片（粘贴后图片将直接显示在文本中）"
            :show-action-buttons="true"
          >
            <template v-slot:action-buttons>
              <el-button @click="cancelAddEdit">取消</el-button>
              <el-button type="primary" @click="saveNote">保存</el-button>
            </template>
          </MarkdownEditor>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- 删除确认弹窗 -->
    <el-dialog
      v-model="showDeleteConfirm"
      title="确认删除"
      width="30%"
      center
    >
      <span>确定要删除笔记 "{{ selectedNoteForDelete?.title }}" 吗？</span>
      <div class="flex justify-end gap-2 mt-4">
        <el-button @click="showDeleteConfirm = false">取消</el-button>
        <el-button type="danger" @click="deleteNote">删除</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import apiService from '../api/apiService';
import { ElMessage, ElForm } from 'element-plus';
import MarkdownEditor from '../components/MarkdownEditor.vue';

// 组件名称
const name = 'ReviewNotesView';

// 响应式状态
const notes = ref([]);
const filteredNotes = ref([]);
const loading = ref(false);
const viewMode = ref('list'); // 默认使用列表视图
const searchKeyword = ref('');
const selectedStock = ref('');
const availableStocks = [
  { value: '600000', label: '浦发银行' },
  { value: '600036', label: '招商银行' },
  { value: '601318', label: '中国平安' },
  { value: '600519', label: '贵州茅台' },
  { value: '000001', label: '平安银行' },
  { value: '300750', label: '宁德时代' }
];
const showNoteDetail = ref(false);
const showNoteModal = ref(false);
const showDeleteConfirm = ref(false);
const editingNote = ref(null);
const selectedNote = ref(null);
const selectedNoteForDelete = ref(null);
const noteForm = reactive({
  title: '',
  content: '',
  stockCode: '',
  stockName: '',
  tags: '复盘笔记'
});
const noteFormRef = ref(null);
// 编辑器组件引用
const markdownEditorRef = ref(null);
const noteFormRules = {
  title: [
    { required: true, message: '请输入笔记标题', trigger: 'blur' },
    { min: 1, max: 50, message: '标题长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入笔记内容', trigger: 'blur' },
    { min: 1, max: 5000, message: '内容长度在 1 到 5000 个字符', trigger: 'blur' }
  ]
};
// 已选择股票的完整信息
const selectedStocks = ref([]);
// 搜索结果相关
const showSearchResults = ref(false);
const searchResults = ref([]);
const searchContainerRef = ref(null);
const searchInputContainerRef = ref(null);

// 获取笔记列表
async function fetchNotes() {
  loading.value = true;
  try {
    // 使用apiService中的getReviewNotes方法获取笔记列表
    const response = await apiService.getReviewNotes();
    notes.value = response;
    // 初始化筛选列表
    filteredNotes.value = [...notes.value];
    // 应用搜索条件
    if (searchKeyword.value || selectedStock.value) {
      handleSearch();
    }
  } catch (error) {
    console.error('获取笔记列表失败:', error);
    ElMessage.error('获取笔记列表失败');
  } finally {
    loading.value = false;
  }
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// 文本截断
function truncateText(text, maxLength) {
  if (!text) return '';
  // 去除HTML标签 - 更彻底的实现
  let plainText = text;
  // 首先移除所有HTML标签，包括自闭合标签
  plainText = plainText.replace(/<[^>]*>/g, '');
  // 然后移除可能的HTML实体
  plainText = plainText.replace(/&nbsp;/g, ' ');
  plainText = plainText.replace(/&lt;/g, '<');
  plainText = plainText.replace(/&gt;/g, '>');
  plainText = plainText.replace(/&amp;/g, '&');
  plainText = plainText.replace(/&quot;/g, '"');
  plainText = plainText.replace(/&#39;/g, "'");
  
  // 去除多余的空白字符
  plainText = plainText.replace(/\s+/g, ' ').trim();
  
  return plainText.length > maxLength ? plainText.substring(0, maxLength) + '...' : plainText;
}

// 查看笔记
function viewNote(note) {
  selectedNote.value = { ...note };
  showNoteDetail.value = true;
}

// 关闭笔记详情
function closeNoteDetail() {
  showNoteDetail.value = false;
  selectedNote.value = null;
}

// 编辑当前笔记
function editCurrentNote() {
  if (selectedNote.value) {
    editingNote.value = selectedNote.value;
    noteForm.title = selectedNote.value.title;
    noteForm.content = selectedNote.value.content;
    noteForm.stockCode = selectedNote.value.stockCode || '';
    noteForm.stockName = selectedNote.value.stockName || '';
    noteForm.tags = selectedNote.value.tags || '复盘笔记';
    
    // 重新加载股票的完整信息
    selectedStocks.value = [];
    if (noteForm.stockCode) {
      // 尝试从API获取股票完整信息
      apiService.getStocks(noteForm.stockCode).then(results => {
        if (results.length > 0) {
          selectedStocks.value.push(results[0]);
        }
      }).catch(error => {
        console.error('获取股票信息失败:', error);
      });
    }
    
    showNoteModal.value = true;
    showNoteDetail.value = false;
  }
}



// 处理搜索框获取焦点
function handleSearchFocus() {
  if (searchKeyword.value.trim()) {
    handleStockSearch();
  }
}

// 股票搜索方法
  async function handleStockSearch() {
  try {
    if (!searchKeyword.value.trim()) {
      searchResults.value = [];
      showSearchResults.value = false;
      return;
    }
    
    const results = await apiService.getStocks(searchKeyword.value.trim());
    searchResults.value = results;
    showSearchResults.value = true;
  } catch (error) {
    console.error('股票搜索失败:', error);
    ElMessage.error('股票搜索失败');
  }
}

// 选择搜索结果
function selectSearchResult(stock) {
  // 检查是否已选择该股票
  if (!selectedStocks.value.some(item => item.stockCode === stock.stockCode)) {
    selectedStocks.value.push(stock);
    // 如果是第一个选择的股票，设置为主关联股票
    if (selectedStocks.value.length === 1) {
      noteForm.stockCode = stock.stockCode;
      noteForm.stockName = stock.stockName;
    }
  }
  searchKeyword.value = '';
  searchResults.value = [];
  showSearchResults.value = false;
}

// 移除选中的股票
function removeStock(stockCode) {
  const index = selectedStocks.value.findIndex(item => item.stockCode === stockCode);
  if (index > -1) {
    selectedStocks.value.splice(index, 1);
    // 如果移除的是当前主股票，更新主股票信息
    if (noteForm.stockCode === stockCode && selectedStocks.value.length > 0) {
      noteForm.stockCode = selectedStocks.value[0].stockCode;
      noteForm.stockName = selectedStocks.value[0].stockName;
    } else if (selectedStocks.value.length === 0) {
      noteForm.stockCode = '';
      noteForm.stockName = '';
    }
  }
}



// 取消添加/编辑
function cancelAddEdit() {
  showNoteModal.value = false;
  editingNote.value = null;
  resetForm();
}

// 保存笔记
async function saveNote() {
  try {
    if (noteFormRef.value) {
      await noteFormRef.value.validate();
    }
    
    // 从MarkdownEditor组件获取最新的内容和标签数据
    const editorInstance = markdownEditorRef.value;
    const editorContent = editorInstance ? editorInstance.getContent() : noteForm.content;
    const editorTags = editorInstance ? editorInstance.getTags() : noteForm.tags;
    
    const noteData = {
      ...noteForm,
      content: editorContent,
      tags: editorTags,
      stockCode: noteForm.stockCode || '',
      stockName: noteForm.stockName || '',
      source: '复盘笔记'  // 添加来源字段，标识该笔记来自复盘笔记页
    };
    
    let response;
    if (editingNote.value) {
      // 更新笔记
      response = await apiService.updateReviewNote(editingNote.value.id, noteData);
      notes.value = notes.value.map(note => 
        note.id === editingNote.value.id ? { ...note, ...response } : note
      );
      ElMessage.success('更新成功');
    } else {
      // 创建新笔记
      response = await apiService.createReviewNote(noteData);
      notes.value.unshift(response);
      ElMessage.success('创建成功');
    }
    
    // 关闭弹窗并重置表单
    cancelAddEdit();
    
    // 应用当前的筛选条件
    applyFilters();
    
  } catch (error) {
    console.error('保存笔记失败:', error);
    if (error.response && error.response.data && error.response.data.detail) {
      ElMessage.error(error.response.data.detail || '保存失败');
    } else {
      ElMessage.error('保存失败，请重试');
    }
  }
}

// 确认删除
function confirmDelete(note) {
  selectedNoteForDelete.value = note;
  showDeleteConfirm.value = true;
}

// 删除笔记
async function deleteNote() {
  try {
    await apiService.deleteNote(selectedNoteForDelete.value.id);
    ElMessage.success('删除成功');
    showDeleteConfirm.value = false;
    selectedNoteForDelete.value = null;
    
    // 重新获取笔记列表
    fetchNotes();
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败，请重试');
  }
}

// 表格行点击
function handleTableRowClick(row) {
  // 表格行点击时查看详情
  viewNote(row);
}



// 获取股票名称
function getStockLabel(stockCode) {
  // 首先处理多个股票代码的情况
  if (stockCode && stockCode.includes(',')) {
    // 如果传入的是多个股票代码，返回第一个的名称
    return getStockLabel(stockCode.split(',')[0]);
  }
  
  // 首先检查当前笔记的stockName是否包含该股票的名称（支持多个股票的情况）
  const currentNote = notes.value.find(note => 
    note.stockCode && 
    note.stockCode.split(',').includes(stockCode)
  );
  if (currentNote && currentNote.stockName) {
    // 将stockName按逗号分割，与stockCode的顺序对应
    const stockCodes = currentNote.stockCode.split(',');
    const stockNames = currentNote.stockName.split(',');
    const index = stockCodes.indexOf(stockCode);
    if (index !== -1 && index < stockNames.length && stockNames[index]) {
      return stockNames[index];
    }
  }
  
  // 先从可用股票列表中查找
  const availableStock = availableStocks.find(s => s.value === stockCode);
  if (availableStock) {
    return availableStock.label;
  }
  
  // 再从已选择的股票信息中查找
  const selectedStock = selectedStocks.value.find(s => s.stockCode === stockCode);
  if (selectedStock) {
    return selectedStock.stockName;
  }
  
  // 如果都找不到，返回股票代码
  return stockCode;
}

// 渲染笔记内容
  function renderNoteContent(content) {
  if (!content) return '';
  
  // 简单替换换行和加粗
  let html = content;
  // 换行
  html = html.replace(/\n/g, '<br>');
  // 加粗
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // 斜体
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // 标题
  html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');
  html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
  html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
  // 列表
  html = html.replace(/^- (.*$)/gm, '<li>$1</li>');
  // 替换图片标记为图片标签 - 现在直接使用Base64数据
  html = html.replace(/\[图片:([^\]]+)\]/g, (match, imgData) => {
    // 直接使用Base64数据作为图片源
    return `<img src="${imgData}" class="content-image" alt="笔记图片" />`;
  });
  
  return html;
}

// 处理搜索
function handleSearch() {
  filteredNotes.value = notes.value.filter(note => {
    // 关键词搜索
    const keywordMatch = !searchKeyword.value || 
      note.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) || 
      note.content.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      (note.stockCode && note.stockCode.toLowerCase().includes(searchKeyword.value.toLowerCase())) ||
      (note.stockName && note.stockName.toLowerCase().includes(searchKeyword.value.toLowerCase()));
      
    // 股票筛选
    const stockMatch = !selectedStock.value || 
      (note.stockCode && note.stockCode.split(',').includes(selectedStock.value));
      
    return keywordMatch && stockMatch;
  });
}

// 编辑笔记
function editNote(note) {
  editingNote.value = note;
  noteForm.title = note.title;
  noteForm.content = note.content;
  noteForm.stockCode = note.stockCode || '';
  noteForm.stockName = note.stockName || '';
  noteForm.tags = note.tags || '复盘笔记';
  
  // 初始化已选择股票的完整信息
  selectedStocks.value = [];
  if (note.stockCode) {
    const stockCodes = note.stockCode.split(',');
    // 填充关联股票信息，优先使用本地数据和note中的stockName
     stockCodes.forEach(code => {
       // 先从本地availableStocks查找
       const localStock = availableStocks.find(s => s.value === code);
       if (localStock) {
        selectedStocks.value.push({
          stockCode: code,
          stockName: localStock.label
        });
      } else {
        // 尝试从note.stockName中获取股票名称
        let stockName = code;
        if (note.stockName) {
          const stockNames = note.stockName.split(',');
          const index = stockCodes.indexOf(code);
          if (index !== -1 && stockNames[index]) {
            stockName = stockNames[index];
          }
        }
        // 直接使用本地信息或从note中获取的信息，避免调用API
        selectedStocks.value.push({
          stockCode: code,
          stockName: stockName
        });
      }
    });
  }
  
  // 解析内容中的图片标记并恢复图片
  // 移除hasImages相关逻辑，因为图片直接存储在content中
  
  showNoteModal.value = true;
  // 如果打开了详情弹窗，先关闭
  closeNoteDetail();
  
  // 给编辑器设置标签
  setTimeout(() => {
    if (markdownEditorRef.value) {
      markdownEditorRef.value.setTags(note.tags || '复盘笔记');
    }
  }, 0);
}

// 重置表单
function resetForm() {
  noteForm.title = '';
  noteForm.content = '';
  noteForm.stockCode = '';
  noteForm.stockName = '';
  noteForm.tags = '复盘笔记';
  selectedStocks.value = [];
  searchKeyword.value = '';
  searchResults.value = [];
  showSearchResults.value = false;
  if (noteFormRef.value) {
    noteFormRef.value.resetFields();
  }
}

// 组件挂载时获取笔记列表
onMounted(() => {
  fetchNotes();
});
</script>

<style scoped>
.notes-container {
  padding: 24px;
  background-color: #f8f9fa;
  min-height: 100vh;
  background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  background: rgba(255, 255, 255, 0.95);
  padding: 20px 30px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.search-filter-section {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid #f0f0f0;
  transition: box-shadow 0.3s ease, transform 0.2s ease;
}

.search-filter-section:hover {
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

.view-switcher {
  background: linear-gradient(135deg, #f5f7fa 0%, #e6eaf0 100%);
  border-radius: 20px;
  padding: 4px;
  display: inline-flex;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.view-switcher:hover {
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.15);
}

.page-header h1 {
  font-size: 28px;
  margin: 0;
  color: #1a1a1a;
  font-weight: 700;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.add-note-btn {
  background: linear-gradient(135deg, #409eff, #67c23a);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.add-note-btn:hover {
  background: linear-gradient(135deg, #66b1ff, #85ce61);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
  transform: translateY(-2px);
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.note-card {
  background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  min-height: 200px;
  border: 1px solid #f0f0f0;
  overflow: hidden;
}

.note-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  transform: translateY(-6px);
  border-color: #e6f7ff;
}

.note-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #409eff 0%, #67c23a 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.note-card:hover::before {
  opacity: 1;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.note-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  flex: 1;
  word-break: break-word;
  line-height: 1.4;
  transition: color 0.3s ease;
}

.note-card:hover .note-title {
  color: #409eff;
}

.note-actions {
  opacity: 0;
  transition: opacity 0.3s ease, transform 0.3s ease;
  transform: translateX(10px);
}

.note-card:hover .note-actions {
  opacity: 1;
  transform: translateX(0);
}

.delete-btn {
  color: #f56c6c;
  transition: color 0.3s ease, transform 0.2s ease;
}

.delete-btn:hover {
  color: #f78989;
  transform: scale(1.1);
}

.note-content {
  color: #595959;
  line-height: 1.7;
  margin: 0 0 16px 0;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 15px;
}

.note-footer {
    position: absolute;
    bottom: 20px;
    left: 20px;
    right: 20px;
    text-align: right;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stock-tag {
    background-color: #ecf5ff;
    color: #409eff;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }

  .related-stock-info {
    margin-bottom: 16px;
  }

.update-time {
  font-size: 12px;
  color: #8c8c8c;
  transition: color 0.3s ease;
}

.note-card:hover .update-time {
  color: #409eff;
}

.empty-notes {
  grid-column: 1 / -1;
  text-align: center;
  padding: 100px 20px;
  color: #8c8c8c;
  background: linear-gradient(180deg, #ffffff 0%, #f5f7fa 100%);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 2px dashed #dcdfe6;
  transition: all 0.3s ease;
}

.empty-notes:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  border-color: #c0c4cc;
}

.notes-table-container {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 24px;
  border: 1px solid #f0f0f0;
  overflow: hidden;
}

.table-actions {
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: center;
  padding: 2px 0;
}

.notes-table-container .table-actions .el-button {
  padding: 4px 8px !important;
  font-size: 11px !important;
  border-radius: 4px !important;
  min-width: 50px;
  height: 26px !important;
  line-height: 14px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.2s ease;
}

.notes-table-container .table-actions .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.stock-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.note-title-text {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 16px;
  margin-bottom: 4px;
  display: block;
  transition: color 0.3s ease;
}

.note-title-text:hover {
  color: #409eff;
}

.note-content-text {
  color: #595959;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
  font-size: 14px;
}

.empty-notes i {
  font-size: 80px;
  margin-bottom: 24px;
  display: block;
  color: #d9d9d9;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.05);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0.8;
  }
}

.empty-notes p {
  font-size: 16px;
  margin: 0;
  color: #8c8c8c;
}

.note-detail {
  padding: 10px 0;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  color: #909399;
  font-size: 14px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.note-content-detail {
  color: #303133;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

.image-preview-container {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.image-preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
}

.image-preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  background-color: #fff;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-preview-item .el-button {
  position: absolute;
  top: 4px;
  right: 4px;
  background-color: rgba(0, 0, 0, 0.5);
}

.content-image {
  max-width: 100%;
  max-height: 400px; /* 增加最大高度 */
  margin: 16px auto; /* 居中显示 */
  display: block; /* 块级元素，确保换行 */
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
  cursor: pointer;
}

.content-image:hover {
  transform: scale(1.01);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.content-image:hover {
  transform: scale(1.01);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.image-placeholder {
  display: inline-block;
  padding: 8px 16px;
  background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
  border-radius: 6px;
  color: #8c8c8c;
  margin: 8px 0;
  font-size: 14px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.08);
}

.note-content-rendered {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.8;
  font-size: 16px;
  color: #595959;
}

/* 模态窗口样式优化 */
.el-dialog {
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15) !important;
  overflow: hidden;
  max-width: 900px; /* 设置最大宽度 */
  margin-top: 20px !important; /* 顶部边距，避免贴顶 */
}

/* 自定义大尺寸模态窗口 */
.el-dialog__wrapper {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
}

.el-dialog__header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 24px 32px !important;
  border-bottom: 1px solid #ebeef5;
}

.el-dialog__title {
  font-size: 22px !important;
  font-weight: 600 !important;
  color: #1a1a1a !important;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.el-dialog__body {
  padding: 32px !important;
}

.el-dialog__footer {
  padding: 20px 32px !important;
  border-top: 1px solid #ebeef5;
  background-color: #f8f9fa;
}

/* 表单样式优化 */
.el-input__wrapper {
  border-radius: 8px !important;
  transition: all 0.3s ease;
}

.el-input__wrapper:hover:not(.is-focus) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1) !important;
}

.el-textarea__inner {
  min-height: 320px !important; /* 增加文本框高度 */
  border-radius: 8px !important;
  font-size: 15px;
  line-height: 1.6;
  border: 2px solid #dcdfe6;
  transition: all 0.3s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* .rich-text-editor 样式已移至 MarkdownEditor 组件内部 */

/* 按钮样式优化 */
.el-button {
  border-radius: 8px !important;
  padding: 12px 24px !important;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.el-button--primary {
  background: linear-gradient(135deg, #409eff, #67c23a) !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.el-button--primary:hover {
  background: linear-gradient(135deg, #66b1ff, #85ce61) !important;
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4) !important;
  transform: translateY(-2px);
}

.el-button--default {
  background: linear-gradient(135deg, #f5f7fa 0%, #e6eaf0 100%) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.el-button--default:hover {
  background: linear-gradient(135deg, #ecf5ff 0%, #e6f4ff 100%) !important;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15) !important;
  transform: translateY(-1px);
}

/* 表格样式优化 */
.el-table {
  border-radius: 12px !important;
  overflow: hidden;
}

.el-table th {
  background: linear-gradient(135deg, #f5f7fa 0%, #e6eaf0 100%) !important;
  font-weight: 600 !important;
  color: #1a1a1a !important;
  border-bottom: 2px solid #ebeef5 !important;
}

.el-table td {
  border-bottom: 1px solid #f0f0f0 !important;
  transition: background-color 0.3s ease;
}

.el-table__row:hover > td {
  background-color: #f5f7fa !important;
}

/* 移除旧的图片预览样式，因为图片现在直接在文本中展示 */

/* 股票标签样式 */
.stock-tag {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, #67c23a 0%, #409eff 100%);
  color: white;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  margin-right: 8px;
  margin-bottom: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(103, 194, 58, 0.3);
}

.stock-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

/* 加载动画 */
.loading-container {
  text-align: center;
  padding: 60px 20px;
}

/* 股票搜索组件样式 */
.stock-search-container {
  width: 100%;
  position: relative;
}

.selected-stocks {
  margin-bottom: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.search-input-wrapper {
  position: relative;
  width: 100%;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  background-color: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  z-index: 1000;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.search-result-item {
  padding: 10px 15px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-result-item:hover {
  background-color: #f5f7fa;
}

.stock-code {
  font-weight: 600;
  color: #303133;
}

.stock-name {
  color: #606266;
}

.stock-industry {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notes-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .notes-grid {
    grid-template-columns: 1fr;
  }
  
  .el-dialog {
    margin: 20px !important;
    width: auto !important;
  }
  
  .el-dialog__header, .el-dialog__body, .el-dialog__footer {
    padding: 16px !important;
  }
}
</style>