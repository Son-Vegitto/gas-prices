import fs from "node:fs";
import path from "node:path";
import { load } from "cheerio";

const STATIONS = [
  { id: "7072", q: "Lukoil+Souderton+PA+gas+price", name: "Lukoil (Souderton)" },
  { id: "33030", q: "Jacks+Food+Mart+Bethlehem+PA+gas+price", name: "Jack's (Bethlehem)" },
  { id: "26758", q: "BJs+Allentown+PA+gas+price", name: "BJ's (Allentown)" }
];

const OUT_FILE = path.join("public", "gas_prices.json");

async function fetchFromSearch(station) {
  try {
    console.log(`Searching for ${station.name}...`);
    // Using Bing Search because it's much easier to scrape from GitHub
    const url = `https://www.bing.com/search?q=${station.q}`;
    
    const res = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
      }
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    const html = await res.text();
    const $ = load(html);
    
    // Look for a price pattern ($X.XX) in the search result snippets
    const pageText = $("body").text();
    const priceMatch = pageText.match(/\$\d\.\d{2}/); 

    return {
      id: station.id,
      name: station.name,
      price: priceMatch ? priceMatch[0] : "N/A"
    };

  } catch (err) {
    console.error(`Search failed for ${station.name}:`, err.message);
    return { id: station.id, name: station.name, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS) {
    results.push(await fetchFromSearch(s));
    await new Promise(r => setTimeout(r, 3000));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Payload:", payload);
}

main();
