"""
采集任务异步处理（Celery）
"""

from celery import shared_task
from django.utils import timezone
import requests
from bs4 import BeautifulSoup
import re
import json


@shared_task
def process_collection_task(task_id):
    """处理采集任务"""
    from .models import CollectionTask, CollectedProduct
    from apps.platforms.models import Platform
    from apps.tenants.models import Tenant
    from .scraper import ScraperFactory
    
    task = CollectionTask.objects.get(id=task_id)
    task.status = 'processing'
    task.started_at = timezone.now()
    task.save()
    
    try:
        success_count = 0
        fail_count = 0
        
        for item in task.source_urls:
            url = item.get('url', '')
            platform_code = item.get('platform', '')
            
            if not url:
                continue
            
            # 检测平台
            if not platform_code:
                platform_code = ScraperFactory.detect_platform(url)
            
            # 获取爬虫
            scraper = ScraperFactory.get_scraper(platform_code)
            if not scraper:
                fail_count += 1
                continue
            
            # 执行采集
            try:
                scraped_data = scraper.scrape(url)
                
                if scraped_data:
                    # 应用采集配置转换
                    apply_collection_config(task, scraped_data)
                    
                    # 保存商品
                    platform = Platform.objects.filter(code=platform_code).first()
                    
                    CollectedProduct.objects.create(
                        tenant=task.tenant,
                        task=task,
                        config=task.config,
                        platform=platform,
                        source_url=scraped_data.source_url,
                        source_platform=scraped_data.source_platform,
                        source_id=scraped_data.source_id,
                        title=scraped_data.title,
                        title_en='',  # TODO: 翻译
                        description=scraped_data.description,
                        main_image=scraped_data.main_image,
                        images=scraped_data.images,
                        original_price_min=scraped_data.original_price,
                        original_price_max=scraped_data.original_price,
                        price_min=scraped_data.price,
                        price_max=scraped_data.price,
                        currency=scraped_data.currency,
                        sku_attributes=scraped_data.sku_attributes,
                        skus=scraped_data.skus,
                        sku_count=len(scraped_data.skus),
                        category_name=scraped_data.category_name,
                        brand=scraped_data.brand,
                        weight=scraped_data.weight,
                        raw_data=scraped_data.raw_data,
                        collect_status='success',
                        collect_time=timezone.now(),
                        status='pending'
                    )
                    success_count += 1
                else:
                    fail_count += 1
                    
            except Exception as e:
                fail_count += 1
                # 记录错误但不中断任务
                print(f"采集失败 {url}: {e}")
        
        # 更新任务状态
        task.success_count = success_count
        task.fail_count = fail_count
        task.status = 'completed' if fail_count == 0 else 'partial' if success_count > 0 else 'failed'
        task.completed_at = timezone.now()
        task.save()
        
    except Exception as e:
        task.status = 'failed'
        task.error_msg = str(e)
        task.completed_at = timezone.now()
        task.save()


def apply_collection_config(task, scraped_data):
    """应用采集配置转换"""
    config = task.config
    if not config:
        return
    
    # 价格转换
    if config.price_rule == 'fixed':
        scraped_data.price = scraped_data.original_price * float(config.price_multiplier) + float(config.price_addition)
    
    # 价格保护
    if config.min_price and scraped_data.price < config.min_price:
        scraped_data.price = config.min_price
    if config.max_price and scraped_data.price > config.max_price:
        scraped_data.price = config.max_price
    
    # 默认库存
    for sku in scraped_data.skus:
        if not sku.get('stock'):
            sku['stock'] = config.default_stock


@shared_task
def process_plugin_data(log_id):
    """处理插件推送的数据"""
    from .models import CollectionPluginLog, CollectedProduct
    
    log = CollectionPluginLog.objects.get(id=log_id)
    log.status = 'processing'
    log.save()
    
    try:
        data = log.payload
        
        # 创建采集商品
        product = CollectedProduct.objects.create(
            tenant=log.tenant,
            source_url=data.get('url', ''),
            source_platform=data.get('platform', ''),
            source_id=data.get('product_id', ''),
            title=data.get('title', ''),
            main_image=data.get('main_image', ''),
            images=data.get('images', []),
            price_min=data.get('price', 0),
            price_max=data.get('price', 0),
            currency=data.get('currency', 'CNY'),
            sku_attributes=data.get('sku_attributes', []),
            skus=data.get('skus', []),
            sku_count=len(data.get('skus', [])),
            raw_data=data,
            collect_status='success',
            collect_time=timezone.now(),
            status='pending'
        )
        
        log.status = 'success'
        log.product = product
        log.processed_at = timezone.now()
        log.save()
        
    except Exception as e:
        log.status = 'failed'
        log.error_msg = str(e)
        log.processed_at = timezone.now()
        log.save()


@shared_task
def download_product_images(product_id):
    """下载商品图片到本地"""
    from .models import CollectedProduct
    import os
    from django.conf import settings
    
    product = CollectedProduct.objects.get(id=product_id)
    
    # 创建存储目录
    tenant_dir = os.path.join(settings.MEDIA_ROOT, 'collections', str(product.tenant_id))
    os.makedirs(tenant_dir, exist_ok=True)
    
    local_images = []
    
    # 下载主图
    if product.main_image:
        try:
            response = requests.get(product.main_image, timeout=30)
            if response.status_code == 200:
                ext = product.main_image.split('.')[-1].split('?')[0] or 'jpg'
                filename = f"{product.id}_main.{ext}"
                filepath = os.path.join(tenant_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                product.main_image_local = f"collections/{product.tenant_id}/{filename}"
        except Exception as e:
            print(f"下载主图失败: {e}")
    
    # 下载详情图
    for idx, img_url in enumerate(product.images[:10]):  # 最多10张
        try:
            response = requests.get(img_url, timeout=30)
            if response.status_code == 200:
                ext = img_url.split('.')[-1].split('?')[0] or 'jpg'
                filename = f"{product.id}_{idx}.{ext}"
                filepath = os.path.join(tenant_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                local_images.append(f"collections/{product.tenant_id}/{filename}")
        except Exception as e:
            print(f"下载图片失败 {img_url}: {e}")
    
    product.images_local = local_images
    product.save()
