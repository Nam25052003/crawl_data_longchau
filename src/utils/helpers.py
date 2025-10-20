"""
Các hàm tiện ích cho crawler
"""
import time
import random
import logging
import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Any
import requests
from fake_useragent import UserAgent

def setup_logging(log_file: str = None) -> logging.Logger:
    """Thiết lập logging"""
    if not log_file:
        log_file = f"logs/crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Tạo thư mục logs nếu chưa có
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def random_delay(min_delay: float = 0.5, max_delay: float = 2.0):
    """Tạo delay ngẫu nhiên giữa các request"""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def get_random_user_agent() -> str:
    """Lấy User-Agent ngẫu nhiên"""
    try:
        ua = UserAgent()
        return ua.random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def save_to_json(data: List[Dict], filename: str):
    """Lưu dữ liệu vào file JSON"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_to_csv(data: List[Dict], filename: str):
    """Lưu dữ liệu vào file CSV"""
    if not data:
        return
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def make_request(url: str, headers: Dict = None, retries: int = 3) -> requests.Response:
    """Thực hiện request với retry logic"""
    if not headers:
        headers = {'User-Agent': get_random_user_agent()}
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff

def clean_text(text: str) -> str:
    """Làm sạch text"""
    if not text:
        return ""
    return text.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

def format_price(price_text: str) -> float:
    """Chuyển đổi text giá thành số"""
    if not price_text:
        return 0.0
    
    # Loại bỏ ký tự không phải số
    price_clean = ''.join(filter(str.isdigit, price_text))
    try:
        return float(price_clean)
    except:
        return 0.0

def create_output_filename(prefix: str, extension: str = 'json') -> str:
    """Tạo tên file output với timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"data/{prefix}_{timestamp}.{extension}"
