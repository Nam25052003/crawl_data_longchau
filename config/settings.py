"""
Cấu hình cho crawler Long Châu
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Cấu hình cơ bản
BASE_URL = "https://nhathuoclongchau.com.vn"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Cấu hình delay giữa các request (giây)
REQUEST_DELAY = 1
RANDOM_DELAY_RANGE = (0.5, 2.0)

# Cấu hình retry
MAX_RETRIES = 3
RETRY_DELAY = 2

# Cấu hình output
OUTPUT_DIR = "data"
LOG_DIR = "logs"

# Cấu hình Selenium (nếu cần)
SELENIUM_TIMEOUT = 10
HEADLESS_MODE = True

# Headers mặc định
DEFAULT_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Danh sách các danh mục cần crawl (có thể tùy chỉnh)
CATEGORIES = [
    "thuc-pham-chuc-nang",
    "duoc-my-pham", 
    "thuoc",
    "cham-soc-ca-nhan",
    "trang-thiet-bi-y-te"
]

# sub CATEGORIES "thuc-pham-chuc-nang"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat
THUC_PHAM_CHUC_NANG = [
    "vitamin-khoang-chat",
    "sinh-ly-noi-tiet-to",
    "cai-thien-tang-cuong-chuc-nang",
    "ho-tro-dieu-tri",
    "ho-tro-tieu-hoa",
    "than-kinh-nao",
    "lam-dep",
    "tim-mach-huyet-ap",
    "dinh-duong"
]

# sub THUC_PHAM_CHUC_NANG "vitamin-khoang-chat"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/canxi-vitamin-D
VITAMIN_KHOANG_CHAT = [
    "canxi-vitamin-D",
    "vitamin-tong-hop",
    "dau-ca-omega-3-dha",
    "vitamin-c",
    "sat-axit-folic",
    "vitamin-e",
    "kem-magie"
]

# sub THUC_PHAM_CHUC_NANG "sinh-ly-noi-tiet-to"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/sinh-ly-nam
SINH_LY_NOI_TIET_TO = [
    "sinh-ly-nam",
    "suc-khoe-tinh-duc",
    "can-bang-noi-tiet-to",
    "sinh-ly-nu",
    "ho-tro-man-kinh"
]

# sub THUC_PHAM_CHUC_NANG "cai-thien-tang-cuong-chuc-nang"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/chuc-nang-gan
CAI_THIEN_TANG_CUONG_CHUC_NANG = [
    "chuc-nang-gan",
    "ho-tro-mien-dich-tang-suc-de-khang",
    "bao-ve-mat",
    "ho-tro-trao-doi-chat",
    "giai-ruou",
    "chong-lao-hoa"
]

# sub THUC_PHAM_CHUC_NANG "ho-tro-dieu-tri"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/xuong-khop
HO_TRO_DIEU_TRI = [
    "xuong-khop",
    "suc-khoe-duong-ho-hap-ho-xoang",
    "than-tien-liet-tuyen",
    "tri",
    "gout",
    "tieu-duong",
    "ung-thu"
]


# sub THUC_PHAM_CHUC_NANG "ho-tro-tieu-hoa"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/da-day-ta-trang
HO_TRO_TIEU_HOA =[
    "da-day-ta-trang",
    "tao-bon",
    "vi-sinh-probiotic",
    "dai-trang",
    "kho-tieu"
]

# sub THUC_PHAM_CHUC_NANG "than-kinh-nao"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/bo-nao-cai-thien-tri-nho
THAN_KINH_NAO = [
    "bo-nao-cai-thien-tri-nho",
    "ho-tro-giac-ngu-ngon",
    "tuan-hoan-mau",
    "kiem-soat-cang-thang",
    "hoat-huyet"
]

# sub THUC_PHAM_CHUC_NANG "lam-dep"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/da
LAM_DEP = [
    "da",
    "ho-tro-giam-can-giam-mo",
    "toc"
]

# sub THUC_PHAM_CHUC_NANG "tim-mach-huyet-ap"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/cholesterol
TIM_MACH_HUYET_AP = [
    "cholesterol",
    "huyet-ap",
    "tinh-mach"
]

# sub THUC_PHAM_CHUC_NANG "dinh-duong"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/sua
DINH_DUONG = [
    "sua",
    "dinh-duong-tre-em"
]

#==================================
# sub CATEGORIES "duoc-my-pham"
# EXAMP URL : https://nhathuoclongchau.com.vn/duoc-my-pham/cham-soc-da-mat
DUOC_MY_PHAM = [
    "cham-soc-da-mat",
    "cham-soc-co-the",
    "giai-phap-lan-da",
    "cham-soc-toc-da-dau",
    "my-pham-trang-diem",
    "cham-soc-da-vung-mat",
    "san-pham-tu-thien-nhien"
]

# sub DUOC_MY_PHAM "cham-soc-da-mat"
# EXAMP URL : https://nhathuoclongchau.com.vn/duoc-my-pham/sua-rua-mat-kem-gel-sua
CHAM_SOC_DA_MAT = [
    "sua-rua-mat-kem-gel-sua",
    "chong-nang-da-mat",
    "duong-da-mat",
    "mat-na",
    "serum-essence-hoac-ampoule",
    "toner-nuoc-hoa-hong-lotion",
    "tay-te-bao-chet",
    "xit-khoang",
    "nuoc-tay-trang"
]

# sub DUOC_MY_PHAM "cham-soc-co-the"
# EXAMP URL :   https://nhathuoclongchau.com.vn/duoc-my-pham/sua-tam-xa-bong
CHAM_SOC_CO_THE = [
    "sua-tam-xa-bong",
    "chong-nang-toan-than",
    "khu-mui",
    "duong-the",
    "tri-nut-da",
    "duong-tay-chan",
    "cham-soc-nguc",
    "massage"
]

# sub DUOC_MY_PHAM "giai-phap-lan-da"
# EXAMP URL : https://nhathuoclongchau.com.vn/duoc-my-pham/tri-seo-mo-tham
GIAI_PHAP_LAN_DA = [
    "tri-seo-mo-tham",
    "da-mun",
    "da-bi-kho-thieu-am",
    "nam-tan-nhang-dom-nau",
    "viem-da-co-dia",
    "da-bi-kich-ung",
    "tai-tao-chong-lao-hoa",
    "da-sam-xin-mau"
]

# sub DUOC_MY_PHAM "cham-soc-toc-da-dau"
# EXAMP URL : https://nhathuoclongchau.com.vn/duoc-my-pham/dau-goi-dau-xa
CHAM_SOC_TOC_DA_DAU = [
    "dau-goi-dau-xa",
    "dau-goi-tri-nam",
    "duong-toc-u-toc",
    "dac-tri"
]

# sub DUOC_MY_PHAM "my-pham-trang-diem"
# EXAMP URL : https://nhathuoclongchau.com.vn/duoc-my-pham/son-moi
MY_PHAM_TRANG_DIEM = [
    "son-moi",
    "trang-diem-mat"
]

# sub DUOC_MY_PHAM "cham-soc-da-vung-mat"
# EXAMP URL : https://nhathuoclongchau.com.vn/duoc-my-pham/ngan-ngua-tri-tham-quang-bong-mat
CHAM_SOC_DA_VUNG_MAT = [
    "ngan-ngua-tri-tham-quang-bong-mat",
    "xoa-nep-nhan-vung-mat",
    "duong-da-ngan-ngua-lao-hoa-vung-mat"
]

# sub DUOC_MY_PHAM "san-pham-tu-thien-nhien"
# EXAMP URL :  https://nhathuoclongchau.com.vn/duoc-my-pham/tinh-dau
SAN_PHAM_TU_THIEN_NHIEN = [
    "tinh-dau",
    "dau-dua"
]

#==================================
# sub CATEGORIES "thuoc"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuoc/thuoc-di-ung
THUOC = [
    "thuoc-di-ung",
    "thuoc-giai-doc-khu-doc-va-ho-tro-cai-nghien",
    "thuoc-da-lieu",
    "mieng-dan-cao-xoa-dau",
    "co-xuong-khop",
    "thuoc-bo-and-vitamin",
    "thuoc-dieu-tri-ung-thu",
    "thuoc-giam-dau-ha-sot-khang-viem",
    "thuoc-ho-hap",
    "thuoc-khang-sinh-khang-nam",
    "thuoc-mat-tai-mui-hong",
    "thuoc-than-kinh",
    "thuoc-tiem-chich-and-dich-truyen",
    "thuoc-tieu-hoa-and-gan-mat",
    "thuoc-tim-mach-and-mau",
    "thuoc-tiet-nieu-sinh-duc",
    "thuoc-te-boi",
    "thuoc-tri-tieu-duong"
]

# sub THUOC "thuoc-di-ung"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuoc/thuoc-di-ung/thuoc-chong-di-ung
THUOC_DI_UNG = [
    "thuoc-chong-di-ung",
    "thuoc-say-tau-xe"
]

# sub THUOC "thuoc-giai-doc-khu-doc-va-ho-tro-cai-nghien"
# EXAMP URL : https://nhathuoclongchau.com.vn/thuoc/thuoc-giai-doc-khu-doc-va-ho-tro-cai-nghien/thuoc-ho-tro-cai-nghien-ma-tuy
THUOC_GIAI_DOC_KHU_DOC_VA_HO_TRO_CAI_NGHIEN = [
    "thuoc-ho-tro-cai-nghien-ma-tuy",
    "cap-cuu-giai-doc",
    "vien-cai-thuoc-la"
]

# sub THUOC "thuoc-da-lieu"
# EXAMP URL : 
THUOC_DA_LIEU = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]

# sub THUOC "mieng-dan-cao-xoa-dau"
# EXAMP URL : 
MIENG_DAN_CAO_XOA_DAU = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]

# sub THUOC "co-xuong-khop"
# EXAMP URL : 
CO_XUONG_KHOP = [
    "",
    "",
    "",
    "",
    "",
]

# sub THUOC "thuoc-bo-and-vitamin"
# EXAMP URL : 
THUOC_BO_AND_VITAMIN = [
    "",
    "",
    "",
    "",
]

# sub THUOC "thuoc-dieu-tri-ung-thu"
# EXAMP URL : 
THUOC_DIEU_TRI_UNG_THU = [
    "",
    "",
    "",
    "",
]

# sub THUOC "thuoc-giam-dau-ha-sot-khang-viem"
# EXAMP URL : 
THUOC_GIAM_DAU_HA_SOT_KHANG_VIE = [
    "",
    "",
    "",
]

# sub THUOC "thuoc-ho-hap"
# EXAMP URL : 
THUOC_HO_HAP = [
    "",
    "",
    "",
]

# sub THUOC "thuoc-khang-sinh-khang-nam"
# EXAMP URL : 
THUOC_KHANG_SINH_KHANG_NAM = [
    "",
    "",
    "",
]

# sub THUOC "thuoc-mat-tai-mui-hong"
# EXAMP URL : 
THUOC_MAT_TAI_MIU_HONG = [
    "",
    "",
    "",
]

# sub THUOC "thuoc-than-kinh"
# EXAMP URL : 
THUOC_THAN_KINH = [
    "",
    "",
    "",
]

# sub THUOC "thuoc-tiem-chich-and-dich-truyen"
# EXAMP URL : 
THUOC_TIEM_CHICH_AND_DICH_TRUYEN = [
    "",
    "",
    "",
]

# sub THUOC "thuoc-tieu-hoa-and-gan-mat"
# EXAMP URL : 
THUOC_TIEU_HOA_AND_GAN_MAT = [
    "",
    "",
    "",
]

# sub THUOC "thuoc-tim-mach-and-mau"
# EXAMP URL : 
THUOC_TIM_MACH_AND_MAU = [
    "",
    "",
    "",
]

# sub THUOC "thuoc-tiet-nieu-sinh-duc"
# EXAMP URL : 
THUOC_TIET_NIEU_SINH_DUC = [
    "",
    "",
    "",
]

# sub THUOC "thuoc-te-boi"
# EXAMP URL : 
THUOC_TE_BOI = [
    "",
    "",
    "",
]

# sub THUOC "thuoc-tri-tieu-duong"
# EXAMP URL : 
THUOC_TRI_TIEU_DUONG = [
    "",
    "",
    "",
]

#==================================
# sub CATEGORIES "cham-soc-ca-nhan"
# EXAMP URL : https://nhathuoclongchau.com.vn/cham-soc-ca-nhan/ho-tro-tinh-duc
CHAM_SOC_CA_NHAN = [
    "ho-tro-tinh-duc",
    "thuc-pham-do-uong",
    "ve-sinh-ca-nhan",
    "cham-soc-rang-mieng",
    "do-dung-gia-dinh",
    "hang-tong-hop",
    "tinh-dau-cac-loai",
    "thiet-bi-lam-dep"
]

# sub CHAM_SOC_CA_NHAN "ho-tro-tinh-duc"
# EXAMP URL : https://nhathuoclongchau.com.vn/cham-soc-ca-nhan/bao-cao-su
HO_TRO_TINH_DUC = [
    "bao-cao-su",
    "gel-boi-tron"
]

# sub CHAM_SOC_CA_NHAN "thuc-pham-do-uong"
# EXAMP URL : https://nhathuoclongchau.com.vn/cham-soc-ca-nhan/nuoc-yen
THUC_PHAM_DO_UONG = [
    "nuoc-yen",
    "keo-cung",
    "nuoc-uong-khong-gas",
    "duong-an-kieng",
    "tra",
    "keo-deo",
    "to-yen"
]

# sub CHAM_SOC_CA_NHAN "ve-sinh-ca-nhan"
# EXAMP URL : https://nhathuoclongchau.com.vn/cham-soc-ca-nhan/dung-dich-ve-sinh-phu-nu
VE_SINH_CA_NHAN = [
    "dung-dich-ve-sinh-phu-nu",
    "ve-sinh-tai",
    "bang-ve-sinh",
    "nuoc-rua-tay"
]

# sub CHAM_SOC_CA_NHAN "cham-soc-rang-mieng"
# EXAMP URL : https://nhathuoclongchau.com.vn/cham-soc-ca-nhan/kem-danh-rang
CHAM_SOC_RANG_MIENG = [
    "kem-danh-rang",
    "ban-chai-dien",
    "chi-nha-khoa",
    "cham-soc-rang",
    "nuoc-suc-mieng"
]

# sub CHAM_SOC_CA_NHAN "do-dung-gia-dinh"
# EXAMP URL : https://nhathuoclongchau.com.vn/cham-soc-ca-nhan/chong-muoi-con-trung
DO_DUNG_GIA_DINH = [
    "chong-muoi-con-trung",
    "do-dung-cho-be",
    "do-dung-cho-me"
]

# sub CHAM_SOC_CA_NHAN "hang-tong-hop"
# EXAMP URL : https://nhathuoclongchau.com.vn/cham-soc-ca-nhan/khan-giay-khan-uot
HANG_TONG_HOP = [
    "khan-giay-khan-uot"
]

# sub CHAM_SOC_CA_NHAN "tinh-dau-cac-loai   
# EXAMP URL : https://nhathuoclongchau.com.vn/cham-soc-ca-nhan/tinh-dau-massage
TINH_DAU_CAC_LOAI = [
    "tinh-dau-massage",
    "tinh-dau-tri-cam",
    "tinh-dau-xong"
]

# sub CHAM_SOC_CA_NHAN "thiet-bi-lam-dep"
# EXAMP URL : https://nhathuoclongchau.com.vn/cham-soc-ca-nhan/dung-cu-tay-long
THIET_BI_LAM_DEP = [
    "dung-cu-tay-long",
    "dung-cu-cao-rau"
]

#==================================
# sub CATEGORIES "trang-thiet-bi-y-te"
# EXAMP URL : https://nhathuoclongchau.com.vn/trang-thiet-bi-y-te/dung-cu-y-te
TRANG_THIET_BI_Y_TE = [
    "dung-cu-y-te",
    "dung-cu-theo-doi",
    "dung-cu-so-cuu",
    "khau-trang"
]

# sub TRANG_THIET_BI_Y_TE "dung-cu-y-te"
# EXAMP URL : https://nhathuoclongchau.com.vn/trang-thiet-bi-y-te/dung-cu-ve-sinh-mui
DUNG_CU_Y_TE = [
   "dung-cu-ve-sinh-mui",
   "kim-cac-loai",
   "may-massage",
   "tui-chuom",
   "vo-ngan-tinh-mach",
   "gang-tay",
   "dai-lung",
   "dung-cu-ve-sinh-tai",
   "dai-nep",
   "may-xong-khi-dung",
   "dung-cu-khac"
]

# sub TRANG_THIET_BI_Y_TE "dung-cu-theo-doi"
# EXAMP URL : https://nhathuoclongchau.com.vn/trang-thiet-bi-y-te/may-do-huyet-ap
DUNG_CU_THEO_DOI = [
    "may-do-huyet-ap",
    "may-que-thu-duong-huyet",
    "thu-thai",
    "nhiet-ke",
    "kit-test-covid",
    "may-do-sp-o2"
]   

# sub TRANG_THIET_BI_Y_TE "dung-cu-so-cuu"
# EXAMP URL : https://nhathuoclongchau.com.vn/trang-thiet-bi-y-te/bang-y-te
DUNG_CU_SO_CUU = [
    "bang-y-te",
    "bong-y-te",
    "con-va-nuoc-sat-trung",
    "cham-soc-vet-thuong",
    "xit-giam-dau",
    "mieng-dan-giam-dau"
]

# sub TRANG_THIET_BI_Y_TE "khau-trang"
# EXAMP URL : https://nhathuoclongchau.com.vn/trang-thiet-bi-y-te/khau-trang-y-te
KHAU_TRANG = [
    "khau-trang-y-te",
    "khau-trang-vai"
]