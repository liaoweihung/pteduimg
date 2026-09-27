# 三張圖卡修訂提示詞

日期：2026-09-27。使用內建 image_gen 編修已檢視的原圖，轉成 WebP 並替換同名專案圖檔，保留分享網址。

## over_one_oint_01.webp

Use case: text-localization. Edit target: supplied pharmacy education infographic. Redesign this single Traditional Chinese portrait card, retaining friendly illustrated style, cream background, blue/green/purple section colors and medication tubes. Replace ALL existing text and diagrams as needed to reflect ONLY exact following content, large legible Traditional Chinese:
Title: 兩種藥膏可以一起擦嗎？
Subtitle: 混擦、分區與使用順序
Panel 1 heading: 不要自行混在一起
Text: 不要把兩種藥膏擠在手上混合。 Illustrate two tubes mixing crossed out.
Text: 醫師開立的複方藥膏，依原處方使用。
Panel 2 heading: 不同部位：依指示分區
Text: 先確認每條藥膏要擦哪個部位。 Illustrate arm marked A and leg marked B, tubes A and B; no diagnoses.
Text: 不要把所有藥都塗在同一塊皮膚。
Panel 3 heading: 同一部位：先確認用法
Text: 是否併用？先擦哪條？要隔多久？
Text: 依藥品、處方及醫師或藥師指示。
Illustrate parent showing two tubes to pharmacist and a checklist; NO clocks with numerical time.
Bottom highlighted text: 沒有適用所有藥膏的固定間隔或順序。
Footer: 更新：2026-09-27｜資料來源與審閱狀態見網頁
Constraints: no dose numbers, no 15–30 minutes, no anti-infective first steroid next, no water-before-oil rule, no added medical claims, no invented author. Output one polished readable portrait image.

## ped_cold_secorine.webp

Use case: text-localization. Edit target: attached Secorine pharmacy infographic. Replace old card content with a redesigned clean Traditional Chinese portrait infographic, retaining warm orange headings, friendly cartoon parents/children and white background. Exact new text below. Remove ALL old dose tables, weight division formulas, dosage examples, old numbered panels, claim that best for a symptom combination, realistic bottle packaging. Use a simple generic orange bottle labeled 息咳寧 (示意) with NO capacity, no trademarks.
Title: 息咳寧糖漿
Subtitle: 成分、用量核對與副作用
Small name: Secorine Syrup
Panel 1: 認對藥品
Text: 每 1 mL 含：
dl-Methylephedrine HCl 1 mg
Chlorpheniramine maleate 0.1 mg
Glyceryl guaiacolate 5 mg
Small text: 衛署藥製字第040833號
Panel 2: 用途
Text: 緩解感冒的流鼻水、鼻塞、打噴嚏、咳嗽、喀痰。
Illustrate child tissue and coughing, no lungs disease indication.
Panel 3 (largest, three illustrated steps): 家長如何核對用量？
Step 1: 看藥名與濃度
Step 2: 看每次 mL 與每日次數
Step 3: 用附屬量器量取
Below: 使用前搖勻；不清楚先問藥師。
Prominent banner: 兒童用量依醫囑，不用體重速算。
Text: 6 歲以下，先由醫師診治。
Panel 4: 服用後注意
Text: 可能嗜睡、頭暈、噁心。
Text: 出現心跳加速、排尿困難或皮疹，停用並諮詢醫藥人員。
Text: 避免酒精；勿自行併用其他感冒或抗過敏藥。
Panel 5 small callout: 息咳寧 ≠ 息咳液
Text: 名稱相似，配方不同；不要自行替換或合用。
Footer: 更新：2026-09-27｜資料來源與審閱狀態見網頁
Do not add any medication dose advice, mL per dose, mg/kg, numerical age dosing table or other text. Preserve drug ingredient concentration numbers exactly, make Roman spelling legible.

## ped_cold_cetirizine.webp

Use case: text-localization. Edit target: attached Cetirizine pharmacy infographic. Redesign one Traditional Chinese portrait card, keep white background, raspberry pink main heading, blue/green/purple modules and friendly cartoon illustrations. Remove ALL old age/dose table, dose amounts, bodyweight calculation, example and all bottle capacity labels. Use simple generic bottle labeled 勝克敏液 1 mg/mL（示意）, NOT replica packaging.
Only use exact following text:
Title: 勝克敏液
Subtitle: 兒童用量怎麼核對？
Secondary title: 成分、用途與副作用
Panel 1 heading: 先認對藥品
Text: Cetirizine 1 mg/mL 口服液
Text: 第二代抗組織胺
Text: 衛署藥製字第044023號
Callout: 濃度 ≠ 每次服用量
Panel 2 heading: 用於過敏症狀
Text: 過敏性鼻炎、蕁麻疹、過敏性搔癢等。
Illustrate sneezing child and child with hives.
Panel 3 heading: 核對藥袋的三個重點
Draw three sequential illustrated panels with bottle, prescription bag, measuring oral syringe WITHOUT numerical dosage markings.
1: 藥名與濃度相符
2: 分清每次用量與每日次數
3: 用口服量器量取
Prominent text: 兒童用量依處方，不用體重速算。
Text: 藥袋不清楚，先請藥師確認。
Panel 4 heading: 可能有哪些副作用？
Text: 嗜睡、頭暈、口乾、噁心或嘔吐。
Text: 第二代抗組織胺仍可能嗜睡。
Panel 5 heading: 這些情況先詢問
Text: 有腎功能問題，或正在吃其他感冒、抗過敏、鎮靜藥。
Text: 不自行加量，也不要沿用別人的藥量。
Footer: 更新：2026-09-27｜資料來源與審閱狀態見網頁
Do not add any extra medical claims or dose quantities. Preserve exact concentration. Legible accurate text and strong reading hierarchy.


## 2026-09-28 三圖共同局部修改提示詞（內建 image_gen）

Remove ONLY the tiny footer text 更新：2026-09-27｜資料來源與審閱狀態見網頁. Fill its former area with matching white/off-white background. Keep all other text, ingredient numbers, illustrations, layout, borders and colors unchanged. Leave a blank footer without replacement text.
