import axios, { AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';
import router from '../router';
import { ElMessage } from 'element-plus';
import { handleApiError } from './errorHandler';

// 声明环境变量类型
declare global {
  interface ImportMeta {
    env: Record<string, string>;
  }
}

// 扩展AxiosRequestConfig接口
interface CustomRequestConfig extends AxiosRequestConfig {
  allowDuplicate?: boolean;
  requestKey?: string;
}

// 扩展InternalAxiosRequestConfig接口
interface CustomInternalRequestConfig extends InternalAxiosRequestConfig {
  allowDuplicate?: boolean;
  requestKey?: string;
}

// 创建一个自定义的Axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_APP_API_BASE_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 创建一个请求取消标记的映射表
const pendingRequests = new Map();

// 生成请求的唯一键
const generateRequestKey = (config: CustomInternalRequestConfig) => {
  const { url, method, params, data } = config;
  return [url, method, JSON.stringify(params), JSON.stringify(data)].join('&');
};

// 请求拦截器
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const customConfig = config as CustomInternalRequestConfig;
    
    // 从本地存储获取token
    const token = localStorage.getItem('token');
    
    // 如果token存在，则添加到请求头中
    if (token) {
      customConfig.headers.Authorization = `Bearer ${token}`;
    }
    
    // 检查是否有相同的请求正在进行中
    const requestKey = generateRequestKey(customConfig);
    
    // 如果已存在相同请求且不允许重复，则取消前一个请求
    if (pendingRequests.has(requestKey) && !customConfig.allowDuplicate) {
      const controller = pendingRequests.get(requestKey);
      controller.abort();
      pendingRequests.delete(requestKey);
    }
    
    // 为当前请求创建AbortController
    const controller = new AbortController();
    customConfig.signal = controller.signal;
    pendingRequests.set(requestKey, controller);
    
    // 添加请求完成后的清理函数
    customConfig.requestKey = requestKey;
    
    return customConfig;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 请求成功完成，从pendingRequests中移除
    const customConfig = response.config as CustomInternalRequestConfig;
    const requestKey = customConfig.requestKey;
    if (requestKey) {
      pendingRequests.delete(requestKey);
    }
    
    return response;
  },
  (error) => {
    // 请求失败，同样需要从pendingRequests中移除
    if (error.config) {
      const customConfig = error.config as CustomInternalRequestConfig;
      if (customConfig.requestKey) {
        pendingRequests.delete(customConfig.requestKey);
      }
    }
    
    // 使用我们的错误处理系统
    return Promise.reject(error);
  }
);

// 扩展API对象，添加带错误处理的方法
const apiWithErrorHandling = {
  async get(url: string, config: CustomRequestConfig = {}) {
    try {
      return await api.get(url, config);
    } catch (error) {
      handleApiError(error);
      throw error;
    }
  },
  
  async post(url: string, data: any = {}, config: CustomRequestConfig = {}) {
    try {
      return await api.post(url, data, config);
    } catch (error) {
      handleApiError(error);
      throw error;
    }
  },
  
  async put(url: string, data: any = {}, config: CustomRequestConfig = {}) {
    try {
      return await api.put(url, data, config);
    } catch (error) {
      handleApiError(error);
      throw error;
    }
  },
  
  async delete(url: string, config: CustomRequestConfig = {}) {
    try {
      return await api.delete(url, config);
    } catch (error) {
      handleApiError(error);
      throw error;
    }
  },
  
  // 原始API实例，用于特殊情况下手动处理错误
  axios: api
};

export default apiWithErrorHandling; 