<template>
  <div class="artist-list-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>艺术家列表</span>
          <div>
            <el-input
              v-model="searchQuery"
              placeholder="搜索艺术家"
              class="search-input"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch"></el-button>
              </template>
            </el-input>
          </div>
        </div>
      </template>
      
      <el-table :data="artists" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="country" label="国家" />
        <el-table-column prop="birthYear" label="出生年份" />
        <el-table-column prop="deathYear" label="逝世年份" />
        <el-table-column prop="artworksCount" label="作品数量" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-button type="text" size="small">查看作品</el-button>
            <el-button type="text" size="small">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'

const searchQuery = ref('')
const artists = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 模拟数据
const loadArtists = () => {
  loading.value = true
  
  // 模拟API请求
  setTimeout(() => {
    artists.value = [
      { id: 1, name: '达芬奇', country: '意大利', birthYear: 1452, deathYear: 1519, artworksCount: 34 },
      { id: 2, name: '梵高', country: '荷兰', birthYear: 1853, deathYear: 1890, artworksCount: 215 },
      { id: 3, name: '莫奈', country: '法国', birthYear: 1840, deathYear: 1926, artworksCount: 123 },
      { id: 4, name: '毕加索', country: '西班牙', birthYear: 1881, deathYear: 1973, artworksCount: 321 },
      { id: 5, name: '草间弥生', country: '日本', birthYear: 1929, deathYear: null, artworksCount: 98 }
    ]
    total.value = 135
    loading.value = false
  }, 500)
}

const handleSearch = () => {
  currentPage.value = 1
  loadArtists()
}

const handlePageChange = (page) => {
  loadArtists()
}

onMounted(() => {
  loadArtists()
})
</script>

<style scoped>
.artist-list-container {
  padding: 20px;
}

.search-input {
  width: 300px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 