-- 拓岳 ERP 数据库 Schema (MySQL)
-- 支持多租户、多平台、跨境电商业务
-- 字符集: utf8mb4

-- ============================================
-- 1. 租户与基础架构
-- ============================================

CREATE TABLE `tenants` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT '租户名称',
    `code` VARCHAR(50) UNIQUE NOT NULL COMMENT '租户编码',
    `status` TINYINT DEFAULT 1 COMMENT '状态: 0-禁用, 1-启用',
    `expired_at` DATETIME COMMENT '过期时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_code` (`code`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='租户表';

CREATE TABLE `users` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `username` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100),
    `phone` VARCHAR(20),
    `password_hash` VARCHAR(255) NOT NULL,
    `real_name` VARCHAR(50),
    `avatar` VARCHAR(255),
    `role` ENUM('admin', 'manager', 'operator', 'viewer') DEFAULT 'operator',
    `status` TINYINT DEFAULT 1,
    `last_login_at` DATETIME,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_tenant_username` (`tenant_id`, `username`),
    INDEX `idx_tenant` (`tenant_id`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ============================================
-- 2. 平台与店铺管理
-- ============================================

CREATE TABLE `platforms` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(20) UNIQUE NOT NULL COMMENT '平台代码: tiktok, shopee, lazada, 1688',
    `name` VARCHAR(50) NOT NULL COMMENT '平台名称',
    `name_en` VARCHAR(50) COMMENT '英文名称',
    `logo_url` VARCHAR(255),
    `website` VARCHAR(100),
    `supported_features` JSON COMMENT '支持的功能列表',
    `status` TINYINT DEFAULT 1,
    `sort_order` INT DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_code` (`code`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='电商平台';

-- 初始化平台数据
INSERT INTO `platforms` (`code`, `name`, `name_en`, `logo_url`, `supported_features`) VALUES
('tiktok', 'TikTok Shop', 'TikTok Shop', '/static/platforms/tiktok.svg', '["order", "product", "collection"]'),
('shopee', 'Shopee', 'Shopee', '/static/platforms/shopee.svg', '["order", "product", "collection"]'),
('lazada', 'Lazada', 'Lazada', '/static/platforms/lazada.svg', '["order", "product"]'),
('1688', '1688', '1688', '/static/platforms/1688.svg', '["collection"]');

CREATE TABLE `shops` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `platform_id` INT UNSIGNED NOT NULL,
    `shop_name` VARCHAR(100) NOT NULL COMMENT '店铺名称',
    `shop_code` VARCHAR(50) COMMENT '店铺编码',
    `site_code` VARCHAR(20) COMMENT '站点代码: SG, MY, TH, ID, PH, VN, TW',
    `access_token` TEXT COMMENT '访问令牌',
    `refresh_token` TEXT COMMENT '刷新令牌',
    `token_expires_at` DATETIME COMMENT '令牌过期时间',
    `platform_shop_id` VARCHAR(100) COMMENT '平台侧店铺ID',
    `auth_status` ENUM('pending', 'authorized', 'expired', 'revoked') DEFAULT 'pending',
    `sync_status` ENUM('pending', 'syncing', 'completed', 'failed') DEFAULT 'pending',
    `last_sync_at` DATETIME,
    `settings` JSON COMMENT '店铺配置',
    `status` TINYINT DEFAULT 1,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_tenant` (`tenant_id`),
    INDEX `idx_platform` (`platform_id`),
    INDEX `idx_auth_status` (`auth_status`),
    UNIQUE KEY `uk_tenant_platform_shop` (`tenant_id`, `platform_id`, `platform_shop_id`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`platform_id`) REFERENCES `platforms`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='店铺授权';

-- ============================================
-- 3. 产品采集模块
-- ============================================

CREATE TABLE `collection_tasks` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `platform_id` INT UNSIGNED NOT NULL,
    `source_url` TEXT NOT NULL COMMENT '采集源链接',
    `source_platform` VARCHAR(20) COMMENT '来源平台: 1688, taobao',
    `status` ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    `error_msg` TEXT,
    `retry_count` TINYINT DEFAULT 0,
    `started_at` DATETIME,
    `completed_at` DATETIME,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_tenant` (`tenant_id`),
    INDEX `idx_user` (`user_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created` (`created_at`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
    FOREIGN KEY (`platform_id`) REFERENCES `platforms`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采集任务';

CREATE TABLE `collected_products` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `task_id` BIGINT UNSIGNED,
    `platform_id` INT UNSIGNED NOT NULL,
    `source_url` TEXT NOT NULL,
    `source_platform` VARCHAR(20) NOT NULL,
    `source_id` VARCHAR(100) COMMENT '源平台商品ID',
    `title` VARCHAR(500) NOT NULL COMMENT '商品标题',
    `main_image` VARCHAR(500) COMMENT '主图URL',
    `images` JSON COMMENT '图片列表',
    `description` TEXT COMMENT '商品描述',
    `original_price` DECIMAL(15,2) COMMENT '原价',
    `price` DECIMAL(15,2) COMMENT '售价',
    `currency` VARCHAR(10) DEFAULT 'CNY',
    `sku_attributes` JSON COMMENT 'SKU属性: [{name: "颜色", values: ["红", "蓝"]}]',
    `skus` JSON COMMENT 'SKU列表',
    `category_id` VARCHAR(50) COMMENT '类目ID',
    `category_name` VARCHAR(100) COMMENT '类目名称',
    `brand` VARCHAR(100),
    `weight` DECIMAL(10,3) COMMENT '重量kg',
    `status` ENUM('pending', 'claimed', 'published', 'ignored') DEFAULT 'pending',
    `claimed_by` BIGINT UNSIGNED,
    `claimed_at` DATETIME,
    `published_product_id` BIGINT UNSIGNED,
    `collected_data` JSON COMMENT '原始采集数据',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_tenant` (`tenant_id`),
    INDEX `idx_task` (`task_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_source` (`source_platform`, `source_id`),
    INDEX `idx_claimed` (`claimed_by`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`task_id`) REFERENCES `collection_tasks`(`id`),
    FOREIGN KEY (`claimed_by`) REFERENCES `users`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采集商品';

-- ============================================
-- 4. 商品管理
-- ============================================

CREATE TABLE `products` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `spu_code` VARCHAR(50) UNIQUE COMMENT 'SPU编码',
    `name` VARCHAR(200) NOT NULL,
    `name_en` VARCHAR(200),
    `description` TEXT,
    `category_id` VARCHAR(50),
    `category_path` VARCHAR(200),
    `brand` VARCHAR(100),
    `main_image` VARCHAR(500),
    `images` JSON,
    `video_url` VARCHAR(500),
    `weight` DECIMAL(10,3) DEFAULT 0,
    `length` DECIMAL(10,2) DEFAULT 0 COMMENT '长cm',
    `width` DECIMAL(10,2) DEFAULT 0 COMMENT '宽cm',
    `height` DECIMAL(10,2) DEFAULT 0 COMMENT '高cm',
    `material` VARCHAR(100),
    `origin` VARCHAR(50) COMMENT '产地',
    `hs_code` VARCHAR(20) COMMENT '海关编码',
    `status` ENUM('draft', 'active', 'inactive', 'archived') DEFAULT 'draft',
    `created_by` BIGINT UNSIGNED,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_tenant` (`tenant_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_spu` (`spu_code`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品SPU';

CREATE TABLE `product_skus` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `product_id` BIGINT UNSIGNED NOT NULL,
    `sku_code` VARCHAR(50) NOT NULL COMMENT 'SKU编码',
    `barcode` VARCHAR(50) COMMENT '条形码',
    `attributes` JSON COMMENT '属性: {color: "红色", size: "XL"}',
    `image` VARCHAR(500),
    `cost_price` DECIMAL(15,2) DEFAULT 0 COMMENT '成本价',
    `sale_price` DECIMAL(15,2) DEFAULT 0 COMMENT '销售价',
    `market_price` DECIMAL(15,2) DEFAULT 0 COMMENT '市场价',
    `weight` DECIMAL(10,3),
    `status` TINYINT DEFAULT 1,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_tenant_sku` (`tenant_id`, `sku_code`),
    INDEX `idx_product` (`product_id`),
    INDEX `idx_barcode` (`barcode`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品SKU';

-- ============================================
-- 5. 库存管理
-- ============================================

CREATE TABLE `inventory` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `sku_id` BIGINT UNSIGNED NOT NULL,
    `warehouse_id` BIGINT UNSIGNED,
    `available_qty` INT DEFAULT 0 COMMENT '可用库存',
    `locked_qty` INT DEFAULT 0 COMMENT '锁定库存',
    `in_transit_qty` INT DEFAULT 0 COMMENT '在途库存',
    `safety_stock` INT DEFAULT 0 COMMENT '安全库存',
    `avg_daily_sales` DECIMAL(10,2) DEFAULT 0 COMMENT '日均销量',
    `last_sale_at` DATETIME,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_tenant_sku_warehouse` (`tenant_id`, `sku_id`, `warehouse_id`),
    INDEX `idx_sku` (`sku_id`),
    INDEX `idx_low_stock` (`available_qty`, `safety_stock`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`sku_id`) REFERENCES `product_skus`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存';

CREATE TABLE `warehouses` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `code` VARCHAR(50),
    `type` ENUM('self', 'third_party', 'fba') DEFAULT 'self',
    `address` VARCHAR(255),
    `contact_name` VARCHAR(50),
    `contact_phone` VARCHAR(20),
    `status` TINYINT DEFAULT 1,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_tenant` (`tenant_id`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='仓库';

CREATE TABLE `purchase_orders` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `po_code` VARCHAR(50) UNIQUE NOT NULL COMMENT '采购单号',
    `supplier_id` BIGINT UNSIGNED,
    `warehouse_id` BIGINT UNSIGNED,
    `total_amount` DECIMAL(15,2) DEFAULT 0,
    `total_qty` INT DEFAULT 0,
    `status` ENUM('draft', 'pending', 'partial', 'completed', 'cancelled') DEFAULT 'draft',
    `notes` TEXT,
    `created_by` BIGINT UNSIGNED,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_tenant` (`tenant_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_po_code` (`po_code`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采购单';

CREATE TABLE `purchase_order_items` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `po_id` BIGINT UNSIGNED NOT NULL,
    `sku_id` BIGINT UNSIGNED NOT NULL,
    `qty` INT NOT NULL COMMENT '采购数量',
    `received_qty` INT DEFAULT 0 COMMENT '已收货',
    `price` DECIMAL(15,2) COMMENT '采购单价',
    `amount` DECIMAL(15,2) COMMENT '金额',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_po` (`po_id`),
    INDEX `idx_sku` (`sku_id`),
    FOREIGN KEY (`po_id`) REFERENCES `purchase_orders`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`sku_id`) REFERENCES `product_skus`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采购单明细';

-- ============================================
-- 6. 订单管理
-- ============================================

CREATE TABLE `orders` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `shop_id` BIGINT UNSIGNED NOT NULL,
    `platform_id` INT UNSIGNED NOT NULL,
    `platform_order_id` VARCHAR(100) NOT NULL COMMENT '平台订单号',
    `order_code` VARCHAR(50) UNIQUE COMMENT '系统订单号',
    `status` ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded') DEFAULT 'pending',
    `sub_status` VARCHAR(50) COMMENT '子状态',
    `order_time` DATETIME NOT NULL COMMENT '下单时间',
    `pay_time` DATETIME COMMENT '支付时间',
    `ship_time` DATETIME COMMENT '发货时间',
    `currency` VARCHAR(10) DEFAULT 'USD',
    `total_amount` DECIMAL(15,2) DEFAULT 0 COMMENT '订单金额',
    `product_amount` DECIMAL(15,2) DEFAULT 0,
    `shipping_fee` DECIMAL(15,2) DEFAULT 0,
    `tax_amount` DECIMAL(15,2) DEFAULT 0,
    `discount_amount` DECIMAL(15,2) DEFAULT 0,
    `profit` DECIMAL(15,2) DEFAULT 0 COMMENT '预估利润',
    `profit_rate` DECIMAL(5,2) DEFAULT 0 COMMENT '利润率%',
    `buyer_name` VARCHAR(100),
    `buyer_email` VARCHAR(100),
    `buyer_phone` VARCHAR(20),
    `receiver_name` VARCHAR(100),
    `receiver_phone` VARCHAR(20),
    `receiver_country` VARCHAR(50),
    `receiver_state` VARCHAR(100),
    `receiver_city` VARCHAR(100),
    `receiver_district` VARCHAR(100),
    `receiver_address` VARCHAR(500),
    `receiver_zip` VARCHAR(20),
    `logistics_company` VARCHAR(50) COMMENT '物流公司',
    `tracking_no` VARCHAR(100) COMMENT '运单号',
    `remark` TEXT,
    `risk_flag` TINYINT DEFAULT 0 COMMENT '风险标记',
    `synced_at` DATETIME COMMENT '同步时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_shop_platform_order` (`shop_id`, `platform_order_id`),
    INDEX `idx_tenant` (`tenant_id`),
    INDEX `idx_shop` (`shop_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_order_time` (`order_time`),
    INDEX `idx_tracking` (`tracking_no`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`shop_id`) REFERENCES `shops`(`id`),
    FOREIGN KEY (`platform_id`) REFERENCES `platforms`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单';

CREATE TABLE `order_items` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `order_id` BIGINT UNSIGNED NOT NULL,
    `product_id` BIGINT UNSIGNED,
    `sku_id` BIGINT UNSIGNED,
    `platform_item_id` VARCHAR(100) COMMENT '平台明细ID',
    `platform_sku_id` VARCHAR(100) COMMENT '平台SKU ID',
    `product_name` VARCHAR(200),
    `sku_name` VARCHAR(200),
    `image` VARCHAR(500),
    `qty` INT NOT NULL,
    `price` DECIMAL(15,2),
    `total_amount` DECIMAL(15,2),
    `cost_price` DECIMAL(15,2) COMMENT '成本价',
    `profit` DECIMAL(15,2) COMMENT '单品利润',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_order` (`order_id`),
    INDEX `idx_sku` (`sku_id`),
    FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`),
    FOREIGN KEY (`sku_id`) REFERENCES `product_skus`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单明细';

-- ============================================
-- 7. 财务数据
-- ============================================

CREATE TABLE `daily_stats` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `shop_id` BIGINT UNSIGNED,
    `stat_date` DATE NOT NULL,
    `order_count` INT DEFAULT 0,
    `valid_order_count` INT DEFAULT 0,
    `total_amount` DECIMAL(15,2) DEFAULT 0,
    `product_amount` DECIMAL(15,2) DEFAULT 0,
    `shipping_fee` DECIMAL(15,2) DEFAULT 0,
    `total_cost` DECIMAL(15,2) DEFAULT 0,
    `profit` DECIMAL(15,2) DEFAULT 0,
    `profit_rate` DECIMAL(5,2) DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_tenant_shop_date` (`tenant_id`, `shop_id`, `stat_date`),
    INDEX `idx_stat_date` (`stat_date`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`shop_id`) REFERENCES `shops`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日统计';

-- ============================================
-- 8. 系统配置
-- ============================================

CREATE TABLE `system_configs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `group` VARCHAR(50) NOT NULL COMMENT '配置分组',
    `key` VARCHAR(100) NOT NULL COMMENT '配置键',
    `value` TEXT COMMENT '配置值',
    `type` ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    `description` VARCHAR(255),
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_tenant_group_key` (`tenant_id`, `group`, `key`),
    INDEX `idx_group` (`group`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置';

CREATE TABLE `operation_logs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `tenant_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED,
    `action` VARCHAR(50) NOT NULL COMMENT '操作类型',
    `target_type` VARCHAR(50) COMMENT '对象类型',
    `target_id` VARCHAR(100) COMMENT '对象ID',
    `before_data` JSON,
    `after_data` JSON,
    `ip_address` VARCHAR(50),
    `user_agent` VARCHAR(500),
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_tenant` (`tenant_id`),
    INDEX `idx_user` (`user_id`),
    INDEX `idx_action` (`action`),
    INDEX `idx_created` (`created_at`),
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志';
