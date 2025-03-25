<template>
  <PageContentWrapper className="profile-container">
    <page-header
      title="个人资料"
      subtitle="查看和更新您的个人信息"
    />
    
    <el-card shadow="hover" class="profile-card">
      <template #header>
        <div class="card-header">
          <h3>基本信息</h3>
        </div>
      </template>
      
      <el-form
        ref="profileForm"
        :model="formModel"
        :rules="formRules"
        label-width="100px"
        v-loading="loadingState.isLoading"
      >
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="用户ID" prop="id">
              <el-input v-model="formModel.id" disabled />
            </el-form-item>
          </el-col>
          
          <el-col :xs="24" :sm="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="formModel.email" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="姓名" prop="full_name">
              <el-input v-model="formModel.full_name" />
            </el-form-item>
          </el-col>
          
          <el-col :xs="24" :sm="12">
            <el-form-item label="用户类型" prop="role">
              <el-tag
                :type="roleTagType"
                size="large"
                class="role-tag"
              >
                {{ roleText }}
              </el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" v-if="isCompanyUser">
          <el-col :xs="24" :sm="12">
            <el-form-item label="公司名称" prop="company_name">
              <el-input v-model="formModel.company_name" />
            </el-form-item>
          </el-col>
          
          <el-col :xs="24" :sm="12">
            <el-form-item label="公司规模" prop="company_size">
              <el-select v-model="formModel.company_size" placeholder="请选择公司规模" style="width: 100%;">
                <el-option label="1-10人" value="1-10" />
                <el-option label="11-50人" value="11-50" />
                <el-option label="51-200人" value="51-200" />
                <el-option label="201-500人" value="201-500" />
                <el-option label="501-1000人" value="501-1000" />
                <el-option label="1000人以上" value="1000+" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" v-if="isCompanyUser">
          <el-col :span="24">
            <el-form-item label="公司介绍" prop="company_description">
              <el-input
                type="textarea"
                v-model="formModel.company_description"
                :rows="3"
                placeholder="请输入公司介绍"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" v-if="!isCompanyUser">
          <el-col :xs="24" :sm="12">
            <el-form-item label="求职状态" prop="job_status">
              <el-select v-model="formModel.job_status" placeholder="请选择求职状态" style="width: 100%;">
                <el-option label="在职找工作" value="employed_seeking" />
                <el-option label="离职找工作" value="unemployed_seeking" />
                <el-option label="在职不找工作" value="employed_not_seeking" />
                <el-option label="应届毕业生" value="fresh_graduate" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :xs="24" :sm="12">
            <el-form-item label="期望城市" prop="preferred_location">
              <el-input v-model="formModel.preferred_location" placeholder="请输入期望工作城市" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="电话号码" prop="phone">
              <el-input v-model="formModel.phone" placeholder="请输入电话号码" />
            </el-form-item>
          </el-col>
          
          <el-col :xs="24" :sm="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="formModel.gender">
                <el-radio label="male">男</el-radio>
                <el-radio label="female">女</el-radio>
                <el-radio label="other">其他</el-radio>
                <el-radio label="prefer_not_to_say">不指定</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button type="primary" @click="updateProfile" :loading="updateLoading">
            保存修改
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card shadow="hover" class="profile-card">
      <template #header>
        <div class="card-header">
          <h3>更改密码</h3>
        </div>
      </template>
      
      <el-form
        ref="passwordForm"
        :model="passwordModel"
        :rules="passwordRules"
        label-width="100px"
        v-loading="passwordLoading"
      >
        <el-form-item label="当前密码" prop="current_password">
          <el-input
            v-model="passwordModel.current_password"
            type="password"
            show-password
            placeholder="请输入当前密码"
          />
        </el-form-item>
        
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordModel.new_password"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordModel.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="updatePassword" :loading="passwordLoading">
            更改密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="profile-card">
      <template #header>
        <div class="card-header">
          <h3>通知设置</h3>
        </div>
      </template>
      
      <el-form
        ref="notificationForm"
        :model="notificationSettings"
        label-width="200px"
      >
        <el-form-item label="职位推荐通知">
          <el-switch v-model="notificationSettings.jobRecommendations" />
        </el-form-item>
        
        <el-form-item label="应用状态更新通知">
          <el-switch v-model="notificationSettings.applicationUpdates" />
        </el-form-item>
        
        <el-form-item label="系统公告通知">
          <el-switch v-model="notificationSettings.systemAnnouncements" />
        </el-form-item>
        
        <el-form-item label="每周职位摘要邮件">
          <el-switch v-model="notificationSettings.weeklyJobDigest" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveNotificationSettings" :loading="notificationLoading">
            保存设置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </PageContentWrapper>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElForm } from 'element-plus';
import { useUserStore } from '@/store/user';
import PageHeader from '@/components/common/PageHeader.vue';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
import api from '@/utils/api';
import { useLoading } from '@/utils/loadingState';

const userStore = useUserStore();
const loadingState = useLoading();
const updateLoading = ref(false);
const passwordLoading = ref(false);
const notificationLoading = ref(false);
const profileForm = ref<InstanceType<typeof ElForm>>();
const passwordForm = ref<InstanceType<typeof ElForm>>();
const notificationForm = ref<InstanceType<typeof ElForm>>();

const formModel = reactive({
  id: '',
  email: '',
  full_name: '',
  role: '',
  company_name: '',
  company_size: '',
  company_description: '',
  job_status: '',
  preferred_location: '',
  phone: '',
  gender: 'prefer_not_to_say'
});

const passwordModel = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
});

const notificationSettings = reactive({
  jobRecommendations: true,
  applicationUpdates: true,
  systemAnnouncements: true,
  weeklyJobDigest: false
});

const formRules = {
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在2到50个字符之间', trigger: 'blur' }
  ],
  company_name: [
    { required: true, message: '请输入公司名称', trigger: 'blur' }
  ]
};

const validatePass = (rule: any, value: string, callback: Function) => {
  if (value === '') {
    callback(new Error('请输入新密码'));
  } else {
    if (passwordModel.confirm_password !== '') {
      passwordForm.value?.validateField('confirm_password', () => null);
    }
    callback();
  }
};

const validatePass2 = (rule: any, value: string, callback: Function) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'));
  } else if (value !== passwordModel.new_password) {
    callback(new Error('两次输入的密码不一致'));
  } else {
    callback();
  }
};

const passwordRules = {
  current_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
};

const isCompanyUser = computed(() => {
  return formModel.role === 'company';
});

const roleText = computed(() => {
  switch (formModel.role) {
    case 'admin':
      return '管理员';
    case 'job_seeker':
      return '求职者';
    case 'company':
      return '企业用户';
    default:
      return '未知角色';
  }
});

const roleTagType = computed(() => {
  switch (formModel.role) {
    case 'admin':
      return 'danger';
    case 'job_seeker':
      return 'success';
    case 'company':
      return 'primary';
    default:
      return 'info';
  }
});

onMounted(async () => {
  await fetchUserProfile();
});

const fetchUserProfile = async () => {
  try {
    await loadingState.withLoading(async () => {
      if (userStore.user.id) {
        // 如果store中已经有数据，直接使用
        Object.assign(formModel, userStore.user);
      } else {
        // 否则重新获取
        await userStore.fetchUserInfo();
        Object.assign(formModel, userStore.user);
      }
    });
  } catch (error) {
    console.error('获取用户信息失败:', error);
    ElMessage.error('获取用户信息失败，请刷新页面重试');
  }
};

const updateProfile = async () => {
  if (!profileForm.value) return;
  
  await profileForm.value.validate(async (valid) => {
    if (valid) {
      updateLoading.value = true;
      
      try {
        await loadingState.withLoading(async () => {
          const updateData = {
            full_name: formModel.full_name
          };
          
          if (isCompanyUser.value) {
            Object.assign(updateData, { company_name: formModel.company_name });
          }
          
          const response = await api.put(`/users/${formModel.id}`, updateData);
          
          // 更新store中的用户信息
          Object.assign(userStore.user, response.data);
          
          ElMessage.success('个人资料更新成功');
        });
      } catch (error: any) {
        console.error('更新个人资料失败:', error);
        ElMessage.error(error.response?.data?.detail || '更新个人资料失败，请稍后重试');
      } finally {
        updateLoading.value = false;
      }
    }
  });
};

const updatePassword = async () => {
  if (!passwordForm.value) return;
  
  await passwordForm.value.validate(async (valid) => {
    if (valid) {
      passwordLoading.value = true;
      
      try {
        await api.put(`/users/me/password`, {
          current_password: passwordModel.current_password,
          new_password: passwordModel.new_password
        });
        
        ElMessage.success('密码修改成功');
        
        // 清空表单
        passwordModel.current_password = '';
        passwordModel.new_password = '';
        passwordModel.confirm_password = '';
        
        passwordForm.value?.resetFields();
      } catch (error: any) {
        console.error('修改密码失败:', error);
        ElMessage.error(error.response?.data?.detail || '修改密码失败，请检查当前密码是否正确');
      } finally {
        passwordLoading.value = false;
      }
    }
  });
};

const saveNotificationSettings = async () => {
  notificationLoading.value = true;
  
  try {
    await loadingState.withLoading(async () => {
      // 这里调用API保存通知设置
      await api.put(`/users/${formModel.id}/notification-settings`, notificationSettings);
      
      ElMessage.success('通知设置已更新');
    });
  } catch (error: any) {
    console.error('更新通知设置失败:', error);
    ElMessage.error(error.response?.data?.detail || '更新通知设置失败，请稍后重试');
  } finally {
    notificationLoading.value = false;
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 900px;
  margin: 0 auto;
}

.profile-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.role-tag {
  font-size: 14px;
  padding: 5px 10px;
}
</style> 