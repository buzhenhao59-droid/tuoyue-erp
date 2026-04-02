# 拓岳 ERP - 产品采集系统

## 概述

拓岳 ERP 产品采集系统是一个深度克隆妙手 ERP 采集功能的完整解决方案，支持多平台商品信息采集、批量处理、价格转换和一键发布。

## 功能特性

### 1. 链接采集
- 支持多平台链接批量采集：1688、淘宝、天猫、Shopee、Lazada、TikTok
- 智能平台检测和链接解析
- 支持换行或 $$ 分隔的多链接输入
- 实时显示链接识别统计

### 2. 插件采集
- 浏览器扩展插件支持
- 一键采集当前页面商品
- 实时连接状态监控
- 支持 Chrome、Edge 等主流浏览器

### 3. 批量导入
- Excel (.xlsx, .xls) 和 CSV 格式支持
- 单次最多导入 1000 条链接
- 下载标准导入模板
- 导入结果预览和错误报告

### 4. AI 智能选品
- 基于市场趋势的智能推荐
- 竞争程度分析
- 盈利潜力评估
- 多维度筛选（平台、类目、价格、关键词）

### 5. 采集配置管理
- 价格转换规则：固定倍率、阶梯倍率、自定义公式
- 图片处理选项：自动下载、去水印、压缩
- 内容翻译设置
- 关键词过滤（包含/排除）
- 默认配置管理

### 6. 商品管理
- 多状态管理：待认领、已认领、编辑中、已发布、已忽略
- 批量操作：认领、忽略、改价、推送
- 商品详情编辑
- SKU 批量编辑
- 图片管理

### 7. 价格管理
- 批量改价：乘以系数、固定加价、固定价格、价格区间
- 取整方式：四舍五入、向上/向下取整、保留小数
- 尾数处理：.99、.88、.98、.00
- 价格预览

### 8. 推送发布
- 多店铺批量推送
- 平台自动适配
- 发布状态跟踪
- 自动翻译选项

## 技术架构

### 后端 (Django)
```
backend/apps/collections/
├── models.py          # 数据模型
├── views.py           # 视图函数
├── api.py             # API 视图集
├── serializers.py     # 序列化器
├── urls.py            # URL 路由
├── scraper.py         # 爬虫模块
├── tasks.py           # Celery 异步任务
├── admin.py           # Django 后台管理
└── __init__.py
```

### 前端 (Vue3 + TypeScript)
```
frontend/src/views/collections/
├── index.vue                          # 主页面
├── components/
│   ├── CollectionInput.vue            # 采集输入组件
│   ├── CollectionConfigPanel.vue      # 采集配置面板
│   ├── VerticalStats.vue              # 垂直统计栏
│   ├── ProductDetailDrawer.vue        # 商品详情抽屉
│   ├── BatchPriceDialog.vue           # 批量改价对话框
│   ├── BatchPushDialog.vue            # 批量推送对话框
│   ├── PluginCollection.vue           # 插件采集页面
│   ├── BulkImport.vue                 # 批量导入页面
│   └── AISelection.vue                # AI 选品页面
├── api.ts                             # API 接口
└── types.ts                           # TypeScript 类型定义
```

## API 接口列表

### 采集配置
- `GET /v1/collections/configs/` - 获取配置列表
- `POST /v1/collections/configs/` - 创建配置
- `PUT /v1/collections/configs/{id}/` - 更新配置
- `DELETE /v1/collections/configs/{id}/` - 删除配置
- `POST /v1/collections/configs/{id}/set_default/` - 设为默认

### 采集任务
- `GET /v1/collections/tasks/` - 获取任务列表
- `POST /v1/collections/tasks/` - 创建任务
- `POST /v1/collections/tasks/{id}/retry/` - 重试任务

### 采集商品
- `GET /v1/collections/products/` - 获取商品列表
- `GET /v1/collections/products/{id}/` - 获取商品详情
- `PUT /v1/collections/products/{id}/` - 更新商品
- `POST /v1/collections/products/{id}/claim/` - 认领商品
- `POST /v1/collections/products/{id}/ignore/` - 忽略商品
- `POST /v1/collections/products/{id}/start_edit/` - 开始编辑
- `POST /v1/collections/products/{id}/publish/` - 发布商品

### 批量操作
- `POST /v1/collections/products/batch_claim/` - 批量认领
- `POST /v1/collections/products/batch_ignore/` - 批量忽略
- `POST /v1/collections/products/batch_update_price/` - 批量改价
- `POST /v1/collections/products/batch_push/` - 批量推送

### 其他
- `GET /v1/collections/stats/` - 获取统计信息
- `POST /v1/collections/plugin_webhook/` - 插件数据接收
- `POST /v1/collections/batch_import/` - 批量导入
- `GET /v1/collections/ai_select/` - AI 选品分析

## 数据模型

### CollectionConfig (采集配置)
- 价格规则：固定倍率、阶梯倍率、自定义公式
- 图片处理：下载、去水印、压缩
- 翻译设置：自动翻译、目标语言
- 关键词过滤：包含词、排除词
- 类目映射

### CollectionTask (采集任务)
- 任务类型：链接采集、插件采集、API导入
- 任务状态：待执行、执行中、已完成、失败、部分成功
- 采集链接列表和状态
- 统计信息：总数、成功数、失败数

### CollectedProduct (采集商品)
- 来源信息：平台、链接、店铺
- 商品信息：标题、描述、图片、SKU
- 价格信息：原始价格、转换后价格
- 物流信息：重量、尺寸
- 业务状态：待认领、已认领、编辑中、已发布、已忽略

## 安装部署

### 后端依赖
```bash
pip install requests beautifulsoup4 pandas celery
```

### 前端依赖
```bash
npm install element-plus @element-plus/icons-vue
```

### 数据库迁移
```bash
python manage.py makemigrations collections
python manage.py migrate
```

### 启动 Celery
```bash
celery -A config worker -l info
```

## 使用指南

### 1. 创建采集配置
1. 进入"采集配置"标签页
2. 点击"新建配置"
3. 设置价格规则、图片处理、翻译等选项
4. 保存配置并设为默认（可选）

### 2. 链接采集
1. 进入"链接采集"标签页
2. 粘贴商品链接（支持多链接，用换行或 $$ 分隔）
3. 选择采集配置
4. 点击"开始采集"

### 3. 批量改价
1. 在商品列表中选择要改价的商品
2. 点击"批量改价"
3. 选择改价方式并设置参数
4. 预览价格后确认

### 4. 推送到店铺
1. 选择要推送的商品
2. 点击"批量推送"
3. 选择目标店铺
4. 确认推送

## 开发计划

### 已完成
- [x] 基础采集功能
- [x] 多平台爬虫支持
- [x] 采集配置管理
- [x] 批量操作功能
- [x] 价格转换规则
- [x] 商品编辑功能
- [x] 插件采集框架
- [x] 批量导入功能
- [x] AI 选品界面

### 待开发
- [ ] 浏览器插件开发
- [ ] 图片自动去水印算法
- [ ] AI 智能翻译集成
- [ ] 更多电商平台适配
- [ ] 采集任务调度优化
- [ ] 数据统计报表

## 注意事项

1. 爬虫模块需要处理反爬机制，建议添加代理和请求频率控制
2. 图片下载需要足够的存储空间
3. 异步任务需要配置 Celery 和消息队列（Redis/RabbitMQ）
4. 生产环境需要配置适当的日志和监控

## 许可证

MIT License
