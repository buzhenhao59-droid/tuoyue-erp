-- ============================================================
-- 拓岳ERP数据库设计 - 核心表结构 (Part 3: 库存、订单、供应商模块)
-- ============================================================

-- ============================================================
-- 4. 库存管理模块 (Inventory)
-- ============================================================

-- 仓库表
CREATE TABLE `warehouses` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '仓库ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `name` VARCHAR(100) NOT NULL COMMENT '仓库名称',
    `code` VARCHAR(50) NOT NULL COMMENT '仓库编码',
    `type` VARCHAR(20) NOT NULL DEFAULT 'self' COMMENT '类型: self-自营 third-第三方',
    `country` VARCHAR(50) NULL COMMENT '国家',
    `province` VARCHAR(50) NULL COMMENT '省/州',
    `city` VARCHAR(50) NULL COMMENT '城市',
    `address` VARCHAR(255) NULL COMMENT '详细地址',
    `contact_name` VARCHAR(50) NULL COMMENT '联系人',
    `contact_phone` VARCHAR(20) NULL COMMENT '联系电话',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-禁用 1-启用',
    `is_default` TINYINT NOT NULL DEFAULT 0 COMMENT '是否默认仓库',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_tenant_code` (`tenant_id`, `code`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_status` (`status`),
    CONSTRAINT `fk_warehouses_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='仓库表';

-- 库存表
CREATE TABLE `inventories` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '库存ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `warehouse_id` BIGINT UNSIGNED NOT NULL COMMENT '仓库ID',
    `sku_id` BIGINT UNSIGNED NOT NULL COMMENT 'SKU ID',
    `quantity` INT NOT NULL DEFAULT 0 COMMENT '可用库存',
    `locked_quantity` INT NOT NULL DEFAULT 0 COMMENT '锁定库存',
    `warning_threshold` INT NOT NULL DEFAULT 10 COMMENT '预警阈值',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    `last_check_at` DATETIME NULL COMMENT '最后盘点时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_warehouse_sku` (`warehouse_id`, `sku_id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_sku_id` (`sku_id`),
    INDEX `idx_quantity` (`quantity`),
    CONSTRAINT `fk_inventories_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_inventories_warehouse` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_inventories_sku` FOREIGN KEY (`sku_id`) REFERENCES `product_skus` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='库存表';

-- 库存流水表
CREATE TABLE `inventory_logs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '流水ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `warehouse_id` BIGINT UNSIGNED NOT NULL COMMENT '仓库ID',
    `sku_id` BIGINT UNSIGNED NOT NULL COMMENT 'SKU ID',
    `type` VARCHAR(20) NOT NULL COMMENT '类型: in-入库 out-出库 adjust-调整',
    `quantity` INT NOT NULL COMMENT '变动数量(正数增加,负数减少)',
    `before_qty` INT NOT NULL COMMENT '变动前数量',
    `after_qty` INT NOT NULL COMMENT '变动后数量',
    `biz_type` VARCHAR(50) NULL COMMENT '业务类型: purchase-采购 sale-销售 return-退货',
    `biz_no` VARCHAR(50) NULL COMMENT '业务单号',
    `remark` VARCHAR(255) NULL COMMENT '备注',
    `operator_id` BIGINT UNSIGNED NULL COMMENT '操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_warehouse_id` (`warehouse_id`),
    INDEX `idx_sku_id` (`sku_id`),
    INDEX `idx_type` (`type`),
    INDEX `idx_biz_no` (`biz_no`),
    INDEX `idx_created_at` (`created_at`),
    CONSTRAINT `fk_inventory_logs_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='库存流水表';

-- ============================================================
-- 5. 订单管理模块 (Order)
-- ============================================================

-- 订单主表
CREATE TABLE `orders` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '订单ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `order_no` VARCHAR(50) NOT NULL COMMENT '系统订单号',
    `platform_order_no` VARCHAR(100) NOT NULL COMMENT '平台订单号',
    `shop_id` BIGINT UNSIGNED NOT NULL COMMENT '店铺ID',
    `platform_id` INT UNSIGNED NOT NULL COMMENT '平台ID',
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态: pending-待处理 paid-已付款 shipped-已发货 completed-已完成 cancelled-已取消',
    `order_status` VARCHAR(50) NULL COMMENT '平台原始状态',
    `currency` VARCHAR(10) NOT NULL DEFAULT 'USD' COMMENT '币种',
    `total_amount` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '订单总金额',
    `product_amount` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '商品金额',
    `shipping_fee` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '运费',
    `discount_amount` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '优惠金额',
    `tax_amount` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '税费',
    `paid_amount` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '实付金额',
    `buyer_id` VARCHAR(100) NULL COMMENT '买家ID',
    `buyer_name` VARCHAR(100) NULL COMMENT '买家名称',
    `buyer_email` VARCHAR(100) NULL COMMENT '买家邮箱',
    `buyer_phone` VARCHAR(50) NULL COMMENT '买家电话',
    `receiver_name` VARCHAR(100) NULL COMMENT '收件人',
    `receiver_phone` VARCHAR(50) NULL COMMENT '收件电话',
    `receiver_country` VARCHAR(50) NULL COMMENT '国家',
    `receiver_province` VARCHAR(100) NULL COMMENT '省/州',
    `receiver_city` VARCHAR(100) NULL COMMENT '城市',
    `receiver_district` VARCHAR(100) NULL COMMENT '区/县',
    `receiver_address` VARCHAR(500) NULL COMMENT '详细地址',
    `receiver_zipcode` VARCHAR(20) NULL COMMENT '邮编',
    `remark` TEXT NULL COMMENT '订单备注',
    `buyer_message` TEXT NULL COMMENT '买家留言',
    `seller_memo` TEXT NULL COMMENT '卖家备注',
    `paid_at` DATETIME NULL COMMENT '付款时间',
    `shipped_at` DATETIME NULL COMMENT '发货时间',
    `completed_at` DATETIME NULL COMMENT '完成时间',
    `synced_at` DATETIME NULL COMMENT '同步时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_platform_order` (`shop_id`, `platform_order_no`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_order_no` (`order_no`),
    INDEX `idx_platform_order_no` (`platform_order_no`),
    INDEX `idx_status` (`status`),
    INDEX `idx_shop_id` (`shop_id`),
    INDEX `idx_paid_at` (`paid_at`),
    INDEX `idx_created_at` (`created_at`),
    CONSTRAINT `fk_orders_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_orders_shop` FOREIGN KEY (`shop_id`) REFERENCES `shops` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_orders_platform` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单主表';

-- 订单商品明细表
CREATE TABLE `order_items` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '明细ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `order_id` BIGINT UNSIGNED NOT NULL COMMENT '订单ID',
    `product_id` BIGINT UNSIGNED NULL COMMENT '商品ID',
    `sku_id` BIGINT UNSIGNED NULL COMMENT 'SKU ID',
    `platform_product_id` VARCHAR(100) NULL COMMENT '平台商品ID',
    `platform_sku_id` VARCHAR(100) NULL COMMENT '平台SKU ID',
    `product_name` VARCHAR(255) NOT NULL COMMENT '商品名称',
    `sku_name` VARCHAR(255) NULL COMMENT 'SKU规格',
    `image` VARCHAR(500) NULL COMMENT '商品图片',
    `quantity` INT NOT NULL DEFAULT 1 COMMENT '数量',
    `unit_price` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '单价',
    `total_price` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '总价',
    `cost_price` DECIMAL(12,2) NULL COMMENT '成本价',
    `weight` DECIMAL(10,3) NULL COMMENT '重量',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_order_id` (`order_id`),
    INDEX `idx_sku_id` (`sku_id`),
    CONSTRAINT `fk_order_items_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_order_items_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
    CONSTRAINT `fk_order_items_sku` FOREIGN KEY (`sku_id`) REFERENCES `product_skus` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单商品明细表';

-- 物流表
CREATE TABLE `shipments` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '物流ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `order_id` BIGINT UNSIGNED NOT NULL COMMENT '订单ID',
    `tracking_no` VARCHAR(100) NOT NULL COMMENT '物流单号',
    `carrier_id` BIGINT UNSIGNED NULL COMMENT '物流商ID',
    `carrier_name` VARCHAR(50) NULL COMMENT '物流商名称',
    `carrier_code` VARCHAR(50) NULL COMMENT '物流商编码',
    `shipping_method` VARCHAR(50) NULL COMMENT '运输方式',
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态: pending-待发货 shipped-已发货 delivered-已签收 returned-已退回',
    `weight` DECIMAL(10,3) NULL COMMENT '包裹重量',
    `shipping_fee` DECIMAL(10,2) NULL COMMENT '实际运费',
    `estimated_delivery` DATE NULL COMMENT '预计送达',
    `shipped_at` DATETIME NULL COMMENT '发货时间',
    `delivered_at` DATETIME NULL COMMENT '送达时间',
    `tracking_data` JSON NULL COMMENT '物流轨迹数据',
    `last_sync_at` DATETIME NULL COMMENT '最后同步时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_order_id` (`order_id`),
    INDEX `idx_tracking_no` (`tracking_no`),
    INDEX `idx_status` (`status`),
    CONSTRAINT `fk_shipments_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_shipments_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物流表';

-- ============================================================
-- 6. 供应商与采购模块 (Supplier & Purchase)
-- ============================================================

-- 供应商表
CREATE TABLE `suppliers` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '供应商ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `name` VARCHAR(100) NOT NULL COMMENT '供应商名称',
    `code` VARCHAR(50) NULL COMMENT '供应商编码',
    `contact_person` VARCHAR(50) NULL COMMENT '联系人',
    `contact_phone` VARCHAR(20) NULL COMMENT '联系电话',
    `contact_email` VARCHAR(100) NULL COMMENT '联系邮箱',
    `address` VARCHAR(255) NULL COMMENT '地址',
    `website` VARCHAR(255) NULL COMMENT '网站',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-禁用 1-启用',
    `remark` TEXT NULL COMMENT '备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_status` (`status`),
    CONSTRAINT `fk_suppliers_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='供应商表';

-- 采购订单表
CREATE TABLE `purchase_orders` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '采购单ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `po_no` VARCHAR(50) NOT NULL COMMENT '采购单号',
    `supplier_id` BIGINT UNSIGNED NOT NULL COMMENT '供应商ID',
    `warehouse_id` BIGINT UNSIGNED NOT NULL COMMENT '入库仓库ID',
    `status` VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '状态: draft-草稿 pending-待确认 confirmed-已确认 received-已收货 completed-已完成 cancelled-已取消',
    `total_amount` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '总金额',
    `total_quantity` INT NOT NULL DEFAULT 0 COMMENT '总数量',
    `remark` TEXT NULL COMMENT '备注',
    `created_by` BIGINT UNSIGNED NULL COMMENT '创建人',
    `confirmed_at` DATETIME NULL COMMENT '确认时间',
    `received_at` DATETIME NULL COMMENT '收货时间',
    `completed_at` DATETIME NULL COMMENT '完成时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_po_no` (`po_no`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_supplier_id` (`supplier_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`),
    CONSTRAINT `fk_purchase_orders_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_purchase_orders_supplier` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_purchase_orders_warehouse` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='采购订单表';

-- 采购订单明细表
CREATE TABLE `purchase_order_items` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '明细ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `purchase_order_id` BIGINT UNSIGNED NOT NULL COMMENT '采购单ID',
    `sku_id` BIGINT UNSIGNED NOT NULL COMMENT 'SKU ID',
    `quantity` INT NOT NULL DEFAULT 0 COMMENT '采购数量',
    `received_quantity` INT NOT NULL DEFAULT 0 COMMENT '已收货数量',
    `unit_price` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '单价',
    `total_price` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '总价',
    `remark` VARCHAR(255) NULL COMMENT '备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_purchase_order_id` (`purchase_order_id`),
    INDEX `idx_sku_id` (`sku_id`),
    CONSTRAINT `fk_purchase_items_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_purchase_items_order` FOREIGN KEY (`purchase_order_id`) REFERENCES `purchase_orders` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_purchase_items_sku` FOREIGN KEY (`sku_id`) REFERENCES `product_skus` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='采购订单明细表';

-- ============================================================
-- 7. 财务管理模块 (Finance)
-- ============================================================

-- 交易流水表
CREATE TABLE `transactions` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '交易ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `transaction_no` VARCHAR(50) NOT NULL COMMENT '交易单号',
    `biz_type` VARCHAR(20) NOT NULL COMMENT '业务类型: order-订单 purchase-采购 refund-退款 other-其他',
    `biz_id` BIGINT UNSIGNED NULL COMMENT '业务单ID',
    `biz_no` VARCHAR(50) NULL COMMENT '业务单号',
    `type` VARCHAR(10) NOT NULL COMMENT '类型: income-收入 expense-支出',
    `amount` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '金额',
    `currency` VARCHAR(10) NOT NULL DEFAULT 'USD' COMMENT '币种',
    `description` VARCHAR(255) NULL COMMENT '描述',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_transaction_no` (`transaction_no`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_biz_type` (`biz_type`),
    INDEX `idx_biz_no` (`biz_no`),
    INDEX `idx_created_at` (`created_at`),
    CONSTRAINT `fk_transactions_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='交易流水表';

-- 物流商表
CREATE TABLE `carriers` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '物流商ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `name` VARCHAR(50) NOT NULL COMMENT '名称',
    `code` VARCHAR(30) NOT NULL COMMENT '编码',
    `tracking_url` VARCHAR(255) NULL COMMENT '查询URL模板',
    `api_config` JSON NULL COMMENT 'API配置',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_tenant_code` (`tenant_id`, `code`),
    INDEX `idx_tenant_id` (`tenant_id`),
    CONSTRAINT `fk_carriers_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物流商表';

-- 初始化常用物流商数据
INSERT INTO `carriers` (`tenant_id`, `name`, `code`, `tracking_url`, `status`) VALUES
(0, 'DHL', 'dhl', 'https://www.dhl.com/en/express/tracking.html?AWB={tracking_no}', 1),
(0, 'UPS', 'ups', 'https://www.ups.com/track?tracknum={tracking_no}', 1),
(0, 'FedEx', 'fedex', 'https://www.fedex.com/apps/fedextrack/?tracknumbers={tracking_no}', 1),
(0, '顺丰速运', 'sf', 'https://www.sf-express.com/cn/sc/dynamic_function/waybill/#search/bill-number/{tracking_no}', 1),
(0, '中通快递', 'zto', 'https://www.zto.com/guestservice/track?billcode={tracking_no}', 1),
(0, '圆通速递', 'yto', 'https://www.yto.net.cn/gw/track?billCode={tracking_no}', 1);
