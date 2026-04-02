"""
数据填充脚本 - 生成测试数据
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

from apps.tenants.models import Tenant
from apps.users.models import User
from apps.platforms.models import Platform, Shop
from apps.products.models import ProductCategory, Product, ProductSKU
from apps.orders.models import Order, OrderItem
from apps.collections.models import CollectionTask, CollectionRecord
from apps.inventory.models import Warehouse, Inventory
from apps.suppliers.models import Supplier


def create_tenant():
    """创建租户"""
    tenant, created = Tenant.objects.get_or_create(
        code='demo',
        defaults={
            'name': '演示租户',
            'plan': 'professional',
            'contact_name': '管理员',
            'contact_email': 'admin@example.com'
        }
    )
    return tenant


def create_user(tenant):
    """创建用户"""
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'tenant': tenant,
            'email': 'admin@example.com',
            'real_name': '系统管理员',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
    return user


def create_platforms():
    """创建电商平台"""
    platforms_data = [
        {'name': 'TikTok Shop', 'code': 'tiktok', 'website': 'https://seller.tiktok.com'},
        {'name': 'Amazon', 'code': 'amazon', 'website': 'https://sellercentral.amazon.com'},
        {'name': 'eBay', 'code': 'ebay', 'website': 'https://www.ebay.com'},
        {'name': 'Shopee', 'code': 'shopee', 'website': 'https://seller.shopee.com'},
        {'name': 'Lazada', 'code': 'lazada', 'website': 'https://sellercenter.lazada.com'},
    ]
    
    platforms = []
    for data in platforms_data:
        platform, _ = Platform.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        platforms.append(platform)
    return platforms


def create_shops(tenant, platforms, user):
    """创建店铺"""
    shops = []
    shop_names = [
        ('TikTok-US', 'tiktok'),
        ('TikTok-UK', 'tiktok'),
        ('Amazon-US', 'amazon'),
        ('eBay-Global', 'ebay'),
        ('Shopee-SG', 'shopee'),
    ]
    
    for name, platform_code in shop_names:
        platform = next((p for p in platforms if p.code == platform_code), None)
        if platform:
            shop, _ = Shop.objects.get_or_create(
                tenant=tenant,
                name=name,
                defaults={
                    'platform': platform,
                    'shop_code': name.lower().replace('-', '_'),
                    'status': 1,
                    'creator': user
                }
            )
            shops.append(shop)
    return shops


def create_categories(tenant):
    """创建商品分类"""
    categories_data = [
        {'name': '电子产品', 'code': 'electronics', 'children': [
            {'name': '手机配件', 'code': 'phone-accessories'},
            {'name': '电脑配件', 'code': 'computer-accessories'},
            {'name': '智能穿戴', 'code': 'wearables'},
        ]},
        {'name': '服装配饰', 'code': 'clothing', 'children': [
            {'name': '女装', 'code': 'women-clothing'},
            {'name': '男装', 'code': 'men-clothing'},
            {'name': '配饰', 'code': 'accessories'},
        ]},
        {'name': '家居用品', 'code': 'home', 'children': [
            {'name': '厨房用品', 'code': 'kitchen'},
            {'name': '收纳整理', 'code': 'storage'},
            {'name': '装饰摆件', 'code': 'decor'},
        ]},
    ]
    
    categories = []
    for parent_data in categories_data:
        parent, _ = ProductCategory.objects.get_or_create(
            tenant=tenant,
            code=parent_data['code'],
            defaults={
                'name': parent_data['name'],
                'level': 1
            }
        )
        categories.append(parent)
        
        for child_data in parent_data['children']:
            child, _ = ProductCategory.objects.get_or_create(
                tenant=tenant,
                code=child_data['code'],
                defaults={
                    'name': child_data['name'],
                    'parent': parent,
                    'level': 2
                }
            )
            categories.append(child)
    
    return categories


def create_products(tenant, categories, user):
    """创建商品"""
    products_data = [
        {'name': 'iPhone 15 Pro Max 手机壳', 'category_code': 'phone-accessories', 'price': 25},
        {'name': 'AirPods Pro 保护套', 'category_code': 'phone-accessories', 'price': 15},
        {'name': '无线蓝牙鼠标', 'category_code': 'computer-accessories', 'price': 35},
        {'name': '机械键盘键帽套装', 'category_code': 'computer-accessories', 'price': 45},
        {'name': '智能运动手环', 'category_code': 'wearables', 'price': 89},
        {'name': '蓝牙耳机', 'category_code': 'wearables', 'price': 59},
        {'name': '夏季印花连衣裙', 'category_code': 'women-clothing', 'price': 39},
        {'name': '纯棉T恤', 'category_code': 'men-clothing', 'price': 19},
        {'name': '时尚太阳镜', 'category_code': 'accessories', 'price': 29},
        {'name': '不锈钢保温杯', 'category_code': 'kitchen', 'price': 22},
        {'name': '收纳盒套装', 'category_code': 'storage', 'price': 18},
        {'name': '北欧风装饰画', 'category_code': 'decor', 'price': 35},
    ]
    
    products = []
    for i, data in enumerate(products_data):
        category = next((c for c in categories if c.code == data['category_code']), None)
        
        spu_code = f"SPU{datetime.now().strftime('%Y%m%d%H%M%S')}{i:04d}"
        
        product, created = Product.objects.get_or_create(
            tenant=tenant,
            spu_code=spu_code,
            defaults={
                'category': category,
                'name': data['name'],
                'name_en': data['name'],
                'main_image': f'https://example.com/images/{spu_code}.jpg',
                'images': [f'https://example.com/images/{spu_code}_{j}.jpg' for j in range(1, 4)],
                'status': 1,
                'source_type': 'manual',
                'creator': user
            }
        )
        
        if created:
            # 创建SKU
            colors = ['黑色', '白色', '红色', '蓝色']
            sizes = ['S', 'M', 'L', 'XL']
            
            for color in colors[:2]:
                sku_code = f"{spu_code}-{color}"
                ProductSKU.objects.get_or_create(
                    tenant=tenant,
                    sku_code=sku_code,
                    defaults={
                        'product': product,
                        'spec_info': {'颜色': color},
                        'purchase_price': Decimal(str(data['price'] * 0.4)),
                        'cost_price': Decimal(str(data['price'] * 0.5)),
                        'sale_price': Decimal(str(data['price'])),
                        'market_price': Decimal(str(data['price'] * 1.2)),
                        'status': 1
                    }
                )
        
        products.append(product)
    
    return products


def create_warehouses(tenant):
    """创建仓库"""
    warehouses_data = [
        {'name': '深圳仓库', 'code': 'SZ01', 'type': 'self', 'city': '深圳'},
        {'name': '义乌仓库', 'code': 'YW01', 'type': 'self', 'city': '义乌'},
        {'name': '美国海外仓', 'code': 'US01', 'type': 'third', 'city': 'Los Angeles'},
    ]
    
    warehouses = []
    for data in warehouses_data:
        wh, _ = Warehouse.objects.get_or_create(
            tenant=tenant,
            code=data['code'],
            defaults={
                'name': data['name'],
                'type': data['type'],
                'country': '中国' if data['type'] == 'self' else 'USA',
                'city': data['city'],
                'status': True
            }
        )
        warehouses.append(wh)
    return warehouses


def create_inventory(tenant, warehouses, products):
    """创建库存"""
    for product in products:
        for sku in product.skus.all():
            for warehouse in warehouses[:2]:  # 只在前两个仓库创建库存
                Inventory.objects.get_or_create(
                    tenant=tenant,
                    warehouse=warehouse,
                    sku=sku,
                    defaults={
                        'quantity': random.randint(50, 500),
                        'locked_quantity': random.randint(0, 20),
                        'warning_threshold': random.randint(10, 50)
                    }
                )


def create_orders(tenant, shops, products, user):
    """创建订单"""
    countries = ['USA', 'UK', 'Germany', 'France', 'Australia', 'Canada', 'Japan']
    statuses = [0, 1, 2, 3, 4]
    status_weights = [5, 20, 30, 25, 20]  # 状态权重
    
    orders = []
    
    # 生成100个订单，分布在30天内
    for i in range(100):
        # 随机日期（最近30天）
        days_ago = random.randint(0, 30)
        created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        shop = random.choice(shops)
        country = random.choice(countries)
        
        # 生成订单号
        order_no = f"ORD{created_at.strftime('%Y%m%d%H%M%S')}{i:04d}"
        
        # 根据日期确定状态（越近的订单状态越靠前）
        if days_ago < 2:
            status = random.choices([0, 1], weights=[30, 70])[0]
        elif days_ago < 7:
            status = random.choices([1, 2], weights=[40, 60])[0]
        else:
            status = random.choices([2, 3, 4], weights=[20, 30, 50])[0]
        
        # 创建订单
        order = Order.objects.create(
            tenant=tenant,
            shop=shop,
            order_no=order_no,
            platform_order_no=f"PF{random.randint(100000000, 999999999)}",
            status=status,
            buyer_name=f"Customer{random.randint(1000, 9999)}",
            buyer_phone=f"+1{random.randint(1000000000, 9999999999)}",
            buyer_email=f"customer{random.randint(1000, 9999)}@example.com",
            receiver_name=f"Receiver{random.randint(1000, 9999)}",
            receiver_phone=f"+1{random.randint(1000000000, 9999999999)}",
            receiver_country=country,
            receiver_city=f"City{random.randint(1, 100)}",
            receiver_address=f"Street {random.randint(1, 999)}, Apt {random.randint(1, 99)}",
            receiver_zip=f"{random.randint(10000, 99999)}",
            product_amount=0,
            shipping_fee=Decimal(str(random.choice([5, 8, 10, 12, 15]))),
            tax_amount=0,
            discount_amount=Decimal(str(random.choice([0, 0, 5, 10]))),
            currency='USD',
            created_at=created_at
        )
        
        # 创建订单商品
        num_items = random.randint(1, 3)
        product_amount = Decimal('0')
        
        for _ in range(num_items):
            product = random.choice(products)
            sku = random.choice(list(product.skus.all())) if product.skus.exists() else None
            
            quantity = random.randint(1, 3)
            unit_price = sku.sale_price if sku else Decimal(str(random.randint(10, 100)))
            
            OrderItem.objects.create(
                tenant=tenant,
                order=order,
                product=product,
                sku=sku,
                product_name=product.name,
                sku_code=sku.sku_code if sku else '',
                sku_spec=sku.spec_info if sku else {},
                quantity=quantity,
                unit_price=unit_price,
                total_price=quantity * unit_price
            )
            
            product_amount += quantity * unit_price
        
        # 更新订单金额
        order.product_amount = product_amount
        order.tax_amount = product_amount * Decimal('0.08')  # 8%税
        order.save()
        
        # 根据状态设置时间
        if status >= 1:
            order.paid_at = created_at + timedelta(hours=random.randint(1, 24))
        if status >= 2:
            order.shipped_at = order.paid_at + timedelta(hours=random.randint(12, 72))
            order.logistics_company = random.choice(['DHL', 'UPS', 'FedEx'])
            order.tracking_no = f"TRK{random.randint(1000000000, 9999999999)}"
        if status >= 3:
            order.delivered_at = order.shipped_at + timedelta(days=random.randint(3, 10))
        if status >= 4:
            pass  # 已完成
        
        order.save()
        orders.append(order)
    
    return orders


def create_collection_records(tenant, user):
    """创建采集记录"""
    platforms = ['1688', 'taobao', 'tmall']
    
    sample_titles = [
        '新款时尚手机壳 防摔保护套',
        '无线蓝牙耳机 降噪运动款',
        '智能手表 多功能运动手环',
        '便携充电宝 20000毫安大容量',
        'USB-C数据线 快充充电线',
        '蓝牙音箱 迷你便携音响',
        '平板电脑支架 铝合金桌面支架',
        '机械键盘 青轴游戏键盘',
        '无线鼠标 静音办公鼠标',
        'Type-C扩展坞 USB分线器',
    ]
    
    for i in range(50):
        platform = random.choice(platforms)
        days_ago = random.randint(0, 30)
        created_at = timezone.now() - timedelta(days=days_ago)
        
        title = random.choice(sample_titles)
        price = Decimal(str(random.randint(10, 200)))
        
        CollectionRecord.objects.create(
            tenant=tenant,
            task=None,
            source_url=f'https://{platform}.com/item/{random.randint(100000000, 999999999)}',
            source_platform=platform,
            source_product_id=str(random.randint(100000000, 999999999)),
            title=f'{title} 款式{i+1}',
            price=price,
            original_price=price * Decimal('1.2'),
            currency='CNY',
            main_image=f'https://example.com/images/collection_{i}.jpg',
            images=[f'https://example.com/images/collection_{i}_{j}.jpg' for j in range(1, 4)],
            description=f'优质{title}，厂家直销，品质保证',
            attributes={'材质': '塑料', '颜色': '多色可选'},
            shop_name=f'{platform}店铺{random.randint(100, 999)}',
            sales_count=random.randint(100, 10000),
            rating=Decimal(str(random.uniform(4.0, 5.0))),
            rating_count=random.randint(50, 1000),
            status=random.choice([0, 0, 0, 2]),  # 大部分待处理
            created_at=created_at
        )


def create_suppliers(tenant):
    """创建供应商"""
    suppliers_data = [
        {'name': '深圳市华强电子有限公司', 'type': 'factory'},
        {'name': '义乌小商品批发市场', 'type': 'wholesale'},
        {'name': '广州服装厂', 'type': 'factory'},
        {'name': '东莞数码科技有限公司', 'type': 'factory'},
        {'name': '杭州家居用品厂', 'type': 'factory'},
    ]
    
    for i, data in enumerate(suppliers_data):
        Supplier.objects.get_or_create(
            tenant=tenant,
            code=f'SUP{i+1:03d}',
            defaults={
                'name': data['name'],
                'type': data['type'],
                'contact_name': f'联系人{i+1}',
                'contact_phone': f'138{random.randint(10000000, 99999999)}',
                'status': 1
            }
        )


def main():
    """主函数"""
    print("开始生成测试数据...")
    
    # 创建基础数据
    tenant = create_tenant()
    print(f"✓ 租户: {tenant.name}")
    
    user = create_user(tenant)
    print(f"✓ 用户: {user.username}")
    
    platforms = create_platforms()
    print(f"✓ 平台: {len(platforms)}个")
    
    shops = create_shops(tenant, platforms, user)
    print(f"✓ 店铺: {len(shops)}个")
    
    categories = create_categories(tenant)
    print(f"✓ 分类: {len(categories)}个")
    
    products = create_products(tenant, categories, user)
    print(f"✓ 商品: {len(products)}个")
    
    warehouses = create_warehouses(tenant)
    print(f"✓ 仓库: {len(warehouses)}个")
    
    create_inventory(tenant, warehouses, products)
    print(f"✓ 库存已创建")
    
    orders = create_orders(tenant, shops, products, user)
    print(f"✓ 订单: {len(orders)}个")
    
    create_collection_records(tenant, user)
    print(f"✓ 采集记录: 50条")
    
    create_suppliers(tenant)
    print(f"✓ 供应商已创建")
    
    print("\n数据生成完成！")
    print(f"登录账号: admin / admin123")


if __name__ == '__main__':
    main()
