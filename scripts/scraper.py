import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

# Setup Chrome Options for GitHub Actions
chrome_options = Options()
chrome_options.add_argument("--headless") # Runs without a window
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

prices = {}

# Start the browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

for name, station_id in stations.items():
    try:
        print(f"Opening GasBuddy for {name}...")
        driver.get(f"https://www.gasbuddy.com/station/{station_id}")
        
        # Give the page 5 seconds to run its JavaScript and bypass challenges
        time.sleep(5) 

        # We look for the price using the class you found!
        # We use a partial match on the class name to be safe
        try:
            element = driver.find_element(By.CSS_SELECTOR, "span[class*='FuelTypePriceDisplay-module__price']")
            price_text = element.text.strip()
            if price_text:
                prices[name] = price_text
                print(f"Success for {name}: {price_text}")
            else:
                prices[name] = "N/A"
        except:
            prices[name] = "Not Found"

    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

driver.quit()

# Save data
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
