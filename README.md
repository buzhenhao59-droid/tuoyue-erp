# 拓岳跨境电商ERP系统

## 🎯 项目概述

**拓岳ERP** (Tuoyue ERP) 是一套面向跨境电商企业的全栈ERP解决方案，深度参考妙手ERP的功能设计，采用现代化技术栈构建。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (Vue 3)                            │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │  商品管理   │ │  订单中心   │ │  库存管理   │ │  财务报表   │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       后端API (Django DRF)                       │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │  用户认证   │ │  业务逻辑   │ │  异步任务   │ │  数据同步   │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据层                                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │   MySQL    │ │   Redis    │ │   MinIO    │ │   Celery   │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 功能模块

### 1. 多平台采集
- ✅ 支持1688、淘宝、天猫商品采集
- ✅ 智能属性映射与SKU匹配
- ✅ 图片批量下载与处理
- ✅ 采集任务队列管理

### 2. 商品管理
- ✅ 商品信息管理 (SPU/SKU)
- ✅ 一键搬家（跨平台迁移）
- ✅ 批量编辑与导入导出
- ✅ 敏感词过滤
- ✅ 多语言翻译集成
- ✅ 图片水印处理

### 3. 订单中心
- ✅ 多店铺订单统一抓取
- ✅ 订单状态自动同步
- ✅ 自动化打单发货
- ✅ 物流跟踪集成
- ✅ 售后管理

### 4. 库存与供应链
- ✅ 多仓库库存管理
- ✅ 库存预警
- ✅ SKU关联管理
- ✅ 采购建议
- ✅ 供应商管理

### 5. 财务报表
- ✅ 利润自动计算
- ✅ 运费对账
- ✅ 数据可视化大屏
- ✅ 多维度报表分析

### 6. 系统管理
- ✅ RBAC权限系统
- ✅ 操作日志审计
- ✅ 多租户(SAAS)架构
- ✅ 系统配置管理

## 🛠️ 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **构建**: Vite 5.x
- **UI库**: Element Plus 2.x
- **状态**: Pinia 2.x
- **路由**: Vue Router 4.x
- **图表**: ECharts 5.x

### 后端
- **框架**: Django 4.2 LTS
- **API**: Django REST Framework 3.14+
- **认证**: JWT (SimpleJWT)
- **任务**: Celery + Redis
- **文档**: drf-spectacular

### 数据库
- **主库**: MySQL 8.0
- **缓存**: Redis 7.x
- **文件**: MinIO / OSS

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Redis 7.x

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/your-org/tuoyue-erp.git
cd tuoyue-erp
```

#### 2. 后端配置
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置数据库
cp .env.example .env
# 编辑 .env 文件配置数据库连接

# 执行迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动服务
python manage.py runserver
```

#### 3. 前端配置
```bash
cd frontend
npm install

# 配置API地址
cp .env.example .env.local
# 编辑 .env.local 文件

# 启动开发服务器
npm run dev
```

#### 4. Docker部署 (推荐)
```bash
# 一键启动所有服务
docker-compose up -d

# 执行数据库迁移
docker-compose exec backend python manage.py migrate

# 创建超级管理员
docker-compose exec backend python manage.py createsuperuser
```

## 📁 项目结构

```
tuoyue-erp/
├── docs/                    # 项目文档
│   └── architecture.md      # 架构设计文档
├── backend/                 # Django后端
│   ├── apps/                # 业务应用
│   │   ├── users/           # 用户管理
│   │   ├── products/        # 商品管理
│   │   ├── orders/          # 订单管理
│   │   ├── inventory/       # 库存管理
│   │   ├── collections/     # 采集管理
│   │   ├── finance/         # 财务管理
│   │   └── system/          # 系统管理
│   ├── config/              # 项目配置
│   └── requirements.txt     # 依赖包
├── frontend/                # Vue前端
│   ├── src/
│   │   ├── views/           # 页面视图
│   │   ├── components/      # 公共组件
│   │   ├── stores/          # 状态管理
│   │   └── api/             # API接口
│   └── package.json
├── database/                # 数据库脚本
│   ├── schema_part1.sql     # 租户、用户、平台
│   ├── schema_part2.sql     # 商品、采集
│   ├── schema_part3.sql     # 库存、订单、财务
│   └── init.sql             # 初始化数据
└── docker-compose.yml       # Docker编排
```

## 📊 数据库设计

### 核心表结构

| 模块 | 主要表 | 说明 |
|------|--------|------|
| 租户用户 | tenants, users, roles | SAAS多租户基础 |
| 平台店铺 | platforms, shops | 电商平台对接 |
| 商品管理 | products, product_skus, categories | SPU/SKU管理 |
| 采集管理 | collection_tasks, collection_records | 数据采集 |
| 订单管理 | orders, order_items, shipments | 订单全流程 |
| 库存管理 | warehouses, inventories, inventory_logs | 库存控制 |
| 供应链 | suppliers, purchase_orders | 采购管理 |
| 财务 | transactions | 资金流水 |

### 执行顺序
```bash
mysql -u root -p < database/schema_part1.sql  # 基础模块
mysql -u root -p < database/schema_part2.sql  # 商品模块
mysql -u root -p < database/schema_part3.sql  # 业务模块
mysql -u root -p < database/init.sql          # 初始化数据
```

## 🔐 安全特性

- **JWT认证**: Access Token + Refresh Token机制
- **RBAC权限**: 基于角色的访问控制
- **数据隔离**: 多租户数据隔离
- **操作审计**: 完整的操作日志记录
- **密码加密**: bcrypt算法
- **敏感数据**: AES加密存储

## 📈 性能优化

- 数据库索引优化
- Redis缓存层
- Celery异步任务
- 数据库读写分离
- 分页查询优化

## 📝 API文档

启动服务后访问:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- Admin: `http://localhost:8000/admin/`

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

[MIT](LICENSE) © 2024 拓岳科技

## 📞 联系我们

- 官网: https://www.tuoyue.com
- 邮箱: support@tuoyue.com
- 电话: 400-XXX-XXXX

---

> **注意**: 本项目为学习研究用途，参考妙手ERP设计思路。商业使用请遵守相关法律法规。
