<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-header">
            <div class="stat-title">站点数量</div>
            <el-icon class="stat-icon"><el-icon-connection /></el-icon>
          </div>
          <div class="stat-value">{{ stats.sites || 0 }}</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-header">
            <div class="stat-title">爬虫任务</div>
            <el-icon class="stat-icon"><el-icon-monitor /></el-icon>
          </div>
          <div class="stat-value">{{ stats.jobs || 0 }}</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-header">
            <div class="stat-title">已抓取数据</div>
            <el-icon class="stat-icon"><el-icon-document /></el-icon>
          </div>
          <div class="stat-value">{{ stats.items || 0 }}</div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-header">
            <div class="stat-title">运行中任务</div>
            <el-icon class="stat-icon"><el-icon-loading /></el-icon>
          </div>
          <div class="stat-value">{{ stats.runningJobs || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近任务 -->
    <el-card class="recent-jobs" header="最近任务">
      <el-table :data="recentJobs" stripe style="width: 100%">
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
        <el-table-column prop="created_at" label="创建时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '../api/config'

// 统计数据
const stats = ref({
  sites: 0,
  jobs: 0,
  items: 0,
  runningJobs: 0
})

// 最近任务
const recentJobs = ref([])

// 获取仪表盘数据
const fetchDashboardData = async () => {
  try {
    // 这里假设后端有一个仪表盘API
    // 实际项目中可能需要分别调用不同的API
    const response = await apiClient.get('/dashboard')
    stats.value = response.data.stats
    recentJobs.value = response.data.recent_jobs
  } catch (error) {
    console.error('获取仪表盘数据失败', error)
    
    // 模拟数据（实际项目中应该删除这部分）
    stats.value = {
      sites: 5,
      jobs: 12,
      items: 1024,
      runningJobs: 2
    }
    
    recentJobs.value = [
      {
        name: '示例任务1',
        site_config: { name: '艺术网站1' },
        status: 'running',
        progress: 45,
        created_at: '2023-10-15 14:30:00'
      },
      {
        name: '示例任务2',
        site_config: { name: '艺术网站2' },
        status: 'completed',
        progress: 100,
        created_at: '2023-10-14 09:15:00'
      },
      {
        name: '示例任务3',
        site_config: { name: '艺术网站3' },
        status: 'failed',
        progress: 23,
        created_at: '2023-10-13 16:45:00'
      }
    ]
  }
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

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dashboard-container {
  padding: 10px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.stat-title {
  font-size: 16px;
  color: #606266;
}

.stat-icon {
  font-size: 24px;
  color: #409EFF;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.recent-jobs {
  margin-top: 20px;
}
</style> 