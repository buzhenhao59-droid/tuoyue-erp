<template>
  <el-drawer
    v-model="visible"
    title="商品详情"
    size="800px"
    :close-on-click-modal="false"
    class="product-detail-drawer"
  >
    <div v-if="product" class="drawer-content">
      <!-- 基本信息 -->
      <el-card shadow="never" class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag :type="getStatusType(product.status)" size="small">
              {{ getStatusText(product.status) }}
            </el-tag>
          </div>
        </template>
        
        <div class="basic-info">
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">来源平台：</span>
              <el-tag size="small" :style="{ background: product.platform_color, color: '#fff' }">
                {{ product.source_platform }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">来源ID：</span>
              <span class="info-value">{{ product.source_id }}</span>
            </div>
          </div>
          
          <div class="info-row">
            <div class="info-item full-width">
              <span class="info-label">来源链接：</span>
              <el-link type="primary" :href="product.source_url" target="_blank" class="source-link">
                {{ product.source_url }}
              </el-link>
            </div>
          </div>
        </div>
      </el-card>
      
      <!-- 商品图片 -->
      <el-card shadow="never" class="info-card">
        <template #header>
          <span>商品图片</span>
        </template>
        
        <div class="image-gallery">
          <div class="main-image">
            <el-image :src="product.main_image" fit="cover" class="gallery-main" />
          </div>
          <div class="thumb-list">
            <el-image
              v-for="(img, index) in product.images.slice(0, 8)"
              :key="index"
              :src="img"
              fit="cover"
              class="gallery-thumb"
            />
          </div>
        </div>
      </el-card>
      
      <!-- 商品标题 -->
      <el-card shadow="never" class="info-card">
        <template #header>
          <span>商品标题</span>
        </template>
        
        <el-form :model="editForm" label-width="80px">
          <el-form-item label="原标题">
            <el-input v-model="product.title" type="textarea" :rows="2" disabled />
          </el-form-item>
          <el-form-item label="编辑标题">
            <el-input v-model="editForm.title" type="textarea" :rows="2" placeholder="输入编辑后的标题" />
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 价格信息 -->
      <el-card shadow="never" class="info-card">
        <template #header>
          <span>价格信息</span>
        </template>
        
        <div class="price-info">
          <div class="price-row">
            <div class="price-item">
              <span class="price-label">原始价格：</span>
              <span class="price-value original">¥{{ product.original_price_min }}</span>
            </div>
            <div class="price-item">
              <span class="price-label">当前价格：</span>
              <span class="price-value current">¥{{ product.price_min }}</span>
            </div>
          </div>
          
          <el-form :model="editForm" label-width="80px" class="edit-price-form">
            <el-form-item label="修改价格">
              <el-input-number v-model="editForm.price" :min="0" :precision="2" :step="1" />
            </el-form-item>
          </el-form>
        </div>
      </el-card>
      
      <!-- SKU 信息 -->
      <el-card shadow="never" class="info-card">
        <template #header>
          <div class="card-header">
            <span>SKU 信息</span>
            <el-tag size="small" type="info">{{ product.sku_count }} 个 SKU</el-tag>
          </div>
        </template>
        
        <el-table :data="product.skus" border size="small">
          <el-table-column prop="sku_id" label="SKU ID" width="120" />
          <el-table-column label="属性" min-width="150">
            <template #default="{ row }">
              <div class="sku-attrs">
                <el-tag
                  v-for="(value, key) in row.attributes"
                  :key="key"
                  size="small"
                  class="sku-attr-tag"
                >
                  {{ key }}: {{ value }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格" width="100">
            <template #default="{ row }">
              ¥{{ row.price }}
            </template>
          </el-table-column>
          <el-table-column prop="stock" label="库存" width="80" />
        </el-table>
      </el-card>
      
      <!-- 操作按钮 -->
      <div class="drawer-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存修改</el-button>
        <el-button type="success" @click="handleClaim" v-if="product.status === 'pending'">认领商品</el-button>
        <el-button type="warning" @click="handlePush">推送到店铺</el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { CollectedProduct } from '@/types/collections'
import { updateCollectedProduct, claimProduct } from '@/api/collections'

interface Props {
  modelValue: boolean
  product: CollectedProduct | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'saved': []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const saving = ref(false)

const editForm = ref({
  title: '',
  price: 0
})

// 监听产品变化，初始化表单
watch(() => props.product, (newProduct) => {
  if (newProduct) {
    editForm.value = {
      title: newProduct.title_en || newProduct.title,
      price: newProduct.price_min || 0
    }
  }
}, { immediate: true })

function getStatusType(status: string): string {
  const map: Record<string, string> = {
    pending: 'warning',
    claimed: 'primary',
    editing: 'primary',
    published: 'success',
    ignored: 'info'
  }
  return map[status] || 'info'
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待认领',
    claimed: '已认领',
    editing: '编辑中',
    published: '已发布',
    ignored: '已忽略'
  }
  return map[status] || status
}

async function handleSave() {
  if (!props.product) return
  
  saving.value = true
  try {
    await updateCollectedProduct(props.product.id, {
      title_en: editForm.value.title,
      price_min: editForm.value.price,
      price_max: editForm.value.price
    })
    ElMessage.success('保存成功')
    emit('saved')
    visible.value = false
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleClaim() {
  if (!props.product) return
  
  try {
    await claimProduct(props.product.id)
    ElMessage.success('认领成功')
    emit('saved')
    visible.value = false
  } catch (error) {
    ElMessage.error('认领失败')
  }
}

function handlePush() {
  ElMessage.info('推送功能开发中...')
}
</script>

<style scoped lang="scss">
.product-detail-drawer {
  :deep(.el-drawer__header) {
    margin-bottom: 0;
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;
  }
  
  :deep(.el-drawer__body) {
    padding: 0;
    background: #f5f7fa;
  }
}

.drawer-content {
  padding: 20px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.info-card {
  margin-bottom: 16px;
  
  :deep(.el-card__header) {
    padding: 12px 16px;
    font-weight: 500;
  }
  
  :deep(.el-card__body) {
    padding: 16px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.basic-info {
  .info-row {
    display: flex;
    gap: 32px;
    margin-bottom: 12px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .info-item {
    display: flex;
    align-items: center;
    
    &.full-width {
      flex: 1;
    }
  }
  
  .info-label {
    color: #909399;
    font-size: 14px;
    margin-right: 8px;
  }
  
  .info-value {
    color: #303133;
    font-size: 14px;
  }
  
  .source-link {
    max-width: 500px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.image-gallery {
  .main-image {
    margin-bottom: 12px;
    
    .gallery-main {
      width: 100%;
      height: 300px;
      border-radius: 8px;
    }
  }
  
  .thumb-list {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    
    .gallery-thumb {
      width: 80px;
      height: 80px;
      border-radius: 4px;
      cursor: pointer;
      border: 2px solid transparent;
      
      &:hover {
        border-color: #00b5ad;
      }
    }
  }
}

.price-info {
  .price-row {
    display: flex;
    gap: 32px;
    margin-bottom: 16px;
  }
  
  .price-item {
    display: flex;
    align-items: center;
  }
  
  .price-label {
    color: #909399;
    font-size: 14px;
    margin-right: 8px;
  }
  
  .price-value {
    font-size: 18px;
    font-weight: 600;
    
    &.original {
      color: #909399;
      text-decoration: line-through;
    }
    
    &.current {
      color: #f56c6c;
    }
  }
}

.sku-attrs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.sku-attr-tag {
  margin-right: 0;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>