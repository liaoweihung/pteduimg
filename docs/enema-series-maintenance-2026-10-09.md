# 浣腸使用系列文字與來源整理

日期：2026-10-09。處理範圍：`enema_use` 的 11 張公開圖卡。原圖、圖片路徑、分享網址、收藏鍵與前後導覽未更動。

## 已完成

- 已逐張閱讀 11 張原圖，補入 11 筆獨立文字版、對應標題、摘要、替代文字及資料來源。
- 所列來源於 2026-10-09 開啟核對；`sourceCheckedAt` 表示這次資料查閱日期，不是來源發布日，也**不是藥師簽核日**。全部保留 `needsMedicalReview: true`。
- 11 頁使用既有 `templates/site-footer.html` 的共通頁尾。文字版、來源日期、標題與 meta 由 `build.py` 產生。
- 同步修正兩份 cards JSON 的「類類型」筆誤。

## 尚待藥師複核與修圖

以下是閱讀原圖後發現的醫療表述風險。因本次要求保留原圖，文字版加上產品差異與警語，但圖片仍會先於文字顯示；需於後續修圖。**不把這些項目標為醫療審核完成。**

| 原圖 | 待確認或修正 |
|---|---|
| `enema_step_1.webp`、`enema_steps.webp` | 「接近體溫約 37°C」與溫水回溫不能視為所有產品必需操作；核對各產品仿單。 |
| `enema_step_3.webp`、`enema_steps.webp`、`enema_comp.webp` | 成人 7–10 cm、兒童 2–5 cm 的固定插入深度不應跨產品／年齡套用；以管嘴設計與產品說明為準。 |
| `enema_step_5.webp`、`enema_steps.webp`、`enema_comp.webp` | 固定「保留 5–15 分鐘，越久越好」不適用所有產品；磷酸鈉資料為通常 1–5 分鐘出現強烈便意，且不超過 10 分鐘；bisacodyl 浣腸為最多 10 分鐘。 |
| `enema_comp.webp` | 五種分類／品牌是否為臺灣現售核准品、成分、固定見效時間、刺激星等、兒童／孕婦適用與腎臟風險，需逐一對臺灣許可證及仿單；現在不能當購藥推薦表。 |
| `enema_clinical_cond.webp` | 「硬便卡在出口」可能提示糞便嵌塞，不能單憑感覺確診或自行反覆灌腸。圖中示意「救急」應加評估及急症界線。 |
| `constipation_cate.webp` | PEG 屬滲透性瀉劑，圖把它與膨脹性瀉劑同組；「安全性高／不依賴」「口服刺激性瀉劑不可天天吃」「浣腸是緊急出口」皆過於絕對。應按產品與臨床情境重寫圖片。 |

此外，若使用者有劇烈腹痛、嘔吐、血便、腹脹加劇、疑似阻塞、腎病、心衰竭或脫水，應先評估，尤其不要自行追加磷酸鹽浣腸。文字版已寫明，但圖卡是否足夠醒目仍待人工確認。

## 本次使用的可開啟來源

- [食藥署：浣腸劑與便祕原因](https://www.fda.gov.tw/Tc/faqContent.aspx?id=1109)
- [食藥署：智慧選擇瀉劑](https://www.fda.gov.tw/tc/newsContent.aspx?cid=4&id=t622351)
- [MedlinePlus：磷酸鈉直腸用藥](https://medlineplus.gov/druginfo/meds/a614018.html)
- [MedlinePlus：Bisacodyl 直腸用藥](https://medlineplus.gov/druginfo/meds/a611051.html)
- [NHS：磷酸鹽浣腸自我操作](https://www.gloshospitals.nhs.uk/your-visit/patient-information-leaflets/self-administration-of-a-phosphate-enema-ghpi1236/)
- [MedlinePlus：糞便嵌塞](https://medlineplus.gov/ency/article/000230.htm)
- [MedlinePlus：便祕自我照護](https://medlineplus.gov/ency/patientinstructions/000120.htm)
- [AGA/ACG：成人慢性特發性便祕藥物治療指引](https://gi.org/journals-publications/ebgi/schoenfeld2_june2023/)

這些來源支持通用操作界線與用藥分類；本次沒有逐一核對圖片中的所有品牌及臺灣許可證，相關欄位維持待確認。
