<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="welcome-card">
          <div class="welcome-message">
            <h2>欢迎回来，{{ userName }}</h2>
            <p>今天是 {{ currentDate }}，开始探索适合您的机会吧！</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-section">
      <el-col :span="24">
        <h3 class="section-title">智能推荐</h3>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card" @click="navigateTo('/recommendations')">
          <div class="feature-icon">
            <el-icon><connection /></el-icon>
          </div>
          <div class="feature-content">
            <h4>职位推荐</h4>
            <p>基于您的简历和偏好，为您推荐最匹配的职位</p>
          </div>
          <div class="feature-action">
            <el-button type="primary" plain>查看推荐</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" v-if="isCompanyUser">
        <el-card shadow="hover" class="feature-card" @click="navigateTo('/recommendations?mode=resume')">
          <div class="feature-icon">
            <el-icon><user /></el-icon>
          </div>
          <div class="feature-content">
            <h4>人才推荐</h4>
            <p>为您的职位寻找最合适的候选人</p>
          </div>
          <div class="feature-action">
            <el-button type="primary" plain>查看推荐</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card" @click="navigateTo('/jobs')">
          <div class="feature-icon">
            <el-icon><opportunity /></el-icon>
          </div>
          <div class="feature-content">
            <h4>热门职位</h4>
            <p>浏览当前市场上的热门职位机会</p>
          </div>
          <div class="feature-action">
            <el-button type="primary" plain>浏览职位</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-section">
      <el-col :span="24">
        <h3 class="section-title">个人中心</h3>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" v-if="!isCompanyUser">
        <el-card shadow="hover" class="feature-card" @click="navigateTo('/resumes')">
          <div class="feature-icon">
            <el-icon><document /></el-icon>
          </div>
          <div class="feature-content">
            <h4>我的简历</h4>
            <p>管理您的简历，提高匹配度</p>
          </div>
          <div class="feature-action">
            <el-button type="primary" plain>管理简历</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" v-if="isCompanyUser">
        <el-card shadow="hover" class="feature-card" @click="navigateTo('/jobs/manage')">
          <div class="feature-icon">
            <el-icon><briefcase /></el-icon>
          </div>
          <div class="feature-content">
            <h4>职位管理</h4>
            <p>管理您发布的职位和申请</p>
          </div>
          <div class="feature-action">
            <el-button type="primary" plain>管理职位</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card" @click="navigateTo('/profile')">
          <div class="feature-icon">
            <el-icon><setting /></el-icon>
          </div>
          <div class="feature-content">
            <h4>账户设置</h4>
            <p>更新您的个人信息和偏好设置</p>
          </div>
          <div class="feature-action">
            <el-button type="primary" plain>设置</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-section" v-if="isAdmin">
      <el-col :span="24">
        <h3 class="section-title">系统管理</h3>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card" @click="navigateTo('/admin')">
          <div class="feature-icon">
            <el-icon><platform /></el-icon>
          </div>
          <div class="feature-content">
            <h4>管理控制台</h4>
            <p>访问系统管理功能</p>
          </div>
          <div class="feature-action">
            <el-button type="primary" plain>进入控制台</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card" @click="navigateTo('/admin/recommendation-config')">
          <div class="feature-icon">
            <el-icon><set-up /></el-icon>
          </div>
          <div class="feature-content">
            <h4>推荐系统配置</h4>
            <p>配置推荐算法和参数</p>
          </div>
          <div class="feature-action">
            <el-button type="primary" plain>配置</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { 
  Connection, 
  User, 
  Opportunity, 
  Document, 
  Briefcase, 
  Setting,
  Platform,
  SetUp
} from '@element-plus/icons-vue'

const router = useRouter()
const store = useStore()

// 用户信息
const userName = computed(() => store.state.user?.name || '用户')
const userRole = computed(() => store.state.user?.role || '')
const isCompanyUser = computed(() => userRole.value === 'company')
const isAdmin = computed(() => userRole.value === 'admin')

// 当前日期
const currentDate = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})

// 导航方法
const navigateTo = (path) => {
  router.push(path)
}

// 在组件挂载时获取用户信息
onMounted(() => {
  if (!store.state.user) {
    store.dispatch('fetchCurrentUser')
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 30px;
  background-color: #f0f9ff;
}

.welcome-message {
  padding: 10px;
}

.welcome-message h2 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 24px;
  font-weight: 500;
}

.section-title {
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 500;
  color: #606266;
  border-left: 4px solid #409eff;
  padding-left: 10px;
}

.dashboard-section {
  margin-bottom: 30px;
}

.feature-card {
  height: 200px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 30px;
  color: #409eff;
  margin-bottom: 15px;
}

.feature-content {
  flex: 1;
}

.feature-content h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: 500;
}

.feature-content p {
  color: #606266;
  font-size: 14px;
}

.feature-action {
  margin-top: 10px;
}
</style> 