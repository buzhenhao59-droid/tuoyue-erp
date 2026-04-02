<!-- 数据大屏 - 拓岳 ERP -->
<template>
  <div class="dashboard-page">
    <!-- 顶部统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card sales">
            <div class="stat-icon">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">今日销售额</div>
              <div class="stat-value">¥{{ formatNumber(stats.todaySales) }}</div>
              <div class="stat-trend" :class="stats.salesTrend >= 0 ? 'up' : 'down'">
                <el-icon><ArrowUp v-if="stats.salesTrend >= 0" /><ArrowDown v-else /></el-icon>
                {{ Math.abs(stats.salesTrend) }}%
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card orders">
            <div class="stat-icon">
              <el-icon><ShoppingCart /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">今日订单</div>
              <div class="stat-value">{{ formatNumber(stats.todayOrders) }}</div>
              <div class="stat-trend" :class="stats.ordersTrend >= 0 ? 'up' : 'down'">
                <el-icon><ArrowUp v-if="stats.ordersTrend >= 0" /><ArrowDown v-else /></el-icon>
                {{ Math.abs(stats.ordersTrend) }}%
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card products">
            <div class="stat-icon">
              <el-icon><Goods /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">商品总数</div>
              <div class="stat-value">{{ formatNumber(stats.totalProducts) }}</div>
              <div class="stat-trend up">
                <el-icon><Plus /></el-icon>
                {{ stats.newProducts }} 新品
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card profit">
            <div class="stat-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">今日利润</div>
              <div class="stat-value">¥{{ formatNumber(stats.todayProfit) }}</div>
              <div class="stat-trend" :class="stats.profitTrend >= 0 ? 'up' : 'down'">
                <el-icon><ArrowUp v-if="stats.profitTrend >= 0" /><ArrowDown v-else /></el-icon>
                {{ Math.abs(stats.profitTrend) }}%
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 待处理提醒看板 -->
    <div class="alert-section">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="alert-card" shadow="hover" @click="goToOrders('pending')">
            <div class="alert-content">
              <div class="alert-icon warning">
                <el-icon><Bell /></el-icon>
              </div>
              <div class="alert-info">
                <div class="alert-count">{{ alerts.pendingPayment }}</div>
                <div class="alert-label">待付款订单</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="alert-card" shadow="hover" @click="goToOrders('processing')">
            <div class="alert-content">
              <div class="alert-icon danger">
                <el-icon><Box /></el-icon>
              </div>
              <div class="alert-info">
                <div class="alert-count">{{ alerts.pendingShipment }}</div>
                <div class="alert-label">待发货订单</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="alert-card" shadow="hover" @click="goToInventory">
            <div class="alert-content">
              <div class="alert-icon warning">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="alert-info">
                <div class="alert-count">{{ alerts.lowStock }}</div>
                <div class="alert-label">库存预警</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="alert-card" shadow="hover" @click="goToCollections">
            <div class="alert-content">
              <div class="alert-icon success">
                <el-icon><Download /></el-icon>
              </div>
              <div class="alert-info">
                <div class="alert-count">{{ alerts.pendingCollections }}</div>
                <div class="alert-label">待认领采集</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <el-row :gutter="16">
        <!-- 销售趋势 -->
        <el-col :xs="24" :lg="16">
          <el-card class="chart-card" shadow="never">
            <template #header>
              <div class="chart-header">
                <span class="chart-title">销售额走势</span>
                <el-radio-group v-model="salesTimeRange" size="small">
                  <el-radio-button label="7">近7天</el-radio-button>
                  <el-radio-button label="30">近30天</el-radio-button>
                  <el-radio-button label="90">近90天</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div ref="salesChartRef" class="chart-container" style="height: 350px;"></div>
          </el-card>
        </el-col>

        <!-- 订单分布 -->
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card" shadow="never">
            <template #header>
              <div class="chart-header">
                <span class="chart-title">订单分布</span>
              </div>
            </template>
            <div ref="orderChartRef" class="chart-container" style="height: 350px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 平台销售对比 + 热销商品 -->
    <div class="charts-section">
      <el-row :gutter="16">
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="never">
            <template #header>
              <div class="chart-header">
                <span class="chart-title">平台销售对比</span>
              </div>
            </template>
            <div ref="platformChartRef" class="chart-container" style="height: 300px;"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="never">
            <template #header>
              <div class="chart-header">
                <span class="chart-title">热销商品 TOP10</span>
              </div>
            </template>
            <div class="top-products">
              <div
                v-for="(product, index) in topProducts"
                :key="product.id"
                class="product-rank-item"
              >
                <div class="rank-number" :class="{ top3: index < 3 }">{{ index + 1 }}</div>
                <el-image :src="product.image" class="product-image" fit="cover" />
                <div class="product-info">
                  <div class="product-name" :title="product.name">{{ product.name }}</div>
                  <div class="product-sales">销量: {{ product.sales }}</div>
                </div>
                <div class="product-amount">¥{{ product.amount }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
// ElMessage imported for future use
import {
  Money, ShoppingCart, Goods, TrendCharts, ArrowUp, ArrowDown, Plus,
  Bell, Box, Warning, Download
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getDashboardStats, getSalesTrend, getOrderDistribution } from '@/api/dashboard'

const router = useRouter()

// 统计数据
const stats = reactive({
  todaySales: 0,
  salesTrend: 0,
  todayOrders: 0,
  ordersTrend: 0,
  totalProducts: 0,
  newProducts: 0,
  todayProfit: 0,
  profitTrend: 0,
})

// 待处理提醒
const alerts = reactive({
  pendingPayment: 0,
  pendingShipment: 0,
  lowStock: 0,
  pendingCollections: 0,
})

// 热销商品
const topProducts = ref([
  { id: 1, name: '无线蓝牙耳机 Pro', image: 'https://via.placeholder.com/50', sales: 1234, amount: 123400 },
  { id: 2, name: '智能手表 Series 8', image: 'https://via.placeholder.com/50', sales: 987, amount: 98700 },
  { id: 3, name: '便携充电宝 20000mAh', image: 'https://via.placeholder.com/50', sales: 856, amount: 42800 },
  { id: 4, name: 'Type-C 快充数据线', image: 'https://via.placeholder.com/50', sales: 743, amount: 14860 },
  { id: 5, name: '手机支架 桌面款', image: 'https://via.placeholder.com/50', sales: 652, amount: 19560 },
  { id: 6, name: '蓝牙音箱 Mini', image: 'https://via.placeholder.com/50', sales: 541, amount: 27050 },
  { id: 7, name: 'LED 台灯护眼', image: 'https://via.placeholder.com/50', sales: 432, amount: 21600 },
  { id: 8, name: 'USB 扩展坞', image: 'https://via.placeholder.com/50', sales: 321, amount: 19260 },
  { id: 9, name: '鼠标垫 超大号', image: 'https://via.placeholder.com/50', sales: 210, amount: 4200 },
  { id: 10, name: '键盘清洁泥', image: 'https://via.placeholder.com/50', sales: 198, amount: 1980 },
])

// 时间范围
const salesTimeRange = ref('7')

// 图表引用
const salesChartRef = ref<HTMLElement>()
const orderChartRef = ref<HTMLElement>()
const platformChartRef = ref<HTMLElement>()

let salesChart: echarts.ECharts | null = null
let orderChart: echarts.ECharts | null = null
let platformChart: echarts.ECharts | null = null

// 格式化数字
function formatNumber(num: number): string {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

// 获取统计数据
async function fetchStats() {
  try {
    const res: any = await getDashboardStats()
    Object.assign(stats, res.stats || {})
    Object.assign(alerts, res.alerts || {})
  } catch (error) {
    console.error('获取统计数据失败', error)
    // 使用模拟数据
    stats.todaySales = 45678
    stats.salesTrend = 12.5
    stats.todayOrders = 234
    stats.ordersTrend = 8.3
    stats.totalProducts = 5678
    stats.newProducts = 23
    stats.todayProfit = 12345
    stats.profitTrend = 15.2
    
    alerts.pendingPayment = 12
    alerts.pendingShipment = 45
    alerts.lowStock = 8
    alerts.pendingCollections = 156
  }
}

// 初始化销售趋势图
function initSalesChart(data: any) {
  if (!salesChartRef.value) return
  
  salesChart = echarts.init(salesChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['销售额', '订单数'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data?.dates || ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      axisLabel: { color: '#606266' }
    },
    yAxis: [
      {
        type: 'value',
        name: '销售额',
        axisLabel: {
          formatter: (value: number) => '¥' + (value >= 1000 ? (value / 1000) + 'k' : value),
          color: '#606266'
        },
        splitLine: { lineStyle: { color: '#ebeef5' } }
      },
      {
        type: 'value',
        name: '订单数',
        axisLabel: { color: '#606266' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '销售额',
        type: 'line',
        smooth: true,
        data: data?.sales || [12000, 13200, 10100, 13400, 9000, 23000, 21000],
        itemStyle: { color: '#00b5ad' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 181, 173, 0.3)' },
            { offset: 1, color: 'rgba(0, 181, 173, 0.05)' }
          ])
        }
      },
      {
        name: '订单数',
        type: 'bar',
        yAxisIndex: 1,
        data: data?.orders || [120, 132, 101, 134, 90, 230, 210],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#79bbff' }
          ])
        }
      }
    ]
  }
  
  salesChart.setOption(option)
}

// 初始化订单分布图
function initOrderChart(data: any) {
  if (!orderChartRef.value) return
  
  orderChart = echarts.init(orderChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      data: data?.labels || ['待付款', '待发货', '已发货', '已完成', '已取消']
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: data?.data || [
          { value: 12, name: '待付款', itemStyle: { color: '#e6a23c' } },
          { value: 45, name: '待发货', itemStyle: { color: '#f56c6c' } },
          { value: 123, name: '已发货', itemStyle: { color: '#409eff' } },
          { value: 456, name: '已完成', itemStyle: { color: '#67c23a' } },
          { value: 23, name: '已取消', itemStyle: { color: '#909399' } },
        ]
      }
    ]
  }
  
  orderChart.setOption(option)
}

// 初始化平台对比图
function initPlatformChart(data: any) {
  if (!platformChartRef.value) return
  
  platformChart = echarts.init(platformChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data?.platforms || ['TikTok Shop', 'Shopee', 'Lazada', 'Amazon', 'eBay'],
      axisLabel: { color: '#606266' }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => '¥' + (value >= 1000 ? (value / 1000) + 'k' : value),
        color: '#606266'
      },
      splitLine: { lineStyle: { color: '#ebeef5' } }
    },
    series: [
      {
        type: 'bar',
        data: data?.sales || [45000, 38000, 28000, 22000, 15000],
        itemStyle: {
          color: (params: any) => {
            const colors = ['#000000', '#ee4d2d', '#0f156d', '#ff9900', '#0064d2']
            return colors[params.dataIndex] || '#00b5ad'
          },
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  }
  
  platformChart.setOption(option)
}

// 获取图表数据
async function fetchChartData() {
  try {
    const [salesRes, orderRes]: any = await Promise.all([
      getSalesTrend({ days: parseInt(salesTimeRange.value) }),
      getOrderDistribution()
    ])
    
    initSalesChart(salesRes.data)
    initOrderChart(orderRes.data)
    initPlatformChart(salesRes.platformData)
  } catch (error) {
    console.error('获取图表数据失败', error)
    // 使用默认数据初始化
    nextTick(() => {
      initSalesChart(null)
      initOrderChart(null)
      initPlatformChart(null)
    })
  }
}

// 路由跳转
function goToOrders(status: string) {
  router.push({ path: '/orders', query: { status } })
}

function goToInventory() {
  router.push('/inventory')
}

function goToCollections() {
  router.push('/collections')
}

// 监听时间范围变化
watch(salesTimeRange, () => {
  fetchChartData()
})

// 窗口大小变化时重绘图表
function handleResize() {
  salesChart?.resize()
  orderChart?.resize()
  platformChart?.resize()
}

onMounted(() => {
  fetchStats()
  fetchChartData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  salesChart?.dispose()
  orderChart?.dispose()
  platformChart?.dispose()
})
</script>

<style scoped lang="scss">
$primary-color: #00b5ad;

.dashboard-page {
  padding: 16px;
}

// 统计卡片
.stats-cards {
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }
  
  &.sales { border-left: 4px solid #00b5ad; }
  &.orders { border-left: 4px solid #409eff; }
  &.products { border-left: 4px solid #67c23a; }
  &.profit { border-left: 4px solid #e6a23c; }
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  
  .sales & { background: rgba(0, 181, 173, 0.1); color: #00b5ad; }
  .orders & { background: rgba(64, 158, 255, 0.1); color: #409eff; }
  .products & { background: rgba(103, 194, 58, 0.1); color: #67c23a; }
  .profit & { background: rgba(230, 162, 60, 0.1); color: #e6a23c; }
  
  .el-icon {
    font-size: 28px;
  }
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  
  &.up { color: #67c23a; }
  &.down { color: #f56c6c; }
}

// 提醒看板
.alert-section {
  margin-bottom: 16px;
}

.alert-card {
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
  }
  
  :deep(.el-card__body) {
    padding: 16px;
  }
}

.alert-content {
  display: flex;
  align-items: center;
}

.alert-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  
  &.warning {
    background: rgba(230, 162, 60, 0.1);
    color: #e6a23c;
  }
  
  &.danger {
    background: rgba(245, 108, 108, 0.1);
    color: #f56c6c;
  }
  
  &.success {
    background: rgba(103, 194, 58, 0.1);
    color: #67c23a;
  }
  
  .el-icon {
    font-size: 24px;
  }
}

.alert-info {
  flex: 1;
}

.alert-count {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.alert-label {
  font-size: 13px;
  color: #909399;
}

// 图表区域
.charts-section {
  margin-bottom: 16px;
}

.chart-card {
  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;
  }
  
  :deep(.el-card__body) {
    padding: 20px;
  }
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

// 热销商品
.top-products {
  max-height: 300px;
  overflow-y: auto;
}

.product-rank-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
  
  &:last-child {
    border-bottom: none;
  }
}

.rank-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #909399;
  background: #f5f7fa;
  margin-right: 12px;
  
  &.top3 {
    color: #fff;
    background: #00b5ad;
  }
}

.product-image {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  margin-right: 12px;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-sales {
  font-size: 12px;
  color: #909399;
}

.product-amount {
  font-size: 14px;
  font-weight: 500;
  color: #f56c6c;
}
</style>