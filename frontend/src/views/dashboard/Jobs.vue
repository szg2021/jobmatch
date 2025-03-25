<template>
  <page-content-wrapper className="jobs-container">
    <page-header
      title="职位管理"
      subtitle="管理您的职位发布"
    />
    
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="action-card">
          <el-button type="primary" size="large" @click="showUploadDialog">
            <el-icon><Plus /></el-icon>
            发布新职位
          </el-button>
          
          <div class="filters">
            <search-box
              v-model="searchQuery"
              placeholder="搜索职位"
              @search="fetchJobs"
              style="width: 200px; margin-right: 10px; margin-bottom: 0;"
            />
            
            <el-select
              v-model="activeFilter"
              placeholder="状态筛选"
              style="width: 120px; margin-right: 10px;"
              @change="handleFilterChange"
            >
              <el-option label="全部" value="" />
              <el-option label="已发布" value="true" />
              <el-option label="已下线" value="false" />
            </el-select>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" v-loading="loadingState.isLoading">
      <el-col :span="24">
        <el-card v-if="jobs.length === 0 && !loadingState.isLoading" shadow="hover" class="empty-card">
          <el-empty description="您还没有发布任何职位">
            <el-button type="primary" @click="showUploadDialog">发布第一个职位</el-button>
          </el-empty>
        </el-card>
        
        <div v-else>
          <el-card 
            v-for="job in jobs" 
            :key="job.job_id" 
            shadow="hover" 
            class="job-card"
            :class="{'job-inactive': !job.is_active}"
          >
            <div class="job-header">
              <h3 class="job-title">{{ job.title }}</h3>
              <status-tag 
                :status="job.is_active ? 'success' : 'info'" 
                :text="job.is_active ? '已发布' : '已下线'" 
              />
            </div>
            
            <div class="job-info">
              <div class="job-details">
                <span class="job-location">
                  <el-icon><Location /></el-icon>
                  {{ job.location }}
                </span>
                <span class="job-type">
                  <el-icon><Briefcase /></el-icon>
                  {{ job.job_type }}
                </span>
                <span class="job-salary" v-if="job.salary_range">
                  <el-icon><Money /></el-icon>
                  {{ job.salary_range }}
                </span>
                <span class="job-date">
                  <el-icon><Calendar /></el-icon>
                  {{ formatDate(job.created_at) }}
                </span>
              </div>
              
              <div class="job-actions">
                <el-button 
                  type="primary" 
                  plain 
                  @click="viewJobDetails(job)"
                >
                  查看详情
                </el-button>
                <el-button 
                  type="info" 
                  plain 
                  @click="editJob(job)"
                >
                  编辑
                </el-button>
                <el-button 
                  :type="job.is_active ? 'warning' : 'success'" 
                  plain 
                  @click="toggleJobStatus(job)"
                >
                  {{ job.is_active ? '下线' : '重新发布' }}
                </el-button>
                <el-button 
                  type="danger" 
                  plain 
                  @click="confirmDeleteJob(job)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
    
    <!-- 职位详情对话框 -->
    <el-dialog
      v-model="jobDetailsVisible"
      title="职位详情"
      width="800px"
      destroy-on-close
    >
      <div v-if="selectedJob">
        <h2>{{ selectedJob.title }}</h2>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="公司名称" :span="2">
            {{ selectedJob.company_name }}
          </el-descriptions-item>
          <el-descriptions-item label="工作地点">
            {{ selectedJob.location }}
          </el-descriptions-item>
          <el-descriptions-item label="工作类型">
            {{ selectedJob.job_type }}
          </el-descriptions-item>
          <el-descriptions-item label="薪资范围" :span="2">
            {{ selectedJob.salary_range || '未提供' }}
          </el-descriptions-item>
          <el-descriptions-item label="发布时间">
            {{ formatDate(selectedJob.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <status-tag 
              :status="selectedJob.is_active ? 'success' : 'info'" 
              :text="selectedJob.is_active ? '已发布' : '已下线'" 
            />
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="job-detail-section">
          <h3>职位要求</h3>
          <div class="requirements">
            <status-tag
              v-for="requirement in selectedJob.requirements"
              :key="requirement"
              :text="requirement"
              effect="light"
              className="requirement-tag"
            />
            <div v-if="!selectedJob.requirements || selectedJob.requirements.length === 0">
              未提供具体要求
            </div>
          </div>
        </div>
        
        <div class="job-detail-section">
          <h3>职位描述</h3>
          <pre class="job-content">{{ selectedJob.content }}</pre>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="jobDetailsVisible = false">关闭</el-button>
        <el-button 
          :type="selectedJob?.is_active ? 'warning' : 'success'" 
          @click="toggleJobStatus(selectedJob)"
        >
          {{ selectedJob?.is_active ? '下线职位' : '重新发布' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 上传职位对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="发布新职位"
      width="800px"
      destroy-on-close
    >
      <el-form
        ref="jobFormRef"
        :model="jobForm"
        :rules="jobRules"
        label-width="100px"
      >
        <el-form-item label="职位名称" prop="title">
          <el-input v-model="jobForm.title" placeholder="请输入职位名称" />
        </el-form-item>
        
        <el-form-item label="工作地点" prop="location">
          <el-input v-model="jobForm.location" placeholder="请输入工作地点" />
        </el-form-item>
        
        <el-form-item label="职位类型" prop="job_type">
          <el-select v-model="jobForm.job_type" placeholder="请选择职位类型" style="width: 100%;">
            <el-option label="全职" value="全职" />
            <el-option label="兼职" value="兼职" />
            <el-option label="实习" value="实习" />
            <el-option label="自由职业" value="自由职业" />
            <el-option label="远程" value="远程" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="薪资范围" prop="salary_range">
          <el-input v-model="jobForm.salary_range" placeholder="例如: 15k-25k/月" />
        </el-form-item>
        
        <el-form-item label="职位描述" prop="content">
          <el-input
            v-model="jobForm.content"
            type="textarea"
            :rows="6"
            placeholder="请详细描述职位的职责、要求等信息"
          />
        </el-form-item>
        
        <el-form-item label="职位要求">
          <status-tag
            v-for="(requirement, index) in jobForm.requirements"
            :key="index"
            :text="requirement"
            status="info"
            effect="light"
            className="requirement-tag"
            closable
            @close="removeRequirement(index)"
          />
          
          <el-input
            v-if="inputVisible"
            ref="requirementInput"
            v-model="requirementInputValue"
            class="tag-input"
            size="small"
            @keyup.enter="handleRequirementInputConfirm"
            @blur="handleRequirementInputConfirm"
          />
          
          <el-button
            v-else
            class="button-new-tag"
            size="small"
            @click="showRequirementInput"
          >
            + 添加要求
          </el-button>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="jobForm.is_active"
            active-text="发布"
            inactive-text="暂不发布"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitJobForm" :loading="loadingState.isLoading">
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 确认删除职位对话框 -->
    <el-dialog
      v-model="deleteConfirmVisible"
      title="确认删除"
      width="400px"
    >
      <p>确定要删除职位 "{{ selectedJob?.title }}" 吗？此操作不可恢复。</p>
      <template #footer>
        <el-button @click="deleteConfirmVisible = false">取消</el-button>
        <el-button type="danger" @click="deleteJob" :loading="loadingState.isLoading">
          确认删除
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑职位对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑职位"
      width="800px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="jobRules"
        label-width="100px"
      >
        <el-form-item label="职位名称" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入职位名称" />
        </el-form-item>
        
        <el-form-item label="工作地点" prop="location">
          <el-input v-model="editForm.location" placeholder="请输入工作地点" />
        </el-form-item>
        
        <el-form-item label="职位类型" prop="job_type">
          <el-select v-model="editForm.job_type" placeholder="请选择职位类型" style="width: 100%;">
            <el-option label="全职" value="全职" />
            <el-option label="兼职" value="兼职" />
            <el-option label="实习" value="实习" />
            <el-option label="自由职业" value="自由职业" />
            <el-option label="远程" value="远程" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="薪资范围" prop="salary_range">
          <el-input v-model="editForm.salary_range" placeholder="例如: 15k-25k/月" />
        </el-form-item>
        
        <el-form-item label="职位描述" prop="content">
          <el-input
            v-model="editForm.content"
            type="textarea"
            :rows="6"
            placeholder="请详细描述职位的职责、要求等信息"
          />
        </el-form-item>
        
        <el-form-item label="职位要求">
          <status-tag
            v-for="(requirement, index) in editForm.requirements"
            :key="index"
            :text="requirement"
            status="info"
            effect="light"
            className="requirement-tag"
            closable
            @close="removeEditRequirement(index)"
          />
          
          <el-input
            v-if="editInputVisible"
            ref="editRequirementInput"
            v-model="editRequirementInputValue"
            class="tag-input"
            size="small"
            @keyup.enter="handleEditRequirementInputConfirm"
            @blur="handleEditRequirementInputConfirm"
          />
          
          <el-button
            v-else
            class="button-new-tag"
            size="small"
            @click="showEditRequirementInput"
          >
            + 添加要求
          </el-button>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="editForm.is_active"
            active-text="发布"
            inactive-text="暂不发布"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEditForm" :loading="loadingState.isLoading">
          保存
        </el-button>
      </template>
    </el-dialog>
  </page-content-wrapper>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import { ElMessage, FormInstance, ElMessageBox } from 'element-plus';
import { Plus, Location, Money, Briefcase, Calendar, Search } from '@element-plus/icons-vue';
import { useUserStore } from '@/store/user';
import PageHeader from '@/components/common/PageHeader.vue';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
import SearchBox from '@/components/common/SearchBox.vue';
import StatusTag from '@/components/common/StatusTag.vue';
import api from '@/utils/api';
import { formatDate } from '@/utils/helpers';
import { Job } from '@/types';
import { useLoading } from '@/utils/loadingState';

const userStore = useUserStore();
const loadingState = useLoading();
const jobs = ref<Job[]>([]);

// 筛选和搜索
const searchQuery = ref('');
const activeFilter = ref('');

// 对话框状态
const uploadDialogVisible = ref(false);
const jobDetailsVisible = ref(false);
const deleteConfirmVisible = ref(false);
const editDialogVisible = ref(false);

// 选中的职位
const selectedJob = ref<Job | null>(null);

// 表单相关
const jobForm = reactive({
  title: '',
  location: '',
  job_type: '',
  salary_range: '',
  content: '',
  requirements: [] as string[],
  is_active: true
});

const jobRules = {
  title: [
    { required: true, message: '请输入职位名称', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入工作地点', trigger: 'blur' }
  ],
  job_type: [
    { required: true, message: '请选择职位类型', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入职位描述', trigger: 'blur' }
  ]
};

const jobFormRef = ref<FormInstance>();

// 添加职位要求相关
const inputVisible = ref(false);
const requirementInputValue = ref('');
const requirementInput = ref();

// 编辑职位相关
const editFormRef = ref<FormInstance>();
const editForm = reactive({
  job_id: '',
  title: '',
  location: '',
  job_type: '',
  salary_range: '',
  content: '',
  requirements: [] as string[],
  is_active: true
});

// 编辑职位要求相关
const editInputVisible = ref(false);
const editRequirementInputValue = ref('');
const editRequirementInput = ref();

// 初始化
onMounted(() => {
  fetchJobs();
});

// 获取职位列表
const fetchJobs = async () => {
  await loadingState.withLoading(async () => {
    try {
      // 构建查询参数
      const params: Record<string, string> = {};
      if (activeFilter.value) {
        params.is_active = activeFilter.value;
      }
      if (searchQuery.value) {
        params.search = searchQuery.value;
      }
      
      const response = await api.get('/jobs', { params });
      jobs.value = response.data || [];
    } catch (error) {
      console.error('获取职位列表失败:', error);
      ElMessage.error('获取职位列表失败，请稍后重试');
    }
  });
};

// 搜索处理
const handleSearch = () => {
  fetchJobs();
};

// 筛选处理
const handleFilterChange = () => {
  fetchJobs();
};

// 打开发布职位对话框
const showUploadDialog = () => {
  // 重置表单
  Object.assign(jobForm, {
    title: '',
    location: '',
    job_type: '',
    salary_range: '',
    content: '',
    requirements: [],
    is_active: true
  });
  
  uploadDialogVisible.value = true;
};

// 提交职位表单
const submitJobForm = async () => {
  if (!jobFormRef.value) return;
  
  await jobFormRef.value.validate(async (valid) => {
    if (valid) {
      await loadingState.withLoading(async () => {
        try {
          // 准备提交数据
          const jobData = {
            title: jobForm.title,
            location: jobForm.location,
            job_type: jobForm.job_type,
            salary_range: jobForm.salary_range,
            content: jobForm.content,
            requirements: jobForm.requirements,
            is_active: jobForm.is_active
          };
          
          const response = await api.post('/jobs', jobData);
          
          ElMessage.success('职位发布成功');
          uploadDialogVisible.value = false;
          
          // 刷新职位列表
          fetchJobs();
        } catch (error: any) {
          console.error('职位发布失败:', error);
          ElMessage.error(error.response?.data?.detail || '职位发布失败，请稍后重试');
        }
      });
    }
  });
};

// 查看职位详情
const viewJobDetails = (job: Job) => {
  selectedJob.value = job;
  jobDetailsVisible.value = true;
};

// 切换职位状态（上线/下线）
const toggleJobStatus = async (job: Job | null) => {
  if (!job) return;
  
  await loadingState.withLoading(async () => {
    try {
      await api.put(`/jobs/${job.job_id}/toggle-active`);
      
      // 更新本地数据
      const jobIndex = jobs.value.findIndex(j => j.job_id === job.job_id);
      if (jobIndex !== -1) {
        const updatedJob = { ...jobs.value[jobIndex], is_active: !jobs.value[jobIndex].is_active };
        jobs.value.splice(jobIndex, 1, updatedJob);
        
        // 如果正在查看详情，也更新详情中的数据
        if (selectedJob.value && selectedJob.value.job_id === job.job_id) {
          selectedJob.value = updatedJob;
        }
      }
      
      ElMessage.success(job.is_active ? '职位已下线' : '职位已重新发布');
      
      // 如果在详情对话框中操作，则关闭对话框
      if (jobDetailsVisible.value) {
        jobDetailsVisible.value = false;
      }
    } catch (error: any) {
      console.error('更新职位状态失败:', error);
      ElMessage.error(error.response?.data?.detail || '操作失败，请稍后重试');
    }
  });
};

// 确认删除职位
const confirmDeleteJob = (job: Job) => {
  selectedJob.value = job;
  deleteConfirmVisible.value = true;
};

// 删除职位
const deleteJob = async () => {
  if (!selectedJob.value) return;
  
  await loadingState.withLoading(async () => {
    try {
      await api.delete(`/jobs/${selectedJob.value.job_id}`);
      
      ElMessage.success('职位已删除');
      deleteConfirmVisible.value = false;
      
      // 从列表中移除
      jobs.value = jobs.value.filter(job => job.job_id !== selectedJob.value?.job_id);
      
      // 如果在详情对话框中删除，则关闭详情对话框
      if (jobDetailsVisible.value) {
        jobDetailsVisible.value = false;
      }
    } catch (error: any) {
      console.error('删除职位失败:', error);
      ElMessage.error(error.response?.data?.detail || '删除失败，请稍后重试');
    }
  });
};

// 处理添加职位要求的输入框显示
const showRequirementInput = () => {
  inputVisible.value = true;
  nextTick(() => {
    requirementInput.value.focus();
  });
};

// 处理添加职位要求
const handleRequirementInputConfirm = () => {
  if (requirementInputValue.value.trim()) {
    jobForm.requirements.push(requirementInputValue.value.trim());
  }
  inputVisible.value = false;
  requirementInputValue.value = '';
};

// 删除职位要求
const removeRequirement = (index: number) => {
  jobForm.requirements.splice(index, 1);
};

// 打开编辑职位对话框
const editJob = (job: Job) => {
  // 填充编辑表单
  Object.assign(editForm, {
    job_id: job.job_id,
    title: job.title,
    location: job.location,
    job_type: job.job_type,
    salary_range: job.salary_range || '',
    content: job.content,
    requirements: job.requirements ? [...job.requirements] : [],
    is_active: job.is_active
  });
  
  editDialogVisible.value = true;
};

// 提交编辑表单
const submitEditForm = async () => {
  if (!editFormRef.value) return;
  
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      await loadingState.withLoading(async () => {
        try {
          // 准备提交数据
          const jobData = {
            title: editForm.title,
            location: editForm.location,
            job_type: editForm.job_type,
            salary_range: editForm.salary_range,
            content: editForm.content,
            requirements: editForm.requirements,
            is_active: editForm.is_active
          };
          
          const response = await api.put(`/jobs/${editForm.job_id}`, jobData);
          
          ElMessage.success('职位更新成功');
          editDialogVisible.value = false;
          
          // 更新本地数据
          const jobIndex = jobs.value.findIndex(j => j.job_id === editForm.job_id);
          if (jobIndex !== -1) {
            jobs.value.splice(jobIndex, 1, response.data);
            
            // 如果正在查看详情，也更新详情中的数据
            if (selectedJob.value && selectedJob.value.job_id === editForm.job_id) {
              selectedJob.value = response.data;
            }
          }
        } catch (error: any) {
          console.error('职位更新失败:', error);
          ElMessage.error(error.response?.data?.detail || '职位更新失败，请稍后重试');
        }
      });
    }
  });
};

// 处理添加编辑职位要求的输入框显示
const showEditRequirementInput = () => {
  editInputVisible.value = true;
  nextTick(() => {
    editRequirementInput.value.focus();
  });
};

// 处理添加编辑职位要求
const handleEditRequirementInputConfirm = () => {
  if (editRequirementInputValue.value.trim()) {
    editForm.requirements.push(editRequirementInputValue.value.trim());
  }
  editInputVisible.value = false;
  editRequirementInputValue.value = '';
};

// 删除编辑职位要求
const removeEditRequirement = (index: number) => {
  editForm.requirements.splice(index, 1);
};
</script>

<style scoped>
.jobs-container {
  max-width: 1200px;
  margin: 0 auto;
}

.action-card {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  align-items: center;
}

.job-card {
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.job-inactive {
  opacity: 0.7;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.job-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.job-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.job-details {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.job-location,
.job-type,
.job-salary,
.job-date {
  display: flex;
  align-items: center;
  color: #606266;
  font-size: 14px;
}

.job-location .el-icon,
.job-type .el-icon,
.job-salary .el-icon,
.job-date .el-icon {
  margin-right: 5px;
}

.job-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

@media (max-width: 768px) {
  .job-info {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .job-actions {
    margin-top: 15px;
    width: 100%;
    justify-content: flex-end;
  }
}

.job-detail-section {
  margin-top: 20px;
}

.job-detail-section h3 {
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: 500;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.requirements {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.requirement-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.job-content {
  white-space: pre-wrap;
  font-family: inherit;
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.tag-input {
  width: 100px;
  margin-right: 10px;
  vertical-align: bottom;
}

.button-new-tag {
  margin-left: 10px;
  height: 32px;
  line-height: 30px;
  padding-top: 0;
  padding-bottom: 0;
}
</style> 