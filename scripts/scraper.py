import requests
import re
import json
import os

stations = {
    "BJs": "https://www.mapquest.com/us/new-jersey/bjs-gas-423589921",
    "Jacks": "https://www.mapquest.com/us/new-jersey/jacks-food-mart-359528652",
    "Lukoil": "https://www.mapquest.com/us/new-jersey/lukoil-304419961"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

prices = {}

for name, url in stations.items():
    try:
        print(f"Polling MapQuest for {name}...")
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text

        # MapQuest stores gas prices in a very predictable format in their HTML
        # Look for the price followed by 'Regular'
        # Pattern: "price":"3.95","label":"Regular"
        match = re.search(r'"price":"(\d\.\d{2})","label":"Regular"', html)
        
        if match:
            prices[name] = f"${match.group(1)}"
        else:
            # Fallback: Just look for the first X.XX price on the page
            # MapQuest pages for gas stations are very clean.
            fallback = re.search(r'(\d\.\d{2})', html)
            if fallback:
                prices[name] = f"${fallback.group(1)}"
            else:
                prices[name] = "N/A"
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save to public folder
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
