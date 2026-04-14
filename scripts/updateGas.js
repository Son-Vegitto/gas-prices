import fs from "node:fs";
import path from "node:path";
import { load } from "cheerio";

const STATION_IDS = ["7072", "33030", "26758"];
const OUT_FILE = path.join("public", "gas_prices.json");

async function fetchWithHeader(url) {
  const res = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9",
      "Cache-Control": "no-cache",
      "Pragma": "no-cache"
    }
  });
  
  if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
  return res.text();
}

async function scrapeStation(id) {
  try {
    const html = await fetchWithHeader(`https://www.gasbuddy.com/station/${id}`);
    const $ = load(html);
    
    // Log the length to the GitHub Action console to debug
    console.log(`Station ${id}: Page received (${html.length} bytes)`);

    // Strategy 1: Look for the price inside a span that contains "PriceDisplay"
    let price = $("[class*='PriceDisplay-module__price']").first().text().trim();

    // Strategy 2: Fallback if they changed the class again (look for the $ sign)
    if (!price || !price.startsWith('$')) {
      $("[class*='price']").each((_, el) => {
        const text = $(el).text().trim();
        if (text.startsWith('$')) {
          price = text;
          return false; 
        }
      });
    }

    const name = $("h1").first().text().trim() || `Station ${id}`;

    return {
      id,
      name,
      price: price || "N/A"
    };
  } catch (err) {
    console.error(`Error on ${id}: ${err.message}`);
    return { id, name: "Error", price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const id of STATION_IDS) {
    results.push(await scrapeStation(id));
    // Wait 3 seconds between stations to stay stealthy
    await new Promise(r => setTimeout(r, 3000));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public");
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("JSON Update Attempted:", payload);
}

main();
