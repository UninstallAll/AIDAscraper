<template>
  <div class="sites-container">
    <div class="page-header">
      <h2>站点管理</h2>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><el-icon-plus /></el-icon>
        添加站点
      </el-button>
    </div>
    
    <el-table :data="sites" v-loading="loading" style="width: 100%">
      <el-table-column prop="name" label="站点名称" />
      <el-table-column prop="url" label="URL" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="requires_login" label="需要登录">
        <template #default="scope">
          <el-tag :type="scope.row.requires_login ? 'warning' : 'success'">
            {{ scope.row.requires_login ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="use_playwright" label="使用Playwright">
        <template #default="scope">
          <el-tag :type="scope.row.use_playwright ? 'primary' : 'info'">
            {{ scope.row.use_playwright ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="editSite(scope.row)">编辑</el-button>
          <el-button size="small" type="primary" @click="createJob(scope.row)">创建任务</el-button>
          <el-button size="small" type="danger" @click="deleteSite(scope.row)">删除</el-button>
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

// 站点列表
const sites = ref([])
const loading = ref(false)
const total = ref(0)
const pageSize = ref(10)
const currentPage = ref(1)

// 获取站点列表
const fetchSites = async (page = 1) => {
  loading.value = true
  try {
    const response = await apiClient.get('/sites', {
      params: {
        skip: (page - 1) * pageSize.value,
        limit: pageSize.value
      }
    })
    sites.value = response.data
    // 假设总数通过响应头或其他方式获取
    total.value = 100 // 示例值
  } catch (error) {
    console.error('获取站点列表失败', error)
    // 模拟数据
    sites.value = [
      {
        id: 1,
        name: '艺术网站1',
        url: 'https://example.com/art1',
        description: '现代艺术展览信息',
        requires_login: true,
        use_playwright: true
      },
      {
        id: 2,
        name: '艺术网站2',
        url: 'https://example.com/art2',
        description: '艺术家档案和作品集',
        requires_login: false,
        use_playwright: false
      }
    ]
    total.value = 2
  } finally {
    loading.value = false
  }
}

// 页码变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchSites(page)
}

// 添加站点对话框
const openAddDialog = () => {
  // 实际项目中这里应该打开一个对话框
  console.log('打开添加站点对话框')
}

// 编辑站点
const editSite = (site) => {
  console.log('编辑站点', site)
}

// 创建任务
const createJob = (site) => {
  console.log('创建任务', site)
}

// 删除站点
const deleteSite = (site) => {
  console.log('删除站点', site)
}

onMounted(() => {
  fetchSites()
})
</script>

<style scoped>
.sites-container {
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