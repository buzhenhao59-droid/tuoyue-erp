<template>
  <el-dialog
    v-model="visible"
    title="批量推送到店铺"
    width="600px"
    :close-on-click-modal="false"
    class="batch-push-dialog"
  >
    <div class="dialog-content">
      <div class="selected-info">
        <el-alert
          :title="`已选择 ${selectedCount} 个商品进行推送`"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
      
      <el-form :model="form" label-width="100px" class="push-form">
        <el-form-item label="目标店铺" required>
          <el-select
            v-model="form.shopIds"
            multiple
            placeholder="请选择要推送到的店铺"
            style="width: 100%"
          >
            <el-option-group
              v-for="group in shopGroups"
              :key="group.platform"
              :label="group.platform"
            >
              <el-option
                v-for="shop in group.shops"
                :key="shop.id"
                :label="shop.name"
                :value="shop.id"
              />
            </el-option-group>
          </el-select>
          <span class="form-tip">支持同时推送到多个店铺</span>
        </el-form-item>
        
        <el-form-item label="推送配置">
          <el-select v-model="form.configId" placeholder="选择推送配置（可选）" clearable style="width: 100%">
            <el-option
              v-for="config in pushConfigs"
              :key="config.id"
              :label="config.name"
              :value="config.id"
            />
          </el-select>
        </el-form-item>
        
        <el-divider />
        
        <el-form-item label="价格调整">
          <el-radio-group v-model="form.priceAdjust">
            <el-radio label="none">保持原价</el-radio>
            <el-radio label="multiply">按比例调整</el-radio>
            <el-radio label="add">固定加价</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="form.priceAdjust === 'multiply'" label="调整比例">
          <el-input-number
            v-model="form.priceMultiplier"
            :min="0.1"
            :max="10"
            :step="0.1"
            :precision="2"
            style="width: 200px"
          />
          <span class="form-tip">例如：1.2 表示上调 20%</span>
        </el-form-item>
        
        <el-form-item v-if="form.priceAdjust === 'add'" label="加价金额">
          <el-input-number
            v-model="form.priceAddition"
            :min="0"
            :step="1"
            :precision="2"
            style="width: 200px"
          />
          <span class="form-tip">在原价格基础上增加指定金额</span>
        </el-form-item>
        
        <el-divider />
        
        <el-form-item label="其他选项">
          <el-checkbox v-model="form.autoTranslate">自动翻译商品信息</el-checkbox>
          <el-checkbox v-model="form.autoCategory">自动匹配类目</el-checkbox>
          <el-checkbox v-model="form.skipError">跳过错误继续推送</el-checkbox>
        </el-form-item>
      </el-form>
      
      <!-- 推送预览 -->
      <div class="push-preview">
        <div class="preview-title">推送预览</div>
        <div class="preview-content">
          <div class="preview-item">
            <span class="preview-label">推送商品数：</span>
            <span class="preview-value">{{ selectedCount }} 个</span>
          </div>
          <div class="preview-item">
            <span class="preview-label">目标店铺数：</span>
            <span class="preview-value">{{ form.shopIds.length }} 个</span>
          </div>
          <div class="preview-item">
            <span class="preview-label">预计生成商品数：</span>
            <span class="preview-value highlight">{{ selectedCount * form.shopIds.length }} 个</span>
          </div>
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="loading" :disabled="!form.shopIds.length">
          开始推送
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getShops } from '@/api/shops'

interface Props {
  modelValue: boolean
  selectedCount: number
  selectedIds: number[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)

const form = ref({
  shopIds: [] as number[],
  configId: undefined as number | undefined,
  priceAdjust: 'none',
  priceMultiplier: 1.0,
  priceAddition: 0,
  autoTranslate: false,
  autoCategory: true,
  skipError: true
})

// 店铺分组
const shopGroups = ref([
  {
    platform: 'TikTok Shop',
    shops: [
      { id: 1, name: 'TikTok 旗舰店' },
      { id: 2, name: 'TikTok 海外店' }
    ]
  },
  {
    platform: 'Shopee',
    shops: [
      { id: 3, name: 'Shopee 新加坡店' },
      { id: 4, name: 'Shopee 马来店' }
    ]
  },
  {
    platform: 'Lazada',
    shops: [
      { id: 5, name: 'Lazada 泰国店' }
    ]
  }
])

// 推送配置
const pushConfigs = ref([
  { id: 1, name: '默认推送配置' },
  { id: 2, name: '海外店铺专用' },
  { id: 3, name: '低价促销配置' }
])

async function fetchShops() {
  try {
    const res: any = await getShops()
    // 处理店铺数据分组
    if (res.data) {
      // 按平台分组
      const groups: Record<string, any[]> = {}
      res.data.forEach((shop: any) => {
        const platform = shop.platform_name || '其他'
        if (!groups[platform]) {
          groups[platform] = []
        }
        groups[platform].push(shop)
      })
      
      shopGroups.value = Object.entries(groups).map(([platform, shops]) => ({
        platform,
        shops
      }))
    }
  } catch (error) {
    console.error('获取店铺失败', error)
    // 使用默认数据
  }
}

function handleConfirm() {
  if (form.value.shopIds.length === 0) {
    ElMessage.warning('请至少选择一个目标店铺')
    return
  }
  
  loading.value = true
  
  // 模拟推送操作
  setTimeout(() => {
    ElMessage.success(`成功推送 ${props.selectedCount} 个商品到 ${form.value.shopIds.length} 个店铺`)
    loading.value = false
    visible.value = false
    emit('success')
  }, 1500)
}

onMounted(() => {
  fetchShops()
})
</script>

<style scoped lang="scss">
.batch-push-dialog {
  :deep(.el-dialog__header) {
    border-bottom: 1px solid #ebeef5;
    padding: 20px;
    margin-right: 0;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px;
  }
  
  :deep(.el-dialog__footer) {
    border-top: 1px solid #ebeef5;
    padding: 16px 20px;
  }
}

.dialog-content {
  max-height: 550px;
  overflow-y: auto;
}

.selected-info {
  margin-bottom: 20px;
}

.push-form {
  .form-tip {
    display: block;
    margin-top: 8px;
    font-size: 13px;
    color: #909399;
  }
}

.push-preview {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  
  .preview-title {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px dashed #dcdfe6;
  }
  
  .preview-content {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .preview-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .preview-label {
    font-size: 14px;
    color: #606266;
  }
  
  .preview-value {
    font-size: 14px;
    font-weight: 500;
    color: #303133;
    
    &.highlight {
      color: #00b5ad;
      font-size: 16px;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>