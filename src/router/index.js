import { createRouter, createWebHistory } from 'vue-router'
import { useMenuStore } from '@/store'

const Layout = () => import('@/layout/index.vue')

const RouteView = {
  name: 'RouteView',
  render: () => null,
}

const modules = [
  {
    path: '/dashboard',
    name: 'DashboardWorkbench',
    component: () => import('@/views/dashboard/Workbench.vue'),
    meta: { title: '工作台', topMenu: 'dashboard' },
  },
  {
    path: '/dashboard/monitor',
    name: 'DashboardMonitor',
    component: () => import('@/views/dashboard/Monitor.vue'),
    meta: { title: '经营概览', topMenu: 'dashboard' },
  },
  {
    path: '/product/list',
    name: 'ProductList',
    component: () => import('@/views/product/ProductList.vue'),
    meta: { title: '商品管理', topMenu: 'product' },
  },
  {
    path: '/product/publish',
    name: 'ProductPublish',
    component: () => import('@/views/product/ProductPublish.vue'),
    meta: { title: '刊登管理', topMenu: 'product' },
  },
  {
    path: '/product/media',
    name: 'ProductMedia',
    component: () => import('@/views/product/ProductMedia.vue'),
    meta: { title: '素材中心', topMenu: 'product' },
  },
  {
    path: '/order/list',
    name: 'OrderList',
    component: () => import('@/views/order/OrderList.vue'),
    meta: { title: '订单列表', topMenu: 'order' },
  },
  {
    path: '/order/after-sale',
    name: 'OrderAfterSale',
    component: () => import('@/views/order/AfterSale.vue'),
    meta: { title: '售后管理', topMenu: 'order' },
  },
  {
    path: '/order/rule',
    name: 'OrderRule',
    component: () => import('@/views/order/OrderRule.vue'),
    meta: { title: '订单规则', topMenu: 'order' },
  },
  {
    path: '/hosting/store',
    name: 'HostingStore',
    component: () => import('@/views/hosting/HostingStore.vue'),
    meta: { title: '店铺托管', topMenu: 'hosting' },
  },
  {
    path: '/hosting/task',
    name: 'HostingTask',
    component: () => import('@/views/hosting/HostingTask.vue'),
    meta: { title: '托管任务', topMenu: 'hosting' },
  },
  {
    path: '/ads/overview',
    name: 'AdsOverview',
    component: () => import('@/views/ads/AdsOverview.vue'),
    meta: { title: '广告总览', topMenu: 'ads' },
  },
  {
    path: '/ads/campaign',
    name: 'AdsCampaign',
    component: () => import('@/views/ads/AdsCampaign.vue'),
    meta: { title: '广告活动', topMenu: 'ads' },
  },
  {
    path: '/ads/report',
    name: 'AdsReport',
    component: () => import('@/views/ads/AdsReport.vue'),
    meta: { title: '投放报表', topMenu: 'ads' },
  },
  {
    path: '/data/realtime',
    name: 'DataRealtime',
    component: () => import('@/views/data/DataRealtime.vue'),
    meta: { title: '今日实时', topMenu: 'data' },
  },
  {
    path: '/data/profit',
    name: 'DataProfit',
    component: () => import('@/views/data/DataProfit.vue'),
    meta: { title: '利润分析', topMenu: 'data' },
  },
  {
    path: '/data/operation',
    name: 'DataOperation',
    component: () => import('@/views/data/DataOperation.vue'),
    meta: { title: '运营分析', topMenu: 'data' },
  },
  {
    path: '/purchase/goods',
    name: 'PurchaseGoods',
    component: () => import('@/views/purchase/PurchaseGoods.vue'),
    meta: { title: '商品采购', topMenu: 'purchase' },
  },
  {
    path: '/purchase/receive',
    name: 'PurchaseReceive',
    component: () => import('@/views/purchase/PurchaseReceive.vue'),
    meta: { title: '收货管理', topMenu: 'purchase' },
  },
  {
    path: '/purchase/supplier',
    name: 'PurchaseSupplier',
    component: () => import('@/views/purchase/PurchaseSupplier.vue'),
    meta: { title: '供应商', topMenu: 'purchase' },
  },
  {
    path: '/warehouse/inventory',
    name: 'WarehouseInventory',
    component: () => import('@/views/warehouse/WarehouseInventory.vue'),
    meta: { title: '库存总览', topMenu: 'warehouse' },
  },
  {
    path: '/warehouse/inbound',
    name: 'WarehouseInbound',
    component: () => import('@/views/warehouse/WarehouseInbound.vue'),
    meta: { title: '入库管理', topMenu: 'warehouse' },
  },
  {
    path: '/warehouse/outbound',
    name: 'WarehouseOutbound',
    component: () => import('@/views/warehouse/WarehouseOutbound.vue'),
    meta: { title: '出库管理', topMenu: 'warehouse' },
  },
  {
    path: '/logistics/channel',
    name: 'LogisticsChannel',
    component: () => import('@/views/logistics/LogisticsChannel.vue'),
    meta: { title: '物流渠道', topMenu: 'logistics' },
  },
  {
    path: '/logistics/track',
    name: 'LogisticsTrack',
    component: () => import('@/views/logistics/LogisticsTrack.vue'),
    meta: { title: '轨迹跟踪', topMenu: 'logistics' },
  },
  {
    path: '/auth/store',
    name: 'AuthStore',
    component: () => import('@/views/auth/AuthStore.vue'),
    meta: { title: '店铺授权', topMenu: 'auth' },
  },
  {
    path: '/auth/api',
    name: 'AuthApi',
    component: () => import('@/views/auth/AuthApi.vue'),
    meta: { title: 'API 凭证', topMenu: 'auth' },
  },
  {
    path: '/more/system',
    component: RouteView,
    meta: { title: '系统配置', topMenu: 'more', hiddenTag: true },
    children: [
      {
        path: 'params',
        name: 'MoreSystemParams',
        component: () => import('@/views/more/SystemParams.vue'),
        meta: { title: '参数配置', topMenu: 'more' },
      },
      {
        path: 'role',
        name: 'MoreSystemRole',
        component: () => import('@/views/more/SystemRole.vue'),
        meta: { title: '角色权限', topMenu: 'more' },
      },
    ],
  },
  {
    path: '/more/message',
    name: 'MoreMessage',
    component: () => import('@/views/more/MessageCenter.vue'),
    meta: { title: '消息中心', topMenu: 'more' },
  },
]

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: modules,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ left: 0, top: 0 }),
})

router.beforeEach((to) => {
  const menuStore = useMenuStore()

  if (to.meta?.topMenu) {
    menuStore.setActiveTopMenu(to.meta.topMenu)
  }

  menuStore.addVisitedView(to)
})

export default router
