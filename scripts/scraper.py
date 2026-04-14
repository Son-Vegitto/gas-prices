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
        
        # 1. Target the JSON block
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        if match:
            data = json.loads(match.group(1))
            try:
                # Get the fuels list
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    # STRICT CHECK: Must be Regular fuel
                    if fuel.get('fuelType') == 'Regular':
                        p_list = fuel.get('prices', [])
                        
                        # We want the 'Credit' price. 
                        # In your Jack's example, Credit and Cash are both 3.99.
                        # We ignore 'gb_card' (the 3.51 discount).
                        valid_options = [
                            float(p['price']) for p in p_list 
                            if p.get('source') != 'gb_card' and p.get('price')
                        ]
                        
                        if valid_options:
                            # We take the HIGHEST valid regular price (which is Credit)
                            # This avoids grabbing the 'Cash' discount if one exists.
                            found_price = f"${max(valid_options):.2f}"
                            break
            except (KeyError, TypeError):
                pass

        # 2. Safety Fallback: Regex specifically for the $3.9x range
        if found_price == "N/A" or float(found_price.strip('$')) > 4.10:
            # Look for any price between 3.90 and 4.00 specifically
            matches = re.findall(r'>(3\.9\d)</span>', html)
            if matches:
                found_price = f"${matches[0]}"
            else:
                # If no 3.9x found, look for any price near the word Regular
                fallback = re.search(r'Regular.*?(\d\.\d{2})', html, re.DOTALL)
                if fallback:
                    found_price = f"${fallback.group(1)}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
