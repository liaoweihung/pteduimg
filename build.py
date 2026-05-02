import os
import re
import datetime
import json

def build_cards_json():
    print("開始產生 cards.json...")

    with open("cards.manual.json", "r", encoding="utf-8") as file:
        manual_cards = json.load(file)

    existing_cards = {}
    if os.path.exists("cards.json"):
        with open("cards.json", "r", encoding="utf-8") as file:
            existing_cards = json.load(file)

    cards = dict(existing_cards)
    for key, manual_item in manual_cards.items():
        item = dict(manual_item)
        if "steps" not in item and key in existing_cards:
            item["steps"] = existing_cards[key].get("steps", [])
        if "steps" not in item:
            item["steps"] = []
        cards[key] = item

    ordered_cards = dict(
        sorted(
            cards.items(),
            key=lambda kv: (
                kv[1].get("order", 9999),
                kv[1].get("title", kv[0]),
                kv[0],
            ),
        )
    )

    with open("cards.json", "w", encoding="utf-8") as file:
        json.dump(ordered_cards, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"✅ cards.json 已更新，共 {len(ordered_cards)} 筆圖卡。")

def update_service_worker():
    print("啟動自動化打包助理...")

    # 1. 自動掃描 img 資料夾底下的所有圖片
    img_folder = 'img'
    with open('cards.json', 'r', encoding='utf-8') as file:
        cards = json.load(file)

    image_paths = sorted({
        step
        for card in cards.values()
        for step in card.get('steps', [])
        if step.startswith(f'{img_folder}/') or step.startswith('images/')
    })
    
    # 建立 PWA 需要的快取清單 (包含首頁和所有圖片)
    cache_list = ["'./'", "'./index.html'", "'./public.html'", "'./icon.png'"]
    for image_path in image_paths:
        cache_list.append(f"'./{image_path}'")
    
    cache_array_str = ",\n  ".join(cache_list)

    # 2. 用目前的「年月日時分」產生一個絕對不會重複的自動版本號
    now = datetime.datetime.now()
    new_version = f"pwa-cache-v{now.strftime('%Y%m%d%H%M')}"

    # 3. 讀取目前的 sw.js
    with open('sw.js', 'r', encoding='utf-8') as file:
        sw_content = file.read()

    # 4. 利用正規表達式 (Regex) 自動替換版本號與檔案清單
    sw_content = re.sub(
        r"const CACHE_NAME = '.*?';", 
        f"const CACHE_NAME = '{new_version}';", 
        sw_content
    )
    
    sw_content = re.sub(
        r"const urlsToCache = \[.*?\];", 
        f"const urlsToCache = [\n  {cache_array_str}\n];", 
        sw_content, 
        flags=re.DOTALL
    )

    # 5. 寫回 sw.js
    with open('sw.js', 'w', encoding='utf-8') as file:
        file.write(sw_content)

    print(f"✅ 大功告成！")
    print(f"🔄 sw.js 版本號已自動更新為: {new_version}")
    print(f"📦 共自動收錄了 {len(image_paths)} 張圖卡至離線大腦中！")

if __name__ == '__main__':
    build_cards_json()
    update_service_worker()

# 👇 從這裡開始新增：自動化 Sitemap 更新模組 👇
print("開始更新 sitemap.xml...")

# 1. 取得今天的日期 (格式：YYYY-MM-DD)
today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

# 2. 準備 sitemap 的內容 (新增了 public.html)
sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://liaoweihung.github.io/pteduimg/</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://liaoweihung.github.io/pteduimg/public.html</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>"""

# 3. 寫入並存檔
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_content)

print(f"✅ sitemap.xml 已成功更新！最後修改日為：{today_str}")
