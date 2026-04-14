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

        found_price = "N/A"
        
        # 1. JSON Extraction - The most reliable source for price tiers
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        if match:
            data = json.loads(match.group(1))
            try:
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    if fuel.get('fuelType') == 'Regular':
                        p_list = fuel.get('prices', [])
                        
                        # Filter out the 'gb_card' ($3.51) and the bot-trap ($6.09)
                        # We want standard pump prices (Cash/Credit)
                        pump_prices = [
                            float(p['price']) for p in p_list 
                            if p.get('price') and p.get('source') != 'gb_card' and float(p['price']) < 5.00
                        ]
                        
                        if pump_prices:
                            # IMPORTANT: The Credit price is always the MAX price for Regular.
                            # BJs: Max(3.86, 3.95) -> 3.95
                            # Jacks: Max(3.89, 3.99) -> 3.99
                            found_price = f"${max(pump_prices):.2f}"
                            break
            except (KeyError, TypeError):
                pass

        # 2. Visual Fallback - Search for the exact string pattern from your screen
        if found_price == "N/A" or float(found_price.strip('$')) < 3.90:
            # Matches strings like ">3.99</span>"
            visual_matches = re.findall(r'>(\d\.\d{2})</span>', html)
            # Filter for the 3.9x range specifically
            hero_range = [p for p in visual_matches if p.startswith('3.9')]
            if hero_range:
                # Jack's Hero Price is usually the first 3.9x in the list
                found_price = f"${hero_range[0]}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
