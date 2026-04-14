import fs from "node:fs";
import path from "node:path";
import { load } from "cheerio";

const STATIONS = [
  { 
    id: "7072", 
    url: "https://www.getupside.com/locations/pa/souderton/", 
    address: "681 E Broad St", 
    name: "Lukoil (Souderton)" 
  },
  { 
    id: "33030", 
    url: "https://www.getupside.com/locations/pa/bethlehem/", 
    address: "3010 Schoenersville Rd", 
    name: "Jack's Food Mart (Bethlehem)" 
  },
  { 
    id: "26758", 
    url: "https://www.getupside.com/locations/pa/allentown/", 
    address: "1785 Airport Rd", 
    name: "BJ's (Allentown)" 
  }
];

const OUT_FILE = path.join("public", "gas_prices.json");

async function fetchFromUpside(station) {
  try {
    console.log(`Checking ${station.name}...`);
    const res = await fetch(station.url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
      }
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    const html = await res.text();
    const $ = load(html);
    let foundPrice = "N/A";

    // Upside lists stations in rows or cards. We look for the specific address.
    $("div, li, tr").each((_, el) => {
        const text = $(el).text();
        if (text.includes(station.address)) {
            // Find the price (usually a large number in a span or div)
            const priceMatch = text.match(/\d\.\d{2}/);
            if (priceMatch) {
                foundPrice = `$${priceMatch[0]}`;
                return false;
            }
        }
    });

    return { id: station.id, name: station.name, price: foundPrice };

  } catch (err) {
    console.error(`Upside failed for ${station.name}:`, err.message);
    return { id: station.id, name: station.name, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS) {
    results.push(await fetchFromUpside(s));
    await new Promise(r => setTimeout(r, 2000));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Final JSON:", payload);
}

main();
