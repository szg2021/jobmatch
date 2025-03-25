<script setup lang="ts">
import { ref, watch } from 'vue';
import { ElButton, ElCard, ElTag } from 'element-plus';

// 日志项的接口
interface LogItem {
  id: number;
  time: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  details?: any;
}

// 创建一个全局存储，记录应用程序的日志
const logs = ref<LogItem[]>([]);
const isVisible = ref(false);
let nextId = 1;

// 全局日志方法，可以在任何地方调用
const addLog = (type: 'info' | 'warning' | 'error' | 'success', message: string, details?: any) => {
  const now = new Date();
  const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}.${now.getMilliseconds().toString().padStart(3, '0')}`;
  
  logs.value.unshift({
    id: nextId++,
    time: timeStr,
    type,
    message,
    details
  });

  // 限制日志数量，防止内存溢出
  if (logs.value.length > 100) {
    logs.value = logs.value.slice(0, 100);
  }
};

// 向外部暴露日志方法
defineExpose({
  info: (message: string, details?: any) => addLog('info', message, details),
  warning: (message: string, details?: any) => addLog('warning', message, details),
  error: (message: string, details?: any) => addLog('error', message, details),
  success: (message: string, details?: any) => addLog('success', message, details),
  clear: () => {
    logs.value = [];
    nextId = 1;
  }
});

// 切换日志面板的可见性
const toggleVisibility = () => {
  isVisible.value = !isVisible.value;
};

// 清除所有日志
const clearLogs = () => {
  logs.value = [];
  nextId = 1;
};

// 日志类型对应的标签类型
const tagType = {
  info: 'info',
  warning: 'warning',
  error: 'danger',
  success: 'success'
};
</script>

<template>
  <div class="log-viewer-container">
    <!-- 日志查看器按钮，始终显示在页面右下角 -->
    <el-button
      class="log-toggle-button"
      :type="isVisible ? 'danger' : 'primary'"
      size="small"
      circle
      @click="toggleVisibility"
    >
      <el-icon>
        <span v-if="isVisible">&#x2715;</span>
        <span v-else>&#x1F4DD;</span>
      </el-icon>
    </el-button>

    <!-- 日志面板，根据isVisible控制显示/隐藏 -->
    <transition name="slide-up">
      <div v-if="isVisible" class="log-panel">
        <el-card>
          <template #header>
            <div class="log-header">
              <h3>应用日志</h3>
              <div>
                <el-button type="danger" size="small" @click="clearLogs">清空日志</el-button>
                <el-button type="primary" size="small" @click="toggleVisibility">关闭</el-button>
              </div>
            </div>
          </template>

          <div class="log-content">
            <template v-if="logs.length > 0">
              <div v-for="log in logs" :key="log.id" class="log-item">
                <div class="log-item-header">
                  <el-tag :type="tagType[log.type]" size="small">{{ log.type.toUpperCase() }}</el-tag>
                  <span class="log-time">{{ log.time }}</span>
                </div>
                <div class="log-message">{{ log.message }}</div>
                <pre v-if="log.details" class="log-details">{{ typeof log.details === 'object' ? JSON.stringify(log.details, null, 2) : log.details }}</pre>
              </div>
            </template>
            <div v-else class="no-logs">
              暂无日志记录
            </div>
          </div>
        </el-card>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.log-viewer-container {
  position: fixed;
  bottom: 80px;
  right: 20px;
  z-index: 9999;
}

.log-toggle-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 10000;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.log-panel {
  position: fixed;
  bottom: 70px;
  right: 20px;
  width: 80vw;
  max-width: 500px;
  max-height: 70vh;
  z-index: 9999;
  border-radius: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-header h3 {
  margin: 0;
  font-size: 16px;
}

.log-content {
  height: 50vh;
  max-height: 500px;
  overflow-y: auto;
  padding: 0;
}

.log-item {
  border-bottom: 1px solid #eee;
  padding: 10px 0;
}

.log-item:last-child {
  border-bottom: none;
}

.log-item-header {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.log-time {
  margin-left: 8px;
  font-size: 12px;
  color: #999;
}

.log-message {
  font-size: 14px;
  word-break: break-word;
  line-height: 1.5;
}

.log-details {
  margin-top: 8px;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
}

.no-logs {
  text-align: center;
  padding: 20px;
  color: #999;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s, opacity 0.3s;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style> 