<template>
  <div class="match-score">
    <el-progress
      type="dashboard"
      :percentage="percentage"
      :color="scoreColor"
      :stroke-width="9"
      :width="size"
      :show-text="false"
    >
      <template #default>
        <div class="score-value">{{ score }}</div>
        <div v-if="label" class="score-label">{{ label }}</div>
      </template>
    </el-progress>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import { formatMatchScore } from '@/utils/helpers';

interface Props {
  value: number;
  size?: number;
  label?: string;
}

const props = withDefaults(defineProps<Props>(), {
  size: 80,
  label: '匹配度'
});

const percentage = computed(() => Math.round(props.value * 100));
const score = computed(() => formatMatchScore(props.value));

const scoreColor = computed(() => {
  const value = props.value;
  
  if (value >= 0.8) {
    return '#67C23A';  // 绿色，匹配度很高
  } else if (value >= 0.6) {
    return '#409EFF';  // 蓝色，匹配度较高
  } else if (value >= 0.4) {
    return '#E6A23C';  // 黄色，匹配度一般
  } else {
    return '#F56C6C';  // 红色，匹配度较低
  }
});
</script>

<style scoped>
.match-score {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.score-value {
  font-size: 16px;
  font-weight: bold;
  line-height: 1;
}

.score-label {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style> 