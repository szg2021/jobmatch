<template>
  <div class="login-container">
    <!-- 顶部导航 -->
    <div class="header">
      <el-icon class="back-icon" @click="goBack"><ArrowLeft /></el-icon>
      <div class="header-title">AI帮你找工作</div>
    </div>

    <!-- 登录横幅 -->
    <div class="login-banner">
      <div class="banner-content">
        <h2>欢迎使用AI招聘推荐平台</h2>
        <p>智能招聘，高效匹配</p>
      </div>
    </div>

    <!-- 登录表单 -->
    <div class="login-form-container">
      <h2 class="form-title">登录账号</h2>

      <!-- 登录方式选择 -->
      <div class="login-type-selector">
        <el-radio-group v-model="loginType" size="large">
          <el-radio-button label="mobile">手机号登录</el-radio-button>
          <el-radio-button label="email">邮箱登录</el-radio-button>
        </el-radio-group>
      </div>

      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form">
        <!-- 手机号输入框 - 仅在手机号登录模式显示 -->
        <el-form-item v-if="loginType === 'mobile'" prop="phone">
          <div class="form-label">手机号</div>
          <el-input 
            v-model="loginForm.phone"
            placeholder="请输入手机号"
            clearable
          >
          </el-input>
        </el-form-item>

        <!-- 邮箱输入框 - 仅在邮箱登录模式显示 -->
        <el-form-item v-if="loginType === 'email'" prop="email">
          <div class="form-label">邮箱</div>
          <el-input 
            v-model="loginForm.email"
            placeholder="请输入邮箱地址"
            clearable
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item prop="password">
          <div class="form-label">密码</div>
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 登录按钮 -->
        <el-form-item>
          <el-button 
            type="primary" 
            class="login-button" 
            :loading="loading" 
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 分割线 -->
      <div class="divider">
        <span class="divider-text">或</span>
      </div>

      <!-- 社交登录 -->
      <div class="social-login">
        <div class="social-button wechat-button">
          <el-icon class="social-icon"><ChatRound /></el-icon>
        </div>
        <div class="register-link">
          没有账号？
          <router-link to="/register">注册</router-link>
        </div>
      </div>

      <!-- 测试账号提示 -->
      <div class="test-account">
        手机号测试: 13900009999，密码：123456
        <br>
        邮箱测试: test@example.com，密码：123456
      </div>
    </div>

    <!-- 底部导航 -->
    <BottomNavigation />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import type { FormInstance } from 'element-plus';
import { 
  ArrowLeft, 
  House, 
  UserFilled, 
  Service, 
  Avatar,
  ChatRound,
  Message,
  Lock
} from '@element-plus/icons-vue';
import api from '@/utils/api';
import { useUserStore } from '@/store/user';
import BottomNavigation from '@/components/layout/BottomNavigation.vue';

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const loginFormRef = ref<FormInstance>();
const loginType = ref('mobile'); // 默认使用手机号登录

// 表单数据
const loginForm = reactive({
  phone: '',
  email: '',
  password: ''
});

// 生成动态验证规则
const loginRules = reactive({
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ]
});

// 返回上一页
const goBack = () => {
  router.back();
};

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return;
  
  try {
    await loginFormRef.value.validate();
    
    loading.value = true;
    let success = false;
    
    try {
      if (loginType.value === 'mobile') {
        // 使用手机号登录
        success = await userStore.loginWithMobile(loginForm.phone, loginForm.password);
      } else {
        // 使用邮箱登录
        success = await userStore.login(loginForm.email, loginForm.password);
      }
      
      if (success) {
        ElMessage.success('登录成功');
        router.push('/dashboard');
      } else {
        ElMessage.error(userStore.error || '登录失败，请检查账号和密码');
      }
    } catch (error) {
      console.error('登录失败', error);
      // 错误已由全局处理器处理
    } finally {
      loading.value = false;
    }
  } catch (validationError) {
    console.log('表单验证失败', validationError);
  }
};

// 当登录类型变化时，重置表单验证状态
watch(loginType, () => {
  if (loginFormRef.value) {
    loginFormRef.value.clearValidate();
  }
});
</script>

<style scoped>
.login-container {
  padding: 16px;
  padding-bottom: 70px;
  min-height: 100vh;
  background-color: #fff;
  position: relative;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}

.back-icon {
  font-size: 20px;
  cursor: pointer;
}

.header-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 18px;
  font-weight: bold;
}

.login-banner {
  position: relative;
  margin-bottom: 30px;
  border-radius: 8px;
  overflow: hidden;
  height: 150px;
  background: linear-gradient(135deg, #4e6ef2, #6a8cff);
  display: flex;
  align-items: flex-end;
  padding: 20px;
}

.banner-content {
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.4);
}

.banner-content h2 {
  margin: 0;
  font-size: 24px;
  margin-bottom: 8px;
}

.banner-content p {
  margin: 0;
  font-size: 14px;
}

.login-form-container {
  padding: 0 10px;
}

.form-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 24px;
  text-align: center;
}

.login-type-selector {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.login-form {
  margin-bottom: 20px;
}

.form-label {
  font-size: 14px;
  margin-bottom: 8px;
  color: #606266;
}

.login-button {
  width: 100%;
  height: 44px;
  border-radius: 22px;
  margin-top: 10px;
}

.divider {
  display: flex;
  align-items: center;
  margin: 16px 0;
  color: #909399;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-top: 1px solid #EBEEF5;
}

.divider-text {
  padding: 0 16px;
}

.social-login {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.social-button {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background-color: #F5F7FA;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  cursor: pointer;
}

.social-icon {
  width: 24px;
  height: 24px;
}

.wechat-button {
  background-color: #07C160;
}

.register-link {
  color: #606266;
  font-size: 14px;
}

.register-link a {
  color: #409EFF;
  text-decoration: none;
}

.test-account {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin-top: 20px;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  background-color: white;
  display: flex;
  justify-content: space-around;
  align-items: center;
  border-top: 1px solid #eee;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #999;
  font-size: 22px;
}

.nav-label {
  font-size: 12px;
  margin-top: 4px;
}
</style> 