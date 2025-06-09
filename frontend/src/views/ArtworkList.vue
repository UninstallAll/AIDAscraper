<template>
  <div class="artwork-list-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>艺术品列表</span>
          <div>
            <el-input
              v-model="searchQuery"
              placeholder="搜索艺术品"
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
      
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="artwork in artworks" :key="artwork.id">
          <el-card class="artwork-card" shadow="hover">
            <template #header>
              <div class="artwork-title">{{ artwork.title }}</div>
            </template>
            <div class="artwork-image-container">
              <el-image :src="artwork.imageUrl" fit="cover" class="artwork-image" :preview-src-list="[artwork.imageUrl]"></el-image>
            </div>
            <div class="artwork-info">
              <div><strong>艺术家:</strong> {{ artwork.artist }}</div>
              <div><strong>年份:</strong> {{ artwork.year }}</div>
              <div><strong>类型:</strong> {{ artwork.type }}</div>
              <div><strong>尺寸:</strong> {{ artwork.dimensions }}</div>
            </div>
            <div class="artwork-actions">
              <el-button type="primary" size="small" @click="viewArtworkDetails(artwork.id)">查看详情</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
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
const artworks = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 模拟数据
const loadArtworks = () => {
  loading.value = true
  
  // 模拟API请求
  setTimeout(() => {
    artworks.value = [
      { id: 1, title: '蒙娜丽莎', artist: '达芬奇', year: '1503-1519', type: '肖像画', dimensions: '77 × 53 cm', imageUrl: 'https://placehold.co/300x400' },
      { id: 2, title: '星夜', artist: '梵高', year: '1889', type: '风景画', dimensions: '73.7 × 92.1 cm', imageUrl: 'https://placehold.co/300x400' },
      { id: 3, title: '日出·印象', artist: '莫奈', year: '1872', type: '风景画', dimensions: '48 × 63 cm', imageUrl: 'https://placehold.co/300x400' },
      { id: 4, title: '戴珍珠耳环的少女', artist: '维米尔', year: '1665', type: '肖像画', dimensions: '44.5 × 39 cm', imageUrl: 'https://placehold.co/300x400' },
      { id: 5, title: '格尔尼卡', artist: '毕加索', year: '1937', type: '历史画', dimensions: '349.3 × 776.6 cm', imageUrl: 'https://placehold.co/300x400' },
      { id: 6, title: '维纳斯的诞生', artist: '波提切利', year: '1486', type: '神话画', dimensions: '172.5 × 278.5 cm', imageUrl: 'https://placehold.co/300x400' }
    ]
    total.value = 254
    loading.value = false
  }, 500)
}

const handleSearch = () => {
  currentPage.value = 1
  loadArtworks()
}

const handlePageChange = (page) => {
  loadArtworks()
}

const viewArtworkDetails = (id) => {
  // 查看详情逻辑
  console.log('查看艺术品详情:', id)
}

onMounted(() => {
  loadArtworks()
})
</script>

<style scoped>
.artwork-list-container {
  padding: 20px;
}

.search-input {
  width: 300px;
}

.artwork-card {
  margin-bottom: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.artwork-title {
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.artwork-image-container {
  height: 200px;
  overflow: hidden;
  margin-bottom: 10px;
}

.artwork-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.artwork-info {
  flex: 1;
  margin-bottom: 10px;
}

.artwork-actions {
  text-align: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 