<template>
  <div class="job-progress">
    <div class="status-container">
      <div class="status-label">
        <el-tag :type="statusType" size="small">{{ job.status }}</el-tag>
      </div>
      <div class="time-info">
        <span v-if="job.started_at">
          开始: {{ formatDate(job.started_at) }}
        </span>
        <span v-if="job.completed_at">
          完成: {{ formatDate(job.completed_at) }}
        </span>
      </div>
    </div>

    <el-progress 
      :percentage="job.progress" 
      :status="progressStatus"
      :stroke-width="strokeWidth"
      :text-inside="textInside"
      :format="formatProgress"
    />
    
    <div class="stats-container" v-if="showStats">
      <div class="stat-item">
        <div class="stat-label">已抓取</div>
        <div class="stat-value">{{ job.items_scraped }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">已保存</div>
        <div class="stat-value">{{ job.items_saved }}</div>
      </div>
      <div class="stat-item" v-if="job.items_failed">
        <div class="stat-label">失败</div>
        <div class="stat-value">{{ job.items_failed }}</div>
      </div>
      <div class="stat-item" v-if="job.runtime_seconds">
        <div class="stat-label">运行时间</div>
        <div class="stat-value">{{ formatRuntime(job.runtime_seconds) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  job: {
    type: Object,
    required: true
  },
  strokeWidth: {
    type: Number,
    default: 6
  },
  textInside: {
    type: Boolean,
    default: false
  },
  showStats: {
    type: Boolean,
    default: true
  }
})

// 根据状态计算标签类型
const statusType = computed(() => {
  const types = {
    'pending': 'info',
    'running': 'primary',
    'completed': 'success',
    'failed': 'danger',
    'cancelled': 'warning'
  }
  return types[props.job.status] || 'info'
})

// 根据状态计算进度条状态
const progressStatus = computed(() => {
  if (props.job.status === 'completed') return 'success'
  if (props.job.status === 'failed') return 'exception'
  if (props.job.status === 'cancelled') return 'warning'
  return ''
})

// 格式化进度显示
const formatProgress = (percentage) => {
  if (props.job.status === 'running') {
    return `${percentage}%`
  }
  return percentage === 100 ? '完成' : `${percentage}%`
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', { 
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化运行时间
const formatRuntime = (seconds) => {
  if (!seconds) return '0秒'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60
  
  let result = ''
  if (hours > 0) result += `${hours}小时`
  if (minutes > 0) result += `${minutes}分钟`
  if (remainingSeconds > 0 || result === '') result += `${remainingSeconds}秒`
  
  return result
}
</script>

<style scoped>
.job-progress {
  margin: 15px 0;
}

.status-container {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.time-info {
  font-size: 12px;
  color: #666;
}

.time-info span {
  margin-left: 10px;
}

.stats-container {
  display: flex;
  margin-top: 10px;
  flex-wrap: wrap;
}

.stat-item {
  margin-right: 20px;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

.stat-value {
  font-size: 14px;
  font-weight: 500;
}
</style> 