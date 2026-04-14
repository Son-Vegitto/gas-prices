import fs from "node:fs";
import path from "node:path";

const STATION_IDS = ["7072", "33030", "26758"];
const OUT_FILE = path.join("public", "gas_prices.json");

async function getPrice(id) {
  const query = {
    operationName: "GetStation",
    variables: { id: id },
    query: `query GetStation($id: ID!) {
      station(id: $id) {
        name
        prices {
          fuelType
          credit {
            price
            postedTime
          }
        }
      }
    }`
  };

  try {
    const response = await fetch("https://www.gasbuddy.com/graphql", {
      method: "POST",
      headers: {
        "accept": "*/*",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "origin": "https://www.gasbuddy.com",
        "referer": `https://www.gasbuddy.com/station/${id}`
      },
      body: JSON.stringify(query),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    const station = data?.data?.station;
    
    if (!station) return { id, name: "Not Found", price: "N/A" };

    // GasBuddy returns prices in an array; we want 'regular'
    const regularData = station.prices.find(p => p.fuelType === "regular");
    const price = regularData?.credit?.price ? `$${regularData.credit.price}` : "N/A";

    return {
      id,
      name: station.name || `Station ${id}`,
      price: price
    };
  } catch (err) {
    console.error(`Error on ${id}:`, err.message);
    return { id, name: "Blocked", price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const id of STATION_IDS) {
    console.log(`Fetching ${id}...`);
    const data = await getPrice(id);
    results.push(data);
    await new Promise(r => setTimeout(r, 2000)); // Be gentle
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Final payload written to disk.");
}

main();
