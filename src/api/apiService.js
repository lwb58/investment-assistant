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
    if (!search) {
      return this.request('GET', `/stocks`);
    }
    return this.request('GET', `/stocks/search/${encodeURIComponent(search)}`);
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
async updateStock(stockId, updateData) {  // 参数名从stockCode改为stockId
  // 只构建包含实际提供字段的请求数据，避免传递undefined值
  const requestData = {};
  
  // 只添加有值的字段
  if (updateData.code !== undefined) requestData.stockCode = updateData.code;
  if (updateData.stockCode !== undefined) requestData.stockCode = updateData.stockCode;
  if (updateData.name !== undefined) requestData.stockName = updateData.name;
  if (updateData.industry !== undefined) requestData.industry = updateData.industry;
  if (updateData.isHold !== undefined) requestData.isHold = updateData.isHold;
  if (updateData.remark !== undefined) requestData.remark = updateData.remark;

  // 路径参数从stockCode改为stockId，匹配后端的{stock_id}
  return this.request('PUT', `/stocks/${stockId}`, {
    body: JSON.stringify(requestData)
  });
}

  /**
   * 删除股票
   * @param {string} stockId - 股票ID
   * @returns {Promise<Object>} 删除结果
   */
  async deleteStock(stockId) {
    return this.request('DELETE', `/stocks/${stockId}`);
  }
  

  
  /**
   * 获取股票实时行情
   * @param {string} stockCode - 股票代码
   * @returns {Promise<Object>} 股票行情数据
   */
  async getStockQuotes(stockCode) {
    return this.request('GET', `/stocks/${stockCode}/quotes`);
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



  // =============== 复盘笔记相关API ===============



  /**
   * 根据股票代码获取相关笔记
   * @param {string} stockCode - 股票代码
   * @returns {Promise<Array>} 笔记列表
   */
  async getNotesByStockCode(stockCode) {
    return this.request('GET', `/notes/stock/${stockCode}`);
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
    // 获取所有类型的笔记，包括估值逻辑笔记
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
   * 获取所有标签
   * @param {string} userId - 用户ID（可选）
   * @returns {Promise<Array>} 标签列表
   */
  async getTags(userId = null) {
    let url = `/tags`;
    if (userId) {
      url += `?user_id=${userId}`;
    }
    return this.request('GET', url);
  }

  /**
   * 创建新标签
   * @param {string} tagName - 标签名称
   * @param {string} userId - 用户ID（可选）
   * @returns {Promise<Object>} 创建的标签
   */
  async createTag(tagName, userId = null) {
    const body = { name: tagName };
    if (userId) {
      body.userId = userId;
    }
    return this.request('POST', `/tags`, {
      body: JSON.stringify(body)
    });
  }

  /**
   * 上传图片
   * @param {File} file - 图片文件
   * @returns {Promise<Object>} 上传结果
   */
  async uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      // 对于文件上传，需要使用不同的请求头处理
      const response = await fetch(`${this.baseURL}/notes/upload/image`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`[${response.status}] ${errorData.detail || '图片上传失败'}`);
      }

      return await response.json();
    } catch (error) {
      console.error('图片上传错误:', error);
      throw error;
    }
  }

  /**
   * 获取股票杜邦分析数据
   * @param {string} stockId - 股票ID
   * @returns {Promise<Object>} 杜邦分析数据
   */
  async getStockDupontAnalysis(stockId) {
    return this.request('GET', `/stocks/dubang/${stockId}`);
  }

  /**
   * 保存利好利空分析
   * @param {Object} data - 利好利空数据
   * @param {number} existingNoteId - 已有的利好利空笔记ID（可选）
   * @returns {Promise<Object>} 保存结果
   */
  async saveProsConsSummary(data, existingNoteId = null) {
    try {
      const prosConsData = {
        title: `[利好利空] ${data.stockCode}`,
        content: JSON.stringify({
          prosPoints: data.prosPoints,
          consPoints: data.consPoints
        }),
        stockCode: data.stockCode,
        stockName: '',
        type: 'pros_cons',  // 指定笔记类型为利好利空分析
        source: '估值逻辑'  // 添加来源字段，标识该笔记来自估值逻辑
      };
      
      // 如果提供了现有笔记ID，则直接更新
      if (existingNoteId) {
        return this.request('PUT', `/notes/${existingNoteId}`, {
          body: JSON.stringify(prosConsData)
        });
      } else {
        // 查找是否已有利好利空笔记（仅在没有提供ID时才需要查找）
        const stockNotes = await this.getNotesByStockCode(data.stockCode);
        const existingProsConsNote = stockNotes.find(note => 
          note.title.startsWith('[利好利空]')
        );
        
        if (existingProsConsNote) {
          return this.request('PUT', `/notes/${existingProsConsNote.id}`, {
            body: JSON.stringify(prosConsData)
          });
        } else {
          return this.request('POST', `/notes`, {
            body: JSON.stringify(prosConsData)
          });
        }
      }
    } catch (error) {
      console.error('保存利好利空数据失败:', error);
      throw error;
    }
  }
  

}

// 导出单例实例
const apiService = new ApiService();
export default apiService;