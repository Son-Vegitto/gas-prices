import cloudscraper
import re
import json
import os

stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

# Create scraper with a real browser fingerprint
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        response = scraper.get(url, timeout=15)
        
        # Look for the price pattern (e.g., 3.45) followed by the regular gas label
        # This regex looks for the dollar amount near the text "Regular"
        match = re.search(r'(\d\.\d{2})</span>[^>]*>Regular', response.text)
        
        if match:
            prices[name] = f"${match.group(1)}"
        else:
            # Fallback: Look for the JSON data blob we tried earlier
            match_json = re.search(r'"fuelType":"Regular","prices":\[{"price":(\d\.\d{2})', response.text)
            if match_json:
                prices[name] = f"${match_json.group(1)}"
            else:
                prices[name] = "N/A"
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Success: {prices}")
