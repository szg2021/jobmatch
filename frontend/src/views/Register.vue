<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h1 class="register-title">注册账号</h1>
        <p class="register-subtitle">{{ title }}</p>
      </div>
      
      <el-form
        ref="registerForm"
        :model="formModel"
        :rules="registerRules"
        class="register-form"
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="formModel.email"
            placeholder="请输入邮箱"
            prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="full_name">
          <el-input
            v-model="formModel.full_name"
            placeholder="请输入姓名"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formModel.password"
            placeholder="请输入密码"
            type="password"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="formModel.confirmPassword"
            placeholder="请再次输入密码"
            type="password"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="用户类型" prop="role">
          <el-radio-group v-model="formModel.role">
            <el-radio label="job_seeker">求职者</el-radio>
            <el-radio label="company">企业用户</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="formModel.role === 'company'" label="公司名称" prop="company_name">
          <el-input
            v-model="formModel.company_name"
            placeholder="请输入公司名称"
            prefix-icon="Office-Building"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="register-button"
            :loading="loading"
            @click="submitForm"
          >
            注册
          </el-button>
        </el-form-item>

        <div class="register-footer">
          <span>已有账号?</span>
          <router-link class="login-link" to="/login">立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, FormInstance } from 'element-plus';
import { Message, Lock, User, OfficeBuilding } from '@element-plus/icons-vue';
import { useUserStore } from '@/store/user';

const title = import.meta.env.VITE_APP_TITLE || 'AI招聘推荐平台';
const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const registerForm = ref<FormInstance>();

const formModel = reactive({
  email: '',
  full_name: '',
  password: '',
  confirmPassword: '',
  role: 'job_seeker',
  company_name: ''
});

const validatePass = (rule: any, value: string, callback: Function) => {
  if (value === '') {
    callback(new Error('请输入密码'));
  } else {
    if (formModel.confirmPassword !== '') {
      registerForm.value?.validateField('confirmPassword', () => null);
    }
    callback();
  }
};

const validatePass2 = (rule: any, value: string, callback: Function) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== formModel.password) {
    callback(new Error('两次输入的密码不一致'));
  } else {
    callback();
  }
};

const registerRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在2到50个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户类型', trigger: 'change' }
  ],
  company_name: [
    { 
      required: true, 
      message: '请输入公司名称', 
      trigger: 'blur',
      // 仅当角色为company时验证
      validator: (rule: any, value: string, callback: Function) => {
        if (formModel.role === 'company' && !value) {
          callback(new Error('请输入公司名称'));
        } else {
          callback();
        }
      }
    }
  ]
};

const submitForm = async () => {
  if (!registerForm.value) return;
  
  await registerForm.value.validate(async (valid: boolean, fields?: any) => {
    if (valid) {
      await handleRegister();
    } else {
      showError(fields);
    }
  });
};

const handleRegister = async () => {
  loading.value = true;
  
  try {
    // 准备注册数据
    const userData = {
      email: formModel.email,
      full_name: formModel.full_name,
      password: formModel.password,
      role: formModel.role
    };
    
    // 如果是企业用户，添加公司名称
    if (formModel.role === 'company') {
      Object.assign(userData, { company_name: formModel.company_name });
    }
    
    const success = await userStore.register(userData);
    
    if (success) {
      ElMessage.success('注册成功！请登录您的账号');
      router.push('/login');
    } else {
      ElMessage.error(userStore.error || '注册失败，请稍后再试');
    }
  } catch (error) {
    console.error('注册异常:', error);
    ElMessage.error('系统错误，请稍后再试');
  } finally {
    loading.value = false;
  }
};

const showError = (fields: string[]) => {
  error.value = true;
  errorFields.value = fields;
};
</script>

<style scoped>
.register-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.register-card {
  width: 450px;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 8px 0;
}

.register-subtitle {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.register-form {
  margin-top: 24px;
}

.register-button {
  width: 100%;
  padding: 12px 0;
}

.register-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.login-link {
  color: var(--primary-color);
  text-decoration: none;
  margin-left: 5px;
}
</style> 