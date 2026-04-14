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

        # 1. Grab the JSON data blob
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        found_price = "N/A"
        
        if match:
            data = json.loads(match.group(1))
            try:
                # Target: pageProps -> station -> fuels
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    if fuel.get('fuelType') == 'Regular':
                        p_list = fuel.get('prices', [])
                        # Standard pump price is usually the last one in the list 
                        # or the one with the highest value (non-discounted)
                        vals = [float(p['price']) for p in p_list if p.get('price')]
                        if vals:
                            # We want the highest realistic price to avoid 'Member' discounts
                            # Filter out anything above $5.50 (likely premium/diesel errors)
                            realistic = [v for v in vals if v < 5.50]
                            if realistic:
                                found_price = f"${max(realistic):.2f}"
                                break
            except (KeyError, TypeError):
                pass

        # 2. Strict Fallback: Only match numbers with TWO decimal places (X.XX)
        # This prevents us from grabbing ratings like "4.5"
        if found_price == "N/A":
            # Regex looking for a price followed by the word 'Regular'
            # or a price inside a 'price' JSON key
            strict_matches = re.findall(r'"price":(\d\.\d{2})', html)
            if not strict_matches:
                strict_matches = re.findall(r'>(\d\.\d{2})</span>', html)
            
            if strict_matches:
                # Filter for NJ price range ($3.00 - $4.50)
                valid = [float(p) for p in strict_matches if 3.00 <= float(p) <= 4.50]
                if valid:
                    found_price = f"${max(valid):.2f}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
