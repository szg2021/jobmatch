<template>
  <page-content-wrapper>
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
      <div class="announcement-text">优质HR已上线, 欢迎前来应聘, 应届生德维优先录用！</div>
    </div>

    <!-- 标签切换 -->
    <div class="tab-container">
      <div class="tab" @click="switchToJobs">招聘岗位</div>
      <div class="tab active">人才简历</div>
    </div>

    <!-- 搜索框 -->
    <div class="search-section">
      <search-box
        v-model="searchQuery"
        placeholder="搜索姓名、职位等"
        @search="fetchTalents"
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
          <el-form-item label="年龄范围">
            <el-select v-model="advancedFilters.ageRange" placeholder="全部" clearable>
              <el-option label="18-25岁" value="18-25" />
              <el-option label="26-30岁" value="26-30" />
              <el-option label="31-35岁" value="31-35" />
              <el-option label="36-40岁" value="36-40" />
              <el-option label="40岁以上" value="40+" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="教育背景">
            <el-select v-model="advancedFilters.education" placeholder="全部" clearable>
              <el-option label="高中及以下" value="高中及以下" />
              <el-option label="大专" value="大专" />
              <el-option label="本科" value="本科" />
              <el-option label="硕士" value="硕士" />
              <el-option label="博士" value="博士" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="工作经验">
            <el-select v-model="advancedFilters.experience" placeholder="全部" clearable>
              <el-option label="应届毕业生" value="0" />
              <el-option label="1-3年" value="1-3" />
              <el-option label="3-5年" value="3-5" />
              <el-option label="5-10年" value="5-10" />
              <el-option label="10年以上" value="10+" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="求职状态">
            <el-select v-model="advancedFilters.status" placeholder="全部" clearable>
              <el-option label="在职找工作" value="在职找工作" />
              <el-option label="已离职求职" value="已离职求职" />
              <el-option label="应届毕业生" value="应届毕业生" />
              <el-option label="实习生" value="实习生" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="技能">
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

    <!-- 人才列表 -->
    <div class="talent-list" v-loading="loadingState.isLoading">
      <template v-if="talents.length > 0">
        <div class="talent-card" v-for="talent in talents" :key="talent.id">
          <div class="talent-header">
            <div class="talent-info">
              <div class="talent-name">{{ talent.name }}</div>
              <div class="talent-detail">
                <span>{{ talent.age }}岁</span>
                <span>{{ talent.education }}</span>
                <span>{{ talent.experience }}年经验</span>
              </div>
            </div>
            <div class="talent-bookmark">
              <el-icon><House /></el-icon>
            </div>
          </div>
          
          <div class="talent-skill-section">
            <div class="section-label">求职意向：</div>
            <div class="talent-skills">
              <status-tag 
                v-for="(skill, index) in talent.skills" 
                :key="index" 
                :text="skill"
                status="success" 
                effect="light"
                size="small"
              />
            </div>
          </div>
          
          <div class="talent-footer">
            <div class="update-time">更新时间：</div>
            <div class="talent-status">{{ talent.status }}</div>
          </div>
        </div>
      </template>
      <el-empty v-else description="暂无人才简历信息"></el-empty>
      
      <div class="load-more" v-if="talents.length > 0">
        <el-button type="primary" plain text>加载更多</el-button>
      </div>
    </div>

    <!-- 底部导航 -->
    <BottomNavigation active-item="jobs-market" />
  </page-content-wrapper>
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
  House, 
  UserFilled, 
  Service, 
  Avatar,
  ArrowDown,
  ArrowUp
} from '@element-plus/icons-vue';
import api from '@/utils/api';
import { useLoading } from '@/utils/loadingState';
import BottomNavigation from '@/components/layout/BottomNavigation.vue';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
import SearchBox from '@/components/common/SearchBox.vue';
import StatusTag from '@/components/common/StatusTag.vue';

interface Talent {
  id: string;
  name: string;
  age: number;
  education: string;
  experience: number;
  skills: string[];
  status: string;
  updated_at?: string;
}

const router = useRouter();
const loadingState = useLoading();
const talents = ref<Talent[]>([]);
const searchQuery = ref('');

// 高级搜索相关
const showAdvancedSearch = ref(false);
const advancedFilters = reactive({
  ageRange: '',
  education: '',
  experience: '',
  status: '',
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

// 切换到招聘岗位标签
const switchToJobs = () => {
  router.push('/dashboard/jobs-market');
};

// 切换高级搜索面板
const toggleAdvancedSearch = () => {
  showAdvancedSearch.value = !showAdvancedSearch.value;
};

// 应用高级筛选
const applyAdvancedFilters = () => {
  fetchTalents();
};

// 重置高级筛选
const resetAdvancedFilters = () => {
  Object.assign(advancedFilters, {
    ageRange: '',
    education: '',
    experience: '',
    status: '',
    skills: []
  });
  fetchTalents();
};

// 搜索处理
const handleSearch = () => {
  fetchTalents();
};

// 获取人才列表
const fetchTalents = async () => {
  try {
    await loadingState.withLoading(async () => {
      // 构建查询参数
      const params: Record<string, any> = {};
      if (searchQuery.value) {
        params.search = searchQuery.value;
      }
      
      // 添加高级筛选条件
      if (advancedFilters.ageRange) params.age_range = advancedFilters.ageRange;
      if (advancedFilters.education) params.education = advancedFilters.education;
      if (advancedFilters.experience) params.experience = advancedFilters.experience;
      if (advancedFilters.status) params.status = advancedFilters.status;
      if (advancedFilters.skills.length > 0) params.skills = advancedFilters.skills.join(',');
      
      // 这里应该是调用后端API获取人才数据
      // const response = await api.get('/talents', { params });
      // talents.value = response.data || [];
      
      // 由于后端可能还没有实现此接口，这里使用模拟数据
      return new Promise(resolve => {
        setTimeout(() => {
          talents.value = [
            {
              id: '1',
              name: '张先生',
              age: 28,
              education: '本科',
              experience: 3,
              skills: ['JavaScript', 'Vue', 'React'],
              status: '已离职求职'
            },
            {
              id: '2',
              name: '李女士',
              age: 30,
              education: '硕士',
              experience: 5,
              skills: ['产品设计', '需求分析', '用户研究'],
              status: '已离职求职'
            }
          ];
          
          // 如果有高级筛选条件，进行本地过滤（实际应该由后端完成）
          if (Object.values(advancedFilters).some(v => v && (Array.isArray(v) ? v.length > 0 : true))) {
            talents.value = talents.value.filter(talent => {
              let matchesAll = true;
              
              // 年龄范围筛选
              if (advancedFilters.ageRange) {
                const [minAge, maxAge] = advancedFilters.ageRange.split('-').map(Number);
                if (minAge && maxAge) {
                  if (talent.age < minAge || talent.age > maxAge) {
                    matchesAll = false;
                  }
                } else if (advancedFilters.ageRange === '40+' && talent.age < 40) {
                  matchesAll = false;
                }
              }
              
              // 教育背景筛选
              if (advancedFilters.education && talent.education !== advancedFilters.education) {
                matchesAll = false;
              }
              
              // 工作经验筛选
              if (advancedFilters.experience) {
                if (advancedFilters.experience === '0' && talent.experience !== 0) {
                  matchesAll = false;
                } else if (advancedFilters.experience === '1-3' && (talent.experience < 1 || talent.experience > 3)) {
                  matchesAll = false;
                } else if (advancedFilters.experience === '3-5' && (talent.experience < 3 || talent.experience > 5)) {
                  matchesAll = false;
                } else if (advancedFilters.experience === '5-10' && (talent.experience < 5 || talent.experience > 10)) {
                  matchesAll = false;
                } else if (advancedFilters.experience === '10+' && talent.experience < 10) {
                  matchesAll = false;
                }
              }
              
              // 求职状态筛选
              if (advancedFilters.status && talent.status !== advancedFilters.status) {
                matchesAll = false;
              }
              
              // 技能筛选
              if (advancedFilters.skills.length > 0) {
                const hasAllSkills = advancedFilters.skills.every(skill => 
                  talent.skills.includes(skill)
                );
                if (!hasAllSkills) {
                  matchesAll = false;
                }
              }
              
              return matchesAll;
            });
          }
          
          resolve(true);
        }, 500);
      });
    });
  } catch (error) {
    console.error('获取人才列表失败:', error);
    ElMessage.error('获取人才列表失败，请稍后重试');
  }
};

// 加载数据
onMounted(() => {
  fetchTalents();
});
</script>

<style scoped>
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

.advanced-search-panel {
  padding: 10px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 16px;
}

.talent-list {
  margin-bottom: 70px;
}

.talent-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.talent-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.talent-info {
  flex: 1;
}

.talent-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 4px;
}

.talent-detail {
  font-size: 13px;
  color: #909399;
}

.talent-detail span {
  margin-right: 10px;
}

.talent-bookmark {
  color: #4e6ef2;
}

.talent-skill-section {
  margin-bottom: 12px;
}

.section-label {
  font-size: 14px;
  margin-bottom: 8px;
  color: #606266;
}

.talent-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.talent-footer {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 13px;
}

.load-more {
  text-align: center;
  margin-top: 16px;
}
</style> 