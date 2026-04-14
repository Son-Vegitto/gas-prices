import cloudscraper
import json
import os

# Your specific station IDs
stations = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

# Mimic a real browser request
scraper = cloudscraper.create_scraper()
prices = {}

# The GraphQL query GasBuddy uses to get station info
graphql_query = """
query GetStation($id: ID!) {
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

for name, station_id in stations.items():
    try:
        print(f"Requesting data for {name}...")
        
        # Send a POST request to their API endpoint
        response = scraper.post(
            "https://www.gasbuddy.com/graphql",
            json={
                "operationName": "GetStation",
                "variables": {"id": station_id},
                "query": graphql_query
            },
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # Navigate to the list of prices
            price_data = data.get('data', {}).get('station', {}).get('prices', [])
            
            # Find 'regular' (usually the first item)
            regular_price = "N/A"
            for p in price_data:
                if p.get('fuel') == 'regular':
                    # Try credit price first, then cash
                    val = p.get('credit', {}).get('price') or p.get('cash', {}).get('price')
                    if val:
                        regular_price = f"${val}"
                    break
            
            prices[name] = regular_price
        else:
            print(f"API Error for {name}: {response.status_code}")
            prices[name] = "Error"
            
    except Exception as e:
        print(f"Failed to fetch {name}: {e}")
        prices[name] = "Error"

# Save to the file your GitHub Action expects
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Data: {prices}")
