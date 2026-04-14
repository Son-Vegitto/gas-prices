import fs from "node:fs";
import path from "node:path";
import { load } from "cheerio";

const STATION_IDS = ["7072", "33030", "26758"];
const OUT_FILE = path.join("public", "gas_prices.json");

async function fetchWithHeader(url) {
  const res = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
  });
  if (!res.ok) throw new Error(`Status ${res.status}`);
  return res.text();
}

async function scrapeStation(id) {
  try {
    const html = await fetchWithHeader(`https://www.gasbuddy.com/station/${id}`);
    const $ = load(html);

    // GasBuddy uses hashed classes, so we use a partial match selector
    const priceText = $("[class*='PriceDisplay-module__price']").first().text().trim();
    const stationName = $("h1").first().text().trim() || `Station ${id}`;

    return {
      id: id,
      name: stationName,
      price: priceText || "N/A"
    };
  } catch (err) {
    return { id: id, name: "Error", price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const id of STATION_IDS) {
    results.push(await scrapeStation(id));
    await new Promise(r => setTimeout(r, 2000)); // Be extra gentle to avoid bans
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public");
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("JSON Updated for KWGT");
}

main();
