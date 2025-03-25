import { defineStore } from 'pinia';
import axios from 'axios';
import { useUserStore } from './user';

interface Resume {
  id: string;
  document_id: string;
  user_id: string;
  content: string;
  skills: string[];
  education: string;
  experience: string;
  created_at: string;
  updated_at: string;
}

interface ResumeState {
  resumes: Resume[];
  currentResume: Resume | null;
  loading: boolean;
  error: string | null;
}

export const useResumeStore = defineStore('resume', {
  state: (): ResumeState => ({
    resumes: [],
    currentResume: null,
    loading: false,
    error: null
  }),
  
  getters: {
    hasResumes: (state) => state.resumes.length > 0,
    getResumeById: (state) => (id: string) => {
      return state.resumes.find(r => r.id === id) || null;
    }
  },
  
  actions: {
    async fetchResumes() {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return;
        
        const response = await axios.get('/api/resumes', {
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        this.resumes = response.data;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch resumes';
      } finally {
        this.loading = false;
      }
    },
    
    async fetchResumeById(id: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return;
        
        const response = await axios.get(`/api/resumes/${id}`, {
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        this.currentResume = response.data;
        return this.currentResume;
      } catch (error: any) {
        this.error = error.response?.data?.detail || `Failed to fetch resume with ID ${id}`;
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    async uploadResume(file: File) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return false;
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await axios.post('/api/resumes/upload', formData, {
          headers: {
            Authorization: `Bearer ${userStore.token}`,
            'Content-Type': 'multipart/form-data'
          }
        });
        
        // 刷新简历列表
        await this.fetchResumes();
        return true;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to upload resume';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async updateResume(id: string, data: any) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return false;
        
        const response = await axios.put(`/api/resumes/${id}`, data, {
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        // 更新本地简历数据
        const index = this.resumes.findIndex(r => r.id === id);
        if (index !== -1) {
          this.resumes[index] = response.data;
        }
        
        if (this.currentResume?.id === id) {
          this.currentResume = response.data;
        }
        
        return true;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to update resume';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async extractSkills(content: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return [];
        
        const response = await axios.post('/api/resumes/extract-skills', 
          { content },
          {
            headers: {
              Authorization: `Bearer ${userStore.token}`
            }
          }
        );
        
        return response.data.skills || [];
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to extract skills';
        return [];
      } finally {
        this.loading = false;
      }
    }
  }
}); 