<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    :width="width"
    :destroy-on-close="destroyOnClose"
    @closed="onClosed"
  >
    <div class="confirm-content">
      <div v-if="icon" class="icon-container">
        <el-icon :size="48" :color="iconColor">
          <component :is="icon" />
        </el-icon>
      </div>
      
      <div class="message-container">
        <slot>
          <p v-if="typeof message === 'string'" v-html="message"></p>
          <template v-else>{{ message }}</template>
        </slot>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <slot name="footer">
          <el-button @click="cancel">{{ cancelButtonText }}</el-button>
          <el-button
            :type="confirmButtonType"
            :loading="loading"
            @click="confirm"
          >
            {{ confirmButtonText }}
          </el-button>
        </slot>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import { WarningFilled, InfoFilled, CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue';

type MessageType = 'success' | 'warning' | 'info' | 'error';

interface Props {
  modelValue?: boolean;
  title?: string;
  message?: string | object;
  type?: MessageType;
  width?: string;
  confirmButtonText?: string;
  cancelButtonText?: string;
  confirmButtonType?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  destroyOnClose?: boolean;
  loading?: boolean;
  showIcon?: boolean;
}

// 组件属性
const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  title: '确认',
  message: '确定要执行此操作吗？',
  type: 'warning',
  width: '400px',
  confirmButtonText: '确定',
  cancelButtonText: '取消',
  confirmButtonType: 'primary',
  destroyOnClose: true,
  loading: false,
  showIcon: true
});

// 组件事件
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'confirm'): void;
  (e: 'cancel'): void;
  (e: 'closed'): void;
}>();

// 对话框可见状态
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

// 根据类型获取图标
const icon = computed(() => {
  if (!props.showIcon) return null;
  
  switch (props.type) {
    case 'success':
      return CircleCheckFilled;
    case 'warning':
      return WarningFilled;
    case 'error':
      return CircleCloseFilled;
    case 'info':
    default:
      return InfoFilled;
  }
});

// 图标颜色
const iconColor = computed(() => {
  switch (props.type) {
    case 'success':
      return '#67C23A';
    case 'warning':
      return '#E6A23C';
    case 'error':
      return '#F56C6C';
    case 'info':
    default:
      return '#909399';
  }
});

// 确认按钮
const confirm = () => {
  emit('confirm');
};

// 取消按钮
const cancel = () => {
  emit('cancel');
  dialogVisible.value = false;
};

// 对话框关闭回调
const onClosed = () => {
  emit('closed');
};
</script>

<style scoped>
.confirm-content {
  display: flex;
  align-items: flex-start;
  padding: 10px 0;
}

.icon-container {
  margin-right: 20px;
  margin-top: 2px;
}

.message-container {
  flex: 1;
}

.message-container p {
  margin: 0;
  line-height: 1.6;
}

.dialog-footer {
  text-align: right;
}
</style> 