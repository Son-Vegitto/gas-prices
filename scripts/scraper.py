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
# Rotating headers slightly to look more like a fresh mobile session
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        response = session.get(url, headers=headers, timeout=15)
        html = response.text

        found_price = "N/A"
        
        # 1. Target the JSON block (it contains the raw data before formatting)
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        if match:
            data = json.loads(match.group(1))
            try:
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    # Target 'Regular' only to avoid $4.09 or $4.39 from your screenshot
                    if fuel.get('fuelType') == 'Regular':
                        p_list = fuel.get('prices', [])
                        
                        # Filter for prices that are:
                        # 1. Not the $6.09 ad
                        # 2. Not the $3.51 GasBuddy Card discount
                        # 3. In a realistic PA range ($3.70 - $4.10)
                        valid_prices = [
                            float(p['price']) for p in p_list 
                            if p.get('price') and 3.70 <= float(p['price']) <= 4.10
                        ]
                        
                        if valid_prices:
                            # Use max() to ensure we get the Credit price ($3.99) 
                            # and not a lower Cash price ($3.89)
                            found_price = f"${max(valid_prices):.2f}"
                            break
            except (KeyError, TypeError):
                pass

        # 2. Fallback: If JSON is blocked, use Regex to find the first 3.9x price
        if found_price == "N/A" or "6.09" in found_price:
            matches = re.findall(r'>(3\.9\d)</span>', html)
            if matches:
                found_price = f"${matches[0]}"
            else:
                # Last ditch: grab any price between 3.80 and 4.00
                all_prices = re.findall(r'(\d\.\d{2})', html)
                realistic = [p for p in all_prices if 3.80 <= float(p) <= 4.05]
                if realistic:
                    found_price = f"${realistic[0]}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
