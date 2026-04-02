# 拓岳ERP系统 - 后端开发完成

## 项目结构

```
tuoyue-erp/backend/
├── apps/                          # 应用模块
│   ├── common/                    # 通用模块
│   │   ├── models.py             # 基础模型
│   │   ├── pagination.py         # 分页器
│   │   └── exceptions.py         # 异常处理
│   ├── users/                     # 用户管理
│   │   ├── models.py             # 用户、角色模型
│   │   ├── views.py              # 登录/用户API
│   │   ├── serializers.py        # 序列化器
│   │   └── urls.py               # URL路由
│   ├── tenants/                   # 租户管理
│   ├── platforms/                 # 平台/店铺管理
│   ├── products/                  # 商品管理
│   ├── collections/               # 产品采集
│   │   ├── models.py             # 采集任务/记录模型
│   │   ├── scraper.py            # 爬虫实现(1688/淘宝)
│   │   ├── views.py              # 采集API
│   │   └── serializers.py        # 序列化器
│   ├── orders/                    # 订单管理
│   │   ├── models.py             # 订单/订单项/状态日志/运单申请
│   │   ├── views.py              # 订单API(状态机/搜索/运单申请)
│   │   └── serializers.py        # 序列化器
│   ├── inventory/                 # 库存管理
│   │   ├── models.py             # 仓库/库存/日志/采购建议
│   │   ├── views.py              # 库存API(预警/采购建议)
│   │   └── serializers.py        # 序列化器
│   ├── suppliers/                 # 供应商管理
│   ├── finance/                   # 财务管理
│   ├── logistics/                 # 物流管理
│   └── system/                    # 系统管理
│       ├── models.py             # 配置/日志/任务/通知
│       ├── views.py              # 系统API
│       ├── dashboard_views.py    # 数据大屏API
│       └── urls.py               # 包含大屏路由
├── config/                        # 项目配置
│   ├── settings.py               # Django设置
│   ├── urls.py                   # 主路由
│   └── wsgi.py                   # WSGI配置
├── manage.py                      # Django管理脚本
├── seed_data.py                   # 数据填充脚本
└── requirements.txt               # 依赖包
```

## 已完成功能

### 1. 数据库模型 ✅
- **products**: 商品分类、SPU、SKU、平台映射
- **orders**: 订单、订单项、状态日志、运单申请
- **inventory**: 仓库、库存、库存日志、采购建议
- **collections**: 采集任务、采集记录、采集规则
- **suppliers**: 供应商、供应商商品、采购订单
- **finance**: 资金账户、交易流水、平台账单、财务报表
- **logistics**: 物流公司、物流渠道、运费、发货单
- **system**: 系统配置、操作日志、定时任务、通知

### 2. 产品采集模块 ✅
- 采集任务管理（创建/执行/取消）
- 爬虫解析逻辑（支持1688/淘宝）
- 使用requests+BeautifulSoup+Header伪装
- 采集记录存储和导入

### 3. 订单处理中心 ✅
- 订单状态机（待付款/待发货/已发货/已签收/已完成/已取消/退款）
- 复杂搜索过滤（状态/店铺/金额/时间/国家/多条件组合）
- 运单号申请Mock（90%成功率模拟）
- 批量更新状态

### 4. 数据大屏 ✅
- 聚合查询（今日/本月/总计统计）
- Echarts图表数据接口：
  - 销售趋势（近30天）
  - 按国家销售统计
  - 按平台销售统计
  - 热销商品排行
  - 订单状态分布
  - 库存分布
  - 财务概览

### 5. 采购建议 ✅
- 库存预警（低库存/零库存检测）
- 采购建议计算（基于30天销量）
- 优先级分级（紧急/高/中/低）

### 6. 店铺授权 ✅
- OAuth授权流程模拟
- 授权状态管理
- 令牌刷新/撤销
- 店铺数据同步

### 7. 数据填充 ✅
- 50条采集记录
- 100个订单（30天分布）
- 30天销售数据
- 12个商品/24个SKU
- 5个店铺/5个平台
- 3个仓库/供应商

## API接口列表

### 认证
- `POST /api/v1/auth/login/` - 登录
- `POST /api/v1/auth/logout/` - 登出

### 用户管理
- `GET/POST /api/v1/auth/users/` - 用户列表/创建
- `GET/PUT/DELETE /api/v1/auth/users/{id}/` - 用户详情
- `GET /api/v1/auth/users/me/` - 当前用户

### 订单管理
- `GET/POST /api/v1/orders/orders/` - 订单列表/创建
- `GET/PUT/DELETE /api/v1/orders/orders/{id}/` - 订单详情
- `POST /api/v1/orders/orders/{id}/update_status/` - 更新状态
- `GET /api/v1/orders/orders/statistics/` - 订单统计
- `POST /api/v1/orders/waybills/apply/` - 申请运单号

### 产品采集
- `GET/POST /api/v1/collections/tasks/` - 采集任务
- `POST /api/v1/collections/tasks/{id}/execute/` - 执行任务
- `GET/POST /api/v1/collections/records/` - 采集记录
- `POST /api/v1/collections/records/import_to_products/` - 导入商品

### 库存管理
- `GET/POST /api/v1/inventory/warehouses/` - 仓库管理
- `GET/POST /api/v1/inventory/stock/` - 库存管理
- `GET /api/v1/inventory/stock/warnings/` - 库存预警
- `GET/POST /api/v1/inventory/suggestions/` - 采购建议
- `POST /api/v1/inventory/suggestions/generate/` - 生成建议

### 数据大屏
- `GET /api/v1/system/dashboard/overview/` - 概览数据
- `GET /api/v1/system/dashboard/sales-trend/` - 销售趋势
- `GET /api/v1/system/dashboard/sales-by-country/` - 国家分布
- `GET /api/v1/system/dashboard/sales-by-platform/` - 平台分布
- `GET /api/v1/system/dashboard/top-products/` - 热销商品
- `GET /api/v1/system/dashboard/order-status/` - 订单状态
- `GET /api/v1/system/dashboard/inventory/` - 库存分布
- `GET /api/v1/system/dashboard/financial/` - 财务概览

### 店铺授权
- `GET/POST /api/v1/platforms/shops/` - 店铺管理
- `POST /api/v1/platforms/shops/{id}/authorize/` - 授权
- `POST /api/v1/platforms/shops/{id}/refresh_token/` - 刷新令牌
- `POST /api/v1/platforms/shops/{id}/sync/` - 同步数据

## 运行步骤

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

3. 填充测试数据
```bash
python seed_data.py
```

4. 启动服务
```bash
python manage.py runserver
```

5. 访问API文档
```
http://localhost:8000/api/docs/
```

## 登录信息
- 用户名: admin
- 密码: admin123
