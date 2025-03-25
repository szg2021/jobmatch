<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="login-title">{{ title }}</h1>
        <p class="login-subtitle">智能招聘推荐平台</p>
      </div>
      
      <el-form
        ref="loginForm"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="email">
          <el-input
            v-model="loginForm.email"
            placeholder="邮箱"
            prefix-icon="Message"
            @keyup.enter="submitForm"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="密码"
            type="password"
            prefix-icon="Lock"
            show-password
            @keyup.enter="submitForm"
          />
        </el-form-item>

        <div class="login-options">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          <router-link class="forgot-password" to="/forgot-password">忘记密码?</router-link>
        </div>

        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="submitForm"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="login-footer">
          <span>还没有账号?</span>
          <router-link class="register-link" to="/register">立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, FormInstance } from 'element-plus';
import { Message, Lock } from '@element-plus/icons-vue';
import { useUserStore } from '@/store/user';

const title = import.meta.env.VITE_APP_TITLE || 'AI招聘推荐平台';
const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const rememberMe = ref(false);
const loginForm = ref<FormInstance>();

const formModel = reactive({
  email: '',
  password: ''
});

const loginRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
};

onMounted(() => {
  // 检查是否已经登录
  if (userStore.isAuthenticated) {
    router.push('/dashboard');
  }
  
  // 从localStorage检查是否记住密码
  const savedEmail = localStorage.getItem('savedEmail');
  if (savedEmail) {
    formModel.email = savedEmail;
    rememberMe.value = true;
  }
});

const submitForm = async () => {
  if (!loginForm.value) return;
  
  await loginForm.value.validate(async (valid: boolean, fields?: any) => {
    if (valid) {
      await handleLogin();
    } else {
      showError(fields);
    }
  });
};

const showError = (fields: string[]) => {
  error.value = true;
  errorFields.value = fields;
};

const handleLogin = async () => {
  loading.value = true;
  
  try {
    const success = await userStore.login(formModel.email, formModel.password);
    
    if (success) {
      // 如果选了"记住我"，保存邮箱
      if (rememberMe.value) {
        localStorage.setItem('savedEmail', formModel.email);
      } else {
        localStorage.removeItem('savedEmail');
      }
      
      ElMessage.success('登录成功！');
      router.push('/dashboard');
    } else {
      ElMessage.error(userStore.error || '登录失败，请检查邮箱和密码');
    }
  } catch (error) {
    console.error('登录异常:', error);
    ElMessage.error('系统错误，请稍后再试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.login-form {
  margin-top: 24px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.forgot-password {
  font-size: 14px;
  color: var(--primary-color);
  text-decoration: none;
}

.login-button {
  width: 100%;
  padding: 12px 0;
}

.login-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.register-link {
  color: var(--primary-color);
  text-decoration: none;
  margin-left: 5px;
}
</style> 