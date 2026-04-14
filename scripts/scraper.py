import requests
import re
import json
import os

stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
}

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        response = session.get(url, headers=headers, timeout=15)
        html = response.text

        # 1. Target the 'Regular' price specifically within the JSON data
        # We look for "Regular" and then grab the FIRST "price":X.XX that follows it
        # This prevents us from grabbing the Premium ($5.XX) prices
        regular_block = re.search(r'"fuelType":"Regular".*?"price":(\d\.\d{2})', html)
        
        if regular_block:
            prices[name] = f"${regular_block.group(1)}"
        else:
            # Fallback: Look for "Regular" in the visual HTML and grab the number immediately before it
            # GasBuddy visual layout often puts the price then the label
            visual_match = re.search(r'>(\d\.\d{2})</span>[^>]*>Regular', html)
            if visual_match:
                prices[name] = f"${visual_match.group(1)}"
            else:
                # Last resort: find all prices and take the SMALLEST one
                # (Regular is almost always the cheapest)
                all_prices = re.findall(r'(\d\.\d{2})', html)
                valid = [float(p) for p in all_prices if 2.50 < float(p) < 6.00]
                if valid:
                    prices[name] = f"${min(valid)}"
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
