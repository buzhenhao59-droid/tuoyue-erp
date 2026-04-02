import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const topMenus = [
  {
    key: 'dashboard',
    label: '首页',
    icon: 'House',
    route: '/dashboard',
    children: [
      { key: 'dashboard-overview', label: '工作台', route: '/dashboard' },
      { key: 'dashboard-monitor', label: '经营概览', route: '/dashboard/monitor' },
    ],
  },
  {
    key: 'product',
    label: '产品',
    icon: 'Box',
    route: '/product/list',
    children: [
      { key: 'product-list', label: '商品管理', route: '/product/list' },
      { key: 'product-publish', label: '刊登管理', route: '/product/publish' },
      { key: 'product-media', label: '素材中心', route: '/product/media' },
    ],
  },
  {
    key: 'order',
    label: '订单',
    icon: 'Tickets',
    route: '/order/list',
    children: [
      { key: 'order-list', label: '订单列表', route: '/order/list' },
      { key: 'order-after-sale', label: '售后管理', route: '/order/after-sale' },
      { key: 'order-rule', label: '订单规则', route: '/order/rule' },
    ],
  },
  {
    key: 'hosting',
    label: '托管',
    icon: 'Connection',
    route: '/hosting/store',
    children: [
      { key: 'hosting-store', label: '店铺托管', route: '/hosting/store' },
      { key: 'hosting-task', label: '托管任务', route: '/hosting/task' },
    ],
  },
  {
    key: 'ads',
    label: '广告',
    icon: 'Promotion',
    route: '/ads/overview',
    children: [
      { key: 'ads-overview', label: '广告总览', route: '/ads/overview' },
      { key: 'ads-campaign', label: '广告活动', route: '/ads/campaign' },
      { key: 'ads-report', label: '投放报表', route: '/ads/report' },
    ],
  },
  {
    key: 'data',
    label: '数据',
    icon: 'DataAnalysis',
    route: '/data/realtime',
    children: [
      { key: 'data-realtime', label: '今日实时', route: '/data/realtime' },
      { key: 'data-profit', label: '利润分析', route: '/data/profit' },
      { key: 'data-operation', label: '运营分析', route: '/data/operation' },
    ],
  },
  {
    key: 'purchase',
    label: '采购',
    icon: 'ShoppingCart',
    route: '/purchase/goods',
    children: [
      { key: 'purchase-goods', label: '商品采购', route: '/purchase/goods' },
      { key: 'purchase-receive', label: '收货管理', route: '/purchase/receive' },
      { key: 'purchase-supplier', label: '供应商', route: '/purchase/supplier' },
    ],
  },
  {
    key: 'warehouse',
    label: '仓库',
    icon: 'HomeFilled',
    route: '/warehouse/inventory',
    children: [
      { key: 'warehouse-inventory', label: '库存总览', route: '/warehouse/inventory' },
      { key: 'warehouse-inbound', label: '入库管理', route: '/warehouse/inbound' },
      { key: 'warehouse-outbound', label: '出库管理', route: '/warehouse/outbound' },
    ],
  },
  {
    key: 'logistics',
    label: '物流',
    icon: 'Van',
    route: '/logistics/channel',
    children: [
      { key: 'logistics-channel', label: '物流渠道', route: '/logistics/channel' },
      { key: 'logistics-track', label: '轨迹跟踪', route: '/logistics/track' },
    ],
  },
  {
    key: 'auth',
    label: '授权',
    icon: 'Key',
    route: '/auth/store',
    children: [
      { key: 'auth-store', label: '店铺授权', route: '/auth/store' },
      { key: 'auth-api', label: 'API 凭证', route: '/auth/api' },
    ],
  },
  {
    key: 'more',
    label: '更多',
    icon: 'MoreFilled',
    route: '/more/system',
    children: [
      {
        key: 'more-system',
        label: '系统配置',
        route: '/more/system',
        children: [
          { key: 'more-system-params', label: '参数配置', route: '/more/system/params' },
          { key: 'more-system-role', label: '角色权限', route: '/more/system/role' },
        ],
      },
      { key: 'more-message', label: '消息中心', route: '/more/message' },
    ],
  },
]

export const useMenuStore = defineStore('menu', () => {
  const activeTopMenu = ref(topMenus[0].key)
  const sidebarCollapsed = ref(false)
  const visitedViews = ref([])

  const activeTopMenuInfo = computed(() => topMenus.find((item) => item.key === activeTopMenu.value) || topMenus[0])
  const sidebarMenus = computed(() => activeTopMenuInfo.value.children || [])

  function setActiveTopMenu(key) {
    activeTopMenu.value = key
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function addVisitedView(route) {
    if (!route?.path || route.meta?.hiddenTag) return

    const exists = visitedViews.value.find((item) => item.path === route.path)
    if (!exists) {
      visitedViews.value.push({
        path: route.path,
        title: route.meta?.title || '未命名页面',
        topMenu: route.meta?.topMenu || activeTopMenu.value,
      })
    }
  }

  function removeVisitedView(path) {
    visitedViews.value = visitedViews.value.filter((item) => item.path !== path)
  }

  return {
    topMenus,
    activeTopMenu,
    sidebarCollapsed,
    visitedViews,
    activeTopMenuInfo,
    sidebarMenus,
    setActiveTopMenu,
    toggleSidebar,
    addVisitedView,
    removeVisitedView,
  }
})
