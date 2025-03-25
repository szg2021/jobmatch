<template>
  <div class="dashboard-container">
    <el-container class="layout-container">
      <el-aside width="220px" class="aside">
        <div class="logo-container">
          <h1 class="logo-text">{{ title }}</h1>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          :router="true"
          :collapse="isCollapse"
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <template #title>首页</template>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/profile">
            <el-icon><User /></el-icon>
            <template #title>个人资料</template>
          </el-menu-item>
          
          <!-- 求职者菜单 -->
          <template v-if="userStore.isJobSeeker">
            <el-menu-item index="/dashboard/resume">
              <el-icon><Document /></el-icon>
              <template #title>我的简历</template>
            </el-menu-item>
            
            <el-menu-item index="/dashboard/job-recommendations">
              <el-icon><Star /></el-icon>
              <template #title>职位推荐</template>
            </el-menu-item>
          </template>
          
          <!-- 企业用户菜单 -->
          <template v-if="userStore.isCompany">
            <el-menu-item index="/dashboard/jobs">
              <el-icon><Briefcase /></el-icon>
              <template #title>职位管理</template>
            </el-menu-item>
            
            <el-menu-item index="/dashboard/candidate-recommendations">
              <el-icon><UserFilled /></el-icon>
              <template #title>人才推荐</template>
            </el-menu-item>
          </template>
          
          <!-- 管理员菜单 -->
          <template v-if="userStore.isAdmin">
            <el-menu-item index="/dashboard/admin">
              <el-icon><Setting /></el-icon>
              <template #title>管理控制台</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-button
              text
              :icon="isCollapse ? 'Expand' : 'Fold'"
              @click="toggleCollapse"
            />
          </div>
          
          <div class="header-right">
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="user-info">
                <el-avatar :size="32" :icon="User" />
                <span class="user-name">{{ userStore.userFullName }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>个人资料
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main class="main">
          <router-view />
        </el-main>
        
        <el-footer class="footer">
          <div class="footer-content">
            <span>© {{ currentYear }} {{ title }}. 保留所有权利.</span>
          </div>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessageBox } from 'element-plus';
import { 
  House, User, Document, Star, Briefcase, 
  UserFilled, Setting, ArrowDown, SwitchButton,
  Expand, Fold
} from '@element-plus/icons-vue';
import { useUserStore } from '@/store/user';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const isCollapse = ref(false);
const title = import.meta.env.VITE_APP_TITLE || 'AI招聘推荐平台';
const currentYear = new Date().getFullYear();

const activeMenu = computed(() => {
  return route.path;
});

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};

const handleCommand = (command: string) => {
  if (command === 'logout') {
    handleLogout();
  } else if (command === 'profile') {
    router.push('/dashboard/profile');
  }
};

const handleLogout = () => {
  ElMessageBox.confirm('确认退出登录吗?', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout();
  }).catch(() => {
    // 取消退出登录
  });
};

onMounted(() => {
  // 检查是否已经登录
  if (!userStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  
  // 加载用户信息
  if (!userStore.user.id) {
    userStore.fetchUserInfo();
  }
});
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  width: 100%;
}

.layout-container {
  height: 100%;
}

.aside {
  background-color: #304156;
  color: #fff;
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.el-menu-vertical {
  border-right: none;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0 8px;
}

.user-name {
  margin-left: 8px;
  margin-right: 4px;
  font-size: 14px;
}

.main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

.footer {
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  height: 40px;
  border-top: 1px solid #e6e6e6;
}

.footer-content {
  color: #606266;
  font-size: 14px;
}
</style> 