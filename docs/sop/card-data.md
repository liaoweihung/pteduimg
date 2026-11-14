# 分類代碼對照表

系列資料（cards.json、cards.manual.json）的分類欄位只能使用本表的代碼，自行編造的代碼不會生效。一個系列可以填多個代碼，同時出現在多個分類；沒填的話只會出現在「全部圖卡」。

新增分類需要修改首頁程式，屬於改程式，須先經藥師同意，不能只改本表。

## 民眾版（public.html，`category: "public_education"`，填在 `topics`）

| 代碼 | 分類 |
|---|---|
| `sports_injury` | 運動傷害 |
| `skin_wound` | 皮膚與傷口 |
| `eyes` | 眼睛 |
| `oral_health` | 口腔 |
| `throat` | 喉嚨 |
| `infectious_diseases` | 傳染病 |
| `heat_illness` | 熱傷害 |
| `insect_repellent` | 防蚊 |
| `gastrointestinal` | 腸胃 |
| `elimination_care` | 排泄與照護 |
| `infant_care` | 嬰幼兒照護 |
| `growth` | 成長 |
| `chronic_conditions` | 慢性病 |
| `sleep` | 睡眠 |
| `pregnancy` | 懷孕 |
| `travel_medication` | 旅遊與用藥常識 |

## 藥師版（index.html，`category: "pharmacist_general"` 或 `"pharmacist_product"`，填在 `departments`）

| 代碼 | 科別 |
|---|---|
| `ophthalmology` | 眼科 |
| `ent` | 耳鼻喉科 |
| `dermatology` | 皮膚科 |
| `plastic_surgery` | 整形外科 |
| `colorectal_surgery` | 直腸外科 |
| `dentistry` | 牙科 |
| `obstetrics_gynecology` | 婦產科 |
| `pediatrics` | 兒科 |
| `chest_medicine_smoking_cessation` | 胸腔科／戒菸 |
| `cardiology` | 心臟內科 |
| `chinese_medicine` | 中醫 |
| `pharmacy_general` | 藥事通用 |

`pharmacist_general` 用於一般藥事衛教，`pharmacist_product` 用於特定產品衛教。
