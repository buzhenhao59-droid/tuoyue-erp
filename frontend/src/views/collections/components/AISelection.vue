<template>
  <div class="ai-selection">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>AI 智能选品</span>
          <el-tag type="success" effect="dark">Beta</el-tag>
        </div>
      </template>

      <div class="ai-content">
        <!-- 筛选条件 -->
        <div class="filter-section">
          <el-form :model="filterForm" inline>
            <el-form-item label="目标平台">
              <el-select v-model="filterForm.platform" placeholder="选择平台" clearable style="width: 150px">
                <el-option label="Shopee" value="shopee" />
                <el-option label="Lazada" value="lazada" />
                <el-option label="TikTok" value="tiktok" />
              </el-select>
            </el-form-item>

            <el-form-item label="类目">
              <el-cascader
                v-model="filterForm.category"
                :options="categoryOptions"
                :props="{ checkStrictly: true, emitPath: false }"
                placeholder="选择类目"
                clearable
                style="width: 180px"
              />
            </el-form-item>

            <el-form-item label="价格区间">
              <el-input-number
                v-model="filterForm.min_price"
                :min="0"
                placeholder="最低价"
                style="width: 120px"
              />
              <span class="price-separator">-</span>
              <el-input-number
                v-model="filterForm.max_price"
                :min="0"
                placeholder="最高价"
                style="width: 120px"
              />
            </el-form-item>

            <el-form-item label="关键词">
              <el-input
                v-model="filterForm.keyword"
                placeholder="输入关键词"
                clearable
                style="width: 150px"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="analyzing" @click="startAnalysis">
                <el-icon><Search /></el-icon>
                智能分析
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 分析结果 -->
        <div v-if="showResults" class="results-section">
          <el-divider />
          
          <!-- 市场分析 -->
          <div class="market-analysis">
            <h3>市场分析</h3>
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="analysis-card">
                  <div class="analysis-icon" style="background: #e6f7ff; color: #1890ff;">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                  <div class="analysis-info">
                    <div class="analysis-label">市场趋势</div>
                    <div class="analysis-value" :class="analysis.market_trend">
                      {{ getTrendText(analysis.market_trend) }}
                    </div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="analysis-card">
                  <div class="analysis-icon" style="background: #fff7e6; color: #fa8c16;">
                    <el-icon><Compass /></el-icon>
                  </div>
                  <div class="analysis-info">
                    <div class="analysis-label">竞争程度</div>
                    <div class="analysis-value" :class="analysis.competition_level">
                      {{ getCompetitionText(analysis.competition_level) }}
                    </div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="analysis-card">
                  <div class="analysis-icon" style="background: #f6ffed; color: #52c41a;">
                    <el-icon><Money /></el-icon>
                  </div>
                  <div class="analysis-info">
                    <div class="analysis-label">盈利潜力</div>
                    <div class="analysis-value" :class="analysis.profit_potential">
                      {{ getProfitText(analysis.profit_potential) }}
                    </div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="analysis-card">
                  <div class="analysis-icon" style="background: #fff0f6; color: #eb2f96;">
                    <el-icon><Star /></el-icon>
                  </div>
                  <div class="analysis-info">
                    <div class="analysis-label">推荐评分</div>
                    <div class="analysis-value score">{{ analysis.recommendation_score }}分</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 推荐商品 -->
          <div class="products-section">
            <div class="section-header">
              <h3>推荐商品</h3>
              <div class="header-actions">
                <el-checkbox v-model="selectAll" @change="handleSelectAll">全选</el-checkbox>
                <el-button type="primary" :disabled="!selectedProducts.length" @click="batchCollect">
                  批量采集 ({{ selectedProducts.length }})
                </el-button>
              </div>
            </div>

            <el-table :data="recommendProducts" stripe @selection-change="handleSelectionChange">
              <el-table-column type="selection" width="50" />
              
              <el-table-column label="商品信息" min-width="300">
                <template #default="{ row }">
                  <div class="product-cell">
                    <el-image :src="row.main_image" class="product-thumb" fit="cover" />
                    <div class="product-info">
                      <div class="product-title">{{ row.title }}</div>
                      <div class="product-tags">
                        <el-tag size="small" type="success">推荐指数 {{ row.score }}%</el-tag>
                      </div>
                    </div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="预估价格" width="120">
                <template #default="{ row }">
                  <div class="price-range">
                    <div class="selling-price">¥{{ row.estimated_price }}</div>
                    <div class="profit">利润 ¥{{ row.estimated_profit }}</div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="市场数据" width="150">
                <template #default="{ row }">
                  <div class="market-data">
                    <div>销量: {{ row.sales_volume }}</div>
                    <div>竞争: {{ row.competition_count }}家</div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link @click="collectProduct(row)">
                    立即采集
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="设置筛选条件，开始AI智能选品">
            <template #image>
              <el-icon :size="80" color="#dcdfe6"><Cpu /></el-icon>
            </template>
          </el-empty>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, TrendCharts, Compass, Money, Star, Cpu } from '@element-plus/icons-vue'
import { aiSelectProducts } from '@/api/collections'
import type { CollectedProduct } from '@/types/collections'

const analyzing = ref(false)
const showResults = ref(false)
const selectAll = ref(false)
const selectedProducts = ref<CollectedProduct[]>([])

const filterForm = reactive({
  platform: '',
  category: '',
  min_price: undefined as number | undefined,
  max_price: undefined as number | undefined,
  keyword: '',
})

const analysis = reactive({
  market_trend: 'up',
  competition_level: 'medium',
  profit_potential: 'high',
  recommendation_score: 85,
})

const recommendProducts = ref<any[]>([])

const categoryOptions = [
  {
    value: '1',
    label: '服装鞋包',
    children: [
      { value: '11', label: '女装' },
      { value: '12', label: '男装' },
      { value: '13', label: '鞋靴' },
    ],
  },
  {
    value: '2',
    label: '数码家电',
    children: [
      { value: '21', label: '手机配件' },
      { value: '22', label: '电脑配件' },
    ],
  },
]

async function startAnalysis() {
  analyzing.value = true
  try {
    const res: any = await aiSelectProducts({
      platform: filterForm.platform,
      category: filterForm.category,
      min_price: filterForm.min_price,
      max_price: filterForm.max_price,
      keyword: filterForm.keyword,
      limit: 20,
    })

    Object.assign(analysis, res.analysis)
    recommendProducts.value = res.products || []
    showResults.value = true
  } catch (error) {
    ElMessage.error('分析失败')
  } finally {
    analyzing.value = false
  }
}

function getTrendText(trend: string): string {
  const map: Record<string, string> = {
    up: '上升',
    down: '下降',
    stable: '平稳',
  }
  return map[trend] || trend
}

function getCompetitionText(level: string): string {
  const map: Record<string, string> = {
    low: '低',
    medium: '中等',
    high: '高',
  }
  return map[level] || level
}

function getProfitText(potential: string): string {
  const map: Record<string, string> = {
    low: '一般',
    medium: '良好',
    high: '优秀',
  }
  return map[potential] || potential
}

function handleSelectionChange(rows: CollectedProduct[]) {
  selectedProducts.value = rows
}

function handleSelectAll(val: boolean) {
  // 全选逻辑
}

function collectProduct(row: any) {
  ElMessage.success('已添加到采集队列')
}

function batchCollect() {
  ElMessage.success(`已批量采集 ${selectedProducts.value.length} 个商品`)
}
</script>

<style scoped lang="scss">
$primary-color: #00b5ad;

.ai-selection {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-content {
  padding: 20px;
}

.filter-section {
  .price-separator {
    margin: 0 8px;
    color: #909399;
  }
}

.results-section {
  margin-top: 20px;
}

.market-analysis {
  margin-bottom: 30px;

  h3 {
    margin-bottom: 16px;
    font-size: 16px;
  }
}

.analysis-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;

  .analysis-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
  }

  .analysis-info {
    flex: 1;

    .analysis-label {
      font-size: 12px;
      color: #909399;
      margin-bottom: 4px;
    }

    .analysis-value {
      font-size: 16px;
      font-weight: 600;

      &.up { color: #67c23a; }
      &.down { color: #f56c6c; }
      &.stable { color: #909399; }
      &.low { color: #67c23a; }
      &.medium { color: #e6a23c; }
      &.high { color: #f56c6c; }
      &.score { color: $primary-color; }
    }
  }
}

.products-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
      font-size: 16px;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 16px;
    }
  }
}

.product-cell {
  display: flex;
  gap: 12px;

  .product-thumb {
    width: 60px;
    height: 60px;
    border-radius: 4px;
  }

  .product-info {
    flex: 1;

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
  }
}

.price-range {
  .selling-price {
    font-size: 14px;
    font-weight: 600;
    color: #f56c6c;
  }

  .profit {
    font-size: 12px;
    color: #67c23a;
    margin-top: 4px;
  }
}

.market-data {
  font-size: 12px;
  color: #606266;

  div {
    margin-bottom: 4px;
  }
}

.empty-state {
  padding: 60px 0;
}
</style>
