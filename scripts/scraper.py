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
        
        # We target the specific JSON blob that contains the real, live prices
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, response.text)
        
        found_price = "N/A"
        
        if match:
            data = json.loads(match.group(1))
            # The actual station data is buried deep here:
            # props -> pageProps -> station -> fuels
            try:
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    # Match 'Regular' specifically
                    if fuel.get('fuelType', '').lower() == 'regular':
                        price_entries = fuel.get('prices', [])
                        if price_entries:
                            # We want the most recent price (usually the first)
                            val = price_entries[0].get('price')
                            if val:
                                found_price = f"${val}"
                                break
            except (KeyError, TypeError):
                # Fallback to a tighter Regex if the JSON path fails
                fallback = re.search(r'"fuelType":"Regular","prices":\[{"price":(\d\.\d{2})', response.text)
                if fallback:
                    found_price = f"${fallback.group(1)}"
        
        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save to public/gas_prices.json
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
