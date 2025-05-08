# 📰 get_data_from_danTri_congnghe

**Mục tiêu**: Tự động thu thập tin tức từ chuyên mục **Công nghệ** trên trang báo điện tử [Dân Trí](https://dantri.com.vn/), lưu vào file CSV và chạy định kỳ vào lúc **6h sáng mỗi ngày**.

---

## 🚀 Tính năng

- Truy cập chuyên mục **Công nghệ** trên Dân Trí
- Lấy thông tin các bài viết:
  - 🏷 Tiêu đề
  - 📄 Mô tả
  - 🖼 Hình ảnh chính
  - 📝 Nội dung đầy đủ
  - 🔗 URL bài viết
  - 🕒 Thời gian thu thập
- Thu thập từ **nhiều trang** (tối đa `MAX_PAGES` có thể cấu hình)
- Lưu dữ liệu vào file CSV (`dantri_congnghe.csv`)
- Tự động chạy **hằng ngày lúc 6:00 AM** nhờ thư viện `schedule`

---

## 🛠 Công nghệ sử dụng

- Python 3.x
- `requests` – Gửi HTTP request
- `BeautifulSoup` – Phân tích HTML
- `csv`, `os`, `datetime` – Xử lý dữ liệu và hệ thống
- `schedule` – Tự động hóa công việc định kỳ

---

## 📦 Cài đặt

### 1. Clone repository
pip install -r requirements.txt
pip install requests beautifulsoup4 schedule
#### Chạy code 
python get_dantri_tech.py


```bash
git clone https://github.com/luongtiensinh/get_data_from_danTri_congnghe.git
cd get_data_from_danTri_congnghe
