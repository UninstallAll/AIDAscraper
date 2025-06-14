import { defineStore } from 'pinia'
import axios from 'axios'
import router from '../router'
import { API_URL } from '../api/config'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // 默认设置为已登录状态，使用测试令牌
    token: 'test-token',
    user: {
      id: 1,
      username: 'test-user',
      email: 'test@example.com',
      is_active: true,
      tenant_id: 'default'
    },
    loading: false,
    error: null
  }),
  
  getters: {
    // 始终返回已登录状态
    isLoggedIn: () => true,
    currentUser: (state) => state.user
  },
  
  actions: {
    async login(username, password) {
      // 直接返回成功，不进行实际登录
      router.push('/')
      return true
    },
    
    async fetchUserInfo() {
      // 不进行实际API调用
      return this.user
    },
    
    logout() {
      // 登出后直接重定向到首页而不是登录页
      router.push('/')
    }
  }
}) 