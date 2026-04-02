<template>
  <div class="plugin-collection">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>插件采集</span>
          <el-button type="primary" @click="showInstallGuide = true">
            <el-icon><Download /></el-icon>
            安装插件
          </el-button>
        </div>
      </template>

      <div class="plugin-content">
        <div class="plugin-status">
          <el-result
            :icon="isConnected ? 'success' : 'info'"
            :title="isConnected ? '插件已连接' : '等待插件连接'"
            :sub-title="isConnected ? '可以开始采集商品' : '请安装并启用浏览器插件'"
          >
            <template #extra>
              <el-button type="primary" @click="testConnection">
                测试连接
              </el-button>
            </template>
          </el-result>
        </div>

        <el-divider />

        <div class="plugin-instructions">
          <h3>使用说明</h3>
          <el-steps :active="1" direction="vertical">
            <el-step title="安装插件">
              <template #description>
                <p>下载并安装浏览器扩展插件</p>
                <p>支持 Chrome、Edge、Firefox 浏览器</p>
              </template>
            </el-step>
            <el-step title="登录账号">
              <template #description>
                <p>在插件中登录您的拓岳ERP账号</p>
                <p>确保账号有采集权限</p>
              </template>
            </el-step>
            <el-step title="开始采集">
              <template #description>
                <p>打开目标商品页面</p>
                <p>点击插件图标即可采集当前商品</p>
              </template>
            </el-step>
          </el-steps>
        </div>

        <el-divider />

        <div class="plugin-stats">
          <h3>今日采集统计</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-card">
                <div class="stat-value">{{ todayStats.total }}</div>
                <div class="stat-label">采集总数</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card">
                <div class="stat-value">{{ todayStats.success }}</div>
                <div class="stat-label">成功</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card">
                <div class="stat-value">{{ todayStats.failed }}</div>
                <div class="stat-label">失败</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>

    <!-- 安装指南对话框 -->
    <el-dialog
      v-model="showInstallGuide"
      title="插件安装指南"
      width="700px"
    >
      <div class="install-guide">
        <el-tabs v-model="activeBrowser">
          <el-tab-pane label="Chrome" name="chrome">
            <div class="guide-content">
              <h4>Chrome 浏览器安装步骤</h4>
              <ol>
                <li>下载插件安装包并解压</li>
                <li>打开 Chrome，访问 <code>chrome://extensions/</code></li>
                <li>开启右上角的"开发者模式"</li>
                <li>点击"加载已解压的扩展程序"</li>
                <li>选择解压后的插件文件夹</li>
              </ol>
              <el-button type="primary" @click="downloadPlugin('chrome')">
                下载 Chrome 插件
              </el-button>
            </div>
          </el-tab-pane>
          <el-tab-pane label="Edge" name="edge">
            <div class="guide-content">
              <h4>Edge 浏览器安装步骤</h4>
              <ol>
                <li>下载插件安装包并解压</li>
                <li>打开 Edge，访问 <code>edge://extensions/</code></li>
                <li>开启左下角的"开发人员模式"</li>
                <li>点击"加载解压缩的扩展"</li>
                <li>选择解压后的插件文件夹</li>
              </ol>
              <el-button type="primary" @click="downloadPlugin('edge')">
                下载 Edge 插件
              </el-button>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'

const isConnected = ref(false)
const showInstallGuide = ref(false)
const activeBrowser = ref('chrome')

const todayStats = reactive({
  total: 0,
  success: 0,
  failed: 0,
})

function testConnection() {
  // 模拟测试连接
  setTimeout(() => {
    isConnected.value = true
    ElMessage.success('插件连接成功')
  }, 1000)
}

function downloadPlugin(browser: string) {
  ElMessage.success(`开始下载 ${browser} 插件`)
  // 实际项目中这里会触发下载
}

onMounted(() => {
  // 检查插件连接状态
  // 获取今日统计
})
</script>

<style scoped lang="scss">
$primary-color: #00b5ad;

.plugin-collection {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plugin-content {
  padding: 20px;
}

.plugin-status {
  padding: 20px 0;
}

.plugin-instructions {
  h3 {
    margin-bottom: 20px;
    font-size: 16px;
  }
}

.plugin-stats {
  h3 {
    margin-bottom: 20px;
    font-size: 16px;
  }

  .stat-card {
    background: #f5f7fa;
    border-radius: 8px;
    padding: 20px;
    text-align: center;

    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: $primary-color;
      margin-bottom: 8px;
    }

    .stat-label {
      font-size: 13px;
      color: #606266;
    }
  }
}

.install-guide {
  .guide-content {
    padding: 20px;

    h4 {
      margin-bottom: 16px;
    }

    ol {
      margin-bottom: 20px;
      padding-left: 20px;

      li {
        margin-bottom: 8px;
        color: #606266;
      }
    }

    code {
      background: #f5f7fa;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: monospace;
    }
  }
}
</style>
