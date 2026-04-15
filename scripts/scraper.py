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

# 1. Configuration
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

# 2. Scrape Data
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

for name, station_id in stations.items():
    try:
        print(f"Opening GasBuddy for {name}...")
        driver.get(f"https://www.gasbuddy.com/station/{station_id}")
        
        driver.execute_script("window.scrollTo(0, 300);")
        selector = "span[class*='FuelTypePriceDisplay-module__price']"
        
        try:
            WebDriverWait(driver, 15).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), "$")
            )
            element = driver.find_element(By.CSS_SELECTOR, selector)
            price_text = element.text.strip()
            
            if "$" in price_text:
                prices[name] = price_text
                print(f"Success for {name}: {price_text}")
            else:
                prices[name] = "N/A"
        except Exception:
            prices[name] = "N/A"

    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "N/A"

driver.quit()

# 3. Sorting Logic
def sort_by_price(item):
    price_str = item[1]
    try:
        # Convert "$3.15" to float 3.15 for sorting
        return float(price_str.replace('$', ''))
    except ValueError:
        # Push N/A to the end
        return float('inf')

sorted_items = sorted(prices.items(), key=sort_by_price)

# 4. Format for KWGT (Mimicking Olympic Project Structure)
# This creates a list of dictionaries inside the 'rows' key
sorted_rows = [{"name": name, "price": price} for name, price in sorted_items]

final_output = {
    "last_updated": time.strftime("%Y-%m-%d %I:%M %p"),
    "rows": sorted_rows
}

# 5. Save to File
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(final_output, f, indent=2)

print(f"File updated successfully. Structure: {json.dumps(final_output, indent=2)}")
