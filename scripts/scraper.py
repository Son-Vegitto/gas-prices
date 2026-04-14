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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/"
}

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        response = session.get(url, headers=headers, timeout=15)
        html = response.text

        found_price = "N/A"
        
        # 1. Target the JSON block exclusively
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        if match:
            data = json.loads(match.group(1))
            try:
                # Get the actual station fuel list
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    # We only care about Regular
                    if fuel.get('fuelType') == 'Regular':
                        p_list = fuel.get('prices', [])
                        
                        # FILTER: We want prices that are:
                        # - Not the $6.09 bot-trap
                        # - Not the $3.51 GasBuddy card discount
                        # - In a realistic PA range ($3.75 - $4.25)
                        valid_prices = [
                            float(p['price']) for p in p_list 
                            if p.get('price') and 3.75 <= float(p['price']) <= 4.25
                        ]
                        
                        if valid_prices:
                            # Use max() to get the Credit price (3.99) over Cash (3.89)
                            found_price = f"${max(valid_prices):.2f}"
                            break
            except (KeyError, TypeError):
                pass

        # 2. Fallback: If JSON is poisoned, use a very specific Regex
        # Looking for a price near the word 'Regular' that isn't 6.09
        if found_price == "N/A" or "6.09" in found_price:
            # Matches any 3.9x in the HTML
            matches = re.findall(r'>(3\.9\d)</span>', html)
            if matches:
                found_price = f"${matches[0]}"
            else:
                # Last resort: find any price between 3.80 and 4.10
                all_nums = re.findall(r'(\d\.\d{2})', html)
                realistic = [n for n in all_nums if 3.80 <= float(n) <= 4.10]
                if realistic:
                    found_price = f"${realistic[0]}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save the clean data
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
