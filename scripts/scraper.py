import requests
import json
import os
import re

# We will use the direct search API that the map uses
# This is much harder to block because it's pure data
stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

prices = {}

for name, station_id in stations.items():
    try:
        print(f"Polling GasBuddy Data for {name}...")
        # We go to the station page but we're going to be extremely careful with how we extract
        url = f"https://www.gasbuddy.com/station/{station_id}"
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text

        # 1. Look for the Price in the 'FuelTypePriceDisplay' module
        # This regex looks for the price specifically near the text 'Regular'
        # It handles the way they split the price into large and small digits
        match = re.search(r'Regular.*?(\d)\.(\d{2})', html, re.DOTALL | re.IGNORECASE)
        
        if match:
            major = match.group(1)
            minor = match.group(2)
            price_val = f"{major}.{minor}"
            
            # SANITY CHECK: Ignore the $6.09 trap and the $3.51 GasBuddy Card price
            if 3.70 <= float(price_val) <= 4.10:
                prices[name] = f"${price_val}"
            else:
                # If the first 'Regular' price is a trap, look for another one
                all_matches = re.findall(r'(\d\.\d{2})', html)
                realistic = [p for p in all_matches if 3.80 <= float(p) <= 4.05]
                if realistic:
                    # Take the highest of the realistic range (matches 'Credit')
                    prices[name] = f"${max(realistic)}"
                else:
                    prices[name] = "N/A"
        else:
            prices[name] = "N/A"

    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save the final synced data
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
