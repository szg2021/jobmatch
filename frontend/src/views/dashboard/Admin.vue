<template>
  <PageContentWrapper className="admin-container">
    <page-header
      title="管理控制台"
      subtitle="系统管理员控制面板"
    />
    
    <el-row :gutter="16" v-loading="loadingState.isLoading">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.users }}</div>
          <div class="stat-label">注册用户</div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.resumes }}</div>
          <div class="stat-label">上传简历</div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.jobs }}</div>
          <div class="stat-label">发布职位</div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card shadow="hover" class="feature-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="用户管理" name="users">
          <el-result
            icon="info"
            title="功能开发中"
            sub-title="用户管理功能即将上线，敬请期待"
          />
        </el-tab-pane>
        
        <el-tab-pane label="简历管理" name="resumes">
          <el-result
            icon="info"
            title="功能开发中"
            sub-title="简历管理功能即将上线，敬请期待"
          />
        </el-tab-pane>
        
        <el-tab-pane label="职位管理" name="jobs">
          <el-result
            icon="info"
            title="功能开发中"
            sub-title="职位管理功能即将上线，敬请期待"
          />
        </el-tab-pane>
        
        <el-tab-pane label="系统设置" name="settings">
          <el-result
            icon="info"
            title="功能开发中"
            sub-title="系统设置功能即将上线，敬请期待"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </PageContentWrapper>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue';
import PageHeader from '@/components/common/PageHeader.vue';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
import { ElMessage } from 'element-plus';
import { useLoading } from '@/utils/loadingState';
import api from '@/utils/api';

const activeTab = ref('users');
const loadingState = useLoading();

const stats = reactive({
  users: 0,
  resumes: 0,
  jobs: 0
});

onMounted(async () => {
  // 这里模拟加载管理员统计数据
  // 实际项目中应该从API获取
  try {
    await loadingState.withLoading(async () => {
      // 模拟数据，实际项目应该替换为API调用
      stats.users = 24;
      stats.resumes = 18;
      stats.jobs = 36;
      
      // 示例API调用（暂时注释掉）
      // const response = await api.get('/admin/stats');
      // Object.assign(stats, response.data);
    });
  } catch (error) {
    console.error('加载管理员统计数据失败:', error);
    ElMessage.error('加载管理员统计数据失败');
  }
});
</script>

<style scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  text-align: center;
  padding: 20px;
  margin-bottom: 20px;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: var(--primary-color);
}

.stat-label {
  font-size: 16px;
  color: #909399;
  margin-top: 8px;
}

.feature-card {
  margin-top: 20px;
}
</style> 