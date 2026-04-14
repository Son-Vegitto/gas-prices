import requests
import json
import os

stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

# We need more specific headers to satisfy GasBuddy's security
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gasbuddy-client-id": "GASBUDDY_WEB",
}

prices = {}

for name, station_id in stations.items():
    try:
        print(f"Polling GasBuddy GraphQL API for {name}...")
        url = "https://www.gasbuddy.com/graphql"
        
        # This expanded query specifically asks for the 'Regular' fuel type (fuelTypeId: 1)
        payload = {
            "operationName": "GetStation",
            "variables": {"id": str(station_id)},
            "query": """
            query GetStation($id: ID!) {
              station(id: $id) {
                prices {
                  fuelProduct
                  credit {
                    price
                  }
                  cash {
                    price
                  }
                }
              }
            }
            """
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            station_data = data.get('data', {}).get('station', {})
            
            if station_data and 'prices' in station_data:
                # Loop through products to find "Regular" (usually product 1)
                regular_price = "N/A"
                for p in station_data['prices']:
                    if p.get('fuelProduct') == 'Regular':
                        # Prefer credit price, then cash
                        val = p.get('credit', {}).get('price') or p.get('cash', {}).get('price')
                        if val:
                            regular_price = f"${val}"
                        break
                prices[name] = regular_price
            else:
                prices[name] = "N/A"
        else:
            print(f"Failed to fetch {name}: HTTP {response.status_code}")
            print(f"Response: {response.text}") # This will show us why it failed in the logs
            prices[name] = "HTTP Error"

    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save the final synced data
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
