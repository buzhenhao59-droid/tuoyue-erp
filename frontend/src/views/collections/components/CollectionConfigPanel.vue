<template>
  <div class="collection-config-panel">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>采集配置管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建配置
          </el-button>
        </div>
      </template>

      <!-- 配置列表 -->
      <el-table :data="configList" v-loading="loading" stripe>
        <el-table-column label="配置名称" prop="name" min-width="150">
          <template #default="{ row }">
            <div class="config-name">
              <span>{{ row.name }}</span>
              <el-tag v-if="row.is_default" size="small" type="success" effect="dark" class="default-tag">
                默认
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="价格规则" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="getPriceRuleType(row.price_rule)">
              {{ getPriceRuleText(row.price_rule) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="价格倍率" width="100">
          <template #default="{ row }">
            {{ row.price_multiplier }}x
          </template>
        </el-table-column>

        <el-table-column label="图片处理" min-width="200">
          <template #default="{ row }">
            <div class="image-options">
              <el-tag v-if="row.download_images" size="small" type="success">下载</el-tag>
              <el-tag v-if="row.watermark_remove" size="small" type="warning">去水印</el-tag>
              <el-tag v-if="row.image_compress" size="small" type="info">压缩</el-tag>
              <el-tag v-if="row.auto_translate" size="small" type="primary">翻译</el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" prop="created_at" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="!row.is_default" type="success" link @click="handleSetDefault(row)">
              设为默认
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 配置编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑配置' : '新建配置'"
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="config-form"
      >
        <el-divider content-position="left">基础设置</el-divider>

        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入配置名称" />
        </el-form-item>

        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>

        <el-divider content-position="left">价格转换规则</el-divider>

        <el-form-item label="价格规则" prop="price_rule">
          <el-radio-group v-model="form.price_rule">
            <el-radio-button label="fixed">固定倍率</el-radio-button>
            <el-radio-button label="tier">阶梯倍率</el-radio-button>
            <el-radio-button label="formula">自定义公式</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 固定倍率 -->
        <template v-if="form.price_rule === 'fixed'">
          <el-form-item label="价格倍率" prop="price_multiplier">
            <el-input-number
              v-model="form.price_multiplier"
              :min="0.1"
              :max="10"
              :step="0.1"
              :precision="2"
            />
            <span class="form-tip">原价格 × 倍率 = 新价格</span>
          </el-form-item>

          <el-form-item label="固定加价" prop="price_addition">
            <el-input-number
              v-model="form.price_addition"
              :min="0"
              :step="1"
              :precision="2"
            />
            <span class="form-tip">在倍率基础上额外增加的金额</span>
          </el-form-item>
        </template>

        <!-- 阶梯倍率 -->
        <template v-if="form.price_rule === 'tier'">
          <el-form-item label="阶梯规则">
            <div class="tier-rules">
              <div
                v-for="(tier, index) in form.tier_rules"
                :key="index"
                class="tier-item"
              >
                <el-input-number
                  v-model="tier.min"
                  placeholder="最低价"
                  :min="0"
                  :precision="2"
                  style="width: 120px"
                />
                <span class="tier-separator">-</span>
                <el-input-number
                  v-model="tier.max"
                  placeholder="最高价"
                  :min="0"
                  :precision="2"
                  style="width: 120px"
                />
                <span class="tier-separator">×</span>
                <el-input-number
                  v-model="tier.multiplier"
                  placeholder="倍率"
                  :min="0.1"
                  :max="10"
                  :step="0.1"
                  :precision="2"
                  style="width: 100px"
                />
                <el-button type="danger" link @click="removeTier(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              <el-button type="primary" link @click="addTier">
                <el-icon><Plus /></el-icon>
                添加阶梯
              </el-button>
            </div>
          </el-form-item>
        </template>

        <!-- 自定义公式 -->
        <template v-if="form.price_rule === 'formula'">
          <el-form-item label="价格公式" prop="price_formula">
            <el-input
              v-model="form.price_formula"
              placeholder="例如: x * 1.5 + 10"
            />
            <div class="formula-help">
              <p>可用变量:</p>
              <ul>
                <li><code>x</code> - 原始价格</li>
                <li><code>min(x, 100)</code> - 最小值函数</li>
                <li><code>max(x, 10)</code> - 最大值函数</li>
                <li><code>round(x)</code> - 四舍五入</li>
              </ul>
            </div>
          </el-form-item>
        </template>

        <el-form-item label="最低售价" prop="min_price">
          <el-input-number
            v-model="form.min_price"
            :min="0"
            :precision="2"
            placeholder="不限制"
          />
        </el-form-item>

        <el-form-item label="最高售价" prop="max_price">
          <el-input-number
            v-model="form.max_price"
            :min="0"
            :precision="2"
            placeholder="不限制"
          />
        </el-form-item>

        <el-divider content-position="left">图片处理</el-divider>

        <el-form-item label="自动下载图片">
          <el-switch v-model="form.download_images" />
        </el-form-item>

        <el-form-item label="自动去水印">
          <el-switch v-model="form.watermark_remove" />
        </el-form-item>

        <el-form-item label="图片压缩">
          <el-switch v-model="form.image_compress" />
        </el-form-item>

        <el-divider content-position="left">内容处理</el-divider>

        <el-form-item label="自动翻译">
          <el-switch v-model="form.auto_translate" />
        </el-form-item>

        <el-form-item v-if="form.auto_translate" label="目标语言">
          <el-select v-model="form.translate_to" style="width: 200px">
            <el-option label="英语" value="en" />
            <el-option label="泰语" value="th" />
            <el-option label="越南语" value="vi" />
            <el-option label="印尼语" value="id" />
            <el-option label="马来语" value="ms" />
            <el-option label="菲律宾语" value="tl" />
          </el-select>
        </el-form-item>

        <el-form-item label="默认库存" prop="default_stock">
          <el-input-number
            v-model="form.default_stock"
            :min="0"
            :max="99999"
            :step="1"
          />
        </el-form-item>

        <el-divider content-position="left">关键词过滤</el-divider>

        <el-form-item label="必须包含">
          <el-select
            v-model="form.keyword_filter.include"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入关键词后按回车"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="排除关键词">
          <el-select
            v-model="form.keyword_filter.exclude"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入关键词后按回车"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { CollectionConfig } from '@/types/collections'
import {
  getCollectionConfigs,
  createCollectionConfig,
  updateCollectionConfig,
  deleteCollectionConfig,
  setDefaultConfig,
} from '@/api/collections'

const loading = ref(false)
const configList = ref<CollectionConfig[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive<Partial<CollectionConfig>>({
  name: '',
  price_rule: 'fixed',
  price_multiplier: 1.5,
  price_addition: 0,
  min_price: null,
  max_price: null,
  auto_translate: false,
  translate_to: 'en',
  download_images: true,
  watermark_remove: false,
  image_compress: true,
  default_stock: 999,
  keyword_filter: { include: [], exclude: [] },
  is_default: false,
  tier_rules: [],
  price_formula: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  price_rule: [{ required: true, message: '请选择价格规则', trigger: 'change' }],
  price_multiplier: [{ required: true, message: '请输入价格倍率', trigger: 'blur' }],
}

function resetForm() {
  form.name = ''
  form.price_rule = 'fixed'
  form.price_multiplier = 1.5
  form.price_addition = 0
  form.min_price = null
  form.max_price = null
  form.auto_translate = false
  form.translate_to = 'en'
  form.download_images = true
  form.watermark_remove = false
  form.image_compress = true
  form.default_stock = 999
  form.keyword_filter = { include: [], exclude: [] }
  form.is_default = false
  form.tier_rules = []
  form.price_formula = ''
}

async function fetchConfigs() {
  loading.value = true
  try {
    const res: any = await getCollectionConfigs()
    configList.value = res.results || []
  } catch (error) {
    ElMessage.error('获取配置列表失败')
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row: CollectionConfig) {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

async function handleSetDefault(row: CollectionConfig) {
  try {
    await setDefaultConfig(row.id)
    ElMessage.success('已设为默认配置')
    fetchConfigs()
  } catch (error) {
    ElMessage.error('设置失败')
  }
}

async function handleDelete(row: CollectionConfig) {
  try {
    await ElMessageBox.confirm('确定删除此配置？', '提示', { type: 'warning' })
    await deleteCollectionConfig(row.id)
    ElMessage.success('删除成功')
    fetchConfigs()
  } catch {
    // Cancelled
  }
}

function addTier() {
  if (!form.tier_rules) {
    form.tier_rules = []
  }
  form.tier_rules.push({
    min: 0,
    max: 100,
    multiplier: 1.5,
  })
}

function removeTier(index: number) {
  form.tier_rules?.splice(index, 1)
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value && form.id) {
        await updateCollectionConfig(form.id, form)
        ElMessage.success('更新成功')
      } else {
        await createCollectionConfig(form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchConfigs()
    } catch (error) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

function getPriceRuleText(rule: string): string {
  const map: Record<string, string> = {
    fixed: '固定倍率',
    tier: '阶梯倍率',
    formula: '自定义公式',
  }
  return map[rule] || rule
}

function getPriceRuleType(rule: string): string {
  const map: Record<string, string> = {
    fixed: 'primary',
    tier: 'success',
    formula: 'warning',
  }
  return map[rule] || 'info'
}

function formatDate(date: string): string {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchConfigs()
})
</script>

<style scoped lang="scss">
$primary-color: #00b5ad;

.collection-config-panel {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.default-tag {
  font-size: 10px;
  padding: 0 4px;
  height: 18px;
  line-height: 16px;
}

.image-options {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.config-form {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 10px;

  .form-tip {
    margin-left: 12px;
    color: #909399;
    font-size: 13px;
  }

  .tier-rules {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .tier-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .tier-separator {
        color: #909399;
      }
    }
  }

  .formula-help {
    margin-top: 8px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 4px;
    font-size: 13px;

    p {
      margin: 0 0 8px;
      font-weight: 500;
    }

    ul {
      margin: 0;
      padding-left: 20px;
    }

    code {
      background: #e4e7ed;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: monospace;
    }
  }
}
</style>
