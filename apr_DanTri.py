import requests
from bs4 import BeautifulSoup
import csv
import os
import schedule
import time
from datetime import datetime
from urllib.parse import urljoin

# Cấu hình
BASE_URL = "https://dantri.com.vn/"
CATEGORY = "cong-nghe"
CATEGORY_NAME = "Công nghệ"
MAX_PAGES = 10  # Số trang tối đa để thu thập
OUTPUT_FILE = "dantri_congnghe.csv"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

headers = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
}

def get_article_details(article_url):
    try:
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Lấy tiêu đề
        title_tag = soup.select_one("h1.title-page")
        title = title_tag.get_text(strip=True) if title_tag else "Không có tiêu đề"

        # Lấy mô tả
        description_tag = soup.select_one("div.singular-sapo")
        description = description_tag.get_text(strip=True) if description_tag else "Không có mô tả"

        # Lấy nội dung
        content_div = soup.select_one("div.singular-content")
        if content_div:
            paragraphs = [p.get_text(strip=True) for p in content_div.find_all("p")]
            content = "\n".join([p for p in paragraphs if p])
        else:
            content = "Không có nội dung"

        # Lấy hình ảnh - Sử dụng nhiều selector để tìm ảnh chính
        image_url = ""
        
        # Thử nhiều cách khác nhau để lấy hình ảnh
        # 1. Ảnh từ thẻ figure đầu tiên (thường là ảnh chính)
        figure_img = soup.select_one("figure.singular-image img, figure.e-img img")
        if figure_img:
            # Ưu tiên lấy data-src nếu có
            if 'data-src' in figure_img.attrs:
                image_url = figure_img['data-src']
            # Sau đó là srcset
            elif 'srcset' in figure_img.attrs:
                srcset = figure_img['srcset']
                parts = srcset.split(',')
                if parts:
                    # Lấy URL cuối cùng trong srcset (thường là bản 2x chất lượng cao)
                    image_url = parts[-1].strip().split()[0]
            # Cuối cùng là src
            elif 'src' in figure_img.attrs:
                image_url = figure_img['src']
        
        # 2. Nếu không tìm thấy, thử tìm trong phần nội dung
        if not image_url:
            content_img = soup.select_one("div.singular-content img, div.article-content img")
            if content_img:
                if 'data-src' in content_img.attrs:
                    image_url = content_img['data-src']
                elif 'srcset' in content_img.attrs:
                    srcset = content_img['srcset']
                    parts = srcset.split(',')
                    if parts:
                        image_url = parts[-1].strip().split()[0]
                elif 'src' in content_img.attrs:
                    image_url = content_img['src']
        
        # 3. Tìm tất cả các ảnh và lấy ảnh đầu tiên
        if not image_url:
            all_imgs = soup.select("img[src], img[data-src]")
            for img in all_imgs:
                if 'data-src' in img.attrs:
                    image_url = img['data-src']
                    break
                elif 'src' in img.attrs:
                    image_url = img['src']
                    break
        
        # Đảm bảo URL hình ảnh là URL đầy đủ
        if image_url and not image_url.startswith(('http://', 'https://')):
            image_url = urljoin(BASE_URL, image_url)

        # In ra thông tin debug
        print(f"- Tiêu đề: {title}")
        print(f"- Hình ảnh: {image_url}")

        return {
            'title': title,
            'description': description,
            'image_url': image_url,
            'content': content,
            'article_url': article_url,
            'scraped_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        print(f"Lỗi khi lấy bài viết {article_url}: {str(e)}")
        return None


def scrape_dantri_tech():
    """Thu thập tin tức công nghệ từ Dantri"""
    all_articles = []
    
    for page in range(1, MAX_PAGES + 1):
        # Tạo URL cho từng trang
        if page == 1:
            url = urljoin(BASE_URL, f"{CATEGORY}.htm")
        else:
            url = urljoin(BASE_URL, f"{CATEGORY}/trang-{page}.htm")
        
        print(f"Đang thu thập trang {page}: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tìm tất cả các bài viết trên trang
            # Thử nhiều selector để phù hợp với cấu trúc trang
            articles = soup.select("article.article-item, div.article, div.news-item")
            
            if not articles:
                print(f"Không tìm thấy bài viết nào trên trang {page}")
                break
            
            print(f"Tìm thấy {len(articles)} bài viết trên trang {page}")
            
            for article in articles:
                link = article.select_one("a[href]")
                if link:
                    article_url = urljoin(BASE_URL, link['href'])
                    print(f"Đang thu thập bài viết: {article_url}")
                    article_data = get_article_details(article_url)
                    if article_data:
                        article_data['category'] = CATEGORY_NAME
                        all_articles.append(article_data)
                        print(f"Đã thu thập: {article_data['title']}")
            
            # Kiểm tra nếu có nút trang tiếp theo
            next_page = soup.select_one("a.next, a.page-next")
            if not next_page:
                print("Không tìm thấy trang tiếp theo, dừng lại")
                break
                
        except Exception as e:
            print(f"Lỗi khi thu thập trang {page}: {str(e)}")
            continue
    
    return all_articles

def save_to_csv(data, filename):
    """Lưu dữ liệu vào file CSV"""
    if not data:
        print("Không có dữ liệu để lưu")
        return
    
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['category', 'title', 'description', 'image_url', 'content', 'article_url', 'scraped_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(data)
    
    print(f"Đã lưu {len(data)} bài viết vào {filename}")

def daily_scraping_job():
    """Công việc thu thập hàng ngày"""
    print(f"\n=== Bắt đầu thu thập dữ liệu lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    articles = scrape_dantri_tech()
    
    if articles:
        save_to_csv(articles, OUTPUT_FILE)
    else:
        print("Không thu thập được bài viết nào")
    
    print(f"=== Hoàn thành lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

def main():
    # Tạo file CSV nếu chưa tồn tại
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'category', 'title', 'description', 'image_url', 'content', 
                'article_url', 'scraped_time'
            ])
            writer.writeheader()
    
    # Lên lịch chạy hàng ngày lúc 6h sáng
    schedule.every().day.at("06:00").do(daily_scraping_job)
    
    # Chạy ngay lần đầu để có dữ liệu
    print("Chạy thu thập dữ liệu ngay lần đầu...")
    daily_scraping_job()
    
    print("Đã thiết lập lịch chạy hàng ngày lúc 6:00 sáng. Đang chờ...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Kiểm tra mỗi phút

if __name__ == "__main__":
    main()