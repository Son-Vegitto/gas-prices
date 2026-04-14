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

        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        found_price = "N/A"
        
        if match:
            data = json.loads(match.group(1))
            try:
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    if fuel.get('fuelType') == 'Regular':
                        p_list = fuel.get('prices', [])
                        # We want the price that is NOT the 'Pay with GasBuddy' price
                        # Often the standard price has a specific flag or is just the largest
                        valid_pump_prices = []
                        for p_entry in p_list:
                            p_val = p_entry.get('price')
                            # Ignore specific discounted prices if they are marked
                            # Or if they are significantly lower than others
                            if p_val:
                                valid_pump_prices.append(float(p_val))
                        
                        if valid_pump_prices:
                            # Standard pump price is almost always the HIGHEST of the regular options
                            # (Discounted card prices are lower)
                            found_price = f"${max(valid_pump_prices)}"
                            break
            except (KeyError, TypeError):
                pass

        # Safety Fallback: Use the 'Max Price' rule in the $3.50-$4.50 range
        if found_price == "N/A":
            all_prices = re.findall(r'(\d\.\d{2})', html)
            valid = [float(p) for p in all_prices if 3.50 <= float(p) <= 4.50]
            if valid:
                found_price = f"${max(valid)}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
