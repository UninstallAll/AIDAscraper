<template>
  <div class="jobs-container">
    <div class="page-header">
      <h2>爬虫任务</h2>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><el-icon-plus /></el-icon>
        创建任务
      </el-button>
    </div>
    
    <div class="filters">
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 120px">
        <el-option label="全部" value="" />
        <el-option label="待处理" value="pending" />
        <el-option label="运行中" value="running" />
        <el-option label="已完成" value="completed" />
        <el-option label="失败" value="failed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      
      <el-select 
        v-model="filterSite" 
        placeholder="站点筛选" 
        clearable 
        filterable
        style="width: 200px; margin-left: 10px"
      >
        <el-option label="全部" value="" />
        <el-option
          v-for="site in sites"
          :key="site.id"
          :label="site.name"
          :value="site.id"
        />
      </el-select>
      
      <el-button type="primary" plain @click="fetchJobs(1)" style="margin-left: 10px">
        筛选
      </el-button>
    </div>
    
    <el-table :data="jobs" v-loading="loading" style="width: 100%">
      <el-table-column prop="name" label="任务名称" min-width="180" />
      <el-table-column prop="site_config.name" label="站点" min-width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="进度" min-width="280">
        <template #default="scope">
          <job-progress :job="scope.row" :text-inside="true" :show-stats="false" />
        </template>
      </el-table-column>
      <el-table-column prop="items_scraped" label="已抓取" width="100" align="center" />
      <el-table-column prop="items_saved" label="已保存" width="100" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="scope">
          <el-button 
            size="small" 
            :disabled="!canStart(scope.row.status)"
            @click="startJob(scope.row)"
          >
            启动
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            :disabled="!canCancel(scope.row.status)"
            @click="cancelJob(scope.row)"
          >
            取消
          </el-button>
          <el-button size="small" type="info" @click="viewDetails(scope.row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- 任务创建对话框 -->
    <job-create-dialog
      v-model:visible="createDialogVisible"
      :site-id="selectedSiteId"
      @created="handleJobCreated"
    />
    
    <!-- 任务详情对话框 -->
    <job-detail-dialog
      v-model:visible="detailDialogVisible"
      :job-id="selectedJobId"
    />
    
    <!-- 确认对话框 -->
    <el-dialog
      v-model="confirmDialogVisible"
      :title="confirmDialogTitle"
      width="30%"
    >
      <span>{{ confirmDialogMessage }}</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="confirmDialogVisible = false">取消</el-button>
          <el-button 
            :type="confirmDialogType" 
            @click="confirmAction" 
            :loading="confirmLoading"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import JobProgress from '../components/JobProgress.vue'
import JobDetailDialog from '../components/JobDetailDialog.vue'
import JobCreateDialog from '../components/JobCreateDialog.vue'
import * as jobApi from '../api/job'
import * as siteApi from '../api/site'

// 路由
const route = useRoute()

// 任务列表
const jobs = ref([])
const loading = ref(false)
const total = ref(0)
const pageSize = ref(10)
const currentPage = ref(1)

// 站点列表
const sites = ref([])

// 筛选条件
const filterStatus = ref('')
const filterSite = ref('')

// 对话框状态
const createDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const confirmDialogVisible = ref(false)
const confirmDialogTitle = ref('')
const confirmDialogMessage = ref('')
const confirmDialogType = ref('primary')
const confirmLoading = ref(false)
const selectedJobId = ref(null)
const selectedSiteId = ref(null)
let confirmCallback = null

// 自动刷新定时器
let refreshTimer = null

// 获取任务列表
const fetchJobs = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      skip: (page - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    // 添加筛选条件
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    
    if (filterSite.value) {
      params.site_config_id = filterSite.value
    }
    
    const response = await jobApi.getJobs(params)
    jobs.value = response.data.items || response.data
    total.value = response.data.total || response.data.length
  } catch (error) {
    console.error('获取任务列表失败', error)
    // 模拟数据
    jobs.value = [
      {
        id: 1,
        name: '示例任务1',
        site_config: { name: '艺术网站1' },
        status: 'running',
        progress: 45,
        items_scraped: 120,
        items_saved: 115,
        created_at: '2023-10-15 14:30:00'
      },
      {
        id: 2,
        name: '示例任务2',
        site_config: { name: '艺术网站2' },
        status: 'completed',
        progress: 100,
        items_scraped: 350,
        items_saved: 348,
        created_at: '2023-10-14 09:15:00'
      },
      {
        id: 3,
        name: '示例任务3',
        site_config: { name: '艺术网站3' },
        status: 'failed',
        progress: 23,
        items_scraped: 45,
        items_saved: 42,
        created_at: '2023-10-13 16:45:00'
      },
      {
        id: 4,
        name: '示例任务4',
        site_config: { name: '艺术网站1' },
        status: 'pending',
        progress: 0,
        items_scraped: 0,
        items_saved: 0,
        created_at: '2023-10-16 10:00:00'
      }
    ]
    total.value = jobs.value.length
  } finally {
    loading.value = false
  }
}

// 获取站点列表
const fetchSites = async () => {
  try {
    const response = await siteApi.getSites({ limit: 100 })
    sites.value = response.data.items || response.data
  } catch (error) {
    console.error('获取站点列表失败', error)
    // 模拟数据
    sites.value = [
      { id: 1, name: '艺术网站1' },
      { id: 2, name: '艺术网站2' },
      { id: 3, name: '艺术网站3' }
    ]
  }
}

// 页码变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchJobs(page)
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

// 判断是否可以启动任务
const canStart = (status) => {
  return ['pending', 'failed', 'cancelled'].includes(status)
}

// 判断是否可以取消任务
const canCancel = (status) => {
  return ['pending', 'running'].includes(status)
}

// 打开创建任务对话框
const openAddDialog = () => {
  selectedSiteId.value = filterSite.value || null
  createDialogVisible.value = true
}

// 启动任务
const startJob = (job) => {
  confirmDialogTitle.value = '启动任务'
  confirmDialogMessage.value = `确定要启动任务 "${job.name}" 吗？`
  confirmDialogType.value = 'primary'
  confirmDialogVisible.value = true
  confirmCallback = async () => {
    confirmLoading.value = true
    try {
      await jobApi.startJob(job.id)
      ElMessage.success('任务启动成功')
      fetchJobs(currentPage.value)
    } catch (error) {
      console.error('启动任务失败', error)
      ElMessage.error('启动任务失败')
    } finally {
      confirmLoading.value = false
      confirmDialogVisible.value = false
    }
  }
}

// 取消任务
const cancelJob = (job) => {
  confirmDialogTitle.value = '取消任务'
  confirmDialogMessage.value = `确定要取消任务 "${job.name}" 吗？`
  confirmDialogType.value = 'danger'
  confirmDialogVisible.value = true
  confirmCallback = async () => {
    confirmLoading.value = true
    try {
      await jobApi.cancelJob(job.id)
      ElMessage.success('任务取消成功')
      fetchJobs(currentPage.value)
    } catch (error) {
      console.error('取消任务失败', error)
      ElMessage.error('取消任务失败')
    } finally {
      confirmLoading.value = false
      confirmDialogVisible.value = false
    }
  }
}

// 查看任务详情
const viewDetails = (job) => {
  selectedJobId.value = job.id
  detailDialogVisible.value = true
}

// 确认对话框操作
const confirmAction = () => {
  if (confirmCallback) {
    confirmCallback()
  }
}

// 处理任务创建成功
const handleJobCreated = (job) => {
  ElMessage.success('任务创建成功')
  fetchJobs(1)
}

// 启动自动刷新
const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer = setInterval(() => {
    // 只有当有运行中的任务时才自动刷新
    const hasRunningJobs = jobs.value.some(job => job.status === 'running')
    if (hasRunningJobs) {
      fetchJobs(currentPage.value)
    }
  }, 10000) // 每10秒刷新一次
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 检查URL参数
const checkUrlParams = () => {
  if (route.query.site_id) {
    filterSite.value = route.query.site_id
  }
  
  if (route.query.action === 'create') {
    selectedSiteId.value = route.query.site_id || null
    createDialogVisible.value = true
  }
}

onMounted(() => {
  fetchJobs()
  fetchSites()
  checkUrlParams()
  startAutoRefresh()
})

onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.jobs-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style> 