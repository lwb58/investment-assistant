// 统一的API服务层
// 所有数据获取方法都集中在这里

class ApiService {
  constructor() {
    // API基础URL
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
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API请求错误:', error);
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
    // 实际API调用
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request('GET', `/stocks${query}`);
  }

  /**
   * 添加新股票
   * @param {Object} stockData - 股票数据
   * @returns {Promise<Object>} 创建的股票
   */
  async addStock(stockData) {
    // 实际API调用
    return this.request('POST', `/stocks`, {
      body: JSON.stringify(stockData)
    });
  }

  /**
   * 更新股票信息
   * @param {string} stockCode - 股票代码
   * @param {Object} stockData - 更新的股票数据
   * @returns {Promise<Object>} 更新后的股票
   */
  async updateStock(stockCode, updateData) {
    // 实际API调用
    return this.request('PUT', `/stocks/${stockCode}`, {
      body: JSON.stringify(updateData)
    });
  }

  /**
   * 删除股票
   * @param {string} stockCode - 股票代码
   * @returns {Promise<Object>} 删除结果
   */
  async deleteStock(stockCode) {
    // 实际API调用
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
      // 使用同一个/stocks端点，通过search查询参数实现搜索功能
      const results = await this.request('GET', `/stocks?search=${encodeURIComponent(keyword)}`);
      // 转换为前端需要的格式
      return results.map(stock => ({
        code: stock.code,
        name: stock.name,
        industry: stock.industry
      }));
    } catch (error) {
      console.error('搜索股票失败:', error);
      // 返回空数组，避免界面崩溃
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
    // 实际API调用
    return this.request('GET', `/stocks/${stockCode}/detail`);
  }

  /**
   * 获取股票财务数据
   * @param {string} stockCode - 股票代码
   * @param {string} year - 年份
   * @returns {Promise<Object>} 财务数据
   */
  async getStockFinancial(stockCode, year) {
    // 实际API调用
    return this.request('GET', `/stocks/${stockCode}/financial/${year}`);
  }

  // =============== 复盘笔记相关API ===============

  /**
   * 获取复盘笔记列表
   * @param {string} search - 搜索关键词（可选）
   * @returns {Promise<Array>} 笔记列表
   */
  async getNotes(search = '') {
    // 实际API调用
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request('GET', `/notes${query}`);
  }

  /**
   * 获取笔记详情
   * @param {number} noteId - 笔记ID
   * @returns {Promise<Object>} 笔记详情
   */
  async getNoteById(noteId) {
    // 实际API调用
    return this.request('GET', `/notes/${noteId}`);
  }

  /**
   * 添加新笔记
   * @param {Object} noteData - 笔记数据
   * @returns {Promise<Object>} 创建的笔记
   */
  async addNote(noteData) {
    // 实际API调用
    return this.request('POST', `/notes`, {
      body: JSON.stringify(noteData)
    });
  }
  
  // 创建复盘笔记（兼容现有代码）
  async createReviewNote(noteData) {
    // 实际API调用
    return this.request('POST', `/notes`, {
      body: JSON.stringify(noteData)
    });
  }
  
  // 更新复盘笔记（兼容现有代码）
  async updateNote(noteId, noteData) {
    // 实际API调用
    return this.request('PUT', `/notes/${noteId}`, {
      body: JSON.stringify(noteData)
    });
  }
  
  // 获取复盘笔记列表（兼容现有代码）
  async getReviewNotes() {
    // 实际API调用
    return this.request('GET', `/notes`);
  }

  /**
   * 更新笔记
   * @param {number} noteId - 笔记ID
   * @param {Object} noteData - 更新的笔记数据
   * @returns {Promise<Object>} 更新后的笔记
   */
  async updateReviewNote(noteId, noteData) {
    // 实际API调用
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
    // 实际API调用
    return this.request('DELETE', `/notes/${noteId}`);
  }

  /**
   * 获取市场概况数据
   * @returns {Promise<Object>} 市场概况数据
   * 注意：后端目前没有实现这个接口，返回模拟数据以避免界面崩溃
   */
  async getMarketOverview() {
    // 由于后端没有实现市场概况接口，返回一个合理的模拟数据
    // 这样可以保证大盘页面正常显示，后续可以在后端实现该接口
    // 注意：当后端实现接口后，可以替换为实际API调用: return this.request('GET', `/market/overview`);
    return {
      "date": new Date().toISOString().split('T')[0],
      "shIndex": "3225.08",
      "shChange": 25.36,
      "shChangeRate": 0.79,
      "szIndex": "11065.88",
      "szChange": 89.25,
      "szChangeRate": 0.81,
      "cyIndex": "2256.77",
      "cyChange": 28.45,
      "cyChangeRate": 1.28,
      "totalVolume": "9682.45",
      "totalAmount": "12345.67",
      "upStocks": 2345,
      "downStocks": 1678,
      "flatStocks": 123,
      "marketHotspots": [
        { "industry": "半导体", "changeRate": 2.85 },
        { "industry": "新能源汽车", "changeRate": 1.98 },
        { "industry": "军工", "changeRate": 1.76 }
      ]
    };
  }
}

// 导出单例实例
const apiService = new ApiService();
export default apiService;