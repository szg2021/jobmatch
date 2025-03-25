<template>
  <PageContentWrapper className="dashboard-home">
    <div class="welcome-banner">
      <h1>欢迎回来，{{ userStore.userFullName }}</h1>
      <p>今天是 {{ today }}，祝您有个愉快的一天！</p>
    </div>

    <el-row :gutter="20" v-loading="loadingState.isLoading">
      <!-- 求职者卡片 -->
      <el-col :xs="24" :sm="12" :md="8" v-if="userStore.isJobSeeker">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>我的简历</span>
              <el-button text @click="navigateTo('/dashboard/resume')">管理</el-button>
            </div>
          </template>
          <div class="card-content">
            <el-empty v-if="!resumeStore.hasResumes" description="您还没有上传简历">
              <el-button type="primary" @click="navigateTo('/dashboard/resume')">上传简历</el-button>
            </el-empty>
            <div v-else class="stat-info">
              <div class="stat-number">{{ resumeStore.resumes.length }}</div>
              <div class="stat-description">已上传的简历</div>
              <el-progress 
                :percentage="100" 
                :format="() => ''" 
                status="success"
                style="margin-top: 10px;"
              />
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8" v-if="userStore.isJobSeeker">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>职位推荐</span>
              <el-button text @click="navigateTo('/dashboard/job-recommendations')">查看</el-button>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-info">
              <div class="stat-number">{{ jobRecommendationsCount }}</div>
              <div class="stat-description">推荐的职位</div>
              <el-button 
                type="primary" 
                style="margin-top: 15px;"
                @click="navigateTo('/dashboard/job-recommendations')"
              >
                查看职位推荐
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 企业用户卡片 -->
      <el-col :xs="24" :sm="12" :md="8" v-if="userStore.isCompany">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>职位管理</span>
              <el-button text @click="navigateTo('/dashboard/jobs')">管理</el-button>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-info">
              <div class="stat-number">0</div>
              <div class="stat-description">已发布的职位</div>
              <el-button 
                type="primary" 
                style="margin-top: 15px;"
                @click="navigateTo('/dashboard/jobs')"
              >
                发布新职位
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8" v-if="userStore.isCompany">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>人才推荐</span>
              <el-button text @click="navigateTo('/dashboard/candidate-recommendations')">查看</el-button>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-info">
              <div class="stat-number">0</div>
              <div class="stat-description">推荐的候选人</div>
              <el-button 
                type="primary" 
                style="margin-top: 15px;"
                @click="navigateTo('/dashboard/candidate-recommendations')"
              >
                查看人才推荐
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 管理员卡片 -->
      <el-col :xs="24" :sm="12" :md="8" v-if="userStore.isAdmin">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>管理控制台</span>
              <el-button text @click="navigateTo('/dashboard/admin')">进入</el-button>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-info">
              <div class="stat-description">系统管理</div>
              <el-button 
                type="primary" 
                style="margin-top: 15px;"
                @click="navigateTo('/dashboard/admin')"
              >
                进入控制台
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 所有用户都可见的卡片 -->
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>个人资料</span>
              <el-button text @click="navigateTo('/dashboard/profile')">编辑</el-button>
            </div>
          </template>
          <div class="card-content profile-card-content">
            <el-avatar :size="64" :icon="User" class="avatar" />
            <div class="profile-info">
              <h3>{{ userStore.userFullName }}</h3>
              <p>{{ userRoleText }}</p>
              <el-button 
                type="primary" 
                plain
                size="small"
                style="margin-top: 10px;"
                @click="navigateTo('/dashboard/profile')"
              >
                编辑资料
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </PageContentWrapper>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/user';
import { useResumeStore } from '@/store/resume';
import { useRecommendationStore } from '@/store/recommendation';
import { User } from '@element-plus/icons-vue';
import { User as UserType } from '@/types';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
import { useLoading } from '@/utils/loadingState';

const router = useRouter();
const userStore = useUserStore();
const resumeStore = useResumeStore();
const recommendationStore = useRecommendationStore();
const loadingState = useLoading();

const today = computed(() => {
  const date = new Date();
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    weekday: 'long'
  });
});

const userRoleText = computed(() => {
  if (userStore.isAdmin) return '管理员';
  if (userStore.isJobSeeker) return '求职者';
  if (userStore.isCompany) {
    const user = userStore.user as UserType;
    return `企业用户 - ${user.company_name || ''}`;
  }
  return '用户';
});

const jobRecommendationsCount = ref(0);

onMounted(async () => {
  // 如果是求职者，加载简历
  if (userStore.isJobSeeker && !resumeStore.hasResumes) {
    try {
      await loadingState.withLoading(async () => {
        await resumeStore.fetchResumes();
        
        // 获取第一份简历的推荐
        if (resumeStore.hasResumes) {
          const firstResumeId = resumeStore.resumes[0].id;
          await recommendationStore.getJobRecommendations(firstResumeId);
          jobRecommendationsCount.value = recommendationStore.jobRecommendations.length;
        }
      });
    } catch (error) {
      console.error('加载简历数据失败:', error);
    }
  }
});

const navigateTo = (path: string) => {
  router.push(path);
};
</script>

<style scoped>
.dashboard-home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-banner {
  background: linear-gradient(135deg, #409EFF 0%, #36D1DC 100%);
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.welcome-banner h1 {
  font-size: 24px;
  margin: 0;
  margin-bottom: 8px;
}

.welcome-banner p {
  margin: 0;
  opacity: 0.9;
}

.dashboard-card {
  margin-bottom: 20px;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  min-height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.stat-info {
  text-align: center;
  width: 100%;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  color: var(--primary-color);
}

.stat-description {
  color: #909399;
  margin: 8px 0;
}

.profile-card-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  padding: 10px;
}

.avatar {
  margin-right: 20px;
}

.profile-info {
  text-align: left;
}

.profile-info h3 {
  margin: 0;
  font-size: 18px;
}

.profile-info p {
  margin: 4px 0;
  color: #909399;
}
</style> 