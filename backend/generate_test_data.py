"""
拓岳 ERP - 测试数据生成脚本
生成符合跨境电商逻辑的模拟数据
"""

import os
import sys
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/home/zmx/.openclaw/workspace/tuoyue-erp/backend')

import django
django.setup()

from django.utils import timezone
from apps.tenants.models import Tenant
from apps.users.models import User
from apps.platforms.models import Platform
from apps.shops.models import Shop
from apps.products.models import Product, ProductSKU
from apps.collections.models import CollectionTask, CollectedProduct
from apps.inventory.models import Inventory, Warehouse
from apps.orders.models import Order, OrderItem
from apps.finance.models import DailyStats


class DataGenerator:
    """测试数据生成器"""
    
    # 商品标题模板
    PRODUCT_TITLES = [
        "2024新款时尚休闲运动鞋",
        "韩版潮流百搭单肩包",
        "智能蓝牙无线耳机",
        "多功能便携式充电宝",
        "高清防水运动相机",
        "创意家居收纳盒套装",
        "简约现代台灯护眼灯",
        "不锈钢保温杯大容量",
        "亲肤柔软床上四件套",
        "迷你便携风扇USB充电",
        "车载手机支架导航架",
        "厨房多功能切菜神器",
        "宠物自动喂食器智能",
        "瑜伽垫防滑加厚健身",
        "儿童益智拼图玩具",
    ]
    
    # 品牌列表
    BRANDS = ["小米", "华为", "苹果", "索尼", "三星", "飞利浦", "美的", "海尔", "无品牌"]
    
    # 类目
    CATEGORIES = [
        ("5001", "数码电器"),
        ("5002", "服装鞋包"),
        ("5003", "家居日用"),
        ("5004", "美妆个护"),
        ("5005", "母婴玩具"),
        ("5006", "运动户外"),
        ("5007", "食品饮料"),
    ]
    
    # SKU 属性
    SKU_ATTRIBUTES = [
        {"name": "颜色", "values": ["红色", "蓝色", "黑色", "白色", "粉色"]},
        {"name": "尺寸", "values": ["S", "M", "L", "XL", "XXL"]},
        {"name": "规格", "values": ["标准版", "升级版", "豪华版"]},
    ]
    
    # 国家/地区
    COUNTRIES = [
        ("SG", "新加坡", "Singapore"),
        ("MY", "马来西亚", "Malaysia"),
        ("TH", "泰国", "Thailand"),
        ("ID", "印尼", "Indonesia"),
        ("PH", "菲律宾", "Philippines"),
        ("VN", "越南", "Vietnam"),
    ]
    
    def __init__(self, tenant_id: int = 1):
        self.tenant = Tenant.objects.get(id=tenant_id)
        self.user = User.objects.filter(tenant=self.tenant).first()
        self.platforms = list(Platform.objects.all())
        self.shops = []
        self.products = []
        
    def generate_all(self):
        """生成所有测试数据"""
        print("=" * 60)
        print("开始生成拓岳 ERP 测试数据")
        print("=" * 60)
        
        self.generate_shops()
        self.generate_products()
        self.generate_inventory()
        self.generate_collected_products(50)
        self.generate_orders(200)
        self.generate_daily_stats()
        
        print("\n" + "=" * 60)
        print("测试数据生成完成！")
        print("=" * 60)
    
    def generate_shops(self):
        """生成店铺数据"""
        print("\n[1/6] 生成店铺数据...")
        
        shop_data = [
            ("TikTok Shop", "tiktok", "SG", "TikTok-SG-Store"),
            ("TikTok Shop", "tiktok", "MY", "TikTok-MY-Store"),
            ("Shopee", "shopee", "SG", "Shopee-SG-Official"),
            ("Shopee", "shopee", "MY", "Shopee-MY-Flagship"),
            ("Lazada", "lazada", "SG", "Lazada-SG-Mall"),
        ]
        
        for name, platform_code, site, shop_name in shop_data:
            platform = Platform.objects.get(code=platform_code)
            shop, created = Shop.objects.get_or_create(
                tenant=self.tenant,
                platform=platform,
                site_code=site,
                defaults={
                    'shop_name': shop_name,
                    'shop_code': f"{platform_code.upper()}-{site}-{random.randint(1000, 9999)}",
                    'platform_shop_id': str(random.randint(10000000, 99999999)),
                    'auth_status': 'authorized',
                    'sync_status': 'completed',
                    'last_sync_at': timezone.now(),
                }
            )
            if created:
                self.shops.append(shop)
                print(f"  ✓ 创建店铺: {shop_name} ({site})")
        
        if not self.shops:
            self.shops = list(Shop.objects.filter(tenant=self.tenant))
        
        print(f"  总计: {len(self.shops)} 个店铺")
    
    def generate_products(self):
        """生成商品数据"""
        print("\n[2/6] 生成商品数据...")
        
        for i in range(30):
            title = random.choice(self.PRODUCT_TITLES)
            category = random.choice(self.CATEGORIES)
            
            product, created = Product.objects.get_or_create(
                tenant=self.tenant,
                spu_code=f"SPU{random.randint(100000, 999999)}",
                defaults={
                    'name': f"{title}-{i+1}",
                    'name_en': f"Product {title}-{i+1}",
                    'description': f"这是商品 {title} 的详细描述，包含产品特点和规格参数。",
                    'category_id': category[0],
                    'category_path': category[1],
                    'brand': random.choice(self.BRANDS),
                    'main_image': f"https://picsum.photos/400/400?random={i}",
                    'images': [f"https://picsum.photos/400/400?random={i+j}" for j in range(5)],
                    'weight': round(random.uniform(0.1, 2.0), 2),
                    'length': round(random.uniform(10, 50), 1),
                    'width': round(random.uniform(10, 50), 1),
                    'height': round(random.uniform(5, 30), 1),
                    'status': 'active',
                    'created_by': self.user,
                }
            )
            
            if created:
                self.products.append(product)
                # 生成 SKU
                self._generate_skus(product)
        
        if not self.products:
            self.products = list(Product.objects.filter(tenant=self.tenant))
        
        print(f"  ✓ 创建 {len(self.products)} 个商品")
        sku_count = ProductSKU.objects.filter(tenant=self.tenant).count()
        print(f"  ✓ 创建 {sku_count} 个 SKU")
    
    def _generate_skus(self, product):
        """为商品生成 SKU"""
        # 随机选择1-2个属性
        attrs = random.sample(self.SKU_ATTRIBUTES, random.randint(1, 2))
        
        # 生成 SKU 组合
        if len(attrs) == 1:
            combinations = [[v] for v in attrs[0]['values'][:3]]
        else:
            combinations = []
            for v1 in attrs[0]['values'][:3]:
                for v2 in attrs[1]['values'][:2]:
                    combinations.append([v1, v2])
        
        for i, combo in enumerate(combinations[:6]):  # 最多6个SKU
            attr_dict = {attrs[j]['name']: combo[j] for j in range(len(combo))}
            attr_str = '-'.join(combo)
            
            ProductSKU.objects.create(
                tenant=self.tenant,
                product=product,
                sku_code=f"{product.spu_code}-{i+1:02d}",
                barcode=f"69{random.randint(100000000000, 999999999999)}",
                attributes=attr_dict,
                image=f"https://picsum.photos/200/200?random={product.id*10+i}",
                cost_price=Decimal(str(round(random.uniform(10, 100), 2))),
                sale_price=Decimal(str(round(random.uniform(20, 200), 2))),
                market_price=Decimal(str(round(random.uniform(30, 300), 2))),
                weight=product.weight,
            )
    
    def generate_inventory(self):
        """生成库存数据"""
        print("\n[3/6] 生成库存数据...")
        
        # 创建仓库
        warehouses, _ = Warehouse.objects.get_or_create(
            tenant=self.tenant,
            code='MAIN',
            defaults={
                'name': '主仓库',
                'type': 'self',
                'address': '深圳市宝安区物流中心',
            }
        )
        
        skus = ProductSKU.objects.filter(tenant=self.tenant)
        count = 0
        
        for sku in skus:
            available = random.randint(0, 500)
            sold_daily = round(random.uniform(0, 20), 2)
            
            Inventory.objects.get_or_create(
                tenant=self.tenant,
                sku=sku,
                warehouse=warehouses,
                defaults={
                    'available_qty': available,
                    'locked_qty': random.randint(0, min(50, available)),
                    'in_transit_qty': random.randint(0, 200),
                    'safety_stock': random.randint(20, 100),
                    'avg_daily_sales': sold_daily,
                }
            )
            count += 1
        
        print(f"  ✓ 创建 {count} 条库存记录")
    
    def generate_collected_products(self, count: int = 50):
        """生成采集商品数据"""
        print(f"\n[4/6] 生成 {count} 条采集记录...")
        
        platforms_map = {'1688': '1688', 'shopee': 'shopee'}
        
        for i in range(count):
            platform_code = random.choice(list(platforms_map.keys()))
            platform = Platform.objects.get(code=platform_code)
            
            title = random.choice(self.PRODUCT_TITLES)
            price = round(random.uniform(5, 100), 2)
            
            # 生成SKU属性
            sku_attrs = [
                {"name": "颜色", "values": random.sample(["红", "蓝", "黑", "白"], 3)},
                {"name": "尺码", "values": random.sample(["S", "M", "L", "XL"], 3)},
            ]
            
            skus = []
            for j in range(random.randint(3, 6)):
                skus.append({
                    'sku_id': f"SKU{random.randint(10000, 99999)}",
                    'name': f"规格{j+1}",
                    'price': round(price * random.uniform(0.8, 1.2), 2),
                    'stock': random.randint(10, 500),
                })
            
            # 随机状态
            status = random.choices(
                ['pending', 'claimed', 'published', 'ignored'],
                weights=[50, 20, 20, 10]
            )[0]
            
            claimed_by = None
            claimed_at = None
            if status in ['claimed', 'published']:
                claimed_by = self.user
                claimed_at = timezone.now() - timedelta(days=random.randint(1, 10))
            
            CollectedProduct.objects.create(
                tenant=self.tenant,
                platform=platform,
                source_url=f"https://detail.{platform_code}.com/item/{random.randint(100000000, 999999999)}",
                source_platform=platform_code,
                source_id=str(random.randint(100000000, 999999999)),
                title=f"[采集] {title} - {i+1}",
                main_image=f"https://picsum.photos/400/400?random={1000+i}",
                images=[f"https://picsum.photos/400/400?random={1000+i+j}" for j in range(5)],
                description=f"采集商品描述 {i+1}",
                original_price=round(price * 1.2, 2),
                price=price,
                currency='CNY',
                sku_attributes=sku_attrs,
                skus=skus,
                category_id=str(random.randint(1000, 9999)),
                category_name=random.choice(self.CATEGORIES)[1],
                brand=random.choice(self.BRANDS),
                weight=round(random.uniform(0.1, 2.0), 2),
                status=status,
                claimed_by=claimed_by,
                claimed_at=claimed_at,
            )
        
        print(f"  ✓ 创建 {count} 条采集记录")
    
    def generate_orders(self, count: int = 200):
        """生成订单数据"""
        print(f"\n[5/6] 生成 {count} 条订单...")
        
        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        status_weights = [15, 25, 30, 25, 5]
        
        skus = list(ProductSKU.objects.filter(tenant=self.tenant))
        
        for i in range(count):
            shop = random.choice(self.shops)
            country = random.choice(self.COUNTRIES)
            
            # 订单时间（过去30天）
            days_ago = random.randint(0, 30)
            order_time = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # 状态
            status = random.choices(statuses, weights=status_weights)[[0]]
            
            # 时间线
            pay_time = None
            ship_time = None
            if status in ['processing', 'shipped', 'delivered']:
                pay_time = order_time + timedelta(minutes=random.randint(5, 60))
            if status in ['shipped', 'delivered']:
                ship_time = pay_time + timedelta(hours=random.randint(1, 48))
            
            # 金额
            product_amount = Decimal(str(round(random.uniform(20, 500), 2)))
            shipping_fee = Decimal(str(round(random.uniform(5, 30), 2)))
            tax = round(product_amount * Decimal('0.08'), 2)
            discount = Decimal(str(round(random.uniform(0, 20), 2)))
            total = product_amount + shipping_fee + tax - discount
            
            # 成本与利润
            cost = product_amount * Decimal('0.6')
            profit = total - cost - shipping_fee
            profit_rate = round((profit / total * 100) if total > 0 else 0, 2)
            
            # 物流
            logistics = random.choice(['J&T Express', 'Ninja Van', 'Shopee Xpress', 'Lazada Logistics'])
            tracking = f"{random.choice(['JT', 'NV', 'SP', 'LZ'])}{random.randint(1000000000, 9999999999)}"
            
            order = Order.objects.create(
                tenant=self.tenant,
                shop=shop,
                platform=shop.platform,
                platform_order_id=str(random.randint(100000000000, 999999999999)),
                order_code=f"TY{timezone.now().strftime('%Y%m%d')}{random.randint(10000, 99999)}",
                status=status,
                order_time=order_time,
                pay_time=pay_time,
                ship_time=ship_time,
                currency=shop.site_code if shop.site_code != 'SG' else 'SGD',
                total_amount=total,
                product_amount=product_amount,
                shipping_fee=shipping_fee,
                tax_amount=tax,
                discount_amount=discount,
                profit=profit,
                profit_rate=profit_rate,
                buyer_name=f"Customer{random.randint(1000, 9999)}",
                buyer_email=f"customer{random.randint(1000, 9999)}@email.com",
                buyer_phone=f"+65{random.randint(80000000, 99999999)}",
                receiver_name=f"Receiver{random.randint(1000, 9999)}",
                receiver_phone=f"+65{random.randint(80000000, 99999999)}",
                receiver_country=country[2],
                receiver_state=random.choice(['Central', 'North', 'South', 'East', 'West']),
                receiver_city=random.choice(['Singapore', 'Kuala Lumpur', 'Bangkok', 'Jakarta']),
                receiver_address=f"{random.randint(1, 999)} {random.choice(['Street', 'Road', 'Avenue', 'Lane'])} {random.randint(1, 99)}",
                receiver_zip=str(random.randint(100000, 999999)),
                logistics_company=logistics if status in ['shipped', 'delivered'] else None,
                tracking_no=tracking if status in ['shipped', 'delivered'] else None,
                synced_at=order_time,
            )
            
            # 生成订单明细
            self._generate_order_items(order, skus)
        
        print(f"  ✓ 创建 {count} 条订单")
    
    def _generate_order_items(self, order, skus):
        """生成订单明细"""
        item_count = random.randint(1, 3)
        selected_skus = random.sample(skus, min(item_count, len(skus)))
        
        for sku in selected_skus:
            qty = random.randint(1, 3)
            price = sku.sale_price
            total = price * qty
            cost = sku.cost_price * qty
            
            OrderItem.objects.create(
                order=order,
                product=sku.product,
                sku=sku,
                platform_item_id=str(random.randint(100000000, 999999999)),
                product_name=sku.product.name,
                sku_name=str(sku.attributes),
                image=sku.image,
                qty=qty,
                price=price,
                total_amount=total,
                cost_price=sku.cost_price,
                profit=total - cost,
            )
    
    def generate_daily_stats(self):
        """生成每日统计数据"""
        print("\n[6/6] 生成每日统计数据...")
        
        # 过去30天
        for days_ago in range(30, -1, -1):
            date = (timezone.now() - timedelta(days=days_ago)).date()
            
            # 整体统计
            order_count = random.randint(20, 100)
            valid_rate = random.uniform(0.85, 0.95)
            valid_count = int(order_count * valid_rate)
            
            avg_order_value = Decimal(str(round(random.uniform(30, 150), 2)))
            total_amount = avg_order_value * valid_count
            
            profit_rate = Decimal(str(round(random.uniform(15, 35), 2)))
            profit = total_amount * profit_rate / 100
            
            DailyStats.objects.get_or_create(
                tenant=self.tenant,
                shop=None,
                stat_date=date,
                defaults={
                    'order_count': order_count,
                    'valid_order_count': valid_count,
                    'total_amount': total_amount,
                    'product_amount': total_amount * Decimal('0.85'),
                    'shipping_fee': total_amount * Decimal('0.1'),
                    'total_cost': total_amount - profit,
                    'profit': profit,
                    'profit_rate': profit_rate,
                }
            )
            
            # 各店铺统计
            for shop in self.shops:
                shop_orders = random.randint(5, 30)
                shop_valid = int(shop_orders * valid_rate)
                shop_amount = avg_order_value * shop_valid
                shop_profit = shop_amount * profit_rate / 100
                
                DailyStats.objects.get_or_create(
                    tenant=self.tenant,
                    shop=shop,
                    stat_date=date,
                    defaults={
                        'order_count': shop_orders,
                        'valid_order_count': shop_valid,
                        'total_amount': shop_amount,
                        'product_amount': shop_amount * Decimal('0.85'),
                        'shipping_fee': shop_amount * Decimal('0.1'),
                        'total_cost': shop_amount - shop_profit,
                        'profit': shop_profit,
                        'profit_rate': profit_rate,
                    }
                )
        
        print(f"  ✓ 创建 31 天统计数据（含整体+各店铺）")


if __name__ == '__main__':
    # 确保有租户
    tenant, _ = Tenant.objects.get_or_create(
        id=1,
        defaults={
            'name': '拓岳科技',
            'code': 'tuoyue',
            'status': 1,
        }
    )
    
    # 确保有用户
    user, _ = User.objects.get_or_create(
        tenant=tenant,
        username='admin',
        defaults={
            'email': 'admin@tuoyue.com',
            'role': 'admin',
            'status': 1,
        }
    )
    if not user.password:
        user.set_password('admin123')
        user.save()
    
    # 生成数据
    generator = DataGenerator(tenant_id=1)
    generator.generate_all()
