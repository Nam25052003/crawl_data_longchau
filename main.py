#!/usr/bin/env python3
"""
Script chính để chạy crawler Long Châu
"""
import argparse
import sys
import os

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(__file__))

from src.crawlers.longchau_crawler import LongChauCrawler
from config.settings import *

def main():
    parser = argparse.ArgumentParser(description='Crawler cho website Long Châu')
    
    # Các tùy chọn crawl
    parser.add_argument('--category-url', '-u', 
                       type=str,
                       help='URL danh mục cụ thể (VD: thuc-pham-chuc-nang/canxi-vitamin-D)')
    parser.add_argument('--mode', '-m',
                       choices=['single', 'vitamin', 'subcategory', 'all'],
                       default='single',
                       help='Chế độ crawl (mặc định: single)')
    parser.add_argument('--main-category', 
                       type=str,
                       help='Danh mục chính (VD: thuc-pham-chuc-nang)')
    parser.add_argument('--subcategories',
                       type=str, 
                       nargs='+',
                       help='Danh sách subcategories')
    
    # Các tùy chọn giới hạn
    parser.add_argument('--max-products', '-n', 
                       type=int, 
                       default=10,
                       help='Số sản phẩm tối đa mỗi danh mục (mặc định: 10)')
    parser.add_argument('--max-products-per-category', 
                       type=int,
                       help='Số sản phẩm tối đa mỗi subcategory')
    
    # Các tùy chọn output
    parser.add_argument('--output-format', '-f', 
                       choices=['json', 'csv', 'both'], 
                       default='both',
                       help='Định dạng file output (mặc định: both)')
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='Hiển thị log chi tiết')
    
    args = parser.parse_args()
    
    # Tạo thư mục cần thiết
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Khởi tạo crawler
    crawler = LongChauCrawler()
    
    try:
        # Reset categories trước khi bắt đầu crawl mới
        crawler.reset_categories()
        if args.mode == 'single':
            if not args.category_url:
                print("❌ Cần cung cấp --category-url cho chế độ single")
                print("VD: python main.py --mode single --category-url thuc-pham-chuc-nang/canxi-vitamin-D")
                return
            
            print(f"🚀 Crawl danh mục: {args.category_url}")
            crawler.crawl_category(args.category_url, max_products=args.max_products)
            
        elif args.mode == 'vitamin':
            print("🚀 Crawl tất cả danh mục vitamin và khoáng chất...")
            crawler.crawl_vitamin_categories(max_products_per_category=args.max_products_per_category or args.max_products)
            
        elif args.mode == 'subcategory':
            if not args.main_category or not args.subcategories:
                print("❌ Cần cung cấp --main-category và --subcategories cho chế độ subcategory")
                print("VD: python main.py --mode subcategory --main-category thuc-pham-chuc-nang --subcategories canxi-vitamin-D vitamin-tong-hop")
                return
            
            print(f"🚀 Crawl subcategories của {args.main_category}...")
            crawler.crawl_subcategories(
                args.main_category, 
                args.subcategories,
                max_products_per_category=args.max_products_per_category or args.max_products
            )
            
        elif args.mode == 'all':
            print("🚀 Crawl tất cả danh mục (chưa implement - sử dụng mode khác)")
            return
        
        # Lưu dữ liệu
        crawler.save_data(args.output_format)
        print("✅ Hoàn thành crawler!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Đã dừng crawler. Đang lưu dữ liệu hiện có...")
        crawler.save_data(args.output_format)
        print("💾 Đã lưu dữ liệu.")
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        crawler.save_data(args.output_format)
        sys.exit(1)

if __name__ == "__main__":
    main()
