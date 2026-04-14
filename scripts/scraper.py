import requests
import json
import os
import re

stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

prices = {}

for name, station_id in stations.items():
    try:
        print(f"Fetching page for {name}...")
        url = f"https://www.gasbuddy.com/station/{station_id}"
        
        # We use a session to look more like a real person
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            
            # GasBuddy stores its data in a JSON object inside a <script> tag.
            # We are looking for "creditPrice": 3.85 or "price": 3.85 near "Regular"
            # This regex looks for the price specifically associated with Regular fuel
            pattern = r'\"fuelProduct\":\"Regular\".*?\"price\":(\d+\.\d+)'
            match = re.search(pattern, html)
            
            if match:
                price_val = match.group(1)
                prices[name] = f"${price_val}"
                print(f"Found {name}: ${price_val}")
            else:
                # Fallback: look for any price-like decimal if the specific pattern fails
                # This helps if they change the JSON structure slightly
                backup_pattern = r'\"price\":(\d+\.\d+)'
                matches = re.findall(backup_pattern, html)
                if matches:
                    prices[name] = f"${matches[0]}"
                else:
                    prices[name] = "N/A"
        else:
            print(f"HTTP {response.status_code} for {name}")
            prices[name] = "Error"

    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save data
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
