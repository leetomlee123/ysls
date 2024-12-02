import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import time
import requests
from lxml import html
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from urllib.parse import urljoin,quote
from datetime import datetime, timedelta
import random

# Configuration
base_url = "https://m.ting13.cc/youshengxiaoshuo/{}/"  # Base URL for your book site
html_directory = "/opt/1panel/apps/openresty/openresty/www/sites/reader.colors.nyc.mn/index/"  # Path to your HTML files
sitemap_output_file = "sitemap.xml"  # Output sitemap file

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
}

# ID range for looping
start_id = 100
end_id=428
# end_id = 19185  # Example: Generate from 19176 to 19185


proxies = {
    "http": "http://127.0.0.1:7891",
    "https": "http://127.0.0.1:7891"
}
session = requests.Session()

# Configure retry strategy
retry_strategy = Retry(
    total=5,  # Total retries
    backoff_factor=1,  # Delay between retries (increasing backoff)
    status_forcelist=[500, 502, 503, 504],  # Retry on server errors
    method_whitelist=["GET", "POST"]  # Methods to retry
)

# Attach the retry strategy to an HTTPAdapter
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Function to generate HTML content for each book
def generate_html(book_id):
    url = base_url.format(book_id)
    print(f"Fetching: {url}")
    try:
        # Send request with headers
        response = session.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        
        # Parse the HTML content
        tree = html.fromstring(response.content)
        
        # Extract parameters from the page
        title = tree.xpath('//title/text()')
        keywords = tree.xpath('//meta[@name="keywords"]/@content')
        description = tree.xpath('//meta[@name="description"]/@content')
        cover_url = tree.xpath('//img[@class="book-cover"]/@src')
        book_title = tree.xpath('//h1[@class="book-title"]/text()')
        genre = tree.xpath('//div[@class="book-rand-a"][1]/a/text()')
        popularity = tree.xpath('//div[@class="book-rand-a"][2]/font/text()')
        author = tree.xpath('//div[@class="book-rand-a"][3]/a/text()')
        narrator = tree.xpath('//div[@class="book-rand-a"][4]/a/text()')
        release_date = tree.xpath('//div[@class="book-rand-a"][5]/text()')
        content_summary = tree.xpath('//div[@class="book-des ellipsis"]/text()')
        
        # Clean up extracted values
        if not title:
            raise Exception("Book title not found")
        title = title[0].strip()
        keywords = keywords[0].strip() if keywords else "No Keywords"
        description = description[0].strip() if description else "No Description"
        cover_url = cover_url[0].strip() if cover_url else "default_cover.jpg"  # Fallback to a default image if not found
        book_title = book_title[0].strip() if book_title else f"Book_{book_id}"
        if not genre:
            raise Exception("genre not found")
        genre = genre[0].strip() if genre else "Unknown Genre"
        popularity = popularity[0].strip() if popularity else "Unknown Popularity"
        author = author[0].strip() if author else "Unknown Author"
        narrator = narrator[0].strip() if narrator else "Unknown Narrator"
        release_date = release_date[0].strip() if release_date else "Unknown Release Date"
        content_summary = content_summary[0].strip() if content_summary else "No content summary available."
        
        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <meta name="keywords" content="{keywords}">
            <meta name="description" content="{description}">
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background-color: #f8f9fa; font-family: Arial, sans-serif; }}
                .cover {{ max-width: 150px; max-height: 150px; padding-right: 1px; }}
                .content {{ max-width: 500px; }}
                .content p {{ padding: 10px 0; }}
                h1, h2 {{ text-align: center; color: #333; }}
            </style>
        </head>
        <body>
            <div class="container-sm">
                <h1>{book_title}</h1>
                <div class="row" style="display: flex; justify-content: center; align-items: center; padding: 2px;">
                    <img src="https://api.nicevoice.nyc.mn/img/proxy?url={cover_url}" alt="Cover Image" class="cover" style="max-width: 150px; margin-right: 2px;">
                    <div class="content" style="flex: 1; padding-left: 10px; max-width: 500px; word-wrap: break-word;">
                        <div><strong>类型:</strong> {genre}</div>
                        <div><strong>热度:</strong> {popularity}</div>
                        <div><strong>作者:</strong> {author}</div>
                        <div><strong>播音:</strong> {narrator}</div>
                        <div><strong>最后更新:</strong> {release_date}</div>
                    </div>
                </div>

                <div>
                    <h2>内容介绍</h2>
                    <p>{content_summary}</p>
                </div>
                <h2>下载APP免费收听</h2>
                
                <div class="row" style="display: flex; justify-content: center; align-items: center; padding: 20px;">
                    <img src="https://alist.colors.nyc.mn/d/local_images/qrcode_www.123865.com.png" alt="QR Code" class="cover">
                </div>
            </div>
        </body>
        </html>
        """
        
        # Replace "13听书网" with "听书楼" in HTML content
        html_content = html_content.replace("13听书网", "听书楼")
        
        # Save the HTML content to a file
        file_name = f"{genre}/{book_title}.html"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(html_content)
        generate_sitemap()
        print(f"Generated HTML file: {file_name}")
        
        return file_name, genre

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for ID {book_id}: {e}")
        return None, None
    except Exception as e:
        print(f"Error processing book {book_id}: {e}")
        return None, None
    finally:
        time.sleep(1)
        
      # Adjust the sleep time if needed

def get_last_modified_date(start_year=2008):
    # 获取文件的最后修改时间
    start_date = datetime(start_year, 1, 1)
    # 当前时间
    end_date = datetime.utcnow()
    # 计算时间范围内的总秒数
    total_seconds = int((end_date - start_date).total_seconds())
    # 生成一个随机的秒数
    random_seconds = random.randint(0, total_seconds)
    # 加上随机秒数得到随机日期
    random_date = start_date + timedelta(seconds=random_seconds)
    # 返回 ISO 8601 格式的日期字符串
    return random_date.strftime("%Y-%m-%dT%H:%M:%S+00:00")

def create_url_entry(urlset, loc, lastmod):
    # 创建 sitemap 中的 <url> 元素
    url = SubElement(urlset, "url")
    loc_element = SubElement(url, "loc")
    loc_element.text = loc
    lastmod_element = SubElement(url, "lastmod")
    lastmod_element.text = lastmod

def clean_path(file_path):
    # 清理路径中的非法代理字符
    return file_path.encode("utf-8", "surrogatepass").decode("utf-8", "ignore")

def generate_sitemap():
    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    for root, _, files in os.walk(html_directory):
        for file_name in files:
            if file_name.endswith(".html"):
                file_path = os.path.join(root, file_name)
                file_path = clean_path(file_path)  # 清理路径
                relative_path = os.path.relpath(file_path, html_directory)
                encoded_path = quote(relative_path.replace("\\", "/"))
                url = urljoin("https://reader.colors.nyc.mn/", encoded_path)
                lastmod = get_last_modified_date()
                create_url_entry(urlset, url, lastmod)

    tree = ElementTree(urlset)
    tree.write(sitemap_output_file, encoding="utf-8", xml_declaration=True)
    print(f"Sitemap saved as {sitemap_output_file}")


generate_sitemap()
# Main loop to generate HTML and update sitemap
#with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit all the book_id's to the thread pool
 #   executor.map(generate_html, range(start_id, end_id + 1))

