import requests
import json
import os

stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

# This is a public API endpoint often used by their mobile-web integration
API_URL = "https://www.gasbuddy.com/assets-v2/api/stations"

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json",
    "referer": "https://www.gasbuddy.com/home",
    "x-gasbuddy-app-id": "gasbuddy-web"
}

prices = {}

for name, s_id in stations.items():
    try:
        print(f"Polling API for {name}...")
        # Direct hit to the station's JSON data
        response = requests.get(f"{API_URL}/{s_id}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            fuels = data.get('fuels', [])
            
            found_price = "N/A"
            for f in fuels:
                # We specifically want 'Regular' gas
                if f.get('fuelType') == 'Regular' or f.get('fuelTypeId') == 1:
                    # Priority: Credit Price -> Cash Price
                    val = f.get('creditPrice') or f.get('cashPrice')
                    if val:
                        found_price = f"${val}"
                        break
            prices[name] = found_price
        else:
            print(f"API Error {response.status_code} for {name}")
            prices[name] = "N/A"
            
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save the results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
