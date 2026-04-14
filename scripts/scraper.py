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
            
            # TRY 1: The standard 2026 method
            try:
                station = await gb.get_station(s_id)
            except AttributeError:
                # TRY 2: Fallback if the library is in a transitional state
                print(f"Method not found, trying search fallback...")
                station = await gb.get_station_details(s_id)
            
            regular_price = "N/A"
            
            if station and hasattr(station, 'prices') and station.prices:
                for p in station.prices:
                    # Look for Regular (checking both .fuel_type and .fuel)
                    fuel_name = getattr(p, 'fuel_type', getattr(p, 'fuel', '')).lower()
                    if fuel_name == "regular":
                        # Get credit or cash
                        val = getattr(p, 'credit_price', getattr(p, 'price', None)) or getattr(p, 'cash_price', None)
                        if val:
                            regular_price = f"${val}"
                        break
            
            prices[name] = regular_price
            
        except Exception as e:
            print(f"Error fetching {name}: {str(e)}")
            # This will help us debug if the method name changed again
            print(f"Available methods in gb object: {dir(gb)}")
            prices[name] = "Error"

    # Save to public/gas_prices.json
    os.makedirs('public', exist_ok=True)
    with open('public/gas_prices.json', 'w') as f:
        json.dump(prices, f)
    
    print(f"Final Data Saved: {prices}")

if __name__ == "__main__":
    asyncio.run(main())
    
