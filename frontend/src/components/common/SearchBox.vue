<template>
  <div class="search-box">
    <el-input
      v-model="inputValue"
      :placeholder="placeholder"
      prefix-icon="Search"
      clearable
      @input="handleInput"
      @keyup.enter="handleSearch"
    >
      <template #append v-if="showSearchButton">
        <el-button :icon="Search" @click="handleSearch">搜索</el-button>
      </template>
    </el-input>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { Search } from '@element-plus/icons-vue';

interface Props {
  placeholder?: string;
  delay?: number;
  showSearchButton?: boolean;
  modelValue?: string;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入搜索关键词',
  delay: 300,
  showSearchButton: false,
  modelValue: ''
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'search', value: string): void;
  (e: 'input', value: string): void;
}>();

// 内部输入值
const inputValue = ref(props.modelValue);

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  inputValue.value = newVal;
});

// 更新输入值并发出input事件
const handleInput = () => {
  emit('update:modelValue', inputValue.value);
  emit('input', inputValue.value);
};

// 立即触发搜索
const handleSearch = () => {
  emit('search', inputValue.value);
};
</script>

<style scoped>
.search-box {
  margin-bottom: 16px;
}
</style> 