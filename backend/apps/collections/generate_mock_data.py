#!/usr/bin/env python3
"""
拓岳 ERP - 采集商品模拟数据生成脚本
生成 50 条模拟采集商品数据用于测试
"""

import os
import sys
import random
from datetime import datetime, timedelta

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
django.setup()

from django.utils import timezone
from apps.tenants.models import Tenant
from apps.users.models import User
from apps.collections.models import CollectionTask, CollectionConfig, CollectedProduct


# 模拟数据配置
PLATFORMS = [
    ('1688', '#FF6A00'),
    ('taobao', '#FF5000'),
    ('tmall', '#FF0036'),
    ('shopee', '#EE4D2D'),
    ('lazada', '#0F156D'),
    ('tiktok', '#000000'),
]

STATUSES = ['pending', 'claimed', 'editing', 'published', 'ignored']

CATEGORIES = [
    '女装', '男装', '童装', '鞋靴', '箱包', '配饰',
    '家居', '数码', '美妆', '食品', '母婴', '运动'
]

PRODUCT_TITLES = [
    '夏季新款连衣裙女显瘦气质法式茶歇裙',
    '2024新款男士休闲裤宽松直筒长裤',
    '韩版时尚女包单肩斜挎包大容量',
    '无线蓝牙耳机降噪运动跑步入耳式',
    '家用智能扫地机器人全自动吸尘',
    '网红同款口红不掉色持久保湿',
    '儿童益智玩具积木拼装',
    '不锈钢保温杯大容量便携水杯',
    '纯棉T恤男短袖夏季新款',
    '运动鞋女跑步鞋透气轻便',
    '护肤套装补水保湿美白',
    '厨房置物架收纳架多层',
    '手机壳防摔保护套硅胶',
    '床上四件套纯棉全棉',
    '电动牙刷超声波全自动',
    '太阳镜女防紫外线偏光',
    '双肩包男大容量商务背包',
    '瑜伽垫加厚防滑健身垫',
    '咖啡机家用全自动意式',
    '空气炸锅家用多功能无油',
    '智能手表运动手环计步',
    '洗发水控油蓬松去屑',
    '零食大礼包网红小吃',
    '宠物用品猫粮狗粮',
    '汽车用品车载充电器',
    '文具套装学生用品',
    '户外帐篷露营装备',
    '健身器材家用哑铃',
    '游戏手柄电脑Steam',
    '投影仪家用高清4K',
]


def generate_random_sku_attributes():
    """生成随机 SKU 属性"""
    attributes = []
    
    # 颜色属性
    colors = ['红色', '蓝色', '黑色', '白色', '粉色', '灰色', '绿色']
    if random.random() > 0.3:
        attributes.append({
            'id': 'color',
            'name': '颜色',
            'values': [{'id': f'c{i}', 'name': c, 'image': ''} 
                      for i, c in enumerate(random.sample(colors, random.randint(2, 5)))]
        })
    
    # 尺码属性
    sizes = ['S', 'M', 'L', 'XL', 'XXL', '均码']
    if random.random() > 0.4:
        attributes.append({
            'id': 'size',
            'name': '尺码',
            'values': [{'id': f's{i}', 'name': s} 
                      for i, s in enumerate(random.sample(sizes, random.randint(2, 4)))]
        })
    
    return attributes


def generate_random_skus(attributes, base_price):
    """生成随机 SKU 列表"""
    skus = []
    
    if not attributes:
        # 无规格商品
        skus.append({
            'sku_id': f'SKU{random.randint(10000, 99999)}',
            'attributes': {},
            'price': base_price,
            'stock': random.randint(10, 1000),
            'image': ''
        })
        return skus
    
    # 根据属性生成 SKU 组合
    import itertools
    
    value_lists = []
    for attr in attributes:
        value_lists.append([(attr['id'], v['name']) for v in attr['values']])
    
    combinations = list(itertools.product(*value_lists))
    
    for i, combo in enumerate(combinations):
        attrs = {k: v for k, v in combo}
        price_variation = random.uniform(-0.1, 0.2)  # 价格浮动
        skus.append({
            'sku_id': f'SKU{random.randint(10000, 99999)}-{i}',
            'attributes': attrs,
            'price': round(base_price * (1 + price_variation), 2),
            'stock': random.randint(10, 500),
            'image': ''
        })
    
    return skus


def generate_mock_data(tenant_id: int = 1, user_id: int = 1, count: int = 50):
    """生成模拟数据"""
    
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        print(f"错误: 租户 ID {tenant_id} 不存在")
        return
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print(f"错误: 用户 ID {user_id} 不存在")
        return
    
    # 获取或创建默认配置
    config, _ = CollectionConfig.objects.get_or_create(
        tenant=tenant,
        is_default=True,
        defaults={
            'name': '默认配置',
            'price_multiplier': 1.5,
            'price_addition': 0,
            'download_images': True,
            'watermark_remove': False,
            'image_compress': True,
            'auto_translate': False,
            'default_stock': 999,
        }
    )
    
    # 创建采集任务
    task = CollectionTask.objects.create(
        tenant=tenant,
        user=user,
        config=config,
        task_type='link',
        task_no=f"CJ{datetime.now().strftime('%Y%m%d%H%M%S')}",
        name='模拟采集任务',
        source_urls=[],
        total_count=count,
        status='completed',
        started_at=timezone.now() - timedelta(hours=2),
        completed_at=timezone.now(),
        success_count=count,
        fail_count=0
    )
    
    # 生成商品数据
    created_count = 0
    
    for i in range(count):
        platform, platform_color = random.choice(PLATFORMS)
        status = random.choice(STATUSES)
        category = random.choice(CATEGORIES)
        title = random.choice(PRODUCT_TITLES)
        
        # 添加随机后缀使标题更独特
        title += f" {random.choice(['新款', '热销', '特价', '限量', '爆款'])}"
        
        # 生成价格
        original_price = round(random.uniform(10, 500), 2)
        price_multiplier = float(config.price_multiplier)
        converted_price = round(original_price * price_multiplier, 2)
        
        # 生成 SKU
        sku_attributes = generate_random_sku_attributes()
        skus = generate_random_skus(sku_attributes, converted_price)
        
        # 生成图片
        image_id = random.randint(100000, 999999)
        main_image = f"https://via.placeholder.com/400x400/{platform_color[1:]}/ffffff?text={platform}+{image_id}"
        images = [
            f"https://via.placeholder.com/400x400/{platform_color[1:]}/ffffff?text={platform}+{image_id}-{j}"
            for j in range(random.randint(3, 8))
        ]
        
        # 创建时间（最近30天内随机）
        created_at = timezone.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # 认领信息
        claimed_by = None
        claimed_at = None
        if status in ['claimed', 'editing', 'published']:
            claimed_by = user
            claimed_at = created_at + timedelta(hours=random.randint(1, 24))
        
        # 创建商品记录
        product = CollectedProduct.objects.create(
            tenant=tenant,
            task=task,
            config=config,
            source_url=f"https://example-{platform}.com/product/{random.randint(1000000, 9999999)}",
            source_platform=platform,
            source_id=str(random.randint(100000000, 999999999)),
            source_shop_id=str(random.randint(10000, 99999)),
            source_shop_name=f"{platform}店铺{random.randint(1, 100)}",
            collect_status='success',
            title=title,
            title_en=title,  # 简化处理
            description=f"这是{title}的详细描述，包含商品特点、规格参数等信息。",
            main_image=main_image,
            images=images,
            original_price_min=original_price,
            original_price_max=original_price * random.uniform(1.0, 1.5),
            price_min=converted_price,
            price_max=converted_price * random.uniform(1.0, 1.2),
            currency='CNY' if platform in ['1688', 'taobao', 'tmall'] else 'USD',
            source_category_name=category,
            sku_attributes=sku_attributes,
            skus=skus,
            sku_count=len(skus),
            status=status,
            claimed_by=claimed_by,
            claimed_at=claimed_at,
            weight=round(random.uniform(0.1, 5.0), 3),
            raw_data={},
        )
        
        # 更新创建时间
        CollectedProduct.objects.filter(id=product.id).update(created_at=created_at)
        
        created_count += 1
        print(f"[{created_count}/{count}] 创建商品: {title[:30]}... ({platform})")
    
    print(f"\n✅ 成功生成 {created_count} 条模拟数据！")
    print(f"\n统计信息:")
    print(f"  - 任务ID: {task.id}")
    print(f"  - 任务编号: {task.task_no}")
    print(f"  - 配置: {config.name}")
    
    # 显示各状态数量
    status_counts = CollectedProduct.objects.filter(task=task).values('status').annotate(count=Count('status'))
    print(f"\n状态分布:")
    for item in status_counts:
        print(f"  - {item['status']}: {item['count']} 个")


def clear_mock_data(tenant_id: int = 1):
    """清除模拟数据"""
    print("正在清除模拟数据...")
    
    # 删除模拟任务相关的商品
    tasks = CollectionTask.objects.filter(name='模拟采集任务', tenant_id=tenant_id)
    deleted_products = 0
    deleted_tasks = 0
    
    for task in tasks:
        count = CollectedProduct.objects.filter(task=task).delete()[0]
        deleted_products += count
        task.delete()
        deleted_tasks += 1
    
    print(f"✅ 已清除 {deleted_tasks} 个任务和 {deleted_products} 个商品")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='生成或清除采集商品模拟数据')
    parser.add_argument('--tenant', type=int, default=1, help='租户ID (默认: 1)')
    parser.add_argument('--user', type=int, default=1, help='用户ID (默认: 1)')
    parser.add_argument('--count', type=int, default=50, help='生成数量 (默认: 50)')
    parser.add_argument('--clear', action='store_true', help='清除模拟数据')
    
    args = parser.parse_args()
    
    if args.clear:
        clear_mock_data(args.tenant)
    else:
        generate_mock_data(args.tenant, args.user, args.count)