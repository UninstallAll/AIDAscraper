<template>
  <div class="website-manager-container">
    <el-row :gutter="20" class="mb-4">
      <el-col :span="24">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>Website Manager</span>
              <el-button type="primary" @click="openAddWebsiteDialog">Add Website</el-button>
            </div>
          </template>
          
          <!-- Loading state -->
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          
          <!-- Empty state -->
          <div v-else-if="websites.length === 0" class="empty-container">
            <el-empty description="No websites registered yet">
              <el-button type="primary" @click="openAddWebsiteDialog">Add Website</el-button>
            </el-empty>
          </div>
          
          <!-- Websites table -->
          <div v-else class="websites-table">
            <el-table :data="websites" style="width: 100%" border>
              <el-table-column prop="name" label="Website Name" min-width="180" />
              <el-table-column prop="url" label="URL" min-width="240" show-overflow-tooltip>
                <template #default="scope">
                  <el-link :href="scope.row.url" target="_blank" type="primary">{{ scope.row.url }}</el-link>
                </template>
              </el-table-column>
              <el-table-column prop="id" label="Website ID" min-width="120" />
              <el-table-column label="Scraper Status" min-width="180">
                <template #default="scope">
                  <el-tag v-if="hasScraperImplementation(scope.row.id)" type="success" effect="dark">
                    <el-icon><Check /></el-icon> Scraper Available
                  </el-tag>
                  <el-tag v-else type="info" effect="plain">
                    <el-icon><Close /></el-icon> No Scraper
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Actions" min-width="200" fixed="right">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="openCreateScraperDialog(scope.row)" 
                    :disabled="hasScraperImplementation(scope.row.id)">
                    Create Scraper
                  </el-button>
                  <el-button type="success" size="small" @click="openRunScraperDialog(scope.row)" 
                    :disabled="!hasScraperImplementation(scope.row.id)">
                    Run Scraper
                  </el-button>
                  <el-dropdown trigger="click">
                    <el-button size="small">
                      More<el-icon class="el-icon--right"><arrow-down /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item @click="editWebsite(scope.row)">Edit</el-dropdown-item>
                        <el-dropdown-item @click="viewScraperDetails(scope.row)" :disabled="!hasScraperImplementation(scope.row.id)">
                          View Scraper Details
                        </el-dropdown-item>
                        <el-dropdown-item divided type="danger" @click="confirmDeleteWebsite(scope.row)">
                          Delete
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Website Stats Overview -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="box-card" v-if="websites.length > 0">
          <template #header>
            <div class="card-header">
              <span>Scraper Statistics</span>
              <el-button type="text" @click="refreshStats">Refresh</el-button>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="6" v-for="(stat, index) in websiteStats" :key="index">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- Add Website Dialog -->
    <el-dialog
      v-model="addWebsiteDialogVisible"
      title="Add Website"
      width="500px"
    >
      <el-form :model="websiteForm" label-width="140px" :rules="websiteRules" ref="websiteFormRef">
        <el-form-item label="Website Name" prop="name">
          <el-input v-model="websiteForm.name" placeholder="e.g. Metropolitan Museum of Art" />
        </el-form-item>
        <el-form-item label="Website ID" prop="id">
          <el-input v-model="websiteForm.id" placeholder="e.g. met_museum" />
          <div class="form-hint">Unique identifier, lowercase with underscores only</div>
        </el-form-item>
        <el-form-item label="Website URL" prop="url">
          <el-input v-model="websiteForm.url" placeholder="e.g. https://www.metmuseum.org" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input 
            v-model="websiteForm.description" 
            type="textarea" 
            rows="3"
            placeholder="Brief description of the website" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addWebsiteDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="addWebsite">Create</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Create Scraper Dialog -->
    <el-dialog
      v-model="createScraperDialogVisible"
      title="Create Website Scraper"
      width="500px"
    >
      <el-form :model="scraperForm" label-width="140px" :rules="scraperRules" ref="scraperFormRef">
        <el-form-item label="Website">
          <el-input v-model="scraperForm.websiteName" :disabled="true" />
        </el-form-item>
        <el-form-item label="Scraper Class Name" prop="scraperName">
          <el-input v-model="scraperForm.scraperName" placeholder="e.g. MetMuseum" />
          <div class="form-hint">'Scraper' suffix will be added automatically</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createScraperDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="createScraper">Create</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Run Scraper Dialog -->
    <el-dialog
      v-model="runScraperDialogVisible"
      title="Run Website Scraper"
      width="500px"
    >
      <el-form :model="runScraperForm" label-width="140px">
        <el-form-item label="Website">
          <el-input v-model="runScraperForm.websiteName" :disabled="true" />
        </el-form-item>
        <el-form-item label="Content Type">
          <el-select v-model="runScraperForm.contentType" placeholder="Select content type">
            <el-option label="Artworks" value="artworks" />
            <el-option label="Artists" value="artists" />
            <el-option label="Exhibitions" value="exhibitions" />
          </el-select>
        </el-form-item>
        <el-form-item label="Max Pages">
          <el-input-number v-model="runScraperForm.pages" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="Items Per Page">
          <el-input-number v-model="runScraperForm.limit" :min="1" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="runScraperDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="runScraper">Run Scraper</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Scraper Details Dialog -->
    <el-dialog
      v-model="scraperDetailsDialogVisible"
      title="Scraper Details"
      width="800px"
    >
      <div v-if="selectedWebsite">
        <h3>{{ selectedWebsite.name }} Scraper</h3>
        
        <el-tabs v-model="activeScraperTab">
          <el-tab-pane label="Implementation Details" name="details">
            <el-descriptions title="Scraper Information" :column="1" border>
              <el-descriptions-item label="Implementation File">
                {{ `src/scrapers/sites/${selectedWebsite.id}.py` }}
              </el-descriptions-item>
              <el-descriptions-item label="Class Name">
                {{ getScraperClassName(selectedWebsite.id) }}
              </el-descriptions-item>
              <el-descriptions-item label="Target URL">
                {{ selectedWebsite.url }}
              </el-descriptions-item>
              <el-descriptions-item label="Last Modified">
                {{ getLastModifiedDate(selectedWebsite.id) }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="Run History" name="history">
            <el-empty description="No run history available" v-if="scraperHistory.length === 0"></el-empty>
            <el-table :data="scraperHistory" style="width: 100%" v-else>
              <el-table-column prop="date" label="Date" width="180" />
              <el-table-column prop="status" label="Status" width="120">
                <template #default="scope">
                  <el-tag
                    :type="scope.row.status === 'completed' ? 'success' : 
                           scope.row.status === 'failed' ? 'danger' : 'warning'"
                  >
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="items" label="Items" width="100" />
              <el-table-column prop="duration" label="Duration" width="120" />
              <el-table-column prop="content_type" label="Content Type" width="120" />
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Check, Close, ArrowDown } from '@element-plus/icons-vue';
import api from '@/api'; // 导入API服务

// Data
const websites = ref([]);
const loading = ref(true);
const addWebsiteDialogVisible = ref(false);
const createScraperDialogVisible = ref(false);
const runScraperDialogVisible = ref(false);
const scraperDetailsDialogVisible = ref(false);
const selectedWebsite = ref(null);
const activeScraperTab = ref('details');

// Available scrapers (from backend)
const availableScrapers = ref([]);

// Website form
const websiteFormRef = ref(null);
const websiteForm = ref({
  id: '',
  name: '',
  url: '',
  description: ''
});

// Scraper form
const scraperFormRef = ref(null);
const scraperForm = ref({
  websiteId: '',
  websiteName: '',
  scraperName: ''
});

// Run scraper form
const runScraperForm = ref({
  websiteId: '',
  websiteName: '',
  contentType: 'artworks',
  pages: 1,
  limit: 20
});

// Scraper history
const scraperHistory = ref([]);

// Website stats
const websiteStats = ref([
  { label: 'Total Websites', value: 0 },
  { label: 'Available Scrapers', value: 0 },
  { label: 'Total Artworks', value: 0 },
  { label: 'Total Artists', value: 0 }
]);

// Form validation rules
const websiteRules = {
  name: [
    { required: true, message: 'Please enter website name', trigger: 'blur' },
    { min: 3, message: 'Name must be at least 3 characters', trigger: 'blur' }
  ],
  id: [
    { required: true, message: 'Please enter website ID', trigger: 'blur' },
    { pattern: /^[a-z0-9_]+$/, message: 'ID must contain only lowercase letters, numbers and underscores', trigger: 'blur' }
  ],
  url: [
    { required: true, message: 'Please enter website URL', trigger: 'blur' },
    { pattern: /^https?:\/\/.+/, message: 'URL must start with http:// or https://', trigger: 'blur' }
  ]
};

const scraperRules = {
  scraperName: [
    { required: true, message: 'Please enter scraper class name', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9]+$/, message: 'Class name must contain only letters and numbers', trigger: 'blur' }
  ]
};

// Load available scrapers from backend
const loadAvailableScrapers = async () => {
  try {
    const scrapers = await api.websites.availableScrapers();
    availableScrapers.value = scrapers.map(scraper => scraper.id);
  } catch (error) {
    console.error('Failed to load available scrapers:', error);
    ElMessage.error('Failed to load available scrapers');
  }
}

// Check if a website has a scraper implementation
const hasScraperImplementation = (websiteId) => {
  return availableScrapers.value.includes(websiteId);
};

// Get scraper class name for a website
const getScraperClassName = (websiteId) => {
  // This would come from the backend in a real app
  const baseClassName = websiteId
    .split('_')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join('');
  
  return `${baseClassName}Scraper`;
};

// Get last modified date for a scraper
const getLastModifiedDate = (websiteId) => {
  // This would come from the backend in a real app
  return new Date().toISOString().split('T')[0];
};

// Open the add website dialog
const openAddWebsiteDialog = () => {
  websiteForm.value = {
    id: '',
    name: '',
    url: '',
    description: ''
  };
  addWebsiteDialogVisible.value = true;
};

// Open create scraper dialog
const openCreateScraperDialog = (website) => {
  scraperForm.value = {
    websiteId: website.id,
    websiteName: website.name,
    scraperName: website.name.replace(/\s/g, '')
  };
  createScraperDialogVisible.value = true;
};

// Open run scraper dialog
const openRunScraperDialog = (website) => {
  runScraperForm.value = {
    websiteId: website.id,
    websiteName: website.name,
    contentType: 'artworks',
    pages: 1,
    limit: 20
  };
  runScraperDialogVisible.value = true;
};

// Add a new website
const addWebsite = async () => {
  if (!websiteFormRef.value) return;
  
  await websiteFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // Call API to add website
        const result = await api.websites.add(websiteForm.value);
        
        // Add to local array
        websites.value.push(result);
        
        ElMessage.success('Website added successfully');
        addWebsiteDialogVisible.value = false;
        updateStats();
      } catch (error) {
        ElMessage.error('Failed to add website: ' + (error.response?.data?.detail || error.message));
        console.error(error);
      }
    }
  });
};

// Create a scraper for a website
const createScraper = async () => {
  if (!scraperFormRef.value) return;
  
  await scraperFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // Call API to create scraper
        await api.websites.createScraper(
          scraperForm.value.websiteId, 
          scraperForm.value.scraperName
        );
        
        // Refresh available scrapers
        await loadAvailableScrapers();
        
        ElMessage.success('Scraper created successfully');
        createScraperDialogVisible.value = false;
        updateStats();
      } catch (error) {
        ElMessage.error('Failed to create scraper: ' + (error.response?.data?.detail || error.message));
        console.error(error);
      }
    }
  });
};

// Run a website scraper
const runScraper = async () => {
  try {
    ElMessage({
      message: `Starting scraper for ${runScraperForm.value.websiteName}`,
      type: 'info'
    });
    
    // Call API to run scraper
    const result = await api.websites.runScraper({
      website_id: runScraperForm.value.websiteId,
      content_type: runScraperForm.value.contentType,
      pages: runScraperForm.value.pages,
      limit: runScraperForm.value.limit
    });
    
    ElMessage.success(`Scraper completed successfully. Retrieved ${result.result.results_count} items.`);
    
    // Add to history
    scraperHistory.value.unshift({
      date: new Date().toISOString().replace('T', ' ').substring(0, 19),
      status: result.status === 'success' ? 'completed' : 'failed',
      items: result.result.results_count || 0,
      duration: `${result.result.duration || 0}s`,
      content_type: runScraperForm.value.contentType
    });
    
    runScraperDialogVisible.value = false;
  } catch (error) {
    ElMessage.error('Failed to run scraper: ' + (error.response?.data?.detail || error.message));
    console.error(error);
  }
};

// Edit website
const editWebsite = (website) => {
  websiteForm.value = { ...website };
  addWebsiteDialogVisible.value = true;
};

// View scraper details
const viewScraperDetails = async (website) => {
  selectedWebsite.value = website;
  
  // This would come from the API
  // TODO: Add API endpoint to get scraper history
  scraperHistory.value = [
    {
      date: new Date().toISOString().replace('T', ' ').substring(0, 19),
      status: 'completed',
      items: 35,
      duration: '45s',
      content_type: 'artworks'
    }
  ];
  
  scraperDetailsDialogVisible.value = true;
};

// Confirm delete website
const confirmDeleteWebsite = (website) => {
  ElMessageBox.confirm(
    `Are you sure you want to delete "${website.name}"?`,
    'Warning',
    {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        // Call API to delete website
        await api.websites.delete(website.id);
        
        // Remove from local array
        websites.value = websites.value.filter(w => w.id !== website.id);
        
        ElMessage.success(`Website "${website.name}" has been deleted`);
        updateStats();
      } catch (error) {
        ElMessage.error('Failed to delete website: ' + (error.response?.data?.detail || error.message));
        console.error(error);
      }
    })
    .catch(() => {
      // User cancelled
    });
};

// Update statistics
const updateStats = () => {
  websiteStats.value = [
    { label: 'Total Websites', value: websites.value.length },
    { label: 'Available Scrapers', value: availableScrapers.value.length },
    { label: 'Total Artworks', value: 0 },  // These would come from backend
    { label: 'Total Artists', value: 0 }    // These would come from backend
  ];
};

// Refresh statistics
const refreshStats = async () => {
  try {
    await loadWebsites();
    await loadAvailableScrapers();
    
    updateStats();
    ElMessage.success('Statistics refreshed');
  } catch (error) {
    ElMessage.error('Failed to refresh statistics');
    console.error(error);
  }
};

// Load websites from backend
const loadWebsites = async () => {
  try {
    loading.value = true;
    
    // Call API to get websites
    websites.value = await api.websites.list();
    
    loading.value = false;
    updateStats();
  } catch (error) {
    ElMessage.error('Failed to load websites: ' + (error.response?.data?.detail || error.message));
    console.error(error);
    loading.value = false;
  }
};

// Load data on component mount
onMounted(async () => {
  try {
    await loadWebsites();
    await loadAvailableScrapers();
  } catch (error) {
    console.error('Error during component initialization:', error);
    loading.value = false;
  }
});
</script>

<style scoped>
.website-manager-container {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container, .empty-container {
  padding: 40px 0;
  text-align: center;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.stat-card {
  text-align: center;
  padding: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  margin-top: 5px;
  font-size: 14px;
  color: #606266;
}
</style> 