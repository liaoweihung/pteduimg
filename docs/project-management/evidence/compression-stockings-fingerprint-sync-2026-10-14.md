# 彈性襪八頁機械指紋同步證據

日期：2026-10-14
相關需求：CR-2026-027 提交前定點修正
目前 Git HEAD：`03b85e16c000d7a194aa9cc724b070c11f7a5ba4`

## 結論

彈性襪八頁的圖片、生成 HTML 與 `data/card_content.json` 對應文字紀錄相對目前 HEAD 均無差異。`page-inventory.csv` 在目前 HEAD 內保存的舊 `content_sha256`／`source_sha256`，與 `scripts/check_project_management.py --propose` 依目前 HEAD 證據重新計算的結果不一致；這是既有清冊機械指紋失同步，不是營養品系列插入造成內容改變。

本次只同步八頁的 `content_sha256`、`source_sha256` 與 `checked_at=2026-10-14`。人工欄位、醫療狀態、圖片、HTML、文字內容、標題、系列順序及收藏鍵均未修改。

## Git 與工具證據

- `git diff --exit-code HEAD -- img/compression_stockings_benefits.webp`：無差異；其餘七張圖片同屬目前 HEAD 已追蹤系列，工作目錄狀態亦無修改。
- `git diff --exit-code HEAD -- cards/compression_stockings_benefits.html`：無差異；八個彈性襪 HTML 均未列於工作目錄修改。
- `git diff HEAD -- data/card_content.json`：本次差異只是在檔案前方新增九筆 `elderly_nutrition_supplements` 紀錄；彈性襪紀錄沒有修改。
- 指紋定義：`content_sha256` 由該頁文字紀錄與圖片 bytes 計算；`source_sha256` 另包含系列 metadata、manual metadata、HTML 與圖片。計算程式為 `scripts/check_project_management.py`。
- 同步後連同九張營養品頁執行定點 `--propose`，結果為零差異、零移除、零來源錯誤；完整管理驗證為零錯誤，18 項管理測試通過。

## 舊值與同步值

| page_id | 舊 content_sha256 | 新 content_sha256 | 舊 source_sha256 | 新 source_sha256 |
|---|---|---|---|---|
| compression_stockings_benefits | `7e6dd05427f54e92de9aeeaffd113620b2af18ddfd26a7471549ea88cd3e26e7` | `5990fb7f091d4c8e0f4c377e4d1d10bd0be24bd4990018c15ade59955ba44ab1` | `b9239d34714656fe68f757da9c9c45b9d4d5f8063a88d69176a5163046b98c6f` | `9a5ef5aa95779dc5bc941f51dffc132f94a1216b9f11de34fe61f86eeef6b838` |
| compression_stockings_pressure | `950e80a04a8e73033591c2ef66ab2b45e4edf3556024d96d7f7fdbbbda853c13` | `e024c0c2f7d34b019f2578bab61c3357fbb008e961ee2977f70fe6f7c4d23690` | `fcd3a05d268596cf734347d0be70833d870349bd06bd160f375ef8b2fe896bac` | `fe6a7a59b5425bb1f5638f611d99ed8e88b3cb08f7927bab89e09cc1f8bde301` |
| compression_stockings_measurement | `76e50ba78d1270102617e88c0b9081f2495ab6187a99c1d4253b33c0cfe8b5dc` | `940f632c5048be38571a7033104b32e7bbd1df0bc22c5bfacb18b985b7019bed` | `e5516f627489b2657ffe9f95b5d8f788fc9baeec0dcd2124ac575eff475427b3` | `216728f636f160104510e6a4137bcb91d4ac15aecb730f177db3479cb4fc132a` |
| compression_stockings_wear_1 | `b0b0de8fe7389f30378fdaa109caa864c59cda947e1ad51f85d76d8349353982` | `00e20d86bfe18d80ba63b7de426c8f2d0246be05ff0e52b28e9a29456098111d` | `810b4937ccba1f0d6d0da1a971945e0e1739f39ca9a834e456722f1ac545fd92` | `433312b790983ff9d3f4c9749237621d3398f09d012f28babd23bfa96b33bfdb` |
| compression_stockings_wear_2 | `164a6f4f40822577a3ffc24f51d4db0c05271f33ff464d05da1d338a8ebae539` | `796d8920f84a5a133b1bb637a9c6ddef618914cd87561d336d7b95649cd33539` | `f3e49ea228ca7fa9f4f0a1ac8289c00b5fb473c09f22e1d25586df5175412a27` | `04874d15a681fd1fa90e65c1fec926b8535b273296ff6d37cd6d4f9d38c3986a` |
| compression_stockings_wear_3 | `691e04e79c5e78834e8bb869e0f2d6e17f7cc710d59c3b2c15f78f3045562b25` | `1628715af1eb964d8f8b7fa9f0662fef0e4001f8a8f6a9366b0915339f8e1ebb` | `4df5154dffaa6571d51a0f4c9ec264a1ac8e2ad2f0f70f9c69172a8b41a9160a` | `d8fbbc406430bc8640281e2a64cdd47d5b17b047d0db991b79ba1d8bdcea6405` |
| compression_stockings_care | `bec0f8c651759189ff75d3ae9fa5056711da7a7e31b17b3d15d0f856471a7cd9` | `c25f548cc227fbc6ccd8469fb2b5ed582955465cbf34e8efa47f68311de16fd5` | `01e3b4265c1347d258d450b36ca3adc54ef8cd1b74398db3cdecbea8edfba8e4` | `ab148c9d857fb8b67a40892275973c3e0f4d1d9c4570af323aa5e9a0b194e041` |
| compression_stockings_safety | `c50cfe0c26966560f37b6077b43f35579272e8c718e8aec20fc17d1748534c9f` | `da7031aa502c368ff0e0f02cf001f0518ca6fe5ce9962ae56b1a947db3fa861f` | `1d884933fd4e2269621477ca6e0db20ed9b8d8dfdc969401bdbeba20e15d86ee` | `ec3276876c1d729750ae4dbebad81f3c4c9e67e16168eb16c3ea90f161ab3703` |
