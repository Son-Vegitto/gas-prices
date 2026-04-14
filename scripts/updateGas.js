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
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
      },
      body: JSON.stringify(query),
    });

    const data = await response.json();
    const station = data.data.station;
    
    // Find "regular" fuel type (usually '1' or 'regular')
    const regularData = station.prices.find(p => p.fuelType === "regular" || p.fuelType === "1");
    const price = regularData?.credit?.price ? `$${regularData.credit.price}` : "N/A";

    return {
      id,
      name: station.name,
      price: price
    };
  } catch (err) {
    console.error(`Error fetching station ${id}:`, err);
    return { id, name: "API Error", price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const id of STATION_IDS) {
    const data = await getPrice(id);
    results.push(data);
    await new Promise(r => setTimeout(r, 1000));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Results:", payload);
}

main();
