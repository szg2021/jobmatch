<template>
  <div class="recommendation-config-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <h2>推荐系统配置</h2>
          <div>
            <el-button
              type="primary"
              @click="createNewConfig"
              :disabled="loading"
            >
              新建配置
            </el-button>
            <el-button
              type="success"
              @click="triggerTraining"
              :disabled="loading || isTraining"
            >
              {{ isTraining ? '训练中...' : '立即训练模型' }}
            </el-button>
          </div>
        </div>
      </template>

      <!-- 配置列表 -->
      <div v-loading="loading" class="config-list">
        <el-empty v-if="configList.length === 0" description="暂无配置" />
        <el-table v-else :data="configList" stripe style="width: 100%">
          <el-table-column label="名称" prop="name" />
          <el-table-column label="模型参数">
            <template #default="{ row }">
              <div>学习率: {{ row.learning_rate }}</div>
              <div>损失函数: {{ row.loss_function }}</div>
              <div>嵌入维度: {{ row.embedding_dim }}</div>
            </template>
          </el-table-column>
          <el-table-column label="推荐权重">
            <template #default="{ row }">
              <div>向量搜索: {{ (row.vector_weight * 100).toFixed(0) }}%</div>
              <div>协同过滤: {{ (row.lightfm_weight * 100).toFixed(0) }}%</div>
            </template>
          </el-table-column>
          <el-table-column label="训练计划" width="160">
            <template #default="{ row }">
              <div>Cron: {{ row.train_schedule }}</div>
              <div>
                启动时训练: <el-tag size="small" :type="row.train_on_startup ? 'success' : 'info'">
                  {{ row.train_on_startup ? '是' : '否' }}
                </el-tag>
              </div>
              <div v-if="row.last_trained">
                上次训练: {{ formatDate(row.last_trained) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">
                {{ row.is_active ? '已激活' : '未激活' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button-group>
                <el-button
                  v-if="!row.is_active"
                  type="primary"
                  size="small"
                  @click="activateConfig(row.id)"
                >
                  激活
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  @click="editConfig(row)"
                >
                  编辑
                </el-button>
                <el-button
                  v-if="!row.is_active"
                  type="danger"
                  size="small"
                  @click="deleteConfig(row.id)"
                >
                  删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 编辑/创建对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑配置' : '创建配置'"
      width="700px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="140px"
        v-loading="formLoading"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="输入配置名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="输入配置描述"
          />
        </el-form-item>

        <el-divider>模型参数</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学习率" prop="learning_rate">
              <el-slider
                v-model="formData.learning_rate"
                :min="0.001"
                :max="0.1"
                :step="0.001"
                :format-tooltip="value => value.toFixed(3)"
              />
              <div class="param-value">{{ formData.learning_rate.toFixed(3) }}</div>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="损失函数" prop="loss_function">
              <el-select v-model="formData.loss_function" placeholder="选择损失函数">
                <el-option label="WARP (加权近似排序)" value="warp" />
                <el-option label="BPR (贝叶斯个性化排序)" value="bpr" />
                <el-option label="Logistic (逻辑回归)" value="logistic" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="嵌入维度" prop="embedding_dim">
              <el-slider
                v-model="formData.embedding_dim"
                :min="16"
                :max="128"
                :step="8"
              />
              <div class="param-value">{{ formData.embedding_dim }}</div>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="训练轮数" prop="epochs">
              <el-slider
                v-model="formData.epochs"
                :min="10"
                :max="100"
                :step="5"
              />
              <div class="param-value">{{ formData.epochs }}</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户正则化参数" prop="user_alpha">
              <el-slider
                v-model="formData.user_alpha"
                :min="0.000001"
                :max="0.001"
                :step="0.000001"
                :format-tooltip="value => value.toExponential(2)"
              />
              <div class="param-value">{{ formData.user_alpha.toExponential(2) }}</div>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="物品正则化参数" prop="item_alpha">
              <el-slider
                v-model="formData.item_alpha"
                :min="0.000001"
                :max="0.001"
                :step="0.000001"
                :format-tooltip="value => value.toExponential(2)"
              />
              <div class="param-value">{{ formData.item_alpha.toExponential(2) }}</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>推荐权重</el-divider>
        
        <el-alert
          type="info"
          :closable="false"
          show-icon
        >
          向量搜索权重和协同过滤权重之和必须等于1.0
        </el-alert>
        
        <el-row :gutter="20" class="mt-2">
          <el-col :span="12">
            <el-form-item label="向量搜索权重" prop="vector_weight">
              <el-slider
                v-model="formData.vector_weight"
                :min="0"
                :max="1"
                :step="0.1"
                :format-tooltip="value => `${(value * 100).toFixed(0)}%`"
                @change="updateLightFMWeight"
              />
              <div class="param-value">{{ (formData.vector_weight * 100).toFixed(0) }}%</div>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="协同过滤权重" prop="lightfm_weight">
              <el-slider
                v-model="formData.lightfm_weight"
                :min="0"
                :max="1"
                :step="0.1"
                :format-tooltip="value => `${(value * 100).toFixed(0)}%`"
                @change="updateVectorWeight"
              />
              <div class="param-value">{{ (formData.lightfm_weight * 100).toFixed(0) }}%</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>训练计划</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="18">
            <el-form-item label="Cron表达式" prop="train_schedule">
              <el-input v-model="formData.train_schedule" placeholder="输入cron表达式，例如: 0 2 * * *">
                <template #append>
                  <el-tooltip content="Cron表达式格式: 分 时 日 月 星期，例如: 0 2 * * * 表示每天凌晨2点">
                    <el-icon><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="启动时训练" prop="train_on_startup">
              <el-switch v-model="formData.train_on_startup" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>其他设置</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最大推荐数量" prop="max_recommendations">
              <el-slider
                v-model="formData.max_recommendations"
                :min="5"
                :max="50"
                :step="5"
              />
              <div class="param-value">{{ formData.max_recommendations }}</div>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="设为活跃配置" prop="is_active">
              <el-switch v-model="formData.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import { format } from 'date-fns'

// 状态
const loading = ref(false)
const isTraining = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const formLoading = ref(false)
const submitLoading = ref(false)
const configList = ref([])
const formRef = ref(null)

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  learning_rate: 0.05,
  loss_function: 'warp',
  embedding_dim: 64,
  user_alpha: 0.000001,
  item_alpha: 0.000001,
  epochs: 30,
  num_threads: 4,
  vector_weight: 0.6,
  lightfm_weight: 0.4,
  train_schedule: '0 2 * * *',
  train_on_startup: true,
  max_recommendations: 10,
  is_active: false
})

// 验证规则
const rules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度应在2到50个字符之间', trigger: 'blur' }
  ],
  learning_rate: [
    { required: true, message: '请设置学习率', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value < 0.001 || value > 0.1) {
          callback(new Error('学习率应在0.001到0.1之间'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  loss_function: [
    { required: true, message: '请选择损失函数', trigger: 'change' }
  ],
  embedding_dim: [
    { required: true, message: '请设置嵌入维度', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value < 16 || value > 128) {
          callback(new Error('嵌入维度应在16到128之间'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  vector_weight: [
    { required: true, message: '请设置向量搜索权重', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (Math.abs(value + formData.lightfm_weight - 1) > 0.001) {
          callback(new Error('向量权重与协同过滤权重之和必须为1'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  lightfm_weight: [
    { required: true, message: '请设置协同过滤权重', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (Math.abs(value + formData.vector_weight - 1) > 0.001) {
          callback(new Error('向量权重与协同过滤权重之和必须为1'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  train_schedule: [
    { required: true, message: '请输入Cron表达式', trigger: 'blur' },
    { 
      pattern: /^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$/,
      message: '请输入有效的Cron表达式',
      trigger: 'blur'
    }
  ],
  max_recommendations: [
    { required: true, message: '请设置最大推荐数量', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value < 5 || value > 50) {
          callback(new Error('最大推荐数量应在5到50之间'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 权重更新函数
const updateLightFMWeight = (value) => {
  formData.lightfm_weight = parseFloat((1 - value).toFixed(1))
}

const updateVectorWeight = (value) => {
  formData.vector_weight = parseFloat((1 - value).toFixed(1))
}

// 监听权重变化
watch(
  () => formData.vector_weight,
  (newValue) => {
    // 保证两个权重之和为1
    formData.lightfm_weight = parseFloat((1 - newValue).toFixed(1))
  }
)

watch(
  () => formData.lightfm_weight,
  (newValue) => {
    // 保证两个权重之和为1
    formData.vector_weight = parseFloat((1 - newValue).toFixed(1))
  }
)

// 日期格式化
const formatDate = (dateStr) => {
  if (!dateStr) return '未训练'
  try {
    const date = new Date(dateStr)
    return format(date, 'yyyy-MM-dd HH:mm:ss')
  } catch (error) {
    return dateStr
  }
}

// 获取配置列表
const fetchConfigList = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/admin/recommendation-config/')
    configList.value = response.data
  } catch (error) {
    ElMessage.error('获取配置列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 获取训练状态
const fetchTrainingStatus = async () => {
  try {
    const response = await axios.get('/api/v1/admin/recommendation-config/training/status')
    isTraining.value = response.data.in_progress
    
    if (isTraining.value) {
      // 如果正在训练，30秒后再次检查
      setTimeout(fetchTrainingStatus, 30000)
    }
  } catch (error) {
    console.error('获取训练状态失败', error)
  }
}

// 创建新配置
const createNewConfig = () => {
  isEditing.value = false
  // 重置表单
  Object.assign(formData, {
    name: '',
    description: '',
    learning_rate: 0.05,
    loss_function: 'warp',
    embedding_dim: 64,
    user_alpha: 0.000001,
    item_alpha: 0.000001,
    epochs: 30,
    num_threads: 4,
    vector_weight: 0.6,
    lightfm_weight: 0.4,
    train_schedule: '0 2 * * *',
    train_on_startup: true,
    max_recommendations: 10,
    is_active: false
  })
  dialogVisible.value = true
}

// 编辑配置
const editConfig = (config) => {
  isEditing.value = true
  formLoading.value = true
  
  // 获取配置详情
  axios.get(`/api/v1/admin/recommendation-config/${config.id}`)
    .then(response => {
      Object.assign(formData, response.data)
      dialogVisible.value = true
    })
    .catch(error => {
      ElMessage.error('获取配置详情失败')
      console.error(error)
    })
    .finally(() => {
      formLoading.value = false
    })
}

// 激活配置
const activateConfig = (id) => {
  loading.value = true
  axios.post(`/api/v1/admin/recommendation-config/${id}/activate`)
    .then(() => {
      ElMessage.success('配置已激活')
      fetchConfigList()
    })
    .catch(error => {
      ElMessage.error('激活配置失败')
      console.error(error)
    })
    .finally(() => {
      loading.value = false
    })
}

// 删除配置
const deleteConfig = (id) => {
  ElMessageBox.confirm('确定要删除此配置吗？此操作不可恢复', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    loading.value = true
    axios.delete(`/api/v1/admin/recommendation-config/${id}`)
      .then(() => {
        ElMessage.success('配置已删除')
        fetchConfigList()
      })
      .catch(error => {
        ElMessage.error('删除配置失败')
        console.error(error)
      })
      .finally(() => {
        loading.value = false
      })
  }).catch(() => {})
}

// 触发训练
const triggerTraining = () => {
  if (isTraining.value) return
  
  ElMessageBox.confirm('确定要开始训练模型吗？这可能需要较长时间', '确认', {
    confirmButtonText: '开始训练',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    loading.value = true
    axios.post('/api/v1/admin/recommendation-config/training/trigger')
      .then(response => {
        ElMessage.success(response.data.message)
        isTraining.value = true
        
        // 30秒后检查训练状态
        setTimeout(fetchTrainingStatus, 30000)
      })
      .catch(error => {
        ElMessage.error('触发训练失败')
        console.error(error)
      })
      .finally(() => {
        loading.value = false
      })
  }).catch(() => {})
}

// 提交表单
const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitLoading.value = true
    
    try {
      if (isEditing.value) {
        // 更新配置
        const id = formData.id
        const { id: _, ...updateData } = formData
        await axios.put(`/api/v1/admin/recommendation-config/${id}`, updateData)
        ElMessage.success('配置已更新')
      } else {
        // 创建配置
        await axios.post('/api/v1/admin/recommendation-config/', formData)
        ElMessage.success('配置已创建')
      }
      
      dialogVisible.value = false
      fetchConfigList()
    } catch (error) {
      ElMessage.error(isEditing.value ? '更新配置失败' : '创建配置失败')
      console.error(error)
    } finally {
      submitLoading.value = false
    }
  })
}

// 生命周期钩子
onMounted(() => {
  fetchConfigList()
  fetchTrainingStatus()
})
</script>

<style scoped>
.recommendation-config-container {
  padding: 20px;
}

.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-list {
  margin-top: 20px;
}

.mt-2 {
  margin-top: 12px;
}

.param-value {
  text-align: center;
  margin-top: 5px;
  font-size: 14px;
  color: #606266;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style> 