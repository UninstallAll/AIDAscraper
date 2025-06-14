<template>
  <div class="jobs-container">
    <div class="page-header">
      <h2>爬虫任务</h2>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><el-icon-plus /></el-icon>
        创建任务
      </el-button>
    </div>
    
    <el-table :data="jobs" v-loading="loading" style="width: 100%">
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="site_config.name" label="站点" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="progress" label="进度">
        <template #default="scope">
          <el-progress :percentage="scope.row.progress" />
        </template>
      </el-table-column>
      <el-table-column prop="items_scraped" label="已抓取" />
      <el-table-column prop="items_saved" label="已保存" />
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作" width="180">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '../api/config'

// 任务列表
const jobs = ref([])
const loading = ref(false)
const total = ref(0)
const pageSize = ref(10)
const currentPage = ref(1)

// 获取任务列表
const fetchJobs = async (page = 1) => {
  loading.value = true
  try {
    const response = await apiClient.get('/jobs', {
      params: {
        skip: (page - 1) * pageSize.value,
        limit: pageSize.value
      }
    })
    jobs.value = response.data
    // 假设总数通过响应头或其他方式获取
    total.value = 100 // 示例值
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
    total.value = 4
  } finally {
    loading.value = false
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

// 创建任务对话框
const openAddDialog = () => {
  // 实际项目中这里应该打开一个对话框
  console.log('打开创建任务对话框')
}

// 启动任务
const startJob = (job) => {
  console.log('启动任务', job)
}

// 取消任务
const cancelJob = (job) => {
  console.log('取消任务', job)
}

// 查看任务详情
const viewDetails = (job) => {
  console.log('查看任务详情', job)
}

onMounted(() => {
  fetchJobs()
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

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 