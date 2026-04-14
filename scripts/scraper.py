import cloudscraper
from bs4 import BeautifulSoup
import json

# Your exact stations
stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

# Using cloudscraper to bypass basic bot protection
scraper = cloudscraper.create_scraper()
prices = {}

for name, url in stations.items():
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # GasBuddy hides their structured data in this script tag
        next_data = soup.find('script', id='__NEXT_DATA__')
        
        if next_data:
            data = json.loads(next_data.string)
            # NOTE: You may need to `print(data)` and inspect the JSON structure locally 
            # to find the exact path to the "Regular" price depending on site updates.
            # It is typically buried somewhere like this:
            # price = data['props']['pageProps']['station']['fuels'][0]['prices'][0]['price']
            
            # Placeholder for where you map the exact JSON path:
            prices[name] = "$3.29" # Replace with actual parsed variable
        else:
            prices[name] = "N/A"
    except Exception as e:
        prices[name] = "Error"

# Save to a simple JSON file
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)
