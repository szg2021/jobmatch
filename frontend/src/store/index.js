import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
  state: {
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  },
  
  getters: {
    isAuthenticated: state => !!state.token,
    isAdmin: state => state.user && state.user.role === 'admin',
    isCompanyUser: state => state.user && state.user.role === 'company',
    isJobSeeker: state => state.user && state.user.role === 'jobseeker',
    getUser: state => state.user,
    getToken: state => state.token,
    isLoading: state => state.loading,
    getError: state => state.error
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_TOKEN(state, token) {
      state.token = token
      if (token) {
        localStorage.setItem('token', token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } else {
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
      }
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    CLEAR_ERROR(state) {
      state.error = null
    }
  },
  
  actions: {
    // 用户登录
    async login({ commit, dispatch }, credentials) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await axios.post('/api/v1/login/access-token', credentials)
        const token = response.data.access_token
        
        commit('SET_TOKEN', token)
        await dispatch('fetchCurrentUser')
        
        return true
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '登录失败')
        return false
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 获取当前用户信息
    async fetchCurrentUser({ commit, state }) {
      if (!state.token) return null
      
      commit('SET_LOADING', true)
      
      try {
        const response = await axios.get('/api/v1/users/me')
        commit('SET_USER', response.data)
        return response.data
      } catch (error) {
        if (error.response && error.response.status === 401) {
          // Token失效，清除用户状态
          commit('SET_TOKEN', null)
          commit('SET_USER', null)
        }
        commit('SET_ERROR', error.response?.data?.detail || '获取用户信息失败')
        return null
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 注册新用户
    async register({ commit, dispatch }, userData) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        await axios.post('/api/v1/users', userData)
        
        // 自动登录
        if (userData.email && userData.password) {
          return await dispatch('login', {
            username: userData.email,
            password: userData.password
          })
        }
        
        return true
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '注册失败')
        return false
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 退出登录
    logout({ commit }) {
      commit('SET_TOKEN', null)
      commit('SET_USER', null)
    },
    
    // 更新用户信息
    async updateUserProfile({ commit, state }, profileData) {
      if (!state.user) return false
      
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await axios.put(`/api/v1/users/${state.user.id}`, profileData)
        commit('SET_USER', response.data)
        return true
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '更新个人信息失败')
        return false
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 清除错误信息
    clearError({ commit }) {
      commit('CLEAR_ERROR')
    }
  }
}) 