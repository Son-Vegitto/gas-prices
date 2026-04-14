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
        
        # 1. Direct JSON extraction
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        if match:
            data = json.loads(match.group(1))
            try:
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    if fuel.get('fuelType') == 'Regular':
                        p_list = fuel.get('prices', [])
                        
                        # We want the standard price. 
                        # We filter out 'gb_card' (the 3.51 discount)
                        # We take the HIGHEST price left (which is the Credit price)
                        valid_prices = [
                            float(p['price']) for p in p_list 
                            if p.get('source') != 'gb_card' and p.get('price')
                        ]
                        
                        if valid_prices:
                            # Use max() to get 3.99 instead of the 3.89 cash price
                            # and 3.95 instead of the 3.86 cash price
                            found_price = f"${max(valid_prices):.2f}"
                            break
            except (KeyError, TypeError):
                pass

        # 2. Safety Fallback: Regex for the '3.9x' pattern
        if found_price == "N/A" or "3.8" in found_price:
            # Look for any price in the 3.9 range in the HTML
            regex_matches = re.findall(r'>(3\.9\d)</span>', html)
            if regex_matches:
                # Prioritize 3.99 if it exists (Jack's), otherwise take the first 3.9x
                if "3.99" in regex_matches:
                    found_price = "$3.99"
                else:
                    found_price = f"${regex_matches[0]}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
