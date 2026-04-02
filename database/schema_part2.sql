-- ============================================================
-- 拓岳ERP数据库设计 - 核心表结构 (Part 2: 商品管理模块)
-- ============================================================

-- 商品分类表
CREATE TABLE `product_categories` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `parent_id` BIGINT UNSIGNED NULL DEFAULT 0 COMMENT '父分类ID',
    `name` VARCHAR(100) NOT NULL COMMENT '分类名称',
    `code` VARCHAR(50) NULL COMMENT '分类编码',
    `level` TINYINT NOT NULL DEFAULT 1 COMMENT '层级',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_parent_id` (`parent_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品分类表';

-- 商品SPU表
CREATE TABLE `products` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '商品ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `category_id` BIGINT UNSIGNED NULL COMMENT '分类ID',
    `spu_code` VARCHAR(50) NOT NULL COMMENT 'SPU编码',
    `name` VARCHAR(255) NOT NULL COMMENT '商品名称',
    `name_en` VARCHAR(255) NULL COMMENT '英文名称',
    `description` TEXT NULL COMMENT '商品描述',
    `description_en` TEXT NULL COMMENT '英文描述',
    `brand` VARCHAR(50) NULL COMMENT '品牌',
    `main_image` VARCHAR(500) NULL COMMENT '主图URL',
    `images` JSON NULL COMMENT '图片列表',
    `weight` DECIMAL(10,3) NULL COMMENT '重量(kg)',
    `length` DECIMAL(10,2) NULL COMMENT '长(cm)',
    `width` DECIMAL(10,2) NULL COMMENT '宽(cm)',
    `height` DECIMAL(10,2) NULL COMMENT '高(cm)',
    `material` VARCHAR(100) NULL COMMENT '材质',
    `origin` VARCHAR(50) NULL COMMENT '产地',
    `hs_code` VARCHAR(20) NULL COMMENT '海关编码',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 0-草稿 1-上架 2-下架',
    `source_type` VARCHAR(20) NULL COMMENT '来源: manual/collection/import',
    `source_url` VARCHAR(500) NULL COMMENT '来源URL',
    `creator_id` BIGINT UNSIGNED NULL COMMENT '创建人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_tenant_spu` (`tenant_id`, `spu_code`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_category_id` (`category_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_spu_code` (`spu_code`),
    CONSTRAINT `fk_products_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_products_category` FOREIGN KEY (`category_id`) REFERENCES `product_categories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品SPU表';

-- 商品SKU表
CREATE TABLE `product_skus` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'SKU ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `product_id` BIGINT UNSIGNED NOT NULL COMMENT '商品ID',
    `sku_code` VARCHAR(50) NOT NULL COMMENT 'SKU编码',
    `barcode` VARCHAR(50) NULL COMMENT '条形码',
    `spec_info` JSON NOT NULL COMMENT '规格信息 {"颜色": "黑色", "尺寸": "XL"}',
    `spec_image` VARCHAR(500) NULL COMMENT '规格图片',
    `purchase_price` DECIMAL(12,2) NULL COMMENT '采购价',
    `cost_price` DECIMAL(12,2) NULL COMMENT '成本价',
    `sale_price` DECIMAL(12,2) NULL COMMENT '销售价',
    `market_price` DECIMAL(12,2) NULL COMMENT '市场价',
    `weight` DECIMAL(10,3) NULL COMMENT '重量(kg)',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-禁用 1-启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_tenant_sku` (`tenant_id`, `sku_code`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_product_id` (`product_id`),
    INDEX `idx_sku_code` (`sku_code`),
    INDEX `idx_barcode` (`barcode`),
    CONSTRAINT `fk_skus_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_skus_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品SKU表';

-- 商品平台映射表 (多平台刊登)
CREATE TABLE `product_platform_mappings` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '映射ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `product_id` BIGINT UNSIGNED NOT NULL COMMENT '商品ID',
    `sku_id` BIGINT UNSIGNED NULL COMMENT 'SKU ID(为空表示SPU级别)',
    `shop_id` BIGINT UNSIGNED NOT NULL COMMENT '店铺ID',
    `platform_product_id` VARCHAR(100) NULL COMMENT '平台商品ID',
    `platform_sku_id` VARCHAR(100) NULL COMMENT '平台SKU ID',
    `platform_listing_id` VARCHAR(100) NULL COMMENT '平台刊登ID',
    `listing_status` TINYINT NOT NULL DEFAULT 0 COMMENT '刊登状态: 0-未刊登 1-刊登中 2-已刊登 3-刊登失败',
    `listing_data` JSON NULL COMMENT '刊登数据快照',
    `last_listed_at` DATETIME NULL COMMENT '最后刊登时间',
    `last_sync_at` DATETIME NULL COMMENT '最后同步时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_sku_shop` (`sku_id`, `shop_id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_product_id` (`product_id`),
    INDEX `idx_shop_id` (`shop_id`),
    CONSTRAINT `fk_mappings_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_mappings_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_mappings_sku` FOREIGN KEY (`sku_id`) REFERENCES `product_skus` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_mappings_shop` FOREIGN KEY (`shop_id`) REFERENCES `shops` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品平台映射表';

-- ============================================================
-- 3. 采集管理模块 (Collection)
-- ============================================================

-- 采集任务表
CREATE TABLE `collection_tasks` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '任务ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `task_no` VARCHAR(50) NOT NULL COMMENT '任务编号',
    `name` VARCHAR(100) NOT NULL COMMENT '任务名称',
    `source_platform` VARCHAR(20) NOT NULL COMMENT '来源平台: 1688/taobao/tmall',
    `source_urls` JSON NOT NULL COMMENT '采集URL列表',
    `task_type` VARCHAR(20) NOT NULL DEFAULT 'single' COMMENT '任务类型: single-单商品 batch-批量',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 0-待执行 1-执行中 2-完成 3-失败',
    `total_count` INT NOT NULL DEFAULT 0 COMMENT '总数量',
    `success_count` INT NOT NULL DEFAULT 0 COMMENT '成功数量',
    `fail_count` INT NOT NULL DEFAULT 0 COMMENT '失败数量',
    `error_msg` TEXT NULL COMMENT '错误信息',
    `started_at` DATETIME NULL COMMENT '开始时间',
    `completed_at` DATETIME NULL COMMENT '完成时间',
    `creator_id` BIGINT UNSIGNED NULL COMMENT '创建人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_task_no` (`task_no`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`),
    CONSTRAINT `fk_collection_tasks_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='采集任务表';

-- 采集商品记录表
CREATE TABLE `collection_records` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `task_id` BIGINT UNSIGNED NOT NULL COMMENT '任务ID',
    `source_url` VARCHAR(500) NOT NULL COMMENT '来源URL',
    `source_platform` VARCHAR(20) NOT NULL COMMENT '来源平台',
    `source_product_id` VARCHAR(100) NULL COMMENT '来源商品ID',
    `title` VARCHAR(255) NULL COMMENT '商品标题',
    `main_image` VARCHAR(500) NULL COMMENT '主图',
    `price_range` VARCHAR(50) NULL COMMENT '价格区间',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 0-待采集 1-采集中 2-成功 3-失败',
    `collected_data` JSON NULL COMMENT '采集的原始数据',
    `error_msg` TEXT NULL COMMENT '错误信息',
    `product_id` BIGINT UNSIGNED NULL COMMENT '关联的商品ID(采集成功后创建)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_task_id` (`task_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_product_id` (`product_id`),
    CONSTRAINT `fk_collection_records_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_collection_records_task` FOREIGN KEY (`task_id`) REFERENCES `collection_tasks` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_collection_records_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='采集商品记录表';
