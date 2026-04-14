import os
import json
import asyncio
import inspect
from py_gasbuddy import GasBuddy

async def main():
    stations_to_track = {
        "BJs": "26758",
        "Jacks": "33030",
        "Lukoil": "7072"
    }

    gb = GasBuddy()
    prices = {}

    # 1. Inspect the library to see what the argument name actually is
    # This prevents the "unexpected keyword argument" error
    sig = inspect.signature(gb.price_lookup)
    arg_name = list(sig.parameters.keys())[0] 
    print(f"Library is expecting argument name: {arg_name}")

    for name, s_id in stations_to_track.items():
        try:
            print(f"Fetching {name} (ID: {s_id})...")
            
            # 2. Call the function using the dynamically discovered argument name
            kwargs = {arg_name: s_id}
            station_data = await gb.price_lookup(**kwargs)
            
            regular_price = "N/A"
            
            if station_data:
                # Some versions return a list, some return a single object
                items = station_data if isinstance(station_data, list) else [station_data]
                
                for p in items:
                    # Check for 'regular' or 'unleaded'
                    fuel_type = getattr(p, 'type', getattr(p, 'fuel_type', '')).lower()
                    if fuel_type in ["regular", "unleaded"]:
                        price_val = getattr(p, 'price', getattr(p, 'credit_price', None))
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
