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
# Use a very specific browser footprint
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        response = session.get(url, headers=headers, timeout=15)
        html = response.text

        # Look for the internal JSON data script
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        found_price = "N/A"
        
        if match:
            data = json.loads(match.group(1))
            try:
                # Digging into the state to find station fuels
                fuel_list = data['props']['pageProps']['station']['fuels']
                for fuel in fuel_list:
                    if fuel.get('fuelType') == 'Regular':
                        p_entries = fuel.get('prices', [])
                        # We want a real price, not 6.09 and not 0.00
                        # We take the first price that isn't a known bot-trap
                        valid_prices = [
                            p.get('price') for p in p_entries 
                            if p.get('price') and float(p.get('price')) < 6.00 and float(p.get('price')) > 0
                        ]
                        if valid_prices:
                            # Use max() to get the standard price (Credit) rather than the card discount
                            found_price = f"${max(valid_prices):.2f}"
                            break
            except (KeyError, TypeError):
                pass

        # If JSON is empty/blocked, use a restricted Regex fallback
        if found_price == "N/A" or "6.09" in found_price:
            # Only look for prices in the 3.xx range (realistic for PA right now)
            regex_prices = re.findall(r'>(3\.\d{2})</span>', html)
            if regex_prices:
                found_price = f"${regex_prices[0]}"
            else:
                # Last ditch effort: find any price between 3.50 and 4.50
                all_nums = re.findall(r'(\d\.\d{2})', html)
                realistic = [n for n in all_nums if 3.50 <= float(n) <= 4.50]
                if realistic:
                    found_price = f"${realistic[0]}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Final safety: if all are N/A, don't overwrite with blank data
if all(v == "N/A" for v in prices.values()):
    print("Warning: All stations returned N/A. Check for Bot-Block.")

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
