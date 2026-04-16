import os
import json
import time
import random  # Added for variable delays
from datetime import datetime, timedelta, timezone
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
    "Raceway 1": "33823",
    "Raceway 2": "208024",
    "Racetrack 1": "26764",
    "Racetrack 2": "33714",
#   "Weis": "204059",
    "Speedway 1": "19659",
    "Speedway 2": "33716",
    "Wawa 1": "210827",
    "Wawa 2": "75991",
    "Wawa 3": "67982",
    "Sheetz": "31735",
    "Gulf 1": "41828",
    "Gulf 2": "33011",
    "Jollys": "33913",
    "Taylor": "31737",
    "Speedway 3": "16010",
    "Lukoil": "7072"
}

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

station_data = {}

# 2. Scrape Data
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

for name, station_id in stations.items():
    url = f"https://www.gasbuddy.com/station/{station_id}"
    try:
        print(f"Opening GasBuddy for {name}...")
        driver.get(url)
        
        # Give the page a moment to load initial scripts
        time.sleep(3) 
        
        # Scroll down to trigger lazy loading of the price
        driver.execute_script("window.scrollTo(0, 400);")
        
        # Pause to let the price element render after the scroll
        time.sleep(2) 
        
        selector = "span[class*='FuelTypePriceDisplay-module__price']"
        
        try:
            # Increased timeout to 20 just in case
            WebDriverWait(driver, 20).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), "$")
            )
            element = driver.find_element(By.CSS_SELECTOR, selector)
            price_text = element.text.strip()
            
            if "$" in price_text:
                price = price_text
                print(f"Success for {name}: {price}")
            else:
                price = "N/A"
        except Exception:
            print(f"Timeout or missing price for {name}")
            price = "N/A"

    except Exception as e:
        print(f"Error at {name}: {e}")
        price = "N/A"
    
    station_data[name] = {"price": price, "url": url}
    
    # Random pause between 2-4 seconds between stations to stay under the radar
    time.sleep(random.uniform(2, 4))

driver.quit()

# 3. Sorting & Dynamic Logo Logic
def sort_by_price(item):
    price_str = item[1]["price"]
    try:
        # Handle N/A by moving them to the bottom
        if price_str == "N/A":
            return float('inf')
        return float(price_str.replace('$', ''))
    except ValueError:
        return float('inf')

sorted_items = sorted(station_data.items(), key=sort_by_price)

base_img_url = "https://raw.githubusercontent.com/Son-Vegitto/gas-prices/main/logos/"

sorted_rows = [
    {
        "name": name.split(' ')[0], 
        "price": data["price"],
        "logo": f"{base_img_url}{name.split(' ')[0].lower()}.png",
        "url": data["url"]
    } 
    for name, data in sorted_items
]

# 4. Timezone Correction
est_now = datetime.now(timezone(timedelta(hours=-4)))
timestamp = est_now.strftime("%d-%b-%Y %I:%M %p")

# 5. Final Output
final_output = {
    "updatedAt": timestamp,
    "source": "GasBuddy",
    "isLiveData": True,
    "rows": sorted_rows
}

# 6. Save to File
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(final_output, f, indent=2)

print(f"File updated. Timestamp: {timestamp}")
