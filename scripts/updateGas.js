import fs from "node:fs";
import path from "node:path";

// PASTE YOUR GOOGLE WEB APP URL HERE
const GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/XXXXX/exec";
const OUT_FILE = path.join("public", "gas_prices.json");

async function main() {
  console.log("Fetching data from Google Sheets Bridge...");
  
  try {
    const res = await fetch(GOOGLE_SHEETS_URL);
    const data = await res.json();
    
    if (!fs.existsSync("public")) fs.mkdirSync("public", { recursive: true });
    fs.writeFileSync(OUT_FILE, JSON.stringify(data, null, 2));
    
    console.log("Success! Data synced from Google:", data);
  } catch (err) {
    console.error("Bridge failed:", err.message);
  }
}

main();
