import os
import json
import asyncio
from py_gasbuddy import GasBuddy

async def main():
    # Your station IDs
    stations_to_track = {
        "BJs": "26758",
        "Jacks": "33030",
        "Lukoil": "7072"
    }

    gb = GasBuddy()
    prices = {}

    for name, s_id in stations_to_track.items():
        try:
            print(f"Fetching {name} (ID: {s_id})...")
            
            # Using the exact method from your debug log
            # In this version, price_lookup returns a list of price objects
            station_data = await gb.price_lookup(s_id)
            
            regular_price = "N/A"
            
            if station_data:
                for p in station_data:
                    # Check for 'regular' fuel type
                    # The library usually returns objects with 'type' and 'price'
                    fuel_type = getattr(p, 'type', '').lower()
                    if fuel_type == "regular":
                        price_val = getattr(p, 'price', None)
                        if price_val:
                            regular_price = f"${price_val}"
                        break
            
            prices[name] = regular_price
            
        except Exception as e:
            print(f"Error fetching {name}: {str(e)}")
            prices[name] = "Error"

    # Save to public/gas_prices.json
    os.makedirs('public', exist_ok=True)
    with open('public/gas_prices.json', 'w') as f:
        json.dump(prices, f)
    
    print(f"Final Data Saved: {prices}")

if __name__ == "__main__":
    asyncio.run(main())
    
