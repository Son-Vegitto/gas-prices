import requests
import json
import os

stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/json"
}

prices = {}

for name, station_id in stations.items():
    try:
        print(f"Polling GasBuddy GraphQL API for {name}...")
        url = "https://www.gasbuddy.com/graphql"
        
        # This is the exact query GasBuddy's own website uses to ask the database for prices
        payload = {
            "operationName": "GetStation",
            "variables": {"id": str(station_id)},
            "query": "query GetStation($id: ID!) { station(id: $id) { prices { credit { price } cash { price } } } }"
        }
        
        # We use a POST request to hit their API
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            try:
                # Navigate through the JSON response to find the prices list
                station_data = data.get('data', {}).get('station', {})
                
                if station_data and station_data.get('prices'):
                    # The first item in the prices list typically corresponds to 'Regular'
                    regular_price_data = station_data['prices'][0]
                    
                    price_val = None
                    
                    # Try to grab the credit price first, fallback to cash price
                    if regular_price_data.get('credit') and regular_price_data['credit'].get('price'):
                        price_val = regular_price_data['credit']['price']
                    elif regular_price_data.get('cash') and regular_price_data['cash'].get('price'):
                        price_val = regular_price_data['cash']['price']
                        
                    if price_val:
                        prices[name] = f"${price_val}"
                    else:
                        prices[name] = "N/A"
                else:
                    prices[name] = "N/A"
            except (KeyError, IndexError, TypeError):
                prices[name] = "Parse Error"
        else:
            print(f"Failed to fetch {name}: HTTP {response.status_code}")
            prices[name] = f"HTTP Error"

    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save the final synced data
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
