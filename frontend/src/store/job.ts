import { defineStore } from 'pinia';
import axios from 'axios';
import { useUserStore } from './user';

interface Job {
  id: string;
  document_id: string;
  user_id: string;
  title: string;
  company_name: string;
  location: string;
  job_type: string;
  salary_range: string;
  content: string;
  requirements: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface JobState {
  jobs: Job[];
  currentJob: Job | null;
  loading: boolean;
  error: string | null;
}

export const useJobStore = defineStore('job', {
  state: (): JobState => ({
    jobs: [],
    currentJob: null,
    loading: false,
    error: null
  }),
  
  getters: {
    hasJobs: (state) => state.jobs.length > 0,
    getJobById: (state) => (id: string) => {
      return state.jobs.find(job => job.id === id) || null;
    },
    activeJobs: (state) => state.jobs.filter(job => job.is_active)
  },
  
  actions: {
    async fetchJobs(filters: any = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return;
        
        // 构建查询参数
        const params = new URLSearchParams();
        if (filters.is_active !== undefined) {
          params.append('is_active', filters.is_active.toString());
        }
        if (filters.company_name) {
          params.append('company_name', filters.company_name);
        }
        if (filters.location) {
          params.append('location', filters.location);
        }
        if (filters.job_type) {
          params.append('job_type', filters.job_type);
        }
        
        const response = await axios.get(`/api/jobs?${params.toString()}`, {
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        this.jobs = response.data;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch jobs';
      } finally {
        this.loading = false;
      }
    },
    
    async fetchJobById(id: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return;
        
        const response = await axios.get(`/api/jobs/${id}`, {
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        this.currentJob = response.data;
        return this.currentJob;
      } catch (error: any) {
        this.error = error.response?.data?.detail || `Failed to fetch job with ID ${id}`;
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    async uploadJob(file: File) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return false;
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await axios.post('/api/jobs/upload', formData, {
          headers: {
            Authorization: `Bearer ${userStore.token}`,
            'Content-Type': 'multipart/form-data'
          }
        });
        
        // 刷新职位列表
        await this.fetchJobs();
        return true;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to upload job';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async updateJob(id: string, data: any) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return false;
        
        const response = await axios.put(`/api/jobs/${id}`, data, {
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        // 更新本地职位数据
        const index = this.jobs.findIndex(job => job.id === id);
        if (index !== -1) {
          this.jobs[index] = response.data;
        }
        
        if (this.currentJob?.id === id) {
          this.currentJob = response.data;
        }
        
        return true;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to update job';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async toggleJobActive(id: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const userStore = useUserStore();
        if (!userStore.token) return false;
        
        const response = await axios.post(`/api/jobs/${id}/toggle-active`, {}, {
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        // 更新本地职位数据
        const index = this.jobs.findIndex(job => job.id === id);
        if (index !== -1) {
          this.jobs[index] = response.data;
        }
        
        if (this.currentJob?.id === id) {
          this.currentJob = response.data;
        }
        
        return true;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to toggle job status';
        return false;
      } finally {
        this.loading = false;
      }
    }
  }
}); 