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
await page.waitForSelector(".product-card", { state: "attached" });

const initial = await page.locator(".product-card").count();
await page.fill("#searchInput", "青光眼");
await page.waitForTimeout(300);
const glaucoma = await page.locator(".product-card").count();
await page.selectOption("#dosageFilter", "ophthalmic_solution");
await page.waitForTimeout(200);
const filtered = await page.locator(".product-card").count();
await page.evaluate(() => document.querySelector(".result-list .product-card")?.click());
await page.waitForSelector("#detailView:not([hidden])");
const detailHasLicense = await page.locator("#detailView").getByText("藥證字號").count();
await page.check("#includeInactive");
await page.waitForTimeout(300);
const withInactive = await page.locator(".product-card").count();
await page.click('button[data-entry="formulation"]');
await page.waitForSelector("#formulationPanel:not([hidden])");
const formulationVisible = await page.locator("#preservativeStats .stat-row").count();
const mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
await page.setViewportSize({ width: 1366, height: 900 });
await page.waitForTimeout(200);
const desktopDetailPosition = await page.locator(".detail-panel").evaluate((el) => getComputedStyle(el).position);

await browser.close();

const result = {
  initial,
  glaucoma,
  filtered,
  detailHasLicense,
  withInactive,
  formulationVisible,
  mobileOverflow,
  desktopDetailPosition,
  errors,
};

if (initial < 1) throw new Error("No initial product cards rendered.");
if (glaucoma < 1) throw new Error("Search for 青光眼 returned no results.");
if (filtered < 1) throw new Error("Dosage filter returned no results.");
if (detailHasLicense < 1) throw new Error("Detail view did not show license field.");
if (withInactive < filtered) throw new Error("Including inactive licenses reduced result count unexpectedly.");
if (formulationVisible < 1) throw new Error("Formulation preservative stats did not render.");
if (mobileOverflow) throw new Error("Mobile viewport has horizontal overflow.");
if (errors.length) throw new Error(`Browser console errors: ${errors.join(" | ")}`);

console.log(JSON.stringify(result, null, 2));
