import fs from "node:fs";
import path from "node:path";

const API_KEY = process.env.SERP_API_KEY; 
const OUT_FILE = path.join("public", "gas_prices.json");

const STATIONS = [
  { id: "7072", q: "Lukoil 681 E Broad St Souderton PA gas price", name: "Lukoil (Souderton)" },
  { id: "33030", q: "Jack's Food Mart 3010 Schoenersville Rd Bethlehem PA gas price", name: "Jack's (Bethlehem)" },
  { id: "26758", q: "BJ's 1785 Airport Rd Allentown PA gas price", name: "BJ's (Allentown)" }
];

async function fetchFromSerp(station) {
  try {
    console.log(`Searching Google for ${station.name}...`);
    const url = `https://serpapi.com/search.json?engine=google&q=${encodeURIComponent(station.q)}&api_key=${API_KEY}`;
    
    const res = await fetch(url);
    const data = await res.json();
    
    // Google often puts the gas price in the "answer_box" or "knowledge_graph"
    let price = "N/A";
    
    // Look in the snippet text for the first $X.XX pattern
    const textToSearch = JSON.stringify(data);
    const priceMatch = textToSearch.match(/\$(\d\.\d{2})/);
    
    if (priceMatch) {
      price = priceMatch[0];
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
    results.push(await fetchFromSerp(s));
    await new Promise(r => setTimeout(r, 1000));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Success:", JSON.stringify(payload, null, 2));
}

main();
