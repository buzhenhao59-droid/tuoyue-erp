<template>
  <div class="collections-page">
    <!-- 顶部 Tab 导航（妙手风格 - 青色主题） -->
    <div class="page-tabs">
      <div
        v-for="tab in tabList"
        :key="tab.key"
        class="tab-item"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <el-icon :size="18"><component :is="tab.icon" /></el-icon>
        <span>{{ tab.label }}</span>
      </div>
    </div>

    <!-- 链接采集 -->
    <div v-show="activeTab === 'link'" class="tab-content">
      <div class="main-content">
        <!-- 左侧：采集输入区 -->
        <div class="left-panel">
          <CollectionInput
            v-model:urls-text="urlsText"
            :detected-urls="detectedUrls"
            :platform-counts="platformCounts"
            :collecting="collecting"
            :config-list="configList"
            v-model:selected-config="selectedConfig"
            v-model:auto-claim="autoClaim"
            @start-collection="startCollection"
          />
        </div>

        <!-- 右侧：垂直统计栏 -->
        <div class="right-panel">
          <VerticalStats :stats="stats" @filter-change="handleStatsFilter" />
        </div>
      </div>
    </div>

    <!-- 插件采集 -->
    <div v-show="activeTab === 'plugin'" class="tab-content">
      <PluginCollection />
    </div>

    <!-- 批量导入 -->
    <div v-show="activeTab === 'import'" class="tab-content">
      <BulkImport :config-list="configList" @import-success="fetchData" />
    </div>

    <!-- AI选品 -->
    <div v-show="activeTab === 'ai'" class="tab-content">
      <AISelection />
    </div>

    <!-- 采集配置 -->
    <div v-show="activeTab === 'config'" class="tab-content">
      <CollectionConfigPanel />
    </div>

    <!-- 商品列表区 -->
    <el-card class="table-card" shadow="never">
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <div class="filter-left">
          <el-select v-model="filter.platform" placeholder="来源平台" clearable style="width: 140px">
            <el-option label="全部平台" value="" />
            <el-option label="1688" value="1688" />
            <el-option label="淘宝" value="taobao" />
            <el-option label="天猫" value="tmall" />
            <el-option label="拼多多" value="pdd" />
            <el-option label="抖店" value="douyin" />
            <el-option label="京东" value="jd" />
            <el-option label="速卖通" value="aliexpress" />
            <el-option label="Shopee" value="shopee" />
            <el-option label="Lazada" value="lazada" />
            <el-option label="亚马逊" value="amazon" />
            <el-option label="eBay" value="ebay" />
            <el-option label="TikTok Shop" value="tiktok" />
          </el-select>
          
          <el-select v-model="filter.status" placeholder="商品状态" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="待认领" value="pending" />
            <el-option label="已认领" value="claimed" />
            <el-option label="编辑中" value="editing" />
            <el-option label="已发布" value="published" />
            <el-option label="已忽略" value="ignored" />
          </el-select>

          <el-date-picker
            v-model="filter.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
          />

          <el-input
            v-model="filter.keyword"
            placeholder="搜索标题/ID/链接"
            clearable
            style="width: 200px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </div>
        
        <div class="filter-right">
          <el-button type="success" :disabled="!selectedRows.length" @click="handleBatchClaim">
            <el-icon><Check /></el-icon>
            批量认领
          </el-button>
          <el-button type="warning" :disabled="!selectedRows.length" @click="handleBatchEditPrice">
            <el-icon><Edit /></el-icon>
            批量改价
          </el-button>
          <el-button type="primary" :disabled="!selectedRows.length" @click="handleBatchPush">
            <el-icon><Upload /></el-icon>
            批量推送
          </el-button>
          <el-button type="danger" :disabled="!selectedRows.length" @click="handleBatchIgnore">
            <el-icon><Delete /></el-icon>
            批量忽略
          </el-button>
        </div>
      </div>

      <!-- 商品表格 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        @selection-change="handleSelectionChange"
        stripe
        class="product-table"
      >
        <el-table-column type="selection" width="50" />
        
        <el-table-column label="商品信息" min-width="320">
          <template #default="{ row }">
            <div class="product-cell">
              <el-image :src="row.main_image" class="product-thumb" fit="cover">
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="product-info">
                <div class="product-title" :title="row.title">{{ row.title }}</div>
                <div class="product-meta">
                  <span class="platform-tag" :style="{ background: row.platform_color }">
                    {{ row.source_platform }}
                  </span>
                  <span class="product-id">ID: {{ row.source_id }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="价格" width="140">
          <template #default="{ row }">
            <div class="price-cell">
              <div class="current-price">{{ row.price_display }}</div>
              <div v-if="row.original_price_min" class="original-price">
                原价: ¥{{ row.original_price_min }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="SKU" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.sku_count }}个</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="认领人" width="120">
          <template #default="{ row }">
            <span v-if="row.claimed_by_name">{{ row.claimed_by_name }}</span>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>

        <el-table-column label="采集时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" type="primary" link @click="handleClaim(row)">
              认领
            </el-button>
            <el-button v-if="row.status === 'pending'" type="danger" link @click="handleIgnore(row)">
              忽略
            </el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handlePush(row)">推送</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[20, 50, 100, 200]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 批量改价对话框 -->
    <BatchPriceDialog 
      v-model="showPriceDialog" 
      :selected-count="selectedRows.length"
      @confirm="handlePriceConfirm"
    />

    <!-- 批量推送对话框 -->
    <BatchPushDialog
      v-model="showPushDialog"
      :selected-count="selectedRows.length"
      :selected-ids="selectedRows.map(r => r.id)"
      @success="handlePushSuccess"
    />

    <!-- 商品详情抽屉 -->
    <ProductDetailDrawer
      v-model="showDetailDrawer"
      :product="selectedProduct"
      @saved="fetchData"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Link, Search, Check, Edit, Delete, Picture } from '@element-plus/icons-vue'
import type { CollectedProduct, CollectionConfig } from '@/types/collections'

import CollectionInput from './components/CollectionInput.vue'
import VerticalStats from './components/VerticalStats.vue'
import BatchPriceDialog from './components/BatchPriceDialog.vue'
import BatchPushDialog from './components/BatchPushDialog.vue'
import ProductDetailDrawer from './components/ProductDetailDrawer.vue'
import CollectionConfigPanel from './components/CollectionConfigPanel.vue'
import PluginCollection from './components/PluginCollection.vue'
import BulkImport from './components/BulkImport.vue'
import AISelection from './components/AISelection.vue'

import {
  getCollectedProducts,
  createCollectionTask,
  getCollectionConfigs,
  claimProduct,
  ignoreProduct,
  batchClaimProducts,
  batchIgnoreProducts,
  batchUpdatePrice,
} from '@/api/collections'

const activeTab = ref('link')
const tabList = [
  { key: 'link', label: '链接采集', icon: 'Link' },
  { key: 'plugin', label: '插件采集', icon: 'Download' },
  { key: 'import', label: '批量导入', icon: 'Upload' },
  { key: 'ai', label: 'AI选品', icon: 'Setting' },
  { key: 'config', label: '采集配置', icon: 'Setting' },
]

const urlsText = ref('')
const selectedConfig = ref<number>()
const collecting = ref(false)
const configList = ref<CollectionConfig[]>([])
const autoClaim = ref(false)

const detectedUrls = computed(() => {
  const urls = urlsText.value.split(/\n|\$\$/).filter(url => url.trim().startsWith('http'))
  return urls.map(url => url.trim())
})

const platformCounts = computed(() => {
  const counts: Record<string, number> = {}
  detectedUrls.value.forEach(url => {
    const platform = detectPlatform(url)
    counts[platform] = (counts[platform] || 0) + 1
  })
  return counts
})

function detectPlatform(url: string): string {
  const lower = url.toLowerCase()
  if (lower.includes('1688.com')) return '1688'
  if (lower.includes('taobao.com')) return '淘宝'
  if (lower.includes('tmall.com')) return '天猫'
  if (lower.includes('shopee')) return 'Shopee'
  if (lower.includes('lazada')) return 'Lazada'
  if (lower.includes('tiktok')) return 'TikTok'
  return '其他'
}

const stats = reactive({
  total: 0,
  pending: 0,
  claimed: 0,
  editing: 0,
  published: 0,
  ignored: 0
})

function handleStatsFilter(status: string) {
  filter.status = status
  handleSearch()
}

const loading = ref(false)
const tableData = ref<CollectedProduct[]>([])
const selectedRows = ref<CollectedProduct[]>([])

const filter = reactive({
  platform: '',
  status: '',
  dateRange: null as Date[] | null,
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const showPriceDialog = ref(false)
const showPushDialog = ref(false)
const showDetailDrawer = ref(false)
const selectedProduct = ref<CollectedProduct | null>(null)

async function fetchData() {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
      platform: filter.platform,
      status: filter.status,
      keyword: filter.keyword
    }

    if (filter.dateRange && filter.dateRange.length === 2) {
      params.start_date = filter.dateRange[0].toISOString().split('T')[0]
      params.end_date = filter.dateRange[1].toISOString().split('T')[0]
    }
    
    const res: any = await getCollectedProducts(params)
    tableData.value = res.results || []
    pagination.total = res.count || 0
    updateStats(res.stats || {})
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

function updateStats(statsData: any) {
  stats.total = statsData.total || pagination.total
  stats.pending = statsData.pending || 0
  stats.claimed = statsData.claimed || 0
  stats.editing = statsData.editing || 0
  stats.published = statsData.published || 0
  stats.ignored = statsData.ignored || 0
}

async function fetchConfigs() {
  try {
    const res: any = await getCollectionConfigs()
    configList.value = res.results || []
    const defaultConfig = configList.value.find(c => c.is_default)
    if (defaultConfig) {
      selectedConfig.value = defaultConfig.id
    }
  } catch (error) {
    console.error('获取配置失败', error)
  }
}

async function startCollection() {
  if (!urlsText.value.trim()) {
    ElMessage.warning('请输入采集链接')
    return
  }
  
  collecting.value = true
  try {
    await createCollectionTask({
      urls_text: urlsText.value,
      config: selectedConfig.value,
      task_type: 'link',
      auto_claim: autoClaim.value
    })
    ElMessage.success('采集任务已创建')
    urlsText.value = ''
    fetchData()
  } catch (error) {
    ElMessage.error('创建任务失败')
  } finally {
    collecting.value = false
  }
}

function handleSelectionChange(rows: CollectedProduct[]) {
  selectedRows.value = rows
}

async function handleBatchClaim() {
  const ids = selectedRows.value.map(r => r.id)
  try {
    await batchClaimProducts(ids)
    ElMessage.success(`成功认领 ${ids.length} 个商品`)
    fetchData()
  } catch (error) {
    ElMessage.error('批量认领失败')
  }
}

async function handleBatchIgnore() {
  const ids = selectedRows.value.map(r => r.id)
  try {
    await ElMessageBox.confirm(`确定忽略选中的 ${ids.length} 个商品？`, '提示', { type: 'warning' })
    await batchIgnoreProducts(ids)
    ElMessage.success('批量忽略成功')
    fetchData()
  } catch {
    // Cancelled
  }
}

function handleBatchEditPrice() {
  showPriceDialog.value = true
}

function handleBatchPush() {
  showPushDialog.value = true
}

async function handlePriceConfirm(data: { type: string, value: number, value2?: number }) {
  const ids = selectedRows.value.map(r => r.id)
  try {
    await batchUpdatePrice({
      ids,
      price_type: data.type,
      value: data.value,
      value2: data.value2
    })
    ElMessage.success('批量改价成功')
    showPriceDialog.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('批量改价失败')
  }
}

function handlePushSuccess() {
  showPushDialog.value = false
  fetchData()
}

async function handleClaim(row: CollectedProduct) {
  try {
    await claimProduct(row.id)
    ElMessage.success('认领成功')
    fetchData()
  } catch (error) {
    ElMessage.error('认领失败')
  }
}

async function handleIgnore(row: CollectedProduct) {
  try {
    await ElMessageBox.confirm('确定忽略此商品？', '提示', { type: 'warning' })
    await ignoreProduct(row.id)
    ElMessage.success('已忽略')
    fetchData()
  } catch {
    // Cancelled
  }
}

function handleEdit(row: CollectedProduct) {
  selectedProduct.value = row
  showDetailDrawer.value = true
}

function handlePush(row: CollectedProduct) {
  selectedRows.value = [row]
  showPushDialog.value = true
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function resetFilter() {
  filter.platform = ''
  filter.status = ''
  filter.dateRange = null
  filter.keyword = ''
  handleSearch()
}

function handleSizeChange(size: number) {
  pagination.pageSize = size
  fetchData()
}

function handlePageChange(page: number) {
  pagination.page = page
  fetchData()
}

function getStatusType(status: string): string {
  const map: Record<string, string> = {
    pending: 'info',
    claimed: 'warning',
    editing: 'primary',
    published: 'success',
    ignored: 'danger',
    failed: 'danger'
  }
  return map[status] || 'info'
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待认领',
    claimed: '已认领',
    editing: '编辑中',
    published: '已发布',
    ignored: '已忽略',
    failed: '采集失败'
  }
  return map[status] || status
}

function formatDate(date: string): string {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchData()
  fetchConfigs()
})

watch(() => filter.status, () => {
  pagination.page = 1
  fetchData()
})
</script>

<style scoped lang="scss">
$primary-color: #00b5ad;

.collections-page {
  padding: 0;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-tabs {
  display: flex;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  
  .tab-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 14px 24px;
    cursor: pointer;
    font-size: 14px;
    color: #606266;
    border-bottom: 2px solid transparent;
    transition: all 0.3s;
    
    &:hover {
      color: $primary-color;
    }
    
    &.active {
      color: $primary-color;
      border-bottom-color: $primary-color;
      font-weight: 500;
    }
  }
}

.tab-content {
  padding: 16px 20px;
}

.main-content {
  display: flex;
  gap: 16px;
}

.left-panel {
  flex: 1;
  min-width: 0;
}

.right-panel {
  width: 200px;
  flex-shrink: 0;
}

.table-card {
  margin: 0 20px 20px;
  
  :deep(.el-card__body) {
    padding: 0;
  }
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  flex-wrap: wrap;
  gap: 12px;
  
  .filter-left {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  .filter-right {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
}

.product-table {
  :deep(.el-table__cell) {
    padding: 12px 0;
  }
}

.product-cell {
  display: flex;
  gap: 12px;
  
  .product-thumb {
    width: 60px;
    height: 60px;
    border-radius: 4px;
    flex-shrink: 0;
  }

  .image-error {
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f7fa;
    color: #909399;
    border-radius: 4px;
  }
  
  .product-info {
    flex: 1;
    min-width: 0;
    
    .product-title {
      font-size: 13px;
      line-height: 1.5;
      color: #303133;
      margin-bottom: 8px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .product-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .platform-tag {
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 11px;
        color: #fff;
        font-weight: 500;
      }

      .product-id {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}

.price-cell {
  .current-price {
    font-size: 14px;
    font-weight: 600;
    color: #f56c6c;
  }

  .original-price {
    font-size: 12px;
    color: #909399;
    text-decoration: line-through;
    margin-top: 4px;
  }
}

.pagination-wrapper {
  padding: 16px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
}

.text-gray {
  color: #909399;
}
</style>
