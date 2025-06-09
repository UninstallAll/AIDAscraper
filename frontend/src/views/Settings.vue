<template>
  <div class="settings-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>Application Settings</span>
          <el-button type="primary" @click="saveSettings">Save Settings</el-button>
        </div>
      </template>
      
      <el-form :model="settingsForm" label-width="180px" label-position="left">
        <el-form-item label="Theme">
          <el-select v-model="settingsForm.theme" placeholder="Select application theme">
            <el-option label="Light" value="light" />
            <el-option label="Dark" value="dark" />
            <el-option label="System Default" value="system" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Language">
          <el-select v-model="settingsForm.language" placeholder="Select application language">
            <el-option label="English" value="en" />
            <el-option label="Chinese" value="zh" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Timezone">
          <el-select v-model="settingsForm.timezone" placeholder="Select timezone" filterable>
            <el-option v-for="tz in timezones" :key="tz.value" :label="tz.label" :value="tz.value" />
          </el-select>
        </el-form-item>
        
        <el-divider>Notifications</el-divider>
        
        <el-form-item label="Enable Notifications">
          <el-switch v-model="settingsForm.enableNotifications" />
        </el-form-item>
        
        <el-form-item label="Notify on Task Completion" v-if="settingsForm.enableNotifications">
          <el-switch v-model="settingsForm.notifyTaskCompletion" />
        </el-form-item>
        
        <el-form-item label="Notify on Task Error" v-if="settingsForm.enableNotifications">
          <el-switch v-model="settingsForm.notifyTaskError" />
        </el-form-item>
        
        <el-divider>System</el-divider>
        
        <el-form-item label="API URL">
          <el-input v-model="settingsForm.apiUrl" placeholder="API server URL" />
        </el-form-item>
        
        <el-form-item label="Data Refresh Interval">
          <el-select v-model="settingsForm.refreshInterval" placeholder="Select refresh interval">
            <el-option label="5 seconds" value="5" />
            <el-option label="10 seconds" value="10" />
            <el-option label="30 seconds" value="30" />
            <el-option label="1 minute" value="60" />
            <el-option label="5 minutes" value="300" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Default Items Per Page">
          <el-input-number v-model="settingsForm.itemsPerPage" :min="5" :max="100" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

// Form data
const settingsForm = ref({
  theme: 'light',
  language: 'en',
  timezone: 'UTC',
  enableNotifications: true,
  notifyTaskCompletion: true,
  notifyTaskError: true,
  apiUrl: 'http://localhost:8000',
  refreshInterval: '30',
  itemsPerPage: 20
});

// Sample timezone data
const timezones = [
  { label: 'UTC (Coordinated Universal Time)', value: 'UTC' },
  { label: 'America/New_York (Eastern Time)', value: 'America/New_York' },
  { label: 'America/Chicago (Central Time)', value: 'America/Chicago' },
  { label: 'America/Denver (Mountain Time)', value: 'America/Denver' },
  { label: 'America/Los_Angeles (Pacific Time)', value: 'America/Los_Angeles' },
  { label: 'Europe/London (Greenwich Mean Time)', value: 'Europe/London' },
  { label: 'Europe/Paris (Central European Time)', value: 'Europe/Paris' },
  { label: 'Asia/Tokyo (Japan Standard Time)', value: 'Asia/Tokyo' },
  { label: 'Asia/Shanghai (China Standard Time)', value: 'Asia/Shanghai' },
  { label: 'Asia/Hong_Kong (Hong Kong Time)', value: 'Asia/Hong_Kong' },
  { label: 'Australia/Sydney (Australian Eastern Time)', value: 'Australia/Sydney' }
];

// Load settings
const loadSettings = async () => {
  try {
    // In a real app, you would load from API or localStorage
    // const response = await api.settings.get();
    // settingsForm.value = response.data;
    
    // For now, try to load from localStorage
    const savedSettings = localStorage.getItem('appSettings');
    if (savedSettings) {
      settingsForm.value = JSON.parse(savedSettings);
      ElMessage.success('Settings loaded');
    }
  } catch (error) {
    console.error('Failed to load settings:', error);
  }
};

// Save settings
const saveSettings = async () => {
  try {
    // In a real app, you would save to API
    // await api.settings.save(settingsForm.value);
    
    // For now, save to localStorage
    localStorage.setItem('appSettings', JSON.stringify(settingsForm.value));
    ElMessage.success('Settings saved successfully');
  } catch (error) {
    ElMessage.error('Failed to save settings');
    console.error(error);
  }
};

onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.el-divider {
  margin: 20px 0;
}
</style> 