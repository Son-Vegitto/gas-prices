import fs from "node:fs";
import path from "node:path";

const API_KEY = process.env.WEB_SCRAPING_AI_KEY; 
const OUT_FILE = path.join("public", "gas_prices.json");

const STATIONS = [
  { id: "7072", url: "https://www.gasbuddy.com/station/7072", name: "Lukoil (Souderton)" },
  { id: "33030", url: "https://www.gasbuddy.com/station/33030", name: "Jack's Food Mart (Bethlehem)" },
  { id: "26758", url: "https://www.gasbuddy.com/station/26758", name: "BJ's (Allentown)" }
];

async function fetchWithAPI(station) {
  try {
    console.log(`Fetching ${station.name}...`);
    
    // WebScraping.ai handles the headers and proxies for us
    const apiUrl = `https://api.webscraping.ai/html?api_key=${API_KEY}&url=${encodeURIComponent(station.url)}&proxy_type=residential`;
    
    const res = await fetch(apiUrl);
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    
    const html = await res.text();
    
    // Search the HTML for the price pattern
    const priceMatch = html.match(/\$(\d\.\d{2})/) || html.match(/\"price\":\"(\d\.\d{2})\"/);
    const price = priceMatch ? `$${priceMatch[1]}` : "N/A";

    return { id: station.id, name: station.name, price };
  } catch (err) {
    console.error(`Error on ${station.name}:`, err.message);
    return { id: station.id, name: station.name, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS) {
    results.push(await fetchWithAPI(s));
    // Brief pause between requests
    await new Promise(r => setTimeout(r, 1000));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Updated data:", JSON.stringify(payload, null, 2));
}

main();
