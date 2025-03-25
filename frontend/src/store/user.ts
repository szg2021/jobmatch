import { defineStore } from 'pinia';
import axios from 'axios';
import router from '../router';
import api from '../utils/api';

interface UserState {
  token: string | null;
  user: {
    id: string | null;
    email: string | null;
    phone: string | null;
    full_name: string | null;
    role: string | null;
    is_active: boolean;
    company_name?: string | null;
    company_size?: string | null;
    company_industry?: string | null;
  };
  loading: boolean;
  error: string | null;
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('token'),
    user: {
      id: null,
      email: null,
      phone: null,
      full_name: null,
      role: null,
      is_active: true,
      company_name: null,
      company_size: null,
      company_industry: null
    },
    loading: false,
    error: null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user.role === 'admin',
    isJobSeeker: (state) => state.user.role === 'job_seeker',
    isEmployer: (state) => state.user.role === 'company',
    userRole: (state) => state.user.role,
    userFullName: (state) => state.user.full_name || 'User'
  },
  
  actions: {
    async login(email: string, password: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.post('/auth/login/email', {
          email,
          password
        });
        
        const { access_token, user } = response.data;
        this.setToken(access_token);
        this.setUser(user);
        
        return true;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Login failed';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async loginWithMobile(phone: string, password: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.post('/auth/login/mobile', {
          phone,
          password
        });
        
        const { access_token, user } = response.data;
        this.setToken(access_token);
        this.setUser(user);
        
        return true;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Login failed';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async register(userData: any) {
      this.loading = true;
      this.error = null;
      
      try {
        await api.post('/auth/register', userData);
        return true;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Registration failed';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async fetchUserInfo() {
      if (!this.token) return;
      
      this.loading = true;
      
      try {
        const response = await api.get('/auth/me');
        this.setUser(response.data);
      } catch (error: any) {
        if (error.response?.status === 401) {
          this.logout();
        }
        this.error = error.response?.data?.detail || 'Failed to fetch user info';
      } finally {
        this.loading = false;
      }
    },
    
    setToken(token: string) {
      this.token = token;
      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    },
    
    logout() {
      this.token = null;
      this.user = {
        id: null,
        email: null,
        phone: null,
        full_name: null,
        role: null,
        is_active: true,
        company_name: null,
        company_size: null,
        company_industry: null
      };
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      router.push('/login');
    },

    setUser(userData: any) {
      this.user = {
        id: userData.id || null,
        email: userData.email || null,
        phone: userData.phone || null,
        full_name: userData.full_name || null,
        role: userData.role || null,
        is_active: userData.is_active !== undefined ? userData.is_active : true,
        company_name: userData.company_name || null,
        company_size: userData.company_size || null,
        company_industry: userData.company_industry || null
      };
    },

    async fetchUserProfile() {
      if (!this.token) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.get('/auth/me');
        this.setUser(response.data);
        return response.data;
      } catch (error: any) {
        this.error = error.message || 'Failed to fetch user profile';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateUserProfile(userData: Partial<UserState['user']>) {
      if (!this.token) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.put('/users/me', userData);
        this.setUser({ ...this.user, ...response.data });
        return response.data;
      } catch (error: any) {
        this.error = error.message || 'Failed to update user profile';
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
}); 