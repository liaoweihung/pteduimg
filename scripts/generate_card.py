import base64
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL_PATH = ROOT / "cards.manual.json"
PENDING_DIR = ROOT / "images" / "pending"


def fail(message):
    print(f"錯誤：{message}", file=sys.stderr)
    raise SystemExit(1)


def slugify(topic):
    ascii_part = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    digest = hashlib.sha1(topic.encode("utf-8")).hexdigest()[:10]
    if ascii_part:
        return f"{ascii_part[:48].strip('-')}-{digest}"
    return f"card-{digest}"


def unique_key_and_path(base_slug):
    key = base_slug.replace("-", "_")
    image_path = PENDING_DIR / f"{base_slug}.png"
    counter = 2

    with open(MANUAL_PATH, "r", encoding="utf-8") as file:
        cards = json.load(file)

    while key in cards or image_path.exists():
        key = f"{base_slug.replace('-', '_')}_{counter}"
        image_path = PENDING_DIR / f"{base_slug}-{counter}.png"
        counter += 1

    return key, image_path


def load_manual_cards():
    try:
        with open(MANUAL_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        fail(f"cards.manual.json 不是合法 JSON，請先修正第 {exc.lineno} 行第 {exc.colno} 欄附近。")
    except FileNotFoundError:
        fail("找不到 cards.manual.json。")

    if not isinstance(data, dict):
        fail("cards.manual.json 最外層必須是 JSON 物件。")
    return data


def build_prompt(topic):
    return f"""
請生成一張 1:1 正方形醫療衛教圖卡，主題是「{topic}」。

風格需求：
- 台灣民眾容易理解的衛教資訊圖卡
- 乾淨、可信任、現代、溫暖
- 適合藥局或診所社群貼文
- 圖像以清楚步驟、重點提示、簡單醫療情境為主
- 不要使用恐嚇式畫面，不要血腥，不要品牌藥名
- 若需要文字，請使用繁體中文，字數少、清楚、易讀
- 避免提供診斷結論；可提醒有疑問請諮詢醫師或藥師
""".strip()


def generate_image(prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        fail("找不到 OPENAI_API_KEY。請先在本機環境變數或 GitHub Actions Secrets 設定。")

    payload = {
        "model": os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1"),
        "prompt": prompt,
        "size": os.environ.get("OPENAI_IMAGE_SIZE", "1024x1024"),
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        fail(f"OpenAI 圖片產生失敗：HTTP {exc.code}，{detail}")
    except urllib.error.URLError as exc:
        fail(f"OpenAI 圖片產生失敗：{exc.reason}")
    except TimeoutError:
        fail("OpenAI 圖片產生逾時，請稍後再試。")

    image = (result.get("data") or [{}])[0]
    if image.get("b64_json"):
        return base64.b64decode(image["b64_json"])
    if image.get("url"):
        try:
            with urllib.request.urlopen(image["url"], timeout=120) as response:
                return response.read()
        except urllib.error.URLError as exc:
            fail(f"圖片網址下載失敗：{exc.reason}")

    fail(f"OpenAI 回傳格式中沒有圖片資料：{json.dumps(result, ensure_ascii=False)[:500]}")


def simple_tags(topic):
    tags = ["醫療衛教", "public_education"]
    compact = topic.strip()
    if compact:
        tags.insert(0, compact)
    return tags


def update_manual_cards(cards, key, topic, image_path):
    max_order = max(
        (item.get("order", 0) for item in cards.values() if isinstance(item, dict)),
        default=0,
    )
    relative_image_path = image_path.relative_to(ROOT).as_posix()
    cards[key] = {
        "title": topic,
        "category": "public_education",
        "order": max_order + 10,
        "hidden": True,
        "icon": "🩺",
        "tags": simple_tags(topic),
        "steps": [relative_image_path],
        "created_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
    }

    with open(MANUAL_PATH, "w", encoding="utf-8") as file:
        json.dump(cards, file, ensure_ascii=False, indent=2)
        file.write("\n")


def run_build():
    result = subprocess.run(
        [sys.executable, "build.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        fail("build.py 執行失敗，已停止。")
    print(result.stdout)


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        fail('請輸入主題，例如：python scripts/generate_card.py "眼藥水怎麼點"')

    topic = sys.argv[1].strip()
    cards = load_manual_cards()
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    base_slug = slugify(topic)
    key, image_path = unique_key_and_path(base_slug)
    prompt = build_prompt(topic)

    print(f"主題：{topic}")
    print(f"圖卡 ID：{key}")
    print("開始呼叫 OpenAI Images API...")
    image_bytes = generate_image(prompt)

    image_path.write_bytes(image_bytes)
    print(f"圖片已儲存：{image_path.relative_to(ROOT).as_posix()}")

    update_manual_cards(cards, key, topic, image_path)
    print("cards.manual.json 已新增 hidden 草稿。")

    run_build()
    print("完成。")


if __name__ == "__main__":
    main()
