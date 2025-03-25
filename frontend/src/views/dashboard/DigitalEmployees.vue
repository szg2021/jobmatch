<template>
  <PageContentWrapper>
    <div class="page-header">
      <div class="page-title">AI数字员工市场</div>
      <div class="header-controls">
        <el-icon><More /></el-icon>
        <el-icon class="circle-icon"><CirclePlus /></el-icon>
      </div>
    </div>

    <div class="subtitle">AI数字员工市场</div>

    <!-- 顶部标签导航 -->
    <div class="tabs-container">
      <div class="tab active">智能Agent</div>
      <div class="tab">行政人事</div>
      <div class="tab">财务管理</div>
      <div class="tab">招投标</div>
      <div class="tab">其他</div>
    </div>

    <!-- AI员工列表 -->
    <div class="employee-list">
      <!-- 智能助手 -->
      <div class="employee-card">
        <div class="employee-header">
          <el-radio v-model="selectedEmployee" label="assistant" class="radio-select">智能助手</el-radio>
        </div>
        <div class="employee-content">
          <div class="employee-description">
            全能型问答助手，处理各种自然语言任务和知识问答
          </div>
          <div class="employee-stats">
            <div class="stat-item">
              <el-icon><View /></el-icon>
              <span>12875</span>
            </div>
            <div class="stat-item">
              <el-icon><Star /></el-icon>
              <span>9834</span>
            </div>
          </div>
        </div>
        <div class="employee-footer">
          <div class="employee-icon">
            <el-icon><School /></el-icon>
          </div>
          <el-button 
            type="danger" 
            round 
            class="try-button"
            @click="handleUseEmployee('assistant')"
          >
            立即使用
          </el-button>
        </div>
      </div>

      <!-- 代码助手 -->
      <div class="employee-card">
        <div class="employee-header">
          <el-radio v-model="selectedEmployee" label="coder" class="radio-select">代码助手</el-radio>
        </div>
        <div class="employee-content">
          <div class="employee-description">
            专业代码生成与优化，支持多种编程语言和框架
          </div>
          <div class="employee-stats">
            <div class="stat-item">
              <el-icon><View /></el-icon>
              <span>8645</span>
            </div>
            <div class="stat-item">
              <el-icon><Star /></el-icon>
              <span>7321</span>
            </div>
          </div>
        </div>
        <div class="employee-footer">
          <div class="employee-icon ai-icon">
            <span>AI</span>
          </div>
          <el-button 
            type="danger" 
            round 
            class="try-button"
            @click="handleUseEmployee('coder')"
          >
            立即使用
          </el-button>
        </div>
      </div>

      <!-- 文档分析师 -->
      <div class="employee-card">
        <div class="employee-header">
          <el-radio v-model="selectedEmployee" label="document-analyst" class="radio-select">文档分析师</el-radio>
        </div>
        <div class="employee-content">
          <div class="employee-description">
            智能分析文档内容，提取关键信息并生成摘要
          </div>
          <div class="employee-stats">
            <div class="stat-item">
              <el-icon><View /></el-icon>
              <span>7432</span>
            </div>
            <div class="stat-item">
              <el-icon><Star /></el-icon>
              <span>6154</span>
            </div>
          </div>
        </div>
        <div class="employee-footer">
          <div class="employee-icon doc-icon">
            <el-icon><Document /></el-icon>
          </div>
          <el-button 
            type="danger" 
            round 
            class="try-button"
            @click="handleUseEmployee('document-analyst')"
          >
            立即使用
          </el-button>
        </div>
      </div>

      <!-- 智能翻译官 -->
      <div class="employee-card">
        <div class="employee-header">
          <el-radio v-model="selectedEmployee" label="translator" class="radio-select">智能翻译官</el-radio>
        </div>
        <div class="employee-content">
          <div class="employee-description">
            高质量多语言翻译，保留原文语义与风格
          </div>
          <div class="employee-stats">
            <div class="stat-item">
              <el-icon><View /></el-icon>
              <span>6543</span>
            </div>
            <div class="stat-item">
              <el-icon><Star /></el-icon>
              <span>5421</span>
            </div>
          </div>
        </div>
        <div class="employee-footer">
          <div class="employee-icon translator-icon">
            <el-icon><User /></el-icon>
          </div>
          <el-button 
            type="danger" 
            round 
            class="try-button"
            @click="handleUseEmployee('translator')"
          >
            立即使用
          </el-button>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <BottomNavigation active-item="digital-employees" />
    
    <!-- 日志查看器 -->
    <LogViewer ref="logViewerRef" />
  </PageContentWrapper>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { 
  More, 
  CirclePlus, 
  View,
  Star,
  School,
  Document,
  User
} from '@element-plus/icons-vue';
import { useLoading } from '@/utils/loadingState';
import { useUserStore } from '@/store/user';
import BottomNavigation from '@/components/layout/BottomNavigation.vue';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
import LogViewer from '@/components/debug/LogViewer.vue';
import logger from '@/utils/logger';

const router = useRouter();
const loadingState = useLoading();
const userStore = useUserStore();
const selectedEmployee = ref('');
const logViewerRef = ref(null);

// 处理使用数字员工
const handleUseEmployee = (employeeType: string) => {
  logger.info(`尝试使用数字员工: ${employeeType}`);
  
  if (!userStore.isLoggedIn) {
    logger.warning('用户未登录，重定向到登录页面');
    ElMessage.warning('请先登录后使用数字员工');
    router.push({
      path: '/login',
      query: { redirect: router.currentRoute.value.fullPath }
    });
    return;
  }
  
  // 这里添加使用数字员工的逻辑
  logger.success(`开始使用数字员工: ${employeeType}`);
  ElMessage.success(`开始使用数字员工: ${employeeType}`);
  
  // 根据不同类型的数字员工执行不同的操作
  switch (employeeType) {
    case 'assistant':
      // 使用智能助手
      logger.info('启动智能助手服务');
      break;
    case 'coder':
      // 使用代码助手
      logger.info('启动代码助手服务');
      break;
    case 'document-analyst':
      // 使用文档分析师
      logger.info('启动文档分析服务');
      break;
    case 'translator':
      // 使用智能翻译官
      logger.info('启动翻译服务');
      break;
    default:
      logger.warning(`未知的数字员工类型: ${employeeType}`);
      break;
  }
};

// 初始化页面
onMounted(() => {
  logger.info('DigitalEmployees页面加载中...');
  
  // 不使用loading状态，直接加载静态数据
  logger.info('加载数字员工数据');
  
  // 模拟短暂的加载过程
  setTimeout(() => {
    logger.success('数字员工数据加载完成');
  }, 300);
  
  // 注册日志组件实例
  if (logViewerRef.value) {
    import('@/utils/logger').then(({ registerLogViewer }) => {
      registerLogViewer(logViewerRef.value);
      logger.info('日志组件已注册');
    });
  }
});
</script>

<style scoped>
.digital-employees-container {
  padding: 16px;
  padding-bottom: 70px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 10px;
  position: relative;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.header-controls {
  position: absolute;
  right: 0;
  display: flex;
  align-items: center;
}

.circle-icon {
  margin-left: 12px;
}

.subtitle {
  font-size: 18px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 16px;
}

.tabs-container {
  display: flex;
  overflow-x: auto;
  white-space: nowrap;
  margin-bottom: 16px;
  padding-bottom: 8px;
  scrollbar-width: none; /* Firefox */
}

.tabs-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Edge */
}

.tab {
  display: inline-block;
  padding: 8px 16px;
  margin-right: 10px;
  font-size: 14px;
  color: #606266;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.tab.active {
  background-color: #6b68ff;
  color: white;
}

.employee-list {
  margin-bottom: 16px;
}

.employee-card {
  background-color: #fff;
  border-radius: 8px;
  margin-bottom: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.employee-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.employee-header {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.radio-select {
  font-size: 16px;
  font-weight: bold;
}

.employee-content {
  padding: 12px 16px;
}

.employee-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
  line-height: 1.5;
}

.employee-stats {
  display: flex;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  margin-right: 20px;
  color: #909399;
}

.stat-item .el-icon {
  margin-right: 4px;
}

.employee-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
}

.employee-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #409eff;
}

.ai-icon {
  background-color: #e6f7ff;
  color: #1890ff;
  font-weight: bold;
  font-size: 16px;
}

.doc-icon {
  background-color: #f6ffed;
  color: #52c41a;
}

.translator-icon {
  background-color: #fff2e8;
  color: #fa541c;
}

.try-button {
  font-size: 14px;
  padding: 6px 20px;
}
</style> 