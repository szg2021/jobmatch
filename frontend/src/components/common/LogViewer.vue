<template>
  <div class="log-viewer" :class="{ 'log-viewer--expanded': isExpanded }">
    <!-- 控制按钮 -->
    <div class="log-viewer__toggle" @click="toggleExpand">
      <el-icon><DocumentCopy /></el-icon>
      <span v-if="unreadCount > 0" class="log-viewer__badge">{{ unreadCount }}</span>
    </div>
    
    <!-- 日志面板 -->
    <transition name="slide">
      <div v-if="isExpanded" class="log-viewer__panel">
        <div class="log-viewer__header">
          <div class="log-viewer__title">日志查看器</div>
          <div class="log-viewer__actions">
            <el-button @click="clearLogs" type="danger" size="small" plain>清除</el-button>
            <el-button @click="toggleExpand" type="primary" size="small" circle>
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>
        
        <div class="log-viewer__content" ref="logContent">
          <div v-if="logs.length === 0" class="log-viewer__empty">
            暂无日志信息
          </div>
          
          <div v-else class="log-viewer__logs">
            <div v-for="(log, index) in logs" :key="index" class="log-viewer__log-item">
              <div class="log-viewer__log-header">
                <span class="log-viewer__log-type" :class="`log-viewer__log-type--${log.type}`">
                  {{ log.type.toUpperCase() }}
                </span>
                <span class="log-viewer__log-time">{{ log.time }}</span>
              </div>
              <div class="log-viewer__log-message">{{ log.message }}</div>
              <div v-if="log.details" class="log-viewer__log-details">
                <pre>{{ typeof log.details === 'string' ? log.details : JSON.stringify(log.details, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, nextTick } from 'vue';
import { DocumentCopy, Close } from '@element-plus/icons-vue';
import { registerLogViewer } from '@/utils/logger';

export default defineComponent({
  name: 'LogViewer',
  components: {
    DocumentCopy,
    Close
  },
  setup() {
    const isExpanded = ref(false);
    const unreadCount = ref(0);
    const logContent = ref<HTMLElement | null>(null);
    
    // 日志项接口
    interface LogItem {
      type: 'info' | 'warning' | 'error' | 'success';
      message: string;
      details?: any;
      time: string;
    }
    
    const logs = ref<LogItem[]>([]);
    
    // 格式化当前时间
    const formatTime = (): string => {
      const now = new Date();
      return [
        now.getHours().toString().padStart(2, '0'),
        now.getMinutes().toString().padStart(2, '0'),
        now.getSeconds().toString().padStart(2, '0'),
        now.getMilliseconds().toString().padStart(3, '0')
      ].join(':');
    };
    
    // 添加日志
    const addLog = (type: 'info' | 'warning' | 'error' | 'success', message: string, details?: any) => {
      logs.value.push({
        type,
        message,
        details,
        time: formatTime()
      });
      
      // 如果日志面板没有展开，增加未读计数
      if (!isExpanded.value) {
        unreadCount.value++;
      }
      
      // 限制最多显示100条日志
      if (logs.value.length > 100) {
        logs.value.shift();
      }
      
      // 滚动到底部
      nextTick(() => {
        scrollToBottom();
      });
    };
    
    // 提供各种类型的日志方法
    const info = (message: string, details?: any) => addLog('info', message, details);
    const warning = (message: string, details?: any) => addLog('warning', message, details);
    const error = (message: string, details?: any) => addLog('error', message, details);
    const success = (message: string, details?: any) => addLog('success', message, details);
    
    // 清除所有日志
    const clearLogs = () => {
      logs.value = [];
      unreadCount.value = 0;
    };
    
    // 切换展开/折叠状态
    const toggleExpand = () => {
      isExpanded.value = !isExpanded.value;
      
      // 如果展开，清除未读计数
      if (isExpanded.value) {
        unreadCount.value = 0;
        nextTick(() => {
          scrollToBottom();
        });
      }
    };
    
    // 滚动到底部
    const scrollToBottom = () => {
      if (logContent.value) {
        logContent.value.scrollTop = logContent.value.scrollHeight;
      }
    };
    
    // 监听日志数组变化，自动滚动到底部
    watch(logs, () => {
      nextTick(() => {
        scrollToBottom();
      });
    });
    
    // 注册组件实例
    onMounted(() => {
      registerLogViewer({
        info,
        warning,
        error,
        success
      });
    });
    
    return {
      isExpanded,
      unreadCount,
      logs,
      logContent,
      toggleExpand,
      clearLogs
    };
  }
});
</script>

<style scoped>
.log-viewer {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.log-viewer__toggle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
  transition: all 0.3s;
}

.log-viewer__toggle:hover {
  transform: scale(1.1);
}

.log-viewer__badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #F56C6C;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 12px;
  min-width: 16px;
  text-align: center;
}

.log-viewer__panel {
  position: absolute;
  bottom: 60px;
  right: 0;
  width: 500px;
  max-height: 400px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.log-viewer__header {
  padding: 10px 15px;
  background-color: #f4f4f5;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-viewer__title {
  font-weight: bold;
  color: #606266;
}

.log-viewer__actions {
  display: flex;
  gap: 8px;
}

.log-viewer__content {
  flex: 1;
  overflow-y: auto;
  max-height: 345px;
  padding: 10px;
}

.log-viewer__empty {
  color: #909399;
  text-align: center;
  padding: 30px 0;
}

.log-viewer__logs {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.log-viewer__log-item {
  padding: 8px;
  border-radius: 4px;
  background-color: #f8f8f8;
  border-left: 4px solid #dcdfe6;
}

.log-viewer__log-item:hover {
  background-color: #f0f0f0;
}

.log-viewer__log-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.log-viewer__log-type {
  font-weight: 600;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 3px;
}

.log-viewer__log-type--info {
  background-color: #e6f1fc;
  color: #409EFF;
}

.log-viewer__log-type--warning {
  background-color: #fdf5e6;
  color: #E6A23C;
}

.log-viewer__log-type--error {
  background-color: #fef0f0;
  color: #F56C6C;
}

.log-viewer__log-type--success {
  background-color: #f0f9eb;
  color: #67C23A;
}

.log-viewer__log-time {
  font-size: 12px;
  color: #909399;
}

.log-viewer__log-message {
  margin-bottom: 5px;
  word-break: break-word;
}

.log-viewer__log-details {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 8px;
  overflow-x: auto;
  font-size: 12px;
}

.log-viewer__log-details pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  white-space: pre-wrap;
}

/* 动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease-out;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style> 