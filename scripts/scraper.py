import cloudscraper
import re
import json
import os

stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

# We'll use a very specific desktop user agent to look like a human browsing on Chrome
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        response = scraper.get(url, timeout=15)
        html = response.text

        # GasBuddy's price display usually looks like this in the raw HTML:
        # <span class="...">3.95</span>...<span>Regular</span>
        # We'll search for a price pattern that is followed by 'Regular' within 200 characters
        
        # This regex looks for: 
        # 1. A price ($X.XX)
        # 2. A bunch of junk/tags in between (up to 300 characters)
        # 3. The word 'Regular'
        regex_pattern = r'(\d\.\d{2})<.*?Regular'
        
        # We use re.DOTALL to make sure the dot matches newlines too
        match = re.search(regex_pattern, html, re.IGNORECASE | re.DOTALL)
        
        if match:
            prices[name] = f"${match.group(1)}"
        else:
            # Plan B: Try to find any price that is NOT 6.09 (the ad price)
            all_prices = re.findall(r'(\d\.\d{2})', html)
            # Remove common 'ad' prices if they appear
            filtered_prices = [p for p in all_prices if p not in ["6.09", "0.00"]]
            
            if filtered_prices:
                prices[name] = f"${filtered_prices[0]}"
            else:
                prices[name] = "N/A"
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
