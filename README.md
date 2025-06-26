# Flipkart Product Scraper

A robust Python-based web scraper for extracting product information from Flipkart's e-commerce platform. Built with Selenium, BeautifulSoup, and SQLite following object-oriented programming principles.

## Features

- **Multi-page Scraping**: Scrapes up to 3 pages of search results
- **Robust Data Extraction**: Extracts product title, image URL, and price
- **Database Storage**: Stores data in SQLite database with proper schema
- **Old/New Data Option**: Choose to keep old scraped data or insert fresh new data when running the scraper if the database already exists
- **CSV Export Option**: After viewing the latest 10 products in the database viewer, you can choose to export all products to a CSV file
- **Error Handling**: Comprehensive logging and error handling
- **Clean Architecture**: Follows OOP principles with separate classes for different responsibilities
- **Configurable**: Supports headless/GUI mode, customizable parameters

## Project Structure

```
flipkart-scraper/
├── flipkart_scraper.py      # Main scraper application
├── database_viewer.py       # Utility to view scraped data
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── .gitignore            # Git ignore rules
├── flipkart_products.db  # SQLite database (created after first run)
└── scraper.log           # Application logs
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/george07-t/Flipcart_Scraper.git
   cd flipkart-scraper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install ChromeDriver**
   - Download ChromeDriver from https://chromedriver.chromium.org/
   - Add ChromeDriver to your system PATH
   - Or install via package manager:
     ```bash
     # Ubuntu/Debian
     sudo apt-get install chromium-chromedriver
     
     # macOS
     brew install chromedriver
     
     # Windows (with chocolatey)
     choco install chromedriver
     ```

## Usage

### Basic Usage

Run the scraper with interactive prompts:
```bash
python flipkart_scraper.py
```

### View Scraped Data

```bash
python database_viewer.py
```

## Database Schema

The scraper creates a `product_info` table with the following structure:

| Column     | Type      | Description                    |
|------------|-----------|--------------------------------|
| id         | INTEGER   | Primary key (auto-increment)  |
| title      | TEXT      | Product title                  |
| image_url  | TEXT      | Product image URL              |
| price      | TEXT      | Product price                  |
| created_at | TIMESTAMP | Record creation timestamp      |

## Configuration

### Environment Variables

- `DATABASE_PATH`: Path to SQLite database file
- `MAX_PAGES`: Maximum pages to scrape (default: 3)
- `HEADLESS_MODE`: Run browser in headless mode (default: True)
- `REQUEST_DELAY`: Delay between requests in seconds (default: 2)

### Code Configuration

Modify `config.py` to adjust scraper settings:

```python
class Config:
    DATABASE_PATH = 'flipkart_products.db'
    MAX_PAGES = 3
    HEADLESS_MODE = True
    REQUEST_DELAY = 2
    BASE_URL = "https://www.flipkart.com"
```

## Architecture

### Class Structure

1. **DatabaseManager**: Handles all database operations
   - Database initialization
   - Product insertion (single and batch)
   - Data retrieval

2. **FlipkartScraper**: Main scraper logic
   - WebDriver setup and management
   - Page navigation and scraping
   - Product data extraction
   - Data validation

3. **Supporting Classes**:
   - **Config**: Configuration management
   - **DatabaseViewer**: Database inspection utilities

### Key Design Patterns

- **Single Responsibility**: Each class has a specific purpose
- **Dependency Injection**: DatabaseManager is injected into FlipkartScraper
- **Resource Management**: Proper cleanup of WebDriver resources
- **Error Handling**: Comprehensive exception handling with logging

## Error Handling

The scraper includes robust error handling for:
- Network timeouts
- Element not found scenarios
- Database connection issues
- WebDriver initialization problems
- Invalid product data

All errors are logged to `scraper.log` with timestamps and detailed information.


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [MIT LICENSE](./LICENSE) file for details.
