-- ============================================================
-- 拓岳ERP数据库设计 - 核心表结构 (Part 1)
-- 数据库: MySQL 8.0
-- 字符集: utf8mb4_unicode_ci
-- 引擎: InnoDB
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS tuoyue_erp 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE tuoyue_erp;

-- ============================================================
-- 1. 租户与用户模块 (Tenant & User)
-- ============================================================

-- 租户表 (SAAS多租户基础)
CREATE TABLE `tenants` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '租户ID',
    `name` VARCHAR(100) NOT NULL COMMENT '租户名称',
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT '租户编码',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-禁用 1-启用',
    `plan` VARCHAR(20) NOT NULL DEFAULT 'basic' COMMENT '套餐: basic/standard/premium',
    `expired_at` DATETIME NULL COMMENT '到期时间',
    `contact_name` VARCHAR(50) NULL COMMENT '联系人',
    `contact_phone` VARCHAR(20) NULL COMMENT '联系电话',
    `contact_email` VARCHAR(100) NULL COMMENT '联系邮箱',
    `settings` JSON NULL COMMENT '租户配置',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_code` (`code`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='租户表';

-- 用户表
CREATE TABLE `users` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `email` VARCHAR(100) NULL COMMENT '邮箱',
    `phone` VARCHAR(20) NULL COMMENT '手机号',
    `real_name` VARCHAR(50) NULL COMMENT '真实姓名',
    `avatar` VARCHAR(255) NULL COMMENT '头像URL',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-禁用 1-启用 2-锁定',
    `is_superuser` TINYINT NOT NULL DEFAULT 0 COMMENT '是否超级管理员',
    `last_login_at` DATETIME NULL COMMENT '最后登录时间',
    `last_login_ip` VARCHAR(50) NULL COMMENT '最后登录IP',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_tenant_username` (`tenant_id`, `username`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_status` (`status`),
    CONSTRAINT `fk_users_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 角色表
CREATE TABLE `roles` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '角色ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `name` VARCHAR(50) NOT NULL COMMENT '角色名称',
    `code` VARCHAR(50) NOT NULL COMMENT '角色编码',
    `description` VARCHAR(255) NULL COMMENT '描述',
    `permissions` JSON NULL COMMENT '权限列表',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_tenant_code` (`tenant_id`, `code`),
    INDEX `idx_tenant_id` (`tenant_id`),
    CONSTRAINT `fk_roles_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 用户角色关联表
CREATE TABLE `user_roles` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `role_id` BIGINT UNSIGNED NOT NULL COMMENT '角色ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_role` (`user_id`, `role_id`),
    CONSTRAINT `fk_user_roles_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_user_roles_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';

-- 操作日志表
CREATE TABLE `operation_logs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `user_id` BIGINT UNSIGNED NULL COMMENT '用户ID',
    `username` VARCHAR(50) NULL COMMENT '用户名',
    `module` VARCHAR(50) NOT NULL COMMENT '操作模块',
    `action` VARCHAR(50) NOT NULL COMMENT '操作类型',
    `description` TEXT NULL COMMENT '操作描述',
    `request_method` VARCHAR(10) NULL COMMENT '请求方法',
    `request_url` VARCHAR(500) NULL COMMENT '请求URL',
    `request_params` JSON NULL COMMENT '请求参数',
    `response_data` JSON NULL COMMENT '响应数据',
    `ip_address` VARCHAR(50) NULL COMMENT 'IP地址',
    `user_agent` VARCHAR(500) NULL COMMENT 'User-Agent',
    `execution_time` INT NULL COMMENT '执行时间(ms)',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-失败 1-成功',
    `error_msg` TEXT NULL COMMENT '错误信息',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_module` (`module`),
    INDEX `idx_created_at` (`created_at`),
    CONSTRAINT `fk_logs_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- ============================================================
-- 2. 店铺与平台模块 (Shop & Platform)
-- ============================================================

-- 电商平台表
CREATE TABLE `platforms` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '平台ID',
    `name` VARCHAR(50) NOT NULL COMMENT '平台名称',
    `code` VARCHAR(20) NOT NULL UNIQUE COMMENT '平台编码',
    `icon` VARCHAR(255) NULL COMMENT '平台图标',
    `website` VARCHAR(255) NULL COMMENT '官网地址',
    `api_base_url` VARCHAR(255) NULL COMMENT 'API基础地址',
    `auth_type` VARCHAR(20) NULL COMMENT '认证类型: oauth/apikey',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电商平台表';

-- 初始化平台数据
INSERT INTO `platforms` (`name`, `code`, `website`, `auth_type`, `sort_order`) VALUES
('TikTok Shop', 'tiktok', 'https://seller.tiktok.com', 'oauth', 1),
('Shopee', 'shopee', 'https://seller.shopee.cn', 'oauth', 2),
('Lazada', 'lazada', 'https://sellercenter.lazada.com', 'oauth', 3),
('Amazon', 'amazon', 'https://sellercentral.amazon.com', 'oauth', 4),
('eBay', 'ebay', 'https://www.ebay.com', 'oauth', 5),
('1688', '1688', 'https://www.1688.com', 'apikey', 6),
('淘宝', 'taobao', 'https://www.taobao.com', 'oauth', 7),
('天猫', 'tmall', 'https://www.tmall.com', 'oauth', 8);

-- 店铺表
CREATE TABLE `shops` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '店铺ID',
    `tenant_id` BIGINT UNSIGNED NOT NULL COMMENT '租户ID',
    `platform_id` INT UNSIGNED NOT NULL COMMENT '平台ID',
    `name` VARCHAR(100) NOT NULL COMMENT '店铺名称',
    `shop_code` VARCHAR(50) NULL COMMENT '店铺编码',
    `platform_shop_id` VARCHAR(100) NULL COMMENT '平台店铺ID',
    `auth_token` TEXT NULL COMMENT '授权令牌(加密存储)',
    `refresh_token` TEXT NULL COMMENT '刷新令牌',
    `token_expires_at` DATETIME NULL COMMENT '令牌过期时间',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-禁用 1-启用 2-授权过期',
    `sync_status` TINYINT NOT NULL DEFAULT 0 COMMENT '同步状态: 0-未同步 1-同步中 2-同步完成',
    `last_sync_at` DATETIME NULL COMMENT '最后同步时间',
    `settings` JSON NULL COMMENT '店铺配置',
    `creator_id` BIGINT UNSIGNED NULL COMMENT '创建人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_tenant_id` (`tenant_id`),
    INDEX `idx_platform_id` (`platform_id`),
    INDEX `idx_status` (`status`),
    CONSTRAINT `fk_shops_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_shops_platform` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='店铺表';
