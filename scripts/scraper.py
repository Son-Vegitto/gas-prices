import cloudscraper
import json
import os

stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

# We need specific headers to look exactly like a real browser
scraper = cloudscraper.create_scraper()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.gasbuddy.com/"
}

prices = {}

for name, s_id in stations.items():
    try:
        print(f"Fetching {name}...")
        # This is the direct API endpoint for station prices
        api_url = f"https://www.gasbuddy.com/assets-v2/api/stations/{s_id}"
        
        response = scraper.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # The API returns a 'fuels' list
            fuels = data.get('fuels', [])
            
            found_price = "N/A"
            for fuel in fuels:
                # GasBuddy API uses 'Regular' or 1 for regular gas
                if fuel.get('fuelType') == 'Regular' or fuel.get('fuelTypeId') == 1:
                    # Check for credit price, then cash price
                    val = fuel.get('creditPrice') or fuel.get('cashPrice')
                    if val:
                        found_price = f"${val}"
                    break
            prices[name] = found_price
        else:
            print(f"API Error {response.status_code} for {name}")
            prices[name] = "N/A"
            
    except Exception as e:
        print(f"Failed {name}: {e}")
        prices[name] = "Error"

# Save the file
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final results: {prices}")
