import datetime
import html
import json
import os
import re
from pathlib import Path
from urllib.parse import quote


BASE_URL = "https://liaoweihung.github.io/pteduimg/"
GA_MEASUREMENT_ID = "G-T5R33JYTC0"
ROOT = Path(__file__).resolve().parent
CARDS_JSON = ROOT / "cards.json"
SEO_JSON = ROOT / "seo.json"
CARDS_DIR = ROOT / "cards"
SITE_TITLE = "藥局衛教助手"


CATEGORY_LABELS = {
    "pharmacist_general": "藥師衛教",
    "pharmacist_product": "藥品衛教",
    "public_education": "民眾疾病衛教",
    "site_guide": "網站使用說明",
    "uncategorized": "其他衛教",
}

FORBIDDEN_SEO_WORDS = ("保證", "治癒")


def read_cards():
    with CARDS_JSON.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_seo():
    if not SEO_JSON.exists():
        return {}
    with SEO_JSON.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data if isinstance(data, dict) else {}


def is_scheduled_hidden(card):
    return isinstance(card, dict) and card.get("hidden") is True and bool(card.get("publish_at"))


def page_for_image(path):
    return f"cards/{Path(path).stem}.html"


def abs_url(path):
    return BASE_URL + quote(path.replace("\\", "/"), safe="/:.?=&%#-")


def esc(value):
    return html.escape(str(value or ""), quote=True)


def clean_seo_text(value):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    for word in FORBIDDEN_SEO_WORDS:
        text = text.replace(word, "")
    return text


def step_topic(card_id, card, step, step_index):
    series_title = clean_seo_text(card.get("title") or card_id)
    texts = card.get("texts") or []
    step_text = clean_seo_text(texts[step_index] if step_index < len(texts) else "")
    image_name = Path(step).stem.replace("_", " ").replace("-", " ")

    if step_text and 2 <= len(step_text) <= 24:
        return step_text
    if series_title:
        return series_title
    return clean_seo_text(image_name) or "衛教圖卡"


def seo_description(topic, series_title, category_label):
    topic = clean_seo_text(topic)
    series_title = clean_seo_text(series_title)
    category_label = clean_seo_text(category_label)

    if category_label == "網站使用說明":
        description = f"這張圖卡整理「{topic}」的操作重點，幫助民眾了解如何使用藥局衛教助手。"
    elif topic != series_title:
        description = f"這張圖卡整理「{topic}」重點，幫助民眾了解{series_title}相關衛教資訊。"
    else:
        description = f"這張圖卡整理「{topic}」重點，幫助民眾了解相關衛教資訊與注意事項。"

    if len(description) < 40:
        description = description.rstrip("。") + "，方便就醫或諮詢藥師時參考。"
    if len(description) > 80:
        description = description[:79].rstrip("，、；：。") + "。"
    return clean_seo_text(description)


def fallback_seo_for_card(card_id, card, step, step_index):
    series_title = clean_seo_text(card.get("title") or card_id)
    steps = card.get("steps") or []
    total = len(steps)
    step_number = step_index + 1
    category = card.get("category") or "uncategorized"
    category_label = CATEGORY_LABELS.get(category, category)
    topic = step_topic(card_id, card, step, step_index)
    page_path = page_for_image(step)
    page_url = abs_url(page_path)
    image_url = abs_url(step)

    title_topic = topic or series_title or "衛教圖卡"
    title = f"{title_topic}｜{SITE_TITLE}"
    h1 = title_topic
    description = seo_description(topic, series_title, category_label)
    alt = f"{title_topic}圖卡" if total <= 1 else f"{title_topic}第 {step_number} 張圖卡"
    tags = card.get("tags") or []
    keywords = "、".join(clean_seo_text(tag) for tag in tags if clean_seo_text(tag))

    return {
        "page_title": title,
        "meta_description": description,
        "h1": h1,
        "image_alt": alt,
        "keywords": keywords,
        "og_title": title,
        "og_description": description,
        "og_image": image_url,
        "og_url": page_url,
        "canonical": page_url,
        "twitter_card": "summary_large_image",
    }


def normalize_card_seo(raw_seo, fallback):
    seo = dict(fallback)
    if isinstance(raw_seo, dict):
        for key, value in raw_seo.items():
            if value:
                seo[key] = clean_seo_text(value)

    seo["page_title"] = seo.get("page_title") or fallback["page_title"]
    seo["meta_description"] = seo.get("meta_description") or fallback["meta_description"]
    seo["h1"] = seo.get("h1") or seo["page_title"].split("｜")[0]
    seo["image_alt"] = seo.get("image_alt") or f"{seo['h1']}圖卡"
    seo["keywords"] = seo.get("keywords") or fallback.get("keywords", "")
    seo["og_title"] = seo.get("og_title") or seo["page_title"]
    seo["og_description"] = seo.get("og_description") or seo["meta_description"]
    seo["og_image"] = seo.get("og_image") or fallback["og_image"]
    seo["og_url"] = seo.get("og_url") or fallback["og_url"]
    seo["canonical"] = seo.get("canonical") or fallback["canonical"]
    seo["twitter_card"] = seo.get("twitter_card") or "summary_large_image"
    return seo


def build_seo_index(cards):
    existing_seo = read_seo()
    seo_index = {}
    used_ids = set()

    for card_id, card in cards.items():
        if is_scheduled_hidden(card):
            continue
        steps = card.get("steps") or []
        for index, step in enumerate(steps):
            if not step:
                continue
            image_id = Path(step).stem
            if image_id in used_ids:
                continue
            used_ids.add(image_id)
            page_path = page_for_image(step)
            fallback = fallback_seo_for_card(card_id, card, step, index)
            raw_seo = existing_seo.get(page_path) or existing_seo.get(image_id)
            seo_index[page_path] = normalize_card_seo(raw_seo, fallback)

    SEO_JSON.write_text(
        json.dumps(seo_index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return seo_index


def share_links(page_url, title):
    encoded_url = quote(page_url, safe="")
    encoded_text = quote(title, safe="")
    return {
        "line": f"https://social-plugins.line.me/lineit/share?url={encoded_url}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        "threads": f"https://www.threads.net/intent/post?text={encoded_text}%20{encoded_url}",
    }


def render_related_cards(series_steps, current_step):
    items = []
    for index, step in enumerate(series_steps, start=1):
        page_path = page_for_image(step)
        active = " active" if step == current_step else ""
        items.append(
            f"""
            <a class="related-item{active}" href="../{esc(page_path)}">
                <img src="../{esc(step)}" alt="同系列圖卡 {index}" loading="lazy">
                <span>第 {index} 張</span>
            </a>"""
        )
    return "\n".join(items)


def render_card_page(card_id, card, step, step_index, seo):
    steps = card.get("steps") or []
    total = len(steps)
    step_number = step_index + 1
    category = card.get("category") or "uncategorized"
    category_label = CATEGORY_LABELS.get(category, category)
    default_return_page = "../public.html" if category == "public_education" else "../index.html"
    title = seo["page_title"]
    tracking_title = seo.get("tracking_title") or title
    description = seo["meta_description"]
    keywords = clean_seo_text(seo.get("keywords") or "")
    h1 = clean_seo_text(card.get("title") or seo["h1"])
    image_alt = seo["image_alt"]
    page_path = page_for_image(step)
    page_url = seo["canonical"]
    image_url = seo["og_image"]
    links = share_links(page_url, title)
    related_cards = render_related_cards(steps, step)
    prev_step = steps[step_index - 1] if total > 1 else step
    next_step = steps[(step_index + 1) % total] if total > 1 else step
    prev_url = f"../{page_for_image(prev_step)}"
    next_url = f"../{page_for_image(next_step)}"
    calculator_styles = ""
    info_heading = (
        f"      <h1>{esc(h1)}</h1>\n"
        f"      <p class=\"meta\">{esc(category_label)} · {step_number}/{total}</p>"
    )
    if card_id == "child_height_weight":
        calculator_styles = """    .info-header {
      display:flex;
      align-items:flex-start;
      justify-content:space-between;
      gap:12px;
      margin:0 0 10px;
    }
    .info-title {
      min-width:0;
    }
    .info-header .meta {
      margin:0;
    }
    .calculator-link {
      flex:0 0 auto;
      display:inline-flex;
      align-items:center;
      justify-content:center;
      min-height:34px;
      border:1px solid var(--line);
      border-radius:8px;
      background:#fff;
      color:var(--brand);
      font-size:.9rem;
      font-weight:700;
      text-decoration:none;
      padding:7px 12px;
      box-shadow:0 1px 5px rgba(15,23,42,.06);
      white-space:nowrap;
    }
    .calculator-link:hover,
    .calculator-link:focus-visible {
      border-color:rgba(0,123,131,.35);
      background:rgba(0,123,131,.06);
    }
"""
        info_heading = f"""      <div class="info-header">
        <div class="info-title">
          <h1>{esc(h1)}</h1>
          <p class="meta">{esc(category_label)} · {step_number}/{total}</p>
        </div>
        <a class="calculator-link" href="../growth-calculator.html">直接計算</a>
      </div>"""

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  {f'<meta name="keywords" content="{esc(keywords)}">' if keywords else ''}
  <link rel="canonical" href="{esc(seo['canonical'])}">
  <link rel="icon" type="image/png" href="../icon.png?v=3">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{esc(SITE_TITLE)}">
  <meta property="og:title" content="{esc(seo['og_title'])}">
  <meta property="og:description" content="{esc(seo['og_description'])}">
  <meta property="og:image" content="{esc(image_url)}">
  <meta property="og:url" content="{esc(seo['og_url'])}">
  <meta name="twitter:card" content="{esc(seo['twitter_card'])}">
  <meta name="twitter:title" content="{esc(seo['og_title'])}">
  <meta name="twitter:description" content="{esc(seo['og_description'])}">
  <meta name="twitter:image" content="{esc(image_url)}">
  <script src="../qrious.min.js"></script>
  <script>
    var GA_MEASUREMENT_ID = '{GA_MEASUREMENT_ID}';
    var urlParams = new URLSearchParams(window.location.search);
    var host = window.location.hostname;
    var isPrivateNetworkHost = ['localhost', '127.0.0.1', '::1'].indexOf(host) !== -1
      || /^192\\.168\\./.test(host)
      || /^10\\./.test(host)
      || /^172\\.(1[6-9]|2\\d|3[0-1])\\./.test(host);
    var isLocalPreview = isPrivateNetworkHost || window.location.protocol === 'file:';

    if (urlParams.get('dev') === '1') {{
      localStorage.setItem('isDeveloper', 'true');
    }}
    if (urlParams.get('dev') === '0') {{
      localStorage.removeItem('isDeveloper');
    }}

    window.isAnalyticsDisabled = isLocalPreview || localStorage.getItem('isDeveloper') === 'true';
    window['ga-disable-' + GA_MEASUREMENT_ID] = window.isAnalyticsDisabled;
    function shouldTrackAnalytics() {{
      return !window.isAnalyticsDisabled && typeof gtag === 'function';
    }}
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    if (!window.isAnalyticsDisabled) {{
      var gaScript = document.createElement('script');
      gaScript.async = true;
      gaScript.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_MEASUREMENT_ID;
      document.head.appendChild(gaScript);
      gtag('js', new Date());
      gtag('config', GA_MEASUREMENT_ID, {{
        page_title: {json.dumps(tracking_title, ensure_ascii=False)},
        page_path: '/pteduimg/{page_path}'
      }});
    }}
    (function() {{
      try {{
        var defaultReturnPage = {json.dumps(default_return_page)};
        var referrerPath = document.referrer ? new URL(document.referrer).pathname : '';
        if (defaultReturnPage === '../public.html') {{
          sessionStorage.setItem('pteduimgCardReturnPage', '../public.html');
        }} else if (referrerPath.endsWith('/public.html')) {{
          sessionStorage.setItem('pteduimgCardReturnPage', '../public.html');
        }} else if (referrerPath.endsWith('/index.html') || referrerPath.endsWith('/pteduimg/')) {{
          sessionStorage.setItem('pteduimgCardReturnPage', '../index.html');
        }}
      }} catch (err) {{}}
    }})();
    function returnToCardHome() {{
      location.href = sessionStorage.getItem('pteduimgCardReturnPage') || {json.dumps(default_return_page)};
    }}
    var cardFavoriteKey = {json.dumps(f"{card_id}-{step_index}")};
    var cardShareUrl = {json.dumps(page_url)};
    var cardTitle = {json.dumps(title, ensure_ascii=False)};
    function getFavorites() {{
      try {{
        var saved = JSON.parse(localStorage.getItem('favImages') || '[]');
        return Array.isArray(saved) ? saved : [];
      }} catch (err) {{
        return [];
      }}
    }}
    function setFavoriteButtonState() {{
      var btn = document.getElementById('favorite-button');
      if (!btn) return;
      var isFavorite = getFavorites().indexOf(cardFavoriteKey) !== -1;
      btn.classList.toggle('active', isFavorite);
      btn.setAttribute('aria-pressed', isFavorite ? 'true' : 'false');
      btn.textContent = isFavorite ? '★' : '☆';
      btn.setAttribute('aria-label', isFavorite ? '取消收藏' : '加入收藏');
    }}
    function toggleFavorite() {{
      var favorites = getFavorites();
      var index = favorites.indexOf(cardFavoriteKey);
      if (index === -1) favorites.push(cardFavoriteKey);
      else favorites.splice(index, 1);
      localStorage.setItem('favImages', JSON.stringify(favorites));
      setFavoriteButtonState();
      if (shouldTrackAnalytics()) {{
        gtag('event', index === -1 ? 'add_favorite_card' : 'remove_favorite_card', {{
          card_title: cardTitle,
          step_number: {step_number}
        }});
      }}
    }}
    function showQRCode() {{
      var modal = document.getElementById('qr-modal');
      var canvas = document.getElementById('qr-canvas');
      if (!modal || !canvas || typeof QRious !== 'function') return;
      new QRious({{ element: canvas, value: cardShareUrl, size: 220 }});
      modal.hidden = false;
      if (shouldTrackAnalytics()) {{
        gtag('event', 'show_qr_code', {{
          card_title: cardTitle,
          step_number: {step_number}
        }});
      }}
    }}
    function closeQRCode() {{
      var modal = document.getElementById('qr-modal');
      if (modal) modal.hidden = true;
    }}
    function showSharePanel() {{
      var modal = document.getElementById('share-modal');
      if (modal) modal.hidden = false;
    }}
    function closeSharePanel() {{
      var modal = document.getElementById('share-modal');
      if (modal) modal.hidden = true;
    }}
    function copyCardShareUrl() {{
      navigator.clipboard.writeText(cardShareUrl).then(function() {{
        alert('已複製圖卡連結');
      }});
      if (shouldTrackAnalytics()) {{
        gtag('event', 'share_instruction_card', {{
          method: 'copy',
          card_title: cardTitle,
          step_number: {step_number}
        }});
      }}
    }}
    document.addEventListener('DOMContentLoaded', setFavoriteButtonState);
    if ('serviceWorker' in navigator) {{
      window.addEventListener('load', function() {{
        navigator.serviceWorker.register('../sw.js').catch(function() {{}});
      }});
    }}
  </script>
  <style>
    :root {{ --ink:#263238; --muted:#64748b; --line:#e5e7eb; --brand:#007b83; }}
    * {{ box-sizing:border-box; }}
    body {{
      margin:0;
      background:#fff;
      color:var(--ink);
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC","Microsoft JhengHei",sans-serif;
      line-height:1.45;
    }}
    .image-stage {{
      min-height:calc(100svh - 104px);
      display:grid;
      place-items:center;
      padding:8px;
      background:#fff;
      position:relative;
    }}
    .hero-img {{
      display:block;
      max-width:100%;
      max-height:calc(100svh - 120px);
      width:auto;
      height:auto;
      object-fit:contain;
      background:#fff;
    }}
    .image-side-link {{
      position:absolute;
      top:0;
      bottom:0;
      width:min(22vw,140px);
      background:transparent;
      border:0;
      z-index:2;
      -webkit-tap-highlight-color:transparent;
    }}
    .image-side-link.prev {{ left:0; }}
    .image-side-link.next {{ right:0; }}
    .top-actions {{
      position:sticky;
      top:0;
      z-index:10;
      display:flex;
      min-height:48px;
      justify-content:space-between;
      align-items:center;
      gap:8px;
      padding:7px 8px;
      background:rgba(255,255,255,.72);
      border-bottom:1px solid rgba(229,231,235,.55);
      backdrop-filter:blur(8px);
    }}
    .action-cluster {{
      display:flex;
      gap:6px;
      overflow-x:auto;
    }}
    .pill {{
      pointer-events:auto;
      display:inline-flex;
      align-items:center;
      min-height:34px;
      border:1px solid rgba(255,255,255,.42);
      border-radius:8px;
      background:rgba(255,255,255,.48);
      color:rgba(38,50,56,.76);
      text-decoration:none;
      font-size:.9rem;
      font-weight:700;
      padding:6px 10px;
      box-shadow:0 1px 5px rgba(15,23,42,.06);
      cursor:pointer;
      white-space:nowrap;
    }}
    .pill:hover,
    .pill:focus-visible {{
      background:rgba(255,255,255,.82);
      color:var(--ink);
    }}
    .pill.active {{
      background:rgba(0,123,131,.62);
      border-color:rgba(0,123,131,.2);
      color:#fff;
    }}
    .icon-pill {{
      justify-content:center;
      width:34px;
      min-width:34px;
      padding:0;
      font-size:1.15rem;
      line-height:1;
    }}
    .page-nav {{
      min-height:56px;
      padding:8px 12px 12px;
      display:flex;
      align-items:center;
      justify-content:center;
      gap:18px;
      border-top:1px solid rgba(229,231,235,.7);
      background:#fff;
    }}
    .page-arrow {{
      display:grid;
      place-items:center;
      width:44px;
      height:44px;
      border:1px solid var(--line);
      border-radius:50%;
      background:#fff;
      color:var(--ink);
      text-decoration:none;
      font-size:1.65rem;
      line-height:1;
      box-shadow:0 1px 5px rgba(15,23,42,.06);
    }}
    .page-count {{
      color:var(--muted);
      font-size:.9rem;
      font-weight:700;
      min-width:64px;
      text-align:center;
    }}
    .info {{
      width:min(100%,880px);
      margin:0 auto;
      padding:12px 12px 28px;
    }}
    h1 {{
      margin:0 0 2px;
      font-size:1rem;
      line-height:1.3;
      letter-spacing:0;
    }}
    .meta {{
      margin:0 0 10px;
      color:var(--muted);
      font-size:.86rem;
    }}
{calculator_styles}    .share-row {{
      display:flex;
      gap:8px;
      overflow-x:auto;
      padding-bottom:2px;
      margin:0 0 18px;
    }}
    .share-button {{
      flex:0 0 auto;
      border:1px solid var(--line);
      border-radius:8px;
      background:#fff;
      color:var(--brand);
      font-size:.9rem;
      font-weight:700;
      text-decoration:none;
      padding:8px 10px;
      cursor:pointer;
    }}
    .section-title {{
      margin:0 0 8px;
      color:var(--muted);
      font-size:.88rem;
      font-weight:700;
    }}
    .related-grid {{
      display:grid;
      grid-template-columns:repeat(4,minmax(0,1fr));
      gap:8px;
    }}
    .related-item {{
      display:block;
      border:1px solid var(--line);
      border-radius:6px;
      overflow:hidden;
      background:#fff;
      color:var(--ink);
      text-decoration:none;
    }}
    .related-item.active {{ border-color:var(--brand); }}
    .related-item img {{
      display:block;
      width:100%;
      aspect-ratio:1;
      object-fit:cover;
      background:#fff;
    }}
    .related-item span {{
      display:block;
      padding:4px 5px;
      font-size:.76rem;
      text-align:center;
      white-space:nowrap;
    }}
    .qr-modal {{
      position:fixed;
      inset:0;
      z-index:20;
      display:grid;
      place-items:center;
      padding:18px;
      background:rgba(15,23,42,.34);
    }}
    .qr-modal[hidden] {{ display:none; }}
    .qr-box,
    .share-box {{
      width:min(100%,300px);
      border-radius:10px;
      background:#fff;
      padding:18px;
      text-align:center;
      box-shadow:0 18px 44px rgba(15,23,42,.18);
    }}
    .qr-box canvas {{
      display:block;
      width:220px;
      height:220px;
      margin:0 auto 12px;
    }}
    .qr-close {{
      width:100%;
      border:0;
      border-radius:8px;
      background:var(--brand);
      color:#fff;
      font-weight:700;
      padding:10px 12px;
      cursor:pointer;
    }}
    .share-box {{
      width:min(100%,340px);
      text-align:left;
    }}
    .share-title {{
      margin:0 0 12px;
      font-size:1rem;
      line-height:1.3;
    }}
    .share-modal-actions {{
      display:grid;
      grid-template-columns:1fr 1fr;
      gap:8px;
      margin-bottom:10px;
    }}
    .share-modal-actions .share-button {{
      text-align:center;
      color:var(--brand);
    }}
    @media (min-width:680px) {{
      .image-stage {{ min-height:calc(100svh - 112px); padding:16px; }}
      .hero-img {{ max-height:calc(100svh - 136px); }}
      .page-arrow {{ width:46px; height:46px; }}
      .info {{ padding:14px 16px 36px; }}
      .related-grid {{ grid-template-columns:repeat(8,minmax(0,1fr)); }}
    }}
  </style>
</head>
<body>
  <main>
    <div class="top-actions">
      <button class="pill" type="button" onclick="returnToCardHome()">返回首頁</button>
      <div class="action-cluster">
        <button class="pill icon-pill" type="button" onclick="showQRCode()" aria-label="顯示 QR code">🔲</button>
        <button class="pill icon-pill" id="favorite-button" type="button" onclick="toggleFavorite()" aria-pressed="false" aria-label="加入收藏">☆</button>
        <button class="pill icon-pill" type="button" onclick="showSharePanel()" aria-label="分享圖卡">↗</button>
      </div>
    </div>
    <section class="image-stage" aria-label="{esc(title)}">
      <a class="image-side-link prev" href="{esc(prev_url)}" aria-label="上一張"></a>
      <img class="hero-img" src="../{esc(step)}" alt="{esc(image_alt)}" decoding="async">
      <a class="image-side-link next" href="{esc(next_url)}" aria-label="下一張"></a>
    </section>
    <nav class="page-nav" aria-label="同系列翻頁">
      <a class="page-arrow" href="{esc(prev_url)}" aria-label="上一張">‹</a>
      <span class="page-count">{step_number}/{total}</span>
      <a class="page-arrow" href="{esc(next_url)}" aria-label="下一張">›</a>
    </nav>
    <section class="info">
{info_heading}
      <div class="section-title">同系列圖卡</div>
      <div class="related-grid">
        {related_cards}
      </div>
    </section>
    <div class="qr-modal" id="qr-modal" hidden>
      <div class="qr-box" role="dialog" aria-modal="true" aria-label="圖卡 QR code">
        <canvas id="qr-canvas"></canvas>
        <button class="qr-close" type="button" onclick="closeQRCode()">完成</button>
      </div>
    </div>
    <div class="qr-modal" id="share-modal" hidden>
      <div class="share-box" role="dialog" aria-modal="true" aria-label="分享圖卡">
        <div class="share-title">分享這張圖卡</div>
        <div class="share-modal-actions">
          <a class="share-button" href="{esc(links['line'])}" target="_blank" rel="noopener">LINE</a>
          <a class="share-button" href="{esc(links['facebook'])}" target="_blank" rel="noopener">Facebook</a>
          <a class="share-button" href="{esc(links['threads'])}" target="_blank" rel="noopener">Threads</a>
          <button class="share-button" type="button" onclick="copyCardShareUrl()">複製連結</button>
        </div>
        <button class="qr-close" type="button" onclick="closeSharePanel()">完成</button>
      </div>
    </div>
  </main>
</body>
</html>
"""


def render_404_page():
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>找不到圖卡｜{SITE_TITLE}</title>
  <meta name="description" content="找不到這張衛教圖卡，請返回首頁重新選擇。">
  <link rel="canonical" href="{BASE_URL}404.html">
  <meta name="robots" content="noindex">
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", sans-serif; background: #fff; color: #263238; }}
    main {{ min-height: 100vh; display: grid; place-items: center; padding: 24px; text-align: center; }}
    a {{ display: inline-flex; margin-top: 14px; padding: 10px 16px; border-radius: 8px; background: #007b83; color: #fff; text-decoration: none; font-weight: 700; }}
  </style>
</head>
<body>
  <main>
    <div>
      <h1>找不到這張圖卡</h1>
      <p>這個連結可能已更新，請回首頁重新選擇。</p>
      <a href="{BASE_URL}">返回首頁</a>
    </div>
  </main>
</body>
</html>
"""


def generate_card_pages(cards, seo_index):
    CARDS_DIR.mkdir(exist_ok=True)
    for old_page in CARDS_DIR.glob("*.html"):
        try:
            old_page.unlink()
        except PermissionError:
            # OneDrive can briefly lock generated files on Windows. Current pages
            # are overwritten below, so a locked stale file should not stop builds.
            pass

    generated_pages = []
    used_ids = set()

    for card_id, card in cards.items():
        if is_scheduled_hidden(card):
            continue
        steps = card.get("steps") or []
        for index, step in enumerate(steps):
            if not step:
                continue
            image_id = Path(step).stem
            if image_id in used_ids:
                continue
            used_ids.add(image_id)
            page_path = page_for_image(step)
            seo = seo_index.get(page_path) or fallback_seo_for_card(card_id, card, step, index)
            (ROOT / page_path).write_text(
                render_card_page(card_id, card, step, index, seo),
                encoding="utf-8",
                newline="\n",
            )
            generated_pages.append(page_path)

    (CARDS_DIR / "404.html").write_text(render_404_page(), encoding="utf-8", newline="\n")
    (ROOT / "404.html").write_text(render_404_page(), encoding="utf-8", newline="\n")
    return generated_pages


def update_service_worker(cards, generated_pages):
    sw_path = ROOT / "sw.js"
    if not sw_path.exists():
        return

    image_files = sorted({
        os.path.basename(step)
        for card in cards.values()
        if not is_scheduled_hidden(card)
        for step in card.get("steps", [])
        if isinstance(step, str) and step.startswith("img/")
    })

    cache_items = [
        "./",
        "./index.html",
        "./public.html",
        "./calc.html",
        "./growth-calculator.html",
        "./taiwan_child_growth_data.json",
        "./taiwan_child_growth_data.js",
        "./css/growth-calculator.css",
        "./icon.png",
        "./404.html",
        "./cards.json",
        "./seo.json",
    ]
    cache_items.extend(f"./img/{img}" for img in image_files)
    cache_items.extend(f"./{page}" for page in generated_pages)
    cache_items.append("./cards/404.html")
    cache_array = ",\n  ".join(json.dumps(item, ensure_ascii=False) for item in cache_items)

    now = datetime.datetime.now()
    new_version = f"pwa-cache-v{now.strftime('%Y%m%d%H%M')}"
    sw_content = sw_path.read_text(encoding="utf-8")
    sw_content = re.sub(r"const CACHE_NAME = '.*?';", f"const CACHE_NAME = '{new_version}';", sw_content)
    sw_content = re.sub(
        r"const urlsToCache = \[.*?\];",
        f"const urlsToCache = [\n  {cache_array}\n];",
        sw_content,
        flags=re.DOTALL,
    )
    sw_path.write_text(sw_content, encoding="utf-8", newline="\n")


def update_sitemap(generated_pages):
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    static_pages = [
        ("", "weekly", "1.0"),
        ("index.html", "weekly", "1.0"),
        ("public.html", "weekly", "0.8"),
        ("calc.html", "monthly", "0.7"),
    ]
    urls = []
    for path, freq, priority in static_pages:
        urls.append(
            f"""  <url>
    <loc>{esc(abs_url(path))}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
        )
    for page in generated_pages:
        urls.append(
            f"""  <url>
    <loc>{esc(abs_url(page))}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>"""
        )

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8", newline="\n")
    (ROOT / "sitemap-main.xml").write_text(sitemap, encoding="utf-8", newline="\n")


def update_robots():
    robots = f"""User-agent: *
Allow: /

Sitemap: {abs_url("sitemap-main.xml")}
"""
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8", newline="\n")


def main():
    cards = read_cards()
    seo_index = build_seo_index(cards)
    generated_pages = generate_card_pages(cards, seo_index)
    update_service_worker(cards, generated_pages)
    update_sitemap(generated_pages)
    update_robots()
    print(f"Generated {len(generated_pages)} static card pages.")
    print("Updated seo.json, sitemap.xml, sitemap-main.xml, robots.txt, and sw.js.")


if __name__ == "__main__":
    main()
