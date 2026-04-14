import cloudscraper
import re
import json
import os

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
        html = response.text

        # 1. Try to find all instances of "price":3.XX
        # This is usually the most reliable way to find the actual data
        price_matches = re.findall(r'"price":(\d\.\d{2})', html)
        
        # 2. Filter out common 'fake' or 'metadata' prices
        # We want prices between $2.00 and $6.00 (standard for 2026)
        valid_prices = [p for p in price_matches if 2.00 <= float(p) <= 6.00]
        
        if valid_prices:
            # Usually the first valid price in the data block is Regular
            prices[name] = f"${valid_prices[0]}"
        else:
            # Fallback: search for the price inside the visual span class
            # GasBuddy often uses a specific span for the price
            span_match = re.search(r'>(\d\.\d{2})</span>', html)
            if span_match:
                prices[name] = f"${span_match.group(1)}"
            else:
                prices[name] = "N/A"
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
