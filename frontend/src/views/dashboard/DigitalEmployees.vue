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

    <!-- 添加AI搜索框 -->
    <div class="search-section">
      <AIChatSearchBox
        @search="handleAISearch"
        @chat-update="updateChatHistory"
        placeholder="请描述您需要的数字员工类型或功能..."
        buttonText="搜索智能体"
        context="我是您的AI助手，可以帮您找到适合的数字员工。请描述您的业务需求、场景或希望解决的问题。"
        :searchExamples="[
          '我需要一个能解析简历的助手',
          '有没有可以帮忙匹配职位的智能体？',
          '我想要一个能生成面试问题的工具',
          '寻找能做背景调查的数字员工'
        ]"
      />
    </div>

    <!-- 顶部标签导航 -->
    <div class="tabs-container">
      <div class="tab active">智能Agent</div>
      <div class="tab">行政人事</div>
      <div class="tab">财务管理</div>
      <div class="tab">招投标</div>
      <div class="tab">其他</div>
    </div>

    <!-- AI员工列表 -->
    <div class="employees-container" v-loading="isLoading">
      <!-- 遍历智能体列表 -->
      <div v-for="agent in agents" :key="agent.id" class="employee-card">
        <div class="employee-icon">
          <el-icon size="36"><component :is="agent.icon" /></el-icon>
        </div>
        <div class="employee-info">
          <div class="employee-header">
            <h3 class="employee-name">{{ agent.name }}</h3>
            <el-tag v-if="agent.isPopular" size="small" type="danger">热门</el-tag>
          </div>
          <p class="employee-category">{{ agent.category }}</p>
          <p class="employee-desc">{{ agent.description }}</p>
          <div class="employee-footer">
            <div class="employee-stats">
              <span class="usage-count">
                <el-icon><user /></el-icon>
                {{ agent.usageCount }}人使用
              </span>
              <span class="rating">
                <el-rate
                  v-model="agent.rating"
                  disabled
                  text-color="#ff9900"
                  score-template="{value}"
                  :show-score="true"
                ></el-rate>
              </span>
            </div>
            <div class="employee-actions">
              <el-button @click="likeAgent(agent.id)" type="text" size="small">
                <el-icon><ThumbUp /></el-icon>
              </el-button>
              <el-button @click="handleUseEmployee(agent.name)" type="primary" size="small" plain>使用</el-button>
            </div>
          </div>
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
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { 
  More, 
  CirclePlus, 
  View,
  Star,
  School,
  Document,
  User,
  ThumbUp
} from '@element-plus/icons-vue';
import loadingState from '@/utils/loadingState';
import { useUserStore } from '@/store/user';
import BottomNavigation from '@/components/layout/BottomNavigation.vue';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
import AIChatSearchBox from '@/components/common/AIChatSearchBox.vue';
import LogViewer from '@/components/debug/LogViewer.vue';
import { logger } from '@/utils/logger';

const router = useRouter();
const userStore = useUserStore();
const selectedEmployee = ref('');
const logViewerRef = ref(null);
const agents = ref([]);
const chatHistory = ref([]);

// 模拟数据
const mockAgents = [
  {
    id: 1,
    name: '智能简历解析助手',
    category: '文档处理',
    icon: 'Document',
    description: '自动解析简历内容，提取关键信息，为HR提供便捷的简历管理工具',
    usageCount: 1857,
    rating: 4.8,
    isPopular: true
  },
  {
    id: 2,
    name: '职位匹配推荐师',
    category: '推荐系统',
    icon: 'Connection',
    description: '基于简历内容和职位要求，智能匹配最合适的候选人和职位',
    usageCount: 2103,
    rating: 4.6,
    isPopular: true
  },
  {
    id: 3,
    name: '面试问题生成器',
    category: '内容生成',
    icon: 'ChatDotRound',
    description: '根据职位要求和候选人简历，自动生成针对性的面试问题',
    usageCount: 1580,
    rating: 4.5,
    isPopular: false
  },
  {
    id: 4,
    name: '背景调查助手',
    category: '信息收集',
    icon: 'Search',
    description: '帮助HR进行候选人背景信息收集和验证，提高招聘决策准确性',
    usageCount: 982,
    rating: 4.2,
    isPopular: false
  }
];

// 使用计算属性获取加载状态
const isLoading = computed(() => loadingState.state.agentsList);

// 获取智能体数据
const fetchAgentsList = async () => {
  try {
    logger.info('开始获取智能体列表');
    await loadingState.withLoadingSafe('agentsList', async () => {
      logger.info('模拟API请求延迟...');
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // 这里可以添加真正的API调用
      // const response = await axios.get('/api/agents');
      // agents.value = response.data;
      
      // 使用模拟数据
      agents.value = [...mockAgents];
      
      logger.success('已成功加载智能体数据');
    }, null, { enabled: true, duration: 500 });
  } catch (error) {
    logger.error('获取智能体列表失败', error);
    // 使用模拟数据作为后备
    agents.value = [...mockAgents];
  }
};

// 使用数字员工
const useEmployee = (employeeType: string) => {
  logger.info(`正在启动数字员工: ${employeeType}`);
  
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后使用数字员工');
    router.push({
      path: '/login',
      query: { redirect: router.currentRoute.value.fullPath }
    });
    return;
  }
  
  // 模拟跳转到对话或使用界面的逻辑
  ElMessage.success(`已启动 ${employeeType}，正在初始化...`);
  
  // 实际项目中应该跳转到对应的智能体界面或打开对话窗口
  setTimeout(() => {
    router.push({
      path: '/dashboard/agent-workspace',
      query: { 
        agent: encodeURIComponent(employeeType),
        mode: 'conversation'
      }
    });
  }, 1000);
};

// 替换handleUseEmployee函数
const handleUseEmployee = (employeeType) => {
  useEmployee(employeeType);
};

// 点赞功能
const likeAgent = (agentId) => {
  logger.info(`给智能体ID:${agentId}点赞`);
  ElMessage.success('感谢您的反馈！');
  
  // 这里可以添加真正的API调用来更新点赞数
  // 这里仅模拟更新本地数据
  const agent = agents.value.find(a => a.id === agentId);
  if (agent) {
    agent.rating = Math.min(5, agent.rating + 0.1);
    agent.usageCount += 1;
  }
};

// 处理AI搜索
const handleAISearch = (query: string, parsedCriteria: any) => {
  logger.info('AI搜索条件', { query, parsedCriteria });
  
  // 使用模拟数据
  agents.value = [...mockAgents];
  
  // 基于AI解析的条件过滤
  if (query) {
    // 简单的相关性匹配逻辑 (实际应通过后端API实现)
    agents.value = agents.value.filter(agent => {
      // 将搜索内容转为关键词
      const searchTerms = query.toLowerCase().split(' ');
      
      // 合并代理的所有文本信息
      const agentText = [
        agent.name,
        agent.category,
        agent.description
      ].join(' ').toLowerCase();
      
      // 计算简单的匹配分数
      let matchScore = 0;
      
      // 关键词匹配
      searchTerms.forEach(term => {
        if (agentText.includes(term)) {
          matchScore += 1;
        }
      });
      
      // 类别精确匹配
      if (parsedCriteria.category && agent.category.includes(parsedCriteria.category)) {
        matchScore += 2;
      }
      
      // 特定功能匹配
      if (parsedCriteria.function) {
        if (agent.description.toLowerCase().includes(parsedCriteria.function.toLowerCase())) {
          matchScore += 3;
        }
      }
      
      // 返回匹配分数大于0的数字员工
      return matchScore > 0;
    });
    
    // 按热门程度排序
    agents.value.sort((a, b) => {
      // 首先按是否热门排序
      if (a.isPopular && !b.isPopular) return -1;
      if (!a.isPopular && b.isPopular) return 1;
      
      // 然后按使用人数排序
      return b.usageCount - a.usageCount;
    });
    
    logger.info(`筛选后的数字员工数量: ${agents.value.length}`);
  }
};

// 更新聊天历史
const updateChatHistory = (history) => {
  chatHistory.value = history;
  // 可以保存到本地存储或进行其他处理
};

// 初始化页面
onMounted(() => {
  fetchAgentsList();
  logger.info('DigitalEmployees页面已加载');
  
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

.search-section {
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

.employees-container {
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

.employee-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f9ff;
  color: #409EFF;
  border-radius: 12px;
  margin-right: 16px;
}

.employee-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.employee-header {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.employee-name {
  margin: 0;
  margin-right: 8px;
  font-size: 18px;
  font-weight: 600;
}

.employee-category {
  color: #909399;
  margin: 4px 0;
  font-size: 14px;
}

.employee-desc {
  margin: 4px 0 12px;
  color: #606266;
  font-size: 14px;
}

.employee-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.employee-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.usage-count {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 14px;
}

.employee-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rating {
  display: flex;
  align-items: center;
}

.try-button {
  font-size: 14px;
  padding: 6px 20px;
}
</style> 