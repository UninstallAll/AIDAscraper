<template>
  <el-dialog
    title="创建爬虫任务"
    v-model="dialogVisible"
    width="50%"
    :before-close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
      label-position="top"
    >
      <el-form-item label="任务名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入任务名称" />
      </el-form-item>

      <el-form-item label="站点" prop="site_config_id">
        <el-select 
          v-model="formData.site_config_id" 
          placeholder="请选择站点"
          filterable
          @change="handleSiteChange"
          style="width: 100%"
        >
          <el-option
            v-for="site in sites"
            :key="site.id"
            :label="site.name"
            :value="site.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="调度类型" prop="schedule_type">
        <el-select v-model="formData.schedule_type" placeholder="请选择调度类型" style="width: 100%">
          <el-option label="立即执行" value="once" />
          <el-option label="定时执行" value="scheduled" />
          <el-option label="周期执行" value="periodic" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="formData.schedule_type === 'scheduled'" label="执行时间" prop="schedule_time">
        <el-date-picker
          v-model="formData.schedule_time"
          type="datetime"
          placeholder="请选择执行时间"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item v-if="formData.schedule_type === 'periodic'" label="周期表达式" prop="cron_expression">
        <el-input 
          v-model="formData.cron_expression" 
          placeholder="请输入Cron表达式，例如: 0 0 * * *"
        />
        <div class="cron-helper">
          <el-link type="primary" href="https://crontab.guru/" target="_blank">
            Cron表达式帮助
          </el-link>
        </div>
      </el-form-item>

      <el-form-item label="高级配置">
        <el-collapse>
          <el-collapse-item title="爬虫配置" name="config">
            <el-form-item label="最大深度" prop="config.max_depth">
              <el-input-number 
                v-model="formData.config.max_depth" 
                :min="1" 
                :max="10"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="请求延迟(秒)" prop="config.delay">
              <el-input-number 
                v-model="formData.config.delay" 
                :min="0" 
                :max="10"
                :step="0.5"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="最大页面数" prop="config.max_pages">
              <el-input-number 
                v-model="formData.config.max_pages" 
                :min="0" 
                :max="1000"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="跟随链接" prop="config.follow_links">
              <el-switch v-model="formData.config.follow_links" />
            </el-form-item>

            <el-form-item label="使用代理" prop="config.use_proxy">
              <el-switch v-model="formData.config.use_proxy" />
            </el-form-item>
          </el-collapse-item>
        </el-collapse>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">创建</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as jobApi from '../api/job'
import * as siteApi from '../api/site'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  siteId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['update:visible', 'created'])

// 对话框可见状态
const dialogVisible = ref(false)

// 监听visible属性变化
watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    fetchSites()
    if (props.siteId) {
      formData.site_config_id = props.siteId
    }
  }
})

// 监听dialogVisible变化，同步更新父组件的visible属性
watch(() => dialogVisible.value, (val) => {
  emit('update:visible', val)
})

// 表单引用
const formRef = ref(null)

// 站点列表
const sites = ref([])
const loading = ref(false)

// 表单数据
const formData = reactive({
  name: '',
  site_config_id: props.siteId || null,
  schedule_type: 'once',
  schedule_time: null,
  cron_expression: '',
  config: {
    max_depth: 3,
    delay: 1,
    max_pages: 100,
    follow_links: true,
    use_proxy: false
  }
})

// 验证规则
const rules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  site_config_id: [
    { required: true, message: '请选择站点', trigger: 'change' }
  ],
  schedule_type: [
    { required: true, message: '请选择调度类型', trigger: 'change' }
  ],
  schedule_time: [
    { 
      required: true, 
      message: '请选择执行时间', 
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (formData.schedule_type === 'scheduled' && !value) {
          callback(new Error('请选择执行时间'))
        } else {
          callback()
        }
      }
    }
  ],
  cron_expression: [
    {
      required: true,
      message: '请输入Cron表达式',
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (formData.schedule_type === 'periodic' && !value) {
          callback(new Error('请输入Cron表达式'))
        } else {
          callback()
        }
      }
    }
  ]
}

// 获取站点列表
const fetchSites = async () => {
  try {
    const response = await siteApi.getSites()
    sites.value = response.data.items || response.data
  } catch (error) {
    console.error('获取站点列表失败', error)
    // 模拟数据
    sites.value = [
      { id: 1, name: '艺术网站1' },
      { id: 2, name: '艺术网站2' },
      { id: 3, name: '艺术网站3' }
    ]
  }
}

// 处理站点选择变化
const handleSiteChange = (siteId) => {
  const site = sites.value.find(s => s.id === siteId)
  if (site) {
    // 自动填充任务名称
    if (!formData.name) {
      formData.name = `${site.name} 爬虫任务`
    }
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    // 准备提交数据
    const submitData = {
      name: formData.name,
      site_config_id: formData.site_config_id,
      schedule_type: formData.schedule_type,
      config: formData.config
    }
    
    // 根据调度类型添加额外字段
    if (formData.schedule_type === 'scheduled' && formData.schedule_time) {
      submitData.schedule_time = formData.schedule_time
    }
    
    if (formData.schedule_type === 'periodic' && formData.cron_expression) {
      submitData.cron_expression = formData.cron_expression
    }
    
    // 提交表单
    const response = await jobApi.createJob(submitData)
    
    ElMessage.success('任务创建成功')
    emit('created', response.data)
    dialogVisible.value = false
  } catch (error) {
    console.error('表单验证或提交失败', error)
    if (error.response) {
      ElMessage.error(error.response.data.detail || '创建任务失败')
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('表单验证失败，请检查输入')
    }
  } finally {
    loading.value = false
  }
}

// 处理关闭对话框
const handleClose = (done) => {
  done()
}

onMounted(() => {
  if (props.siteId) {
    formData.site_config_id = props.siteId
  }
})
</script>

<style scoped>
.cron-helper {
  margin-top: 5px;
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style> 