import cloudscraper
import re
import json
import os

stations = {
    "BJs": "BJ's Gas 165 New Rd Parsippany NJ gas prices",
    "Jacks": "Jacks Food Mart Parsippany NJ gas prices",
    "Lukoil": "Lukoil 1410 US-46 Parsippany NJ gas prices"
}

scraper = cloudscraper.create_scraper()

prices = {}

for name, query in stations.items():
    try:
        print(f"Searching for {name} prices...")
        # Search Google for the station price
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        response = scraper.get(search_url, timeout=15)
        
        # Look for a price pattern in the search results
        # Google often shows "$3.95" or similar in the snippet
        match = re.search(r'\$(\d\.\d{2})', response.text)
        
        if match:
            prices[name] = f"${match.group(1)}"
        else:
            prices[name] = "N/A"
            
    except Exception as e:
        print(f"Error searching {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
