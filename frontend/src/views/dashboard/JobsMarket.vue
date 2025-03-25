<template>
  <PageContentWrapper>
    <div class="page-header">
      <div class="page-title">人才市场</div>
      <div class="header-controls">
        <el-icon><More /></el-icon>
        <el-icon class="circle-icon"><CirclePlus /></el-icon>
      </div>
    </div>

    <!-- 公告栏 -->
    <div class="announcement-bar">
      <el-icon><Bell /></el-icon>
      <div class="announcement-text">热烈祝贺我司成功入选2023年度最佳雇主企业！</div>
    </div>

    <!-- 标签切换 -->
    <div class="tab-container">
      <div class="tab active">招聘岗位</div>
      <div class="tab">人才简历</div>
    </div>

    <!-- 搜索框 -->
    <div class="search-section">
      <SearchBox
        v-model="searchQuery"
        placeholder="搜索职位名称、公司等"
        @search="fetchJobs"
      />
      
      <el-button 
        type="primary" 
        plain 
        class="advanced-search-btn"
        @click="toggleAdvancedSearch"
      >
        {{ showAdvancedSearch ? '隐藏高级搜索' : '高级搜索' }}
        <el-icon><ArrowDown v-if="!showAdvancedSearch" /><ArrowUp v-else /></el-icon>
      </el-button>
    </div>
    
    <!-- 高级搜索面板 -->
    <el-collapse-transition>
      <div v-show="showAdvancedSearch" class="advanced-search-panel">
        <el-form :model="advancedFilters" label-width="100px" size="small" inline>
          <el-form-item label="职位类型">
            <el-select v-model="advancedFilters.jobType" placeholder="全部" clearable>
              <el-option label="全职" value="全职" />
              <el-option label="兼职" value="兼职" />
              <el-option label="实习" value="实习" />
              <el-option label="自由职业" value="自由职业" />
              <el-option label="远程" value="远程" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="地点">
            <el-input v-model="advancedFilters.location" placeholder="输入城市" clearable />
          </el-form-item>
          
          <el-form-item label="经验要求">
            <el-select v-model="advancedFilters.experience" placeholder="全部" clearable>
              <el-option label="无经验" value="无经验" />
              <el-option label="1-3年" value="1-3年" />
              <el-option label="3-5年" value="3-5年" />
              <el-option label="5-10年" value="5-10年" />
              <el-option label="10年以上" value="10年以上" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="薪资范围">
            <el-select v-model="advancedFilters.salary" placeholder="全部" clearable>
              <el-option label="面议" value="面议" />
              <el-option label="5k以下" value="<5k" />
              <el-option label="5k-10k" value="5k-10k" />
              <el-option label="10k-15k" value="10k-15k" />
              <el-option label="15k-20k" value="15k-20k" />
              <el-option label="20k-30k" value="20k-30k" />
              <el-option label="30k以上" value=">30k" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="技能要求">
            <el-select
              v-model="advancedFilters.skills"
              multiple
              collapse-tags
              collapse-tags-tooltip
              placeholder="选择技能"
              style="width: 240px"
            >
              <el-option
                v-for="skill in commonSkills"
                :key="skill"
                :label="skill"
                :value="skill"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="applyAdvancedFilters">应用筛选</el-button>
            <el-button @click="resetAdvancedFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-collapse-transition>

    <!-- 职位列表 -->
    <div class="job-list">
      <template v-if="jobs.length > 0">
        <div 
          class="job-card" 
          v-for="job in jobs" 
          :key="job.job_id"
          @click="handleJobCardClick(job)"
        >
          <div class="job-header">
            <div class="job-title">{{ job.title }}</div>
            <div class="job-salary">{{ job.salary_range }}</div>
          </div>
          <div class="job-company">{{ job.company_name }}</div>
          <div class="job-location">{{ job.location }}</div>
          <div class="job-tags">
            <StatusTag
              v-for="(tag, index) in getJobTags(job)"
              :key="index"
              :text="tag"
              status="info"
            />
          </div>
          <div class="job-info-row">
            <div class="job-applicants">{{ job.applicants || 0 }}人已申请</div>
            <div class="job-date">{{ formatDate(job.created_at) }}</div>
          </div>
          <div class="job-actions">
            <el-button 
              size="small" 
              type="primary" 
              plain 
              class="action-button"
              @click="(e) => handleContact(e, job)"
            >
              在线沟通
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              class="action-button"
              @click="(e) => handleApply(e, job)"
            >
              立即报名
            </el-button>
          </div>
        </div>
      </template>
      <el-empty v-else description="暂无招聘岗位信息"></el-empty>
    </div>

    <!-- 底部导航 -->
    <BottomNavigation active-item="jobs-market" />

    <!-- 添加日志查看器组件 -->
    <LogViewer ref="logViewerRef" />
  </PageContentWrapper>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { 
  More, 
  CirclePlus, 
  Search, 
  Bell,
  ArrowDown,
  ArrowUp
} from '@element-plus/icons-vue';
import api from '@/utils/api';
import { formatDate } from '@/utils/helpers';
import { useLoading } from '@/utils/loadingState';
import { useUserStore } from '@/store/user';
import type { Job } from '@/types';
import BottomNavigation from '@/components/layout/BottomNavigation.vue';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
import SearchBox from '@/components/common/SearchBox.vue';
import StatusTag from '@/components/common/StatusTag.vue';
import LogViewer from '@/components/debug/LogViewer.vue';
import logger from '@/utils/logger';

const router = useRouter();
const loadingState = useLoading();
const userStore = useUserStore();
const jobs = ref<Job[]>([]);
const searchQuery = ref('');
const logViewerRef = ref(null);

// 高级搜索相关
const showAdvancedSearch = ref(false);
const advancedFilters = reactive({
  jobType: '',
  location: '',
  experience: '',
  salary: '',
  skills: [] as string[]
});

// 常用技能列表供选择
const commonSkills = [
  'JavaScript', 'TypeScript', 'React', 'Vue', 'Angular',
  'Node.js', 'Python', 'Java', 'C++', 'Go',
  'SQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
  'AWS', 'Azure', 'GCP', 'UI/UX', 'Figma',
  'Product Management', 'Agile', 'Scrum', 'Marketing', 'Sales',
  'Finance', 'HR', 'Operations', 'Communication', 'Leadership'
];

// 获取职位标签
const getJobTags = (job: Job) => {
  if (!job) return [];
  
  const tags = [];
  if (job.job_type) tags.push(job.job_type);
  
  // 确保requirements存在且是数组
  if (job.requirements && Array.isArray(job.requirements) && job.requirements.length > 0) {
    // 最多显示3个技能标签
    return [...tags, ...job.requirements.slice(0, 3)];
  }
  
  return tags;
};

// 切换高级搜索面板
const toggleAdvancedSearch = () => {
  showAdvancedSearch.value = !showAdvancedSearch.value;
};

// 应用高级筛选
const applyAdvancedFilters = () => {
  fetchJobs();
};

// 重置高级筛选
const resetAdvancedFilters = () => {
  Object.assign(advancedFilters, {
    jobType: '',
    location: '',
    experience: '',
    salary: '',
    skills: []
  });
  fetchJobs();
};

// 获取职位列表
const fetchJobs = async () => {
  try {
    logger.info('开始获取职位列表数据');
    
    // 直接使用静态数据，不尝试调用API
    jobs.value = [
      {
        job_id: '1',
        title: '前端开发工程师',
        company_name: '科技有限公司',
        location: '北京',
        job_type: '全职',
        salary_range: '15k-25k',
        description: '负责公司产品的前端开发...',
        requirements: ['JavaScript', 'Vue.js', 'React'],
        is_active: true,
        created_at: new Date().toISOString(),
        applicants: 25
      },
      {
        job_id: '2',
        title: '产品经理',
        company_name: '互联网科技公司',
        location: '上海',
        job_type: '全职',
        salary_range: '20k-30k',
        description: '负责产品规划与设计...',
        requirements: ['产品设计', '需求分析', '用户研究'],
        is_active: true,
        created_at: new Date().toISOString(),
        applicants: 18
      },
      {
        job_id: '3',
        title: 'Java后端开发工程师',
        company_name: '金融科技有限公司',
        location: '深圳',
        job_type: '全职',
        salary_range: '25k-35k',
        description: '负责系统后端开发与优化...',
        requirements: ['Java', 'Spring Boot', 'MySQL'],
        is_active: true,
        created_at: new Date().toISOString(),
        applicants: 32
      },
      {
        job_id: '4',
        title: 'UI/UX设计师',
        company_name: '设计创意公司',
        location: '杭州',
        job_type: '全职',
        salary_range: '12k-20k',
        description: '负责产品界面设计与用户体验优化...',
        requirements: ['Figma', 'Adobe XD', '用户研究'],
        is_active: true,
        created_at: new Date().toISOString(),
        applicants: 15
      }
    ];
    
    logger.success('已成功加载职位数据');
    
    // 如果有搜索或筛选条件，可以在客户端进行过滤
    if (searchQuery.value || 
        advancedFilters.jobType || 
        advancedFilters.location || 
        advancedFilters.experience || 
        advancedFilters.salary || 
        advancedFilters.skills.length > 0) {
      
      logger.info('正在应用筛选条件', { 
        searchQuery: searchQuery.value,
        filters: { ...advancedFilters }
      });
      
      jobs.value = jobs.value.filter(job => {
        // 搜索查询筛选
        const matchesSearch = !searchQuery.value || 
          job.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          job.company_name.toLowerCase().includes(searchQuery.value.toLowerCase());
        
        if (!matchesSearch) return false;
        
        // 职位类型筛选
        const matchesJobType = !advancedFilters.jobType || 
          job.job_type === advancedFilters.jobType;
        
        if (!matchesJobType) return false;
        
        // 地点筛选
        const matchesLocation = !advancedFilters.location || 
          job.location.includes(advancedFilters.location);
        
        if (!matchesLocation) return false;
        
        // 技能筛选
        const matchesSkills = advancedFilters.skills.length === 0 || 
          advancedFilters.skills.some(skill => 
            job.requirements && job.requirements.includes(skill)
          );
        
        if (!matchesSkills) return false;
        
        return true;
      });
      
      logger.info(`筛选后剩余职位: ${jobs.value.length}个`);
    }
    
    // 模拟API延迟 (添加短暂延迟以提供更好的用户体验)
    await new Promise(resolve => setTimeout(resolve, 300));
    
  } catch (error) {
    logger.error('职位列表加载过程发生异常', error);
    ElMessage.error('加载职位信息时发生错误');
  }
};

// 职位卡片点击处理
const handleJobCardClick = (job: Job) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后查看详情');
    router.push({
      path: '/login',
      query: { redirect: router.currentRoute.value.fullPath }
    });
    return;
  }
  
  // 这里添加查看职位详情的逻辑
  ElMessage.success(`查看职位: ${job.title}`);
};

// 处理在线沟通
const handleContact = (event: Event, job: Job) => {
  event.stopPropagation(); // 阻止冒泡
  
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后进行在线沟通');
    router.push({
      path: '/login',
      query: { redirect: router.currentRoute.value.fullPath }
    });
    return;
  }
  
  // 这里添加在线沟通的逻辑
  ElMessage.success(`与 ${job.company_name} 进行在线沟通`);
};

// 处理立即报名
const handleApply = (event: Event, job: Job) => {
  event.stopPropagation(); // 阻止冒泡
  
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后进行报名');
    router.push({
      path: '/login',
      query: { redirect: router.currentRoute.value.fullPath }
    });
    return;
  }
  
  // 这里添加立即报名的逻辑
  ElMessage.success(`已报名职位: ${job.title}`);
};

// 组件挂载后注册日志组件实例
onMounted(() => {
  fetchJobs();
  if (logViewerRef.value) {
    import('@/utils/logger').then(({ registerLogViewer }) => {
      registerLogViewer(logViewerRef.value);
      logger.info('JobsMarket页面已加载');
    });
  }
});
</script>

<style scoped>
.jobs-market-container {
  padding: 16px;
  padding-bottom: 70px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 16px;
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

.announcement-bar {
  background-color: #fff8e6;
  border-radius: 4px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.announcement-bar .el-icon {
  color: #e6a23c;
  margin-right: 8px;
  font-size: 16px;
}

.announcement-text {
  color: #cf5f0f;
  font-size: 14px;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tab-container {
  display: flex;
  margin-bottom: 16px;
  background-color: #fff;
  border-radius: 4px;
  padding: 2px;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-size: 16px;
  cursor: pointer;
  color: #606266;
  transition: all 0.3s;
  border-bottom: 2px solid transparent;
}

.tab.active {
  color: #4e6ef2;
  border-bottom-color: #4e6ef2;
  font-weight: bold;
}

.search-section {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.advanced-search-btn {
  margin-left: 10px;
}

.job-list {
  margin-bottom: 16px;
}

.job-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.job-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.job-salary {
  color: #f56c6c;
  font-weight: bold;
  font-size: 14px;
}

.job-company {
  color: #606266;
  font-size: 14px;
  margin-bottom: 4px;
}

.job-location {
  color: #909399;
  font-size: 13px;
  margin-bottom: 12px;
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.job-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  color: #909399;
  font-size: 12px;
}

.job-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.action-button {
  flex: 1;
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
  cursor: pointer;
}

.nav-label {
  font-size: 12px;
  margin-top: 4px;
}

.nav-item.active {
  color: #f56c6c;
}

.advanced-search-panel {
  padding: 10px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}
</style> 