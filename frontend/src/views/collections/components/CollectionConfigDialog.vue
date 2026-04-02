<template>
  <el-dialog
    v-model="visible"
    title="采集配置"
    width="700px"
    :close-on-click-modal="false"
  >
    <el-form :model="form" label-width="120px">
      <el-divider>基础设置</el-divider>
      
      <el-form-item label="配置名称">
        <el-input v-model="form.name" placeholder="请输入配置名称" />
      </el-form-item>
      
      <el-form-item label="设为默认">
        <el-switch v-model="form.is_default" />
      </el-form-item>
      
      <el-divider>价格转换</el-divider>
      
      <el-form-item label="价格规则">
        <el-radio-group v-model="form.price_rule">
          <el-radio label="fixed">固定倍率</el-radio>
          <el-radio label="tier">阶梯倍率</el-radio>
          <el-radio label="formula">自定义公式</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="价格倍率">
        <el-input-number v-model="form.price_multiplier" :min="0.1" :max="10" :precision="2" />
        <span class="form-tip">采集价格 × 倍率 = 销售价格</span>
      </el-form-item>
      
      <el-form-item label="固定加价">
        <el-input-number v-model="form.price_addition" :min="0" :precision="2" />
        <span class="form-tip">在倍率基础上额外增加的金额</span>
      </el-form-item>
      
      <el-form-item label="价格保护">
        <el-col :span="11">
          <el-input-number v-model="form.min_price" placeholder="最低价" :precision="2" style="width: 100%" />
        </el-col>
        <el-col :span="2" class="text-center">-</el-col>
        <el-col :span="11">
          <el-input-number v-model="form.max_price" placeholder="最高价" :precision="2" style="width: 100%" />
        </el-col>
      </el-form-item>
      
      <el-divider>内容处理</el-divider>
      
      <el-form-item label="自动翻译">
        <el-switch v-model="form.auto_translate" />
        <span class="form-tip" v-if="form.auto_translate">
          <el-select v-model="form.translate_to" style="width: 120px; margin-left: 10px">
            <el-option label="英语" value="en" />
            <el-option label="泰语" value="th" />
            <el-option label="越南语" value="vi" />
            <el-option label="印尼语" value="id" />
          </el-select>
        </span>
      </el-form-item>
      
      <el-divider>图片处理</el-divider>
      
      <el-form-item label="下载图片">
        <el-switch v-model="form.download_images" />
      </el-form-item>
      
      <el-form-item label="自动去水印">
        <el-switch v-model="form.watermark_remove" />
      </el-form-item>
      
      <el-form-item label="图片压缩">
        <el-switch v-model="form.image_compress" />
      </el-form-item>
      
      <el-divider>SKU默认设置</el-divider>
      
      <el-form-item label="默认库存">
        <el-input-number v-model="form.default_stock" :min="0" :max="99999" />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">保存配置</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { createCollectionConfig, updateCollectionConfig } from '@/api/collections'
import type { CollectionConfig } from '@/types/collections'

const props = defineProps<{
  modelValue: boolean
  editData?: CollectionConfig
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'save': []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val)
})

const saving = ref(false)

const form = reactive({
  name: '',
  is_default: false,
  price_rule: 'fixed',
  price_multiplier: 1.5,
  price_addition: 0,
  min_price: null as number | null,
  max_price: null as number | null,
  auto_translate: false,
  translate_to: 'en',
  download_images: true,
  watermark_remove: false,
  image_compress: true,
  default_stock: 999
})

// 监听编辑数据
watch(() => props.editData, (data) => {
  if (data) {
    Object.assign(form, data)
  } else {
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.name = ''
  form.is_default = false
  form.price_rule = 'fixed'
  form.price_multiplier = 1.5
  form.price_addition = 0
  form.min_price = null
  form.max_price = null
  form.auto_translate = false
  form.translate_to = 'en'
  form.download_images = true
  form.watermark_remove = false
  form.image_compress = true
  form.default_stock = 999
}

async function handleSave() {
  if (!form.name) {
    ElMessage.warning('请输入配置名称')
    return
  }
  
  saving.value = true
  try {
    const data: any = { ...form }
    if (props.editData) {
      await updateCollectionConfig(props.editData.id, data)
    } else {
      await createCollectionConfig(data)
    }
    ElMessage.success('保存成功')
    visible.value = false
    emit('save')
    resetForm()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 13px;
}

.text-center {
  text-align: center;
}
</style>
