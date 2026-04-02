// 采集模块类型定义（妙手 ERP 深度克隆版）

// 采集配置
export interface CollectionConfig {
  id: number
  name: string
  price_rule: 'fixed' | 'tier' | 'formula'
  price_multiplier: number
  price_addition: number
  min_price: number | null
  max_price: number | null
  auto_translate: boolean
  translate_to: string
  download_images: boolean
  watermark_remove: boolean
  image_compress: boolean
  default_sku_attrs: Array<{
    name: string
    values: string[]
  }>
  default_stock: number
  keyword_filter: {
    include?: string[]
    exclude?: string[]
  }
  category_mapping: Record<string, string>
  is_default: boolean
  created_at: string
  updated_at: string
  // 扩展字段
  tier_rules?: Array<{
    min: number
    max: number
    multiplier: number
  }>
  price_formula?: string
}

// SKU 属性
export interface SKUAttribute {
  id?: string
  name: string
  values: Array<{
    id?: string
    name: string
    image?: string
  }>
}

// SKU 项
export interface SKUItem {
  sku_id: string
  attributes: Record<string, string>
  price: number
  original_price?: number
  stock: number
  image?: string
  barcode?: string
}

// 采集商品
export interface CollectedProduct {
  id: number
  source_url: string
  source_platform: string
  source_id: string
  platform_color: string
  platform_icon: string
  
  collect_status: string
  collect_error?: string
  
  title: string
  title_en?: string
  description?: string
  description_en?: string
  
  main_image: string
  main_image_local?: string
  images: string[]
  images_local?: string[]
  
  original_price_min?: number
  original_price_max?: number
  price_min?: number
  price_max?: number
  price_display: string
  currency: string
  
  source_category_name?: string
  target_category_id?: string
  target_category_name?: string
  
  brand?: string
  material?: string
  origin?: string
  weight?: number
  length?: number
  width?: number
  height?: number
  
  sku_attributes: SKUAttribute[]
  skus: SKUItem[]
  sku_count: number
  
  status: 'pending' | 'claimed' | 'editing' | 'published' | 'ignored' | 'failed'
  claimed_by?: number
  claimed_by_name?: string
  claimed_at?: string
  claim_note?: string
  
  editor?: number
  editor_name?: string
  editing_at?: string
  
  published_shops?: Array<{
    shop_id: number
    platform: string
    status: string
    time: string
  }>
  
  raw_data?: Record<string, any>
  created_at: string
  updated_at: string
}

// 采集任务
export interface CollectionTask {
  id: number
  task_no: string
  task_type: 'link' | 'plugin' | 'api' | 'import'
  name?: string
  config?: number
  config_name?: string
  source_urls: Array<{
    url: string
    platform: string
    status: string
    error?: string
  }>
  source_platform?: string
  total_count: number
  success_count: number
  fail_count: number
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'partial'
  error_msg?: string
  retry_count: number
  progress_percent: number
  started_at?: string
  completed_at?: string
  created_at: string
  user: number
  user_name?: string
}

// 采集统计
export interface CollectionStats {
  total: number
  pending: number
  claimed: number
  editing: number
  published: number
  ignored: number
  failed: number
  by_platform: Record<string, number>
}

// 筛选参数
export interface CollectionFilter {
  platform?: string
  status?: string
  dateRange?: Date[]
  keyword?: string
}

// 店铺
export interface Shop {
  id: number
  name: string
  platform: string
  shop_id: string
  status: string
}
