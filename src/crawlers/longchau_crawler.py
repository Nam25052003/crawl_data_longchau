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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from config.settings import *
from src.utils.helpers import *

class LongChauCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.logger = setup_logging()
        self.products = []
        self.driver = None
    
    def __del__(self):
        """Destructor để đảm bảo Selenium driver được đóng"""
        self.close_selenium_driver()
    
    def init_selenium_driver(self):
        """Khởi tạo Selenium WebDriver"""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Chạy ẩn browser
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={USER_AGENT}')
            
            try:
                # Sử dụng webdriver-manager để tự động tải ChromeDriver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.implicitly_wait(10)
                self.logger.info("Đã khởi tạo Selenium WebDriver")
            except Exception as e:
                self.logger.error(f"Lỗi khởi tạo WebDriver: {str(e)}")
                raise
    
    def close_selenium_driver(self):
        """Đóng Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("Đã đóng Selenium WebDriver")
        
    def get_product_urls(self, category_url: str) -> List[str]:
        """Lấy danh sách URL sản phẩm từ một danh mục với xử lý nút 'Xem thêm'"""
        product_urls = []
        
        try:
            url = f"{BASE_URL}/{category_url}"
            self.logger.info(f"Crawling category page: {url}")
            
            # Khởi tạo Selenium driver
            self.init_selenium_driver()
            self.driver.get(url)
            
            # Đợi trang load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Click vào nút "Xem thêm" cho đến khi không còn nút nào
            max_clicks = 20  # Giới hạn số lần click để tránh vòng lặp vô tận
            click_count = 0
            
            while click_count < max_clicks:
                try:
                    # Tìm nút "Xem thêm"
                    see_more_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(.//span, 'Xem thêm') and contains(.//span, 'sản phẩm')]"))
                    )
                    
                    # Scroll đến nút
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
                    time.sleep(1)
                    
                    # Click vào nút
                    see_more_button.click()
                    click_count += 1
                    
                    self.logger.info(f"Đã click 'Xem thêm' lần {click_count}")
                    
                    # Đợi content load
                    time.sleep(2)
                    
                except TimeoutException:
                    # Không còn nút "Xem thêm"
                    self.logger.info("Không còn nút 'Xem thêm', đã load tất cả sản phẩm")
                    break
                except Exception as e:
                    self.logger.warning(f"Lỗi khi click 'Xem thêm': {str(e)}")
                    break
            
            # Lấy HTML sau khi đã load tất cả sản phẩm
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Tìm grid sản phẩm chính - grid có class 'grid-cols-2' và 'md:grid-cols-4'
            product_grid = None
            all_grids = soup.find_all('div', class_=True)
            
            for div in all_grids:
                classes = div.get('class', [])
                if (isinstance(classes, list) and 
                    'grid' in classes and 
                    'grid-cols-2' in classes and 
                    'md:grid-cols-4' in classes):
                    product_grid = div
                    break
            
            if product_grid:
                # Lấy tất cả product links từ grid chính
                all_links_in_grid = product_grid.find_all('a', href=lambda x: x and '.html' in x)
                
                # Lọc chỉ lấy links trong category hiện tại
                category_path = f"/{category_url.split('/')[0]}/"  # Ví dụ: /thuc-pham-chuc-nang/
                
                seen_urls = set()
                for link in all_links_in_grid:
                    href = link.get('href')
                    if (href and 
                        category_path in href and 
                        href.count('/') >= 2):  # Đảm bảo là URL sản phẩm chi tiết
                        
                        if href.startswith('/'):
                            href = BASE_URL + href
                        
                        # Chỉ thêm nếu chưa thấy URL này
                        if href not in seen_urls:
                            seen_urls.add(href)
                            product_urls.append(href)
                
                self.logger.info(f"Tìm thấy grid sản phẩm chính với {len(product_urls)} sản phẩm unique")
            else:
                # Fallback: lấy tất cả unique links trong category
                self.logger.warning("Không tìm thấy grid sản phẩm chính, sử dụng fallback")
                
                category_path = f"/{category_url.split('/')[0]}/"
                all_links = soup.find_all('a', href=lambda x: x and '.html' in x and category_path in x)
                
                seen_urls = set()
                for link in all_links:
                    href = link.get('href')
                    if href and href.count('/') >= 2:
                        if href.startswith('/'):
                            href = BASE_URL + href
                        
                        if href not in seen_urls:
                            seen_urls.add(href)
                            product_urls.append(href)
                
                self.logger.info(f"Fallback: tìm thấy {len(product_urls)} sản phẩm unique")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi crawl danh mục {category_url}: {str(e)}")
        finally:
            # Đóng Selenium driver
            self.close_selenium_driver()
        
        # Filter chỉ lấy URL sản phẩm thực sự (đã loại bỏ duplicate ở trên)
        filtered_urls = [url for url in product_urls if self.is_product_url(url)]
        
        self.logger.info(f"Tìm thấy {len(filtered_urls)} sản phẩm trong danh mục {category_url} (sau khi load tất cả)")
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
        import json
        import re
        
        # Tìm trong JSON scripts trước (nguồn chính xác nhất)
        scripts = soup.find_all('script', type='application/json')
        for script in scripts:
            try:
                script_content = script.string
                if script_content:
                    # Thử parse JSON
                    try:
                        data = json.loads(script_content)
                        brand_info = self._find_brand_in_json(data)
                        if brand_info:
                            return clean_text(brand_info)
                    except:
                        # Nếu không parse được JSON, tìm bằng regex
                        brand_matches = re.findall(r'"brand[^"]*":\s*"([^"]+)"', script_content, re.IGNORECASE)
                        if brand_matches:
                            return clean_text(brand_matches[0])
                        
                        manufacturer_matches = re.findall(r'"manufacturer[^"]*":\s*"([^"]+)"', script_content, re.IGNORECASE)
                        if manufacturer_matches:
                            return clean_text(manufacturer_matches[0])
            except:
                continue
        
        # Tìm trong structured data (JSON-LD)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                brand_info = self._find_brand_in_json(data)
                if brand_info:
                    return clean_text(brand_info)
            except:
                continue
        
        # Tìm trong table info (sử dụng extract_table_info)
        brand_from_table = self.extract_table_info(soup, "Thương hiệu")
        if brand_from_table:
            return brand_from_table
        
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
    
    def _find_brand_in_json(self, data, path=""):
        """Tìm brand trong JSON structure"""
        if isinstance(data, dict):
            for key, value in data.items():
                if 'brand' in key.lower() or 'manufacturer' in key.lower():
                    if isinstance(value, str):
                        return value
                    elif isinstance(value, dict) and 'name' in value:
                        return value['name']
                
                # Đệ quy tìm trong nested objects
                result = self._find_brand_in_json(value, f"{path}.{key}")
                if result:
                    return result
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                result = self._find_brand_in_json(item, f"{path}[{i}]")
                if result:
                    return result
        
        return None
    
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
        """Trích xuất danh sách ảnh sản phẩm từ gallery carousel"""
        images = []
        
        # 1. Trích xuất từ carousel gallery chính
        carousel_gallery = soup.find('div', class_='carousel-gallery-list')
        if carousel_gallery:
            # Lấy tất cả ảnh trong carousel
            gallery_imgs = carousel_gallery.find_all('img', class_='gallery-img')
            for img in gallery_imgs:
                src = img.get('src')
                srcset = img.get('srcset')
                
                # Ưu tiên lấy URL chất lượng cao từ srcset
                if srcset:
                    # Lấy URL 2x (chất lượng cao) từ srcset
                    srcset_parts = srcset.split(',')
                    for part in srcset_parts:
                        if '2x' in part:
                            src = part.split(' ')[0].strip()
                            break
                    else:
                        # Nếu không có 2x, lấy URL đầu tiên
                        src = srcset_parts[0].split(' ')[0].strip()
                
                if src and self.is_product_image(src):
                    # Chuyển đổi sang full size nếu cần
                    full_size_src = self.convert_to_full_size_image(src)
                    images.append(full_size_src)
        
        # 2. Trích xuất từ modal gallery (nếu có)
        # Tìm các ảnh trong modal lightbox gallery
        modal_thumbs = soup.find_all('div', class_='lg-thumb-item')
        for thumb in modal_thumbs:
            img = thumb.find('img')
            if img:
                src = img.get('src')
                if src and self.is_product_image(src):
                    # Chuyển đổi từ thumbnail sang full size
                    full_size_src = self.convert_to_full_size_image(src)
                    images.append(full_size_src)
        
        # 3. Tìm ảnh từ các script JSON data (nếu có)
        # Long Châu thường embed dữ liệu ảnh trong script tags
        script_tags = soup.find_all('script', type='application/json')
        for script in script_tags:
            try:
                import json
                import re
                script_content = script.get_text()
                # Tìm URLs ảnh trong JSON
                image_urls = re.findall(r'https://cdn\.nhathuoclongchau\.com\.vn/[^"]*\.(?:jpg|jpeg|png|webp)', script_content)
                for url in image_urls:
                    if self.is_product_image(url):
                        full_size_url = self.convert_to_full_size_image(url)
                        images.append(full_size_url)
            except:
                continue
        
        # 4. Fallback: Tìm ảnh sản phẩm khác
        if not images:
            product_imgs = soup.find_all('img')
            for img in product_imgs:
                src = img.get('src') or img.get('data-src')
                if src and self.is_product_image(src):
                    full_size_src = self.convert_to_full_size_image(src)
                    images.append(full_size_src)
        
        # Loại bỏ duplicate và return
        return list(dict.fromkeys(images))  # Giữ thứ tự và loại bỏ duplicate
    
    def is_product_image(self, src: str) -> bool:
        """Kiểm tra xem URL có phải là ảnh sản phẩm không"""
        if not src:
            return False
        
        src_lower = src.lower()
        
        # Loại trừ các ảnh không phải sản phẩm trước
        exclude_patterns = [
            'logo', 'banner', 'icon', 'badge', 'smalls/',
            'facebook', 'zalo', 'download', 'payment',
            'visa', 'master', 'momo', 'napas', 'vnpay',
            'apple_pay', 'amex', 'jcb', 'bo_cong_thuong',
            'legit_', 'dmca_', 'search_', 'menu_',
            'truyen_thong', 'tin_khuyen_mai', 'chuyen_trang',
            'deep_link', 'goc_suc_khoe', 'short_video',
            'cup_', 'benh_', 'thuong_hieu', 'danh_muc',
            'kiem_tra_suc_khoe', 'header_', 'footer_'
        ]
        
        for exclude in exclude_patterns:
            if exclude in src_lower:
                return False
        
        # Kiểm tra các pattern của ảnh sản phẩm Long Châu
        # 1. URL từ CDN chính của Long Châu
        if 'cms-prod.s3-sgn09.fptcloud.com' in src_lower:
            # 2. Pattern ảnh sản phẩm (DSC_ là pattern chụp sản phẩm)
            if 'dsc_' in src_lower:
                return True
            
            # 3. Tên sản phẩm cụ thể trong URL
            product_name_patterns = [
                'lineabon', 'omexxel', 'calci', 'vitamin', 'nutrimed',
                'nutrigrow', 'osteocare', 'vitabiotics', 'anica',
                'pharma', 'ergopharm', 'nordic', 'excelife'
            ]
            
            for pattern in product_name_patterns:
                if pattern in src_lower:
                    return True
            
            # 4. Kiểm tra số sản phẩm (pattern 00XXXXXX)
            import re
            if re.search(r'00\d{6}', src):
                return True
        
        return False
    
    def convert_to_full_size_image(self, thumbnail_url: str) -> str:
        """Chuyển đổi URL thumbnail thành URL full size"""
        if not thumbnail_url:
            return thumbnail_url
        
        # Thay thế kích thước thumbnail bằng kích thước lớn hơn
        # Pattern: /unsafe/150x0/ -> /unsafe/768x0/ hoặc /unsafe/1024x0/
        if '/unsafe/150x0/' in thumbnail_url:
            return thumbnail_url.replace('/unsafe/150x0/', '/unsafe/768x0/')
        elif '/unsafe/375x0/' in thumbnail_url:
            return thumbnail_url.replace('/unsafe/375x0/', '/unsafe/768x0/')
        elif '/unsafe/https://' in thumbnail_url:
            # Fix malformed URLs: /unsafe/https://... -> /unsafe/768x0/filters:quality(90)/https://...
            return thumbnail_url.replace('/unsafe/https://', '/unsafe/768x0/filters:quality(90)/https://')
        
        return thumbnail_url
    
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
        import re
        
        # Tìm tất cả container có chứa từ 'đánh giá'
        rating_containers = soup.find_all(text=lambda x: x and 'đánh giá' in x)
        
        for text_node in rating_containers:
            parent = text_node.parent
            if parent:
                full_text = parent.get_text().strip()
                
                # Thử các pattern khác nhau để tìm rating
                patterns = [
                    r'(\d+(?:\.\d+)?)\s*\(',  # X.X (trước dấu ngoặc) - pattern tốt nhất
                    r'(\d+(?:\.\d+)?)\s*sao',  # X.X sao
                    r'(\d+(?:\.\d+)?)\s*/',  # X.X/5
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, full_text)
                    if match:
                        try:
                            rating_val = float(match.group(1))
                            # Kiểm tra xem có phải rating hợp lệ không (0-5)
                            if 0 <= rating_val <= 5:
                                return rating_val
                        except:
                            continue
        
        # Fallback: tìm trong các container flex items-center
        rating_containers = soup.find_all('div', class_='flex items-center')
        for container in rating_containers:
            rating_text = container.get_text()
            if 'đánh giá' in rating_text or 'sao' in rating_text:
                # Sử dụng pattern trước dấu ngoặc
                match = re.search(r'(\d+(?:\.\d+)?)\s*\(', rating_text)
                if match:
                    try:
                        rating_val = float(match.group(1))
                        if 0 <= rating_val <= 5:
                            return rating_val
                    except:
                        continue
        
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
