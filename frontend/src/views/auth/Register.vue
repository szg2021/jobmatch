<template>
  <div class="register-container">
    <!-- 顶部导航 -->
    <div class="header">
      <el-icon class="back-icon" @click="goBack"><ArrowLeft /></el-icon>
      <div class="header-title">AI帮你找工作</div>
    </div>

    <!-- 注册横幅 -->
    <div class="register-banner">
      <div class="banner-content">
        <h2>欢迎使用AI招聘推荐平台</h2>
        <p>智能招聘，高效匹配</p>
      </div>
    </div>

    <!-- 注册表单 -->
    <div class="register-form-container">
      <h2 class="form-title">注册</h2>

      <!-- 注册方式选择 -->
      <div class="register-type-selector">
        <el-radio-group v-model="registerType" size="large">
          <el-radio-button label="mobile">手机号注册</el-radio-button>
          <el-radio-button label="email">邮箱注册</el-radio-button>
        </el-radio-group>
      </div>

      <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" class="register-form">
        <!-- 手机号输入框 - 仅在手机号注册模式显示 -->
        <el-form-item v-if="registerType === 'mobile'" prop="phone">
          <div class="form-label">手机号</div>
          <el-input 
            v-model="registerForm.phone"
            placeholder="请输入手机号"
            clearable
          >
            <template #prefix>
              <el-icon><Phone /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 邮箱输入框 - 仅在邮箱注册模式显示 -->
        <el-form-item v-if="registerType === 'email'" prop="email">
          <div class="form-label">邮箱</div>
          <el-input 
            v-model="registerForm.email"
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
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 确认密码输入框 -->
        <el-form-item prop="confirmPassword">
          <div class="form-label">确认密码</div>
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 用户类型选择 -->
        <el-form-item prop="userType">
          <div class="form-label">用户类型</div>
          <el-radio-group v-model="registerForm.userType">
            <el-radio label="jobseeker">求职者</el-radio>
            <el-radio label="employer">企业招聘方</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 注册按钮 -->
        <el-form-item>
          <el-button 
            type="primary" 
            class="register-button" 
            :loading="loading" 
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 社交登录 -->
      <div class="social-login">
        <div class="login-link">
          已有账号？
          <router-link to="/login">登录</router-link>
        </div>
      </div>

      <!-- 第三方登录 -->
      <div class="other-login">
        <div class="other-login-title">其他登录方式</div>
        <div class="other-login-icons">
          <div class="social-button wechat-button">
            <el-icon class="social-icon"><ChatRound /></el-icon>
          </div>
        </div>
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
import type { FormInstance, FormRules } from 'element-plus';
import { 
  ArrowLeft,
  ChatRound,
  Message,
  Lock,
  Phone
} from '@element-plus/icons-vue';
import api from '@/utils/api';
import { useUserStore } from '@/store/user';
import BottomNavigation from '@/components/layout/BottomNavigation.vue';

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const registerFormRef = ref<FormInstance>();
const registerType = ref('mobile'); // 默认使用手机号注册

// 表单数据
const registerForm = reactive({
  phone: '',
  email: '',
  password: '',
  confirmPassword: '',
  userType: 'jobseeker'
});

// 验证密码一致性
const validatePass = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'));
  } else {
    callback();
  }
};

// 表单验证规则
const registerRules = reactive<FormRules>({
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
  ],
  confirmPassword: [
    { required: true, validator: validatePass, trigger: 'blur' }
  ],
  userType: [
    { required: true, message: '请选择用户类型', trigger: 'change' }
  ]
});

// 返回上一页
const goBack = () => {
  router.back();
};

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return;
  
  try {
    await registerFormRef.value.validate();
    
    loading.value = true;
    try {
      // 根据注册类型准备数据
      const userData = {
        password: registerForm.password,
        user_type: registerForm.userType,
        ...(registerType.value === 'mobile' ? { phone: registerForm.phone } : { email: registerForm.email })
      };
      
      // 使用 userStore 的 register 方法
      const success = await userStore.register(userData);
      
      if (success) {
        ElMessage.success('注册成功，请登录');
        // 跳转到登录页
        router.push('/login');
      } else {
        ElMessage.error(userStore.error || '注册失败，请稍后再试');
      }
    } catch (error) {
      // 错误已由全局处理器处理
    } finally {
      loading.value = false;
    }
  } catch (validationError) {
    // 表单验证失败，不执行注册操作
    loading.value = false;
  }
};

// 当注册类型变化时，重置表单验证状态
watch(registerType, () => {
  if (registerFormRef.value) {
    registerFormRef.value.clearValidate();
  }
});
</script>

<style scoped>
.register-container {
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

.register-banner {
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
  position: absolute;
  bottom: 20px;
  left: 20px;
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

.register-form-container {
  padding: 0 10px;
}

.form-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 24px;
  text-align: center;
}

.register-type-selector {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.register-form {
  margin-bottom: 20px;
}

.form-label {
  font-size: 14px;
  margin-bottom: 8px;
  color: #606266;
}

.register-button {
  width: 100%;
  height: 44px;
  border-radius: 22px;
  margin-top: 10px;
}

.social-login {
  text-align: center;
  margin-bottom: 20px;
}

.login-link {
  color: #606266;
  font-size: 14px;
}

.login-link a {
  color: #409EFF;
  text-decoration: none;
}

.other-login {
  text-align: center;
}

.other-login-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 16px;
}

.other-login-icons {
  display: flex;
  justify-content: center;
}

.social-button {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background-color: #F5F7FA;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.social-icon {
  width: 24px;
  height: 24px;
}

.wechat-button {
  background-color: #07C160;
}
</style> 