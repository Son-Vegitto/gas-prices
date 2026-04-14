import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const STATION_IDS = ["7072", "33030", "26758"];
const OUT_FILE = path.join("public", "gas_prices.json");

async function scrapeStation(browser, id) {
  const page = await browser.newPage();
  // Mimic a real user
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });
  
  try {
    console.log(`Navigating to Station ${id}...`);
    await page.goto(`https://www.gasbuddy.com/station/${id}`, { waitUntil: 'domcontentloaded', timeout: 60000 });

    // Wait for the price element to appear (using a generic selector for "price")
    const priceSelector = "[class*='PriceDisplay-module__price']";
    await page.waitForSelector(priceSelector, { timeout: 10000 });

    const price = await page.locator(priceSelector).first().innerText();
    const name = await page.locator("h1").first().innerText();

    await page.close();
    return { id, name: name.trim(), price: price.trim() };
  } catch (err) {
    console.error(`Failed to scrape ${id}: ${err.message}`);
    await page.close();
    return { id, name: "Error", price: "N/A" };
  }
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const results = [];

  for (const id of STATION_IDS) {
    results.push(await scrapeStation(browser, id));
    // Brief pause
    await new Promise(r => setTimeout(r, 2000));
  }

  await browser.close();

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public");
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Success:", payload);
}

main();
