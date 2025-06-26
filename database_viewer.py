import sqlite3
import pandas as pd
from datetime import datetime
from config import Config
class DatabaseViewer:
    def __init__(self, db_path: str = Config.DATABASE_PATH):
        """ Initializes the DatabaseViewer with the path to the database."""
        self.db_path = db_path
    
    def view_all_products(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("SELECT * FROM product_info ORDER BY created_at DESC", conn)
                print(f"Total products: {len(df)}")
                print("\nLatest 10 products:")
                print(df.head(10).to_string(index=False))
                # Ask user if they want to save all data to CSV (default yes)
                save_csv = input("\nDo you want to save all products to CSV? (y/n, default: y): ").strip().lower()
                if save_csv == '' or save_csv == 'y':
                    df.to_csv("all_products.csv", index=False)
                    print("All products saved to all_products.csv")
                else:
                    print("Data not saved to CSV.")
                return df
        except Exception as e:
            print(f"Error viewing products: {e}")
            return None
    
    def get_stats(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total count
                cursor.execute("SELECT COUNT(*) FROM product_info")
                total = cursor.fetchone()[0]
                
                # Products with prices
                cursor.execute("SELECT COUNT(*) FROM product_info WHERE price IS NOT NULL AND price != ''")
                with_price = cursor.fetchone()[0]
                
                # Products with images
                cursor.execute("SELECT COUNT(*) FROM product_info WHERE image_url IS NOT NULL AND image_url != ''")
                with_image = cursor.fetchone()[0]
                
                print(f"Database Statistics:")
                print(f"Total products: {total}")
                print(f"Products with price: {with_price}")
                print(f"Products with image: {with_image}")
                
        except Exception as e:
            print(f"Error getting stats: {e}")

if __name__ == "__main__":
    viewer = DatabaseViewer()
    viewer.get_stats()
    viewer.view_all_products()