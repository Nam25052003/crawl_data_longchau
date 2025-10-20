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
from datetime import datetime

from config.settings import *
from src.utils.helpers import *

class LongChauCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.logger = setup_logging()
        self.products = []
        
    def get_product_urls(self, category_url: str) -> List[str]:
        """Lấy danh sách URL sản phẩm từ một danh mục"""
        product_urls = []
        
        try:
            url = f"{BASE_URL}/{category_url}"
            self.logger.info(f"Crawling category page: {url}")
            
            response = make_request(url, self.session.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm các link sản phẩm - Long Châu có thể có nhiều pattern khác nhau
            product_links = soup.find_all('a', href=True)
            
            for link in product_links:
                href = link.get('href')
                if href:
                    # Kiểm tra các pattern URL sản phẩm của Long Châu
                    if ('.html' in href and 
                        any(keyword in href for keyword in ['/thuoc/', '/thuc-pham-chuc-nang/', '/duoc-my-pham/', '/cham-soc-ca-nhan/', '/trang-thiet-bi-y-te/']) and
                        href.count('/') >= 2):  # Đảm bảo là URL sản phẩm chi tiết
                        
                        if href.startswith('/'):
                            href = BASE_URL + href
                        product_urls.append(href)
            
            random_delay(*RANDOM_DELAY_RANGE)
            
        except Exception as e:
            self.logger.error(f"Lỗi khi crawl danh mục {category_url}: {str(e)}")
        
        # Loại bỏ duplicate và filter chỉ lấy URL sản phẩm thực sự
        unique_urls = list(set(product_urls))
        filtered_urls = [url for url in unique_urls if self.is_product_url(url)]
        
        self.logger.info(f"Tìm thấy {len(filtered_urls)} sản phẩm trong danh mục {category_url}")
        return filtered_urls
    
    def is_product_url(self, url: str) -> bool:
        """Kiểm tra xem URL có phải là URL sản phẩm không"""
        # URL sản phẩm thường có format: /category/subcategory/product-name.html
        parts = url.replace(BASE_URL, '').split('/')
        return (len(parts) >= 3 and 
                url.endswith('.html') and
                not any(exclude in url for exclude in ['?', '#', 'page=', 'sort=']))
    
    def crawl_product_detail(self, product_url: str) -> Dict[str, Any]:
        """Crawl thông tin chi tiết một sản phẩm"""
        try:
            response = make_request(product_url, self.session.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trích xuất thông tin sản phẩm theo cấu trúc Long Châu
            product_data = {
                'url': product_url,
                'name': self.extract_product_name(soup),
                'price': self.extract_price(soup),
                'unit': self.extract_unit(soup),
                'sku': self.extract_sku(soup),
                'rating': self.extract_rating(soup),
                'reviews_count': self.extract_reviews_count(soup),
                'comments_count': self.extract_comments_count(soup),
                'brand': self.extract_brand(soup),
                'official_name': self.extract_official_name(soup),
                'category': self.extract_category(soup),
                'registration_number': self.extract_registration_number(soup),
                'form': self.extract_form(soup),
                'package_size': self.extract_package_size(soup),
                'origin_brand': self.extract_origin_brand(soup),
                'manufacturer': self.extract_manufacturer(soup),
                'country_of_manufacture': self.extract_country_of_manufacture(soup),
                'ingredients': self.extract_ingredients(soup),
                'images': self.extract_images(soup),
                'original_price': self.extract_original_price(soup),
                'discount': self.extract_discount(soup),
                'description': self.extract_description(soup),
                'usage': self.extract_usage(soup),
                'availability': self.extract_availability(soup),
                'crawled_at': datetime.now().isoformat()
            }
            
            return product_data
            
        except Exception as e:
            self.logger.error(f"Lỗi khi crawl sản phẩm {product_url}: {str(e)}")
            return None
    
    def extract_product_name(self, soup: BeautifulSoup) -> str:
        """Trích xuất tên sản phẩm"""
        # Selector chính xác từ Long Châu
        element = soup.select_one('h1[data-test="product_name"]')
        if element:
            return clean_text(element.get_text())
        
        # Fallback selectors
        selectors = ['h1', '.product-title', '.product-name', '.title']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return clean_text(element.get_text())
        return ""
    
    def extract_price(self, soup: BeautifulSoup) -> float:
        """Trích xuất giá sản phẩm"""
        # Selector chính xác từ Long Châu
        element = soup.select_one('span[data-test="price"]')
        if element:
            price_text = element.get_text()
            if price_text and any(char.isdigit() for char in price_text):
                return format_price(price_text)
        
        # Fallback selectors
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
        # Trích xuất từ bảng thông tin
        ingredients = self.extract_table_info(soup, "Thành phần")
        if ingredients:
            return ingredients
            
        # Fallback selectors
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
        # Tìm trong thông tin sản phẩm theo cấu trúc Long Châu
        brand_div = soup.find('div', string=lambda text: text and 'Thương hiệu:' in text)
        if brand_div:
            # Lấy text sau "Thương hiệu: "
            brand_text = brand_div.get_text()
            if 'Thương hiệu:' in brand_text:
                return clean_text(brand_text.split('Thương hiệu:')[1].strip())
        
        # Fallback selectors
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
    
    def extract_unit(self, soup: BeautifulSoup) -> str:
        """Trích xuất đơn vị tính"""
        element = soup.select_one('span[data-test="unit"]')
        if element:
            return clean_text(element.get_text())
        return ""
    
    def extract_sku(self, soup: BeautifulSoup) -> str:
        """Trích xuất mã sản phẩm (SKU)"""
        element = soup.select_one('span[data-test-id="sku"]')
        if element:
            return clean_text(element.get_text())
        return ""
    
    def extract_rating(self, soup: BeautifulSoup) -> float:
        """Trích xuất đánh giá sao"""
        # Tìm rating trong cấu trúc Long Châu
        rating_container = soup.find('div', class_='flex items-center')
        if rating_container:
            rating_text = rating_container.get_text()
            # Tìm số đầu tiên trong text (rating)
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        
        # Fallback selectors
        selectors = ['.rating', '.stars', '.danh-gia']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text()
                try:
                    return float(''.join(filter(str.isdigit, text.split('/')[0])))
                except:
                    pass
        return 0.0
    
    def extract_reviews_count(self, soup: BeautifulSoup) -> int:
        """Trích xuất số lượng đánh giá"""
        # Tìm text chứa "đánh giá"
        rating_container = soup.find('div', class_='flex items-center')
        if rating_container:
            text = rating_container.get_text()
            if 'đánh giá' in text:
                import re
                match = re.search(r'(\d+)\s*đánh giá', text)
                if match:
                    try:
                        return int(match.group(1))
                    except:
                        pass
        
        # Fallback selectors
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
    
    def extract_comments_count(self, soup: BeautifulSoup) -> int:
        """Trích xuất số lượng bình luận"""
        # Tìm text chứa "bình luận"
        rating_container = soup.find('div', class_='flex items-center')
        if rating_container:
            text = rating_container.get_text()
            if 'bình luận' in text:
                import re
                match = re.search(r'(\d+)\s*bình luận', text)
                if match:
                    try:
                        return int(match.group(1))
                    except:
                        pass
        return 0
    
    def extract_table_info(self, soup: BeautifulSoup, label: str) -> str:
        """Trích xuất thông tin từ bảng chi tiết sản phẩm"""
        # Tìm trong bảng content-list
        table = soup.find('table', class_='content-list')
        if table:
            rows = table.find_all('tr', class_='content-container')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label_cell = cells[0]
                    value_cell = cells[1]
                    if label_cell and label in label_cell.get_text():
                        return clean_text(value_cell.get_text())
        return ""
    
    def extract_official_name(self, soup: BeautifulSoup) -> str:
        """Trích xuất tên chính hãng"""
        return self.extract_table_info(soup, "Tên chính hãng")
    
    def extract_registration_number(self, soup: BeautifulSoup) -> str:
        """Trích xuất số đăng ký"""
        return self.extract_table_info(soup, "Số đăng ký")
    
    def extract_form(self, soup: BeautifulSoup) -> str:
        """Trích xuất dạng bào chế"""
        return self.extract_table_info(soup, "Dạng bào chế")
    
    def extract_package_size(self, soup: BeautifulSoup) -> str:
        """Trích xuất quy cách"""
        return self.extract_table_info(soup, "Quy cách")
    
    def extract_origin_brand(self, soup: BeautifulSoup) -> str:
        """Trích xuất xuất xứ thương hiệu"""
        return self.extract_table_info(soup, "Xuất xứ thương hiệu")
    
    def extract_manufacturer(self, soup: BeautifulSoup) -> str:
        """Trích xuất nhà sản xuất"""
        return self.extract_table_info(soup, "Nhà sản xuất")
    
    def extract_country_of_manufacture(self, soup: BeautifulSoup) -> str:
        """Trích xuất nước sản xuất"""
        return self.extract_table_info(soup, "Nước sản xuất")
    
    def crawl_category(self, category_url: str, max_products: int = None):
        """Crawl toàn bộ sản phẩm trong một danh mục"""
        self.logger.info(f"Bắt đầu crawl danh mục: {category_url}")
        
        # Lấy danh sách URL sản phẩm
        product_urls = self.get_product_urls(category_url)
        
        if max_products:
            product_urls = product_urls[:max_products]
        
        # Crawl từng sản phẩm
        for url in tqdm(product_urls, desc=f"Crawling {category_url}"):
            product_data = self.crawl_product_detail(url)
            if product_data:
                self.products.append(product_data)
            
            random_delay(*RANDOM_DELAY_RANGE)
        
        self.logger.info(f"Hoàn thành crawl danh mục {category_url}: {len([p for p in self.products if category_url in p.get('url', '')])} sản phẩm mới")
    
    def crawl_subcategories(self, main_category: str, subcategories: list, max_products_per_category: int = None):
        """Crawl tất cả subcategories của một main category"""
        self.logger.info(f"Bắt đầu crawl main category: {main_category}")
        
        for subcategory in subcategories:
            try:
                category_url = f"{main_category}/{subcategory}"
                self.crawl_category(category_url, max_products_per_category)
            except Exception as e:
                self.logger.error(f"Lỗi khi crawl subcategory {subcategory}: {str(e)}")
                continue
    
    def crawl_vitamin_categories(self, max_products_per_category: int = None):
        """Crawl tất cả danh mục vitamin và khoáng chất"""
        from config.settings import VITAMIN_KHOANG_CHAT
        self.crawl_subcategories("thuc-pham-chuc-nang", VITAMIN_KHOANG_CHAT, max_products_per_category)
    
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
        # Crawl danh mục canxi-vitamin-D cụ thể
        crawler.crawl_category("thuc-pham-chuc-nang/canxi-vitamin-D", max_products=10)
        
        # Hoặc crawl tất cả danh mục vitamin
        # crawler.crawl_vitamin_categories(max_products_per_category=5)
        
        # Hoặc crawl một subcategory cụ thể
        # from config.settings import VITAMIN_KHOANG_CHAT
        # crawler.crawl_subcategories("thuc-pham-chuc-nang", VITAMIN_KHOANG_CHAT[:2], max_products_per_category=5)
        
        # Lưu dữ liệu
        crawler.save_data('both')
        
    except KeyboardInterrupt:
        print("\nĐã dừng crawler. Đang lưu dữ liệu...")
        crawler.save_data('both')
    except Exception as e:
        logging.error(f"Lỗi không mong muốn: {str(e)}")
        crawler.save_data('both')
