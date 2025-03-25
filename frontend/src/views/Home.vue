<template>
  <div class="home-container">
    <el-row class="header">
      <el-col :span="24">
        <div class="app-title">AI帮你找工作</div>
        <div class="action-icons">
          <el-icon><More /></el-icon>
          <el-icon class="circle-icon"><CirclePlus /></el-icon>
        </div>
      </el-col>
    </el-row>

    <!-- 快速匹配和在线沟通模块 -->
    <el-card class="main-card blue-card" @click="navigateToJobRecommendations">
      <div class="card-content">
        <div class="card-title">快速匹配 & 在线沟通</div>
      </div>
    </el-card>

    <el-row :gutter="12" class="feature-row">
      <!-- 科技城人才市场模块 -->
      <el-col :xs="24" :sm="12">
        <el-card class="feature-card blue-bg" @click="navigateToJobMarket">
          <div class="feature-content">
            <div class="feature-title">科技城人才市场</div>
          </div>
        </el-card>
      </el-col>

      <!-- AI在线专业职业测评模块 -->
      <el-col :xs="24" :sm="12">
        <el-card class="feature-card dark-blue-bg" @click="navigateToDigitalEmployees">
          <div class="feature-content">
            <div class="feature-title">AI在线</div>
            <div class="feature-subtitle">专业职业测评</div>
            <el-button round class="action-button" @click.stop="navigateToDigitalEmployees">立即体验</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 智能简历模块 -->
    <el-row class="feature-row">
      <el-col :span="24">
        <el-card class="feature-card orange-bg" @click="navigateToResumes">
          <div class="feature-content">
            <div>
              <div class="feature-title">智能简历</div>
              <div class="feature-text">对求职者上传的简历</div>
              <div class="feature-text">AI自动匹配合适的岗位</div>
              <el-button round class="action-button" @click.stop="navigateToResumes">立即体验</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时数据统计 -->
    <el-card class="stats-card">
      <div class="stats-content">
        <div class="stats-item">
          <div class="stats-label">实时岗位：</div>
          <div class="stats-value">10个</div>
        </div>
        <div class="stats-item">
          <div class="stats-label">实时简历：</div>
          <div class="stats-value">9700个</div>
        </div>
      </div>
    </el-card>

    <!-- 专家顾问模块 -->
    <el-card class="experts-card">
      <div class="experts-content">
        <div class="expert-item">
          <div class="expert-avatar">
            <el-avatar :size="50" src="https://placekitten.com/100/100"></el-avatar>
          </div>
          <div class="expert-info">
            <div class="expert-name">余老师</div>
            <div class="expert-title">人才市场岗位专家</div>
            <el-button round size="small" type="primary" class="chat-button" @click="handleChatWithExpert('余老师')">直接沟通</el-button>
          </div>
        </div>
        
        <div class="expert-item">
          <div class="expert-avatar">
            <el-avatar :size="50" src="https://placekitten.com/101/101"></el-avatar>
          </div>
          <div class="expert-info">
            <div class="expert-name">徐老师</div>
            <div class="expert-title">高级简历优化专家</div>
            <el-button round size="small" type="primary" class="chat-button" @click="handleChatWithExpert('徐老师')">直接沟通</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 市场动态模块 -->
    <div class="section-header" @click="navigateToNews">
      <div class="section-title">市场动态</div>
      <div class="section-more">更多</div>
    </div>

    <el-card class="market-news-card" @click="navigateToNews">
      <div class="news-item">
        <div class="news-icon">72</div>
        <div class="news-title">最新招聘市场趋势分析</div>
      </div>
    </el-card>

    <!-- 底部导航 -->
    <BottomNavigation active-item="home" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { 
  More, 
  CirclePlus, 
  House, 
  UserFilled, 
  Service, 
  Avatar 
} from '@element-plus/icons-vue';
import { useLoading } from '@/utils/loadingState';
import { useUserStore } from '@/store/user';
import BottomNavigation from '@/components/layout/BottomNavigation.vue';

const router = useRouter();
const { isLoading, withLoading } = useLoading();
const userStore = useUserStore();

// 检查用户登录状态并决定是否需要重定向到登录页
const checkLoginRedirect = (route: string): boolean => {
  if (!userStore.isLoggedIn) {
    const publicRoutes = ['jobs-market', 'digital-employees'];
    const routeName = route.split('/').pop() || '';
    
    if (!publicRoutes.includes(routeName)) {
      ElMessage.warning('请先登录后访问此功能');
      router.push({
        path: '/login',
        query: { redirect: route }
      });
      return false;
    }
  }
  return true;
};

// 首页导航功能
const navigateToJobMarket = () => {
  router.push('/dashboard/jobs-market');
};

const navigateToResumes = () => {
  if (checkLoginRedirect('/dashboard/resume')) {
    router.push('/dashboard/resume');
  }
};

const navigateToDigitalEmployees = () => {
  router.push('/dashboard/digital-employees');
};

const navigateToProfile = () => {
  if (checkLoginRedirect('/dashboard/profile')) {
    router.push('/dashboard/profile');
  }
};

const navigateToJobRecommendations = () => {
  if (checkLoginRedirect('/dashboard/job-recommendations')) {
    router.push('/dashboard/job-recommendations');
  }
};

const navigateToNews = () => {
  ElMessage.info('市场动态功能即将上线');
};

// 与专家沟通功能
const handleChatWithExpert = (expertName: string) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后与专家沟通');
    router.push({
      path: '/login',
      query: { redirect: router.currentRoute.value.fullPath }
    });
    return;
  }
  
  ElMessage.success(`正在连接${expertName}...`);
};

// 加载数据
onMounted(async () => {
  // 这里可以添加获取首页数据的逻辑
});
</script>

<style scoped>
.home-container {
  padding: 16px;
  background-color: #f5f7fa;
  min-height: 100vh;
  position: relative;
  padding-bottom: 60px; /* 为底部导航留出空间 */
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.app-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  text-align: center;
  flex-grow: 1;
}

.action-icons {
  position: absolute;
  right: 16px;
  top: 16px;
  display: flex;
  align-items: center;
}

.circle-icon {
  margin-left: 12px;
}

.main-card {
  margin-bottom: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.main-card:hover {
  transform: translateY(-2px);
}

.blue-card {
  background-color: #4e6ef2;
  color: white;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-content {
  text-align: center;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
}

.feature-row {
  margin-bottom: 16px;
}

.feature-card {
  height: 120px;
  border-radius: 8px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  cursor: pointer;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-2px);
}

.blue-bg {
  background-color: #4e6ef2;
}

.dark-blue-bg {
  background-color: #1e293b;
}

.orange-bg {
  background-color: #f5723e;
}

.feature-content {
  text-align: center;
  padding: 15px;
}

.feature-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 4px;
}

.feature-subtitle {
  font-size: 14px;
  margin-bottom: 8px;
}

.feature-text {
  font-size: 12px;
  margin-bottom: 4px;
  color: rgba(255, 255, 255, 0.9);
}

.action-button {
  background: white;
  color: #333;
  margin-top: 8px;
  padding: 6px 16px;
  font-size: 12px;
}

.stats-card {
  margin-bottom: 16px;
  border-radius: 8px;
}

.stats-content {
  display: flex;
  justify-content: space-between;
  padding: 10px 15px;
}

.stats-item {
  display: flex;
  align-items: baseline;
}

.stats-label {
  font-size: 14px;
  color: #666;
}

.stats-value {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
  margin-left: 4px;
}

.experts-card {
  margin-bottom: 16px;
  border-radius: 8px;
}

.experts-content {
  padding: 15px;
}

.expert-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.expert-avatar {
  margin-right: 12px;
}

.expert-info {
  flex: 1;
}

.expert-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 4px;
}

.expert-title {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.chat-button {
  padding: 4px 12px;
  font-size: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  cursor: pointer;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
}

.section-more {
  font-size: 14px;
  color: #409eff;
}

.market-news-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.market-news-card:hover {
  transform: translateY(-2px);
}

.news-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.news-icon {
  width: 40px;
  height: 40px;
  background-color: #95de64;
  color: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 12px;
}

.news-title {
  font-size: 14px;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  background-color: white;
  display: flex;
  justify-content: space-around;
  align-items: center;
  border-top: 1px solid #eee;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #999;
  font-size: 22px;
}

.nav-label {
  font-size: 12px;
  margin-top: 4px;
}

.nav-item.active {
  color: #f56c6c;
}

@media (max-width: 768px) {
  .home-container {
    padding: 12px;
  }
}
</style> 