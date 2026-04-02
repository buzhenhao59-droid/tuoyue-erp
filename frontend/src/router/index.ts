import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login/index.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      name: 'Layout',
      component: () => import('@/layouts/MainLayout.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: '/dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/index.vue'),
          meta: { title: '数据大屏', icon: 'DataLine' }
        },
        {
          path: '/products',
          name: 'Products',
          component: () => import('@/views/products/index.vue'),
          meta: { title: '商品管理', icon: 'Goods' }
        },
        {
          path: '/collections',
          name: 'Collections',
          component: () => import('@/views/collections/index.vue'),
          meta: { title: '采集管理', icon: 'Download' }
        },
        {
          path: '/orders',
          name: 'Orders',
          component: () => import('@/views/orders/index.vue'),
          meta: { title: '订单中心', icon: 'ShoppingCart' }
        },
        {
          path: '/inventory',
          name: 'Inventory',
          component: () => import('@/views/inventory/index.vue'),
          meta: { title: '库存管理', icon: 'Box' }
        },
        {
          path: '/finance',
          name: 'Finance',
          component: () => import('@/views/finance/index.vue'),
          meta: { title: '财务报表', icon: 'Money' }
        },
        {
          path: '/system',
          name: 'System',
          component: () => import('@/views/system/index.vue'),
          meta: { title: '系统设置', icon: 'Setting' }
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/error/404.vue')
    }
  ]
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.public) {
    next()
    return
  }
  
  if (!userStore.token) {
    next('/login')
    return
  }
  
  next()
})

export default router
