import requests
import re
import json
import os

stations = {
    "BJs": "https://www.google.com/search?q=BJs+Gas+Parsippany+NJ+gasbuddy+regular+price",
    "Jacks": "https://www.google.com/search?q=Jacks+Food+Mart+Parsippany+NJ+gasbuddy+regular+price",
    "Lukoil": "https://www.google.com/search?q=Lukoil+Parsippany+NJ+US-46+gasbuddy+regular+price"
}

# Standard headers to look like a desktop browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

prices = {}

for name, url in stations.items():
    try:
        print(f"Checking Google for {name} price...")
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text

        # Search for a price pattern like "$3.92" or "3.92" 
        # specifically in a context that looks like a search snippet.
        # We look for a 3 followed by a dot and two digits.
        match = re.search(r'\$(\d\.\d{2})', html)
        
        if match:
            prices[name] = f"${match.group(1)}"
        else:
            # Fallback for when the $ sign isn't there
            match_no_dollar = re.search(r'\s(\d\.\d{2})\s', html)
            if match_no_dollar:
                prices[name] = f"${match_no_dollar.group(1)}"
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
