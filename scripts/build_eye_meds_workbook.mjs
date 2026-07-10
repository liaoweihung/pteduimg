import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(".");
const tablesPath = path.join(root, "eye_meds_tables.json");
const outputPath = path.join(root, "eye_meds_tw.xlsx");

const tables = JSON.parse(await fs.readFile(tablesPath, "utf8"));

function colName(index) {
  let n = index + 1;
  let out = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    out = String.fromCharCode(65 + rem) + out;
    n = Math.floor((n - 1) / 26);
  }
  return out;
}

function rowsToMatrix(table) {
  const matrix = [table.columns];
  for (const row of table.rows) {
    matrix.push(table.columns.map((col) => row[col] ?? ""));
  }
  return matrix;
}

function setColumnWidths(sheet, columns) {
  columns.forEach((col, idx) => {
    const letter = colName(idx);
    let width = 16;
    if (/商品名|英文品名|適應症完整|全部成分|資料來源|備註|排除原因/.test(col)) width = 34;
    if (/許可證字號|許可證種類|分類依據|主要成分|規格|包裝|命中關鍵字/.test(col)) width = 24;
    if (/百分比|排名|數量|產品數/.test(col)) width = 12;
    if (idx > 25) width = 13;
    sheet.getRange(`${letter}:${letter}`).format.columnWidth = width;
  });
}

const workbook = Workbook.create();

for (const [sheetName, table] of Object.entries(tables)) {
  const sheet = workbook.worksheets.add(sheetName);
  sheet.showGridLines = false;
  const matrix = rowsToMatrix(table);
  const lastCol = colName(table.columns.length - 1);
  const lastRow = matrix.length;
  sheet.getRange(`A1:${lastCol}${lastRow}`).values = matrix;
  sheet.getRange(`A1:${lastCol}1`).format = {
    fill: "#245C5A",
    font: { bold: true, color: "#FFFFFF" },
    wrapText: true,
  };
  sheet.getRange(`A1:${lastCol}${lastRow}`).format.borders = {
    preset: "inside",
    style: "thin",
    color: "#D7E2DF",
  };
  sheet.getRange(`A2:${lastCol}${lastRow}`).format.wrapText = true;
  setColumnWidths(sheet, table.columns);
  sheet.freezePanes.freezeRows(1);
  if (lastRow > 1 && table.columns.length > 1) {
    const safeName = sheetName.replace(/[^A-Za-z0-9]/g, "");
    const tableObj = sheet.tables.add(`A1:${lastCol}${lastRow}`, true, `${safeName}Table`);
    tableObj.style = "TableStyleMedium2";
    tableObj.showFilterButton = true;
  }
  if (["Raw Database", "Compare Table", "Excluded Products"].includes(sheetName)) {
    sheet.freezePanes.freezeColumns(3);
  }
}

const raw = workbook.worksheets.getItem("Raw Database");
raw.getRange("A1:U1").format.rowHeight = 34;

const cf = workbook.worksheets.getItem("Component Frequency");
if (tables["Component Frequency"].rows.length > 0) {
  cf.getRange("C2:C" + (tables["Component Frequency"].rows.length + 1)).format.numberFormat = "0.0%";
}

const ps = workbook.worksheets.getItem("Preservative Summary");
if (tables["Preservative Summary"].rows.length > 0) {
  ps.getRange("C2:C" + (tables["Preservative Summary"].rows.length + 1)).format.numberFormat = "0.0%";
}

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);
console.log(outputPath);
