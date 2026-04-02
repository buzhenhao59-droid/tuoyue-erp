<template>
  <el-container class="main-layout">
    <el-aside :width="sidebarCollapsed ? '72px' : '240px'" class="sidebar">
      <div class="logo" @click="goHome">
        <div class="logo-mark">拓</div>
        <div v-if="!sidebarCollapsed" class="logo-text">
          <div class="title">拓岳 ERP</div>
          <div class="subtitle">跨境运营中台</div>
        </div>
      </div>

      <el-scrollbar class="menu-scrollbar">
        <el-menu
          :default-active="activeMenu"
          :collapse="sidebarCollapsed"
          :collapse-transition="false"
          unique-opened
          router
          class="sidebar-menu"
          background-color="#0f172a"
          text-color="#94a3b8"
          active-text-color="#ffffff"
        >
          <template v-for="item in menuTree" :key="item.path">
            <el-sub-menu v-if="item.children?.length" :index="item.path">
              <template #title>
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.title }}</span>
              </template>
              <el-menu-item
                v-for="child in item.children"
                :key="child.path"
                :index="child.path"
              >
                <el-icon><component :is="child.icon" /></el-icon>
                <span>{{ child.title }}</span>
              </el-menu-item>
            </el-sub-menu>

            <el-menu-item v-else :index="item.path">
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <el-container class="main-container">
      <el-header class="topbar">
        <div class="topbar-left">
          <el-button text class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
            <el-icon :size="18"><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
          </el-button>

          <el-breadcrumb separator=">">
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path || item.title">
              <span>{{ item.title }}</span>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="topbar-right">
          <div class="header-stat">
            <span class="label">当前组织</span>
            <strong>拓岳 ERP</strong>
          </div>

          <el-dropdown @command="handleCommand">
            <div class="user-box">
              <el-avatar :size="34">
                {{ userInitial }}
              </el-avatar>
              <div class="user-meta">
                <div class="name">{{ displayName }}</div>
                <div class="role">管理员</div>
              </div>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <div class="tabbar-wrap">
        <div class="tabbar-scroll">
          <div
            v-for="tab in visitedTabs"
            :key="tab.path"
            class="tab-item"
            :class="{ active: tab.path === route.path }"
            @click="goTab(tab.path)"
          >
            <span>{{ tab.title }}</span>
            <el-icon
              v-if="tab.closable"
              class="tab-close"
              @click.stop="closeTab(tab.path)"
            >
              <Close />
            </el-icon>
          </div>
        </div>
        <div class="tabbar-actions">
          <el-button text @click="refreshCurrent">刷新</el-button>
        </div>
      </div>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <keep-alive :include="keepAliveNames">
            <component :is="Component" :key="cacheKey" />
          </keep-alive>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, Close, Expand, Fold } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

interface MenuChild {
  path: string
  title: string
  icon: string
}

interface MenuItem extends MenuChild {
  children?: MenuChild[]
}

interface VisitedTab {
  path: string
  title: string
  name?: string
  closable: boolean
}

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const sidebarCollapsed = ref(false)
const refreshSeed = ref(0)

const menuTree: MenuItem[] = [
  {
    path: '/dashboard',
    title: '实时概览',
    icon: 'DataLine'
  },
  {
    path: '/products',
    title: '产品管理',
    icon: 'Goods',
    children: [
      { path: '/products', title: '产品中心', icon: 'Goods' },
      { path: '/collections', title: '产品采集', icon: 'Download' }
    ]
  },
  {
    path: '/orders',
    title: '订单管理',
    icon: 'ShoppingCart',
    children: [
      { path: '/orders', title: '订单处理', icon: 'List' }
    ]
  },
  {
    path: '/inventory',
    title: '采购 / 仓储',
    icon: 'Box',
    children: [
      { path: '/inventory', title: '库存分析', icon: 'Box' }
    ]
  },
  {
    path: '/finance',
    title: '财务报表',
    icon: 'Money'
  },
  {
    path: '/system',
    title: '物流 / 授权',
    icon: 'Setting',
    children: [
      { path: '/system', title: '系统设置', icon: 'Setting' }
    ]
  }
]

const baseTabs: VisitedTab[] = [
  { path: '/dashboard', title: '实时概览', name: 'Dashboard', closable: false }
]

const visitedTabs = ref<VisitedTab[]>([...baseTabs])

const activeMenu = computed(() => route.path)

const displayName = computed(() => userStore.userInfo?.real_name || userStore.username || '管理员')
const userInitial = computed(() => displayName.value?.slice(0, 1) || '拓')
const cacheKey = computed(() => `${route.path}-${refreshSeed.value}`)
const keepAliveNames = computed(() => visitedTabs.value.map(tab => tab.name).filter(Boolean) as string[])

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta.title as string
  }))
})

function ensureTab() {
  const exists = visitedTabs.value.find(tab => tab.path === route.path)
  if (exists) return

  visitedTabs.value.push({
    path: route.path,
    title: (route.meta.title as string) || '未命名页面',
    name: route.name ? String(route.name) : undefined,
    closable: route.path !== '/dashboard'
  })
}

watch(
  () => route.fullPath,
  () => {
    ensureTab()
  },
  { immediate: true }
)

function goHome() {
  router.push('/dashboard')
}

function goTab(path: string) {
  router.push(path)
}

function closeTab(path: string) {
  const index = visitedTabs.value.findIndex(tab => tab.path === path)
  if (index === -1) return

  const closingCurrent = route.path === path
  visitedTabs.value.splice(index, 1)

  if (closingCurrent) {
    const fallback = visitedTabs.value[index - 1] || visitedTabs.value[index] || visitedTabs.value[0]
    if (fallback) router.push(fallback.path)
  }
}

function refreshCurrent() {
  refreshSeed.value += 1
}

function handleCommand(command: string) {
  switch (command) {
    case 'logout':
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
      break
    case 'profile':
      ElMessage.info('个人中心稍后接入')
      break
    case 'settings':
      router.push('/system')
      break
  }
}
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  background: #f8fafc;
}

.sidebar {
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  border-right: 1px solid rgba(148, 163, 184, 0.12);
  transition: width 0.2s ease;
  overflow: hidden;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 12px;
  cursor: pointer;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);

  .logo-mark {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #14b8a6 0%, #0ea5e9 100%);
    color: #fff;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .title {
    color: #f8fafc;
    font-size: 16px;
    font-weight: 700;
    line-height: 1.2;
  }

  .subtitle {
    color: #94a3b8;
    font-size: 12px;
    margin-top: 2px;
  }
}

.menu-scrollbar {
  height: calc(100vh - 64px);
}

.sidebar-menu {
  border-right: none;
  padding: 12px 8px 20px;

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 44px;
    line-height: 44px;
    border-radius: 10px;
    margin-bottom: 6px;
  }

  :deep(.el-menu-item.is-active) {
    background: linear-gradient(90deg, rgba(20, 184, 166, 0.92), rgba(14, 165, 233, 0.9));
    box-shadow: 0 8px 20px rgba(20, 184, 166, 0.18);
  }
}

.main-container {
  min-width: 0;
}

.topbar {
  height: 64px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.topbar-left,
.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #f1f5f9;
}

.header-stat {
  text-align: right;

  .label {
    display: block;
    font-size: 12px;
    color: #94a3b8;
  }

  strong {
    font-size: 14px;
    color: #0f172a;
  }
}

.user-box {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 14px;
  transition: all 0.2s ease;

  &:hover {
    background: #f8fafc;
  }

  .user-meta {
    line-height: 1.2;
  }

  .name {
    font-size: 14px;
    font-weight: 600;
    color: #0f172a;
  }

  .role {
    font-size: 12px;
    color: #94a3b8;
  }
}

.tabbar-wrap {
  height: 48px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  gap: 12px;
}

.tabbar-scroll {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  min-width: 0;
  flex: 1;
}

.tab-item {
  height: 32px;
  padding: 0 12px;
  border-radius: 10px;
  background: #f1f5f9;
  color: #475569;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;

  &.active {
    background: linear-gradient(90deg, #14b8a6, #0ea5e9);
    color: #ffffff;
  }
}

.tab-close {
  border-radius: 50%;

  &:hover {
    background: rgba(255, 255, 255, 0.18);
  }
}

.main-content {
  background: #f8fafc;
  padding: 16px;
  overflow: auto;
}
</style>
