class ApiService {
  constructor() {
    // API基础URL（配合Vite代理配置）
    this.baseURL = '/api';
  }

  // 通用请求方法
  async request(method, endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method,
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });

      if (!response.ok) {
        // 尝试解析错误响应内容
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`[${response.status}] ${errorData.detail || '请求失败'}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API请求错误 [${endpoint}]:`, error);
      throw error;
    }
  }

  // =============== 股票清单相关API ===============

  /**
   * 获取股票清单
   * @param {string} search - 搜索关键词（可选）
   * @returns {Promise<Array>} 股票列表
   */
  async getStocks(search = '') {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request('GET', `/stocks${query}`);
  }

  /**
   * 添加新股票
   * @param {Object} stockData - 股票数据
   * @returns {Promise<Object>} 创建的股票
   */
  async addStock(stockData) {
      const requestData = {
      stockCode: stockData.code,    // 前端code → 后端stockCode
      stockName: stockData.name,    // 前端name → 后端stockName
      isHold: stockData.holding,    // 前端holding → 后端isHold
      industry: stockData.industry, // 前端industry → 后端industry（新增字段）
      remark: stockData.remark || ''// 可选字段，空值兜底
    };
    return this.request('POST', `/stocks/add`, {
      body: JSON.stringify(requestData)
    });
  }

  /**
   * 更新股票信息
   * @param {string} stockCode - 股票代码
   * @param {Object} stockData - 更新的股票数据
   * @returns {Promise<Object>} 更新后的股票
   */
  async updateStock(stockCode, updateData) {
    // 字段映射：前端→后端（和addStock保持一致，避免字段名不匹配）
    const requestData = {
      // 保留需要更新的核心字段，过滤无效字段
      stockCode: updateData.code || stockCode, // 股票代码（兜底用传入的stockCode）
      stockName: updateData.name,             // 前端name → 后端stockName
      industry: updateData.industry,          // 前端industry → 后端industry
      isHold: updateData.holding,             // 前端holding → 后端isHold（关键映射）
      remark: updateData.remark || '',        // 可选字段，空值兜底
      // 移除前端特有的字段，避免后端校验报错
      holding: undefined,
      code: undefined
    };

    // 发送PUT请求，路径和后端保持一致（复数stocks）
    return this.request('PUT', `/stocks/${stockCode}`, {
      body: JSON.stringify(requestData)
    });
  }

  /**
   * 删除股票
   * @param {string} stockCode - 股票代码
   * @returns {Promise<Object>} 删除结果
   */
  async deleteStock(stockCode) {
    return this.request('DELETE', `/stocks/${stockCode}`);
  }
  
  /**
   * 搜索股票
   * @param {string} keyword - 搜索关键词（股票代码或名称）
   * @returns {Promise<Array>} 搜索结果列表
   */
  async searchStocks(keyword) {
    if (!keyword || keyword.trim().length < 1) {
      return [];
    }
    
    try {
      const results = await this.request('GET', `/stocks/search/${encodeURIComponent(keyword)}`);
      return results.map(stock => ({
        code: stock.code,
        name: stock.name,
        industry: stock.industry
      }));
    } catch (error) {
      console.error('搜索股票失败:', error);
      return [];
    }
  }

  // =============== 股票详情相关API ===============

  /**
   * 获取股票详细信息
   * @param {string} stockCode - 股票代码
   * @returns {Promise<Object>} 股票详细信息
   */
  async getStockDetail(stockCode) {
    return this.request('GET', `/stocks/${stockCode}/detail`);
  }

  /**
   * 获取股票财务数据
   * @param {string} stockCode - 股票代码
   * @param {string} year - 年份
   * @returns {Promise<Object>} 财务数据
   */
  async getStockFinancial(stockCode, year) {
    return this.request('GET', `/stocks/${stockCode}/financial/${year}`);
  }

  // =============== 复盘笔记相关API ===============

  /**
   * 获取复盘笔记列表
   * @param {string} search - 搜索关键词（可选）
   * @returns {Promise<Array>} 笔记列表
   */
  async getNotes(search = '') {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request('GET', `/notes${query}`);
  }

  /**
   * 获取笔记详情
   * @param {number} noteId - 笔记ID
   * @returns {Promise<Object>} 笔记详情
   */
  async getNoteById(noteId) {
    return this.request('GET', `/notes/${noteId}`);
  }

  /**
   * 添加新笔记
   * @param {Object} noteData - 笔记数据
   * @returns {Promise<Object>} 创建的笔记
   */
  async addNote(noteData) {
    return this.request('POST', `/notes`, {
      body: JSON.stringify(noteData)
    });
  }
  
  // 创建复盘笔记（兼容现有代码）
  async createReviewNote(noteData) {
    return this.request('POST', `/notes`, {
      body: JSON.stringify(noteData)
    });
  }
  
  // 更新复盘笔记（兼容现有代码）
  async updateNote(noteId, noteData) {
    return this.request('PUT', `/notes/${noteId}`, {
      body: JSON.stringify(noteData)
    });
  }
  
  // 获取复盘笔记列表（兼容现有代码）
  async getReviewNotes() {
    return this.request('GET', `/notes`);
  }

  /**
   * 更新笔记
   * @param {number} noteId - 笔记ID
   * @param {Object} noteData - 更新的笔记数据
   * @returns {Promise<Object>} 更新后的笔记
   */
  async updateReviewNote(noteId, noteData) {
    return this.request('PUT', `/notes/${noteId}`, {
      body: JSON.stringify(noteData)
    });
  }

  /**
   * 删除笔记
   * @param {number} noteId - 笔记ID
   * @returns {Promise<Object>} 删除结果
   */
  async deleteNote(noteId) {
    return this.request('DELETE', `/notes/${noteId}`);
  }

  /**
   * 获取市场概况数据
   * @returns {Promise<Object>} 市场概况数据
   */
  async getMarketOverview() {
    // 调用实际后端接口（已实现）
    return this.request('GET', `/market/overview`);
  }
}

// 导出单例实例
const apiService = new ApiService();
export default apiService;