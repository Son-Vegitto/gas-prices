import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

# Chrome setup for GitHub Actions
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

prices = {}

# Start the browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

for name, station_id in stations.items():
    try:
        print(f"Opening GasBuddy for {name}...")
        driver.get(f"https://www.gasbuddy.com/station/{station_id}")
        
        # 1. Human-like scroll
        driver.execute_script("window.scrollTo(0, 300);")
        
        # 2. Smart Wait: Look for the price element
        selector = "span[class*='FuelTypePriceDisplay-module__price']"
        
        try:
            # Wait up to 15 seconds for the "$" to appear in the price span
            WebDriverWait(driver, 15).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), "$")
            )
            
            element = driver.find_element(By.CSS_SELECTOR, selector)
            price_text = element.text.strip()
            
            # Final sanity check to ensure we didn't grab dashes
            if "$" in price_text:
                prices[name] = price_text
                print(f"Success for {name}: {price_text}")
            else:
                prices[name] = "Price Missing"
                print(f"Warning: {name} loaded but price is empty/dashes.")
                
        except Exception as wait_error:
            # If we timeout, try one last direct grab before giving up
            print(f"Wait timed out for {name}, attempting last-ditch grab...")
            try:
                final_check = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                prices[name] = final_check if final_check else "N/A"
            except:
                prices[name] = "Not Found"

    except Exception as e:
        print(f"Critical error at {name}: {e}")
        prices[name] = "Error"

driver.quit()

# --- NEW SORTING LOGIC ---
def sort_by_price(item):
    """
    Helper function to sort prices. 
    item[0] is the station name, item[1] is the price string.
    """
    price_str = item[1]
    try:
        # Strip the '$' and convert to a float for mathematical sorting
        return float(price_str.replace('$', ''))
    except ValueError:
        # If it's "Error", "Not Found", or "Price Missing", 
        # return infinity so it gets pushed to the very bottom of the list.
        return float('inf')

# Sort the dictionary items using our helper function
sorted_items = sorted(prices.items(), key=sort_by_price)

# Convert to a list of dictionaries (Highly recommended for KWGT)
# This will look like: [{"name": "Lukoil", "price": "$3.10"}, {"name": "BJs", "price": "$3.15"}]
sorted_prices_list = [{"name": name, "price": price} for name, price in sorted_items]

# Save the final sorted data
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    # Use indent=2 to make the JSON file readable if you check it on GitHub
    json.dump(sorted_prices_list, f, indent=2)

print(f"Final Sorted Outcome: {json.dumps(sorted_prices_list, indent=2)}")
