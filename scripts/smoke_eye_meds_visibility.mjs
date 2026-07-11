import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("../node_modules/playwright");

const url = process.argv[2] || "http://127.0.0.1:8000/eye-meds.html";
const executablePath = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

const browser = await chromium.launch({ headless: true, executablePath });
const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true });
await page.goto(url, { waitUntil: "networkidle" });
await page.waitForSelector(".product-card", { state: "attached" });

const firstTop = await page.locator("#results").evaluate((el) => el.getBoundingClientRect().top);
const countText = await page.locator("#quickResultCount").textContent();
await page.click("#jumpToResults");
await page.waitForTimeout(700);
const afterJumpTop = await page.locator("#results").evaluate((el) => el.getBoundingClientRect().top);

await page.click('button[data-entry="indication"]');
const value = await page.locator("#entrySelect option").nth(1).getAttribute("value");
await page.selectOption("#entrySelect", value);
await page.waitForTimeout(700);
const afterSelectTop = await page.locator("#results").evaluate((el) => el.getBoundingClientRect().top);
const updatedCountText = await page.locator("#quickResultCount").textContent();

await browser.close();

if (!/目前 \d+ 筆結果/.test(countText || "")) throw new Error(`Quick result count is not visible: ${countText}`);
if (!/目前 \d+ 筆結果/.test(updatedCountText || "")) throw new Error(`Quick result count did not update: ${updatedCountText}`);
if (afterJumpTop > 120) throw new Error("Jump button did not bring results near the top.");
if (afterSelectTop > 120) throw new Error("Dropdown selection did not bring results near the top.");

console.log(JSON.stringify({ firstTop, afterJumpTop, afterSelectTop, countText, updatedCountText }, null, 2));
