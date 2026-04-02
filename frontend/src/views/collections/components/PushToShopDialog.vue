<template>
  <el-dialog
    v-model="visible"
    title="推送到店铺"
    width="600px"
  >
    <div class="push-dialog-content">
      <p class="tip">已选择 {{ selectedIds.length }} 个商品，请选择目标店铺：</p>
      
      <el-checkbox-group v-model="selectedShops">
        <div class="shop-list">
          <el-checkbox v-for="shop in shopList" :key="shop.id" :label="shop.id">
            <div class="shop-item">
              <img :src="shop.logo" class="shop-logo" />
              <div class="shop-info">
                <div class="shop-name">{{ shop.name }}</div>
                <div class="shop-platform">{{ shop.platform }}</div>
              </div>
            </div>
          </el-checkbox>
        </div>
      </el-checkbox-group>
      
      <el-divider />
      
      <el-form label-width="100px">
        <el-form-item label="发布配置">
          <el-select v-model="selectedConfig" placeholder="选择发布配置（可选）">
            <el-option label="默认配置" :value="null" />
            <el-option v-for="config in configList" :key="config.id" :label="config.name" :value="config.id" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleConfirm" :disabled="!selectedShops.length">
        确定推送
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getCollectionConfigs } from '@/api/collections'

const props = defineProps<{
  modelValue: boolean
  selectedIds: number[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'confirm': [shopIds: number[]]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const selectedShops = ref<number[]>([])
const selectedConfig = ref<number | null>(null)

const shopList = ref<any[]>([
  // 模拟数据，实际应从API获取
  { id: 1, name: 'TikTok Shop - SG', platform: 'TikTok', logo: '/static/platforms/tiktok.svg' },
  { id: 2, name: 'Shopee - SG', platform: 'Shopee', logo: '/static/platforms/shopee.svg' },
  { id: 3, name: 'Lazada - MY', platform: 'Lazada', logo: '/static/platforms/lazada.svg' },
])

const configList = ref<any[]>([])

onMounted(async () => {
  try {
    const res: any = await getCollectionConfigs()
    configList.value = res.results || []
  } catch (error) {
    console.error('获取配置失败', error)
  }
})

function handleConfirm() {
  emit('confirm', selectedShops.value)
  selectedShops.value = []
}
</script>

<style scoped>
.push-dialog-content {
  .tip {
    margin-bottom: 16px;
    color: #606266;
  }
  
  .shop-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: 300px;
    overflow-y: auto;
  }
  
  .shop-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px;
    
    .shop-logo {
      width: 40px;
      height: 40px;
      border-radius: 4px;
    }
    
    .shop-info {
      .shop-name {
        font-weight: 500;
        color: #303133;
      }
      
      .shop-platform {
        font-size: 12px;
        color: #909399;
        margin-top: 4px;
      }
    }
  }
}
</style>
