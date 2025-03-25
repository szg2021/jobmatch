import { ref } from 'vue';

// 记录LogViewer组件实例的引用
let logViewerInstance: any = null;

// 注册LogViewer组件实例
export const registerLogViewer = (instance: any) => {
  logViewerInstance = instance;
};

// 日志方法
export const logger = {
  info: (message: string, details?: any) => {
    console.info('[INFO]', message, details);
    logViewerInstance?.info(message, details);
  },
  warning: (message: string, details?: any) => {
    console.warn('[WARNING]', message, details);
    logViewerInstance?.warning(message, details);
  },
  error: (message: string, details?: any) => {
    console.error('[ERROR]', message, details);
    logViewerInstance?.error(message, details);
  },
  success: (message: string, details?: any) => {
    console.log('[SUCCESS]', message, details);
    logViewerInstance?.success(message, details);
  },
  // 用于API请求错误处理的便捷方法
  apiError: (endpoint: string, error: any) => {
    const errorDetails = {
      endpoint,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    };
    
    console.error(`[API ERROR] ${endpoint}`, errorDetails);
    logViewerInstance?.error(`API错误: ${endpoint}`, errorDetails);
    
    return errorDetails;
  },
  // 记录API请求
  apiRequest: (method: string, endpoint: string, data?: any) => {
    console.log(`[API REQUEST] ${method} ${endpoint}`, data);
    logViewerInstance?.info(`API请求: ${method} ${endpoint}`, data);
  },
  // 记录API响应
  apiResponse: (endpoint: string, response: any) => {
    console.log(`[API RESPONSE] ${endpoint}`, response);
    logViewerInstance?.success(`API响应: ${endpoint}`, {
      status: response.status,
      data: response.data
    });
  }
};

// 导出默认的日志服务
export default logger; 