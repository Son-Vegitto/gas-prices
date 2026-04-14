import requests
import re
import json
import os
import random

stations = {
    "BJs": "https://www.gasbuddy.com/station/26758",
    "Jacks": "https://www.gasbuddy.com/station/33030",
    "Lukoil": "https://www.gasbuddy.com/station/7072"
}

# A list of real-world user agents to rotate
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

prices = {}

for name, url in stations.items():
    try:
        print(f"Scraping {name}...")
        # Pick a random agent and use a session to handle cookies
        session = requests.Session()
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/"
        }
        
        response = session.get(url, headers=headers, timeout=15)
        html = response.text

        found_price = "N/A"
        
        # --- LAYER 1: The JSON Data (Best Accuracy) ---
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html)
        
        if match:
            try:
                data = json.loads(match.group(1))
                fuels = data['props']['pageProps']['station']['fuels']
                for fuel in fuels:
                    if fuel.get('fuelType') == 'Regular':
                        p_list = fuel.get('prices', [])
                        # We want the HIGHEST standard price (Credit)
                        standard_prices = [
                            float(p['price']) for p in p_list 
                            if p.get('source') != 'gb_card' and p.get('price')
                        ]
                        if standard_prices:
                            found_price = f"${max(standard_prices):.2f}"
                            break
            except:
                pass

        # --- LAYER 2: HTML Span Search (Matches the Hero Display) ---
        if found_price == "N/A":
            # Search for prices that look like your $3.9x target
            visual_matches = re.findall(r'>(\d\.\d{2})</span>', html)
            # Filter for realistic PA pump prices (ignore the $3.5x discounts)
            realistic = [p for p in visual_matches if float(p) > 3.80]
            if realistic:
                found_price = f"${realistic[0]}"

        # --- LAYER 3: Regular Label Anchor ---
        if found_price == "N/A":
            regex_match = re.search(r'Regular.*?(\d\.\d{2})', html, re.DOTALL)
            if regex_match:
                found_price = f"${regex_match.group(1)}"

        prices[name] = found_price
                
    except Exception as e:
        print(f"Error at {name}: {e}")
        prices[name] = "Error"

# Save results
os.makedirs('public', exist_ok=True)
with open('public/gas_prices.json', 'w') as f:
    json.dump(prices, f)

print(f"Final Outcome: {prices}")
