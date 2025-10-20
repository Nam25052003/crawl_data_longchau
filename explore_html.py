#!/usr/bin/env python3
"""
Script khám phá cấu trúc HTML của Long Châu để tìm CSS selectors đúng
"""
import requests
from bs4 import BeautifulSoup
import sys
import os

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(__file__))

from config.settings import BASE_URL, DEFAULT_HEADERS

def explore_page_structure(url):
    """Khám phá cấu trúc HTML của một trang"""
    print(f"🔍 Exploring: {url}")
    
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Title: {soup.title.string if soup.title else 'No title'}")
        
        # Tìm tất cả các link có chứa từ khóa sản phẩm
        product_keywords = ['san-pham', 'product', 'thuoc', 'item']
        
        print("\n📦 Looking for product links...")
        product_links = []
        
        for keyword in product_keywords:
            links = soup.find_all('a', href=lambda x: x and keyword in x.lower())
            if links:
                print(f"   Found {len(links)} links containing '{keyword}':")
                for i, link in enumerate(links[:5]):  # Chỉ hiển thị 5 link đầu
                    href = link.get('href')
                    text = link.get_text().strip()[:50]
                    if href.startswith('/'):
                        href = BASE_URL + href
                    print(f"     {i+1}. {text} -> {href}")
                    product_links.append(href)
                if len(links) > 5:
                    print(f"     ... and {len(links) - 5} more")
        
        # Tìm các class có thể chứa sản phẩm
        print("\n🎯 Looking for product containers...")
        potential_selectors = [
            '[class*="product"]',
            '[class*="item"]', 
            '[class*="card"]',
            '[class*="box"]',
            '.row > div',
            '.grid > div'
        ]
        
        for selector in potential_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"   {selector}: {len(elements)} elements")
                # Hiển thị class của element đầu tiên
                if elements[0].get('class'):
                    print(f"     Example classes: {' '.join(elements[0].get('class'))}")
        
        # Tìm các thẻ img (có thể là ảnh sản phẩm)
        print("\n🖼️  Looking for images...")
        images = soup.find_all('img')
        product_images = [img for img in images if img.get('src') and any(keyword in img.get('src', '').lower() for keyword in ['product', 'thuoc', 'item'])]
        
        if product_images:
            print(f"   Found {len(product_images)} potential product images")
            for i, img in enumerate(product_images[:3]):
                src = img.get('src')
                alt = img.get('alt', 'No alt')[:30]
                print(f"     {i+1}. {alt} -> {src}")
        
        # Lưu HTML để debug
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"\n💾 Saved HTML to debug_page.html for manual inspection")
        
        return product_links[:5]  # Trả về 5 link sản phẩm đầu tiên
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_product_page(product_url):
    """Test cấu trúc trang sản phẩm"""
    print(f"\n🔍 Testing product page: {product_url}")
    
    try:
        response = requests.get(product_url, headers=DEFAULT_HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Status: {response.status_code}")
        
        # Tìm các element có thể chứa thông tin sản phẩm
        info_selectors = {
            'title': ['h1', '.title', '.product-title', '.name'],
            'price': ['.price', '.cost', '.gia', '[class*="price"]'],
            'description': ['.description', '.desc', '.mo-ta', '.content'],
            'image': ['img[src*="product"]', '.product-image img', '.main-image img']
        }
        
        for info_type, selectors in info_selectors.items():
            print(f"\n📋 Looking for {info_type}...")
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    element = elements[0]
                    if info_type == 'image':
                        content = element.get('src', 'No src')
                    else:
                        content = element.get_text().strip()[:100]
                    print(f"   ✅ {selector}: {content}")
                    break
            else:
                print(f"   ❌ No {info_type} found")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test trang danh mục
    category_url = f"{BASE_URL}/thuoc"
    product_links = explore_page_structure(category_url)
    
    # Test trang sản phẩm nếu tìm thấy
    if product_links:
        test_product_page(product_links[0])
    else:
        print("\n⚠️  No product links found to test")
        
        # Thử test trang chủ
        print("\n🏠 Testing homepage instead...")
        homepage_links = explore_page_structure(BASE_URL)
        if homepage_links:
            test_product_page(homepage_links[0])
