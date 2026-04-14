import cloudscraper
from bs4 import BeautifulSoup
import json
import os

stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'android',
        'desktop': False
    }
)

prices = {}

for name, url in stations.items():
    try:
        print(f"Fetching {name}...")
        response = scraper.get(url, timeout=10)
        
        if response.status_code != 200:
            prices[name] = f"Error {response.status_code}"
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        next_data = soup.find('script', id='__NEXT_DATA__')
        
        if next_data:
            data = json.loads(next_data.string)
            # Navigate the JSON tree to find the fuel list
            # The structure is usually props -> pageProps -> station -> fuels
            fuels = data.get('props', {}).get('pageProps', {}).get('station', {}).get('fuels', [])
            
            found_price = "N/A"
            for fuel in fuels:
                # We only want Regular (case insensitive check)
                if fuel.get('fuelType', '').lower() == 'regular':
                    price_list = fuel.get('prices', [])
                    if price_list:
                        # Grab the most recent price (first in list)
                        val = price_list[0].get('price')
                        found_price = f"${val}" if val else "N/A"
                    break
            prices[name] = found_price
        else:
            prices[name] = "No Data"
            
    except Exception as e:
        print(f"Failed to scrape {name}: {e}")
        prices[name] = "Error"

# Ensure the public directory exists
os.makedirs('public', exist_ok=True)

# Save to the specific file your GitHub Action is looking for
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)
    print("File saved successfully.")
