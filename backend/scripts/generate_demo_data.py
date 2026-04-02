"""
拓岳ERP - 数据生成脚本
生成符合跨境电商逻辑的测试数据
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_demo')
sys.path.insert(0, '/home/zmx/.openclaw/workspace/tuoyue-erp/backend')
django.setup()

import random
import string
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

from apps.tenants.models import Tenant
from apps.users.models import User, Role, UserRole
from apps.platforms.models import Platform, Shop
from apps.products.models import ProductCategory, Product, ProductSKU, ProductPlatformMapping
from apps.collections.models import CollectionTask, CollectionRecord
from apps.orders.models import Order, OrderItem, OrderShipment
from apps.inventory.models import Warehouse, Inventory, InventoryLog
from apps.suppliers.models import Supplier, PurchaseOrder, PurchaseOrderItem
from apps.finance.models import Transaction


def generate_code(prefix, length=8):
    """生成随机编码"""
    return prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_order_no():
    """生成订单号"""
    return 'ORD' + datetime.now().strftime('%Y%m%d') + ''.join(random.choices(string.digits, k=6))


def generate_task_no():
    """生成任务编号"""
    return 'TSK' + datetime.now().strftime('%Y%m%d') + ''.join(random.choices(string.digits, k=6))


def create_tenant_and_user():
    """创建租户和超级用户"""
    print("创建租户...")
    tenant, _ = Tenant.objects.get_or_create(
        code='tuoyue',
        defaults={
            'name': '拓岳跨境电商',
            'plan': 'premium',
            'contact_name': '管理员',
            'contact_email': 'admin@tuoyue.com'
        }
    )
    
    print("创建超级用户...")
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@tuoyue.com',
            tenant=tenant,
            real_name='系统管理员'
        )
        
        # 创建角色
        role, _ = Role.objects.get_or_create(
            tenant=tenant,
            code='super_admin',
            defaults={
                'name': '超级管理员',
                'permissions': ['*']
            }
        )
        UserRole.objects.get_or_create(user=user, role=role)
    else:
        user = User.objects.get(username='admin')
    
    return tenant, user


def create_platforms():
    """创建电商平台"""
    print("创建电商平台...")
    platforms_data = [
        {'name': 'TikTok Shop', 'code': 'tiktok', 'website': 'https://seller.tiktok.com'},
        {'name': 'Shopee', 'code': 'shopee', 'website': 'https://seller.shopee.cn'},
        {'name': 'Lazada', 'code': 'lazada', 'website': 'https://sellercenter.lazada.com'},
        {'name': 'Amazon', 'code': 'amazon', 'website': 'https://sellercentral.amazon.com'},
        {'name': 'eBay', 'code': 'ebay', 'website': 'https://www.ebay.com'},
        {'name': '1688', 'code': '1688', 'website': 'https://www.1688.com'},
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
    """创建店铺"""
    print("创建店铺...")
    shops_data = [
        {'name': 'TikTok-US店', 'platform_code': 'tiktok'},
        {'name': 'TikTok-UK店', 'platform_code': 'tiktok'},
        {'name': 'Shopee-新加坡', 'platform_code': 'shopee'},
        {'name': 'Shopee-马来西亚', 'platform_code': 'shopee'},
        {'name': 'Lazada-泰国', 'platform_code': 'lazada'},
        {'name': 'Amazon-US', 'platform_code': 'amazon'},
    ]
    
    shops = []
    platform_map = {p.code: p for p in platforms}
    
    for data in shops_data:
        platform = platform_map.get(data['platform_code'])
        if platform:
            shop, _ = Shop.objects.get_or_create(
                tenant=tenant,
                platform=platform,
                name=data['name'],
                defaults={
                    'shop_code': generate_code('SHP'),
                    'status': 1
                }
            )
            shops.append(shop)
    return shops


def create_categories(tenant):
    """创建商品分类"""
    print("创建商品分类...")
    categories_data = [
        {'name': '数码电子', 'code': 'digital'},
        {'name': '服装配饰', 'code': 'clothing'},
        {'name': '家居用品', 'code': 'home'},
        {'name': '美妆个护', 'code': 'beauty'},
        {'name': '运动户外', 'code': 'sports'},
    ]
    
    categories = []
    for data in categories_data:
        cat, _ = ProductCategory.objects.get_or_create(
            tenant=tenant,
            code=data['code'],
            defaults={'name': data['name']}
        )
        categories.append(cat)
    return categories


def create_products(tenant, categories, user):
    """创建商品和SKU"""
    print("创建商品...")
    
    products_data = [
        {
            'name': '无线蓝牙耳机 Pro',
            'category_idx': 0,
            'spu_code': 'EAR-001',
            'price': Decimal('89.99'),
            'specs': [{'颜色': '黑色', '尺寸': '标准'}, {'颜色': '白色', '尺寸': '标准'}]
        },
        {
            'name': '智能手表 Series 5',
            'category_idx': 0,
            'spu_code': 'WATCH-002',
            'price': Decimal('199.99'),
            'specs': [{'颜色': '黑色'}, {'颜色': '银色'}, {'颜色': '金色'}]
        },
        {
            'name': '夏季纯棉T恤',
            'category_idx': 1,
            'spu_code': 'TSHIRT-003',
            'price': Decimal('19.99'),
            'specs': [{'颜色': '白色', '尺寸': 'M'}, {'颜色': '白色', '尺寸': 'L'}, 
                     {'颜色': '黑色', '尺寸': 'M'}, {'颜色': '黑色', '尺寸': 'L'}]
        },
        {
            'name': 'LED台灯护眼灯',
            'category_idx': 2,
            'spu_code': 'LAMP-004',
            'price': Decimal('45.99'),
            'specs': [{'颜色': '白色'}, {'颜色': '黑色'}]
        },
        {
            'name': '面部精华液',
            'category_idx': 3,
            'spu_code': 'SERUM-005',
            'price': Decimal('35.99'),
            'specs': [{'容量': '30ml'}, {'容量': '50ml'}]
        },
    ]
    
    products = []
    for data in products_data:
        product, _ = Product.objects.get_or_create(
            tenant=tenant,
            spu_code=data['spu_code'],
            defaults={
                'category': categories[data['category_idx']],
                'name': data['name'],
                'name_en': data['name'],
                'brand': '拓岳优选',
                'main_image': f'https://via.placeholder.com/400x400?text={data["spu_code"]}',
                'status': 1,
                'creator': user
            }
        )
        
        # 创建SKU
        for i, spec in enumerate(data['specs']):
            sku_code = f"{data['spu_code']}-{i+1}"
            ProductSKU.objects.get_or_create(
                tenant=tenant,
                sku_code=sku_code,
                defaults={
                    'product': product,
                    'spec_info': spec,
                    'purchase_price': data['price'] * Decimal('0.4'),
                    'cost_price': data['price'] * Decimal('0.5'),
                    'sale_price': data['price'],
                    'market_price': data['price'] * Decimal('1.2'),
                    'status': 1
                }
            )
        
        products.append(product)
    
    return products


def create_collection_records(tenant, user):
    """创建采集记录 - 50条待认领记录"""
    print("创建采集记录 (50条)...")
    
    platforms = ['1688', 'taobao', 'tmall']
    statuses = [0, 1, 2]  # 待采集、采集中、成功
    
    # 创建采集任务
    task = CollectionTask.objects.create(
        tenant=tenant,
        task_no=generate_task_no(),
        name='批量采集任务-2024-01',
        source_platform='1688',
        source_urls=[],
        task_type='batch',
        status=2,  # 完成
        total_count=50,
        success_count=45,
        fail_count=5,
        creator=user
    )
    
    # 创建50条采集记录
    for i in range(50):
        platform = random.choice(platforms)
        status = random.choice(statuses)
        
        CollectionRecord.objects.create(
            tenant=tenant,
            task=task,
            source_url=f'https://{platform}.com/product/{i+1000}',
            source_platform=platform,
            source_product_id=f'PID-{i+1000}',
            title=f'采集商品示例-{i+1} ({platform})',
            main_image=f'https://via.placeholder.com/300x300?text=COL-{i+1}',
            price_range=f'¥{random.randint(10, 200)}-{random.randint(200, 500)}',
            status=status,
            collected_data={
                'title': f'采集商品示例-{i+1}',
                'price': random.randint(50, 300),
                'images': [f'https://via.placeholder.com/300x300?text=IMG-{j}' for j in range(5)],
                'attributes': {'材质': '棉', '产地': '中国'}
            }
        )
    
    print(f"已创建 50 条采集记录")


def create_orders(tenant, shops, user):
    """创建订单数据"""
    print("创建订单数据...")
    
    order_statuses = ['pending', 'paid', 'shipped', 'completed']
    platforms = ['tiktok', 'shopee', 'lazada']
    
    # 生成100个订单
    for i in range(100):
        shop = random.choice(shops)
        status = random.choice(order_statuses)
        platform = random.choice(platforms)
        
        # 订单金额
        product_amount = Decimal(random.randint(50, 500))
        shipping_fee = Decimal(random.randint(5, 20))
        discount = Decimal(random.randint(0, 20))
        total = product_amount + shipping_fee - discount
        
        order = Order.objects.create(
            tenant=tenant,
            order_no=generate_order_no(),
            platform_order_no=f'PF-{random.randint(10000000, 99999999)}',
            shop=shop,
            platform_id=shop.platform.id,
            status=status,
            currency='USD',
            total_amount=total,
            product_amount=product_amount,
            shipping_fee=shipping_fee,
            discount_amount=discount,
            paid_amount=total if status in ['paid', 'shipped', 'completed'] else Decimal('0'),
            buyer_name=f'Buyer_{i+1}',
            buyer_email=f'buyer{i+1}@example.com',
            receiver_name=f'Receiver_{i+1}',
            receiver_phone=f'+86{random.randint(10000000000, 19999999999)}',
            receiver_country=random.choice(['US', 'UK', 'SG', 'MY', 'TH']),
            receiver_address=f'{random.randint(1, 999)} Main St, City',
            paid_at=timezone.now() - timedelta(days=random.randint(0, 30)) if status in ['paid', 'shipped', 'completed'] else None,
            shipped_at=timezone.now() - timedelta(days=random.randint(0, 10)) if status in ['shipped', 'completed'] else None
        )
        
        # 创建订单商品
        OrderItem.objects.create(
            tenant=tenant,
            order=order,
            product_name=f'商品-{random.randint(1, 50)}',
            sku_name='标准规格',
            quantity=random.randint(1, 5),
            unit_price=product_amount / random.randint(1, 3),
            total_price=product_amount,
            cost_price=product_amount * Decimal('0.4')
        )
    
    print(f"已创建 100 个订单")


def create_inventory(tenant, products):
    """创建库存数据"""
    print("创建库存数据...")
    
    # 创建仓库
    warehouse, _ = Warehouse.objects.get_or_create(
        tenant=tenant,
        code='MAIN-01',
        defaults={
            'name': '主仓库',
            'type': 'self',
            'country': 'CN',
            'city': '深圳',
            'is_default': True
        }
    )
    
    # 为每个SKU创建库存
    skus = ProductSKU.objects.filter(tenant=tenant)
    for sku in skus:
        quantity = random.randint(0, 200)
        Inventory.objects.get_or_create(
            tenant=tenant,
            warehouse=warehouse,
            sku=sku,
            defaults={
                'quantity': quantity,
                'locked_quantity': random.randint(0, min(10, quantity)),
                'warning_threshold': 20
            }
        )
    
    print(f"已为 {skus.count()} 个SKU创建库存")


def create_suppliers_and_purchases(tenant, user):
    """创建供应商和采购单"""
    print("创建供应商...")
    
    suppliers_data = [
        {'name': '深圳数码科技有限公司', 'contact': '张经理'},
        {'name': '广州服装批发厂', 'contact': '李老板'},
        {'name': '义乌小商品供应商', 'contact': '王经理'},
    ]
    
    suppliers = []
    for data in suppliers_data:
        supplier, _ = Supplier.objects.get_or_create(
            tenant=tenant,
            name=data['name'],
            defaults={
                'code': generate_code('SUP'),
                'contact_person': data['contact'],
                'contact_phone': f'138{random.randint(10000000, 99999999)}',
                'status': 1
            }
        )
        suppliers.append(supplier)
    
    print("创建采购单...")
    warehouse = Warehouse.objects.filter(tenant=tenant).first()
    
    for i in range(20):
        po = PurchaseOrder.objects.create(
            tenant=tenant,
            po_no=generate_code('PO'),
            supplier=random.choice(suppliers),
            warehouse=warehouse,
            status=random.choice(['draft', 'pending', 'confirmed', 'received', 'completed']),
            total_amount=Decimal(random.randint(1000, 10000)),
            total_quantity=random.randint(50, 500),
            created_by=user
        )
    
    print(f"已创建 {len(suppliers)} 个供应商, 20 个采购单")


def create_dashboard_data(tenant):
    """创建数据大屏所需的30天销售数据"""
    print("创建数据大屏数据...")
    
    # 创建交易记录 - 过去30天
    for i in range(30):
        date = timezone.now() - timedelta(days=i)
        
        # 每天的交易数据
        for _ in range(random.randint(5, 20)):
            Transaction.objects.create(
                tenant=tenant,
                transaction_no=generate_code('TRX'),
                biz_type='order',
                type='income',
                amount=Decimal(random.randint(50, 500)),
                currency='USD',
                description='订单收入',
                status=1,
                created_at=date
            )
    
    print("已创建 30 天的交易数据")


def main():
    """主函数 - 生成所有测试数据"""
    print("=" * 60)
    print("拓岳ERP - 测试数据生成脚本")
    print("=" * 60)
    
    # 1. 基础数据
    tenant, user = create_tenant_and_user()
    platforms = create_platforms()
    shops = create_shops(tenant, platforms)
    categories = create_categories(tenant)
    
    # 2. 商品数据
    products = create_products(tenant, categories, user)
    
    # 3. 核心业务数据
    create_collection_records(tenant, user)
    create_orders(tenant, shops, user)
    create_inventory(tenant, products)
    create_suppliers_and_purchases(tenant, user)
    create_dashboard_data(tenant)
    
    print("=" * 60)
    print("测试数据生成完成!")
    print(f"租户: {tenant.name}")
    print(f"登录用户: admin / admin123")
    print("=" * 60)


if __name__ == '__main__':
    main()
