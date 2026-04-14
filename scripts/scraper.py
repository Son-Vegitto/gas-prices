import os
import json
import asyncio
from gasbuddy import GasBuddy

async def main():
    # Your station IDs
    station_ids = {
        "BJs": 26758,
        "Jacks": 33030,
        "Lukoil": 7072
    }

    gb = GasBuddy()
    prices = {}

    for name, s_id in station_ids.items():
        try:
            print(f"Fetching data for {name}...")
            # This fetches the full station object
            station = await gb.get_station(s_id)
            
            # Navigate the station object to find Regular fuel
            regular_price = "N/A"
            if station.prices:
                for fuel in station.prices:
                    if fuel.fuel_type == "Regular":
                        # Get the credit price, fall back to cash if credit isn't listed
                        price_val = fuel.credit_price or fuel.cash_price
                        if price_val:
                            regular_price = f"${price_val}"
                        break
            
            prices[name] = regular_price
            
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            prices[name] = "Error"

    # Save the final file
    os.makedirs('public', exist_ok=True)
    with open('public/gas_prices.json', 'w') as f:
        json.dump(prices, f)
    
    print(f"Saved: {prices}")

if __name__ == "__main__":
    asyncio.run(main())
