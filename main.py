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
from config.settings import CATEGORIES

def main():
    parser = argparse.ArgumentParser(description='Crawler cho website Long Châu')
    parser.add_argument('--category', '-c', 
                       choices=CATEGORIES + ['all'], 
                       default='all',
                       help='Danh mục cần crawl (mặc định: all)')
    parser.add_argument('--max-pages', '-p', 
                       type=int, 
                       default=5,
                       help='Số trang tối đa mỗi danh mục (mặc định: 5)')
    parser.add_argument('--max-products', '-n', 
                       type=int, 
                       help='Số sản phẩm tối đa mỗi danh mục')
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
        if args.category == 'all':
            print("🚀 Bắt đầu crawl tất cả danh mục...")
            crawler.crawl_all_categories(
                max_pages_per_category=args.max_pages,
                max_products_per_category=args.max_products
            )
        else:
            print(f"🚀 Bắt đầu crawl danh mục: {args.category}")
            crawler.crawl_category(
                args.category,
                max_pages=args.max_pages,
                max_products=args.max_products
            )
        
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
