import fs from "node:fs";
import path from "node:path";
import { load } from "cheerio";

// ---- Config ----
const STATION_IDS = ["7072", "33030", "26758"];
const OUT_FILE = path.join("public", "gas_prices.json");

// ---- Helpers ----
/**
 * GasBuddy will block the default Node.js fetch agent. 
 * We must mimic a real browser.
 */
async function fetchWithHeader(url) {
  const res = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"
    }
  });
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  return res.text();
}

function formatCurrentDate() {
  const now = new Date();
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });

  let parts = formatter.formatToParts(now);
  let d = parts.find(p => p.type === 'day').value;
  let m = parts.find(p => p.type === 'month').value;
  let y = parts.find(p => p.type === 'year').value;
  let hr = parts.find(p => p.type === 'hour').value;
  let min = parts.find(p => p.type === 'minute').value;
  let dayPeriod = parts.find(p => p.type === 'dayPeriod').value;

  return `${d}-${m}-${y} ${hr}:${min} ${dayPeriod}`;
}

// ---- Main Logic ----
async function scrapeStation(id) {
  const url = `https://www.gasbuddy.com/station/${id}`;
  try {
    const html = await fetchWithHeader(url);
    const $ = load(html);

    // Get Station Name (usually in the H1)
    const name = $("h1").text().trim() || `Station ${id}`;
    
    // Get Address
    const address = $(".StationDetails-module__address___3_N_k").text().trim() || "Address not found";

    // Find the Regular Price
    // We look for a span that contains 'price' in its class name
    let price = "N/A";
    $("[class*='PriceDisplay-module__price']").each((_, el) => {
      const val = $(el).text().trim();
      if (val.startsWith("$")) {
        price = val;
        return false; // Found the first one (usually Regular), break loop
      }
    });

    return {
      id,
      name,
      address,
      regularPrice: price,
      url
    };
  } catch (err) {
    console.error(`Error scraping station ${id}:`, err.message);
    return { id, error: "Failed to fetch data" };
  }
}

async function main() {
  console.log("Starting Gas Price Update...");
  
  const results = [];
  for (const id of STATION_IDS) {
    const data = await scrapeStation(id);
    results.push(data);
    // Tiny delay to be polite to the server
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  const payload = {
    updatedAt: formatCurrentDate(),
    stations: results
  };

  fs.mkdirSync(path.dirname(OUT_FILE), { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2), "utf8");

  console.log(`Successfully wrote ${results.length} stations to ${OUT_FILE}`);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
