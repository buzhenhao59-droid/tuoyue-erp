<template>
  <el-container class="main-layout">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>拓岳ERP</h2>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              {{ userStore.username }}
              <el-icon><ArrowDown /></el-icon>
            </span>
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
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const menuItems = [
  { path: '/dashboard', title: '数据大屏', icon: 'DataLine' },
  { path: '/products', title: '商品管理', icon: 'Goods' },
  { path: '/collections', title: '采集管理', icon: 'Download' },
  { path: '/orders', title: '订单中心', icon: 'ShoppingCart' },
  { path: '/inventory', title: '库存管理', icon: 'Box' },
  { path: '/finance', title: '财务报表', icon: 'Money' },
  { path: '/system', title: '系统设置', icon: 'Setting' }
]

const handleCommand = (command: string) => {
  switch (command) {
    case 'logout':
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
      break
    case 'profile':
      // TODO: 个人中心
      break
    case 'settings':
      // TODO: 系统设置
      break
  }
}
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    border-bottom: 1px solid #1f2d3d;
    
    h2 {
      margin: 0;
      font-size: 20px;
    }
  }
  
  .sidebar-menu {
    border-right: none;
  }
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  
  .header-right {
    .user-info {
      cursor: pointer;
      color: #606266;
      
      &:hover {
        color: #409EFF;
      }
    }
  }
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
