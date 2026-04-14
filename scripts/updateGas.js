import fs from "node:fs";
import path from "node:path";

const API_KEY = process.env.SERP_API_KEY; 
const OUT_FILE = path.join("public", "gas_prices.json");

// We are feeding Google the exact GasBuddy URLs
const STATIONS = [
  { id: "7072", url: "https://www.gasbuddy.com/station/7072", name: "Lukoil (Souderton)" },
  { id: "33030", url: "https://www.gasbuddy.com/station/33030", name: "Jack's (Bethlehem)" },
  { id: "26758", url: "https://www.gasbuddy.com/station/26758", name: "BJ's (Allentown)" }
];

async function fetchFromGoogleCache(station) {
  try {
    console.log(`Pulling Google SERP data for ${station.name}...`);
    
    // We search Google for the exact GasBuddy page URL
    const url = `https://serpapi.com/search.json?engine=google&q=${encodeURIComponent(station.url)}&api_key=${API_KEY}`;
    
    const res = await fetch(url);
    if (!res.ok) throw new Error(`SerpApi returned ${res.status}`);
    
    const data = await res.json();
    let price = "N/A";

    // Convert the entire Google search result payload into a string
    const textToSearch = JSON.stringify(data);
    
    // Look for a realistic gas price ($2.XX, $3.XX, or $4.XX) anywhere in Google's scraped data
    const priceMatch = textToSearch.match(/\$([234]\.\d{2})/);
    
    if (priceMatch) {
      price = priceMatch[0]; // Gets the full "$X.XX" string
    }

    return { id: station.id, name: station.name, price };
  } catch (err) {
    console.error(`Error on ${station.name}:`, err.message);
    return { id: station.id, name: station.name, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS) {
    results.push(await fetchFromGoogleCache(s));
    // Brief pause between requests
    await new Promise(r => setTimeout(r, 1000));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  
  console.log("Final Data:", JSON.stringify(payload, null, 2));
}

main();
