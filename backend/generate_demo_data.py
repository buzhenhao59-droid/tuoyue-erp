#!/usr/bin/env python3
"""
拓岳 ERP - 演示数据生成（适配新模型）
"""

import os
import sys
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/home/zmx/.openclaw/workspace/tuoyue-erp/backend')

import django
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.tenants.models import Tenant
from apps.users.models import User
from apps.platforms.models import Platform
from apps.collections.models import CollectionConfig, CollectedProduct


def generate_demo_data():
    """生成演示数据"""
    print("=" * 60)
    print("拓岳 ERP - 生成演示数据")
    print("=" * 60)
    
    # 1. 创建租户
    tenant, _ = Tenant.objects.get_or_create(
        id=1,
        defaults={
            'name': '拓岳科技',
            'code': 'tuoyue',
            'status': 1,
        }
    )
    print(f"\n✓ 租户: {tenant.name}")
    
    # 2. 创建管理员
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@tuoyue.com',
            'is_staff': True,
            'is_active': True,
            'tenant': tenant,
        }
    )
    if not created and not user.tenant_id:
        user.tenant = tenant
        user.save()
    if not user.password:
        user.set_password('admin123')
        user.save()
    
    print(f"✓ 管理员: admin / admin123")
    
    # 3. 确保平台数据
    platforms_data = [
        ('tiktok', 'TikTok Shop'),
        ('shopee', 'Shopee'),
        ('lazada', 'Lazada'),
        ('1688', '1688'),
    ]
    for code, name in platforms_data:
        Platform.objects.get_or_create(code=code, defaults={'name': name})
    print(f"✓ 平台: {len(platforms_data)} 个")
    
    # 4. 创建默认采集配置
    config, _ = CollectionConfig.objects.get_or_create(
        tenant=tenant,
        is_default=True,
        defaults={
            'name': '默认配置',
            'price_rule': 'fixed',
            'price_multiplier': 1.5,
            'price_addition': 0,
            'auto_translate': False,
            'download_images': True,
            'default_stock': 999,
        }
    )
    print(f"✓ 采集配置: {config.name}")
    
    # 5. 生成采集商品数据
    titles = [
        "2024新款时尚休闲运动鞋男女同款",
        "韩版潮流百搭单肩包斜挎包",
        "智能蓝牙无线耳机降噪版",
        "多功能便携式充电宝20000mAh",
        "高清防水运动相机4K",
        "创意家居收纳盒套装",
        "简约现代LED台灯护眼",
        "不锈钢保温杯大容量500ml",
        "亲肤柔软床上四件套",
        "迷你便携USB充电风扇",
        "车载手机支架导航架",
        "厨房多功能切菜神器",
        "宠物自动喂食器智能定时",
        "瑜伽垫防滑加厚健身垫",
        "儿童益智拼图玩具3-6岁",
        "无线鼠标静音办公游戏",
        "机械键盘青轴RGB背光",
        "便携折叠自行车16寸",
        "智能手环心率血压监测",
        "蓝牙音箱户外防水音响",
    ]
    
    platforms = ['1688', 'shopee']
    statuses = ['pending', 'pending', 'pending', 'claimed', 'published', 'ignored']
    
    # 清空旧数据
    CollectedProduct.objects.filter(tenant=tenant).delete()
    
    count = 50
    for i in range(count):
        platform_code = random.choice(platforms)
        platform = Platform.objects.get(code=platform_code)
        title = random.choice(titles)
        price = round(random.uniform(10, 200), 2)
        status = random.choice(statuses)
        
        # SKU属性
        sku_attrs = [
            {"name": "颜色", "values": [{"name": c} for c in random.sample(["红色", "蓝色", "黑色", "白色", "粉色"], 3)]},
            {"name": "尺码", "values": [{"name": s} for s in random.sample(["S", "M", "L", "XL"], 3)]},
        ]
        
        # SKU列表
        skus = []
        for j in range(random.randint(3, 6)):
            skus.append({
                "sku_id": f"SKU{random.randint(10000, 99999)}",
                "attributes": {"颜色": random.choice(["红色", "蓝色", "黑色"]), "尺码": random.choice(["M", "L"])},
                "price": round(price * random.uniform(0.9, 1.1), 2),
                "stock": random.randint(10, 500),
            })
        
        claimed_by = None
        claimed_at = None
        if status in ['claimed', 'published']:
            claimed_by = user
            claimed_at = timezone.now() - timedelta(days=random.randint(1, 10))
        
        CollectedProduct.objects.create(
            tenant=tenant,
            config=config,
            source_url=f"https://detail.{platform_code}.com/item/{random.randint(100000000, 999999999)}",
            source_platform=platform_code,
            source_id=str(random.randint(100000000, 999999999)),
            title=f"{title} - 型号{i+1:03d}",
            main_image=f"https://picsum.photos/400/400?random={i}",
            images=[f"https://picsum.photos/400/400?random={i+j}" for j in range(5)],
            description=f"采集商品描述 {i+1}",
            original_price_min=round(price * 1.2, 2),
            original_price_max=round(price * 1.3, 2),
            price_min=price,
            price_max=round(price * 1.1, 2),
            currency='CNY',
            sku_attributes=sku_attrs,
            skus=skus,
            sku_count=len(skus),
            source_category_id=str(random.randint(1000, 9999)),
            source_category_name=random.choice(["数码电器", "服装鞋包", "家居日用", "美妆个护", "母婴玩具"]),
            brand=random.choice(["小米", "华为", "无品牌", "Apple", "Sony", ""]),
            weight=round(random.uniform(0.1, 2.0), 2),
            collect_status='success',
            collect_time=timezone.now(),
            status=status,
            claimed_by=claimed_by,
            claimed_at=claimed_at,
        )
    
    print(f"✓ 采集商品: {count} 条")
    
    # 统计
    pending = CollectedProduct.objects.filter(tenant=tenant, status='pending').count()
    claimed = CollectedProduct.objects.filter(tenant=tenant, status='claimed').count()
    published = CollectedProduct.objects.filter(tenant=tenant, status='published').count()
    ignored = CollectedProduct.objects.filter(tenant=tenant, status='ignored').count()
    
    print(f"\n{'=' * 60}")
    print("数据统计:")
    print(f"  - 待认领: {pending}")
    print(f"  - 已认领: {claimed}")
    print(f"  - 已发布: {published}")
    print(f"  - 已忽略: {ignored}")
    print(f"{'=' * 60}")
    print("\n演示数据生成完成！")
    print("登录信息: admin / admin123")


if __name__ == '__main__':
    generate_demo_data()
