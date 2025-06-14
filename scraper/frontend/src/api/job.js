/**
 * 爬虫任务API服务
 */
import apiClient from './config'

/**
 * 获取任务列表
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的记录数
 * @param {string} params.status - 任务状态过滤
 * @param {number} params.site_config_id - 站点配置ID过滤
 * @returns {Promise} - 响应Promise
 */
export function getJobs(params = {}) {
  return apiClient.get('/jobs', { params })
}

/**
 * 获取任务详情
 * @param {number} id - 任务ID
 * @returns {Promise} - 响应Promise
 */
export function getJob(id) {
  return apiClient.get(`/jobs/${id}`)
}

/**
 * 创建任务
 * @param {Object} data - 任务数据
 * @returns {Promise} - 响应Promise
 */
export function createJob(data) {
  return apiClient.post('/jobs', data)
}

/**
 * 更新任务
 * @param {number} id - 任务ID
 * @param {Object} data - 任务数据
 * @returns {Promise} - 响应Promise
 */
export function updateJob(id, data) {
  return apiClient.put(`/jobs/${id}`, data)
}

/**
 * 删除任务
 * @param {number} id - 任务ID
 * @returns {Promise} - 响应Promise
 */
export function deleteJob(id) {
  return apiClient.delete(`/jobs/${id}`)
}

/**
 * 启动任务
 * @param {number} id - 任务ID
 * @returns {Promise} - 响应Promise
 */
export function startJob(id) {
  return apiClient.post(`/jobs/${id}/start`)
}

/**
 * 取消任务
 * @param {number} id - 任务ID
 * @returns {Promise} - 响应Promise
 */
export function cancelJob(id) {
  return apiClient.post(`/jobs/${id}/cancel`)
}

/**
 * 获取任务日志
 * @param {number} id - 任务ID
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回的日志行数
 * @returns {Promise} - 响应Promise
 */
export function getJobLogs(id, params = {}) {
  return apiClient.get(`/jobs/${id}/logs`, { params })
}

/**
 * 获取任务统计信息
 * @param {Object} params - 查询参数
 * @returns {Promise} - 响应Promise
 */
export function getJobStats(params = {}) {
  return apiClient.get('/jobs/stats', { params })
}

export default {
  getJobs,
  getJob,
  createJob,
  updateJob,
  deleteJob,
  startJob,
  cancelJob,
  getJobLogs,
  getJobStats
} 