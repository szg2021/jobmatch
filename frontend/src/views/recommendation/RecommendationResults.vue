<template>
  <div class="recommendation-results">
    <el-card>
      <template #header>
        <div class="page-header">
          <h2>{{ isJobMode ? '职位推荐结果' : '简历推荐结果' }}</h2>
          <div class="header-actions">
            <el-button-group>
              <el-button 
                :type="isJobMode ? 'primary' : ''" 
                @click="switchMode('job')"
              >
                职位推荐
              </el-button>
              <el-button 
                :type="!isJobMode ? 'primary' : ''" 
                @click="switchMode('resume')"
              >
                简历推荐
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>

      <div class="search-controls">
        <el-form :inline="true" :model="form" class="form">
          <el-form-item v-if="isJobMode" label="选择简历">
            <el-select 
              v-model="form.resumeId" 
              placeholder="选择您的简历" 
              @change="handleResumeChange"
              :loading="resumesLoading"
              :disabled="loading"
            >
              <el-option
                v-for="resume in resumes"
                :key="resume.id"
                :label="resume.title"
                :value="resume.id"
              />
              <template #empty>
                <div class="empty-options">
                  <p v-if="resumesLoading">正在加载简历...</p>
                  <p v-else>没有可用的简历</p>
                  <el-button 
                    v-if="!resumesLoading && resumes.length === 0" 
                    type="primary" 
                    size="small"
                    @click="goToCreateResume"
                  >
                    创建简历
                  </el-button>
                </div>
              </template>
            </el-select>
          </el-form-item>
          
          <el-form-item v-else label="选择职位">
            <el-select 
              v-model="form.jobId" 
              placeholder="选择职位" 
              @change="handleJobChange"
              :loading="jobsLoading"
              :disabled="loading"
            >
              <el-option
                v-for="job in jobs"
                :key="job.id"
                :label="job.title"
                :value="job.id"
              />
              <template #empty>
                <div class="empty-options">
                  <p v-if="jobsLoading">正在加载职位...</p>
                  <p v-else>没有可用的职位</p>
                  <el-button 
                    v-if="!jobsLoading && jobs.length === 0 && isCompanyUser" 
                    type="primary" 
                    size="small"
                    @click="goToCreateJob"
                  >
                    发布职位
                  </el-button>
                </div>
              </template>
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              @click="fetchRecommendations" 
              :loading="loading"
              :disabled="!canFetch"
            >
              获取推荐
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-if="errorMessage" class="error-message">
        <el-alert :title="errorMessage" type="error" show-icon :closable="true" @close="errorMessage = ''" />
      </div>

      <div class="filter-controls">
        <div class="filters">
          <span class="filter-label">算法筛选:</span>
          <el-checkbox-group v-model="algorithmFilters">
            <el-checkbox label="vector">向量搜索</el-checkbox>
            <el-checkbox label="lightfm">协同过滤</el-checkbox>
          </el-checkbox-group>
        </div>
        
        <div class="filters">
          <span class="filter-label">分数筛选:</span>
          <el-slider 
            v-model="scoreRange" 
            range 
            :min="0" 
            :max="100" 
            :format-tooltip="value => `${value}%`"
          ></el-slider>
        </div>
      </div>

      <div v-if="loading" class="loading-container">
        <div v-for="i in 3" :key="i" class="skeleton-item">
          <el-skeleton :loading="true" animated>
            <template #template>
              <div class="skeleton-card">
                <div class="skeleton-header">
                  <el-skeleton-item variant="h3" style="width: 70%" />
                  <el-skeleton-item variant="circle" style="width: 50px; height: 50px" />
                </div>
                <el-skeleton-item variant="p" style="width: 40%" />
                <el-skeleton-item variant="p" style="width: 80%" />
                <el-skeleton-item variant="button" style="width: 120px; margin-top: 15px" />
              </div>
            </template>
          </el-skeleton>
        </div>
      </div>
      
      <div v-else-if="recommendations.length === 0" class="empty-container">
        <el-empty description="暂无推荐结果">
          <template #description>
            <p v-if="hasSearched && filteredRecommendations.length === 0 && recommendations.length > 0">
              没有找到符合筛选条件的结果，请尝试调整筛选条件
            </p>
            <p v-else-if="hasSearched">
              没有找到匹配的推荐结果，请尝试选择不同的{{ isJobMode ? '简历' : '职位' }}
            </p>
            <p v-else>
              请选择{{ isJobMode ? '简历' : '职位' }}并点击"获取推荐"按钮
            </p>
          </template>
          <el-button v-if="hasSearched" @click="resetFilters">重置筛选条件</el-button>
        </el-empty>
      </div>
      
      <div v-else class="results-container">
        <div v-if="filteredRecommendations.length === 0 && recommendations.length > 0" class="no-filtered-results">
          <el-alert
            type="warning"
            show-icon
            :closable="false"
            title="没有符合筛选条件的结果"
            description="请尝试调整筛选条件或重置筛选"
          />
          <el-button class="reset-button" @click="resetFilters">重置筛选</el-button>
        </div>
        
        <div v-for="item in filteredRecommendations" :key="item.id" class="recommendation-item">
          <recommendation-card
            :title="item.title"
            :company="isJobMode ? item.company : (item.user ? item.user.name : '')"
            :match-score="item.match_score"
            :algorithms="item.algorithms || []"
            :match-details="item.match_details"
          >
            <template #actions>
              <div class="card-actions">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="viewDetail(item)"
                >
                  查看详情
                </el-button>
                <el-button 
                  v-if="isJobMode" 
                  type="success" 
                  size="small"
                  @click="applyJob(item.id)"
                  :loading="applyingJobId === item.id"
                >
                  申请职位
                </el-button>
                <el-button 
                  v-else 
                  type="success" 
                  size="small"
                  @click="contactCandidate(item)"
                >
                  联系候选人
                </el-button>
              </div>
            </template>
          </recommendation-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import axios from 'axios'
import RecommendationCard from '@/components/recommendation/RecommendationCard.vue'
import { useUserStore } from '@/store/user'

// 路由器
const router = useRouter()
const userStore = useUserStore()

// 状态
const mode = ref('job')  // 'job' 或 'resume'
const loading = ref(false)
const resumesLoading = ref(false)
const jobsLoading = ref(false)
const resumes = ref([])
const jobs = ref([])
const recommendations = ref([])
const hasSearched = ref(false)
const errorMessage = ref('')
const applyingJobId = ref(null)

// 记录上次获取的推荐结果，用于缓存
const cachedRecommendations = ref({
  job: {}, // { resumeId: recommendations }
  resume: {} // { jobId: recommendations }
})

// 表单数据
const form = ref({
  resumeId: null,
  jobId: null,
  limit: 20,
  includeDetails: true
})

// 筛选条件
const algorithmFilters = ref(['vector', 'lightfm'])
const scoreRange = ref([0, 100])

// 计算属性
const isJobMode = computed(() => mode.value === 'job')
const isCompanyUser = computed(() => userStore.user?.role === 'company')

const canFetch = computed(() => {
  return isJobMode.value ? !!form.value.resumeId : !!form.value.jobId
})

const filteredRecommendations = computed(() => {
  if (!recommendations.value || recommendations.value.length === 0) {
    return []
  }
  
  return recommendations.value.filter(rec => {
    // 检查算法筛选
    const hasMatchedAlgorithm = !rec.algorithms || rec.algorithms.length === 0 
      ? true 
      : rec.algorithms.some(algo => algorithmFilters.value.includes(algo))
    
    if (!hasMatchedAlgorithm) return false
    
    // 检查分数筛选
    const score = Math.round((rec.match_score || 0) * 100)
    return score >= scoreRange.value[0] && score <= scoreRange.value[1]
  })
})

// 方法
const switchMode = async (newMode) => {
  if (mode.value === newMode) return
  
  mode.value = newMode
  errorMessage.value = ''
  recommendations.value = []
  hasSearched.value = false
  
  // 根据模式加载必要的数据
  if (isJobMode.value) {
    if (resumes.value.length === 0) {
      await fetchResumes()
    }
  } else {
    if (jobs.value.length === 0) {
      await fetchJobs()
    }
  }
}

const fetchResumes = async () => {
  resumesLoading.value = true
  errorMessage.value = ''
  
  try {
    // 获取当前用户的简历列表
    const response = await axios.get('/api/v1/resumes/my')
    resumes.value = response.data
    
    // 如果有简历，自动选中第一个
    if (resumes.value.length > 0 && !form.value.resumeId) {
      form.value.resumeId = resumes.value[0].id
    } else if (resumes.value.length === 0) {
      ElNotification({
        title: '提示',
        message: '您还没有创建简历，请先创建一份简历以获取推荐',
        type: 'warning',
        duration: 5000
      })
    }
  } catch (error) {
    console.error('获取简历列表失败', error)
    errorMessage.value = error.response?.data?.detail || error.response?.data?.message || '获取简历列表失败，请稍后再试'
    ElMessage.error(errorMessage.value)
  } finally {
    resumesLoading.value = false
  }
}

const fetchJobs = async () => {
  jobsLoading.value = true
  errorMessage.value = ''
  
  try {
    // 获取职位列表
    const response = await axios.get('/api/v1/jobs')
    jobs.value = response.data.items || []
    
    // 如果有职位，自动选中第一个
    if (jobs.value.length > 0 && !form.value.jobId) {
      form.value.jobId = jobs.value[0].id
    } else if (jobs.value.length === 0) {
      ElNotification({
        title: '提示',
        message: '没有可用的职位，请稍后再试',
        type: 'warning',
        duration: 5000
      })
    }
  } catch (error) {
    console.error('获取职位列表失败', error)
    errorMessage.value = error.response?.data?.detail || error.response?.data?.message || '获取职位列表失败，请稍后再试'
    ElMessage.error(errorMessage.value)
  } finally {
    jobsLoading.value = false
  }
}

const fetchRecommendations = async () => {
  if (!canFetch.value) {
    ElMessage.warning(`请先选择${isJobMode.value ? '简历' : '职位'}`)
    return
  }
  
  // 检查缓存中是否有这个请求的结果
  const cacheKey = isJobMode.value ? form.value.resumeId : form.value.jobId
  const cachedResults = isJobMode.value 
    ? cachedRecommendations.value.job[cacheKey]
    : cachedRecommendations.value.resume[cacheKey]
    
  if (cachedResults) {
    recommendations.value = cachedResults
    hasSearched.value = true
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    const url = isJobMode.value 
      ? '/api/v1/recommendations/jobs' 
      : '/api/v1/recommendations/resumes'
    
    const params = {
      limit: form.value.limit,
      include_details: form.value.includeDetails
    }
    
    if (isJobMode.value) {
      params.resume_id = form.value.resumeId
    } else {
      params.job_id = form.value.jobId
    }
    
    const response = await axios.get(url, { params })
    
    if (response.data && response.data.success) {
      recommendations.value = response.data.data || []
      
      // 缓存结果
      if (isJobMode.value) {
        cachedRecommendations.value.job[form.value.resumeId] = [...recommendations.value]
      } else {
        cachedRecommendations.value.resume[form.value.jobId] = [...recommendations.value]
      }
      
      if (recommendations.value.length === 0) {
        ElMessage.info(`没有找到匹配的${isJobMode.value ? '职位' : '简历'}推荐`)
      }
    } else {
      errorMessage.value = response.data?.message || '获取推荐失败，请稍后再试'
      ElMessage.error(errorMessage.value)
    }
  } catch (error) {
    console.error('获取推荐失败', error)
    errorMessage.value = error.response?.data?.detail || error.response?.data?.message || '获取推荐失败，请稍后再试'
    ElMessage.error(errorMessage.value)
  } finally {
    loading.value = false
    hasSearched.value = true
  }
}

const handleResumeChange = () => {
  // 清空先前的推荐结果
  recommendations.value = []
  hasSearched.value = false
  errorMessage.value = ''
  
  // 自动获取推荐
  fetchRecommendations()
}

const handleJobChange = () => {
  // 清空先前的推荐结果
  recommendations.value = []
  hasSearched.value = false
  errorMessage.value = ''
  
  // 自动获取推荐
  fetchRecommendations()
}

const resetFilters = () => {
  algorithmFilters.value = ['vector', 'lightfm']
  scoreRange.value = [0, 100]
}

const viewDetail = (item) => {
  if (isJobMode.value) {
    router.push(`/jobs/${item.id}`)
  } else {
    router.push(`/resumes/${item.id}`)
  }
}

const applyJob = async (jobId) => {
  if (!jobId) return
  
  applyingJobId.value = jobId
  
  try {
    // 确认申请
    await ElMessageBox.confirm(
      '确定要申请这个职位吗？',
      '申请确认',
      {
        confirmButtonText: '确认申请',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 创建申请
    const resumeId = form.value.resumeId
    const response = await axios.post('/api/v1/applications', {
      job_id: jobId,
      resume_id: resumeId,
      cover_letter: '通过推荐系统申请'
    })
    
    if (response.data && response.data.success) {
      ElMessage.success('职位申请已提交')
    } else {
      ElMessage.error(response.data?.message || '申请失败，请稍后再试')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('申请职位失败', error)
      ElMessage.error(error.response?.data?.detail || error.response?.data?.message || '申请失败，请稍后再试')
    }
  } finally {
    applyingJobId.value = null
  }
}

const contactCandidate = (item) => {
  ElMessageBox.alert(
    `请联系候选人: ${item.user?.name || '未知'}\n邮箱: ${item.user?.email || '未提供'}`,
    '联系候选人',
    {
      confirmButtonText: '确定'
    }
  )
}

const goToCreateResume = () => {
  router.push('/resumes/create')
}

const goToCreateJob = () => {
  router.push('/jobs/create')
}

// 生命周期钩子
onMounted(async () => {
  // 基于当前模式加载初始数据
  if (isJobMode.value) {
    await fetchResumes()
  } else {
    await fetchJobs()
  }
})

// 观察筛选条件变化
watch([algorithmFilters, scoreRange], () => {
  const filteredCount = filteredRecommendations.value.length
  const totalCount = recommendations.value.length
  
  if (filteredCount < totalCount && totalCount > 0) {
    const hiddenCount = totalCount - filteredCount
    ElMessage.info(`已筛选出 ${filteredCount} 条结果，隐藏了 ${hiddenCount} 条不符合条件的结果`)
  }
}, { deep: true })
</script>

<style scoped>
.recommendation-results {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 10px;
}

.search-controls {
  margin-bottom: 20px;
}

.form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.error-message {
  margin-bottom: 20px;
}

.filter-controls {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.filters {
  margin-bottom: 15px;
}

.filter-label {
  font-weight: 500;
  margin-right: 10px;
}

.loading-container {
  padding: 20px 0;
}

.skeleton-item {
  margin-bottom: 16px;
}

.skeleton-card {
  padding: 20px;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.empty-container {
  padding: 40px 0;
  text-align: center;
}

.empty-options {
  padding: 10px;
  text-align: center;
}

.results-container {
  min-height: 200px;
}

.recommendation-item {
  margin-bottom: 16px;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.no-filtered-results {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.reset-button {
  margin-left: 10px;
}

@media (max-width: 768px) {
  .recommendation-results {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .form .el-form-item {
    margin-right: 0;
  }
  
  .card-actions {
    flex-direction: column;
  }
}
</style> 