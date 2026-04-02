<template>
  <div class="bulk-import">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>批量导入</span>
        </div>
      </template>

      <div class="import-content">
        <el-steps :active="currentStep" finish-status="success" simple>
          <el-step title="下载模板" />
          <el-step title="填写数据" />
          <el-step title="上传文件" />
          <el-step title="导入完成" />
        </el-steps>

        <div class="step-content">
          <!-- 步骤1: 下载模板 -->
          <div v-if="currentStep === 0" class="step-panel">
            <div class="template-download">
              <h3>选择导入平台</h3>
              <el-radio-group v-model="importForm.platform" size="large">
                <el-radio-button label="1688">1688</el-radio-button>
                <el-radio-button label="taobao">淘宝</el-radio-button>
                <el-radio-button label="tmall">天猫</el-radio-button>
                <el-radio-button label="shopee">Shopee</el-radio-button>
                <el-radio-button label="lazada">Lazada</el-radio-button>
                <el-radio-button label="tiktok">TikTok</el-radio-button>
              </el-radio-group>

              <div class="template-info">
                <h4>模板说明</h4>
                <p>1. 下载对应平台的导入模板</p>
                <p>2. 按照模板格式填写商品链接</p>
                <p>3. 支持 Excel (.xlsx) 和 CSV (.csv) 格式</p>
                <p>4. 单次最多导入 1000 条链接</p>
              </div>

              <el-button type="primary" size="large" @click="downloadTemplate">
                <el-icon><Download /></el-icon>
                下载导入模板
              </el-button>
            </div>
          </div>

          <!-- 步骤2: 填写数据 -->
          <div v-if="currentStep === 1" class="step-panel">
            <div class="data-prepare">
              <h3>数据准备</h3>
              <div class="template-preview">
                <el-table :data="previewData" border size="small">
                  <el-table-column prop="url" label="商品链接" min-width="300" />
                  <el-table-column prop="platform" label="平台" width="100" />
                  <el-table-column prop="category" label="目标类目" width="150" />
                  <el-table-column prop="price_multiplier" label="价格倍率" width="100" />
                </el-table>
              </div>
              <p class="tip">请按照以上格式准备您的数据</p>
              <el-button type="primary" @click="currentStep = 2">下一步</el-button>
            </div>
          </div>

          <!-- 步骤3: 上传文件 -->
          <div v-if="currentStep === 2" class="step-panel">
            <div class="file-upload">
              <h3>上传文件</h3>
              
              <el-form :model="importForm" label-width="100px">
                <el-form-item label="采集配置">
                  <el-select v-model="importForm.config_id" placeholder="选择采集配置（可选）" clearable style="width: 300px">
                    <el-option
                      v-for="config in configList"
                      :key="config.id"
                      :label="config.name"
                      :value="config.id"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item label="导入文件" required>
                  <el-upload
                    ref="uploadRef"
                    drag
                    action="/api/v1/collections/batch_import/"
                    :auto-upload="false"
                    :on-change="handleFileChange"
                    :on-success="handleUploadSuccess"
                    :on-error="handleUploadError"
                    accept=".xlsx,.xls,.csv"
                    :limit="1"
                  >
                    <el-icon class="el-icon--upload"><Upload /></el-icon>
                    <div class="el-upload__text">
                      拖拽文件到此处或 <em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        支持 .xlsx, .xls, .csv 格式，单次最多 1000 条
                      </div>
                    </template>
                  </el-upload>
                </el-form-item>
              </el-form>

              <div class="upload-actions">
                <el-button @click="currentStep = 1">上一步</el-button>
                <el-button type="primary" :loading="importing" @click="startImport">
                  开始导入
                </el-button>
              </div>
            </div>
          </div>

          <!-- 步骤4: 导入完成 -->
          <div v-if="currentStep === 3" class="step-panel">
            <div class="import-result">
              <el-result
                :icon="importResult.success ? 'success' : 'warning'"
                :title="importResult.success ? '导入成功' : '导入完成（部分失败）'"
                :sub-title="`成功: ${importResult.success_count} 条，失败: ${importResult.fail_count} 条`"
              >
                <template #extra>
                  <el-button type="primary" @click="resetImport">继续导入</el-button>
                  <el-button @click="$emit('importSuccess')">查看商品</el-button>
                </template>
              </el-result>

              <div v-if="importResult.errors?.length" class="error-list">
                <h4>错误详情</h4>
                <el-table :data="importResult.errors" size="small" max-height="200">
                  <el-table-column prop="row" label="行号" width="80" />
                  <el-table-column prop="url" label="链接" min-width="200" />
                  <el-table-column prop="error" label="错误信息" />
                </el-table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Upload } from '@element-plus/icons-vue'
import type { UploadFile, UploadInstance } from 'element-plus'
import type { CollectionConfig } from '@/types/collections'
import { batchImportProducts } from '@/api/collections'

interface Props {
  configList: CollectionConfig[]
}

defineProps<Props>()

const emit = defineEmits<{
  'importSuccess': []
}>()

const currentStep = ref(0)
const uploadRef = ref<UploadInstance>()
const importing = ref(false)

const importForm = reactive({
  platform: '1688',
  config_id: undefined as number | undefined,
  file: null as File | null,
})

const importResult = reactive({
  success: true,
  success_count: 0,
  fail_count: 0,
  errors: [] as any[],
})

const previewData = [
  { url: 'https://detail.1688.com/offer/123456.html', platform: '1688', category: '女装', price_multiplier: 1.5 },
  { url: 'https://item.taobao.com/item.htm?id=123456', platform: '淘宝', category: '男装', price_multiplier: 1.8 },
]

function downloadTemplate() {
  // 生成模板文件并下载
  const csvContent = '商品链接,平台,目标类目,价格倍率\nhttps://example.com/product,1688,女装,1.5'
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `导入模板_${importForm.platform}.csv`
  link.click()
  
  currentStep.value = 1
}

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    importForm.file = file.raw
  }
}

async function startImport() {
  if (!importForm.file) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  importing.value = true
  try {
    const res: any = await batchImportProducts({
      file: importForm.file,
      platform: importForm.platform,
      config_id: importForm.config_id,
    })

    importResult.success = res.fail_count === 0
    importResult.success_count = res.success_count || 0
    importResult.fail_count = res.fail_count || 0
    importResult.errors = res.errors || []

    currentStep.value = 3
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

function handleUploadSuccess(response: any) {
  importResult.success = response.fail_count === 0
  importResult.success_count = response.success_count || 0
  importResult.fail_count = response.fail_count || 0
  importResult.errors = response.errors || []
  currentStep.value = 3
}

function handleUploadError() {
  ElMessage.error('上传失败')
  importing.value = false
}

function resetImport() {
  currentStep.value = 0
  importForm.file = null
  importForm.config_id = undefined
  uploadRef.value?.clearFiles()
}
</script>

<style scoped lang="scss">
$primary-color: #00b5ad;

.bulk-import {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.import-content {
  padding: 20px;
}

.step-content {
  margin-top: 30px;
}

.step-panel {
  padding: 20px;
}

.template-download {
  text-align: center;

  h3 {
    margin-bottom: 20px;
  }

  .template-info {
    margin: 30px 0;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;
    text-align: left;

    h4 {
      margin-bottom: 12px;
    }

    p {
      margin: 8px 0;
      color: #606266;
    }
  }
}

.data-prepare {
  text-align: center;

  h3 {
    margin-bottom: 20px;
  }

  .template-preview {
    margin: 20px 0;
  }

  .tip {
    color: #909399;
    margin: 20px 0;
  }
}

.file-upload {
  max-width: 500px;
  margin: 0 auto;

  h3 {
    text-align: center;
    margin-bottom: 20px;
  }

  .upload-actions {
    margin-top: 20px;
    text-align: center;
  }
}

.import-result {
  .error-list {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
    }
  }
}
</style>
