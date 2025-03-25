<template>
  <div 
    :class="['default-image', className]" 
    :style="[
      { width: width + 'px', height: height + 'px', backgroundColor: bgColor },
      customStyle
    ]"
  >
    <el-icon v-if="icon" :size="iconSize" :color="iconColor"><component :is="icon" /></el-icon>
    <span v-else-if="text" class="text" :style="{ color: textColor, fontSize: textSize + 'px' }">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  width?: number;
  height?: number;
  icon?: string;
  iconSize?: number;
  iconColor?: string;
  text?: string;
  textSize?: number;
  textColor?: string;
  bgColor?: string;
  className?: string;
  customStyle?: Record<string, string>;
}

const props = withDefaults(defineProps<Props>(), {
  width: 100,
  height: 100,
  iconSize: 30,
  iconColor: '#909399',
  textSize: 14,
  textColor: '#909399',
  bgColor: '#f5f7fa',
  className: '',
  customStyle: () => ({})
});
</script>

<style scoped>
.default-image {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  overflow: hidden;
}

.text {
  text-align: center;
  padding: 0 10px;
  word-break: break-word;
}
</style> 