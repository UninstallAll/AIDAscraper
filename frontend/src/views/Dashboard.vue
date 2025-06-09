<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <h1>艺术数据管理系统</h1>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-20">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>艺术家数量</span>
              <el-button type="text">查看全部</el-button>
            </div>
          </template>
          <div class="card-body">
            <div class="statistic-value">{{ artistCount }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>艺术品数量</span>
              <el-button type="text">查看全部</el-button>
            </div>
          </template>
          <div class="card-body">
            <div class="statistic-value">{{ artworkCount }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>爬虫任务</span>
              <el-button type="text">管理</el-button>
            </div>
          </template>
          <div class="card-body">
            <div class="statistic-value">{{ scraperTaskCount }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>数据来源</span>
              <el-button type="text">详情</el-button>
            </div>
          </template>
          <div class="card-body">
            <div class="statistic-value">{{ dataSourceCount }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>最近爬取的数据</span>
              <el-button type="primary" size="small">启动新任务</el-button>
            </div>
          </template>
          <el-table :data="recentData" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="source" label="来源" />
            <el-table-column prop="type" label="类型" />
            <el-table-column prop="createdAt" label="爬取时间" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-button type="text" size="small">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 统计数据
const artistCount = ref(0)
const artworkCount = ref(0)
const scraperTaskCount = ref(0)
const dataSourceCount = ref(0)
const recentData = ref([])

// 模拟数据
const loadDashboardData = () => {
  // 模拟API请求
  setTimeout(() => {
    artistCount.value = 1250
    artworkCount.value = 5678
    scraperTaskCount.value = 12
    dataSourceCount.value = 8
    
    recentData.value = [
      { id: 1, name: '蒙娜丽莎', source: '卢浮宫', type: '绘画', createdAt: '2025-06-08 14:30:22' },
      { id: 2, name: '维纳斯的诞生', source: '乌菲兹美术馆', type: '绘画', createdAt: '2025-06-08 13:45:10' },
      { id: 3, name: '最后的晚餐', source: '圣玛丽亚修道院', type: '壁画', createdAt: '2025-06-08 12:10:45' },
      { id: 4, name: '大卫', source: '佛罗伦萨学院美术馆', type: '雕塑', createdAt: '2025-06-08 10:25:33' },
      { id: 5, name: '向日葵', source: '梵高博物馆', type: '绘画', createdAt: '2025-06-08 09:18:56' }
    ]
  }, 500)
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.box-card {
  margin-bottom: 20px;
}

.statistic-value {
  font-size: 28px;
  font-weight: bold;
  text-align: center;
  color: #409EFF;
}

.card-body {
  padding: 20px 0;
}
</style> 