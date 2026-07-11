import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("../node_modules/playwright");

const url = process.argv[2] || "http://127.0.0.1:8000/eye-meds.html";
const executablePath = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

const browser = await chromium.launch({ headless: true, executablePath });
const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true });
const errors = [];

page.on("pageerror", (error) => errors.push(error.message));
page.on("console", (message) => {
  const text = message.text();
  if (message.type() === "error" && !text.includes("404 (File not found)")) errors.push(text);
});

await page.goto(url, { waitUntil: "networkidle" });
await page.waitForSelector("#entrySelect option", { state: "attached" });

async function chooseEntry(entry) {
  await page.click(`button[data-entry="${entry}"]`);
  await page.waitForTimeout(150);
  const optionCount = await page.locator("#entrySelect option").count();
  if (optionCount < 2) throw new Error(`${entry} dropdown has no choices.`);
  const value = await page.locator("#entrySelect option").nth(1).getAttribute("value");
  await page.selectOption("#entrySelect", value);
  await page.waitForTimeout(250);
  const inputValue = await page.inputValue("#searchInput");
  const resultCount = await page.locator(".product-card").count();
  if (inputValue !== value) throw new Error(`${entry} did not sync selected value into search input.`);
  if (resultCount < 1) throw new Error(`${entry} selected value returned no products.`);
  return { entry, optionCount, value, resultCount };
}

const checks = [];
checks.push(await chooseEntry("indication"));
checks.push(await chooseEntry("ingredient"));
checks.push(await chooseEntry("class"));
checks.push(await chooseEntry("product"));
checks.push(await chooseEntry("formulation"));

await browser.close();

if (errors.length) throw new Error(`Browser console errors: ${errors.join(" | ")}`);
console.log(JSON.stringify({ checks, errors }, null, 2));
