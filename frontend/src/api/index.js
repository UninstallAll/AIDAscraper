import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 在发送请求前做些什么
    return config
  },
  error => {
    // 对请求错误做些什么
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 对响应数据做些什么
    const res = response.data
    
    // 根据API设计自定义判断逻辑
    if (res.code && res.code !== 0) {
      // 处理错误
      console.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    } else {
      return res
    }
  },
  error => {
    // 对响应错误做些什么
    console.error('请求错误: ' + error)
    return Promise.reject(error)
  }
)

// API请求函数
export default {
  // 爬虫任务相关API
  scrapers: {
    // 获取所有爬虫任务
    getTasks() {
      return api.get('/scrapers/tasks')
    },
    
    // 创建新爬虫任务
    createTask(data) {
      return api.post('/scrapers/tasks', data)
    },
    
    // 获取任务详情
    getTaskDetail(id) {
      return api.get(`/scrapers/tasks/${id}`)
    },
    
    // 控制爬虫任务
    controlTask(id, action) {
      return api.put(`/scrapers/tasks/${id}/control`, { action })
    }
  },
  
  // 艺术家相关API
  artists: {
    // 获取艺术家列表
    list(params) {
      return api.get('/artists', { params })
    },
    
    // 获取艺术家详情
    getDetail(id) {
      return api.get(`/artists/${id}`)
    },
    
    // 获取艺术家作品
    getArtworks(id) {
      return api.get(`/artists/${id}/artworks`)
    }
  },
  
  // 艺术品相关API
  artworks: {
    // 获取艺术品列表
    list(params) {
      return api.get('/artworks', { params })
    },
    
    // 获取艺术品详情
    getDetail(id) {
      return api.get(`/artworks/${id}`)
    }
  },
  
  // 数据统计API
  statistics: {
    // 获取控制面板数据
    getDashboard() {
      return api.get('/statistics/dashboard')
    }
  }
} 