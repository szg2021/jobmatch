<template>
  <div class="dashboard-layout">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useUserStore } from '@/store/user';

const userStore = useUserStore();

onMounted(() => {
  // 在组件挂载时加载用户信息
  userStore.fetchUserProfile();
});
</script>

<style scoped>
.dashboard-layout {
  height: 100%;
  width: 100%;
}
</style> 