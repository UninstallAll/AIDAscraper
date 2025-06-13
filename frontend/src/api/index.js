import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',  // 移除/api前缀，因为后端路由已经包含了它
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
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
apiClient.interceptors.response.use(
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

// 网站管理API
export const websiteApi = {
  // 获取所有网站列表
  list: async () => {
    const response = await apiClient.get('/websites/')
    return response.data
  },

  // 获取单个网站信息
  get: async (id) => {
    const response = await apiClient.get(`/websites/${id}`)
    return response.data
  },

  // 添加新网站
  add: async (website) => {
    const response = await apiClient.post('/websites/', website)
    return response.data
  },

  // 删除网站
  delete: async (id) => {
    const response = await apiClient.delete(`/websites/${id}`)
    return response.data
  },

  // 检查网站是否有爬虫实现
  checkScraper: async (id) => {
    const response = await apiClient.get(`/websites/${id}/has_scraper`)
    return response.data
  },

  // 创建爬虫
  createScraper: async (websiteId, scraperName) => {
    const response = await apiClient.post(`/websites/${websiteId}/create_scraper`, {
      website_id: websiteId,
      scraper_name: scraperName
    })
    return response.data
  },

  // 运行爬虫
  runScraper: async (params) => {
    const response = await apiClient.post('/websites/run_scraper', params)
    return response.data
  },

  // 获取所有可用爬虫
  availableScrapers: async () => {
    const response = await apiClient.get('/websites/scrapers/available')
    return response.data
  }
}

// 导出所有API服务
export default {
  websites: websiteApi
} 