<template>
  <div class="scraper-config-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>Scraper Configuration</span>
          <el-button type="primary" @click="saveConfig">Save Configuration</el-button>
        </div>
      </template>
      
      <el-form :model="configForm" label-width="180px" label-position="left">
        <el-tabs v-model="activeTab">
          <!-- General Settings Tab -->
          <el-tab-pane label="General Settings" name="general">
            <el-form-item label="Default User Agent">
              <el-input v-model="configForm.userAgent" placeholder="User agent string" />
            </el-form-item>
            
            <el-form-item label="Request Timeout (seconds)">
              <el-input-number v-model="configForm.timeout" :min="1" :max="60" />
            </el-form-item>
            
            <el-form-item label="Retry Count">
              <el-input-number v-model="configForm.retryCount" :min="0" :max="10" />
            </el-form-item>
            
            <el-form-item label="Request Delay (ms)">
              <el-input-number v-model="configForm.requestDelay" :min="0" :max="10000" :step="100" />
            </el-form-item>
            
            <el-form-item label="Concurrent Requests">
              <el-input-number v-model="configForm.concurrentRequests" :min="1" :max="20" />
            </el-form-item>
            
            <el-form-item label="Use Random User Agent">
              <el-switch v-model="configForm.useRandomUserAgent" />
            </el-form-item>
          </el-tab-pane>
          
          <!-- Proxy Settings Tab -->
          <el-tab-pane label="Proxy Settings" name="proxy">
            <el-form-item label="Enable Proxy">
              <el-switch v-model="configForm.useProxy" />
            </el-form-item>
            
            <template v-if="configForm.useProxy">
              <el-form-item label="Proxy Type">
                <el-select v-model="configForm.proxyType" placeholder="Select proxy type">
                  <el-option label="HTTP" value="http" />
                  <el-option label="HTTPS" value="https" />
                  <el-option label="SOCKS5" value="socks5" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="Proxy Host">
                <el-input v-model="configForm.proxyHost" placeholder="Proxy host (e.g. 127.0.0.1)" />
              </el-form-item>
              
              <el-form-item label="Proxy Port">
                <el-input-number v-model="configForm.proxyPort" :min="1" :max="65535" />
              </el-form-item>
              
              <el-form-item label="Proxy Authentication">
                <el-switch v-model="configForm.proxyAuth" />
              </el-form-item>
              
              <template v-if="configForm.proxyAuth">
                <el-form-item label="Proxy Username">
                  <el-input v-model="configForm.proxyUsername" placeholder="Username" />
                </el-form-item>
                
                <el-form-item label="Proxy Password">
                  <el-input v-model="configForm.proxyPassword" type="password" placeholder="Password" show-password />
                </el-form-item>
              </template>
            </template>
          </el-tab-pane>
          
          <!-- Storage Settings Tab -->
          <el-tab-pane label="Storage Settings" name="storage">
            <el-form-item label="Database Type">
              <el-select v-model="configForm.dbType" placeholder="Select database type">
                <el-option label="MongoDB" value="mongodb" />
                <el-option label="PostgreSQL" value="postgresql" />
                <el-option label="SQLite" value="sqlite" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Connection String" v-if="configForm.dbType !== 'sqlite'">
              <el-input v-model="configForm.dbConnectionString" placeholder="Database connection string" />
            </el-form-item>
            
            <el-form-item label="Database Path" v-if="configForm.dbType === 'sqlite'">
              <el-input v-model="configForm.dbPath" placeholder="Path to SQLite database file" />
            </el-form-item>
            
            <el-form-item label="Save Media Files">
              <el-switch v-model="configForm.saveMediaFiles" />
            </el-form-item>
            
            <el-form-item label="Media Storage Path" v-if="configForm.saveMediaFiles">
              <el-input v-model="configForm.mediaPath" placeholder="Path to save media files" />
            </el-form-item>
          </el-tab-pane>
          
          <!-- Advanced Settings Tab -->
          <el-tab-pane label="Advanced Settings" name="advanced">
            <el-form-item label="Use JavaScript Rendering">
              <el-switch v-model="configForm.useJsRendering" />
            </el-form-item>
            
            <el-form-item label="JavaScript Renderer" v-if="configForm.useJsRendering">
              <el-select v-model="configForm.jsRenderer" placeholder="Select renderer">
                <el-option label="Playwright" value="playwright" />
                <el-option label="Selenium" value="selenium" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Headless Mode" v-if="configForm.useJsRendering">
              <el-switch v-model="configForm.headless" />
            </el-form-item>
            
            <el-form-item label="Browser" v-if="configForm.useJsRendering">
              <el-select v-model="configForm.browser" placeholder="Select browser">
                <el-option label="Chrome" value="chrome" />
                <el-option label="Firefox" value="firefox" />
                <el-option label="Edge" value="edge" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Log Level">
              <el-select v-model="configForm.logLevel" placeholder="Select log level">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARNING" value="warning" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Enable Custom HTTP Headers">
              <el-switch v-model="configForm.useCustomHeaders" />
            </el-form-item>
            
            <el-form-item label="Custom HTTP Headers" v-if="configForm.useCustomHeaders">
              <el-input
                type="textarea"
                v-model="configForm.customHeaders"
                placeholder="Enter headers in JSON format"
                rows="5"
              />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

const activeTab = ref('general');

// Form data
const configForm = ref({
  // General Settings
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  timeout: 30,
  retryCount: 3,
  requestDelay: 1000,
  concurrentRequests: 5,
  useRandomUserAgent: false,
  
  // Proxy Settings
  useProxy: false,
  proxyType: 'http',
  proxyHost: '',
  proxyPort: 8080,
  proxyAuth: false,
  proxyUsername: '',
  proxyPassword: '',
  
  // Storage Settings
  dbType: 'mongodb',
  dbConnectionString: 'mongodb://localhost:27017/artscraper',
  dbPath: './data/artscraper.db',
  saveMediaFiles: true,
  mediaPath: './media',
  
  // Advanced Settings
  useJsRendering: true,
  jsRenderer: 'playwright',
  headless: true,
  browser: 'chrome',
  logLevel: 'info',
  useCustomHeaders: false,
  customHeaders: '{\n  "Accept-Language": "en-US,en;q=0.9"\n}'
});

// Load configuration from backend
const loadConfig = async () => {
  try {
    // In a real app, you would load from API
    // const response = await api.scrapers.getConfig();
    // configForm.value = response.data;
    
    // For now, just use default values
    ElMessage.success('Configuration loaded');
  } catch (error) {
    ElMessage.error('Failed to load configuration');
    console.error(error);
  }
};

// Save configuration to backend
const saveConfig = async () => {
  try {
    // In a real app, you would save to API
    // await api.scrapers.saveConfig(configForm.value);
    
    // For now, just show success message
    console.log('Configuration saved:', configForm.value);
    ElMessage.success('Configuration saved successfully');
  } catch (error) {
    ElMessage.error('Failed to save configuration');
    console.error(error);
  }
};

onMounted(() => {
  loadConfig();
});
</script>

<style scoped>
.scraper-config-container {
  padding: 20px;
}

.el-form {
  max-width: 100%;
}
</style> 