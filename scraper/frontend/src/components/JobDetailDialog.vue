<template>
  <el-dialog
    :title="job ? `任务详情: ${job.name}` : '任务详情'"
    v-model="dialogVisible"
    width="80%"
    :before-close="handleClose"
    destroy-on-close
  >
    <div v-if="job" class="job-detail">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="info">
          <div class="info-container">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="任务ID">{{ job.id }}</el-descriptions-item>
              <el-descriptions-item label="任务名称">{{ job.name }}</el-descriptions-item>
              <el-descriptions-item label="站点">{{ job.site_config?.name }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(job.status)">{{ job.status }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDateTime(job.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="开始时间">{{ formatDateTime(job.started_at) }}</el-descriptions-item>
              <el-descriptions-item label="完成时间">{{ formatDateTime(job.completed_at) }}</el-descriptions-item>
              <el-descriptions-item label="运行时间">{{ formatRuntime(job.runtime_seconds) }}</el-descriptions-item>
              <el-descriptions-item label="调度类型">{{ job.schedule_type }}</el-descriptions-item>
              <el-descriptions-item label="租户ID">{{ job.tenant_id }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="progress-container">
            <h3>任务进度</h3>
            <job-progress :job="job" :stroke-width="10" />
          </div>

          <div class="config-container" v-if="job.config">
            <h3>任务配置</h3>
            <el-input
              type="textarea"
              :rows="5"
              v-model="configJson"
              readonly
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="任务日志" name="logs">
          <div class="logs-container">
            <div class="logs-header">
              <el-select v-model="logLevel" placeholder="日志级别" style="width: 120px">
                <el-option label="全部" value="all" />
                <el-option label="INFO" value="INFO" />
                <el-option label="WARNING" value="WARNING" />
                <el-option label="ERROR" value="ERROR" />
                <el-option label="DEBUG" value="DEBUG" />
              </el-select>
              <el-button type="primary" size="small" @click="fetchLogs">刷新</el-button>
            </div>
            <div class="logs-content" v-loading="logsLoading">
              <div v-if="logs.length === 0" class="no-logs">
                暂无日志
              </div>
              <div v-else class="log-entries">
                <div 
                  v-for="(log, index) in filteredLogs" 
                  :key="index" 
                  class="log-entry"
                  :class="getLogClass(log.level)"
                >
                  <span class="log-time">{{ formatLogTime(log.timestamp) }}</span>
                  <span class="log-level" :class="getLogClass(log.level)">{{ log.level }}</span>
                  <span class="log-message">{{ log.message }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="抓取数据" name="data" v-if="job.status !== 'pending'">
          <div class="data-container">
            <el-table :data="scrapedItems" v-loading="itemsLoading" style="width: 100%">
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="page_type" label="类型" width="100" />
              <el-table-column prop="url" label="URL" show-overflow-tooltip />
              <el-table-column prop="created_at" label="抓取时间" width="180" />
              <el-table-column label="操作" width="100">
                <template #default="scope">
                  <el-button size="small" @click="viewItemDetail(scope.row)">查看</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="pagination">
              <el-pagination
                background
                layout="prev, pager, next"
                :total="itemsTotal"
                :page-size="itemsPageSize"
                @current-change="handleItemsPageChange"
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    <div v-else class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import JobProgress from './JobProgress.vue'
import * as jobApi from '../api/job'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  jobId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['update:visible'])

// 对话框可见状态
const dialogVisible = ref(false)

// 监听visible属性变化
watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val && props.jobId) {
    fetchJobDetail()
  }
})

// 监听dialogVisible变化，同步更新父组件的visible属性
watch(() => dialogVisible.value, (val) => {
  emit('update:visible', val)
  if (!val) {
    closeWebSocket()
  }
})

// 任务数据
const job = ref(null)
const loading = ref(false)
const activeTab = ref('info')
const configJson = computed(() => {
  if (!job.value || !job.value.config) return '{}'
  return JSON.stringify(job.value.config, null, 2)
})

// 日志数据
const logs = ref([])
const logsLoading = ref(false)
const logLevel = ref('all')

// WebSocket连接
let websocket = null
const websocketConnected = ref(false)
const websocketReconnectAttempts = ref(0)
const maxReconnectAttempts = 5

// 抓取数据
const scrapedItems = ref([])
const itemsLoading = ref(false)
const itemsTotal = ref(0)
const itemsPageSize = ref(10)
const itemsCurrentPage = ref(1)

// 获取任务详情
const fetchJobDetail = async () => {
  if (!props.jobId) return
  
  loading.value = true
  try {
    const response = await jobApi.getJob(props.jobId)
    job.value = response.data
    
    // 如果任务正在运行，定时刷新
    if (job.value.status === 'running') {
      startRefreshTimer()
    }
    
    // 初始加载日志和数据
    if (activeTab.value === 'logs') {
      fetchLogs()
      // 如果任务正在运行，建立WebSocket连接
      if (job.value.status === 'running') {
        connectWebSocket()
      }
    } else if (activeTab.value === 'data') {
      fetchScrapedItems()
    }
  } catch (error) {
    console.error('获取任务详情失败', error)
    ElMessage.error('获取任务详情失败')
    
    // 模拟数据
    job.value = {
      id: props.jobId,
      name: '示例任务',
      site_config: { name: '艺术网站1' },
      status: 'running',
      progress: 65,
      items_scraped: 150,
      items_saved: 145,
      items_failed: 5,
      created_at: '2023-10-15 14:30:00',
      started_at: '2023-10-15 14:31:00',
      runtime_seconds: 3600,
      schedule_type: 'once',
      tenant_id: 'default',
      config: {
        max_depth: 3,
        follow_links: true,
        delay: 1.5
      }
    }
  } finally {
    loading.value = false
  }
}

// 获取任务日志
const fetchLogs = async () => {
  if (!props.jobId) return
  
  logsLoading.value = true
  try {
    const response = await jobApi.getJobLogs(props.jobId, { limit: 100 })
    logs.value = response.data || []
  } catch (error) {
    console.error('获取任务日志失败', error)
    
    // 模拟数据
    logs.value = [
      { timestamp: '2023-10-15T14:31:00', level: 'INFO', message: '任务开始执行' },
      { timestamp: '2023-10-15T14:31:05', level: 'INFO', message: '开始抓取页面: https://example.com/art' },
      { timestamp: '2023-10-15T14:31:10', level: 'INFO', message: '成功解析页面，提取到15个链接' },
      { timestamp: '2023-10-15T14:31:15', level: 'WARNING', message: '页面加载超时，重试中...' },
      { timestamp: '2023-10-15T14:31:20', level: 'ERROR', message: '无法访问页面: https://example.com/art/404' },
      { timestamp: '2023-10-15T14:31:25', level: 'INFO', message: '已保存50个数据项' }
    ]
  } finally {
    logsLoading.value = false
  }
}

// WebSocket连接
const connectWebSocket = () => {
  if (!props.jobId || websocketConnected.value) return
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  const baseUrl = `${protocol}//${host}`
  const wsUrl = `${baseUrl}/api/v1/ws/jobs/${props.jobId}/logs`
  
  try {
    websocket = new WebSocket(wsUrl)
    
    websocket.onopen = () => {
      console.log('WebSocket连接已建立')
      websocketConnected.value = true
      websocketReconnectAttempts.value = 0
      
      // 发送心跳
      startHeartbeat()
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'pong') {
        // 心跳响应
        return
      }
      
      if (data.type === 'connection_established') {
        console.log('WebSocket连接已确认')
        return
      }
      
      // 处理日志消息
      if (data.level && data.message) {
        // 添加新日志到顶部
        logs.value.unshift(data)
        
        // 限制日志数量，避免过多
        if (logs.value.length > 200) {
          logs.value = logs.value.slice(0, 200)
        }
      }
    }
    
    websocket.onclose = () => {
      console.log('WebSocket连接已关闭')
      websocketConnected.value = false
      
      // 如果任务仍在运行，尝试重新连接
      if (job.value && job.value.status === 'running' && websocketReconnectAttempts.value < maxReconnectAttempts) {
        console.log(`尝试重新连接WebSocket (${websocketReconnectAttempts.value + 1}/${maxReconnectAttempts})`)
        websocketReconnectAttempts.value++
        setTimeout(connectWebSocket, 2000) // 2秒后重试
      }
    }
    
    websocket.onerror = (error) => {
      console.error('WebSocket错误:', error)
      websocketConnected.value = false
    }
  } catch (error) {
    console.error('创建WebSocket连接失败:', error)
  }
}

// 关闭WebSocket连接
const closeWebSocket = () => {
  if (websocket) {
    websocket.close()
    websocket = null
    websocketConnected.value = false
  }
}

// 发送心跳
let heartbeatTimer = null
const startHeartbeat = () => {
  stopHeartbeat()
  heartbeatTimer = setInterval(() => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send('ping')
    }
  }, 30000) // 每30秒发送一次心跳
}

const stopHeartbeat = () => {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}

// 获取抓取数据
const fetchScrapedItems = async (page = 1) => {
  if (!props.jobId) return
  
  itemsLoading.value = true
  try {
    // 这里应该调用获取抓取数据的API
    // const response = await apiClient.get(`/jobs/${props.jobId}/items`, {
    //   params: {
    //     skip: (page - 1) * itemsPageSize.value,
    //     limit: itemsPageSize.value
    //   }
    // })
    // scrapedItems.value = response.data.items
    // itemsTotal.value = response.data.total
    
    // 模拟数据
    scrapedItems.value = [
      { id: 1, title: '艺术家1', page_type: 'artist', url: 'https://example.com/artist/1', created_at: '2023-10-15 14:35:00' },
      { id: 2, title: '作品1', page_type: 'artwork', url: 'https://example.com/artwork/1', created_at: '2023-10-15 14:36:00' },
      { id: 3, title: '展览1', page_type: 'exhibition', url: 'https://example.com/exhibition/1', created_at: '2023-10-15 14:37:00' }
    ]
    itemsTotal.value = 3
  } catch (error) {
    console.error('获取抓取数据失败', error)
  } finally {
    itemsLoading.value = false
  }
}

// 处理抓取数据分页变化
const handleItemsPageChange = (page) => {
  itemsCurrentPage.value = page
  fetchScrapedItems(page)
}

// 查看抓取数据详情
const viewItemDetail = (item) => {
  console.log('查看抓取数据详情', item)
}

// 根据日志级别筛选日志
const filteredLogs = computed(() => {
  if (logLevel.value === 'all') {
    return logs.value
  }
  return logs.value.filter(log => log.level === logLevel.value)
})

// 获取日志级别对应的CSS类
const getLogClass = (level) => {
  const classes = {
    'INFO': 'log-info',
    'WARNING': 'log-warning',
    'ERROR': 'log-error',
    'DEBUG': 'log-debug'
  }
  return classes[level] || ''
}

// 根据状态获取标签类型
const getStatusType = (status) => {
  const types = {
    'pending': 'info',
    'running': 'primary',
    'completed': 'success',
    'failed': 'danger',
    'cancelled': 'warning'
  }
  return types[status] || 'info'
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 格式化日志时间
const formatLogTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN')
}

// 格式化运行时间
const formatRuntime = (seconds) => {
  if (!seconds) return '-'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60
  
  let result = ''
  if (hours > 0) result += `${hours}小时`
  if (minutes > 0) result += `${minutes}分钟`
  if (remainingSeconds > 0 || result === '') result += `${remainingSeconds}秒`
  
  return result
}

// 处理关闭对话框
const handleClose = (done) => {
  stopRefreshTimer()
  closeWebSocket()
  done()
}

// 定时刷新
let refreshTimer = null
const startRefreshTimer = () => {
  stopRefreshTimer()
  refreshTimer = setInterval(() => {
    if (job.value && job.value.status === 'running') {
      fetchJobDetail()
    } else {
      stopRefreshTimer()
    }
  }, 5000) // 每5秒刷新一次
}

const stopRefreshTimer = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 监听标签页切换
watch(() => activeTab.value, (val) => {
  if (val === 'logs') {
    fetchLogs()
    // 如果任务正在运行，建立WebSocket连接
    if (job.value && job.value.status === 'running') {
      connectWebSocket()
    }
  } else if (val === 'data' && scrapedItems.value.length === 0) {
    fetchScrapedItems()
  } else {
    // 如果切换到其他标签，关闭WebSocket连接
    closeWebSocket()
  }
})

// 组件卸载时清除定时器和WebSocket连接
onBeforeUnmount(() => {
  stopRefreshTimer()
  stopHeartbeat()
  closeWebSocket()
})
</script>

<style scoped>
.job-detail {
  padding: 10px;
}

.progress-container,
.config-container {
  margin-top: 20px;
}

h3 {
  font-size: 16px;
  margin-bottom: 10px;
  font-weight: 500;
  color: #333;
}

.logs-container {
  height: 500px;
  display: flex;
  flex-direction: column;
}

.logs-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
  gap: 10px;
}

.logs-content {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  background-color: #f8f8f8;
  font-family: monospace;
}

.no-logs {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #909399;
}

.log-entry {
  padding: 3px 0;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-time {
  margin-right: 10px;
  color: #909399;
}

.log-level {
  margin-right: 10px;
  font-weight: bold;
}

.log-info {
  color: #409EFF;
}

.log-warning {
  color: #E6A23C;
}

.log-error {
  color: #F56C6C;
}

.log-debug {
  color: #909399;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 