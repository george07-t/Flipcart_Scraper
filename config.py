import os

class Config:
    # Database settings
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'flipkart_products.db')
    
    # Scraper settings
    MAX_PAGES = int(os.getenv('MAX_PAGES', '3'))
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'True').lower() == 'true'
    REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', '2'))
    
    # Flipkart settings
    BASE_URL = "https://www.flipkart.com"
    
    # Chrome driver settings
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ]