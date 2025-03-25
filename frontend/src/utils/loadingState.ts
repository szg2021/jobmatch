import { ref, computed } from 'vue';
import logger from './logger';

/**
 * 创建一个加载状态管理器
 * @param initialState 初始加载状态
 * @returns 加载状态管理对象
 */
export function useLoading(initialState = false) {
  const isLoading = ref(initialState);
  
  // 已进行的加载操作次数
  const loadingCount = ref(0);
  
  // 存储超时计时器
  const timeoutIds = ref<number[]>([]);
  
  // 是否有任何加载操作正在进行
  const hasActiveLoading = computed(() => loadingCount.value > 0);
  
  /**
   * 开始加载
   */
  const startLoading = () => {
    loadingCount.value++;
    isLoading.value = true;
    logger.info('开始加载操作', { loadingCount: loadingCount.value });
  };
  
  /**
   * 结束加载
   */
  const endLoading = () => {
    if (loadingCount.value > 0) {
      loadingCount.value--;
    }
    
    if (loadingCount.value === 0) {
      isLoading.value = false;
      logger.info('所有加载操作已完成');
    } else {
      logger.info('结束一项加载操作', { remainingCount: loadingCount.value });
    }
  };
  
  /**
   * 执行带加载状态的异步操作
   * @param asyncOperation 异步操作函数
   * @param timeoutMs 超时时间（毫秒），默认为30000毫秒（30秒）
   * @returns 异步操作的结果
   */
  const withLoading = async <T>(
    asyncOperation: () => Promise<T>, 
    timeoutMs: number = 30000
  ): Promise<T> => {
    startLoading();
    
    // 创建一个Promise，在超时后会自动解析
    const timeoutPromise = new Promise<void>((resolve) => {
      const timeoutId = window.setTimeout(() => {
        logger.warning(`加载操作超时（${timeoutMs}ms），强制结束加载状态`);
        endLoading();
        resolve();
      }, timeoutMs);
      
      timeoutIds.value.push(timeoutId);
    });
    
    try {
      // 使用Promise.race，确保无论异步操作是否完成，都会在超时后结束加载状态
      const result = await Promise.race([
        // 原始异步操作
        asyncOperation().catch(error => {
          logger.error('异步操作失败', error);
          throw error;
        }),
        
        // 超时后返回的Promise (不会直接返回，只是确保超时后会结束加载状态)
        timeoutPromise.then(() => {
          throw new Error(`操作超时（${timeoutMs}ms）`);
        })
      ]) as T;
      
      return result;
    } catch (error) {
      logger.error('withLoading操作发生错误', error);
      throw error;
    } finally {
      // 清除所有此操作的超时计时器
      endLoading();
    }
  };
  
  /**
   * 重置加载状态
   */
  const resetLoading = () => {
    // 清除所有超时计时器
    timeoutIds.value.forEach(id => clearTimeout(id));
    timeoutIds.value = [];
    
    if (loadingCount.value > 0) {
      logger.warning(`强制重置加载状态，清除了${loadingCount.value}个未完成的加载操作`);
    }
    
    loadingCount.value = 0;
    isLoading.value = false;
  };
  
  // 向window暴露紧急重置方法，以便在控制台调试时使用
  if (typeof window !== 'undefined') {
    // @ts-ignore
    window.__resetLoading = resetLoading;
  }
  
  return {
    isLoading,
    loadingCount,
    hasActiveLoading,
    startLoading,
    endLoading,
    withLoading,
    resetLoading
  };
} 