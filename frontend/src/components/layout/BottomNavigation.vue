<template>
  <div class="bottom-nav">
    <div 
      class="nav-item" 
      :class="{ active: currentActiveItem === 'home' }"
      @click="navigate('home')"
    >
      <el-icon><House /></el-icon>
      <div class="nav-label">首页</div>
    </div>
    <div 
      class="nav-item" 
      :class="{ active: currentActiveItem === 'jobs-market' }"
      @click="navigate('jobs-market')"
    >
      <el-icon><UserFilled /></el-icon>
      <div class="nav-label">人才市场</div>
    </div>
    <div 
      class="nav-item" 
      :class="{ active: currentActiveItem === 'digital-employees' }"
      @click="navigate('digital-employees')"
    >
      <el-icon><Service /></el-icon>
      <div class="nav-label">数字员工</div>
    </div>
    <div 
      class="nav-item" 
      :class="{ active: currentActiveItem === 'profile' }"
      @click="navigate('profile')"
    >
      <el-icon><Avatar /></el-icon>
      <div class="nav-label">个人中心</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router';
import { computed } from 'vue';
import { 
  House, 
  UserFilled, 
  Service, 
  Avatar 
} from '@element-plus/icons-vue';
import { useUserStore } from '@/store/user';

interface Props {
  activeItem?: 'home' | 'jobs-market' | 'digital-employees' | 'profile';
}

const props = withDefaults(defineProps<Props>(), {
  activeItem: 'home'
});

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

// 计算当前活动的菜单项
const currentActiveItem = computed(() => {
  const path = route.path;
  if (path === '/' || path === '/dashboard') return 'home';
  if (path.includes('jobs-market')) return 'jobs-market';
  if (path.includes('digital-employees')) return 'digital-employees';
  if (path.includes('profile')) return 'profile';
  return props.activeItem;
});

// 导航函数
const navigate = (route: string) => {
  switch (route) {
    case 'home':
      router.push('/');
      break;
    case 'jobs-market':
      if (userStore.isLoggedIn) {
        router.push('/dashboard/jobs-market');
      } else {
        // 允许游客访问，但记录重定向信息
        router.push('/dashboard/jobs-market');
      }
      break;
    case 'digital-employees':
      if (userStore.isLoggedIn) {
        router.push('/dashboard/digital-employees');
      } else {
        // 允许游客访问，但记录重定向信息
        router.push('/dashboard/digital-employees');
      }
      break;
    case 'profile':
      if (userStore.isLoggedIn) {
        router.push('/dashboard/profile');
      } else {
        // 未登录时，点击个人中心跳转登录页
        router.push('/login');
      }
      break;
  }
};
</script>

<style scoped>
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
</style> 