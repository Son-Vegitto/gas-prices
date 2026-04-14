import requests
import json
import os
from bs4 import BeautifulSoup

stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

prices = {}

for name, station_id in stations.items():
    try:
        print(f"Polling GasBuddy Data for {name}...")
        url = f"https://www.gasbuddy.com/station/{station_id}"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the first span where the class contains the core price module name
            # This ignores the random letters/numbers at the end that GasBuddy rotates
            price_span = soup.find('span', class_=lambda c: c and 'FuelTypePriceDisplay-module__price' in c)
            
            if price_span:
                # Extract the text (e.g., "$3.85")
                price = price_span.text.strip()
                prices[name] = price
            else:
                prices[name] = "N/A"
        else:
            print(f"Failed to fetch {name}: HTTP {response.status_code}")
            prices[name] = "Error"

    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save the final synced data
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
