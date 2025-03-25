/**
 * 全局加载状态管理工具
 * 提供加载状态的管理，包括超时处理、错误处理和日志记录
 */
import { reactive, readonly } from 'vue';
import { ElMessage } from 'element-plus';
import { logger } from './logger';

// 加载状态接口
interface LoadingStateInterface {
  [key: string]: boolean;
}

// 超时设置接口
interface TimeoutSettings {
  enabled: boolean;
  duration: number; // 超时时间（毫秒）
  callback?: () => void; // 超时回调函数
}

// 默认超时设置
const DEFAULT_TIMEOUT: TimeoutSettings = {
  enabled: true,
  duration: 10000, // 默认10秒超时
};

// 创建响应式加载状态对象
const state = reactive<LoadingStateInterface>({});

// 超时计时器映射
const timeoutTimers: Map<string, NodeJS.Timeout> = new Map();

/**
 * 设置加载状态
 * @param key 加载状态标识符
 * @param value 加载状态值
 * @param timeout 超时设置
 */
function setLoading(key: string, value: boolean, timeout: TimeoutSettings = DEFAULT_TIMEOUT): void {
  // 如果存在计时器，先清除
  if (timeoutTimers.has(key)) {
    clearTimeout(timeoutTimers.get(key)!);
    timeoutTimers.delete(key);
  }

  // 设置新的加载状态
  state[key] = value;
  
  // 记录日志
  logger.info(`加载状态变更: ${key} = ${value}`);

  // 如果开启加载且启用了超时，设置超时计时器
  if (value && timeout.enabled) {
    const timer = setTimeout(() => {
      state[key] = false;
      logger.warning(`加载状态超时: ${key} (${timeout.duration}ms)`);
      ElMessage.warning(`操作超时，请检查网络连接或重试`);
      if (timeout.callback) {
        timeout.callback();
      }
    }, timeout.duration);
    timeoutTimers.set(key, timer);
  }
}

/**
 * 获取加载状态
 * @param key 加载状态标识符
 * @returns 加载状态值
 */
function getLoading(key: string): boolean {
  return !!state[key];
}

/**
 * 使用加载状态包装异步函数
 * @param key 加载状态标识符
 * @param fn 要执行的异步函数
 * @param timeout 超时设置
 * @returns 包装后的异步函数结果
 */
async function withLoading<T>(
  key: string, 
  fn: () => Promise<T>, 
  timeout: TimeoutSettings = DEFAULT_TIMEOUT
): Promise<T> {
  try {
    setLoading(key, true, timeout);
    
    // 创建一个超时Promise
    const timeoutPromise = new Promise<never>((_, reject) => {
      if (timeout.enabled) {
        setTimeout(() => {
          reject(new Error(`操作超时：${timeout.duration}ms`));
        }, timeout.duration);
      }
    });
    
    // 使用Promise.race确保即使原始Promise挂起也会结束
    const result = await Promise.race([fn(), timeoutPromise]);
    return result;
  } catch (error) {
    logger.error(`加载过程出错: ${key}`, error);
    throw error;
  } finally {
    setLoading(key, false);
  }
}

/**
 * 使用加载状态运行异步函数，但忽略错误
 * @param key 加载状态标识符
 * @param fn 要执行的异步函数
 * @param fallback 发生错误时的返回值
 * @param timeout 超时设置
 * @returns 异步函数结果或fallback值
 */
async function withLoadingSafe<T>(
  key: string, 
  fn: () => Promise<T>, 
  fallback: T, 
  timeout: TimeoutSettings = DEFAULT_TIMEOUT
): Promise<T> {
  try {
    return await withLoading(key, fn, timeout);
  } catch (error) {
    logger.warning(`安全加载出错但已恢复: ${key}`, error);
    return fallback;
  }
}

/**
 * 清除所有加载状态
 */
function clearAllLoadingStates(): void {
  // 清除所有计时器
  timeoutTimers.forEach(timer => clearTimeout(timer));
  timeoutTimers.clear();
  
  // 重置所有加载状态
  Object.keys(state).forEach(key => {
    state[key] = false;
  });
  
  logger.info('已清除所有加载状态');
}

export default {
  state: readonly(state),
  setLoading,
  getLoading,
  withLoading,
  withLoadingSafe,
  clearAllLoadingStates
}; 