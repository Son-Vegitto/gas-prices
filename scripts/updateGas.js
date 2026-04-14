import fs from "node:fs";
import path from "node:path";

const API_KEY = process.env.WEB_SCRAPING_AI_KEY; 
const OUT_FILE = path.join("public", "gas_prices.json");

const STATIONS = [
  { id: "7072", url: "https://www.gasbuddy.com/station/7072", name: "Lukoil (Souderton)" },
  { id: "33030", url: "https://www.gasbuddy.com/station/33030", name: "Jack's Food Mart (Bethlehem)" },
  { id: "26758", url: "https://www.gasbuddy.com/station/26758", name: "BJ's (Allentown)" }
];

async function fetchWithAPI(station) {
  try {
    console.log(`Fetching ${station.name}...`);
    
    // Adding 'render=true' to the API call. 
    // This tells WebScraping.ai to run the JavaScript (like a real browser).
    const apiUrl = `https://api.webscraping.ai/html?api_key=${API_KEY}&url=${encodeURIComponent(station.url)}&proxy_type=residential&render=true`;
    
    const res = await fetch(apiUrl);
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    
    const html = await res.text();

    // DIAGNOSTIC: See what we are actually getting
    console.log(`Debug: Received ${html.length} characters. Start: ${html.substring(0, 100).replace(/\n/g, '')}`);

    // If we see "Pardon Our Interruption", we are still being blocked
    if (html.includes("Pardon Our Interruption") || html.includes("captcha")) {
      console.error("Blocked by Captcha/Bot Wall even with proxy.");
      return { id: station.id, name: station.name, price: "Blocked" };
    }

    // New broad-spectrum price search
    // Looks for: "price":3.49 or "price":"3.49" or $3.49
    const regexList = [
      /\"price\"\:\"?(\d\.\d{2})\"?/,
      /credit\"\:\{\"price\"\:(\d\.\d{2})/,
      /\$(\d\.\d{2})/
    ];

    let foundPrice = "N/A";

    for (const regex of regexList) {
      const match = html.match(regex);
      if (match && match[1]) {
        foundPrice = `$${match[1]}`;
        break; 
      }
    }

    return { id: station.id, name: station.name, price: foundPrice };
  } catch (err) {
    console.error(`Error on ${station.name}:`, err.message);
    return { id: station.id, name: station.name, price: "N/A" };
  }
}

async function main() {
  const results = [];
  for (const s of STATIONS) {
    results.push(await fetchWithAPI(s));
    await new Promise(r => setTimeout(r, 2000));
  }

  const payload = {
    updated: new Date().toLocaleString("en-US", { timeZone: "America/New_York" }),
    stations: results
  };

  if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(payload, null, 2));
  console.log("Final JSON:", JSON.stringify(payload, null, 2));
}

main();
