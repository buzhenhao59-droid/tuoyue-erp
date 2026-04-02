#!/usr/bin/env python3
"""
拓岳 ERP - 测试数据生成脚本
生成采集商品、订单、库存等测试数据
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
from faker import Faker

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
django.setup()

from django.utils import timezone
from apps.tenants.models import Tenant
from apps.users.models import User
from apps.products.models import Product, ProductSKU
from apps.collections.models import CollectionConfig, CollectionTask, CollectedProduct
from apps.orders.models import Order, OrderItem
from apps.inventory.models import Inventory, Warehouse
from apps.platforms.models import Platform, Shop

fake = Faker('zh_CN')


def create_tenant():
    """创建测试租户"""
    tenant, created = Tenant.objects.get_or_create(
        code='test',
        defaults={
            'name': '拓岳测试租户',
            'status': 1
        }
    )
    return tenant


def create_user(tenant):
    """创建测试用户"""
    user, created = User.objects.get_or_create(
        tenant=tenant,
        username='admin',
        defaults={
            'email': 'admin@tuoyue.com',
            'is_active': True,
            'is_staff': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
    return user


def create_platforms():
    """创建电商平台"""
    platforms_data = [
        {'code': 'tiktok', 'name': 'TikTok Shop', 'name_en': 'TikTok Shop'},
        {'code': 'shopee', 'name': 'Shopee', 'name_en': 'Shopee'},
        {'code': 'lazada', 'name': 'Lazada', 'name_en': 'Lazada'},
        {'code': '1688', 'name': '1688', 'name_en': '1688'},
    ]
    
    platforms = []
    for data in platforms_data:
        platform, _ = Platform.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        platforms.append(platform)
    return platforms


def create_shops(tenant, platforms):
    """创建测试店铺"""
    shops = []
    for platform in platforms[:3]:  # 只为前3个平台创建店铺
        shop, _ = Shop.objects.get_or_create(
            tenant=tenant,
            platform=platform,
            shop_name=f'{platform.name}旗舰店',
            defaults={
                'auth_status': 'authorized',
                'status': 1
            }
        )
        shops.append(shop)
    return shops


def create_collection_config(tenant):
    """创建采集配置"""
    config, _ = CollectionConfig.objects.get_or_create(
        tenant=tenant,
        name='默认配置',
        defaults={
            'price_rule': 'fixed',
            'price_multiplier': 1.5,
            'price_addition': 10,
            'auto_translate': False,
            'download_images': True,
            'is_default': True
        }
    )
    return config


def generate_collected_products(tenant, user, config, count=50):
    """生成采集商品数据"""
    platforms = ['1688', 'taobao', 'tmall', 'shopee']
    statuses = ['pending', 'claimed', 'editing', 'published', 'ignored']
    status_weights = [0.4, 0.2, 0.1, 0.2, 0.1]  # pending 占40%
    
    products = []
    for i in range(count):
        platform = random.choice(platforms)
        status = random.choices(statuses, weights=status_weights)[0]
        
        # 生成SKU
        sku_count = random.randint(1, 5)
        skus = []
        sku_attributes = []
        
        if random.random() > 0.3:  # 70% 有SKU
            colors = ['红色', '蓝色', '黑色', '白色']
            sizes = ['S', 'M', 'L', 'XL']
            
            sku_attributes = [
                {'name': '颜色', 'values': random.sample(colors, random.randint(2, 4))},
                {'name': '尺寸', 'values': random.sample(sizes, random.randint(2, 4))}
            ]
            
            for j in range(sku_count):
                skus.append({
                    'sku_id': f'SKU{fake.unique.random_number(digits=8)}',
                    'attributes': {
                        '颜色': random.choice(colors),
                        '尺寸': random.choice(sizes)
                    },
                    'price': round(random.uniform(10, 500), 2),
                    'stock': random.randint(10, 1000)
                })
        
        original_price = round(random.uniform(10, 500), 2)
        price = round(original_price * 1.5, 2)
        
        product = CollectedProduct.objects.create(
            tenant=tenant,
            config=config,
            source_url=f'https://detail.{platform}.com/offer/{fake.unique.random_number(digits=10)}.html',
            source_platform=platform,
            source_id=str(fake.unique.random_number(digits=10)),
            title=fake.catch_phrase() + ' ' + random.choice(['爆款', '热销', '新品', '特价']),
            description=fake.text(max_nb_chars=500),
            main_image=f'https://via.placeholder.com/400x400?text={platform}',
            images=[f'https://via.placeholder.com/400x400?text={platform}{i}' for i in range(5)],
            original_price_min=original_price,
            original_price_max=original_price,
            price_min=price,
            price_max=price,
            currency='CNY',
            sku_attributes=sku_attributes,
            skus=skus,
            sku_count=len(skus),
            status=status,
            weight=round(random.uniform(0.1, 5), 2),
            created_at=timezone.now() - timedelta(days=random.randint(0, 30))
        )
        products.append(product)
    
    print(f'✅ 生成 {len(products)} 个采集商品')
    return products


def generate_products(tenant, count=30):
    """生成商品数据"""
    products = []
    categories = ['电子产品', '服装配饰', '家居用品', '运动户外', '美妆护肤']
    
    for i in range(count):
        category = random.choice(categories)
        
        product = Product.objects.create(
            tenant=tenant,
            name=fake.catch_phrase() + ' ' + category,
            description=fake.text(max_nb_chars=1000),
            category_name=category,
            main_image=f'https://via.placeholder.com/400x400?text=Product{i}',
            weight=round(random.uniform(0.1, 5), 2),
            status=random.choice(['active', 'draft', 'active', 'active']),
            created_at=timezone.now() - timedelta(days=random.randint(1, 60))
        )
        
        # 生成 SKU
        sku_count = random.randint(1, 4)
        for j in range(sku_count):
            ProductSKU.objects.create(
                tenant=tenant,
                product=product,
                sku_code=f'SKU{fake.unique.random_number(digits=8)}',
                attributes={'颜色': random.choice(['红', '蓝', '黑']), '尺寸': random.choice(['S', 'M', 'L'])},
                cost_price=round(random.uniform(10, 200), 2),
                sale_price=round(random.uniform(20, 500), 2),
                status=1
            )
        
        products.append(product)
    
    print(f'✅ 生成 {len(products)} 个商品')
    return products


def generate_orders(tenant, shops, count=100):
    """生成订单数据"""
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    status_weights = [0.1, 0.2, 0.3, 0.35, 0.05]
    
    orders = []
    for i in range(count):
        shop = random.choice(shops)
        status = random.choices(statuses, weights=status_weights)[0]
        
        # 生成订单金额
        item_count = random.randint(1, 5)
        product_amount = round(random.uniform(50, 1000), 2)
        shipping_fee = round(random.uniform(5, 50), 2)
        total_amount = product_amount + shipping_fee
        
        order = Order.objects.create(
            tenant=tenant,
            shop=shop,
            platform=shop.platform,
            platform_order_id=f'ORD{fake.unique.random_number(digits=12)}',
            order_code=f'TY{fake.unique.random_number(digits=10)}',
            status=status,
            currency='USD',
            total_amount=total_amount,
            product_amount=product_amount,
            shipping_fee=shipping_fee,
            profit=round(total_amount * 0.25, 2),
            profit_rate=25,
            buyer_name=fake.name(),
            receiver_name=fake.name(),
            receiver_phone=fake.phone_number(),
            receiver_country=random.choice(['中国', '美国', '新加坡', '马来西亚']),
            receiver_address=fake.address(),
            order_time=timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
            created_at=timezone.now() - timedelta(days=random.randint(0, 30))
        )
        
        # 生成订单明细
        for j in range(item_count):
            OrderItem.objects.create(
                order=order,
                product_name=fake.catch_phrase(),
                sku_name=random.choice(['红色-L', '蓝色-M', '黑色-S']),
                qty=random.randint(1, 3),
                price=round(random.uniform(10, 200), 2),
                total_amount=round(random.uniform(20, 400), 2),
                cost_price=round(random.uniform(5, 100), 2)
            )
        
        orders.append(order)
    
    print(f'✅ 生成 {len(orders)} 个订单')
    return orders


def generate_inventory(tenant, products):
    """生成库存数据"""
    warehouse, _ = Warehouse.objects.get_or_create(
        tenant=tenant,
        name='默认仓库',
        defaults={'code': 'DEFAULT', 'type': 'self'}
    )
    
    inventories = []
    for product in products:
        for sku in ProductSKU.objects.filter(product=product):
            inventory, _ = Inventory.objects.get_or_create(
                tenant=tenant,
                sku=sku,
                warehouse=warehouse,
                defaults={
                    'available_qty': random.randint(0, 500),
                    'locked_qty': random.randint(0, 50),
                    'safety_stock': random.randint(10, 50)
                }
            )
            inventories.append(inventory)
    
    print(f'✅ 生成 {len(inventories)} 条库存记录')
    return inventories


def main():
    """主函数"""
    print('🚀 开始生成拓岳 ERP 测试数据...\n')
    
    # 创建基础数据
    tenant = create_tenant()
    user = create_user(tenant)
    platforms = create_platforms()
    shops = create_shops(tenant, platforms)
    config = create_collection_config(tenant)
    
    print(f'✅ 租户: {tenant.name}')
    print(f'✅ 用户: {user.username} (密码: admin123)')
    print(f'✅ 平台: {len(platforms)} 个')
    print(f'✅ 店铺: {len(shops)} 个\n')
    
    # 生成业务数据
    collected_products = generate_collected_products(tenant, user, config, count=50)
    products = generate_products(tenant, count=30)
    orders = generate_orders(tenant, shops, count=100)
    inventories = generate_inventory(tenant, products)
    
    print('\n✨ 测试数据生成完成！')
    print('=' * 50)
    print('登录信息:')
    print(f'  用户名: admin')
    print(f'  密码: admin123')
    print(f'  租户: {tenant.code}')
    print('=' * 50)


if __name__ == '__main__':
    main()