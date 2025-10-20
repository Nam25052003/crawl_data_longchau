# Long Châu Crawler 🏥

Công cụ crawl dữ liệu sản phẩm từ website Nhà thuốc Long Châu (nhathuoclongchau.com.vn).

## ✨ Tính năng

- ✅ Crawl thông tin sản phẩm từ các danh mục khác nhau
- ✅ Trích xuất tên sản phẩm, URL, ảnh và thông tin chi tiết
- ✅ Hỗ trợ xuất dữ liệu ra JSON và CSV
- ✅ Có retry logic và error handling
- ✅ Tuân thủ rate limiting để không làm quá tải server
- ✅ Logging chi tiết để debug

## 🚀 Cài đặt nhanh

### Bước 1: Cài đặt dependencies
```bash
# Sử dụng Python system (khuyến nghị)
pip3 install requests beautifulsoup4 lxml tqdm fake-useragent python-dotenv --user

# Hoặc tạo virtual environment (tùy chọn)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Bước 2: Chạy crawler
```bash
# Crawl demo với 2 sản phẩm
python3 main.py -c thuoc -p 1 -n 2

# Crawl tất cả danh mục
python3 main.py

# Xem tất cả tùy chọn
python3 main.py --help
```

## 📖 Hướng dẫn sử dụng chi tiết

### Các lệnh cơ bản

```bash
# Crawl một danh mục cụ thể
python3 main.py --category thuoc

# Giới hạn số trang và sản phẩm
python3 main.py -c thuc-pham-chuc-nang --max-pages 3 --max-products 50

# Chỉ xuất JSON
python3 main.py -c cham-soc-ca-nhan --output-format json

# Hiển thị log chi tiết
python3 main.py -c thuoc --verbose
```

### Các danh mục có sẵn

| Danh mục | Mô tả |
|----------|--------|
| `thuoc` | Thuốc và dược phẩm |
| `thuc-pham-chuc-nang` | Thực phẩm chức năng |
| `cham-soc-ca-nhan` | Chăm sóc cá nhân |

### Tùy chọn command line

| Tham số | Mô tả | Mặc định |
|---------|--------|----------|
| `--category, -c` | Danh mục cần crawl | `all` |
| `--max-pages, -p` | Số trang tối đa mỗi danh mục | `5` |
| `--max-products, -n` | Số sản phẩm tối đa mỗi danh mục | Không giới hạn |
| `--output-format, -f` | Định dạng output (json/csv/both) | `both` |
| `--verbose, -v` | Hiển thị log chi tiết | `false` |

## 📁 Cấu trúc dự án

```
craw_data_longchau/
├── main.py                 # Script chính để chạy crawler
├── demo.py                 # Script demo với ít sản phẩm
├── requirements.txt        # Dependencies Python
├── env.example            # File cấu hình mẫu
├── README.md              # Hướng dẫn này
├── config/
│   └── settings.py        # Cấu hình crawler
├── src/
│   ├── crawlers/
│   │   └── longchau_crawler.py  # Crawler chính
│   └── utils/
│       └── helpers.py     # Các hàm tiện ích
├── data/                  # Thư mục chứa dữ liệu output
└── logs/                  # Thư mục chứa log files
```

## 📊 Dữ liệu output

### Thông tin được crawl

- **Thông tin cơ bản**: Tên sản phẩm, URL
- **Giá cả**: Giá hiện tại, giá gốc, giảm giá
- **Mô tả**: Mô tả sản phẩm, thành phần, cách sử dụng
- **Phân loại**: Thương hiệu, danh mục
- **Trạng thái**: Tình trạng còn hàng
- **Đánh giá**: Số sao, số lượt đánh giá
- **Media**: Danh sách ảnh sản phẩm
- **Metadata**: Thời gian crawl

### Định dạng file

**JSON**: `data/longchau_products_YYYYMMDD_HHMMSS.json`
```json
{
  "url": "https://nhathuoclongchau.com.vn/thuoc/...",
  "name": "Thuốc ABC 500mg...",
  "price": 25000.0,
  "description": "Mô tả sản phẩm...",
  "images": ["https://cdn.nhathuoclongchau.com.vn/..."],
  "crawled_at": "2025-10-20T14:24:07"
}
```

**CSV**: `data/longchau_products_YYYYMMDD_HHMMSS.csv`

## ⚙️ Cấu hình

### Chỉnh sửa cấu hình trong `config/settings.py`:

```python
# Thời gian delay giữa các request (giây)
REQUEST_DELAY = 1
RANDOM_DELAY_RANGE = (0.5, 2.0)

# Số lần retry khi request thất bại
MAX_RETRIES = 3

# Danh sách danh mục cần crawl
CATEGORIES = [
    "thuoc",
    "thuc-pham-chuc-nang", 
    "cham-soc-ca-nhan"
]
```

### Sử dụng file .env (tùy chọn):

```bash
cp env.example .env
# Chỉnh sửa các giá trị trong file .env
```

## 🔧 Tùy chỉnh nâng cao

### Thêm danh mục mới

1. Kiểm tra URL danh mục có hoạt động:
```bash
python3 test_urls.py
```

2. Thêm vào `CATEGORIES` trong `config/settings.py`:
```python
CATEGORIES = [
    "thuoc",
    "danh-muc-moi",  # Thêm danh mục mới
    # ...
]
```

### Tùy chỉnh CSS selectors

Chỉnh sửa các method `extract_*` trong `LongChauCrawler` class để phù hợp với cấu trúc HTML:

```python
def extract_price(self, soup: BeautifulSoup) -> float:
    selectors = ['.price', '[class*="price"]', '.new-selector']
    # ...
```

### Khám phá cấu trúc HTML

```bash
# Khám phá cấu trúc trang
python3 explore_html.py

# Tìm sản phẩm thực tế
python3 find_products.py
```

## 📝 Ví dụ sử dụng

### Crawl nhanh cho demo
```bash
python3 demo.py
```

### Crawl production với nhiều sản phẩm
```bash
python3 main.py -c thuoc -p 10 -n 100 --verbose
```

### Crawl tất cả danh mục với giới hạn
```bash
python3 main.py --max-pages 5 --max-products 50
```

## 🐛 Troubleshooting

### Lỗi thường gặp:

1. **ModuleNotFoundError**: 
   ```bash
   pip3 install requests beautifulsoup4 lxml --user
   ```

2. **Không tìm thấy sản phẩm**: 
   - Kiểm tra URL danh mục
   - Chạy `python3 test_urls.py` để debug

3. **Request timeout**: 
   - Kiểm tra kết nối mạng
   - Tăng timeout trong `config/settings.py`

4. **Blocked by website**: 
   - Tăng delay giữa các request
   - Thay đổi User-Agent

### Debug:

```bash
# Chạy với log chi tiết
python3 main.py --verbose

# Kiểm tra log files
tail -f logs/crawler_*.log

# Khám phá cấu trúc HTML
python3 explore_html.py
```

## 📄 Lưu ý quan trọng

1. **Tuân thủ robots.txt**: Kiểm tra file robots.txt của website
2. **Respect rate limiting**: Sử dụng delay phù hợp
3. **Cập nhật selectors**: CSS selectors có thể thay đổi
4. **Backup dữ liệu**: Dữ liệu được lưu với timestamp
5. **Chỉ dùng cho mục đích học tập**: Tuân thủ Terms of Service

## 🎯 Kết quả mong đợi

Sau khi chạy thành công, bạn sẽ có:

- ✅ File JSON với dữ liệu structured
- ✅ File CSV để phân tích trong Excel
- ✅ Log files để debug
- ✅ Thông tin sản phẩm chi tiết

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch  
5. Tạo Pull Request

---

**Lưu ý**: Crawler này được tạo cho mục đích học tập và nghiên cứu. Vui lòng tuân thủ các quy định pháp luật và chính sách của website khi sử dụng.
