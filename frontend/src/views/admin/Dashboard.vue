<template>
  <div class="admin-dashboard">
    <h1>管理员仪表盘</h1>
    
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="dashboard-card" shadow="hover">
          <router-link to="/admin/users">
            <div class="card-content">
              <el-icon><User /></el-icon>
              <div class="card-title">用户管理</div>
              <div class="card-desc">管理系统用户、权限和账号</div>
            </div>
          </router-link>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="dashboard-card" shadow="hover">
          <router-link to="/admin/jobs">
            <div class="card-content">
              <el-icon><Briefcase /></el-icon>
              <div class="card-title">岗位管理</div>
              <div class="card-desc">查看和管理所有岗位信息</div>
            </div>
          </router-link>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="dashboard-card" shadow="hover">
          <router-link to="/admin/recommendation-config">
            <div class="card-content">
              <el-icon><Setting /></el-icon>
              <div class="card-title">推荐系统配置</div>
              <div class="card-desc">管理AI推荐引擎参数设置</div>
            </div>
          </router-link>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="dashboard-card" shadow="hover">
          <router-link to="/admin/statistics">
            <div class="card-content">
              <el-icon><DataAnalysis /></el-icon>
              <div class="card-title">系统统计</div>
              <div class="card-desc">查看平台运行数据和指标</div>
            </div>
          </router-link>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Other dashboard content -->
  </div>
</template>

<script>
import { User, Briefcase, Setting, DataAnalysis } from '@element-plus/icons-vue'

export default {
  components: {
    User, Briefcase, Setting, DataAnalysis
  },
  // ... existing code ...
}
</script>

// ... existing styles ... 