import { ElMessage, ElMessageBox } from 'element-plus';
import axios, { AxiosError } from 'axios';
import router from '@/router';
import type { MessageBoxData } from 'element-plus';

/**
 * 处理API请求错误
 * @param error - Axios错误对象
 * @param customMessage - 自定义错误消息
 * @returns 处理过的错误对象，可以在catch块中继续使用
 */
export function handleApiError(error: any, customMessage?: string): any {
  // 如果是取消的请求，不显示错误
  if (axios.isCancel(error)) {
    console.log('Request canceled:', error.message);
    return error;
  }
  
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    
    // 处理常见HTTP错误状态码
    if (status === 401) {
      // 未授权，清除登录信息并重定向到登录页
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // 如果不是在登录页，弹出提示并跳转
      if (router.currentRoute.value.name !== 'login') {
        ElMessage.error('登录已过期，请重新登录');
        router.push('/login');
      }
    } else if (status === 403) {
      ElMessage.error('没有权限执行此操作');
    } else if (status === 404) {
      ElMessage.error(customMessage || '请求的资源不存在');
    } else if (status === 422) {
      // 数据验证错误
      const validationErrors = error.response?.data?.detail || [];
      if (Array.isArray(validationErrors) && validationErrors.length > 0) {
        // 显示第一个验证错误
        ElMessage.error(validationErrors[0].msg);
      } else {
        ElMessage.error(customMessage || '提交的数据无效');
      }
    } else if (status === 429) {
      ElMessage.error('请求过于频繁，请稍后再试');
    } else if (status && status >= 500) {
      ElMessage.error(customMessage || '服务器错误，请稍后再试');
    } else {
      // 其他错误
      const errorMsg = error.response?.data?.detail || customMessage || '请求失败，请稍后再试';
      ElMessage.error(errorMsg);
    }
  } else {
    // 非HTTP错误（如网络问题）
    if (error.message === 'Network Error') {
      ElMessage.error('网络连接失败，请检查您的网络连接');
    } else {
      ElMessage.error(customMessage || '发生错误，请稍后再试');
    }
  }
  
  // 记录详细错误到控制台
  console.error('API Error:', error);
  
  // 返回错误对象以便进一步处理
  return error;
}

/**
 * 创建一个带有确认对话框的异步操作处理函数
 * @param action - 要执行的异步操作
 * @param confirmOptions - 确认对话框的选项
 * @returns Promise
 */
export async function confirmAction<T>(
  action: () => Promise<T>,
  {
    title = '确认操作',
    message = '确定要执行此操作吗？',
    confirmButtonText = '确定',
    cancelButtonText = '取消',
    type = 'warning'
  } = {}
): Promise<T | undefined> {
  try {
    await ElMessageBox.confirm(
      message, 
      title, 
      {
        confirmButtonText,
        cancelButtonText,
        type: type as 'warning' | 'info' | 'success' | 'error' | ''
      }
    );
    
    return await action();
  } catch (error) {
    // 用户取消操作，不需要处理
    if (error === 'cancel') {
      return undefined;
    }
    
    // 其他错误，调用错误处理
    return handleApiError(error);
  }
}

/**
 * 格式化API错误消息
 * @param error - 错误对象
 * @returns 格式化后的错误消息
 */
export function formatErrorMessage(error: any): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data;
    
    if (typeof data === 'string') {
      return data;
    }
    
    if (data?.detail) {
      if (typeof data.detail === 'string') {
        return data.detail;
      }
      
      if (Array.isArray(data.detail) && data.detail.length > 0) {
        return data.detail[0].msg || '请求数据无效';
      }
    }
    
    return `错误 (${error.response?.status || 'unknown'}): ${error.message}`;
  }
  
  return error?.message || '未知错误';
} 