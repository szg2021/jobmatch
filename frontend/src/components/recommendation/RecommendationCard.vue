<template>
  <div class="recommendation-card">
    <el-card class="box-card" :body-style="{ padding: '0px' }">
      <div class="card-header">
        <div class="header-left">
          <h3 class="title">{{ title || '未知标题' }}</h3>
          <div v-if="company" class="company">{{ company }}</div>
        </div>
        <div class="header-right">
          <div class="match-score">
            <el-progress
              type="circle"
              :percentage="Math.round(safeMatchScore * 100)"
              :color="getScoreColor(safeMatchScore)"
              :stroke-width="6"
              :width="50"
            ></el-progress>
            <span class="score-text">{{ getScoreText }}</span>
          </div>
        </div>
      </div>

      <div class="card-body">
        <div class="algorithms">
          <span class="label">推荐算法:</span>
          <div class="algorithm-tags">
            <el-tag 
              v-for="algorithm in algorithms" 
              :key="algorithm"
              size="small"
              :type="getAlgorithmType(algorithm)"
              class="algorithm-tag"
            >
              {{ getAlgorithmName(algorithm) }}
            </el-tag>
            <el-tag v-if="!algorithms || algorithms.length === 0" size="small" type="info">
              未指定算法
            </el-tag>
          </div>
        </div>

        <div v-if="hasMatchDetails && showDetails" class="match-details">
          <el-divider>匹配详情</el-divider>
          
          <div v-if="safeMatchDetails.similarity !== undefined" class="detail-item">
            <span class="label">内容相似度:</span>
            <el-progress 
              :percentage="Math.round(safeMatchDetails.similarity * 100)" 
              :stroke-width="10"
              :color="getScoreColor(safeMatchDetails.similarity)"
            ></el-progress>
          </div>
          
          <div v-if="safeMatchDetails.skill_score !== undefined" class="detail-item">
            <span class="label">技能匹配度:</span>
            <el-progress 
              :percentage="Math.round(safeMatchDetails.skill_score * 100)" 
              :stroke-width="10"
              :color="getScoreColor(safeMatchDetails.skill_score)"
            ></el-progress>
          </div>
          
          <div v-if="safeMatchDetails.lightfm_score !== undefined" class="detail-item">
            <span class="label">协同过滤分数:</span>
            <el-progress 
              :percentage="Math.round(safeMatchDetails.lightfm_score * 100)" 
              :stroke-width="10"
              :color="getScoreColor(safeMatchDetails.lightfm_score)"
            ></el-progress>
          </div>
          
          <div v-if="hasMatchedSkills" class="matched-skills">
            <span class="label">匹配技能:</span>
            <div class="skills-list">
              <template v-if="safeMatchDetails.matched_skills && safeMatchDetails.matched_skills.length > 0">
                <el-tag
                  v-for="skill in safeMatchDetails.matched_skills"
                  :key="skill"
                  size="small"
                  type="success"
                  class="skill-tag"
                >
                  {{ skill }}
                </el-tag>
              </template>
              <el-tag v-else size="small" type="info">无匹配技能</el-tag>
            </div>
          </div>
        </div>
      </div>

      <div class="card-footer">
        <el-button type="text" @click="toggleDetails">
          {{ showDetails ? '隐藏详情' : '查看详情' }}
        </el-button>
        <slot name="actions"></slot>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  company: {
    type: String,
    default: ''
  },
  matchScore: {
    type: Number,
    required: true
  },
  algorithms: {
    type: Array,
    default: () => []
  },
  matchDetails: {
    type: Object,
    default: () => null
  }
})

const showDetails = ref(false)

// 安全访问matchScore
const safeMatchScore = computed(() => {
  // 确保是有效数字且在0-1之间
  let score = Number(props.matchScore)
  if (isNaN(score)) return 0
  return Math.max(0, Math.min(1, score))
})

// 安全访问matchDetails
const safeMatchDetails = computed(() => {
  return props.matchDetails || {}
})

// 判断是否有匹配细节可以显示
const hasMatchDetails = computed(() => {
  return !!props.matchDetails && (
    props.matchDetails.similarity !== undefined ||
    props.matchDetails.skill_score !== undefined ||
    props.matchDetails.lightfm_score !== undefined ||
    (props.matchDetails.matched_skills && props.matchDetails.matched_skills.length > 0)
  )
})

// 判断是否有匹配技能
const hasMatchedSkills = computed(() => {
  return !!props.matchDetails && 
    props.matchDetails.matched_skills && 
    Array.isArray(props.matchDetails.matched_skills)
})

const getScoreText = computed(() => {
  const score = safeMatchScore.value
  if (score >= 0.8) return '极高匹配'
  if (score >= 0.6) return '高匹配'
  if (score >= 0.4) return '中等匹配'
  if (score >= 0.2) return '低匹配'
  return '很低匹配'
})

const getScoreColor = (score) => {
  if (score >= 0.8) return '#67c23a'
  if (score >= 0.6) return '#7cc863'
  if (score >= 0.4) return '#e6a23c'
  if (score >= 0.2) return '#f56c6c'
  return '#909399'
}

const getAlgorithmType = (algorithm) => {
  switch (algorithm) {
    case 'vector':
      return 'primary'
    case 'lightfm':
      return 'success'
    case 'hybrid':
      return 'warning'
    default:
      return 'info'
  }
}

const getAlgorithmName = (algorithm) => {
  switch (algorithm) {
    case 'vector':
      return '向量搜索'
    case 'lightfm':
      return '协同过滤'
    case 'hybrid':
      return '混合算法'
    default:
      return algorithm
  }
}

// 切换详情显示
const toggleDetails = () => {
  showDetails.value = !showDetails.value
}
</script>

<style scoped>
.recommendation-card {
  margin-bottom: 16px;
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  flex-wrap: wrap;
}

.header-left {
  flex: 1;
  min-width: 200px;
}

.title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
  word-break: break-word;
}

.company {
  margin-top: 5px;
  font-size: 14px;
  color: #606266;
}

.match-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 5px 0;
}

.score-text {
  margin-top: 5px;
  font-size: 12px;
  color: #606266;
}

.card-body {
  padding: 15px 20px;
}

.algorithms {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.algorithm-tags {
  display: flex;
  flex-wrap: wrap;
}

.label {
  margin-right: 10px;
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.algorithm-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.match-details {
  margin-top: 15px;
}

.detail-item {
  margin-bottom: 12px;
}

.matched-skills {
  margin-top: 15px;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  margin-top: 8px;
}

.skill-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.card-footer {
  display: flex;
  padding: 10px 20px;
  border-top: 1px solid #f0f0f0;
  justify-content: space-between;
  flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    display: flex;
    justify-content: center;
    margin-top: 10px;
  }
  
  .algorithms {
    flex-direction: column;
  }
  
  .label {
    margin-bottom: 5px;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 10px;
  }
}
</style> 