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
    
    // Residential proxy is key here
    const apiUrl = `https://api.webscraping.ai/html?api_key=${API_KEY}&url=${encodeURIComponent(station.url)}&proxy_type=residential`;
    
    const res = await fetch(apiUrl);
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    
    const html = await res.text();
    
    // Regex Strategy 1: Look for the specific price class/schema used by GasBuddy
    // It often looks like: "price":"3.49" or >$3.49</span>
    const regexList = [
      /\"price\"\:\"(\d\.\d{2})\"/,             // JSON-LD schema
      /itemprop=\"price\" content=\"(\d\.\d{2})\"/, // Microdata
      /\$(\d\.\d{2})/,                         // Standard $X.XX
      /Price-module__price___[\w\d]+\">(\d\.\d{2})</ // React module class
    ];

    let foundPrice = "N/A";

    for (const regex of regexList) {
      const match = html.match(regex);
      if (match && match[1]) {
        foundPrice = `$${match[1]}`;
        break; 
      } else if (match && match[0].startsWith('$')) {
        foundPrice = match[0]; // For the standard $X.XX match
        break;
      }
    }

    return { id: station.id, name: station.name, price: foundPrice };
  } catch (err) {
    console.error(`Error on ${station.name}:`, err.message);
    return { id: station.id, name: station.name, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS) {
    results.push(await fetchWithAPI(s));
    await new Promise(r => setTimeout(r, 1500));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Results Found:", JSON.stringify(payload, null, 2));
}

main();
