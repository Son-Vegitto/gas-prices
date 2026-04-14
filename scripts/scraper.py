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

        # 1. Extract the raw JSON data blob
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        found_price = "N/A"
        
        if match:
            data = json.loads(match.group(1))
            try:
                # Digging into the actual station data structure
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    # We only want Regular
                    if fuel.get('fuelType') == 'Regular':
                        # Get the 'prices' list
                        p_list = fuel.get('prices', [])
                        if p_list:
                            # Use the real price, not the 'pay with card' price
                            val = p_list[0].get('price')
                            if val:
                                found_price = f"${val}"
                                break
            except (KeyError, TypeError):
                pass

        # 2. Safety Fallback: If JSON is scrambled, use the 'Min Price' rule 
        # but exclude known decoy numbers like 2.55
        if found_price == "N/A" or found_price == "$2.55":
            all_prices = re.findall(r'(\d\.\d{2})', html)
            # Filter for realistic NJ prices (between $3.50 and $4.50)
            valid = [float(p) for p in all_prices if 3.50 <= float(p) <= 4.50]
            if valid:
                found_price = f"${min(valid)}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
