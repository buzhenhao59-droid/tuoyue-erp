#!/usr/bin/env python3
"""
生成50条采集商品模拟数据
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/home/zmx/.openclaw/workspace/tuoyue-erp/backend')
django.setup()

from apps.collections.models import CollectedProduct, CollectionTask
from apps.tenants.models import Tenant
from apps.users.models import User
import random
from datetime import datetime, timedelta

# 商品标题模板
TITLES = [
    "夏季新款女装连衣裙甜美碎花裙", "韩版时尚休闲T恤女短袖", "高腰显瘦牛仔裤女直筒裤",
    "气质优雅雪纺衬衫女长袖", "运动休闲套装女两件套", "复古文艺棉麻长裙",
    "ins风宽松卫衣女连帽", "职业装套装女西装外套", "温柔风针织开衫女",
    "性感露肩上衣女短袖", "百搭基础款白T恤女", "法式复古方领连衣裙",
    "显瘦阔腿裤女高腰垂感", "甜美娃娃领衬衫女", "休闲运动裤女束脚裤",
    "气质中长款风衣女", "简约纯色针织衫女", "复古格子衬衫女长袖",
    "高腰A字裙女半身裙", "舒适家居服女套装", "时尚百搭小西装女",
    "甜美蕾丝连衣裙女", "休闲牛仔外套女", "气质真丝围巾女",
    "复古马丁靴女短靴", "时尚单肩包女斜挎", "简约手表女石英表",
    "甜美发饰套装女", "时尚太阳镜女韩版", "优雅珍珠项链女"
]

# 平台配置
PLATFORMS = [
    ('1688', '#FF6A00'),
    ('taobao', '#FF5000'),
    ('tmall', '#FF0036'),
    ('shopee', '#EE4D2D'),
    ('lazada', '#0F156D'),
]

# 状态
STATUSES = ['pending', 'claimed', 'editing', 'published', 'ignored']
STATUS_WEIGHTS = [0.4, 0.2, 0.15, 0.15, 0.1]

# 类目
CATEGORIES = [
    ('5001', '女装'), ('5002', '男装'), ('5003', '童装'),
    ('5004', '鞋靴'), ('5005', '箱包'), ('5006', '配饰')
]

def generate_mock_data():
    print("开始生成模拟数据...")
    
    # 获取默认租户和用户
    try:
        tenant = Tenant.objects.first()
        user = User.objects.first()
        if not tenant or not user:
            print("错误：请先创建租户和用户")
            return
    except Exception as e:
        print(f"获取租户/用户失败: {e}")
        return
    
    # 创建采集任务
    task = CollectionTask.objects.create(
        tenant=tenant,
        user=user,
        task_no=f"CJ{datetime.now().strftime('%Y%m%d%H%M%S')}",
        task_type='link',
        name='批量导入测试任务',
        status='completed',
        total_count=50,
        success_count=50,
        fail_count=0
    )
    
    print(f"创建任务: {task.task_no}")
    
    # 生成50条商品数据
    products = []
    for i in range(50):
        platform, color = random.choice(PLATFORMS)
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
        category = random.choice(CATEGORIES)
        title = random.choice(TITLES)
        
        # 生成价格
        original_price = round(random.uniform(20, 500), 2)
        price_multiplier = round(random.uniform(1.3, 2.0), 2)
        price_min = round(original_price * price_multiplier, 2)
        price_max = round(price_min * random.uniform(1.1, 1.5), 2)
        
        # 生成SKU
        sku_count = random.randint(1, 8)
        skus = []
        sku_attrs = []
        
        # 如果有多个SKU，生成规格
        if sku_count > 1:
            colors = ['红色', '蓝色', '黑色', '白色', '粉色', '灰色']
            sizes = ['S', 'M', 'L', 'XL', 'XXL']
            
            sku_attrs = [
                {'name': '颜色', 'values': [{'name': c} for c in random.sample(colors, min(3, len(colors)))]},
                {'name': '尺码', 'values': [{'name': s} for s in random.sample(sizes, min(3, len(sizes)))]}
            ]
            
            for j in range(sku_count):
                skus.append({
                    'sku_id': f'SKU{i+1:03d}-{j+1}',
                    'attributes': {
                        '颜色': random.choice(colors),
                        '尺码': random.choice(sizes)
                    },
                    'price': round(price_min * random.uniform(0.9, 1.1), 2),
                    'stock': random.randint(10, 999),
                    'image': f'https://via.placeholder.com/300x300.png?text=SKU{j+1}'
                })
        else:
            skus = [{
                'sku_id': f'SKU{i+1:03d}',
                'attributes': {'默认': '规格'},
                'price': price_min,
                'stock': random.randint(10, 999),
                'image': f'https://via.placeholder.com/300x300.png?text=Product{i+1}'
            }]
        
        # 生成图片
        main_image = f'https://via.placeholder.com/400x400.png?text={platform}+{i+1}'
        images = [main_image] + [f'https://via.placeholder.com/400x400.png?text=Detail{j}' for j in range(random.randint(2, 5))]
        
        # 创建时间（最近30天内）
        created_at = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        product = CollectedProduct(
            tenant=tenant,
            task=task,
            source_url=f'https://example.com/product/{i+1}',
            source_platform=platform,
            source_id=f'{platform.upper()}{random.randint(100000, 999999)}',
            source_shop_id=f'SHOP{random.randint(1000, 9999)}',
            source_shop_name=f'{platform}店铺{random.randint(1, 100)}',
            collect_status='success',
            title=title,
            title_en=title,
            description=f'这是商品{i+1}的详细描述，包含材质、尺寸、洗涤说明等信息。',
            main_image=main_image,
            images=images,
            original_price_min=original_price,
            original_price_max=original_price * random.uniform(1.1, 1.3),
            price_min=price_min,
            price_max=price_max,
            currency='CNY',
            source_category_id=category[0],
            source_category_name=category[1],
            sku_attributes=sku_attrs,
            skus=skus,
            sku_count=sku_count,
            status=status,
            weight=round(random.uniform(0.2, 1.5), 3),
            created_at=created_at,
            updated_at=created_at
        )
        products.append(product)
    
    # 批量创建
    CollectedProduct.objects.bulk_create(products)
    
    print(f"✅ 成功创建 {len(products)} 条采集商品数据")
    
    # 统计
    stats = {}
    for status in STATUSES:
        count = CollectedProduct.objects.filter(status=status).count()
        stats[status] = count
    
    print("\n状态分布:")
    for status, count in stats.items():
        print(f"  {status}: {count}")
    
    print("\n平台分布:")
    for platform, _ in PLATFORMS:
        count = CollectedProduct.objects.filter(source_platform=platform).count()
        print(f"  {platform}: {count}")

if __name__ == '__main__':
    generate_mock_data()