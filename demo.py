#!/usr/bin/env python3
"""
Script demo để test crawler Long Châu
"""
import sys
import os

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(__file__))

from src.crawlers.longchau_crawler import LongChauCrawler

def demo_crawler():
    """Demo crawler với một vài sản phẩm"""
    print("🚀 Bắt đầu demo crawler Long Châu...")
    
    # Tạo thư mục cần thiết
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Khởi tạo crawler
    crawler = LongChauCrawler()
    
    try:
        # Test crawl một danh mục với giới hạn nhỏ
        print("📦 Đang crawl danh mục 'thuoc-khong-ke-don' (tối đa 1 trang, 5 sản phẩm)...")
        crawler.crawl_category("thuoc-khong-ke-don", max_pages=1, max_products=5)
        
        # Lưu dữ liệu
        crawler.save_data('both')
        
        print(f"✅ Demo hoàn thành! Đã crawl {len(crawler.products)} sản phẩm.")
        print("📁 Kiểm tra thư mục 'data/' để xem kết quả.")
        
    except Exception as e:
        print(f"❌ Lỗi trong demo: {str(e)}")
        print("💡 Có thể cần điều chỉnh CSS selectors trong crawler.")

if __name__ == "__main__":
    demo_crawler()
