<template>
  <PageContentWrapper className="resume-container">
    <page-header
      title="我的简历"
      subtitle="管理您的简历并获取职位推荐"
    >
      <template #actions>
        <el-button
          type="primary"
          @click="showUploadDialog"
          :disabled="loadingState.isLoading"
        >
          上传新简历
        </el-button>
      </template>
    </page-header>
    
    <el-card shadow="hover" v-loading="loadingState.isLoading">
      <template v-if="resumeStore.hasResumes">
        <el-tabs v-model="activeTab" type="card">
          <el-tab-pane label="简历列表" name="list">
            <el-table
              :data="resumeStore.resumes"
              style="width: 100%"
              border
              stripe
            >
              <el-table-column prop="id" label="ID" width="100" />
              <el-table-column label="上传日期" width="180">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="更新日期" width="180">
                <template #default="scope">
                  {{ formatDate(scope.row.updated_at) }}
                </template>
              </el-table-column>
              <el-table-column label="提取技能" show-overflow-tooltip>
                <template #default="scope">
                  <el-tag
                    v-for="skill in scope.row.skills"
                    :key="skill"
                    class="skill-tag"
                    type="success"
                    effect="light"
                  >
                    {{ skill }}
                  </el-tag>
                  <span v-if="!scope.row.skills || scope.row.skills.length === 0">
                    未提取到技能
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" align="center">
                <template #default="scope">
                  <el-button
                    type="primary"
                    size="small"
                    @click="viewResumeDetails(scope.row)"
                  >
                    详情
                  </el-button>
                  <el-button
                    type="success"
                    size="small"
                    @click="viewRecommendations(scope.row)"
                  >
                    推荐
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          
          <el-tab-pane label="简历详情" name="details" v-if="selectedResume">
            <el-form label-position="top">
              <el-form-item label="简历ID">
                <span>{{ selectedResume.id }}</span>
              </el-form-item>
              
              <el-form-item label="教育经历">
                <el-input
                  v-model="selectedResume.education"
                  type="textarea"
                  :rows="4"
                  placeholder="暂无教育经历数据"
                />
              </el-form-item>
              
              <el-form-item label="工作经验">
                <el-input
                  v-model="selectedResume.experience"
                  type="textarea"
                  :rows="4"
                  placeholder="暂无工作经验数据"
                />
              </el-form-item>
              
              <el-form-item label="提取技能">
                <div class="skills-container">
                  <el-tag
                    v-for="skill in selectedResume.skills"
                    :key="skill"
                    class="skill-tag"
                    type="success"
                    effect="light"
                    closable
                    @close="removeSkill(skill)"
                  >
                    {{ skill }}
                  </el-tag>
                  <el-input
                    v-if="inputVisible"
                    ref="skillInput"
                    v-model="inputValue"
                    class="skill-input"
                    size="small"
                    @keyup.enter="addSkill"
                    @blur="addSkill"
                  />
                  <el-button
                    v-else
                    class="button-new-skill"
                    size="small"
                    @click="showInput"
                  >
                    + 添加技能
                  </el-button>
                  <el-button
                    class="button-extract-skills"
                    type="primary"
                    plain
                    size="small"
                    @click="extractSkills"
                    :loading="extractingSkills"
                  >
                    自动提取技能
                  </el-button>
                </div>
                <div class="skill-suggestions" v-if="skillSuggestions.length > 0">
                  <p class="suggestion-title">技能建议：</p>
                  <div class="suggestion-list">
                    <el-tag
                      v-for="skill in skillSuggestions"
                      :key="skill"
                      class="suggestion-tag"
                      type="info"
                      effect="plain"
                      @click="addSuggestedSkill(skill)"
                    >
                      + {{ skill }}
                    </el-tag>
                  </div>
                </div>
              </el-form-item>
              
              <el-form-item label="简历内容">
                <el-input
                  v-model="selectedResume.content"
                  type="textarea"
                  :rows="15"
                  placeholder="暂无简历内容"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button
                  type="primary"
                  @click="updateSelectedResume"
                  :loading="updateLoading"
                >
                  保存更改
                </el-button>
                <el-button @click="activeTab = 'list'">返回列表</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </template>
      
      <template v-else-if="!loadingState.isLoading">
        <el-empty description="您还没有上传过简历">
          <el-button type="primary" @click="showUploadDialog">上传简历</el-button>
        </el-empty>
      </template>
    </el-card>
    
    <!-- 上传简历对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传简历"
      width="500px"
    >
      <file-upload
        :allowed-types="['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']"
        :max-size="10"
        tip="请上传PDF或DOCX格式的简历文件，不超过10MB"
        @upload="uploadResume"
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
        </span>
      </template>
    </el-dialog>
  </PageContentWrapper>
</template>

<script lang="ts" setup>
import { ref, computed, reactive, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElInput } from 'element-plus';
import { useResumeStore } from '@/store/resume';
import PageHeader from '@/components/common/PageHeader.vue';
import FileUpload from '@/components/common/FileUpload.vue';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
import { formatDate } from '@/utils/helpers';
import { useLoading } from '@/utils/loadingState';

const router = useRouter();
const resumeStore = useResumeStore();
const loadingState = useLoading();
const updateLoading = ref(false);
const activeTab = ref('list');
const uploadDialogVisible = ref(false);
const selectedResume = ref<any>(null);
const inputVisible = ref(false);
const inputValue = ref('');
const skillInput = ref<InstanceType<typeof ElInput>>();
const extractingSkills = ref(false);
const skillSuggestions = ref([]);

onMounted(async () => {
  try {
    await loadingState.withLoading(async () => {
      await resumeStore.fetchResumes();
    });
  } catch (error) {
    console.error('获取简历列表失败:', error);
    ElMessage.error('获取简历列表失败，请刷新页面重试');
  }
});

const showUploadDialog = () => {
  uploadDialogVisible.value = true;
};

const uploadResume = async (file: File) => {
  try {
    await loadingState.withLoading(async () => {
      const success = await resumeStore.uploadResume(file);
      
      if (success) {
        ElMessage.success('简历上传成功');
        uploadDialogVisible.value = false;
      } else {
        ElMessage.error(resumeStore.error || '简历上传失败，请稍后重试');
      }
    });
  } catch (error) {
    console.error('上传简历异常:', error);
    ElMessage.error('系统错误，请稍后再试');
  }
};

const viewResumeDetails = async (resume: any) => {
  try {
    await loadingState.withLoading(async () => {
      const detailedResume = await resumeStore.fetchResumeById(resume.id);
      selectedResume.value = { ...detailedResume };
      activeTab.value = 'details';
    });
  } catch (error) {
    console.error('获取简历详情失败:', error);
    ElMessage.error('获取简历详情失败，请稍后重试');
  }
};

const viewRecommendations = (resume: any) => {
  router.push({
    name: 'JobRecommendations',
    query: { resumeId: resume.id }
  });
};

const showInput = () => {
  inputVisible.value = true;
  nextTick(() => {
    skillInput.value?.input?.focus();
  });
};

const addSkill = () => {
  if (inputValue.value && selectedResume.value) {
    const skills = selectedResume.value.skills || [];
    
    if (!skills.includes(inputValue.value.trim())) {
      selectedResume.value.skills = [...skills, inputValue.value.trim()];
    }
  }
  
  inputVisible.value = false;
  inputValue.value = '';
};

const removeSkill = (skillToRemove: string) => {
  if (selectedResume.value) {
    selectedResume.value.skills = selectedResume.value.skills.filter(
      (skill: string) => skill !== skillToRemove
    );
  }
};

const updateSelectedResume = async () => {
  if (!selectedResume.value) return;
  
  try {
    updateLoading.value = true;
    await loadingState.withLoading(async () => {
      const success = await resumeStore.updateResume(selectedResume.value.id, {
        skills: selectedResume.value.skills,
        education: selectedResume.value.education,
        experience: selectedResume.value.experience
      });
      
      if (success) {
        ElMessage.success('简历更新成功');
      } else {
        ElMessage.error(resumeStore.error || '简历更新失败，请稍后重试');
      }
    });
    updateLoading.value = false;
  } catch (error) {
    console.error('更新简历异常:', error);
    ElMessage.error('系统错误，请稍后再试');
    updateLoading.value = false;
  }
};

const extractSkills = async () => {
  if (!selectedResume.value) return;
  
  try {
    extractingSkills.value = true;
    await loadingState.withLoading(async () => {
      const suggestions = await resumeStore.extractSkills(selectedResume.value.content);
      skillSuggestions.value = suggestions;
      
      if (suggestions.length === 0) {
        ElMessage.info('未从简历中提取到技能，请检查简历内容或手动添加技能');
      } else {
        ElMessage.success(`成功提取到 ${suggestions.length} 项技能`);
      }
    });
  } catch (error) {
    console.error('提取技能异常:', error);
    ElMessage.error('系统错误，请稍后再试');
  } finally {
    extractingSkills.value = false;
  }
};

const addSuggestedSkill = (skill: string) => {
  if (selectedResume.value) {
    const skills = selectedResume.value.skills || [];
    if (!skills.includes(skill)) {
      selectedResume.value.skills = [...skills, skill];
    }
  }
};
</script>

<style scoped>
.resume-container {
  max-width: 1200px;
  margin: 0 auto;
}

.skill-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.skills-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.skill-input {
  width: 100px;
  margin-right: 8px;
  vertical-align: middle;
}

.button-new-skill {
  margin-bottom: 8px;
}

.skill-suggestions {
  margin-top: 10px;
}

.suggestion-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.suggestion-list {
  display: flex;
  flex-wrap: wrap;
}

.suggestion-tag {
  margin-right: 5px;
  margin-bottom: 5px;
  cursor: pointer;
}
</style> 