import cloudscraper
import json
import os
import re

stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

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
        
        # 1. Try to find the JSON data blob hidden in the page
        # This is where GasBuddy stores the data before the page even loads
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, response.text)
        
        found_price = "N/A"
        
        if match:
            data = json.loads(match.group(1))
            # Dig through the nested JSON structure
            # pageProps -> station -> fuels
            try:
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    if fuel.get('fuelType', '').lower() == 'regular':
                        price_list = fuel.get('prices', [])
                        if price_list:
                            # Use the first available price
                            val = price_list[0].get('price')
                            if val:
                                found_price = f"${val}"
                                break
            except KeyError:
                pass
        
        # 2. Safety Fallback: if JSON fails, look for any price-like number
        # near the text "Regular" anywhere in the page
        if found_price == "N/A":
            fallback_match = re.search(r'(\d\.\d{2}).{1,50}Regular', response.text, re.IGNORECASE)
            if fallback_match:
                found_price = f"${fallback_match.group(1)}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save to the public folder for GitHub Pages / Raw access
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
