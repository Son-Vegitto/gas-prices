import requests
import json
import os

# Station IDs from your URLs
station_ids = {
    "BJs": "26758",
    "Jacks": "33030",
    "Lukoil": "7072"
}

def get_gas_price(station_id):
    # Using their internal GraphQL-like endpoint logic
    url = "https://www.gasbuddy.com/assets-v2/api/stations"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "referer": f"https://www.gasbuddy.com/station/{station_id}"
    }
    
    try:
        # We fetch the station data directly
        response = requests.get(f"{url}/{station_id}", headers=headers, timeout=20)
        data = response.json()
        
        # We look for 'Regular' in the fuels list
        fuels = data.get('fuels', [])
        for fuel in fuels:
            if fuel.get('fuelType') == 'Regular':
                prices = fuel.get('prices', [])
                # Filter out the $6.09 ad and the $3.51 GasBuddy card discount
                # We want the 'Credit' price which is the highest standard price
                valid_prices = [
                    float(p['price']) for p in prices 
                    if p.get('price') and 3.60 < float(p['price']) < 5.00
                ]
                
                if valid_prices:
                    # max() ensures we get $3.99 (Credit) instead of $3.89 (Cash)
                    return f"${max(valid_prices):.2f}"
        
        return "N/A"
    except Exception as e:
        print(f"Error fetching ID {station_id}: {e}")
        return "Error"

# Main execution
final_prices = {}
for name, sid in station_ids.items():
    print(f"Polling API for {name}...")
    final_prices[name] = get_gas_price(sid)

# Save to public folder for your widget
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(final_prices, f)

print(f"Final Outcome: {final_prices}")
