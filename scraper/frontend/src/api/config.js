import axios from 'axios'

// API基础URL
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    // 添加默认的测试令牌
    'Authorization': 'Bearer test-token'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 始终使用测试令牌
    config.headers.Authorization = 'Bearer test-token'
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => response,
  error => {
    // 对于API错误，打印日志但不重定向到登录页
    if (error.response) {
      console.error('API错误:', error.response.status, error.response.data)
    }
    return Promise.reject(error)
  }
)

export default apiClient 