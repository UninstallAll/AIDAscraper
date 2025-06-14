<template>
  <div class="site-config-form">
    <el-form 
      ref="formRef" 
      :model="formData" 
      :rules="rules" 
      label-width="140px"
      label-position="top"
    >
      <!-- 基本信息 -->
      <h3>基本信息</h3>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="站点名称" prop="name">
            <el-input v-model="formData.name" placeholder="请输入站点名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="站点URL" prop="url">
            <el-input v-model="formData.url" placeholder="请输入站点URL" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="站点描述" prop="description">
        <el-input 
          v-model="formData.description" 
          type="textarea" 
          placeholder="请输入站点描述"
          :rows="2"
        />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="是否需要登录" prop="requires_login">
            <el-switch v-model="formData.requires_login" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="使用Playwright" prop="use_playwright">
            <el-switch v-model="formData.use_playwright" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 登录设置 (条件显示) -->
      <div v-if="formData.requires_login">
        <h3>登录设置</h3>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="登录页面URL" prop="login_url">
              <el-input v-model="formData.login_url" placeholder="请输入登录页面URL" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名字段名" prop="login_username_field">
              <el-input v-model="formData.login_username_field" placeholder="例如: username" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码字段名" prop="login_password_field">
              <el-input v-model="formData.login_password_field" placeholder="例如: password" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="login_username">
              <el-input v-model="formData.login_username" placeholder="请输入用户名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码" prop="login_password">
              <el-input 
                v-model="formData.login_password" 
                type="password" 
                placeholder="请输入密码"
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 爬虫配置 -->
      <h3>爬虫配置</h3>
      <el-form-item label="起始URL列表" prop="start_urls">
        <el-tag
          v-for="(url, index) in formData.start_urls"
          :key="index"
          closable
          @close="removeStartUrl(index)"
          class="url-tag"
        >
          {{ url }}
        </el-tag>
        <el-input
          v-if="inputVisible"
          ref="urlInputRef"
          v-model="inputValue"
          class="url-input"
          size="small"
          @keyup.enter="addStartUrl"
          @blur="addStartUrl"
        />
        <el-button v-else class="button-new-tag" size="small" @click="showInput">
          + 添加URL
        </el-button>
      </el-form-item>
      
      <el-form-item label="允许的域名" prop="allowed_domains">
        <el-tag
          v-for="(domain, index) in formData.allowed_domains"
          :key="index"
          closable
          @close="removeDomain(index)"
          class="domain-tag"
        >
          {{ domain }}
        </el-tag>
        <el-input
          v-if="domainInputVisible"
          ref="domainInputRef"
          v-model="domainInputValue"
          class="domain-input"
          size="small"
          @keyup.enter="addDomain"
          @blur="addDomain"
        />
        <el-button v-else class="button-new-tag" size="small" @click="showDomainInput">
          + 添加域名
        </el-button>
      </el-form-item>

      <!-- XPath配置 -->
      <h3>XPath配置</h3>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="列表页XPath" prop="list_page_xpath">
            <el-input v-model="formData.list_page_xpath" placeholder="例如: //div[@class='item-list']//a" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="下一页XPath" prop="next_page_xpath">
            <el-input v-model="formData.next_page_xpath" placeholder="例如: //a[@class='next-page']" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="详情页XPath" prop="detail_page_xpath">
        <el-input v-model="formData.detail_page_xpath" placeholder="例如: //div[@class='detail-content']" />
      </el-form-item>

      <!-- 字段映射 -->
      <h3>字段映射</h3>
      <el-form-item label="字段映射配置" prop="field_mappings">
        <el-table :data="fieldMappingsArray" style="width: 100%">
          <el-table-column label="字段名">
            <template #default="scope">
              <el-input v-model="scope.row.field" placeholder="字段名" />
            </template>
          </el-table-column>
          <el-table-column label="XPath">
            <template #default="scope">
              <el-input v-model="scope.row.xpath" placeholder="XPath表达式" />
            </template>
          </el-table-column>
          <el-table-column width="120">
            <template #default="scope">
              <el-button type="danger" size="small" @click="removeFieldMapping(scope.$index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top: 10px;">
          <el-button type="primary" size="small" @click="addFieldMapping">
            添加字段映射
          </el-button>
        </div>
      </el-form-item>

      <!-- 高级配置 -->
      <h3>高级配置</h3>
      <el-form-item label="爬虫配置JSON" prop="config">
        <el-input
          v-model="configJson"
          type="textarea"
          :rows="5"
          placeholder="请输入JSON格式的爬虫配置"
          @change="updateConfig"
        />
      </el-form-item>
      
      <!-- 表单操作 -->
      <el-form-item>
        <el-button type="primary" @click="submitForm">保存</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { validateSiteConfig } from '../utils/schema-validator'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({})
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

// 表单引用
const formRef = ref(null)

// 表单数据
const formData = reactive({
  name: '',
  url: '',
  description: '',
  requires_login: false,
  login_url: '',
  login_username_field: '',
  login_password_field: '',
  login_username: '',
  login_password: '',
  start_urls: [],
  allowed_domains: [],
  list_page_xpath: '',
  next_page_xpath: '',
  detail_page_xpath: '',
  field_mappings: {},
  use_playwright: false,
  config: {},
  is_active: true,
  tenant_id: 'default'
})

// 字段映射数组形式，用于表格展示
const fieldMappingsArray = ref([])

// 配置JSON字符串
const configJson = ref('{}')

// 验证规则
const rules = {
  name: [{ required: true, message: '请输入站点名称', trigger: 'blur' }],
  url: [{ required: true, message: '请输入站点URL', trigger: 'blur' }],
  start_urls: [{ type: 'array', required: true, message: '请至少添加一个起始URL', trigger: 'change' }]
}

// 起始URL输入
const inputVisible = ref(false)
const inputValue = ref('')
const urlInputRef = ref(null)

// 域名输入
const domainInputVisible = ref(false)
const domainInputValue = ref('')
const domainInputRef = ref(null)

// 显示URL输入框
const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    urlInputRef.value.focus()
  })
}

// 添加起始URL
const addStartUrl = () => {
  if (inputValue.value) {
    formData.start_urls.push(inputValue.value)
    inputValue.value = ''
  }
  inputVisible.value = false
}

// 删除起始URL
const removeStartUrl = (index) => {
  formData.start_urls.splice(index, 1)
}

// 显示域名输入框
const showDomainInput = () => {
  domainInputVisible.value = true
  nextTick(() => {
    domainInputRef.value.focus()
  })
}

// 添加域名
const addDomain = () => {
  if (domainInputValue.value) {
    formData.allowed_domains.push(domainInputValue.value)
    domainInputValue.value = ''
  }
  domainInputVisible.value = false
}

// 删除域名
const removeDomain = (index) => {
  formData.allowed_domains.splice(index, 1)
}

// 添加字段映射
const addFieldMapping = () => {
  fieldMappingsArray.value.push({ field: '', xpath: '' })
  updateFieldMappings()
}

// 删除字段映射
const removeFieldMapping = (index) => {
  fieldMappingsArray.value.splice(index, 1)
  updateFieldMappings()
}

// 更新字段映射对象
const updateFieldMappings = () => {
  const mappings = {}
  fieldMappingsArray.value.forEach(item => {
    if (item.field && item.xpath) {
      mappings[item.field] = item.xpath
    }
  })
  formData.field_mappings = mappings
}

// 更新配置对象
const updateConfig = () => {
  try {
    formData.config = JSON.parse(configJson.value)
  } catch (error) {
    ElMessage.error('配置JSON格式错误')
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 更新字段映射
    updateFieldMappings()
    
    // 使用JSON Schema验证
    const validationResult = validateSiteConfig(formData)
    if (!validationResult.valid) {
      ElMessage.error(`表单验证失败: ${validationResult.errors.join(', ')}`)
      return
    }
    
    // 提交表单数据
    emit('submit', { ...formData })
  } catch (error) {
    console.error('表单验证失败', error)
    ElMessage.error('表单验证失败，请检查输入')
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 初始化表单数据
const initFormData = () => {
  // 如果是编辑模式，填充初始数据
  if (props.isEdit && props.initialData) {
    Object.keys(formData).forEach(key => {
      if (props.initialData[key] !== undefined) {
        formData[key] = props.initialData[key]
      }
    })
    
    // 处理字段映射
    fieldMappingsArray.value = Object.entries(formData.field_mappings || {}).map(
      ([field, xpath]) => ({ field, xpath })
    )
    
    // 处理配置JSON
    configJson.value = JSON.stringify(formData.config || {}, null, 2)
  } else {
    // 默认值
    formData.start_urls = [formData.url]
    formData.allowed_domains = formData.url ? [new URL(formData.url).hostname] : []
  }
}

onMounted(() => {
  initFormData()
})
</script>

<style scoped>
.site-config-form {
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
}

h3 {
  margin-top: 20px;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.url-tag,
.domain-tag {
  margin-right: 10px;
  margin-bottom: 10px;
}

.url-input,
.domain-input {
  width: 200px;
  margin-right: 10px;
  vertical-align: bottom;
}

.button-new-tag {
  margin-bottom: 10px;
}
</style> 