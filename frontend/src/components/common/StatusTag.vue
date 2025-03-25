<template>
  <el-tag
    :type="tagType"
    :effect="effect"
    :size="size"
    :class="['status-tag', className]"
  >
    <el-icon v-if="icon"><component :is="icon" /></el-icon>
    <slot>{{ text }}</slot>
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type StatusType = 'success' | 'warning' | 'info' | 'error' | 'default';
type TagEffect = 'dark' | 'light' | 'plain';
type TagSize = 'large' | 'default' | 'small';

interface Props {
  status?: StatusType;
  text?: string;
  icon?: string;
  effect?: TagEffect;
  size?: TagSize;
  className?: string;
}

const props = withDefaults(defineProps<Props>(), {
  status: 'default',
  text: '',
  effect: 'light',
  size: 'small',
  className: ''
});

// 根据状态类型返回对应的Element Plus标签类型
const tagType = computed(() => {
  switch (props.status) {
    case 'success':
      return 'success';
    case 'warning':
      return 'warning';
    case 'info':
      return 'info';
    case 'error':
      return 'danger';
    default:
      return ''; // Element Plus中默认标签没有type
  }
});
</script>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  line-height: 1;
}

.status-tag .el-icon {
  margin-right: 4px;
  font-size: 14px;
}
</style> 