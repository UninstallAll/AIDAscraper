<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <el-menu
      class="sidebar-menu"
      :default-active="activeMenu"
      :collapse="isCollapse"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <div class="logo-container">
        <span v-if="!isCollapse">AIDA Scraper</span>
        <span v-else>AIDA</span>
      </div>
      
      <el-menu-item index="/">
        <el-icon><el-icon-odometer /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>
      
      <el-menu-item index="/sites">
        <el-icon><el-icon-connection /></el-icon>
        <span>站点管理</span>
      </el-menu-item>
      
      <el-menu-item index="/jobs">
        <el-icon><el-icon-monitor /></el-icon>
        <span>爬虫任务</span>
      </el-menu-item>
    </el-menu>
    
    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-button 
            type="text" 
            @click="toggleSidebar"
            class="toggle-button"
          >
            <el-icon v-if="isCollapse"><el-icon-expand /></el-icon>
            <el-icon v-else><el-icon-fold /></el-icon>
          </el-button>
          <breadcrumb />
        </div>
        
        <div class="header-right">
          <el-dropdown trigger="click">
            <div class="user-info">
              <span>{{ authStore.currentUser?.username }}</span>
              <el-icon><el-icon-arrow-down /></el-icon>
            </div>
            
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="authStore.logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'
import Breadcrumb from '../components/Breadcrumb.vue'

const authStore = useAuthStore()
const route = useRoute()

// 侧边栏折叠状态
const isCollapse = ref(false)

// 当前活动菜单
const activeMenu = computed(() => {
  return route.path
})

// 切换侧边栏
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
}

.sidebar-menu {
  height: 100%;
  width: auto;
  min-height: 100vh;
  transition: width 0.3s;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 210px;
}

.logo-container {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-button {
  padding: 0;
  margin-right: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-info span {
  margin-right: 5px;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}
</style> 