<template>
  <div class="vertical-stats">
    <el-card shadow="never" class="stats-card">
      <div class="stats-header">
        <span class="stats-title">商品状态</span>
      </div>
      
      <div class="stats-list">
        <div
          v-for="item in statsList"
          :key="item.key"
          class="stats-item"
          :class="{ active: activeStatus === item.key }"
          @click="handleClick(item.key)"
        >
          <div class="stats-item-left">
            <div class="stats-dot" :style="{ background: item.color }"></div>
            <span class="stats-label">{{ item.label }}</span>
          </div>
          <div class="stats-count" :style="{ color: item.color }">
            {{ stats[item.key] || 0 }}
          </div>
        </div>
      </div>
      
      <div class="stats-total">
        <div class="stats-item">
          <div class="stats-item-left">
            <div class="stats-dot" style="background: #909399;"></div>
            <span class="stats-label">全部商品</span>
          </div>
          <div class="stats-count" style="color: #303133; font-weight: 600;">
            {{ stats.total || 0 }}
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 快速操作 -->
    <el-card shadow="never" class="quick-actions">
      <div class="stats-header">
        <span class="stats-title">快速操作</span>
      </div>
      
      <div class="action-list">
        <el-button type="primary" plain class="action-btn" @click="$emit('action', 'createTask')">
          <el-icon><Plus /></el-icon>
          创建采集任务
        </el-button>
        <el-button type="success" plain class="action-btn" @click="$emit('action', 'batchClaim')">
          <el-icon><Check /></el-icon>
          批量认领
        </el-button>
        <el-button type="warning" plain class="action-btn" @click="$emit('action', 'batchPrice')">
          <el-icon><Edit /></el-icon>
          批量改价
        </el-button>
        <el-button type="info" plain class="action-btn" @click="$emit('action', 'export')">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Check, Edit, Download } from '@element-plus/icons-vue'

interface Stats {
  total: number
  pending: number
  claimed: number
  editing: number
  published: number
  ignored: number
}

type StatsKey = Exclude<keyof Stats, 'total'>

interface Props {
  stats: Stats
}

const { stats } = defineProps<Props>()

const emit = defineEmits<{
  'filter-change': [status: string]
  'action': [action: string]
}>()

const activeStatus = ref('')

const statsList: Array<{ key: StatsKey; label: string; color: string }> = [
  { key: 'pending', label: '待认领', color: '#e6a23c' },
  { key: 'claimed', label: '已认领', color: '#409eff' },
  { key: 'editing', label: '编辑中', color: '#67c23a' },
  { key: 'published', label: '已发布', color: '#00b5ad' },
  { key: 'ignored', label: '已忽略', color: '#909399' },
]

function handleClick(status: string) {
  activeStatus.value = activeStatus.value === status ? '' : status
  emit('filter-change', activeStatus.value)
}
</script>

<style scoped lang="scss">
$primary-color: #00b5ad;

.vertical-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-card,
.quick-actions {
  :deep(.el-card__body) {
    padding: 16px;
  }
}

.stats-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.stats-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stats-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    background: #f5f7fa;
  }
  
  &.active {
    background: rgba($primary-color, 0.1);
  }
}

.stats-item-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stats-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.stats-label {
  font-size: 14px;
  color: #606266;
}

.stats-count {
  font-size: 16px;
  font-weight: 600;
}

.stats-total {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #ebeef5;
}

// 快速操作
.action-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-btn {
  width: 100%;
  justify-content: flex-start;
  padding: 12px;
  border-radius: 6px;
  
  .el-icon {
    margin-right: 8px;
  }
}
</style>