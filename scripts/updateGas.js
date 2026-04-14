import fs from "node:fs";
import path from "node:path";

const API_KEY = process.env.WEB_SCRAPING_AI_KEY; 
const OUT_FILE = path.join("public", "gas_prices.json");

const STATIONS = [
  { id: "7072", q: "Lukoil+681+E+Broad+St+Souderton+PA+gas+price", name: "Lukoil (Souderton)" },
  { id: "33030", q: "Jacks+Food+Mart+3010+Schoenersville+Rd+Bethlehem+PA+gas+price", name: "Jack's Food Mart (Bethlehem)" },
  { id: "26758", q: "BJs+Gas+1785+Airport+Rd+Allentown+PA+gas+price", name: "BJ's (Allentown)" }
];

async function fetchFromGoogle(station) {
  try {
    console.log(`Searching Google for ${station.name}...`);
    
    // We search Google via the proxy. 
    // We don't need 'render' for Google snippets, which saves credits.
    const googleUrl = `https://www.google.com/search?q=${station.q}`;
    const apiUrl = `https://api.webscraping.ai/html?api_key=${API_KEY}&url=${encodeURIComponent(googleUrl)}&proxy_type=residential`;
    
    const res = await fetch(apiUrl);
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    
    const html = await res.text();

    // Google often shows the price as "Regular: $3.49" or just "$3.49" in the snippet.
    // We look for the first price match that isn't a weird number.
    const priceMatch = html.match(/\$(\d\.\d{2})/);
    
    return { 
      id: station.id, 
      name: station.name, 
      price: priceMatch ? priceMatch[0] : "N/A" 
    };

  } catch (err) {
    console.error(`Error searching ${station.name}:`, err.message);
    return { id: station.id, name: station.name, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS) {
    results.push(await fetchFromGoogle(s));
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
