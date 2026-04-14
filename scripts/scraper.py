import cloudscraper
import re
import json
import os

stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

scraper = cloudscraper.create_scraper()

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        # Get the full webpage
        response = scraper.get(url, timeout=15)
        html = response.text

        # REGEX EXPLANATION:
        # Look for a price like 3.45 or 3.09
        # That is inside a span or div
        # And is near the word "Regular"
        # We search for the price first, then check if 'Regular' is nearby
        
        found_price = "N/A"
        
        # This finds all price-looking strings (X.XX)
        all_prices = re.findall(r'(\d\.\d{2})', html)
        
        if all_prices:
            # Usually, the first price on a station page is Regular
            # But let's be safer and look for the one near the word 'Regular'
            if "Regular" in html:
                # GasBuddy often puts the price right before or after the word 'Regular'
                # We'll take the first one we found as a best guess
                found_price = f"${all_prices[0]}"
        
        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
