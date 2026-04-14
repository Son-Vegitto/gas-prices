import fs from "node:fs";
import path from "node:path";
import { load } from "cheerio";

const STATIONS = [
  { 
    id: "7072", 
    url: "https://www.mapquest.com/gas-prices/pa/souderton", 
    search: "Lukoil", 
    display: "Lukoil (Souderton)" 
  },
  { 
    id: "33030", 
    url: "https://www.mapquest.com/gas-prices/pa/bethlehem", 
    search: "Jack's", 
    display: "Jack's (Bethlehem)" 
  },
  { 
    id: "26758", 
    url: "https://www.mapquest.com/gas-prices/pa/allentown", 
    search: "BJ's", 
    display: "BJ's (Allentown)" 
  }
];

const OUT_FILE = path.join("public", "gas_prices.json");

async function fetchFromMapQuest(station) {
  try {
    console.log(`Checking MapQuest for ${station.display}...`);
    const res = await fetch(station.url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
      }
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    const html = await res.text();
    const $ = load(html);
    let foundPrice = "N/A";

    // Scan for the station name and the price that follows it
    $("[class*='station-name'], .name, h4").each((_, el) => {
        const text = $(el).text().trim();
        if (text.toLowerCase().includes(station.search.toLowerCase())) {
            // Find the price in the nearest container
            const container = $(el).closest('div, li, .mqa-card');
            const priceMatch = container.text().match(/\$\d\.\d{2}/);
            if (priceMatch) {
                foundPrice = priceMatch[0];
                return false;
            }
        }
    });

    return { id: station.id, name: station.display, price: foundPrice };

  } catch (err) {
    console.error(`MapQuest failed for ${station.display}:`, err.message);
    return { id: station.id, name: station.display, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS) {
    results.push(await fetchFromMapQuest(s));
    await new Promise(r => setTimeout(r, 2000));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Final JSON:", JSON.stringify(payload, null, 2));
}

main();
