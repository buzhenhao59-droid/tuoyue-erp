"""
拓岳 ERP - 产品采集爬虫模块
支持 1688、淘宝、天猫、Shopee、Lazada、TikTok 等平台的商品信息采集
"""

import re
import json
import time
import random
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup


@dataclass
class CollectedProduct:
    """采集的商品数据结构"""
    source_url: str
    source_platform: str
    source_id: str
    title: str
    main_image: str
    images: List[str]
    description: str
    original_price: float
    price: float
    currency: str
    sku_attributes: List[Dict]
    skus: List[Dict]
    category_id: str
    category_name: str
    brand: str
    weight: float
    raw_data: Dict


class BaseScraper:
    """爬虫基类"""
    
    # 请求头池，模拟不同浏览器
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self._init_session()
    
    def _init_session(self):
        """初始化会话，设置请求头"""
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def _get_random_ua(self) -> str:
        """获取随机 User-Agent"""
        return random.choice(self.USER_AGENTS)
    
    def _add_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """添加随机延迟，模拟人类行为"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def _extract_json_from_html(self, html: str, pattern: str) -> Optional[Dict]:
        """从 HTML 中提取 JSON 数据"""
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None
    
    def scrape(self, url: str) -> Optional[Dict]:
        """子类必须实现的采集方法"""
        raise NotImplementedError


class Alibaba1688Scraper(BaseScraper):
    """1688 商品采集器"""
    
    PLATFORM_CODE = '1688'
    
    def scrape(self, url: str) -> Optional[Dict]:
        """
        采集 1688 商品信息
        示例 URL: https://detail.1688.com/offer/123456789.html
        """
        try:
            # 提取商品ID
            offer_id = self._extract_offer_id(url)
            if not offer_id:
                print(f"[1688] 无法提取商品ID: {url}")
                return None
            
            # 设置请求头
            self.session.headers['User-Agent'] = self._get_random_ua()
            self.session.headers['Referer'] = 'https://www.1688.com/'
            
            # 添加延迟
            self._add_delay(1, 2)
            
            # 发送请求
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"[1688] 请求失败: {response.status_code}")
                return None
            
            # 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取商品数据
            product_data = self._parse_product_data(soup, response.text, offer_id, url)
            
            if not product_data:
                print(f"[1688] 解析失败: {url}")
                return None
            
            return product_data
            
        except Exception as e:
            print(f"[1688] 采集异常: {e}")
            return None
    
    def _extract_offer_id(self, url: str) -> Optional[str]:
        """从 URL 中提取 offer ID"""
        patterns = [
            r'/offer/(\d+)\.html',
            r'offerId=(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _parse_product_data(self, soup: BeautifulSoup, html: str, offer_id: str, url: str) -> Optional[Dict]:
        """解析商品数据"""
        try:
            # 提取标题
            title_selectors = [
                'h1.d-title',
                '.offer-title h1',
                '[data-spm="offer_title"]',
                'h1.title',
            ]
            title = ''
            for selector in title_selectors:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text(strip=True)
                    break
            
            # 提取价格
            price = self._extract_price(soup, html)
            
            # 提取图片
            images = self._extract_images(soup, html)
            main_image = images[0] if images else ''
            
            # 提取SKU信息
            sku_attributes, skus = self._extract_skus(soup, html)
            
            # 提取类目
            category_name = self._extract_category(soup)
            
            # 提取描述
            description = self._extract_description(soup)
            
            # 提取重量
            weight = self._extract_weight(soup, html)
            
            return {
                'source_url': f"https://detail.1688.com/offer/{offer_id}.html",
                'source_platform': self.PLATFORM_CODE,
                'source_id': offer_id,
                'title': title or '未知商品',
                'main_image': main_image,
                'images': images[:10],  # 最多10张
                'description': description,
                'original_price': price,
                'price': price,
                'currency': 'CNY',
                'sku_attributes': sku_attributes,
                'skus': skus,
                'category_id': '',
                'category_name': category_name,
                'brand': '',
                'weight': weight,
                'raw_data': {}
            }
            
        except Exception as e:
            print(f"[1688] 解析异常: {e}")
            return None
    
    def _extract_price(self, soup: BeautifulSoup, html: str) -> float:
        """提取价格"""
        # 尝试多种价格选择器
        price_patterns = [
            r'"price":"(\d+\.?\d*)"',
            r'"offerPrice":"(\d+\.?\d*)"',
            r'class="[^"]*price[^"]*"[^>]*>(\d+\.?\d*)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, html)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        # 从页面元素提取
        price_selectors = [
            '.price .value',
            '.offer-price',
            '[data-spm="price"]',
        ]
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    return float(match.group(1))
        
        return 0.0
    
    def _extract_images(self, soup: BeautifulSoup, html: str) -> List[str]:
        """提取商品图片"""
        images = []
        
        # 从 JSON 数据中提取
        img_pattern = r'"imageUrlList":\s*(\[[^\]]+\])'
        match = re.search(img_pattern, html)
        if match:
            try:
                img_list = json.loads(match.group(1))
                images = [url.replace('\\u002F', '/') for url in img_list]
            except:
                pass
        
        # 从 img 标签提取
        if not images:
            for img in soup.select('.gallery img, .offer-img img, .main-image img'):
                src = img.get('src') or img.get('data-src')
                if src:
                    images.append(src)
        
        return images
    
    def _extract_skus(self, soup: BeautifulSoup, html: str) -> tuple:
        """提取SKU信息"""
        sku_attributes = []
        skus = []
        
        # 尝试从页面 JSON 提取
        sku_pattern = r'"skuProps":\s*(\[[^\]]+\])'
        match = re.search(sku_pattern, html)
        if match:
            try:
                sku_props = json.loads(match.group(1))
                for prop in sku_props:
                    attr = {
                        'name': prop.get('prop', ''),
                        'values': [v.get('name', '') for v in prop.get('value', [])]
                    }
                    sku_attributes.append(attr)
            except:
                pass
        
        # 提取SKU列表
        sku_list_pattern = r'"skuList":\s*(\[[^\]]+\])'
        match = re.search(sku_list_pattern, html)
        if match:
            try:
                sku_list = json.loads(match.group(1))
                for sku in sku_list:
                    skus.append({
                        'sku_id': sku.get('skuId', ''),
                        'attributes': sku.get('attributes', {}),
                        'price': float(sku.get('price', 0)),
                        'stock': int(sku.get('stock', 0)),
                        'image': sku.get('image', ''),
                    })
            except:
                pass
        
        return sku_attributes, skus
    
    def _extract_category(self, soup: BeautifulSoup) -> str:
        """提取类目"""
        category_elem = soup.select_one('.category-path, .breadcrumb')
        if category_elem:
            return category_elem.get_text(strip=True, separator=' > ')
        return ''
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """提取商品描述"""
        desc_elem = soup.select_one('.offer-desc, .description, #mod-detail-description')
        if desc_elem:
            return desc_elem.get_text(strip=True)
        return ''
    
    def _extract_weight(self, soup: BeautifulSoup, html: str) -> float:
        """提取重量"""
        weight_patterns = [
            r'(\d+\.?\d*)\s*[kK][gG]',
            r'重量[:：]\s*(\d+\.?\d*)',
        ]
        for pattern in weight_patterns:
            match = re.search(pattern, html)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        return 0.0


class TaobaoScraper(BaseScraper):
    """淘宝商品采集器"""
    
    PLATFORM_CODE = 'taobao'
    
    def scrape(self, url: str) -> Optional[Dict]:
        """采集淘宝商品信息"""
        try:
            item_id = self._extract_item_id(url)
            if not item_id:
                return None
            
            self.session.headers['User-Agent'] = self._get_random_ua()
            self.session.headers['Referer'] = 'https://www.taobao.com/'
            
            self._add_delay(1, 2)
            
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取商品数据
            title = self._extract_title(soup)
            price = self._extract_price(soup, response.text)
            images = self._extract_images(soup, response.text)
            
            return {
                'source_url': url,
                'source_platform': self.PLATFORM_CODE,
                'source_id': item_id,
                'title': title,
                'main_image': images[0] if images else '',
                'images': images[:10],
                'description': '',
                'original_price': price,
                'price': price,
                'currency': 'CNY',
                'sku_attributes': [],
                'skus': [],
                'category_id': '',
                'category_name': '',
                'brand': '',
                'weight': 0,
                'raw_data': {}
            }
            
        except Exception as e:
            print(f"[Taobao] 采集异常: {e}")
            return None
    
    def _extract_item_id(self, url: str) -> Optional[str]:
        """提取商品ID"""
        patterns = [
            r'id=(\d+)',
            r'item/(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取标题"""
        selectors = ['h3.tb-main-title', '.tb-detail-hd h1', 'h1[data-spm]']
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ''
    
    def _extract_price(self, soup: BeautifulSoup, html: str) -> float:
        """提取价格"""
        patterns = [
            r'"price":"(\d+\.?\d*)"',
            r'"defaultItemPrice":"(\d+\.?\d*)"',
        ]
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        return 0.0
    
    def _extract_images(self, soup: BeautifulSoup, html: str) -> List[str]:
        """提取图片"""
        images = []
        pattern = r'"auctionImages":\s*(\[[^\]]+\])'
        match = re.search(pattern, html)
        if match:
            try:
                img_list = json.loads(match.group(1))
                images = [f"https:{url}" if url.startswith('//') else url for url in img_list]
            except:
                pass
        return images


class TmallScraper(TaobaoScraper):
    """天猫商品采集器"""
    
    PLATFORM_CODE = 'tmall'


class ShopeeScraper(BaseScraper):
    """Shopee 商品采集器"""
    
    PLATFORM_CODE = 'shopee'
    
    def scrape(self, url: str) -> Optional[Dict]:
        """
        采集 Shopee 商品信息
        示例 URL: https://shopee.sg/product/123/456
        """
        try:
            shop_id, item_id = self._extract_ids(url)
            if not shop_id or not item_id:
                print(f"[Shopee] 无法提取ID: {url}")
                return None
            
            # Shopee 使用 API 获取数据
            self.session.headers['User-Agent'] = self._get_random_ua()
            self.session.headers['Referer'] = 'https://shopee.sg/'
            
            self._add_delay(1, 2)
            
            # 调用 Shopee API
            api_url = f"https://shopee.sg/api/v4/item/get"
            params = {
                'itemid': item_id,
                'shopid': shop_id,
            }
            
            response = self.session.get(api_url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"[Shopee] API请求失败: {response.status_code}")
                return None
            
            data = response.json()
            if data.get('error'):
                print(f"[Shopee] API错误: {data.get('error_msg')}")
                return None
            
            return self._parse_api_data(data.get('data', {}), url, shop_id, item_id)
            
        except Exception as e:
            print(f"[Shopee] 采集异常: {e}")
            return None
    
    def _extract_ids(self, url: str) -> tuple:
        """提取 shop_id 和 item_id"""
        patterns = [
            r'product/(\d+)/(\d+)',
            r'i\.(\d+)\.(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), match.group(2)
        return None, None
    
    def _parse_api_data(self, data: Dict, url: str, shop_id: str, item_id: str) -> Optional[Dict]:
        """解析 API 返回的数据"""
        try:
            item = data
            
            # 提取图片
            images = []
            for img in item.get('images', []):
                images.append(f"https://cf.shopee.sg/file/{img}")
            
            # 提取SKU
            sku_attributes = []
            skus = []
            
            tier_variations = item.get('tier_variations', [])
            for tier in tier_variations:
                attr = {
                    'name': tier.get('name', ''),
                    'values': tier.get('options', [])
                }
                sku_attributes.append(attr)
            
            models = item.get('models', [])
            for model in models:
                skus.append({
                    'sku_id': str(model.get('modelid', '')),
                    'name': model.get('name', ''),
                    'price': model.get('price', 0) / 100000,  # Shopee 价格单位
                    'stock': model.get('stock', 0),
                })
            
            return {
                'source_url': url,
                'source_platform': self.PLATFORM_CODE,
                'source_id': item_id,
                'title': item.get('name', ''),
                'main_image': images[0] if images else '',
                'images': images[:10],
                'description': item.get('description', ''),
                'original_price': item.get('price_max', 0) / 100000,
                'price': item.get('price', 0) / 100000,
                'currency': item.get('currency', 'SGD'),
                'sku_attributes': sku_attributes,
                'skus': skus,
                'category_id': str(item.get('catid', '')),
                'category_name': '',
                'brand': item.get('brand', ''),
                'weight': item.get('weight', 0) / 1000,  # 转换为kg
                'raw_data': item
            }
            
        except Exception as e:
            print(f"[Shopee] 解析异常: {e}")
            return None


class LazadaScraper(BaseScraper):
    """Lazada 商品采集器"""
    
    PLATFORM_CODE = 'lazada'
    
    def scrape(self, url: str) -> Optional[Dict]:
        """采集 Lazada 商品信息"""
        try:
            item_id = self._extract_item_id(url)
            if not item_id:
                return None
            
            self.session.headers['User-Agent'] = self._get_random_ua()
            self.session.headers['Referer'] = 'https://www.lazada.sg/'
            
            self._add_delay(1, 2)
            
            response = self.session.get(url, timeout=30)
            
            if response.status_code != 200:
                return None
            
            # 从页面提取数据
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试从 script 标签提取
            script_pattern = r'window\.__initData\s*=\s*({.+?});'
            match = re.search(script_pattern, response.text)
            
            if match:
                data = json.loads(match.group(1))
                return self._parse_data(data, url, item_id)
            
            # 备用方案：从 HTML 提取
            return self._parse_from_html(soup, url, item_id)
            
        except Exception as e:
            print(f"[Lazada] 采集异常: {e}")
            return None
    
    def _extract_item_id(self, url: str) -> Optional[str]:
        """提取商品ID"""
        patterns = [
            r'-i(\d+)',
            r'/products/[\w-]+-(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _parse_data(self, data: Dict, url: str, item_id: str) -> Dict:
        """解析 Lazada 数据"""
        # 根据实际数据结构解析
        return {
            'source_url': url,
            'source_platform': self.PLATFORM_CODE,
            'source_id': item_id,
            'title': data.get('data', {}).get('root', {}).get('fields', {}).get('product', {}).get('title', ''),
            'main_image': '',
            'images': [],
            'description': '',
            'original_price': 0,
            'price': 0,
            'currency': 'SGD',
            'sku_attributes': [],
            'skus': [],
            'category_id': '',
            'category_name': '',
            'brand': '',
            'weight': 0,
            'raw_data': data
        }
    
    def _parse_from_html(self, soup: BeautifulSoup, url: str, item_id: str) -> Dict:
        """从 HTML 解析"""
        title_elem = soup.select_one('.pdp-product-title h1')
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        return {
            'source_url': url,
            'source_platform': self.PLATFORM_CODE,
            'source_id': item_id,
            'title': title,
            'main_image': '',
            'images': [],
            'description': '',
            'original_price': 0,
            'price': 0,
            'currency': 'SGD',
            'sku_attributes': [],
            'skus': [],
            'category_id': '',
            'category_name': '',
            'brand': '',
            'weight': 0,
            'raw_data': {}
        }


class TikTokScraper(BaseScraper):
    """TikTok Shop 商品采集器"""
    
    PLATFORM_CODE = 'tiktok'
    
    def scrape(self, url: str) -> Optional[Dict]:
        """采集 TikTok Shop 商品信息"""
        try:
            product_id = self._extract_product_id(url)
            if not product_id:
                return None
            
            self.session.headers['User-Agent'] = self._get_random_ua()
            
            # TikTok Shop 需要特殊的 API 调用
            # 这里提供基础框架
            
            return {
                'source_url': url,
                'source_platform': self.PLATFORM_CODE,
                'source_id': product_id,
                'title': '',
                'main_image': '',
                'images': [],
                'description': '',
                'original_price': 0,
                'price': 0,
                'currency': 'USD',
                'sku_attributes': [],
                'skus': [],
                'category_id': '',
                'category_name': '',
                'brand': '',
                'weight': 0,
                'raw_data': {}
            }
            
        except Exception as e:
            print(f"[TikTok] 采集异常: {e}")
            return None
    
    def _extract_product_id(self, url: str) -> Optional[str]:
        """提取商品ID"""
        patterns = [
            r'/product/(\d+)',
            r'product_id=(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None


class ScraperFactory:
    """爬虫工厂"""
    
    SCRAPERS = {
        '1688': Alibaba1688Scraper,
        'taobao': TaobaoScraper,
        'tmall': TmallScraper,
        'shopee': ShopeeScraper,
        'lazada': LazadaScraper,
        'tiktok': TikTokScraper,
    }
    
    @classmethod
    def get_scraper(cls, platform: str) -> Optional[BaseScraper]:
        """获取对应平台的爬虫"""
        scraper_class = cls.SCRAPERS.get(platform.lower())
        if scraper_class:
            return scraper_class()
        return None
    
    @classmethod
    def detect_platform(cls, url: str) -> Optional[str]:
        """从 URL 检测平台"""
        domain_patterns = {
            '1688': ['1688.com'],
            'taobao': ['taobao.com'],
            'tmall': ['tmall.com'],
            'pdd': ['pinduoduo.com', 'yangkeduo.com'],
            'douyin': ['douyin.com'],
            'jd': ['jd.com', 'jingdong.com'],
            'aliexpress': ['aliexpress.com'],
            'shopee': ['shopee.'],
            'lazada': ['lazada.'],
            'amazon': ['amazon.'],
            'ebay': ['ebay.'],
            'tiktok': ['tiktok.com'],
        }
        
        url_lower = url.lower()
        for platform, domains in domain_patterns.items():
            for domain in domains:
                if domain in url_lower:
                    return platform
        return None


# ============================================
# 使用示例
# ============================================

if __name__ == '__main__':
    # 测试 1688 采集
    test_url = "https://detail.1688.com/offer/680245789012.html"
    
    platform = ScraperFactory.detect_platform(test_url)
    print(f"检测到平台: {platform}")
    
    scraper = ScraperFactory.get_scraper(platform)
    if scraper:
        product = scraper.scrape(test_url)
        if product:
            print(f"采集成功: {product['title']}")
            print(f"价格: {product['price']} {product['currency']}")
            print(f"图片数: {len(product['images'])}")
            print(f"SKU数: {len(product['skus'])}")
        else:
            print("采集失败")
    else:
        print(f"不支持的平台: {platform}")