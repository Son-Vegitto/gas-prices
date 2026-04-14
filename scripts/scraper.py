import requests
import json
import os

stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

# These are the "Magic" headers that usually bypass the 400 error
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-gasbuddy-client-id": "GASBUDDY_WEB",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

prices = {}

for name, station_id in stations.items():
    try:
        print(f"Attempting API pull for {name}...")
        url = "https://www.gasbuddy.com/graphql"
        
        # This is a minimized query - less likely to trigger syntax-related 400s
        query = """
        query GetStation($id: ID!) {
          station(id: $id) {
            prices {
              fuelProduct
              credit { price }
              cash { price }
            }
          }
        }
        """
        
        payload = {
            "operationName": "GetStation",
            "variables": {"id": str(station_id)},
            "query": query
        }
        
        # We use a session to handle any cookie requirements automatically
        session = requests.Session()
        response = session.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            station_data = data.get('data', {}).get('station', {})
            
            if station_data and 'prices' in station_data:
                # Find Regular gas (fuelProduct is a string)
                regular_entry = next((p for p in station_data['prices'] if p.get('fuelProduct') == 'Regular'), None)
                
                if regular_entry:
                    # Logic: Credit price first, then Cash
                    price = regular_entry.get('credit', {}).get('price') or regular_entry.get('cash', {}).get('price')
                    prices[name] = f"${price}" if price else "N/A"
                else:
                    prices[name] = "N/A"
            else:
                prices[name] = "No Data"
        else:
            print(f"Error {response.status_code} for {name}")
            prices[name] = "Error"

    except Exception as e:
        print(f"Exception for {name}: {e}")
        prices[name] = "Error"

# Save the final synced data
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Success! Final data: {prices}")
