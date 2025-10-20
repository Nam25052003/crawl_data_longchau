#!/usr/bin/env python3
"""
Script tìm sản phẩm thực tế trên Long Châu
"""
import requests
from bs4 import BeautifulSoup
import sys
import os
import re

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(__file__))

from config.settings import BASE_URL, DEFAULT_HEADERS

def find_actual_products():
    """Tìm sản phẩm thực tế"""
    
    # Thử các URL có thể chứa sản phẩm
    test_urls = [
        f"{BASE_URL}/thuoc/thuoc-khang-sinh-khang-nam",
        f"{BASE_URL}/thuoc/thuoc-tim-mach-and-mau", 
        f"{BASE_URL}/thuoc/thuoc-tieu-hoa-and-gan-mat",
        f"{BASE_URL}/thuc-pham-chuc-nang",
        f"{BASE_URL}/cham-soc-ca-nhan"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"✅ Status: {response.status_code}")
            
            # Tìm tất cả các link
            links = soup.find_all('a', href=True)
            product_links = []
            
            for link in links:
                href = link.get('href')
                text = link.get_text().strip()
                
                # Tìm link có pattern giống sản phẩm
                if href and any(pattern in href for pattern in ['/san-pham/', '/product/', '/thuoc/']):
                    if href.startswith('/'):
                        href = BASE_URL + href
                    
                    # Loại bỏ link danh mục
                    if not any(skip in href for skip in ['/thuoc?', '/thuoc/tra-cuu', '/thuoc/thuoc-']):
                        if len(text) > 5 and len(text) < 100:  # Text hợp lý
                            product_links.append((text, href))
            
            if product_links:
                print(f"📦 Found {len(product_links)} potential products:")
                for i, (text, href) in enumerate(product_links[:5]):
                    print(f"   {i+1}. {text[:50]} -> {href}")
                
                # Test trang sản phẩm đầu tiên
                if product_links:
                    test_product_detail(product_links[0][1])
                    return product_links[0][1]  # Trả về URL sản phẩm đầu tiên
            else:
                print("❌ No product links found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

def test_product_detail(product_url):
    """Test chi tiết trang sản phẩm"""
    print(f"\n🔍 Testing product detail: {product_url}")
    
    try:
        response = requests.get(product_url, headers=DEFAULT_HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Status: {response.status_code}")
        
        # Tìm thông tin sản phẩm với nhiều selector khác nhau
        selectors_to_test = {
            'title': [
                'h1',
                '.product-title', 
                '.title',
                '[class*="title"]',
                '.name',
                '.product-name'
            ],
            'price': [
                '.price',
                '[class*="price"]',
                '.cost',
                '.gia',
                '[class*="gia"]',
                'span[class*="price"]',
                'div[class*="price"]'
            ],
            'image': [
                '.product-image img',
                '.main-image img', 
                'img[alt*="product"]',
                'img[src*="product"]',
                '.image img',
                'img'
            ]
        }
        
        found_info = {}
        
        for info_type, selectors in selectors_to_test.items():
            print(f"\n📋 Testing {info_type} selectors:")
            for selector in selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        element = elements[0]
                        if info_type == 'image':
                            content = element.get('src', element.get('data-src', 'No src'))
                        else:
                            content = element.get_text().strip()
                        
                        if content and len(content) > 0:
                            print(f"   ✅ {selector}: {content[:100]}")
                            if info_type not in found_info:
                                found_info[info_type] = (selector, content)
                            break
                except Exception as e:
                    continue
            
            if info_type not in found_info:
                print(f"   ❌ No {info_type} found")
        
        # Lưu thông tin tìm được
        if found_info:
            print(f"\n✅ Successfully found selectors:")
            for info_type, (selector, content) in found_info.items():
                print(f"   {info_type}: {selector}")
        
        return found_info
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def search_for_products():
    """Tìm sản phẩm qua tìm kiếm"""
    search_terms = ['paracetamol', 'vitamin', 'thuoc ho']
    
    for term in search_terms:
        print(f"\n🔍 Searching for: {term}")
        search_url = f"{BASE_URL}/tim-kiem?s={term}"
        
        try:
            response = requests.get(search_url, headers=DEFAULT_HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"✅ Status: {response.status_code}")
            
            # Tìm link sản phẩm trong kết quả tìm kiếm
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                text = link.get_text().strip()
                
                if href and 'san-pham' in href and len(text) > 10:
                    if href.startswith('/'):
                        href = BASE_URL + href
                    print(f"📦 Found: {text[:50]} -> {href}")
                    return href
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    # Thử tìm sản phẩm từ danh mục
    product_url = find_actual_products()
    
    # Nếu không tìm thấy, thử tìm kiếm
    if not product_url:
        print("\n🔍 Trying search...")
        product_url = search_for_products()
    
    if product_url:
        print(f"\n✅ Found working product URL: {product_url}")
    else:
        print("\n❌ Could not find any product URLs")
