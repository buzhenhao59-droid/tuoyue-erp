<template>
  <el-dialog
    v-model="visible"
    title="批量修改价格"
    width="500px"
    :close-on-click-modal="false"
    class="batch-price-dialog"
  >
    <div class="dialog-content">
      <div class="selected-info">
        <el-alert
          :title="`已选择 ${selectedCount} 个商品`"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
      
      <el-form :model="form" label-width="100px" class="price-form">
        <el-form-item label="改价方式">
          <el-radio-group v-model="form.priceType">
            <el-radio-button label="multiply">乘以系数</el-radio-button>
            <el-radio-button label="add">固定加价</el-radio-button>
            <el-radio-button label="fixed">固定价格</el-radio-button>
            <el-radio-button label="range">随机价格</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <!-- 乘以系数 -->
        <template v-if="form.priceType === 'multiply'">
          <el-form-item label="价格系数">
            <el-input-number
              v-model="form.value"
              :min="0.1"
              :max="10"
              :step="0.1"
              :precision="2"
              style="width: 200px"
            />
            <span class="form-tip">原价 × 系数 = 新价格</span>
          </el-form-item>
        </template>
        
        <!-- 固定加价 -->
        <template v-if="form.priceType === 'add'">
          <el-form-item label="加价金额">
            <el-input-number
              v-model="form.value"
              :min="0"
              :step="1"
              :precision="2"
              style="width: 200px"
            />
            <span class="form-tip">原价 + 加价 = 新价格</span>
          </el-form-item>
        </template>
        
        <!-- 固定价格 -->
        <template v-if="form.priceType === 'fixed'">
          <el-form-item label="固定价格">
            <el-input-number
              v-model="form.value"
              :min="0"
              :step="1"
              :precision="2"
              style="width: 200px"
            />
            <span class="form-tip">所有商品统一为此价格</span>
          </el-form-item>
        </template>
        
        <!-- 随机价格 -->
        <template v-if="form.priceType === 'range'">
          <el-form-item label="价格区间">
            <div class="range-inputs">
              <el-input-number
                v-model="form.value"
                :min="0"
                :step="1"
                :precision="2"
                placeholder="最低价"
                style="width: 140px"
              />
              <span class="range-separator">-</span>
              <el-input-number
                v-model="form.value2"
                :min="0"
                :step="1"
                :precision="2"
                placeholder="最高价"
                style="width: 140px"
              />
            </div>
            <span class="form-tip">在区间内随机生成价格</span>
          </el-form-item>
        </template>
        
        <el-divider />
        
        <el-form-item label="取整方式">
          <el-select v-model="form.roundType" style="width: 200px">
            <el-option label="四舍五入" value="round" />
            <el-option label="向上取整" value="ceil" />
            <el-option label="向下取整" value="floor" />
            <el-option label="保留两位小数" value="keep" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="尾数处理">
          <el-select v-model="form.endingType" style="width: 200px">
            <el-option label="不处理" value="none" />
            <el-option label=".99 结尾" value="99" />
            <el-option label=".88 结尾" value="88" />
            <el-option label=".98 结尾" value="98" />
            <el-option label=".00 结尾" value="00" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="价格预览">
          <div class="preview-box">
            <div class="preview-item">
              <span class="preview-label">原价 100 元 →</span>
              <span class="preview-value">{{ calculatePreview(100) }} 元</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">原价 200 元 →</span>
              <span class="preview-value">{{ calculatePreview(200) }} 元</span>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="loading">
          确认修改
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  modelValue: boolean
  selectedCount: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'confirm': [data: { type: string; value: number; value2?: number; roundType: string; endingType: string }]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)

const form = ref({
  priceType: 'multiply',
  value: 1.5,
  value2: undefined as number | undefined,
  roundType: 'round',
  endingType: 'none'
})

// 计算预览价格
function calculatePreview(originalPrice: number): string {
  let newPrice = originalPrice
  
  switch (form.value.priceType) {
    case 'multiply':
      newPrice = originalPrice * form.value.value
      break
    case 'add':
      newPrice = originalPrice + form.value.value
      break
    case 'fixed':
      newPrice = form.value.value
      break
    case 'range':
      const min = form.value.value || originalPrice * 0.8
      const max = form.value.value2 || originalPrice * 1.2
      newPrice = min + Math.random() * (max - min)
      break
  }
  
  // 取整处理
  switch (form.value.roundType) {
    case 'round':
      newPrice = Math.round(newPrice)
      break
    case 'ceil':
      newPrice = Math.ceil(newPrice)
      break
    case 'floor':
      newPrice = Math.floor(newPrice)
      break
    case 'keep':
      newPrice = Math.round(newPrice * 100) / 100
      break
  }
  
  // 尾数处理
  if (form.value.endingType !== 'none') {
    const integerPart = Math.floor(newPrice)
    newPrice = integerPart + parseInt(form.value.endingType) / 100
  }
  
  return newPrice.toFixed(2)
}

function handleConfirm() {
  if (form.value.priceType === 'range' && (!form.value.value || !form.value.value2)) {
    ElMessage.warning('请输入完整的价格区间')
    return
  }
  
  emit('confirm', {
    type: form.value.priceType,
    value: form.value.value,
    value2: form.value.value2,
    roundType: form.value.roundType,
    endingType: form.value.endingType
  })
}

// 重置表单
watch(visible, (val) => {
  if (val) {
    form.value = {
      priceType: 'multiply',
      value: 1.5,
      value2: undefined,
      roundType: 'round',
      endingType: 'none'
    }
  }
})
</script>

<style scoped lang="scss">
.batch-price-dialog {
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
  max-height: 500px;
  overflow-y: auto;
}

.selected-info {
  margin-bottom: 20px;
}

.price-form {
  .form-tip {
    margin-left: 12px;
    font-size: 13px;
    color: #909399;
  }
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .range-separator {
    color: #909399;
    font-weight: 500;
  }
}

.preview-box {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  
  .preview-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px dashed #dcdfe6;
    
    &:last-child {
      border-bottom: none;
    }
  }
  
  .preview-label {
    font-size: 14px;
    color: #606266;
  }
  
  .preview-value {
    font-size: 16px;
    font-weight: 600;
    color: #f56c6c;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>