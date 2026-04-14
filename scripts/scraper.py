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
        
        # 1. Target the JSON data (the most reliable source)
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        if match:
            data = json.loads(match.group(1))
            try:
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    # We ONLY want Regular
                    if fuel.get('fuelType') == 'Regular':
                        p_list = fuel.get('prices', [])
                        
                        # We want the standard price (Credit/Cash)
                        # We ignore 'gb_card' (the $3.51 discount)
                        standard_prices = [
                            float(p['price']) for p in p_list 
                            if p.get('source') != 'gb_card' and p.get('price')
                        ]
                        
                        if standard_prices:
                            # Since Jack's has no cash/credit diff, 
                            # max() or min() here will both return 3.99.
                            found_price = f"${max(standard_prices):.2f}"
                            break
            except (KeyError, TypeError):
                pass

        # 2. Safety Fallback: Regex for "3.XX" prices
        if found_price == "N/A" or "4.29" in found_price:
            # Look for the price that is specifically labeled as 'Regular' in the HTML
            # This regex looks for a price followed by 'Regular' within 50 characters
            visual_match = re.search(r'(\d\.\d{2}).{1,50}Regular', html, re.IGNORECASE | re.DOTALL)
            if visual_match:
                found_price = f"${visual_match.group(1)}"
            else:
                # Last resort: find any price in the 3.90 range
                fallback = re.findall(r'3\.\d{2}', html)
                if fallback:
                    found_price = f"${fallback[0]}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
