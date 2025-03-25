<template>
  <div 
    class="page-content-wrapper"
    :class="[className, { 'has-bottom-nav': hasBottomNav }]"
  >
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
interface Props {
  className?: string;
  hasBottomNav?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  className: '',
  hasBottomNav: true
});
</script>

<style scoped>
.page-content-wrapper {
  padding: 16px;
  background-color: #f5f7fa;
  min-height: 100vh;
  position: relative;
}

.has-bottom-nav {
  padding-bottom: 70px; /* 为底部导航留出空间 */
}
</style> 