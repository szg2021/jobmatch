<template>
  <PageContentWrapper className="job-recommendations-container">
    <page-header
      title="职位推荐"
      subtitle="基于您的简历自动推荐最匹配的职位"
    />
    
    <el-card v-if="!selectedResume" shadow="hover" v-loading="resumeLoadingState.isLoading">
      <template v-if="resumeStore.hasResumes">
        <h3>选择简历</h3>
        <p>请选择一份简历以查看针对性的职位推荐</p>
        
        <el-select
          v-model="selectedResumeId"
          placeholder="选择简历"
          style="width: 100%; margin-bottom: 20px;"
          @change="loadRecommendations"
        >
          <el-option
            v-for="resume in resumeStore.resumes"
            :key="resume.id"
            :label="`上传于 ${formatDate(resume.created_at)}`"
            :value="resume.id"
          />
        </el-select>
      </template>
      
      <el-empty v-else description="您还没有上传简历">
        <el-button type="primary" @click="goToResumePage">上传简历</el-button>
      </el-empty>
    </el-card>
    
    <template v-if="selectedResume">
      <el-card shadow="hover" class="resume-card">
        <template #header>
          <div class="card-header">
            <div>
              <h3>已选简历</h3>
              <p class="resume-date">上传于 {{ formatDate(selectedResume.created_at) }}</p>
            </div>
            <div class="header-actions">
              <el-button type="primary" size="small" @click="showMatchSettings">
                <el-icon><Setting /></el-icon>
                匹配设置
              </el-button>
              <el-button text @click="changeResume">更换简历</el-button>
            </div>
          </div>
        </template>
        
        <div class="resume-skills">
          <h4>提取技能：</h4>
          <div>
            <el-tag
              v-for="skill in selectedResume.skills"
              :key="skill"
              class="skill-tag"
              type="success"
              effect="light"
            >
              {{ skill }}
            </el-tag>
            <span v-if="!selectedResume.skills || selectedResume.skills.length === 0">
              未提取到技能
            </span>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="hover" class="recommendations-card" v-loading="jobLoadingState.isLoading">
        <template #header>
          <div class="card-header">
            <h3>推荐职位</h3>
            <el-button
              type="primary"
              size="small"
              @click="refreshRecommendations"
              :disabled="jobLoadingState.isLoading"
            >
              刷新推荐
            </el-button>
          </div>
        </template>
        
        <template v-if="recommendationStore.hasJobRecommendations">
          <el-row :gutter="20">
            <el-col
              v-for="job in recommendationStore.jobRecommendations"
              :key="job.job_id"
              :xs="24"
              :sm="24"
              :md="12"
              :lg="8"
              :xl="8"
            >
              <el-card shadow="hover" class="job-card">
                <template #header>
                  <div class="job-header">
                    <h4 class="job-title">{{ job.title }}</h4>
                    <match-score
                      :value="job.match_score"
                      :size="70"
                    />
                  </div>
                </template>
                
                <div class="job-info">
                  <div class="job-item">
                    <span class="label">公司：</span>
                    <span class="value">{{ job.company_name }}</span>
                  </div>
                  <div class="job-item">
                    <span class="label">地点：</span>
                    <span class="value">{{ job.location }}</span>
                  </div>
                  <div class="job-item">
                    <span class="label">类型：</span>
                    <span class="value">{{ job.job_type }}</span>
                  </div>
                  <div class="job-item">
                    <span class="label">技能匹配：</span>
                    <span class="value">{{ formatMatchScore(job.match_details.skill_score) }}</span>
                  </div>
                  
                  <div class="matched-skills">
                    <h5>匹配技能：</h5>
                    <div>
                      <el-tag
                        v-for="skill in job.match_details.matched_skills"
                        :key="skill"
                        class="skill-tag"
                        type="info"
                        effect="light"
                        size="small"
                      >
                        {{ skill }}
                      </el-tag>
                      <span v-if="!job.match_details.matched_skills || job.match_details.matched_skills.length === 0">
                        无匹配技能
                      </span>
                    </div>
                  </div>
                  
                  <div class="job-actions">
                    <el-button
                      type="primary"
                      @click="viewJobDetails(job.job_id)"
                    >
                      查看详情
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </template>
        
        <el-empty
          v-else-if="!jobLoadingState.isLoading"
          description="暂无匹配的职位推荐"
        >
          <p>尝试更新您的简历技能或等待更多职位发布</p>
        </el-empty>
      </el-card>
    </template>
    
    <!-- 职位详情对话框 -->
    <el-dialog
      v-model="jobDetailsVisible"
      title="职位详情"
      width="800px"
      destroy-on-close
    >
      <div v-loading="detailsLoadingState.isLoading">
        <template v-if="currentJob">
          <h2>{{ currentJob.title }}</h2>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="公司名称" :span="2">
              {{ currentJob.company_name }}
            </el-descriptions-item>
            <el-descriptions-item label="工作地点">
              {{ currentJob.location }}
            </el-descriptions-item>
            <el-descriptions-item label="工作类型">
              {{ currentJob.job_type }}
            </el-descriptions-item>
            <el-descriptions-item label="薪资范围" :span="2">
              {{ currentJob.salary_range || '未提供' }}
            </el-descriptions-item>
          </el-descriptions>
          
          <div class="job-detail-section">
            <h3>职位要求</h3>
            <div class="requirements">
              <el-tag
                v-for="requirement in currentJob.requirements"
                :key="requirement"
                class="requirement-tag"
                effect="light"
              >
                {{ requirement }}
              </el-tag>
              <div v-if="!currentJob.requirements || currentJob.requirements.length === 0">
                未提供具体要求
              </div>
            </div>
          </div>
          
          <div class="job-detail-section">
            <h3>职位描述</h3>
            <pre class="job-content">{{ currentJob.content }}</pre>
          </div>
          
          <div class="job-detail-section">
            <h3>匹配分析</h3>
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="match-card">
                  <h4>总匹配度</h4>
                  <match-score
                    :value="currentJobMatch?.match_score || 0"
                    :size="100"
                  />
                </div>
              </el-col>
              <el-col :span="8">
                <div class="match-card">
                  <h4>技能匹配</h4>
                  <match-score
                    :value="currentJobMatch?.match_details?.skill_score || 0"
                    :size="100"
                    label="技能"
                  />
                </div>
              </el-col>
              <el-col :span="8">
                <div class="match-card">
                  <h4>内容匹配</h4>
                  <match-score
                    :value="currentJobMatch?.match_details?.context_score || 0"
                    :size="100"
                    label="内容"
                  />
                </div>
              </el-col>
            </el-row>
            
            <h4>匹配技能</h4>
            <div class="matched-skills">
              <el-tag
                v-for="skill in currentJobMatch?.match_details?.matched_skills"
                :key="skill"
                class="skill-tag"
                type="success"
                effect="light"
              >
                {{ skill }}
              </el-tag>
              <span v-if="!currentJobMatch?.match_details?.matched_skills || currentJobMatch?.match_details?.matched_skills.length === 0">
                无匹配技能
              </span>
            </div>
            
            <div class="match-explanation" v-if="currentJobMatch?.match_details?.explanation">
              <h4>匹配解释</h4>
              <div class="explanation-content">
                {{ currentJobMatch.match_details.explanation }}
              </div>
            </div>
          </div>
        </template>
      </div>
    </el-dialog>

    <!-- 匹配设置对话框 -->
    <el-dialog
      v-model="matchSettingsVisible"
      title="匹配设置"
      width="500px"
    >
      <el-form label-position="top">
        <el-form-item label="技能匹配权重">
          <el-slider
            v-model="matchSettings.skillWeight"
            :min="0"
            :max="100"
            :step="5"
            :format-tooltip="(val) => `${val}%`"
          />
        </el-form-item>
        
        <el-form-item label="内容匹配权重">
          <el-slider
            v-model="matchSettings.contextWeight"
            :min="0"
            :max="100"
            :step="5"
            :format-tooltip="(val) => `${val}%`"
            :disabled="true"
          />
        </el-form-item>
        
        <el-form-item label="匹配算法">
          <el-select 
            v-model="matchSettings.algorithm" 
            style="width: 100%;"
          >
            <el-option 
              label="基础匹配 (简单技能比对)" 
              value="basic" 
            />
            <el-option 
              label="增强匹配 (语义分析)" 
              value="enhanced" 
            />
            <el-option 
              label="高级匹配 (AI深度匹配)" 
              value="advanced" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="最低匹配度">
          <el-input-number
            v-model="matchSettings.minScore"
            :min="0"
            :max="100"
            :step="5"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="matchSettingsVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMatchSettings">保存设置</el-button>
      </template>
    </el-dialog>
  </PageContentWrapper>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useResumeStore } from '@/store/resume';
import { useRecommendationStore } from '@/store/recommendation';
import PageHeader from '@/components/common/PageHeader.vue';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
import MatchScore from '@/components/common/MatchScore.vue';
import { formatDate, formatMatchScore } from '@/utils/helpers';
import { useLoading } from '@/utils/loadingState';
import api from '@/utils/api';
import { Job, JobRecommendation } from '@/types';
import { Setting } from '@element-plus/icons-vue';

interface JobMatch extends JobRecommendation {
  // 扩展匹配接口以包含完整的职位详情
}

const route = useRoute();
const router = useRouter();
const resumeStore = useResumeStore();
const recommendationStore = useRecommendationStore();

const resumeLoadingState = useLoading();
const jobLoadingState = useLoading();
const detailsLoadingState = useLoading();
const selectedResumeId = ref('');
const jobDetailsVisible = ref(false);
const currentJob = ref<Job | null>(null);
const currentJobMatch = ref<JobRecommendation | null>(null);

// 匹配设置
const matchSettingsVisible = ref(false);
const matchSettings = ref({
  skillWeight: 60,
  contextWeight: 40, // 会根据skillWeight自动计算
  algorithm: 'enhanced',
  minScore: 40
});

// 监听技能权重变化，自动更新内容权重
watch(() => matchSettings.value.skillWeight, (newVal) => {
  matchSettings.value.contextWeight = 100 - newVal;
});

const selectedResume = computed(() => {
  if (!selectedResumeId.value) return null;
  return resumeStore.getResumeById(selectedResumeId.value);
});

watch(() => route.query.resumeId, (newId) => {
  if (newId && typeof newId === 'string') {
    selectedResumeId.value = newId;
    loadRecommendations();
  }
}, { immediate: true });

onMounted(async () => {
  try {
    await resumeLoadingState.withLoading(async () => {
      // 获取简历列表
      if (!resumeStore.hasResumes) {
        await resumeStore.fetchResumes();
      }
      
      // 如果URL中没有resumeId，但有简历，默认选第一个
      if (!selectedResumeId.value && resumeStore.resumes.length > 0) {
        selectedResumeId.value = resumeStore.resumes[0].id;
        await loadRecommendations();
      }
    });
  } catch (error) {
    console.error('初始化数据失败:', error);
    ElMessage.error('获取数据失败，请刷新页面重试');
  }
});

const loadRecommendations = async () => {
  if (!selectedResumeId.value) return;
  
  try {
    await jobLoadingState.withLoading(async () => {
      await recommendationStore.getJobRecommendations(selectedResumeId.value);
    });
  } catch (error) {
    console.error('获取职位推荐失败:', error);
    ElMessage.error('获取职位推荐失败，请稍后重试');
  }
};

const refreshRecommendations = () => {
  loadRecommendations();
};

const changeResume = () => {
  selectedResumeId.value = '';
};

const goToResumePage = () => {
  router.push('/dashboard/resume');
};

const viewJobDetails = async (jobId: string) => {
  jobDetailsVisible.value = true;
  
  try {
    await detailsLoadingState.withLoading(async () => {
      // 获取职位详情
      const response = await api.get(`/jobs/${jobId}`);
      currentJob.value = response.data;
      
      // 获取匹配详情
      const matchResponse = await api.get('/recommendations/match-details', {
        params: {
          resume_id: selectedResumeId.value,
          job_id: jobId
        }
      });
      
      currentJobMatch.value = matchResponse.data;
    });
  } catch (error) {
    console.error('获取职位详情失败:', error);
    ElMessage.error('获取职位详情失败，请稍后重试');
  }
};

// 显示匹配设置对话框
const showMatchSettings = () => {
  matchSettingsVisible.value = true;
};

// 保存匹配设置并重新获取推荐
const saveMatchSettings = async () => {
  try {
    await jobLoadingState.withLoading(async () => {
      // 准备参数
      const params = {
        resume_id: selectedResumeId.value,
        settings: matchSettings.value
      };
      
      // 调用推荐API，传入设置
      await recommendationStore.getJobRecommendations(
        selectedResumeId.value, 
        matchSettings.value
      );
    });
    
    matchSettingsVisible.value = false;
    ElMessage.success('匹配设置已更新，已刷新推荐结果');
  } catch (error) {
    console.error('更新匹配设置失败:', error);
    ElMessage.error('更新匹配设置失败，请稍后重试');
  }
};
</script>

<style scoped>
.job-recommendations-container {
  max-width: 1200px;
  margin: 0 auto;
}

.resume-card {
  margin-bottom: 20px;
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

.resume-date {
  font-size: 14px;
  color: #909399;
  margin: 5px 0 0 0;
}

.resume-skills {
  margin-top: 10px;
}

.resume-skills h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-weight: 500;
  font-size: 16px;
}

.recommendations-card {
  margin-bottom: 20px;
}

.job-card {
  margin-bottom: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.job-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.job-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.job-item {
  margin-bottom: 8px;
  display: flex;
}

.job-item .label {
  font-weight: 500;
  width: 80px;
  flex-shrink: 0;
}

.job-item .value {
  flex: 1;
}

.matched-skills {
  margin-top: 10px;
  margin-bottom: 15px;
}

.matched-skills h5 {
  margin-top: 0;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
}

.job-actions {
  margin-top: auto;
  display: flex;
  justify-content: center;
  padding-top: 15px;
}

.skill-tag {
  margin-right: 8px;
  margin-bottom: 8px;
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
  margin-bottom: 8px;
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

.match-card {
  text-align: center;
  padding: 15px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.match-card h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: 500;
}
</style> 