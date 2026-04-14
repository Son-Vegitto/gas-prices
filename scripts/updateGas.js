import fs from "node:fs";
import path from "node:path";

const STATIONS = [
  { id: "7072", zip: "18964", search: "Lukoil", display: "Lukoil (Souderton)" },
  { id: "33030", zip: "18017", search: "Jack's Food Mart", display: "Jack's (Bethlehem)" },
  { id: "26758", zip: "18109", search: "BJ's", display: "BJ's (Allentown)" }
];

const OUT_FILE = path.join("public", "gas_prices.json");

async function fetchFromGeico(station) {
  try {
    // Geico's gas tool uses a simple fetchable URL
    const url = `https://api.geico.com/ms/gas-prices/v1/fuel-prices?zipCode=${station.zip}&radius=5`;
    
    console.log(`Searching for ${station.display}...`);
    const res = await fetch(url, {
      headers: {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      }
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    const data = await res.json();
    
    // Scan the list of stations Geico found
    const found = data.fuelStations?.find(s => 
      s.name.toLowerCase().includes(station.search.toLowerCase())
    );

    if (found) {
      // Get the 'Regular' fuel price
      const regPrice = found.fuelPrices?.find(p => p.fuelType === "Regular");
      return { 
        id: station.id, 
        name: station.display, 
        price: regPrice ? `$${regPrice.price}` : "N/A" 
      };
    }

    return { id: station.id, name: station.display, price: "Not in Results" };
  } catch (err) {
    console.error(`Failed ${station.display}:`, err.message);
    return { id: station.id, name: station.display, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS) {
    results.push(await fetchFromGeico(s));
    await new Promise(r => setTimeout(r, 2000));
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
