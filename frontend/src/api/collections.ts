import request from '@/utils/request'
import type { 
  CollectedProduct, 
  CollectionTask, 
  CollectionConfig,
  CollectionStats 
} from '@/types/collections'

// ===== 采集配置 =====
export function getCollectionConfigs() {
  return request<{
    count: number
    results: CollectionConfig[]
  }>({
    url: '/v1/collections/configs/',
    method: 'get'
  })
}

export function createCollectionConfig(data: Partial<CollectionConfig>) {
  return request<CollectionConfig>({
    url: '/v1/collections/configs/',
    method: 'post',
    data
  })
}

export function updateCollectionConfig(id: number, data: Partial<CollectionConfig>) {
  return request<CollectionConfig>({
    url: `/v1/collections/configs/${id}/`,
    method: 'put',
    data
  })
}

export function deleteCollectionConfig(id: number) {
  return request({
    url: `/v1/collections/configs/${id}/`,
    method: 'delete'
  })
}

export function setDefaultConfig(id: number) {
  return request({
    url: `/v1/collections/configs/${id}/set_default/`,
    method: 'post'
  })
}

// ===== 采集任务 =====
export function getCollectionTasks(params?: {
  page?: number
  page_size?: number
  status?: string
}) {
  return request<{
    count: number
    results: CollectionTask[]
  }>({
    url: '/v1/collections/tasks/',
    method: 'get',
    params
  })
}

export function createCollectionTask(data: {
  urls_text: string
  config?: number
  task_type: string
  name?: string
  auto_claim?: boolean
}) {
  return request<CollectionTask>({
    url: '/v1/collections/tasks/',
    method: 'post',
    data
  })
}

export function retryCollectionTask(id: number) {
  return request({
    url: `/v1/collections/tasks/${id}/retry/`,
    method: 'post'
  })
}

// ===== 采集商品 =====
export function getCollectedProducts(params?: {
  page?: number
  page_size?: number
  platform?: string
  status?: string
  keyword?: string
  start_date?: string
  end_date?: string
}) {
  return request<{
    count: number
    results: CollectedProduct[]
    stats?: CollectionStats
  }>({
    url: '/v1/collections/products/',
    method: 'get',
    params
  })
}

export function getCollectedProductDetail(id: number) {
  return request<CollectedProduct>({
    url: `/v1/collections/products/${id}/`,
    method: 'get'
  })
}

export function updateCollectedProduct(id: number, data: Partial<CollectedProduct>) {
  return request<CollectedProduct>({
    url: `/v1/collections/products/${id}/`,
    method: 'put',
    data
  })
}

// ===== 商品操作 =====
export function claimProduct(id: number) {
  return request({
    url: `/v1/collections/products/${id}/claim/`,
    method: 'post'
  })
}

export function ignoreProduct(id: number) {
  return request({
    url: `/v1/collections/products/${id}/ignore/`,
    method: 'post'
  })
}

export function startEditProduct(id: number) {
  return request({
    url: `/v1/collections/products/${id}/start_edit/`,
    method: 'post'
  })
}

export function publishProduct(id: number, data: { shop_ids: number[] }) {
  return request({
    url: `/v1/collections/products/${id}/publish/`,
    method: 'post',
    data
  })
}

// ===== 批量操作 =====
export function batchClaimProducts(ids: number[]) {
  return request({
    url: '/v1/collections/products/batch_claim/',
    method: 'post',
    data: { ids }
  })
}

export function batchIgnoreProducts(ids: number[]) {
  return request({
    url: '/v1/collections/products/batch_ignore/',
    method: 'post',
    data: { ids }
  })
}

export function batchUpdatePrice(data: {
  ids: number[]
  price_type: string
  value: number
  value2?: number
}) {
  return request({
    url: '/v1/collections/products/batch_update_price/',
    method: 'post',
    data
  })
}

export function batchPushToShop(data: {
  ids: number[]
  shop_ids: number[]
  config_id?: number
}) {
  return request({
    url: '/v1/collections/products/batch_push/',
    method: 'post',
    data
  })
}

// ===== 统计 =====
export function getCollectionStats() {
  return request<CollectionStats>({
    url: '/v1/collections/stats/',
    method: 'get'
  })
}

// ===== 插件 Webhook =====
export function pluginWebhook(data: {
  plugin_id: string
  plugin_version: string
  url: string
  platform: string
  data: Record<string, any>
}) {
  return request({
    url: '/v1/collections/plugin_webhook/',
    method: 'post',
    data
  })
}

// ===== 批量导入 =====
export function batchImportProducts(data: {
  file: File
  platform: string
  config_id?: number
}) {
  const formData = new FormData()
  formData.append('file', data.file)
  formData.append('platform', data.platform)
  if (data.config_id) {
    formData.append('config_id', data.config_id.toString())
  }

  return request({
    url: '/v1/collections/batch_import/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// ===== AI选品 =====
export function aiSelectProducts(params: {
  platform?: string
  category?: string
  min_price?: number
  max_price?: number
  keyword?: string
  limit?: number
}) {
  return request<{
    products: CollectedProduct[]
    analysis: {
      market_trend: string
      competition_level: string
      profit_potential: string
      recommendation_score: number
    }
  }>({
    url: '/v1/collections/ai_select/',
    method: 'get',
    params
  })
}
