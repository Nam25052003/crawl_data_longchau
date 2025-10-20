"""
Crawler chính cho website Long Châu
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
from tqdm import tqdm
import logging

from config.settings import *
from src.utils.helpers import *

class LongChauCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.logger = setup_logging()
        self.products = []
        
    def get_product_urls(self, category: str, max_pages: int = 5) -> List[str]:
        """Lấy danh sách URL sản phẩm từ một danh mục"""
        product_urls = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{BASE_URL}/{category}?page={page}"
                self.logger.info(f"Crawling category page: {url}")
                
                response = make_request(url, self.session.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Tìm các link sản phẩm dựa trên cấu trúc thực tế của Long Châu
                product_links = soup.find_all('a', href=lambda x: x and '/thuoc/' in x and '.html' in x)
                
                if not product_links:
                    self.logger.warning(f"Không tìm thấy sản phẩm nào ở trang {page}")
                    break
                
                for link in product_links:
                    href = link.get('href')
                    if href:
                        if href.startswith('/'):
                            href = BASE_URL + href
                        product_urls.append(href)
                
                random_delay(*RANDOM_DELAY_RANGE)
                
            except Exception as e:
                self.logger.error(f"Lỗi khi crawl trang {page}: {str(e)}")
                continue
        
        self.logger.info(f"Tìm thấy {len(product_urls)} sản phẩm trong danh mục {category}")
        return list(set(product_urls))  # Loại bỏ duplicate
    
    def crawl_product_detail(self, product_url: str) -> Dict[str, Any]:
        """Crawl thông tin chi tiết một sản phẩm"""
        try:
            response = make_request(product_url, self.session.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trích xuất thông tin sản phẩm (cần điều chỉnh selector theo cấu trúc thực tế)
            product_data = {
                'url': product_url,
                'name': self.extract_product_name(soup),
                'price': self.extract_price(soup),
                'original_price': self.extract_original_price(soup),
                'discount': self.extract_discount(soup),
                'description': self.extract_description(soup),
                'ingredients': self.extract_ingredients(soup),
                'usage': self.extract_usage(soup),
                'brand': self.extract_brand(soup),
                'category': self.extract_category(soup),
                'availability': self.extract_availability(soup),
                'images': self.extract_images(soup),
                'rating': self.extract_rating(soup),
                'reviews_count': self.extract_reviews_count(soup),
                'crawled_at': datetime.now().isoformat()
            }
            
            return product_data
            
        except Exception as e:
            self.logger.error(f"Lỗi khi crawl sản phẩm {product_url}: {str(e)}")
            return None
    
    def extract_product_name(self, soup: BeautifulSoup) -> str:
        """Trích xuất tên sản phẩm"""
        selectors = ['h1', '.product-title', '.product-name', '.title']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return clean_text(element.get_text())
        return ""
    
    def extract_price(self, soup: BeautifulSoup) -> float:
        """Trích xuất giá sản phẩm"""
        selectors = ['.price', '[class*="price"]', '.cost', '.gia', 'span[class*="price"]', 'div[class*="price"]']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text()
                if price_text and any(char.isdigit() for char in price_text):
                    return format_price(price_text)
        return 0.0
    
    def extract_original_price(self, soup: BeautifulSoup) -> float:
        """Trích xuất giá gốc"""
        selectors = ['.price-original', '.price-old', '.original-price']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return format_price(element.get_text())
        return 0.0
    
    def extract_discount(self, soup: BeautifulSoup) -> str:
        """Trích xuất thông tin giảm giá"""
        selectors = ['.discount-percent', '.sale-badge', '.discount']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return clean_text(element.get_text())
        return ""
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Trích xuất mô tả sản phẩm"""
        selectors = ['.product-description', '.description', '.product-detail']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return clean_text(element.get_text())
        return ""
    
    def extract_ingredients(self, soup: BeautifulSoup) -> str:
        """Trích xuất thành phần"""
        selectors = ['.ingredients', '.composition', '.thanh-phan']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return clean_text(element.get_text())
        return ""
    
    def extract_usage(self, soup: BeautifulSoup) -> str:
        """Trích xuất cách sử dụng"""
        selectors = ['.usage', '.cach-dung', '.instructions']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return clean_text(element.get_text())
        return ""
    
    def extract_brand(self, soup: BeautifulSoup) -> str:
        """Trích xuất thương hiệu"""
        selectors = ['.brand', '.manufacturer', '.thuong-hieu']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return clean_text(element.get_text())
        return ""
    
    def extract_category(self, soup: BeautifulSoup) -> str:
        """Trích xuất danh mục"""
        selectors = ['.breadcrumb', '.category', '.danh-muc']
        for selector in selectors:
            elements = soup.select(f'{selector} a')
            if elements:
                return ' > '.join([clean_text(el.get_text()) for el in elements])
        return ""
    
    def extract_availability(self, soup: BeautifulSoup) -> str:
        """Trích xuất tình trạng còn hàng"""
        selectors = ['.availability', '.stock-status', '.tinh-trang']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return clean_text(element.get_text())
        return ""
    
    def extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Trích xuất danh sách ảnh"""
        images = []
        selectors = ['img', '.product-images img', '.gallery img', '.image img']
        for selector in selectors:
            elements = soup.select(selector)
            for img in elements:
                src = img.get('src') or img.get('data-src')
                if src and ('product' in src.lower() or 'thuoc' in src.lower() or 'cms-prod' in src):
                    if src.startswith('/'):
                        src = BASE_URL + src
                    images.append(src)
        return list(set(images))
    
    def extract_rating(self, soup: BeautifulSoup) -> float:
        """Trích xuất đánh giá sao"""
        selectors = ['.rating', '.stars', '.danh-gia']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Tìm số sao từ class hoặc text
                text = element.get_text()
                try:
                    return float(''.join(filter(str.isdigit, text.split('/')[0])))
                except:
                    pass
        return 0.0
    
    def extract_reviews_count(self, soup: BeautifulSoup) -> int:
        """Trích xuất số lượng đánh giá"""
        selectors = ['.reviews-count', '.review-count', '.so-danh-gia']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text()
                try:
                    return int(''.join(filter(str.isdigit, text)))
                except:
                    pass
        return 0
    
    def crawl_category(self, category: str, max_pages: int = 5, max_products: int = None):
        """Crawl toàn bộ sản phẩm trong một danh mục"""
        self.logger.info(f"Bắt đầu crawl danh mục: {category}")
        
        # Lấy danh sách URL sản phẩm
        product_urls = self.get_product_urls(category, max_pages)
        
        if max_products:
            product_urls = product_urls[:max_products]
        
        # Crawl từng sản phẩm
        for url in tqdm(product_urls, desc=f"Crawling {category}"):
            product_data = self.crawl_product_detail(url)
            if product_data:
                self.products.append(product_data)
            
            random_delay(*RANDOM_DELAY_RANGE)
        
        self.logger.info(f"Hoàn thành crawl danh mục {category}: {len(self.products)} sản phẩm")
    
    def crawl_all_categories(self, max_pages_per_category: int = 5, max_products_per_category: int = None):
        """Crawl tất cả danh mục"""
        for category in CATEGORIES:
            try:
                self.crawl_category(category, max_pages_per_category, max_products_per_category)
            except Exception as e:
                self.logger.error(f"Lỗi khi crawl danh mục {category}: {str(e)}")
                continue
    
    def save_data(self, format_type: str = 'both'):
        """Lưu dữ liệu đã crawl"""
        if not self.products:
            self.logger.warning("Không có dữ liệu để lưu")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type in ['json', 'both']:
            json_file = f"data/longchau_products_{timestamp}.json"
            save_to_json(self.products, json_file)
            self.logger.info(f"Đã lưu {len(self.products)} sản phẩm vào {json_file}")
        
        if format_type in ['csv', 'both']:
            csv_file = f"data/longchau_products_{timestamp}.csv"
            save_to_csv(self.products, csv_file)
            self.logger.info(f"Đã lưu {len(self.products)} sản phẩm vào {csv_file}")

if __name__ == "__main__":
    crawler = LongChauCrawler()
    
    # Ví dụ sử dụng
    try:
        # Crawl một danh mục cụ thể
        crawler.crawl_category("thuoc-khong-ke-don", max_pages=2, max_products=10)
        
        # Hoặc crawl tất cả danh mục
        # crawler.crawl_all_categories(max_pages_per_category=2, max_products_per_category=5)
        
        # Lưu dữ liệu
        crawler.save_data('both')
        
    except KeyboardInterrupt:
        print("\nĐã dừng crawler. Đang lưu dữ liệu...")
        crawler.save_data('both')
    except Exception as e:
        logging.error(f"Lỗi không mong muốn: {str(e)}")
        crawler.save_data('both')
