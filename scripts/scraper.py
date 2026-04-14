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

        # 1. Look for the "Hero" price in the visual HTML first.
        # GasBuddy displays the current Regular price in a very specific span.
        # It usually looks like: <span class="...">3.99</span>
        # We search for the first price that is NOT the 'Pay with GasBuddy' discount.
        
        # This regex looks for a price that is NOT 3.24 or 3.51 (common discounts)
        all_visual_prices = re.findall(r'>(\d\.\d{2})</span>', html)
        
        # Filter out the lower "GasBuddy Card" prices we saw in your screenshot ($3.51, etc)
        # We want the standard price, which is usually the HIGHEST of the Regular options.
        valid_pump_prices = [p for p in all_visual_prices if float(p) > 3.60]

        if valid_pump_prices:
            # The first large price in the list is almost always the Regular Credit price.
            prices[name] = f"${valid_pump_prices[0]}"
        else:
            # Fallback to the JSON block if visual fails
            json_pattern = r'"fuelType":"Regular".*?"price":(\d\.\d{2})'
            match = re.search(json_pattern, html)
            if match:
                prices[name] = f"${match.group(1)}"
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
