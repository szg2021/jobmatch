import { defineStore } from 'pinia';
import axios from 'axios';
import { useUserStore } from './user';

interface JobRecommendation {
  job_id: string;
  title: string;
  company_name: string;
  location: string;
  job_type: string;
  match_score: number;
  match_details: {
    skill_score: number;
    matched_skills: string[];
    context_score: number;
    explanation?: string;
  };
}

interface ResumeRecommendation {
  resume_id: string;
  user_id: string;
  full_name: string;
  match_score: number;
  match_details: {
    skill_score: number;
    matched_skills: string[];
    context_score: number;
  };
}

interface RecommendationState {
  jobRecommendations: JobRecommendation[];
  resumeRecommendations: ResumeRecommendation[];
  loading: boolean;
  error: string | null;
}

// 匹配设置接口
interface MatchSettings {
  skillWeight?: number;
  contextWeight?: number;
  algorithm?: 'basic' | 'enhanced' | 'advanced';
  minScore?: number;
}

export const useRecommendationStore = defineStore('recommendation', {
  state: (): RecommendationState => ({
    jobRecommendations: [],
    resumeRecommendations: [],
    loading: false,
    error: null
  }),
  
  getters: {
    hasJobRecommendations: (state) => state.jobRecommendations.length > 0,
    hasResumeRecommendations: (state) => state.resumeRecommendations.length > 0,
    topJobRecommendations: (state) => {
      return [...state.jobRecommendations]
        .sort((a, b) => b.match_score - a.match_score)
        .slice(0, 5);
    },
    topResumeRecommendations: (state) => {
      return [...state.resumeRecommendations]
        .sort((a, b) => b.match_score - a.match_score)
        .slice(0, 5);
    }
  },
  
  actions: {
    async getJobRecommendations(resumeId: string, settings?: MatchSettings) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return;
        
        // 构建参数
        const params: Record<string, any> = { resume_id: resumeId };
        
        // 添加匹配设置
        if (settings) {
          if (settings.skillWeight !== undefined) params.skill_weight = settings.skillWeight;
          if (settings.contextWeight !== undefined) params.context_weight = settings.contextWeight;
          if (settings.algorithm !== undefined) params.algorithm = settings.algorithm;
          if (settings.minScore !== undefined) params.min_score = settings.minScore;
        }
        
        const response = await axios.get(`/api/recommendations/resume/${resumeId}/jobs`, {
          params,
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        this.jobRecommendations = response.data;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch job recommendations';
      } finally {
        this.loading = false;
      }
    },
    
    async getResumeRecommendations(jobId: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return;
        
        const response = await axios.get(`/api/recommendations/job/${jobId}/resumes`, {
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        this.resumeRecommendations = response.data;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch resume recommendations';
      } finally {
        this.loading = false;
      }
    },
    
    async getDetailedMatch(resumeId: string, jobId: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return null;
        
        const response = await axios.get(`/api/recommendations/match-details`, {
          params: {
            resume_id: resumeId,
            job_id: jobId
          },
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch detailed match';
        return null;
      } finally {
        this.loading = false;
      }
    }
  }
}); 