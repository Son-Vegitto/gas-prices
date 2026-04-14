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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        response = session.get(url, headers=headers, timeout=15)
        html = response.text

        # 1. Find the word 'Regular' and the first price ($X.XX) that follows it.
        # This bypasses the hidden metadata and grabs what's visually near the label.
        # Pattern: Find 'Regular', then skip up to 300 chars of HTML, then find X.XX
        match = re.search(r'Regular.*?(\d\.\d{2})', html, re.IGNORECASE | re.DOTALL)
        
        if match:
            val = match.group(1)
            # Validate: If it's too low (like 3.24 or 3.51 from the GB card), 
            # we keep looking for the next one.
            if float(val) < 3.60:
                # Search again but skip the first match
                second_match = re.search(r'Regular.*?(\d\.\d{2}).*?(\d\.\d{2})', html, re.IGNORECASE | re.DOTALL)
                if second_match:
                    prices[name] = f"${second_match.group(2)}"
                else:
                    prices[name] = f"${val}"
            else:
                prices[name] = f"${val}"
        else:
            # Plan B: Direct JSON search for the 'price' field
            json_match = re.search(r'"fuelType":"Regular".*?"price":(\d\.\d{2})', html)
            if json_match:
                prices[name] = f"${json_match.group(1)}"
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
