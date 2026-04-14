import fs from "node:fs";
import path from "node:path";
import { load } from "cheerio";

const STATIONS_TO_TRACK = [
  { 
    id: "7072", 
    searchUrl: "https://www.gasbuddy.com/home?search=18964&fuel=1", 
    nameSearch: "Lukoil", 
    city: "Souderton" 
  },
  { 
    id: "33030", 
    searchUrl: "https://www.gasbuddy.com/home?search=18017&fuel=1", 
    nameSearch: "Jack's Food Mart", 
    city: "Bethlehem" 
  },
  { 
    id: "26758", 
    searchUrl: "https://www.gasbuddy.com/home?search=18109&fuel=1", 
    nameSearch: "BJ's", 
    city: "Allentown" 
  }
];

const OUT_FILE = path.join("public", "gas_prices.json");

async function fetchPrice(station) {
  try {
    const res = await fetch(station.searchUrl, {
      headers: { 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" 
      }
    });
    
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    const html = await res.text();
    const $ = load(html);
    let price = "N/A";

    // GasBuddy search results are usually in 'stationListItem' containers
    $("[class*='GenericStationListItem-module__stationListItem']").each((_, el) => {
      const stationNameText = $(el).find("h3").text().trim();
      
      // Look for our station name in the list item
      if (stationNameText.toLowerCase().includes(station.nameSearch.toLowerCase())) {
        const foundPrice = $(el).find("[class*='StationDisplayPrice-module__price']").text().trim();
        if (foundPrice.startsWith("$")) {
          price = foundPrice;
          return false; // Found it, stop looking
        }
      }
    });

    return { id: station.id, name: `${station.nameSearch} (${station.city})`, price };
  } catch (err) {
    console.error(`Error fetching ${station.nameSearch}:`, err.message);
    return { id: station.id, name: station.nameSearch, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS_TO_TRACK) {
    console.log(`Searching for ${s.nameSearch} in ${s.city}...`);
    results.push(await fetchPrice(s));
    await new Promise(r => setTimeout(r, 3000)); // Be gentle to avoid getting flagged
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Update Complete:", payload);
}

main();
