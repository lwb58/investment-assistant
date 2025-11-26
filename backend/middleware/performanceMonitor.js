/**
 * 性能监控中间件
 * 用于记录API请求的响应时间和处理性能
 */
function performanceMonitor(req, res, next) {
  // 记录请求开始时间
  const startTime = Date.now();
  const requestId = generateRequestId();
  
  // 记录请求信息
  console.log(`[${new Date().toISOString()}] [${requestId}] Request: ${req.method} ${req.url}`);
  
  // 保存原始的end方法
  const originalEnd = res.end;
  
  // 重写end方法以记录响应时间
  res.end = function(...args) {
    // 计算响应时间
    const responseTime = Date.now() - startTime;
    
    // 获取状态码
    const statusCode = res.statusCode;
    
    // 根据响应时间和状态码决定日志级别
    let logLevel = 'INFO';
    if (responseTime > 1000) {
      logLevel = 'WARN'; // 响应时间超过1秒警告
    }
    if (statusCode >= 500) {
      logLevel = 'ERROR'; // 服务器错误
    }
    
    // 记录响应信息
    console.log(`[${new Date().toISOString()}] [${requestId}] [${logLevel}] Response: ${statusCode} ${responseTime}ms - ${req.method} ${req.url}`);
    
    // 调用原始的end方法
    originalEnd.apply(res, args);
  };
  
  next();
}

/**
 * 生成唯一的请求ID
 * @returns {string} 请求ID
 */
function generateRequestId() {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export default performanceMonitor;