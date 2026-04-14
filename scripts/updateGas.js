import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const STATION_IDS = ["7072", "33030", "26758"];
const OUT_FILE = path.join("public", "gas_prices.json");

async function scrapeStation(browser, id) {
  // Creating a context with a standard desktop User-Agent
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    console.log(`Checking Station ${id}...`);
    
    // Go to page and wait until the basic HTML is loaded
    await page.goto(`https://www.gasbuddy.com/station/${id}`, { 
      waitUntil: 'domcontentloaded', 
      timeout: 60000 
    });

    // Wait for ANY element containing a "$" followed by a digit
    // This bypasses the need for specific class names
    const priceLocator = page.locator('text=/\$\d+/').first();
    await priceLocator.waitFor({ timeout: 15000 });

    const price = await priceLocator.innerText();
    const name = await page.locator("h1").first().innerText();

    await context.close();
    return { id, name: name.trim(), price: price.trim() };
  } catch (err) {
    console.error(`Station ${id} failed: ${err.message}`);
    // Take a screenshot to the logs folder if you wanted to debug, 
    // but for now, we'll just return N/A
    await context.close();
    return { id, name: "Blocked or Timeout", price: "N/A" };
  }
}

async function main() {
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const results = [];
  for (const id of STATION_IDS) {
    results.push(await scrapeStation(browser, id));
    // Wait 5 seconds between stations to look more human
    await new Promise(r => setTimeout(r, 5000));
  }

  await browser.close();

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Final Output:", payload);
}

main();
