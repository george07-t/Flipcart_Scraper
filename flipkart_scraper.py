import sqlite3
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Handles database operations for product data storage."""
    
    def __init__(self, db_path: str = "flipkart_products.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Initialize the database and create product_info table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS product_info (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        image_url TEXT,
                        price TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def insert_product(self, title: str, image_url: str, price: str) -> bool:
        """Insert a single product into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO product_info (title, image_url, price, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (title, image_url, price, datetime.now()))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error inserting product: {e}")
            return False
    
    def insert_products_batch(self, products: List[Dict[str, str]]) -> int:
        """Insert multiple products in batch."""
        inserted_count = 0
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for product in products:
                    cursor.execute('''
                        INSERT INTO product_info (title, image_url, price, created_at)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        product.get('title', ''),
                        product.get('image_url', ''),
                        product.get('price', ''),
                        datetime.now()
                    ))
                    inserted_count += 1
                conn.commit()
                logger.info(f"Successfully inserted {inserted_count} products")
        except sqlite3.Error as e:
            logger.error(f"Batch insert error: {e}")
        return inserted_count
    
    def get_product_count(self) -> int:
        """Get total number of products in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM product_info")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Error getting product count: {e}")
            return 0


class FlipkartScraper:
    """Main scraper class for Flipkart product data extraction."""
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://www.flipkart.com"
        self.headless = headless
        self.driver = None
        self.db_manager = DatabaseManager()
        self.setup_driver()
    
    def setup_driver(self) -> None:
        """Setup Chrome WebDriver with appropriate options."""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("WebDriver setup completed")
        except Exception as e:
            logger.error(f"WebDriver setup failed: {e}")
            raise
    
    def search_products(self, keyword: str, max_pages: int = 3) -> List[Dict[str, str]]:
        """Search for products and scrape data from multiple pages."""
        all_products = []
        
        for page_num in range(1, max_pages + 1):
            logger.info(f"Scraping page {page_num} for keyword: {keyword}")
            
            # Construct search URL
            if page_num == 1:
                search_url = f"{self.base_url}/search?q={keyword}"
            else:
                search_url = f"{self.base_url}/search?q={keyword}&page={page_num}"
            
            products = self.scrape_page(search_url)
            if products:
                all_products.extend(products)
                logger.info(f"Found {len(products)} products on page {page_num}")
            else:
                logger.warning(f"No products found on page {page_num}")
                break
            
            # Add delay between requests
            time.sleep(2)
        
        return all_products
    
    def scrape_page(self, url: str) -> List[Dict[str, str]]:
        """Scrape products from a single page."""
        products = []
        
        try:
            self.driver.get(url)
            
            # Wait for products to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-id]"))
            )
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find product containers
            product_containers = soup.find_all('div', {'data-id': True})
            
            for container in product_containers:
                product = self.extract_product_info(container)
                if product and self.validate_product(product):
                    products.append(product)
            
        except TimeoutException:
            logger.error(f"Timeout waiting for page to load: {url}")
        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
        
        return products
    
    def extract_product_info(self, container) -> Optional[Dict[str, str]]:
        """Extract product information from a container element."""
        try:
            product = {}
            
            # Extract title
            title_elem = container.find('div', class_='KzDlHZ') or \
                        container.find('a', class_='wjcEIp') or \
                        container.find('a', class_='WKTcLC')
            
            if title_elem:
                product['title'] = title_elem.get_text(strip=True)
            else:
                # Try alternative selectors
                title_elem = container.find('div', class_='_4rR01T')
                if title_elem:
                    product['title'] = title_elem.get_text(strip=True)
            
            # Extract image URL
            img_elem = container.find('img')
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src')
                if img_src:
                    product['image_url'] = img_src if img_src.startswith('http') else urljoin(self.base_url, img_src)
            
            # Extract price
            price_elem = container.find('div', class_='Nx9bqj') or \
                        container.find('div', class_='_30jeq3') or \
                        container.find('div', class_='_1_WHN1')
            
            if price_elem:
                product['price'] = price_elem.get_text(strip=True)
            
            return product if product.get('title') else None
            
        except Exception as e:
            logger.error(f"Error extracting product info: {e}")
            return None
    
    def validate_product(self, product: Dict[str, str]) -> bool:
        """Validate if product data is complete and valid."""
        required_fields = ['title']
        return all(product.get(field) for field in required_fields)
    
    def save_products(self, products: List[Dict[str, str]]) -> int:
        """Save products to database."""
        if not products:
            logger.warning("No products to save")
            return 0
        
        return self.db_manager.insert_products_batch(products)
    
    def run_scraper(self, keyword: str, max_pages: int = 3) -> Dict[str, int]:
        """Main method to run the scraper."""
        logger.info(f"Starting scraper for keyword: {keyword}")
        
        try:
            # Scrape products
            products = self.search_products(keyword, max_pages)
            
            # Save to database
            saved_count = self.save_products(products)
            
            # Get total count in database
            total_count = self.db_manager.get_product_count()
            
            result = {
                'scraped': len(products),
                'saved': saved_count,
                'total_in_db': total_count
            }
            
            logger.info(f"Scraping completed. Results: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Scraper execution failed: {e}")
            raise
        finally:
            self.close()
    
    def close(self) -> None:
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")


def main():
    """Main function to run the scraper."""
    print("Flipkart Product Scraper")
    print("=" * 50)
    
    # Get user input
    keyword = input("Enter search keyword (default: smartphone): ").strip()
    if not keyword:
        keyword = "smartphone"
    
    max_pages_input = input("Enter max pages to scrape (default: 3): ").strip()
    try:
        max_pages = int(max_pages_input) if max_pages_input else 3
        max_pages = min(max_pages, 3)  # Limit to 3 pages as per requirement
    except ValueError:
        max_pages = 3
    
    headless_input = input("Run in headless mode? (y/n, default: y): ").strip().lower()
    headless = headless_input != 'n'
    
    print(f"\nConfiguration:")
    print(f"Keyword: {keyword}")
    print(f"Max pages: {max_pages}")
    print(f"Headless mode: {headless}")
    print("-" * 50)
    
    # Run scraper
    scraper = FlipkartScraper(headless=headless)
    
    try:
        results = scraper.run_scraper(keyword, max_pages)
        
        print(f"\nScraping Results:")
        print(f"Products scraped: {results['scraped']}")
        print(f"Products saved: {results['saved']}")
        print(f"Total products in database: {results['total_in_db']}")
        print(f"\nDatabase file: flipkart_products.db")
        print(f"Log file: scraper.log")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
        logger.error(f"Main execution error: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
