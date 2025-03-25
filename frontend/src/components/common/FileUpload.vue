<template>
  <div class="file-upload">
    <el-upload
      class="upload-container"
      drag
      :accept="allowedFileTypes"
      :action="'#'"
      :auto-upload="false"
      :show-file-list="false"
      :on-change="handleChange"
      :before-upload="beforeUpload"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖放文件到此处或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          {{ tip || `请上传${fileTypeText}文件，不超过${maxSize}MB` }}
        </div>
      </template>
    </el-upload>

    <div v-if="file" class="selected-file">
      <el-card shadow="hover">
        <div class="file-info">
          <el-icon class="file-icon"><document /></el-icon>
          <div class="file-details">
            <h4 class="file-name">{{ file.name }}</h4>
            <p class="file-meta">{{ formatFileSize(file.size) }}</p>
          </div>
          <div class="file-actions">
            <el-button type="primary" size="small" @click="submitFile">上传</el-button>
            <el-button type="default" size="small" @click="clearFile">取消</el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { UploadFilled, Document } from '@element-plus/icons-vue';
import { formatFileSize } from '@/utils/helpers';

interface Props {
  allowedTypes?: string[];
  maxSize?: number;
  tip?: string;
}

const props = withDefaults(defineProps<Props>(), {
  allowedTypes: () => ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  maxSize: 10,
  tip: ''
});

const emit = defineEmits<{
  (e: 'upload', file: File): void
}>();

const file = ref<File | null>(null);

const allowedFileTypes = props.allowedTypes.join(',');

const fileTypeText = props.allowedTypes.includes('application/pdf') && 
                    props.allowedTypes.includes('application/vnd.openxmlformats-officedocument.wordprocessingml.document') 
                    ? 'PDF或DOCX' 
                    : props.allowedTypes.includes('application/pdf') 
                      ? 'PDF' 
                      : 'DOCX';

const beforeUpload = (file: File) => {
  // 检查文件类型
  const isAllowedType = props.allowedTypes.includes(file.type);
  if (!isAllowedType) {
    ElMessage.error(`只允许上传${fileTypeText}文件！`);
    return false;
  }
  
  // 检查文件大小
  const isLessThanMaxSize = file.size / 1024 / 1024 < props.maxSize;
  if (!isLessThanMaxSize) {
    ElMessage.error(`文件大小不能超过${props.maxSize}MB！`);
    return false;
  }
  
  return isAllowedType && isLessThanMaxSize;
};

const handleChange = (uploadFile: any) => {
  file.value = uploadFile.raw;
};

const submitFile = () => {
  if (file.value) {
    emit('upload', file.value);
  } else {
    ElMessage.warning('请先选择一个文件！');
  }
};

const clearFile = () => {
  file.value = null;
};
</script>

<style scoped>
.file-upload {
  width: 100%;
}

.upload-container {
  width: 100%;
}

.selected-file {
  margin-top: 20px;
}

.file-info {
  display: flex;
  align-items: center;
}

.file-icon {
  font-size: 24px;
  margin-right: 10px;
  color: var(--primary-color);
}

.file-details {
  flex: 1;
}

.file-name {
  margin: 0;
  font-weight: 500;
  font-size: 16px;
  color: var(--text-color);
  word-break: break-all;
}

.file-meta {
  margin: 5px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.file-actions {
  display: flex;
  gap: 8px;
}
</style> 