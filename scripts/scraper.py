import requests
import re
import json
import os
import time

stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

# Real-world headers to bypass the basic bot-check
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
}

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        # Add a tiny sleep to avoid looking like a rapid-fire script
        time.sleep(2)
        
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text

        # 1. Look for the Price near 'Regular'
        # We search for 'Regular' and then the first 3.9x or 3.8x that follows it
        # This matches the 'Hero' price in your screenshot
        match = re.search(r'Regular.*?(\d\.\d{2})', html, re.IGNORECASE | re.DOTALL)
        
        if match:
            val = match.group(1)
            # Validation: If it grabs the $3.51 'GasBuddy Card' price, skip it and grab the next one
            if float(val) < 3.70:
                # Look for the SECOND price after 'Regular' (usually the Credit price)
                match_two = re.search(r'Regular.*?3\.\d{2}.*?(3\.\d{2})', html, re.IGNORECASE | re.DOTALL)
                if match_two:
                    prices[name] = f"${match_two.group(1)}"
                else:
                    prices[name] = f"${val}"
            else:
                prices[name] = f"${val}"
        else:
            # 2. Fallback: Search for any price in the 3.80-4.05 range
            all_prices = re.findall(r'(\d\.\d{2})', html)
            realistic = [p for p in all_prices if 3.80 <= float(p) <= 4.05]
            if realistic:
                # Take the highest (usually Credit)
                prices[name] = f"${max(realistic)}"
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
