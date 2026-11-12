# 哺乳期間小毛病：網頁文字、SEO/AEO、站內互連與 Antigravity 提示詞（2026-11-12）

依據：claude/breastfeeding-minor-ailments-cards-v2-2026-11-12.md（圖卡文字 v2）、claude/breastfeeding-cards-image-prompts-2026-11-12.md（生圖提示詞）
結構比照現有 `pregnancy_minor_ailments`（cards.json／seo.json／data/card_content.json，每張圖卡一個 `cards/<圖檔名>.html` 頁面）。

---

## 一、給 Antigravity 的提示詞（直接貼）

```
新增圖卡系列「哺乳期間小毛病」，9 張圖卡，依 AGENTS.md 與 Card Manager 流程做，不要直接手改 HTML。
參考現有 pregnancy_minor_ailments 的寫法與欄位。

1. 系列 id：breastfeeding_minor_ailments。cards.json 依下方「二、系列設定」建立（title、icon、topics、tags、texts、steps）。
2. 圖卡：我會放 9 張圖，依下方檔名轉 webp 放進 img/，轉圖時依既有流程在底部預留空白帶加入 logo。
3. 每張圖卡頁：seo.json 寫入下方「三、各圖卡」的 page_title、meta_description、h1、image_alt、og；
   keywords 用每張卡自己的關鍵字，不要把整個系列的 tags 全部塞進每一頁。
   data/card_content.json 寫入 summary 與 sections；needsMedicalReview 設 false（藥師已審）。
4. 開啟共用 footer（showFooter）。
5. 站內互連：依下方「四、站內互連」加連結，包括「懷孕期間小毛病」對應卡雙向互連。找不到對應頁就列出來給我，不要自己建。
6. 加入 sitemap，並讓本系列出現在 public.html「最近新增」。依現有流程 build（python build.py --only breastfeeding_minor_ailments），檢查手機版正常後 commit、push。
7. 在 docs/project-management 登記本次新增系列。
8. 完成後回報：新增／修改的檔案清單、頁面網址、沒做到的項目。
```

---

## 二、系列設定（cards.json）

- **id**：`breastfeeding_minor_ailments`
- **title**：哺乳期間小毛病
- **category**：public_education
- **icon**：🤱
- **order**：34（接在懷孕期間小毛病 33 之後）
- **topics**：`["pregnancy", "infant_care", "gastrointestinal"]`
  - 建議：目前沒有「哺乳」主題。最省事的做法是把 build.py 的 `"pregnancy": "懷孕"` 改成 `"懷孕與哺乳"`，不另開新主題。
- **showFooter**：true

**texts / steps**

| # | texts（圖卡標題） | steps（圖檔） |
|---|---|---|
| 1 | 哺乳期間頭痛、發燒可以吃什麼？ | img/breastfeeding_minor_fever_pain.webp |
| 2 | 哺乳期間鼻塞、流鼻水可以用什麼？ | img/breastfeeding_minor_rhinitis.webp |
| 3 | 哺乳期間咳嗽可以吃什麼？ | img/breastfeeding_minor_cough.webp |
| 4 | 哺乳期間便祕可以用什麼？ | img/breastfeeding_minor_constipation.webp |
| 5 | 哺乳期間拉肚子，可以吃止瀉藥嗎？ | img/breastfeeding_minor_diarrhea.webp |
| 6 | 哺乳期間胃酸逆流、胃不舒服可以吃什麼？ | img/breastfeeding_minor_reflux.webp |
| 7 | 哺乳期間皮膚癢，可以擦藥或吃藥嗎？ | img/breastfeeding_minor_itch.webp |
| 8 | 哺乳期間睡不好，可以怎麼做？ | img/breastfeeding_minor_insomnia.webp |
| 9 | 哺乳期間乳房脹痛、塞奶怎麼辦？ | img/breastfeeding_minor_engorgement.webp |

**tags（系列）**

哺乳期間小毛病、哺乳用藥、餵母乳可以吃藥嗎、哺乳期吃藥、餵奶吃藥、母乳用藥安全、哺乳媽媽、產後用藥、哺乳頭痛、哺乳發燒、哺乳感冒、哺乳鼻塞、哺乳咳嗽、哺乳便祕、哺乳拉肚子、哺乳胃食道逆流、哺乳皮膚癢、哺乳失眠、塞奶、乳房脹痛、漲奶、乳腺炎、奶量減少、退奶、Acetaminophen、普拿疼、Ibuprofen、布洛芬、Loratadine、Cetirizine、Fexofenadine、Fluticasone、Oxymetazoline、Pseudoephedrine、Methylephedrine、Chlorpheniramine、Dextromethorphan、右美沙芬、Acetylcysteine、Codeine、Dihydrocodeine、可待因、氧化鎂、Lactulose、PEG、Sennoside、Loperamide、ORS、Famotidine、Omeprazole、Hydrocortisone、Melatonin、褪黑激素、產後憂鬱、產後子癲前症、冷敷

> 注意：網站同時用「便秘」「便祕」兩種寫法。網頁內文用「便祕」，tags 兩種都放（加「哺乳便秘」）。

---

## 三、各圖卡：SEO 與網頁文字

AEO 寫法：每段第一句直接回答問題，再補說明；FAQ 句型用民眾會問的口語。

### 卡 1｜cards/breastfeeding_minor_fever_pain.html

- **page_title**：哺乳期間頭痛、發燒可以吃什麼？普拿疼、布洛芬可以嗎｜藥局衛教助手
- **meta_description**：哺乳期間頭痛、發燒，可以使用 Acetaminophen（普拿疼）或 Ibuprofen（布洛芬），多數情況不必停餵母乳。不建議自行吃阿斯匹靈；產後劇烈頭痛、視力模糊或血壓升高要立即就醫。
- **h1**：哺乳期間頭痛、發燒可以吃什麼？
- **image_alt**：哺乳期間頭痛發燒用藥衛教圖卡：可選 Acetaminophen、Ibuprofen，不建議自行吃 Aspirin，產後劇烈頭痛、視力模糊、上腹痛或血壓升高要立即就醫
- **keywords**：哺乳頭痛、哺乳發燒、餵母乳可以吃普拿疼嗎、哺乳吃止痛藥、Acetaminophen、普拿疼、Ibuprofen、布洛芬、阿斯匹靈、產後頭痛、產後子癲前症

**summary**：哺乳期間頭痛或發燒，可以使用 Acetaminophen（乙醯胺酚）或 Ibuprofen（布洛芬），兩者都是哺乳期常用的退燒止痛藥，多數情況不需要停餵母乳。

**sections**
- **怎麼選？**：只需要退燒、止痛時，Acetaminophen 是第一選擇；需要消炎（例如塞奶、牙痛）時可選 Ibuprofen。成人請依包裝標示使用，Acetaminophen 一天總量不要超過包裝建議的上限。服藥可安排在餵奶後，減少寶寶接觸的藥量。
- **避免重複成分**：綜合感冒藥常含 Acetaminophen，和普拿疼一起吃容易過量。購買前先看成分，或請藥師幫忙核對。
- **哪些人用 Ibuprofen 要先問？**：有胃潰瘍、胃出血病史、對 NSAID 過敏、氣喘吃止痛藥會發作，或腎功能不佳者，請先詢問醫師或藥師。
- **不建議自行使用 Aspirin**：阿斯匹靈用於止痛退燒時，哺乳期有其他更適合的選擇。醫師開立的低劑量阿斯匹靈請照處方使用。
- **就醫警訊**：產後 6 週內出現劇烈頭痛、視力模糊、上腹痛、明顯水腫或血壓升高，可能是產後子癲前症，請立即就醫。發燒合併乳房紅腫熱痛，要考慮乳腺炎。

**FAQ**
- 餵母乳可以吃普拿疼嗎？可以。Acetaminophen 是哺乳期間常用的退燒止痛藥，一般劑量不需要停餵。
- 吃完止痛藥要隔多久才能餵奶？Acetaminophen、Ibuprofen 一般不需要特別等待，可在餵奶後服藥。

### 卡 2｜cards/breastfeeding_minor_rhinitis.html

- **page_title**：哺乳期間鼻塞、流鼻水可以用什麼？哪些感冒藥會讓奶量變少｜藥局衛教助手
- **meta_description**：哺乳期間鼻塞，可先用生理食鹽水洗鼻；過敏可用 Loratadine、Cetirizine 或類固醇鼻噴劑。Pseudoephedrine、Methylephedrine 可能減少奶量，購買綜合感冒藥前先看成分。
- **h1**：哺乳期間鼻塞、流鼻水可以用什麼？
- **image_alt**：哺乳期間鼻塞流鼻水用藥衛教圖卡：優先生理食鹽水洗鼻、非嗜睡抗組織胺與類固醇鼻噴劑，Oxymetazoline 最多 3 天，偽麻黃鹼與甲基麻黃鹼可能減少奶量
- **keywords**：哺乳鼻塞、哺乳流鼻水、哺乳過敏性鼻炎、哺乳感冒藥、餵母乳可以吃鼻塞藥嗎、奶量變少、退奶、Pseudoephedrine、偽麻黃鹼、Methylephedrine、Chlorpheniramine、Loratadine、Cetirizine、Fexofenadine、Fluticasone、Oxymetazoline、洗鼻

**summary**：哺乳期間鼻塞、流鼻水，先用生理食鹽水噴鼻或洗鼻；過敏性鼻炎可選較不嗜睡的抗組織胺或類固醇鼻噴劑。選藥時除了寶寶，也要注意奶量。

**sections**
- **優先選擇**：生理食鹽水噴鼻、洗鼻沒有藥物進入母乳的問題，適合先用。過敏引起的鼻水、噴嚏，可選 Loratadine、Cetirizine、Fexofenadine；鼻塞為主可用 Fluticasone、Budesonide 等類固醇鼻噴劑，局部使用，進入母乳的量很少。
- **鼻塞很嚴重時**：Oxymetazoline 鼻噴劑可短期使用，最多連續 3 天，用太久可能反而更塞。
- **可能讓奶量變少的成分**：Pseudoephedrine（偽麻黃鹼）有研究顯示單次服用就可能降低奶量；Methylephedrine（甲基麻黃鹼）作用類似。這兩種成分常見於台灣的綜合感冒藥，奶量還沒穩定、或本來奶量就偏少的媽媽，請避免自行使用。
- **容易嗜睡的抗組織胺**：Chlorpheniramine 等第一代抗組織胺可能讓寶寶嗜睡、喝奶變差，高劑量也可能影響奶量。如果非用不可，以短期、低劑量為主，並觀察寶寶。
- **就醫警訊**：鼻塞超過 10 天、黃綠鼻涕合併臉頰痛或發燒，可能是鼻竇炎，請就醫。

**FAQ**
- 哺乳期間可以吃綜合感冒藥嗎？不建議自行吃。很多綜合感冒藥含偽麻黃鹼、甲基麻黃鹼或嗜睡抗組織胺，可能影響奶量或讓寶寶嗜睡，最好請藥師依症狀挑單一成分。
- 吃鼻塞藥會退奶嗎？Pseudoephedrine 可能減少奶量，尤其產後初期或奶量不穩時要避免。

### 卡 3｜cards/breastfeeding_minor_cough.html

- **page_title**：哺乳期間咳嗽可以吃什麼？止咳藥、化痰藥怎麼選｜藥局衛教助手
- **meta_description**：哺乳期間乾咳可考慮 Dextromethorphan（右美沙芬），有痰可用 Acetylcysteine。含可待因、二氫可待因的止咳藥應避免，買咳嗽藥水前先看成分。
- **h1**：哺乳期間咳嗽可以吃什麼？
- **image_alt**：哺乳期間咳嗽用藥衛教圖卡：乾咳可用 Dextromethorphan，有痰可用 Acetylcysteine，避免含 Codeine、Dihydrocodeine 與甲基麻黃鹼的止咳藥，持續高燒、喘、胸痛、咳血要就醫
- **keywords**：哺乳咳嗽、餵母乳咳嗽藥、哺乳止咳藥、哺乳化痰藥、Dextromethorphan、右美沙芬、Acetylcysteine、化痰藥、Guaifenesin、Ambroxol、Codeine、可待因、Dihydrocodeine、二氫可待因、咳嗽藥水

**summary**：哺乳期間乾咳可考慮 Dextromethorphan（右美沙芬），有痰可考慮 Acetylcysteine。含 Codeine 或 Dihydrocodeine 的止咳藥可能讓寶寶嗜睡、呼吸變慢，應避免自行使用。

**sections**
- **乾咳**：Dextromethorphan 以止咳糖漿的一般劑量使用時，進入母乳的量很低，可作為乾咳的選擇。
- **有痰咳嗽**：先多喝水、避免菸害。化痰藥可考慮 Acetylcysteine；Guaifenesin、Ambroxol 的哺乳期資料較少，不代表有害，需要時請藥師評估，寶寶是新生兒或早產兒時更要先問。
- **要避開的成分**：Codeine（可待因）與 Dihydrocodeine（二氫可待因）屬於鴉片類止咳成分，少數媽媽代謝較快，可能讓寶寶嗜睡、呼吸變慢；台灣不少止咳藥水與綜合感冒藥含二氫可待因。含 Methylephedrine 的複方可能減少奶量；高酒精含量的糖漿也不建議。
- **就醫警訊**：持續高燒、喘、胸痛、咳血，或咳嗽超過 3 週、越來越嚴重，請就醫。

**FAQ**
- 哺乳可以喝咳嗽藥水嗎？可以，但要看成分。避開含可待因、二氫可待因的產品，以 Dextromethorphan 等單純成分為優先。
- 寶寶出現什麼狀況要注意？媽媽吃止咳藥後，寶寶異常嗜睡、叫不醒、喝奶變差或呼吸變慢，要立即就醫。

### 卡 4｜cards/breastfeeding_minor_constipation.html

- **page_title**：哺乳期間便祕可以用什麼？氧化鎂、軟便藥可以吃嗎｜藥局衛教助手
- **meta_description**：產後與哺乳期間便祕很常見。先增加水分與纖維；需要用藥時，氧化鎂、乳果糖、PEG、洋車前子殼都可在哺乳期使用，番瀉苷、Bisacodyl、甘油栓劑可短期使用，不需停餵母乳。
- **h1**：哺乳期間便祕可以用什麼？
- **image_alt**：哺乳期間便祕用藥衛教圖卡：先多喝水與纖維，可選氧化鎂、洋車前子殼、乳果糖、PEG，必要時短期用番瀉苷、Bisacodyl 或甘油栓劑
- **keywords**：哺乳便祕、哺乳便秘、產後便秘、產後便祕、餵母乳可以吃軟便藥嗎、氧化鎂、Magnesium oxide、Lactulose、乳果糖、PEG、Macrogol、Psyllium、洋車前子、Sennoside、番瀉苷、Bisacodyl、甘油栓劑、浣腸

**summary**：哺乳期間便祕，先從喝水、纖維與活動改善；需要用藥時，氧化鎂、乳果糖、PEG 與洋車前子殼都是哺乳期可用的選擇，一般便祕藥不需要停餵母乳。

**sections**
- **先從生活習慣開始**：哺乳會增加水分需求，餵奶時順手喝一杯水。多吃蔬菜、水果、全穀類，依身體恢復狀況適度活動。
- **常用軟便藥**：氧化鎂是台灣最常用的軟便藥，幾乎不進入母乳；腎功能不佳者先問醫師，並與部分抗生素、鐵劑間隔服用。洋車前子殼要配足量水；乳果糖、PEG 可讓糞便保持水分，效果較溫和。
- **短期使用**：番瀉苷、Bisacodyl 屬刺激性瀉劑，必要時短期使用；甘油栓劑作用快、在局部作用。
- **產後特別情況**：會陰傷口或痔瘡疼痛會讓人不敢解便，可以和醫師討論先用軟便藥。
- **就醫警訊**：腹痛明顯、嘔吐、血便，或長期排便困難，請就醫確認原因。

**FAQ**
- 哺乳可以吃氧化鎂嗎？可以。氧化鎂吸收很少，哺乳期間可以使用。
- 吃瀉藥寶寶會拉肚子嗎？常用的軟便藥進入母乳的量很少，一般不會讓寶寶拉肚子。

### 卡 5｜cards/breastfeeding_minor_diarrhea.html

- **page_title**：哺乳期間拉肚子可以吃止瀉藥嗎？還能餵母乳嗎｜藥局衛教助手
- **meta_description**：哺乳媽媽拉肚子，先用口服電解質液少量多次補水，通常可以繼續餵母乳。沒有發燒、血便的成人急性水瀉，可短期使用 Loperamide；次水楊酸鉍不建議自行使用。
- **h1**：哺乳期間拉肚子，可以吃止瀉藥嗎？
- **image_alt**：哺乳期間腹瀉衛教圖卡：先用 ORS 補水，通常可繼續哺乳，必要時短期使用 Loperamide，不建議次水楊酸鉍，發燒、血便、劇烈腹痛或脫水要就醫
- **keywords**：哺乳拉肚子、哺乳腹瀉、拉肚子可以餵母乳嗎、哺乳止瀉藥、Loperamide、洛哌丁胺、ORS、口服電解質液、脫水、次水楊酸鉍、Bismuth subsalicylate

**summary**：哺乳媽媽拉肚子，第一步是補充水分與電解質，通常可以繼續餵母乳。沒有發燒、血便的成人急性水瀉，必要時可短期使用 Loperamide。

**sections**
- **先補水**：腹瀉會流失水分，哺乳又需要更多水分，建議用口服電解質液（ORS）少量多次補充。脫水可能讓奶量暫時下降，補足水分後通常會恢復。
- **還能餵母乳嗎？**：一般腸胃炎通常可以繼續哺乳，母乳中的抗體反而能保護寶寶。抱寶寶、餵奶前後與如廁後都要徹底洗手。
- **止瀉藥**：Loperamide 進入母乳的量很少，沒有警訊的成人急性水瀉可短期使用，請依包裝標示。次水楊酸鉍含水楊酸鹽，不建議自行使用。其他常見止瀉藥（如正露丸、高克痢）的哺乳期使用，可請藥師評估。
- **不要自行止瀉的情況**：發燒、血便、劇烈腹痛或腹脹，表示可能是細菌感染或其他問題，用止瀉藥壓住症狀反而可能延誤。
- **就醫警訊**：發燒、血便、劇烈腹痛，或口乾、尿量明顯減少、頭暈等脫水症狀。

**FAQ**
- 媽媽拉肚子會傳染給寶寶嗎？病菌主要透過手和接觸傳染，不是透過母乳。勤洗手比停餵更重要。
- 拉肚子奶量變少怎麼辦？先補足水分與電解質，持續依寶寶需求哺乳，奶量通常會回來。

### 卡 6｜cards/breastfeeding_minor_reflux.html

- **page_title**：哺乳期間胃酸逆流、胃痛可以吃胃藥嗎？｜藥局衛教助手
- **meta_description**：哺乳期間胃酸逆流，可短期使用制酸劑、海藻酸鹽或 Famotidine，必要時由醫師評估 Omeprazole 等 PPI，不必因胃藥停餵母乳。產後上腹痛合併頭痛、視力模糊要立即就醫。
- **h1**：哺乳期間胃酸逆流、胃不舒服可以吃什麼？
- **image_alt**：哺乳期間胃酸逆流用藥衛教圖卡：先調整飲食與作息，可選制酸劑、海藻酸鹽、Famotidine，必要時醫師評估 PPI，吐血、黑便或產後上腹痛合併頭痛要就醫
- **keywords**：哺乳胃食道逆流、哺乳胃痛、哺乳胃藥、餵母乳可以吃胃藥嗎、制酸劑、胃乳、碳酸鈣、Alginate、海藻酸鹽、Famotidine、Omeprazole、Pantoprazole、PPI、產後上腹痛

**summary**：哺乳期間胃酸逆流、胃不舒服，可以短期使用制酸劑、海藻酸鹽或 Famotidine；症狀較頑固時，可由醫師評估 Omeprazole 等 PPI。多種常見胃藥都不需要停餵母乳。

**sections**
- **先調整習慣**：產後作息不規律、邊顧寶寶邊吃飯，容易吃太快、吃太飽。少量多餐，飯後 2–3 小時內不要躺下，減少油炸、甜食、咖啡與辛辣食物。
- **常見胃藥**：制酸劑（碳酸鈣、鎂鋁鹽類）與海藻酸鹽主要在胃裡作用，吸收很少，適合偶爾發作時使用。Famotidine 抑制胃酸分泌，進入母乳的量少。Omeprazole、Pantoprazole 等 PPI 哺乳期可用，需要時由醫師評估。
- **吃胃藥要注意**：制酸劑會影響部分藥物吸收（如鐵劑、部分抗生素），請錯開服用時間。
- **就醫警訊**：持續劇痛、吐血、黑便、吞嚥困難或體重下降。產後上腹痛合併頭痛、視力模糊或血壓升高，可能是產後子癲前症，請立即就醫。

**FAQ**
- 哺乳可以喝胃乳嗎？可以。制酸劑吸收很少，哺乳期間可以短期使用。
- 胃痛就是胃酸太多嗎？不一定。膽結石、胰臟炎，甚至產後子癲前症都可能上腹痛，反覆或劇烈疼痛要就醫。

### 卡 7｜cards/breastfeeding_minor_itch.html

- **page_title**：哺乳期間皮膚癢可以擦藥嗎？乳頭能擦類固醇嗎｜藥局衛教助手
- **meta_description**：哺乳期間皮膚乾癢，先加強無香料保濕；輕度濕疹可短期擦 Hydrocortisone，需要口服可選 Cetirizine、Loratadine。乳頭或乳暈擦藥要選低效價乳霜、餵奶後擦，避免寶寶吃到藥膏。
- **h1**：哺乳期間皮膚癢，可以擦藥或吃藥嗎？
- **image_alt**：哺乳期間皮膚癢衛教圖卡：先保濕，可短期擦 Hydrocortisone，口服 Cetirizine、Loratadine，乳頭擦藥選低效價乳霜、餵奶後擦，紅腫熱痛流膿要就醫
- **keywords**：哺乳皮膚癢、產後皮膚癢、哺乳濕疹、乳頭濕疹、乳頭擦藥、哺乳擦類固醇、Hydrocortisone、外用類固醇、Cetirizine、Loratadine、保濕乳液

**summary**：哺乳期間皮膚癢，先從保濕與溫和清潔開始；輕度濕疹可短期擦低效價類固醇，需要口服時可選 Cetirizine、Loratadine。擦在乳頭附近時，要避免寶寶直接吃到藥膏。

**sections**
- **皮膚乾癢**：產後荷爾蒙變化、頻繁洗手與睡眠不足，都可能讓皮膚變乾。洗澡水溫不要太熱，洗後 3 分鐘內擦無香料保濕乳液或乳霜。
- **外用藥**：Hydrocortisone 等低效價類固醇適合短期擦在輕度濕疹、發炎處。擦在身體其他部位、面積不大時，進入母乳的量極少。
- **擦在乳頭或乳暈**：先確認成分，由醫師或藥師指導。選低效價類固醇與乳霜劑型，避免軟膏（寶寶可能吃進較多基劑）。餵奶後擦薄薄一層，下次餵奶前若還有殘留，用清水輕輕擦掉。不要在乳房上大範圍使用中、強效類固醇。
- **口服抗組織胺**：Cetirizine、Loratadine 較不嗜睡，適合需要口服止癢時。
- **就醫警訊**：紅腫熱痛、流膿、皮疹擴散，或乳頭持續疼痛、破皮不癒（可能是黴菌感染或含乳姿勢問題）。

**FAQ**
- 擦藥膏後可以馬上餵奶嗎？擦在身體其他部位可以；擦在乳頭附近，建議餵奶後再擦，下次餵奶前先擦掉殘留。

### 卡 8｜cards/breastfeeding_minor_insomnia.html

- **page_title**：哺乳期間睡不好怎麼辦？助眠方法與安眠藥、褪黑激素怎麼用｜藥局衛教助手
- **meta_description**：哺乳期間睡不好，可以從夜奶時保持昏暗、家人分工夜間照顧、白天曬太陽與補眠開始改善；哺乳媽媽每天 1–2 杯咖啡沒問題，下午後少喝。需要藥物時由醫師評估，失眠合併情緒低落要評估產後憂鬱。
- **h1**：哺乳期間睡不好，可以怎麼做？
- **image_alt**：哺乳期間睡不好衛教圖卡：夜奶只開小夜燈、同房不同床、家人分工夜間照顧，白天補眠與曬太陽，咖啡每天 1–2 杯，安眠藥由醫師評估，褪黑激素在台灣屬處方藥，失眠合併情緒低落要評估產後憂鬱
- **keywords**：哺乳失眠、產後失眠、哺乳睡不好怎麼辦、夜奶睡眠、餵奶後睡不著、哺乳咖啡、哺乳安眠藥、餵母乳可以吃安眠藥嗎、哺乳褪黑激素、褪黑激素、失眠認知行為治療、產後憂鬱、產後焦慮

**summary**：哺乳期間睡不好，有很多不用吃藥的方法可以先試：夜奶時保持昏暗、家人分工、白天曬太陽與把握時間補眠。若仍需要藥物，部分安眠藥經醫師評估可以短期使用，不一定要停餵母乳。

**sections**
- **夜奶時，幫自己更快再睡著**：
  - 夜奶只開小夜燈，不開大燈、不滑手機，餵完比較容易接著睡。
  - 寶寶床放在媽媽房間（同房不同床），夜奶不用走遠，抱回床也方便。
  - 換尿布、拍嗝、哄睡交給家人，媽媽只負責餵奶，餵完就回去睡。
- **家人分工，換一段完整睡眠**：用擠出的母乳或依醫囑的配方奶，讓家人餵其中一餐，媽媽可以連續睡 4–5 小時。奶量剛建立的前幾週，若間隔太久會脹奶，可先和醫護人員或泌乳顧問討論怎麼安排。
- **白天這樣做，晚上更好睡**：
  - 寶寶睡時跟著補眠，家事先放一邊，也可以請親友來幫忙。
  - 早上拉開窗簾、帶寶寶出門曬太陽或散步，有助調整媽媽的生理時鐘，也幫寶寶分辨白天和晚上。
  - 每天盡量在差不多的時間起床，作息越固定，越容易入睡。
- **咖啡因與飲食**：哺乳媽媽每天喝 1–2 杯咖啡一般沒問題，但下午以後少喝；茶、可樂、能量飲料也含咖啡因。晚餐不要吃太飽。不要用酒精助眠，酒精會讓睡眠變淺，也會進入母乳。
- **睡前放鬆**：洗溫水澡、做簡單伸展或腹式呼吸，放下手機。躺了一段時間仍睡不著，可以起來做安靜的事，有睡意再回床上，不要躺在床上一直看時間。
- **不吃藥的專業治療**：失眠持續超過一個月，可以詢問醫師「失眠認知行為治療（CBT-I）」。這是不用吃藥的睡眠治療，哺乳期間也適合。
- **助眠藥物**：部分短效安眠藥經醫師評估可以短期使用，醫師會依寶寶年齡、健康狀況挑選。Melatonin 在台灣屬處方藥，需經醫師評估，不是保健食品。
- **不要自己拿感冒藥助眠**：含 Diphenhydramine、Chlorpheniramine 的感冒藥或抗過敏藥，可能讓寶寶嗜睡，也可能影響奶量。
- **安全提醒**：使用任何鎮靜或助眠藥後，不要和寶寶同床或抱著寶寶在沙發上睡著，並留意寶寶是否異常嗜睡、喝奶變差。
- **產後憂鬱與焦慮**：照顧新生兒很累是正常的，但如果寶寶睡了自己還是睡不著，或持續情緒低落、容易哭泣、焦慮、對事情失去興趣超過 2 週，請就醫評估產後憂鬱或焦慮，這些都可以治療。

**FAQ**
- 哺乳期間睡不好可以怎麼做？先從夜奶保持昏暗、家人分擔夜間照顧、白天曬太陽與補眠開始；這些方法不影響母乳，可以同時進行。
- 哺乳可以喝咖啡嗎？可以。每天 1–2 杯一般沒問題，下午以後少喝，避免影響自己的睡眠；若寶寶出現煩躁、難入睡，可再減量。
- 餵母乳可以吃褪黑激素嗎？褪黑激素在台灣是處方藥，哺乳期研究有限，需經醫師評估，不建議自行購買服用。
- 吃安眠藥要停餵母乳嗎？不一定。醫師可以挑選適合哺乳的藥物，不需要因為失眠就放棄哺乳。

### 卡 9｜cards/breastfeeding_minor_engorgement.html

- **page_title**：塞奶、乳房脹痛怎麼辦？冷敷還是熱敷？何時是乳腺炎｜藥局衛教助手
- **meta_description**：塞奶、乳房脹痛時，依寶寶需求正常哺乳，冷敷減少腫脹，避免用力按摩與過度擠奶；可用 Ibuprofen 或 Acetaminophen 止痛。紅腫熱痛合併發燒，或 12–24 小時沒改善要就醫。
- **h1**：哺乳期間乳房脹痛、塞奶怎麼辦？
- **image_alt**：塞奶與乳房脹痛衛教圖卡：依寶寶需求哺乳、冷敷、避免用力按摩與過度擠奶，可用 Ibuprofen、Acetaminophen 止痛，紅腫熱痛發燒或 12–24 小時未改善要就醫
- **keywords**：塞奶、塞奶怎麼辦、乳房脹痛、漲奶、乳腺阻塞、乳腺炎、塞奶冷敷熱敷、塞奶按摩、乳腺炎症狀、乳腺炎抗生素、Ibuprofen、布洛芬、Acetaminophen

**summary**：塞奶、乳房脹痛時，依寶寶需求正常哺乳、冷敷減少腫脹，避免用力按摩與過度擠奶；疼痛可用 Ibuprofen 或 Acetaminophen。紅腫熱痛合併發燒，要考慮乳腺炎並就醫。

**sections**
- **為什麼不要一直擠？**：目前的哺乳醫學建議認為，塞奶多半是乳房組織發炎腫脹，不是奶「卡住」。為了排空而一直擠，反而會刺激更多奶量，讓腫脹更嚴重。依寶寶需求正常餵即可。
- **冷敷，不要長時間熱敷**：餵奶後用毛巾包冰敷袋冷敷，可減輕腫脹與疼痛。長時間熱敷可能讓發炎更明顯。
- **不要用力按摩**：用力推揉可能造成組織受傷、加重發炎。可以用很輕的手法，從乳房往腋下方向輕撫。
- **止痛藥**：Ibuprofen 同時止痛與消炎，Acetaminophen 可止痛退燒，兩者都可在哺乳期使用，請依包裝標示。
- **何時就醫？**：乳房明顯紅腫熱痛、發燒、畏寒或全身不適；照護 12–24 小時仍未改善或惡化；摸到持續的硬塊或有波動感。醫師會評估是否需要抗生素。乳腺炎多數不需要停餵母乳。

**FAQ**
- 塞奶要冷敷還是熱敷？建議冷敷。冷敷可以減少腫脹與疼痛，長時間熱敷可能讓發炎更嚴重。
- 乳腺炎可以繼續餵奶嗎？多數可以，繼續哺乳有助於恢復；若需抗生素，醫師會選擇哺乳期可用的藥物。

---

## 四、站內互連

### A. 與「懷孕期間小毛病」一對一雙向互連（最重要）

| 哺乳版 | 孕期版 |
|---|---|
| breastfeeding_minor_fever_pain | pregnancy_minor_fever_pain |
| breastfeeding_minor_rhinitis | pregnancy_minor_rhinitis |
| breastfeeding_minor_cough | pregnancy_minor_cough |
| breastfeeding_minor_constipation | pregnancy_minor_constipation |
| breastfeeding_minor_diarrhea | pregnancy_minor_diarrhea |
| breastfeeding_minor_reflux | pregnancy_minor_nausea（腸胃不適類，較弱的對應） |
| breastfeeding_minor_itch | pregnancy_minor_itch |
| breastfeeding_minor_insomnia | pregnancy_minor_insomnia |
| breastfeeding_minor_engorgement | （無對應） |

連結文字建議：哺乳版寫「懷孕期間也有同樣困擾？看孕期版」，孕期版寫「產後哺乳期間怎麼用藥？看哺乳版」。

### B. 各卡加連到既有相關頁

| 哺乳版卡 | 連到 | 連結文字建議 |
|---|---|---|
| 2 鼻塞 | cards/nasal_rinse_1.html（洗鼻器） | 洗鼻器怎麼用？ |
| 2 鼻塞 | cards/nasal_1.html（鼻噴劑使用步驟） | 鼻噴劑正確使用步驟 |
| 3 咳嗽 | cards/sore_throat_causes.html | 喉嚨痛一起出現？ |
| 4 便祕 | cards/laxative_comparison.html、cards/constipation_cate.html | 便祕藥怎麼選？各類型比較 |
| 4 便祕 | cards/enema_steps.html | 浣腸怎麼用 |
| 5 腹瀉 | cards/diarrhea_care_1.html、diarrhea_care_2.html | 成人腹瀉居家照顧與就醫警訊 |
| 5 腹瀉 | cards/diarrhea_care_5.html | 寶寶也拉肚子？母乳要不要停 |
| 5 腹瀉 | cards/diarrhea_drugs_1.html、diarrhea_drugs_5.html | 常見止瀉藥怎麼選、Loperamide |
| 6 胃 | cards/stomach_medicine_guide.html、stomach_medicine_alginate.html、stomach_medicine_h2_blocker.html、stomach_medicine_ppi.html | 胃藥怎麼吃？ |
| 7 皮膚癢 | cards/atopic_dermatitis_care.html | 異位性皮膚炎藥膏怎麼擦 |
| 8 失眠 | cards/bzd_z_sleep_aids.html | 常見助眠藥物分類 |
| 1、9 | 卡 1 ↔ 卡 9 互連 | 乳房紅腫發燒？看塞奶與乳腺炎 |

> 回連：上述既有頁面中，若內文有提到「孕婦或哺乳先問藥師」，可在旁加一行連回本系列對應卡。

### C. 主題頁與導覽

- 本系列 topics 放 `pregnancy`、`infant_care`、`gastrointestinal`，讓三個主題頁都列得到。
- 建議把 `pregnancy` 主題名稱改為「懷孕與哺乳」，懷孕、哺乳兩系列放同一主題下。
- 未來若做孕產主題整合頁（比照 topics/acne.html），以「懷孕期間小毛病」「哺乳期間小毛病」「妊娠紋」「驗孕」為主軸。

---

## 五、AEO / SEO 建議

1. **搶「可以嗎」型問句**：民眾常搜「餵母乳可以吃 XX 嗎」。每頁 page_title 都放了一個問句，FAQ 再用口語問法回答，首句直接答「可以／不建議」。
2. **結構化資料**：頁面標 `MedicalWebPage`，加 `lastReviewed: 2026-11-12`、審閱者「藥師」；若產生器支援，FAQ 加 `FAQPage`（瘀青系列曾因產生器不支援而沒做，這次可一併評估）。
3. **台灣在地詞**：普拿疼、胃乳、氧化鎂、塞奶、漲奶、退奶都是台灣民眾實際用詞，放在 keywords 與內文，但不要堆疊。
4. **每頁 keywords 分開寫**：孕期系列每頁都塞了整個系列約 100 個 tags，搜尋引擎無法分辨每頁重點。本系列建議每頁只放自己的 10–15 個字；孕期系列之後也可以比照修正。
5. **E-E-A-T**：頁尾列參考資料（LactMed、NHS SPS、ABM Protocol #36）與查核日期 2026-11-12。
6. **避免禁用字**：build.py 會擋「保證」「治癒」，以上文字已避開。

---

## 六、參考資料

- LactMed（NIH Drugs and Lactation Database）：https://www.ncbi.nlm.nih.gov/books/NBK501922/
- NHS Specialist Pharmacy Service – Safety in breastfeeding：https://www.sps.nhs.uk/
- Academy of Breastfeeding Medicine Clinical Protocol #36: The Mastitis Spectrum (2022)
