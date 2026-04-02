<template>
  <div class="collection-input">
    <el-card shadow="never">
      <!-- 平台矩阵图标 - 妙手风格 -->
      <div class="platform-matrix">
        <div
          v-for="platform in platforms"
          :key="platform.code"
          class="platform-item"
          :class="{ active: selectedPlatform === platform.code }"
          @click="selectedPlatform = platform.code"
        >
          <div class="platform-icon" :style="{ background: platform.color }">
            <img v-if="platform.logo" :src="platform.logo" class="platform-logo" />
            <span v-else>{{ platform.icon }}</span>
          </div>
          <span class="platform-name">{{ platform.name }}</span>
        </div>
      </div>

      <!-- 富文本输入框 -->
      <div class="input-section">
        <el-input
          :model-value="urlsText"
          @update:model-value="$emit('update:urlsText', $event)"
          type="textarea"
          :rows="10"
          placeholder="请粘贴商品链接，支持多个链接，使用 $$ 或换行分隔&#10;示例：&#10;https://detail.1688.com/offer/123456.html&#10;$$&#10;https://item.taobao.com/item.htm?id=123456"
          resize="none"
          class="url-input"
        />
        
        <!-- 输入统计 -->
        <div class="input-stats">
          <div class="stats-left">
            <span class="detected-count">
              <el-icon><Link /></el-icon>
              已识别 <strong>{{ detectedUrls.length }}</strong> 个链接
            </span>
            <div class="platform-tags">
              <el-tag
                v-for="(count, platform) in platformCounts"
                :key="platform"
                size="small"
                :type="getPlatformTagType(platform)"
                effect="light"
                class="platform-tag"
              >
                {{ platform }} {{ count }}
              </el-tag>
            </div>
          </div>
          <el-button type="primary" link @click="clearInput">
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div class="action-bar">
        <div class="action-left">
          <el-select
            :model-value="selectedConfig"
            @update:model-value="$emit('update:selectedConfig', $event)"
            placeholder="选择采集配置"
            style="width: 200px"
            class="config-select"
          >
            <el-option
              v-for="config in configList"
              :key="config.id"
              :label="config.name"
              :value="config.id"
            />
          </el-select>
          
          <el-checkbox
            :model-value="autoClaim"
            @update:model-value="$emit('update:autoClaim', $event)"
            class="auto-claim-checkbox"
          >
            自动认领
          </el-checkbox>
        </div>
        
        <el-button
          type="primary"
          size="large"
          :loading="collecting"
          :disabled="!detectedUrls.length"
          @click="$emit('startCollection')"
          class="collect-btn"
        >
          <el-icon><VideoPlay /></el-icon>
          开始采集
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Link, Delete, VideoPlay } from '@element-plus/icons-vue'
import type { CollectionConfig } from '@/types/collections'

interface Props {
  urlsText: string
  detectedUrls: string[]
  platformCounts: Record<string, number>
  collecting: boolean
  configList: CollectionConfig[]
  selectedConfig?: number
  autoClaim: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:urlsText': [value: string]
  'update:selectedConfig': [value: number | undefined]
  'update:autoClaim': [value: boolean]
  'startCollection': []
}>()

// 平台矩阵数据 - 妙手 ERP 完整平台列表
const platforms = [
  { code: '1688', name: '1688', icon: '1688', color: '#FF6A00' },
  { code: 'taobao', name: '淘宝', icon: '淘', color: '#FF5000' },
  { code: 'tmall', name: '天猫', icon: '猫', color: '#FF0036' },
  { code: 'pdd', name: '拼多多', icon: '拼', color: '#E02E24' },
  { code: 'douyin', name: '抖店', icon: '抖', color: '#000000' },
  { code: 'jd', name: '京东', icon: 'JD', color: '#E4393C' },
  { code: 'aliexpress', name: '速卖通', icon: 'AE', color: '#FF4747' },
  { code: 'shopee', name: 'Shopee', icon: 'S', color: '#EE4D2D' },
  { code: 'lazada', name: 'Lazada', icon: 'L', color: '#0F156D' },
  { code: 'amazon', name: '亚马逊', icon: 'A', color: '#FF9900' },
  { code: 'ebay', name: 'eBay', icon: 'e', color: '#E53238' },
  { code: 'tiktok', name: 'TikTok Shop', icon: 'TT', color: '#000000' },
]

const selectedPlatform = ref('')

function getPlatformTagType(platform: string): string {
  const map: Record<string, string> = {
    '1688': 'warning',
    '淘宝': 'danger',
    '天猫': 'danger',
    '拼多多': 'danger',
    '抖店': 'info',
    '京东': 'danger',
    '速卖通': 'warning',
    'Shopee': 'success',
    'Lazada': 'primary',
    '亚马逊': 'warning',
    'eBay': 'danger',
    'TikTok Shop': 'info',
  }
  return map[platform] || 'info'
}

function clearInput() {
  emit('update:urlsText', '')
}
</script>

<style scoped lang="scss">
$primary-color: #00b5ad;

.collection-input {
  :deep(.el-card__body) {
    padding: 20px;
  }
}

// 平台矩阵 - 妙手风格
.platform-matrix {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px dashed #e4e7ed;
}

.platform-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s;
  border: 2px solid transparent;
  min-width: 60px;
  
  &:hover {
    background: #f5f7fa;
    transform: translateY(-2px);
  }
  
  &.active {
    border-color: $primary-color;
    background: rgba($primary-color, 0.05);
  }
}

.platform-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.platform-logo {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.platform-name {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
}

// 输入区域
.input-section {
  margin-bottom: 16px;
}

.url-input {
  :deep(.el-textarea__inner) {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 13px;
    line-height: 1.6;
    padding: 12px;
    border-radius: 8px;
  }
}

.input-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  
  .stats-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .detected-count {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    color: #606266;
    
    strong {
      color: $primary-color;
      font-size: 18px;
      margin: 0 4px;
    }
  }
  
  .platform-tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  .platform-tag {
    font-size: 12px;
  }
}

// 操作栏
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.action-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.config-select {
  :deep(.el-input__wrapper) {
    border-radius: 6px;
  }
}

.auto-claim-checkbox {
  :deep(.el-checkbox__label) {
    font-size: 14px;
  }
}

.collect-btn {
  min-width: 140px;
  height: 44px;
  font-size: 15px;
  font-weight: 500;
  background: $primary-color;
  border-color: $primary-color;
  border-radius: 8px;
  
  &:hover {
    background: darken($primary-color, 5%);
    border-color: darken($primary-color, 5%);
  }
  
  &:disabled {
    background: #c0c4cc;
    border-color: #c0c4cc;
  }
  
  .el-icon {
    font-size: 18px;
    margin-right: 6px;
  }
}
</style>