/**
 * 站点配置API服务
 */
import apiClient from './config'

/**
 * 获取站点列表
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的记录数
 * @returns {Promise} - 响应Promise
 */
export function getSites(params = {}) {
  return apiClient.get('/sites', { params })
}

/**
 * 获取站点详情
 * @param {number} id - 站点ID
 * @returns {Promise} - 响应Promise
 */
export function getSite(id) {
  return apiClient.get(`/sites/${id}`)
}

/**
 * 创建站点
 * @param {Object} data - 站点数据
 * @returns {Promise} - 响应Promise
 */
export function createSite(data) {
  return apiClient.post('/sites', data)
}

/**
 * 更新站点
 * @param {number} id - 站点ID
 * @param {Object} data - 站点数据
 * @returns {Promise} - 响应Promise
 */
export function updateSite(id, data) {
  return apiClient.put(`/sites/${id}`, data)
}

/**
 * 删除站点
 * @param {number} id - 站点ID
 * @returns {Promise} - 响应Promise
 */
export function deleteSite(id) {
  return apiClient.delete(`/sites/${id}`)
}

/**
 * 测试站点配置
 * @param {Object} data - 站点配置数据
 * @returns {Promise} - 响应Promise
 */
export function testSiteConfig(data) {
  return apiClient.post('/sites/test', data)
}

/**
 * 导入站点配置
 * @param {Object} data - 站点配置JSON数据
 * @returns {Promise} - 响应Promise
 */
export function importSiteConfig(data) {
  return apiClient.post('/sites/import', data)
}

/**
 * 导出站点配置
 * @param {number} id - 站点ID
 * @returns {Promise} - 响应Promise
 */
export function exportSiteConfig(id) {
  return apiClient.get(`/sites/${id}/export`)
}

export default {
  getSites,
  getSite,
  createSite,
  updateSite,
  deleteSite,
  testSiteConfig,
  importSiteConfig,
  exportSiteConfig
} 