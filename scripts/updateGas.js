import fs from "node:fs";
import path from "node:path";
import { load } from "cheerio";

const STATIONS = [
  { id: "7072", name: "Lukoil Souderton PA", url: "https://www.gasbuddy.com/station/7072" },
  { id: "33030", name: "Jacks Food Mart Bethlehem PA", url: "https://www.gasbuddy.com/station/33030" },
  { id: "26758", name: "BJs Allentown PA", url: "https://www.gasbuddy.com/station/26758" }
];

const OUT_FILE = path.join("public", "gas_prices.json");

async function fetchWithProxy(station) {
  // Using a public "all-origins" proxy to hide the GitHub IP
  const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(station.url)}`;

  try {
    console.log(`Fetching ${station.name} via proxy...`);
    const res = await fetch(proxyUrl);
    if (!res.ok) throw new Error(`Proxy Error: ${res.status}`);
    
    const data = await res.json();
    const $ = load(data.contents);

    // Look for price in the meta tags or specific spans
    // GasBuddy often puts the price in a meta tag for SEO
    let price = $("meta[property='og:description']").attr("content") || "";
    const priceMatch = price.match(/\$\d+\.\d{2}/);
    
    if (priceMatch) {
      return { id: station.id, name: station.name, price: priceMatch[0] };
    }

    // Fallback to text search
    let bodyText = $("body").text();
    const bodyMatch = bodyText.match(/\$\d+\.\d{2}/);
    
    return { 
      id: station.id, 
      name: station.name, 
      price: bodyMatch ? bodyMatch[0] : "N/A" 
    };

  } catch (err) {
    console.error(`Error on ${station.id}:`, err.message);
    return { id: station.id, name: station.name, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS) {
    results.push(await fetchWithProxy(s));
    await new Promise(r => setTimeout(r, 2000));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Finished:", payload);
}

main();
