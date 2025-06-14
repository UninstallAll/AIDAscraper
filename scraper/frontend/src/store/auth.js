import { defineStore } from 'pinia'
import axios from 'axios'
import router from '../router'
import { API_URL } from '../api/config'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    loading: false,
    error: null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    currentUser: (state) => state.user
  },
  
  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      
      try {
        const formData = new FormData()
        formData.append('username', username)
        formData.append('password', password)
        
        const response = await axios.post(`${API_URL}/auth/login`, formData)
        const { access_token } = response.data
        
        // 保存令牌
        this.token = access_token
        localStorage.setItem('token', access_token)
        
        // 设置默认Authorization头
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        // 获取用户信息
        await this.fetchUserInfo()
        
        // 重定向到首页
        router.push('/')
        
        return true
      } catch (error) {
        this.error = error.response?.data?.detail || '登录失败，请检查用户名和密码'
        return false
      } finally {
        this.loading = false
      }
    },
    
    async fetchUserInfo() {
      try {
        const response = await axios.get(`${API_URL}/auth/me`)
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
      } catch (error) {
        console.error('获取用户信息失败', error)
      }
    },
    
    logout() {
      // 清除状态
      this.token = null
      this.user = null
      
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 清除Authorization头
      delete axios.defaults.headers.common['Authorization']
      
      // 重定向到登录页
      router.push('/login')
    }
  }
}) 