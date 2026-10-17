# 品牌化頁首預覽

本目錄是獨立預覽，未套用至正式網站。未執行 build.py、Commit 或 Push。

## 開啟方式
在專案根目錄執行 `python -m http.server 8766 --bind 127.0.0.1`，瀏覽：
http://127.0.0.1:8766/output/brand-header-preview/review.html

- pharmacist.html：藥師版完整功能副本。
- public.html：民眾版完整功能副本。
- review.html：兩版 390px 手機直式並排比較，可點連結開啟完整頁面。

## 設計
保留藥師版 #2c3e50 深藍灰、民眾版既有白底頁首與淺藍導覽。兩版統一品牌名稱，加入版本小字；Logo 使用 48px 白底圓角容器，窄於 360px 時改為 44px。額外品牌紅色只用於版本旁的 4px 小圓點。保留既有導覽、按鈕、內容、篩選和圖卡功能。

Logo 原檔：D:/Downloads/紅臉大鬍子微笑頭像.png；logo.png 是逐位元複製，未重繪、裁切或另行生成。

## 預覽隔離
HTML 為目前首頁副本，以 base ../../ 讀取既有資源；專用 CSS 只由預覽頁載入。雙版本導覽和互相關聯入口指向預覽副本，其他工具與圖卡連結仍可前往本機正式頁面。預覽不註冊 Service Worker、加上 noindex；將副本 localStorage 改成 sessionStorage，避免改寫正式收藏與排序。預覽副本不代表離線快取或正式部署驗證。

重新同步首頁副本：`python output/brand-header-preview/build_preview.py`。

兩版 Logo 與品牌名稱整組置中。上方版本切換按鈕移除 focus 參數，切換後從頁面頂端顯示；相關主題入口保留原定位行為。
