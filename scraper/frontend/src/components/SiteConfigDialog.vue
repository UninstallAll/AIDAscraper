<template>
  <el-dialog
    :title="isEdit ? '编辑站点配置' : '添加站点配置'"
    v-model="dialogVisible"
    width="80%"
    :before-close="handleClose"
    destroy-on-close
  >
    <site-config-form
      ref="formRef"
      :initial-data="formData"
      :is-edit="isEdit"
      @submit="handleSubmit"
      @cancel="dialogVisible = false"
    />
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import SiteConfigForm from './SiteConfigForm.vue'
import * as siteApi from '../api/site'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  siteData: {
    type: Object,
    default: () => ({})
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'created', 'updated'])

// 对话框可见状态
const dialogVisible = ref(false)

// 监听visible属性变化
watch(() => props.visible, (val) => {
  dialogVisible.value = val
})

// 监听dialogVisible变化，同步更新父组件的visible属性
watch(() => dialogVisible.value, (val) => {
  emit('update:visible', val)
})

// 表单引用
const formRef = ref(null)

// 表单数据
const formData = reactive({...props.siteData})

// 加载状态
const loading = ref(false)

// 处理关闭对话框
const handleClose = (done) => {
  done()
}

// 提交表单
const submitForm = () => {
  if (formRef.value) {
    formRef.value.submitForm()
  }
}

// 处理表单提交
const handleSubmit = async (data) => {
  loading.value = true
  
  try {
    if (props.isEdit) {
      // 更新站点
      await siteApi.updateSite(data.id, data)
      ElMessage.success('站点更新成功')
      emit('updated', data)
    } else {
      // 创建站点
      const response = await siteApi.createSite(data)
      ElMessage.success('站点创建成功')
      emit('created', response.data)
    }
    
    // 关闭对话框
    dialogVisible.value = false
  } catch (error) {
    console.error('保存站点配置失败', error)
    ElMessage.error(error.response?.data?.detail || '保存站点配置失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style> 