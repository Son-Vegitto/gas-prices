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
            
            if "$" in price_text:
                prices[name] = price_text
                print(f"Success for {name}: {price_text}")
            else:
                prices[name] = "N/A"
                print(f"Warning: {name} loaded but price is empty/dashes.")
                
        except Exception as wait_error:
            print(f"Wait timed out for {name}, attempting last-ditch grab...")
            try:
                final_check = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                prices[name] = final_check if final_check else "N/A"
            except:
                prices[name] = "N/A"

    except Exception as e:
        print(f"Critical error at {name}: {e}")
        prices[name] = "N/A"

driver.quit()

# --- SORTING LOGIC ---
def sort_by_price(item):
    price_str = item[1]
    try:
        # Convert "$3.15" to 3.15
        return float(price_str.replace('$', ''))
    except ValueError:
        # Push "N/A" or "Error" to the end
        return float('inf')

sorted_items = sorted(prices.items(), key=sort_by_price)

# Convert to a list of dictionaries
sorted_prices_list = [{"name": name, "price": price} for name, price in sorted_items]

# --- KWGT-FRIENDLY WRAPPER ---
# Wrapping in a dictionary fixes the "Illegal Character" (Array) error
final_json_structure = {
    "stations": sorted_prices_list
}

# Save the final synced data
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(final_json_structure, f, indent=2)

print(f"Final Outcome: {json.dumps(final_json_structure, indent=2)}")
