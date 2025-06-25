import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def init_db(db_path="flipkart_products.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS product_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        image_url TEXT,
        price TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def insert_products(products, db_path="flipkart_products.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    count = 0
    for p in products:
        c.execute('''INSERT INTO product_info (title, image_url, price, created_at) VALUES (?, ?, ?, datetime('now'))''',
                  (p.get('title', ''), p.get('image_url', ''), p.get('price', '')))
        count += 1
    conn.commit()
    conn.close()
    return count

def get_product_count(db_path="flipkart_products.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM product_info')
    count = c.fetchone()[0]
    conn.close()
    return count

# Scraper functions

def extract_product_info(container, base_url):
    product = {}
    title_elem = container.find('div', class_='KzDlHZ') or \
                container.find('a', class_='wjcEIp') or \
                container.find('a', class_='WKTcLC')
    if title_elem:
        product['title'] = title_elem.get_text(strip=True)
    else:
        title_elem = container.find('div', class_='_4rR01T')
        if title_elem:
            product['title'] = title_elem.get_text(strip=True)
    img_elem = container.find('img')
    if img_elem:
        img_src = img_elem.get('src') or img_elem.get('data-src')
        if img_src:
            product['image_url'] = img_src if img_src.startswith('http') else urljoin(base_url, img_src)
    price_elem = container.find('div', class_='Nx9bqj') or \
                container.find('div', class_='_30jeq3') or \
                container.find('div', class_='_1_WHN1')
    if price_elem:
        product['price'] = price_elem.get_text(strip=True)
    if product.get('title'):
        return product
    return None

def scrape_page(driver, url, base_url):
    products = []
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-id]"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_containers = soup.find_all('div', {'data-id': True})
        for container in product_containers:
            product = extract_product_info(container, base_url)
            if product:
                products.append(product)
    except TimeoutException:
        print(f"Timeout waiting for page to load: {url}")
    except Exception as e:
        print(f"Error scraping page {url}: {e}")
    return products

def search_products(driver, keyword, max_pages, base_url):
    all_products = []
    for page_num in range(1, max_pages + 1):
        print(f"Scraping page {page_num} for keyword: {keyword}")
        if page_num == 1:
            search_url = f"{base_url}/search?q={keyword}"
        else:
            search_url = f"{base_url}/search?q={keyword}&page={page_num}"
        products = scrape_page(driver, search_url, base_url)
        if products:
            all_products.extend(products)
            print(f"Found {len(products)} products on page {page_num}")
        else:
            print(f"No products found on page {page_num}")
            break
        time.sleep(2)
    return all_products

def main():
    print("Flipkart Product Scraper")
    print("=" * 50)
    keyword = input("Enter search keyword (default: smartphone): ").strip()
    if not keyword:
        keyword = "smartphone"
    max_pages_input = input("Enter max pages to scrape (default: 3): ").strip()
    try:
        max_pages = int(max_pages_input) if max_pages_input else 3
        max_pages = min(max_pages, 3)
    except ValueError:
        max_pages = 3
    headless_input = input("Run in headless mode? (y/n, default: y): ").strip().lower()
    headless = headless_input != 'n'
    print(f"\nConfiguration:")
    print(f"Keyword: {keyword}")
    print(f"Max pages: {max_pages}")
    print(f"Headless mode: {headless}")
    print("-" * 50)
    base_url = "https://www.flipkart.com"
    init_db()
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    try:
        products = search_products(driver, keyword, max_pages, base_url)
        saved_count = insert_products(products)
        total_count = get_product_count()
        print(f"\nScraping Results:")
        print(f"Products scraped: {len(products)}")
        print(f"Products saved: {saved_count}")
        print(f"Total products in database: {total_count}")
        print(f"\nDatabase file: flipkart_products.db")
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        driver.quit()
        print("WebDriver closed")

if __name__ == "__main__":
    main()
