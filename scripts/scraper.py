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
            
            # The library method name is now get_station_and_prices
            # It returns a station object with a 'prices' list
            station = await gb.get_station_and_prices(s_id)
            
            regular_price = "N/A"
            
            if station and station.prices:
                # The library organizes these by fuel type
                for p in station.prices:
                    if p.fuel_type.lower() == "regular":
                        # Some stations report cash vs credit; we'll take credit first
                        val = p.credit_price or p.cash_price
                        if val:
                            regular_price = f"${val}"
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
