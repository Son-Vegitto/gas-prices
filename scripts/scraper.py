import requests
import re
import json
import os

stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

# Use a session to look like a persistent mobile user
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name} via Mobile Emulation...")
        response = session.get(url, headers=headers, timeout=15)
        html = response.text

        # Use a very specific regex to find the price inside the Next.js data block
        # Look for the price value directly inside the "Regular" fuel block
        # pattern: "fuelType":"Regular","prices":[{"price":3.95
        match = re.search(r'"fuelType":"Regular".*?"price":(\d\.\d{2})', html)
        
        if match:
            prices[name] = f"${match.group(1)}"
        else:
            # Plan B: Look for any price-like string that isn't a common ad price
            all_prices = re.findall(r'(\d\.\d{2})', html)
            # Filter out known non-gas numbers we've seen before
            filtered = [p for p in all_prices if 2.50 < float(p) < 5.50]
            if filtered:
                prices[name] = f"${filtered[0]}"
            else:
                prices[name] = "N/A"
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
