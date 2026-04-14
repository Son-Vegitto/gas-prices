import cloudscraper
import json
import os

stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

scraper = cloudscraper.create_scraper()

# This is the exact query the GasBuddy website sends
query = """
query GetStationPrices($id: ID!) {
    station(id: $id) {
        prices {
            fuel
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

prices = {}

for name, s_id in stations.items():
    try:
        print(f"Fetching {name}...")
        
        response = scraper.post(
            "https://www.gasbuddy.com/graphql",
            json={
                "operationName": "GetStationPrices",
                "variables": {"id": s_id},
                "query": query
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            station_prices = data.get('data', {}).get('station', {}).get('prices', [])
            
            found_price = "N/A"
            for p in station_prices:
                # We want regular gas
                if p.get('fuel') == 'regular':
                    # Check credit first, then cash
                    val = p.get('credit', {}).get('price') or p.get('cash', {}).get('price')
                    if val:
                        found_price = f"${val}"
                    break
            prices[name] = found_price
        else:
            print(f"Error {response.status_code} for {name}")
            prices[name] = "N/A"
            
    except Exception as e:
        print(f"Failed {name}: {e}")
        prices[name] = "Error"

# Save the results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final results: {prices}")
