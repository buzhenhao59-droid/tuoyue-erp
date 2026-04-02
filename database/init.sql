-- ============================================================
-- 拓岳ERP数据库初始化脚本
-- 执行顺序: schema_part1.sql -> schema_part2.sql -> schema_part3.sql
-- ============================================================

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS tuoyue_erp 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE tuoyue_erp;

-- 执行各模块SQL文件
-- 注意: 实际部署时请按顺序执行以下文件:
-- source schema_part1.sql;  -- 租户、用户、平台、店铺
-- source schema_part2.sql;  -- 商品、采集
-- source schema_part3.sql;  -- 库存、订单、供应商、财务

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 初始化系统数据
-- ============================================================

-- 创建默认租户
INSERT INTO `tenants` (`name`, `code`, `plan`, `contact_name`, `contact_email`) VALUES
('拓岳科技', 'tuoyue', 'premium', '管理员', 'admin@tuoyue.com');

-- 创建超级管理员
-- 密码: admin123 (bcrypt加密)
INSERT INTO `users` (`tenant_id`, `username`, `password`, `email`, `real_name`, `is_superuser`, `status`) VALUES
(1, 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I1K', 'admin@tuoyue.com', '系统管理员', 1, 1);

-- 创建默认角色
INSERT INTO `roles` (`tenant_id`, `name`, `code`, `description`, `permissions`) VALUES
(1, '超级管理员', 'super_admin', '拥有所有权限', '["*"]'),
(1, '商品管理员', 'product_manager', '管理商品信息', '["product:read", "product:write"]'),
(1, '订单处理员', 'order_processor', '处理订单', '["order:read", "order:write"]'),
(1, '财务人员', 'finance', '查看财务报表', '["finance:read"]'),
(1, '普通员工', 'staff', '只读权限', '["product:read", "order:read", "inventory:read"]');

-- 关联超级管理员角色
INSERT INTO `user_roles` (`user_id`, `role_id`) VALUES (1, 1);

-- ============================================================
-- 数据库索引优化建议
-- ============================================================

-- 订单表分区建议 (大数据量时)
-- ALTER TABLE orders PARTITION BY RANGE (YEAR(created_at)) (
--     PARTITION p2023 VALUES LESS THAN (2024),
--     PARTITION p2024 VALUES LESS THAN (2025),
--     PARTITION p2025 VALUES LESS THAN (2026),
--     PARTITION p_future VALUES LESS THAN MAXVALUE
-- );

-- 库存流水表分区建议
-- ALTER TABLE inventory_logs PARTITION BY RANGE (UNIX_TIMESTAMP(created_at)) (
--     PARTITION p_before_2024 VALUES LESS THAN (UNIX_TIMESTAMP('2024-01-01')),
--     PARTITION p_2024_q1 VALUES LESS THAN (UNIX_TIMESTAMP('2024-04-01')),
--     PARTITION p_2024_q2 VALUES LESS THAN (UNIX_TIMESTAMP('2024-07-01')),
--     PARTITION p_future VALUES LESS THAN MAXVALUE
-- );
