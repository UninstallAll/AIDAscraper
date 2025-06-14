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

    <!-- 站点配置对话框 -->
    <site-config-dialog
      v-model:visible="dialogVisible"
      :site-data="currentSite"
      :is-edit="isEdit"
      @created="handleSiteCreated"
      @updated="handleSiteUpdated"
    />

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="30%"
    >
      <span>确定要删除站点 "{{ currentSite.name }}" 吗？此操作不可恢复。</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="deleteLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import SiteConfigDialog from '../components/SiteConfigDialog.vue'
import * as siteApi from '../api/site'

// 路由
const router = useRouter()

// 站点列表
const sites = ref([])
const loading = ref(false)
const total = ref(0)
const pageSize = ref(10)
const currentPage = ref(1)

// 对话框状态
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const deleteLoading = ref(false)
const isEdit = ref(false)
const currentSite = ref({})

// 获取站点列表
const fetchSites = async (page = 1) => {
  loading.value = true
  try {
    const response = await siteApi.getSites({
      skip: (page - 1) * pageSize.value,
      limit: pageSize.value
    })
    sites.value = response.data.items || response.data
    total.value = response.data.total || response.data.length
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
    total.value = sites.value.length
  } finally {
    loading.value = false
  }
}

// 页码变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchSites(page)
}

// 打开添加站点对话框
const openAddDialog = () => {
  isEdit.value = false
  currentSite.value = {}
  dialogVisible.value = true
}

// 编辑站点
const editSite = (site) => {
  isEdit.value = true
  currentSite.value = {...site}
  dialogVisible.value = true
}

// 创建任务
const createJob = (site) => {
  router.push({
    name: 'Jobs',
    query: { 
      site_id: site.id,
      site_name: site.name,
      action: 'create'
    }
  })
}

// 删除站点
const deleteSite = (site) => {
  currentSite.value = site
  deleteDialogVisible.value = true
}

// 确认删除
const confirmDelete = async () => {
  deleteLoading.value = true
  try {
    await siteApi.deleteSite(currentSite.value.id)
    ElMessage.success('站点删除成功')
    fetchSites(currentPage.value)
    deleteDialogVisible.value = false
  } catch (error) {
    console.error('删除站点失败', error)
    ElMessage.error(error.response?.data?.detail || '删除站点失败')
  } finally {
    deleteLoading.value = false
  }
}

// 处理站点创建成功
const handleSiteCreated = () => {
  fetchSites(currentPage.value)
  ElMessage.success('站点创建成功')
}

// 处理站点更新成功
const handleSiteUpdated = () => {
  fetchSites(currentPage.value)
  ElMessage.success('站点更新成功')
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style> 