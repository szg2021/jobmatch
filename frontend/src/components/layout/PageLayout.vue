<template>
  <div class="page-layout">
    <div class="page-header">
      <slot name="header"></slot>
    </div>
    <div class="page-content">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="page-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
// 页面布局组件
</script>

<style scoped>
.page-layout {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  background-color: #fff;
}

.page-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.page-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background-color: #fff;
}
</style> 