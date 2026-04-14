import requests
import re
import json
import os

# Using the URLs for the specific PA locations
stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

session = requests.Session()
# Using a high-quality Windows User Agent to look like a standard desktop user
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        response = session.get(url, headers=headers, timeout=15)
        html = response.text

        found_price = "N/A"

        # 1. Look for the fuel data in the JSON block
        # We look specifically for "Regular" fuel and the price associated with it
        json_pattern = r'"fuelType":"Regular".*?"price":(\d\.\d{2})'
        match = re.search(json_pattern, html)
        
        if match:
            found_price = f"${match.group(1)}"
        else:
            # 2. Fallback: Find all 3.XX or 4.XX numbers
            # We filter out ratings like 4.5 by requiring two decimal places
            all_prices = re.findall(r'(\d\.\d{2})', html)
            
            # Real gas prices in PA right now are between $3.50 and $4.50
            # We filter for that range to ignore metadata junk
            valid_prices = [p for p in all_prices if 3.50 <= float(p) <= 4.50]
            
            if valid_prices:
                # The first valid price in the HTML is almost always Regular
                found_price = f"${valid_prices[0]}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save the results to the public folder
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
