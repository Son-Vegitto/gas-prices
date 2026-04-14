import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const STATION_IDS = ["7072", "33030", "26758"];
const OUT_FILE = path.join("public", "gas_prices.json");

async function scrapeStation(browser, id) {
  // Use a mobile-like user agent to often bypass heavy desktop bot checks
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1'
  });
  
  const page = await context.newPage();
  
  try {
    console.log(`Checking Station ${id}...`);
    // Navigate and wait for the network to be somewhat quiet
    await page.goto(`https://www.gasbuddy.com/station/${id}`, { 
      waitUntil: 'networkidle', 
      timeout: 60000 
    });

    // Let's grab the Name first
    const name = await page.locator("h1").first().innerText({ timeout: 10000 });

    // New Strategy: Look for the text "$" followed by numbers anywhere in the main area
    const priceText = await page.evaluate(() => {
      // Find all elements that have a "$" in them
      const elements = Array.from(document.querySelectorAll('span, div, p'));
      const priceElement = elements.find(el => /^\$\d+\.\d{2}/.test(el.innerText.trim()));
      return priceElement ? priceElement.innerText.trim() : null;
    });

    await context.close();
    return { 
      id, 
      name: name.trim() || `Station ${id}`, 
      price: priceText || "N/A" 
    };

  } catch (err) {
    console.error(`Error on ${id}:`, err.message);
    await context.close();
    return { id, name: "Blocked/Error", price: "N/A" };
  }
}

async function main() {
  // Launch with essential flags for GitHub Actions
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'] 
  });

  const results = [];
  for (const id of STATION_IDS) {
    results.push(await scrapeStation(browser, id));
    await new Promise(r => setTimeout(r, 5000)); // 5s delay to be safe
  }

  await browser.close();

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Final Result:", JSON.stringify(payload, null, 2));
}

main();
