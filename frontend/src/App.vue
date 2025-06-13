<template>
  <div class="app-container">
    <el-container class="layout-container">
      <el-aside width="240px" class="sidebar">
        <div class="logo">
          <h2>ArtScraper</h2>
        </div>
        <el-menu
          router
          :default-active="$route.path"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#fff"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>Dashboard</span>
          </el-menu-item>
          
          <el-sub-menu index="/scrapers">
            <template #title>
              <el-icon><Connection /></el-icon>
              <span>Scrapers</span>
            </template>
            <el-menu-item index="/scraper-status">
              <el-icon><Loading /></el-icon>
              <span>Tasks & Status</span>
            </el-menu-item>
            <el-menu-item index="/scraper-config">
              <el-icon><Setting /></el-icon>
              <span>Configuration</span>
            </el-menu-item>
            <el-menu-item index="/website-manager">
              <el-icon><Management /></el-icon>
              <span>Website Manager</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="/data">
            <template #title>
              <el-icon><DataAnalysis /></el-icon>
              <span>Scraped Data</span>
            </template>
            <el-menu-item index="/artists">
              <el-icon><User /></el-icon>
              <span>Artists</span>
            </el-menu-item>
            <el-menu-item index="/artworks">
              <el-icon><Picture /></el-icon>
              <span>Artworks</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>Settings</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-container class="main-container">
        <el-header class="header">
          <div class="header-left">
            <el-icon class="toggle-sidebar-btn" @click="toggleSidebar"><Fold /></el-icon>
          </div>
          <div class="header-right">
            <el-dropdown>
              <span class="user-dropdown">
                Admin <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>Profile</el-dropdown-item>
                  <el-dropdown-item>Logout</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { 
  Monitor, 
  Connection, 
  Loading, 
  Setting, 
  DataAnalysis, 
  User, 
  Picture,
  Fold,
  ArrowDown,
  Management
} from '@element-plus/icons-vue';

const isCollapsed = ref(false);

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};
</script>

<style>
.app-container {
  height: 100%;
  width: 100%;
}

.layout-container {
  height: 100%;
}

.sidebar {
  background-color: #304156;
  color: white;
  height: 100%;
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border-bottom: 1px solid #1f2d3d;
}

.el-menu-vertical {
  border-right: none;
}

.header {
  background-color: #fff;
  color: #333;
  line-height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e6e6e6;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
}

.toggle-sidebar-btn {
  font-size: 20px;
  cursor: pointer;
  margin-right: 15px;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.main-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-content {
  padding: 20px;
  height: calc(100% - 60px);
  overflow-y: auto;
}
</style> 