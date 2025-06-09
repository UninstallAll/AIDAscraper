<template>
  <div class="scraper-status-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>爬虫任务状态</span>
          <el-button type="primary" @click="createNewTask">新建爬虫任务</el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="运行中任务" name="running">
          <el-table :data="runningTasks" style="width: 100%" v-loading="loading">
            <el-table-column prop="id" label="任务ID" width="80" />
            <el-table-column prop="target" label="目标网站" />
            <el-table-column prop="startTime" label="开始时间" />
            <el-table-column prop="progress" label="进度">
              <template #default="scope">
                <el-progress :percentage="scope.row.progress" :status="getProgressStatus(scope.row.progress)"></el-progress>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button type="warning" size="small" @click="pauseTask(scope.row.id)">暂停</el-button>
                <el-button type="danger" size="small" @click="stopTask(scope.row.id)">停止</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="已完成任务" name="completed">
          <el-table :data="completedTasks" style="width: 100%" v-loading="loading">
            <el-table-column prop="id" label="任务ID" width="80" />
            <el-table-column prop="target" label="目标网站" />
            <el-table-column prop="startTime" label="开始时间" />
            <el-table-column prop="endTime" label="结束时间" />
            <el-table-column prop="itemsScraped" label="采集数量" />
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button type="info" size="small" @click="viewTaskDetails(scope.row.id)">详情</el-button>
                <el-button type="success" size="small" @click="restartTask(scope.row.id)">重新运行</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 新建任务对话框 -->
    <el-dialog v-model="dialogVisible" title="新建爬虫任务" width="500px">
      <el-form :model="newTaskForm" label-width="120px">
        <el-form-item label="目标网站">
          <el-select v-model="newTaskForm.target" placeholder="选择目标网站" style="width: 100%">
            <el-option v-for="site in targetSites" :key="site.value" :label="site.label" :value="site.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="采集深度">
          <el-slider v-model="newTaskForm.depth" :min="1" :max="5" :step="1" show-stops />
        </el-form-item>
        <el-form-item label="并发数">
          <el-input-number v-model="newTaskForm.concurrency" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="数量限制">
          <el-input-number v-model="newTaskForm.limit" :min="0" :max="10000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitNewTask">创建</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('running')
const loading = ref(false)
const runningTasks = ref([])
const completedTasks = ref([])
const dialogVisible = ref(false)
const newTaskForm = ref({
  target: '',
  depth: 2,
  concurrency: 2,
  limit: 1000
})

// 可选择的目标网站
const targetSites = [
  { label: '卢浮宫官网', value: 'louvre' },
  { label: '大都会艺术博物馆', value: 'met' },
  { label: '故宫博物院', value: 'palace-museum' },
  { label: '泰特美术馆', value: 'tate' },
  { label: '梵高博物馆', value: 'vangogh-museum' }
]

const getProgressStatus = (progress) => {
  if (progress < 30) return 'exception'
  if (progress < 70) return ''
  return 'success'
}

const getStatusType = (status) => {
  const statusMap = {
    '运行中': 'primary',
    '已完成': 'success',
    '已停止': 'info',
    '出错': 'danger',
    '暂停': 'warning'
  }
  return statusMap[status] || 'info'
}

// 模拟加载任务数据
const loadTasks = () => {
  loading.value = true
  
  // 模拟API请求
  setTimeout(() => {
    runningTasks.value = [
      { id: 1, target: '卢浮宫官网', startTime: '2025-06-08 12:30:45', progress: 75, status: '运行中' },
      { id: 2, target: '大都会艺术博物馆', startTime: '2025-06-08 14:20:10', progress: 23, status: '运行中' }
    ]
    
    completedTasks.value = [
      { id: 3, target: '故宫博物院', startTime: '2025-06-07 09:15:30', endTime: '2025-06-07 11:45:22', itemsScraped: 532, status: '已完成' },
      { id: 4, target: '泰特美术馆', startTime: '2025-06-06 16:30:00', endTime: '2025-06-06 18:12:45', itemsScraped: 245, status: '已完成' },
      { id: 5, target: '梵高博物馆', startTime: '2025-06-05 10:00:15', endTime: '2025-06-05 10:35:50', itemsScraped: 98, status: '已停止' }
    ]
    
    loading.value = false
  }, 500)
}

// 打开新建任务对话框
const createNewTask = () => {
  dialogVisible.value = true
}

// 提交新任务
const submitNewTask = () => {
  console.log('创建新任务:', newTaskForm.value)
  ElMessage.success(`成功创建针对 ${newTaskForm.value.target} 的爬虫任务`)
  dialogVisible.value = false
  
  // 模拟添加新任务
  const newTask = {
    id: Math.floor(Math.random() * 1000) + 10,
    target: targetSites.find(site => site.value === newTaskForm.value.target)?.label || newTaskForm.value.target,
    startTime: new Date().toLocaleString(),
    progress: 0,
    status: '运行中'
  }
  
  runningTasks.value.unshift(newTask)
}

// 暂停任务
const pauseTask = (id) => {
  ElMessage.warning(`任务 #${id} 已暂停`)
  const task = runningTasks.value.find(t => t.id === id)
  if (task) {
    task.status = '暂停'
  }
}

// 停止任务
const stopTask = (id) => {
  ElMessage.info(`任务 #${id} 已停止`)
  runningTasks.value = runningTasks.value.filter(t => t.id !== id)
  
  // 模拟将任务移动到已完成列表
  const task = runningTasks.value.find(t => t.id === id)
  if (task) {
    completedTasks.value.unshift({
      ...task,
      endTime: new Date().toLocaleString(),
      itemsScraped: Math.floor(task.progress * 10),
      status: '已停止'
    })
  }
}

// 查看任务详情
const viewTaskDetails = (id) => {
  console.log('查看任务详情:', id)
  ElMessage.info(`查看任务 #${id} 的详细信息`)
}

// 重新运行任务
const restartTask = (id) => {
  ElMessage.success(`任务 #${id} 已重新启动`)
  
  // 模拟重启任务
  const task = completedTasks.value.find(t => t.id === id)
  if (task) {
    const newTask = {
      ...task,
      startTime: new Date().toLocaleString(),
      progress: 0,
      status: '运行中'
    }
    
    runningTasks.value.unshift(newTask)
    completedTasks.value = completedTasks.value.filter(t => t.id !== id)
  }
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.scraper-status-container {
  padding: 20px;
}
</style> 