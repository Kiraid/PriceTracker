import time
from db import get_latest_products_all, insert_new_price
from scraper import scrape_data  # make sure this returns the latest price
import traceback

SLEEP_INTERVAL = 60 * 60 * 24  # 24 hours in seconds

def run_daily_tracker():
    while True:
        print("🔁 Running daily tracker...")

        try:
            products = get_latest_products_all()

            if not products:
                print("No products found to track.")
            else:
                for product in products:
                    (
                        db_id,
                        product_id,
                        user_id,
                        product_url,
                        product_name,
                        old_price,
                        percentage,
                        timestamp
                    ) = product

                    print(f"🔍 Scraping {product_name} for user {user_id}")

                    try:
                        time.sleep(3)
                        _, new_price = scrape_data(product_url)
                        if float(new_price) < float(old_price) * (float(percentage)/100):
                            print("email sent")
                        if new_price is not None:
                            insert_new_price(
                                user_id=user_id,
                                product_name=product_name,
                                product_url=product_url,
                                product_price=new_price,
                                product_id=product_id,
                                percentage=percentage
                            )
                            print(f"✅ Inserted new price {new_price} for {product_name}")
                        else:
                            print(f"⚠️ No price found for {product_name}")

                    except Exception as e:
                        print(f"❌ Error scraping {product_url}: {e}")
                        traceback.print_exc()

        except Exception as e:
            print(f"🔥 Error in daily tracker: {e}")
            traceback.print_exc()

        print(f"⏳ Sleeping for 24 hours...\n")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    run_daily_tracker()
