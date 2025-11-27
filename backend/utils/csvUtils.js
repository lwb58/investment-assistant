/**
 * CSV工具模块
 * 提供CSV文件生成和导出功能
 */

/**
 * 将数据对象数组转换为CSV字符串
 * @param {Array} data - 数据对象数组
 * @param {Array} headers - 可选的自定义表头映射
 * @returns {string} CSV格式的字符串
 */
function exportToCSV(data, headers = null) {
  if (!data || data.length === 0) {
    return '';
  }
  
  // 使用数据中的第一个对象来确定列头，除非提供了自定义表头
  const columns = headers || Object.keys(data[0]);
  
  // 创建CSV头部行
  let csvContent = '\ufeff'; // UTF-8 BOM，确保Excel正确识别中文
  
  // 添加表头
  csvContent += columns.join(',') + '\n';
  
  // 添加数据行
  for (const row of data) {
    const rowValues = [];
    
    for (const column of columns) {
      let value = row[column];
      
      // 处理特殊情况
      if (value === null || value === undefined) {
        value = '';
      } else if (typeof value === 'string') {
        // 如果字符串包含逗号、引号或换行符，需要用引号包围并转义内部引号
        if (value.includes(',') || value.includes('"') || value.includes('\n')) {
          value = '"' + value.replace(/"/g, '""') + '"';
        }
      } else if (value instanceof Date) {
        // 格式化日期
        value = value.toISOString().split('T')[0];
      } else if (typeof value === 'number') {
        // 确保数字格式正确
        value = value.toString();
      }
      
      rowValues.push(value);
    }
    
    csvContent += rowValues.join(',') + '\n';
  }
  
  return csvContent;
}

/**
 * 将CSV字符串转换为数据对象数组
 * @param {string} csvString - CSV格式的字符串
 * @returns {Array} 数据对象数组
 */
function parseCSV(csvString) {
  const lines = csvString.split('\n');
  const result = [];
  
  if (lines.length < 2) {
    return result;
  }
  
  // 解析表头
  const headers = lines[0].split(',').map(header => header.trim());
  
  // 解析数据行
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    
    // 处理包含逗号和引号的复杂CSV行
    const values = parseCSVLine(line);
    
    if (values.length > 0) {
      const row = {};
      headers.forEach((header, index) => {
        if (index < values.length) {
          row[header] = values[index];
        }
      });
      result.push(row);
    }
  }
  
  return result;
}

/**
 * 解析单行CSV数据，处理引号和逗号
 * @param {string} line - CSV行
 * @returns {Array} 解析后的值数组
 */
function parseCSVLine(line) {
  const values = [];
  let currentValue = '';
  let inQuotes = false;
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    
    if (char === '"') {
      if (inQuotes && i < line.length - 1 && line[i + 1] === '"') {
        // 处理双引号转义
        currentValue += '"';
        i++; // 跳过下一个引号
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      // 遇到逗号且不在引号内，保存当前值
      values.push(currentValue.trim());
      currentValue = '';
    } else {
      currentValue += char;
    }
  }
  
  // 添加最后一个值
  values.push(currentValue.trim());
  
  return values;
}

export {
  exportToCSV,
  parseCSV
};