import argparse
import csv
import datetime
import html
import json
import os
import re
import warnings
from pathlib import Path
from urllib.parse import quote
from scripts.incremental_build import write_if_changed, run_incremental, save_baseline, worker_version

from scripts.card_archive import read_retired_cards, write_retired_pages
from scripts.acne_pilot import load_navigation, render_navigation, STYLES as ACNE_PILOT_STYLES
from scripts.site_footer import render_footer, footer_styles, sync_footer
from scripts.site_header import HEADER_STYLES, render_header
from scripts.acne_pilot import is_acne_topic, render_topic_return, TOP_NAV_STYLES


BASE_URL = "https://liaoweihung.github.io/pteduimg/"
GA_MEASUREMENT_ID = "G-T5R33JYTC0"
ROOT = Path(__file__).resolve().parent
CARDS_JSON = ROOT / "cards.json"
CARDS_MANUAL_JSON = ROOT / "cards.manual.json"
SEO_JSON = ROOT / "seo.json"
CARD_CONTENT_JSON = ROOT / "data" / "card_content.json"
LABEL_LINKS_JSON = ROOT / "data" / "label_links.json"
CARD_TEXT_REPORT = ROOT / "data" / "card_text_web_integration_report.md"
CARDS_DIR = ROOT / "cards"
SITE_TITLE = "藥局衛教助手"


PUBLIC_TOPIC_TITLES = {
    "sports_injury": "運動傷害",
    "skin_wound": "皮膚與傷口",
    "acne": "痘痘／粉刺",
    "eyes": "眼睛",
    "oral_health": "口腔",
    "throat": "喉嚨",
    "infectious_diseases": "傳染病",
    "heat_illness": "中暑",
    "insect_repellent": "防蚊液",
    "gastrointestinal": "胃腸相關",
    "elimination_care": "排泄與照護",
    "infant_care": "嬰幼兒照護",
    "growth": "成長",
    "chronic_conditions": "慢性病",
    "sleep": "睡眠",
    "pregnancy": "懷孕與哺乳",
    "travel_medication": "旅遊與用藥常識",
}


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


def read_manual_cards():
    if CARDS_MANUAL_JSON.exists():
        with CARDS_MANUAL_JSON.open("r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def read_seo():
    if not SEO_JSON.exists():
        return {}
    with SEO_JSON.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data if isinstance(data, dict) else {}


def read_card_content():
    if not CARD_CONTENT_JSON.exists():
        return {}
    with CARD_CONTENT_JSON.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("data/card_content.json must be a JSON array")

    content_index = {}
    for record in data:
        if not isinstance(record, dict) or record.get("matchConfidence") != "high":
            continue
        image = record.get("image")
        if not isinstance(image, str) or not image:
            continue
        content_index[image.replace("\\", "/")] = record
    return content_index


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


def apply_card_content_seo(seo, card_content):
    if not card_content:
        return seo
    title = clean_seo_text(card_content.get("title"))
    summary = clean_seo_text(card_content.get("summary"))
    alt_text = clean_seo_text(card_content.get("altText"))
    if title:
        seo["page_title"] = f"{title}｜{SITE_TITLE}"
        seo["h1"] = title
        seo["og_title"] = seo["page_title"]
    if summary:
        seo["meta_description"] = summary
        seo["og_description"] = summary
    if alt_text:
        seo["image_alt"] = alt_text
    return seo


def build_seo_index(cards, card_content_index, write_output=True, existing_seo=None):
    existing_seo = read_seo() if existing_seo is None else existing_seo
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
            seo = normalize_card_seo(raw_seo, fallback)
            card_content = card_content_index.get(step.replace("\\", "/"))
            seo_index[page_path] = apply_card_content_seo(seo, card_content)

    if write_output:
        write_if_changed(SEO_JSON,
            json.dumps(seo_index, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return seo_index


def read_page_json_ld(path):
    if not path.is_file():
        return {}
    match = re.search(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        path.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    if not match:
        return {}
    try:
        data = json.loads(match.group(1))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def content_modified_date(card_content, page_url):
    # These fields denote substantive text/image revisions, not exports or builds.
    # Never infer a content date from source checks or previously generated HTML.
    content = card_content or {}
    dates = {}
    for field in ("updatedAt", "imageUpdatedAt"):
        value = content.get(field)
        if value is None or value == "":
            continue
        if isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            try:
                datetime.date.fromisoformat(value)
                dates[field] = value
                continue
            except ValueError:
                pass
        warnings.warn(
            f"{page_url}: invalid {field}={value!r}; expected a valid YYYY-MM-DD; ignored.",
            UserWarning,
            stacklevel=2,
        )
    return dates.get("updatedAt") or dates.get("imageUpdatedAt")


def render_json_ld(seo, headline, card_content=None):
    date_modified = content_modified_date(card_content, seo["canonical"])
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "description": seo["meta_description"],
        "image": seo["og_image"],
        "url": seo["canonical"],
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": seo["canonical"],
        },
        "inLanguage": "zh-TW",
        "isPartOf": {
            "@type": "WebSite",
            "name": SITE_TITLE,
            "url": BASE_URL,
        },
    }
    if date_modified:
        data["dateModified"] = date_modified
    keywords = clean_seo_text(seo.get("keywords") or "")
    if keywords:
        data["keywords"] = keywords
    person = read_page_json_ld(ROOT / "author.html").get("mainEntity", {})
    credited_author = clean_seo_text((card_content or {}).get("author"))
    if (isinstance(person, dict) and person.get("@type") == "Person"
            and all(person.get(key) for key in ("@id", "name", "url"))
            and (not credited_author or credited_author == person["name"])):
        data["author"] = {
            "@type": "Person",
            "@id": person["@id"],
            "name": person["name"],
            "url": person["url"],
        }
    return json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")


def share_links(page_url, title):
    encoded_url = quote(page_url, safe="")
    encoded_text = quote(title, safe="")
    return {
        "line": f"https://social-plugins.line.me/lineit/share?url={encoded_url}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        "threads": f"https://www.threads.net/intent/post?text={encoded_text}%20{encoded_url}",
    }


def render_related_cards(series_steps, current_step, seo_index):
    items = []
    for index, step in enumerate(series_steps, start=1):
        page_path = page_for_image(step)
        title = (seo_index.get(page_path) or {}).get("page_title") or f"第 {index} 張"
        title = title.removesuffix(f"｜{SITE_TITLE}")
        current = ' aria-current="page"' if step == current_step else ""
        items.append(
            f'<li><a class="related-item" href="../{esc(page_path)}"{current}>'
            f'{esc(title)}</a></li>'
        )
    return "\n".join(items)


_LABEL_LINKS = None


def read_label_links():
    global _LABEL_LINKS
    if _LABEL_LINKS is None:
        _LABEL_LINKS = {}
        if LABEL_LINKS_JSON.exists():
            with LABEL_LINKS_JSON.open("r", encoding="utf-8") as file:
                data = json.load(file)
            pages = data.get("pages") if isinstance(data, dict) else None
            if isinstance(pages, dict):
                _LABEL_LINKS = {key.replace("\\", "/"): value for key, value in pages.items() if isinstance(value, list)}
    return _LABEL_LINKS


def render_label_links(step):
    items = []
    for entry in read_label_links().get(step.replace("\\", "/"), []):
        if not isinstance(entry, dict):
            continue
        url = entry.get("url", "")
        name = clean_seo_text(entry.get("name"))
        license_number = clean_seo_text(entry.get("license"))
        if not (isinstance(url, str) and url.startswith("https://mcp.fda.gov.tw/") and name):
            continue
        license_html = f'<span class="label-link-license">{esc(license_number)}</span>' if license_number else ""
        items.append(
            f'<li><a class="label-link" href="{esc(url)}" target="_blank" rel="noopener noreferrer">'
            f'<span class="label-link-name">{esc(name)}</span>{license_html}</a></li>'
        )
    if not items:
        return ""
    return (
        '      <section class="label-links" aria-label="食藥署藥品仿單">\n'
        '        <div class="section-title">食藥署藥品仿單</div>\n'
        f'        <ul class="label-link-list">{"".join(items)}</ul>\n'
        '      </section>\n'
    )


LABEL_LINK_STYLES = """    .label-links {
      margin:0 0 18px;
    }
    .label-link-list {
      list-style:none;
      margin:0;
      padding:0;
      display:grid;
      gap:8px;
    }
    .label-link {
      display:flex;
      align-items:stretch;
      min-height:44px;
      border:1px solid var(--line);
      border-radius:10px;
      background:#fff;
      color:var(--ink);
      text-decoration:none;
      overflow:hidden;
    }
    .label-link-name {
      flex:1 1 auto;
      padding:10px 12px;
      font-weight:700;
      line-height:1.45;
      color:var(--brand);
      overflow-wrap:anywhere;
    }
    .label-link-license {
      flex:0 0 auto;
      display:flex;
      align-items:center;
      padding:8px 12px;
      background:var(--brand);
      color:#fff;
      font-size:.82rem;
      font-weight:700;
      white-space:nowrap;
    }
    .label-link-license::after {
      content:"↗";
      margin-left:6px;
    }
    .label-link:hover,
    .label-link:focus-visible {
      border-color:var(--brand);
    }
    @media (max-width:420px) {
      .label-link { flex-direction:column; }
      .label-link-license { justify-content:space-between; }
    }
"""


def render_card_text_content(card_content, h1, category_label, step_number, total, header_link=""):
    if not card_content:
        return ""
    summary = clean_seo_text(card_content.get("summary"))
    section_html = []
    for section in card_content.get("sections") or []:
        if not isinstance(section, dict):
            continue
        heading = clean_seo_text(section.get("heading"))
        text = clean_seo_text(section.get("text"))
        if not heading or not text:
            continue
        section_html.append(
            f"""          <section>
            <h2>{esc(heading)}</h2>
            <p>{esc(text)}</p>
          </section>"""
        )
    sections = "\n".join(section_html)
    reference_links = []
    for reference in card_content.get("references") or []:
        if not isinstance(reference, dict):
            continue
        url = reference.get("url", "")
        label = clean_seo_text(reference.get("title"))
        if isinstance(url, str) and url.startswith("https://") and label:
            reference_links.append(f'<li><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a></li>')
    references = ""
    if reference_links:
        checked_at = clean_seo_text(card_content.get("sourceCheckedAt"))
        date_label = f"（資料查核：{esc(checked_at)}）" if checked_at else ""
        references = f'<section class="card-references"><h2>資料來源{date_label}</h2><ul>{"".join(reference_links)}</ul></section>'
        sections += "\n" + references
    editorial = ""
    if card_content.get("updatedAt") and card_content.get("revisionCredit"):
        editorial_parts = [f'內容更新：{clean_seo_text(card_content["updatedAt"])}']
        for field, label in (("author", "作者"), ("revisionCredit", "本次修訂"), ("reviewStatus", "審閱狀態")):
            if card_content.get("showEditorialDetails") is False:
                continue
            value = clean_seo_text(card_content.get(field))
            if value:
                editorial_parts.append(f"{label}：{value}")
        editorial = '\n        <p class="meta">' + esc(" ｜ ".join(editorial_parts)) + '</p>'
    details_open = " open" if card_content.get("expandText") else ""
    heading = (
        f"<h1>{esc(h1)}</h1>\n"
        f"        <p class=\"meta\">{esc(category_label)} · {step_number}/{total}</p>"
    )
    if header_link:
        heading = (
            "<div class=\"info-header\">\n"
            "          <div class=\"info-title\">\n"
            f"            <h1>{esc(h1)}</h1>\n"
            f"            <p class=\"meta\">{esc(category_label)} · {step_number}/{total}</p>\n"
            "          </div>\n"
            f"          {header_link}\n"
            "        </div>"
        )
    return f"""      <article class="card-text-content">
        {heading}{editorial}
        <details class="card-text-details"{details_open}>
          <summary>文字版重點</summary>
          <div class="card-text-body">
            <p class="card-summary">{esc(summary)}</p>
{sections}
          </div>
        </details>
      </article>"""


def show_shared_footer(card_id, card):
    return bool(card.get("showFooter") or is_acne_topic(card_id, card))


def render_next_reads(card_id, card, cards, manual_cards):
    topics = manual_cards.get(card_id, {}).get("topics") or card.get("topics") or []
    if not topics:
        return ""

    ordered_public_series = [
        (sid, c) for sid, c in cards.items()
        if c.get("category") == "public_education" and not c.get("hidden") and c.get("steps")
    ]

    topic_blocks = []
    seen_series = {card_id}

    for topic_id in topics:
        topic_title = PUBLIC_TOPIC_TITLES.get(topic_id, topic_id)
        candidates = []
        for sid, c in ordered_public_series:
            if sid in seen_series:
                continue
            c_topics = manual_cards.get(sid, {}).get("topics") or c.get("topics") or []
            if topic_id in c_topics:
                candidates.append((sid, c))
                if len(candidates) >= 3:
                    break

        if len(candidates) < 2:
            for sid, c in ordered_public_series:
                if sid == card_id or any(s == sid for s, _ in candidates):
                    continue
                c_topics = manual_cards.get(sid, {}).get("topics") or c.get("topics") or []
                if topic_id in c_topics:
                    candidates.append((sid, c))
                    if len(candidates) >= 3:
                        break

        for sid, _ in candidates:
            seen_series.add(sid)

        series_lis = []
        for sid, c in candidates:
            first_step = c["steps"][0]
            series_lis.append(f'<li><a href="../{esc(page_for_image(first_step))}">{esc(c["title"])}</a></li>')

        list_html = f'<ul class="next-series-list">\n            {"".join(series_lis)}\n          </ul>' if series_lis else ''
        return_link_html = f'<div class="next-topic-return"><a href="../public.html?topic={esc(topic_id)}">‹ 回到『{esc(topic_title)}』主題</a></div>'

        topic_blocks.append(
            f'        <div class="next-topic-group">\n'
            f'          <div class="next-topic-title">主題：{esc(topic_title)}</div>\n'
            f'          {list_html}\n'
            f'          {return_link_html}\n'
            f'        </div>'
        )

    if not topic_blocks:
        return ""

    blocks_html = "\n".join(topic_blocks)
    return (
        f'\n      <div class="next-series-section">\n'
        f'        <div class="section-title">接下來可以看</div>\n'
        f'{blocks_html}\n'
        f'      </div>'
    )


def render_card_page(card_id, card, step, step_index, seo, card_content=None, series_links="", series_seo=None, pilot=None, cards=None, manual_cards=None):
    if cards is None:
        cards = read_cards()
    if manual_cards is None:
        manual_cards = read_manual_cards()
    # Opt-in only: preserve every other series' output and the medical source record.
    if pilot and card_content:
        card_content = {**card_content, "expandText": False}
    steps = card.get("steps") or []
    total = len(steps)
    step_number = step_index + 1
    category = card.get("category") or "uncategorized"
    category_label = CATEGORY_LABELS.get(category, category)
    is_public = (category == "public_education")

    series_topics = (manual_cards.get(card_id, {}).get("topics") or card.get("topics") or []) if is_public else []
    if is_public:
        if len(series_topics) == 1:
            single_topic = series_topics[0]
            single_topic_title = PUBLIC_TOPIC_TITLES.get(single_topic, single_topic)
            default_return_page = f"../public.html?topic={single_topic}"
            default_btn_text = f"‹ 回到『{single_topic_title}』"
        else:
            default_return_page = "../public.html"
            default_btn_text = "‹ 看更多衛教圖卡"
    else:
        default_return_page = "../index.html"
        default_btn_text = "返回首頁"

    title = seo["page_title"]
    tracking_title = seo.get("tracking_title") or title
    description = seo["meta_description"]
    keywords = clean_seo_text(seo.get("keywords") or "")
    h1 = clean_seo_text(seo.get("display_title") or (card_content or {}).get("title") or card.get("title") or seo["h1"])
    manual_card = manual_cards.get(card_id) or {}
    # Series opt-in: H1 uses the per-page card_content title instead of the SEO display_title.
    title_from_card_text = card.get("title_from_card_text", manual_card.get("title_from_card_text"))
    if title_from_card_text is True and card_content:
        h1 = clean_seo_text(card_content["title"])
    image_alt = seo["image_alt"]
    page_path = page_for_image(step)
    acne_topic = is_acne_topic(card_id, card)
    top_actions_class = "top-actions acne-topic-actions" if acne_topic else "top-actions"
    return_navigation = (render_topic_return(page_path) if acne_topic else
                         f'<button class="pill" type="button" onclick="returnToCardHome()">{default_btn_text}</button>')
    is_public_last_step = (category == "public_education" and step_index == total - 1)
    next_reads_html = render_next_reads(card_id, card, cards, manual_cards) if is_public_last_step else ""
    if is_public:
        return_script = f"""    function readHubReturnState() {{
      try {{
        var state = JSON.parse(sessionStorage.getItem('pteduimgReturnState') || 'null');
        if (!state || !state.hub || !state.url || !document.referrer) return null;
        var from = new URL(document.referrer).pathname;
        if (from === new URL(state.url, window.location.href).pathname || from.indexOf('/cards/') !== -1) return state;
      }} catch (err) {{}}
      return null;
    }}
    function updateReturnButton() {{
      try {{
        var btn = document.querySelector('button[onclick="returnToCardHome()"]');
        if (!btn) return;
        var hub = readHubReturnState();
        if (hub) {{
          btn.textContent = '‹ 回到' + hub.hubTitle;
          return;
        }}
        var stateRaw = sessionStorage.getItem('pteduimgReturnState');
        var topicTitles = {json.dumps(PUBLIC_TOPIC_TITLES, ensure_ascii=False)};
        if (stateRaw) {{
          var state = JSON.parse(stateRaw);
          if (state && state.url && !state.hub) {{
            var returnUrl = new URL(state.url, window.location.href);
            var q = returnUrl.searchParams.get('q');
            var topic = returnUrl.searchParams.get('topic');
            if (q && q.trim()) {{
              btn.textContent = '‹ 回到搜尋結果';
              return;
            }}
            if (topic && topic !== 'all' && topicTitles[topic]) {{
              btn.textContent = '‹ 回到『' + topicTitles[topic] + '』';
              return;
            }}
            btn.textContent = '‹ 看更多衛教圖卡';
            return;
          }}
        }}
        btn.textContent = {json.dumps(default_btn_text)};
      }} catch (err) {{}}
    }}
    if (document.readyState === 'loading') {{
      document.addEventListener('DOMContentLoaded', updateReturnButton);
    }} else {{
      updateReturnButton();
    }}
    function returnToCardHome() {{
      try {{
        var stateRaw = sessionStorage.getItem('pteduimgReturnState');
        if (stateRaw) {{
          var state = JSON.parse(stateRaw);
          if (state && state.url && (!state.hub || readHubReturnState())) {{
            sessionStorage.setItem('pteduimgRestorePending', '1');
            location.href = state.url;
            return;
          }}
        }}
      }} catch (err) {{}}
      location.href = {json.dumps(default_return_page)};
    }}"""
    else:
        return_script = """    function readHubReturnState() {
      try {
        var state = JSON.parse(sessionStorage.getItem('pteduimgReturnState') || 'null');
        if (!state || !state.hub || !state.url || !document.referrer) return null;
        var from = new URL(document.referrer).pathname;
        if (from === new URL(state.url, window.location.href).pathname || from.indexOf('/cards/') !== -1) return state;
      } catch (err) {}
      return null;
    }
    function updateReturnButton() {
      var hub = readHubReturnState();
      var btn = document.querySelector('button[onclick="returnToCardHome()"]');
      if (hub && btn) btn.textContent = '‹ 回到' + hub.hubTitle;
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', updateReturnButton);
    } else {
      updateReturnButton();
    }
    function returnToCardHome() {
      var hub = readHubReturnState();
      if (hub) {
        try { sessionStorage.setItem('pteduimgRestorePending', '1'); } catch (err) {}
        location.href = hub.url;
        return;
      }
      location.href = "../index.html";
    }"""
    topic_nav_styles = TOP_NAV_STYLES if acne_topic else ""
    mobile_nav_styles = """
    @media (max-width:679px) {
      .image-stage { min-height:0; padding:12px 8px; }
      .hero-img { max-height:calc(100svh - 220px); }
    }
""" if acne_topic else ""
    header_html = render_header(return_navigation, '      <div class="action-cluster">\n        <button class="pill icon-pill" type="button" onclick="showQRCode()" aria-label="顯示 QR code">🔲</button>\n        <button class="pill icon-pill" id="favorite-button" type="button" onclick="toggleFavorite()" aria-pressed="false" aria-label="加入收藏">☆</button>\n        <button class="pill icon-pill" type="button" onclick="showSharePanel()" aria-label="分享圖卡">↗</button>\n      </div>', top_actions_class)
    page_url = seo["canonical"]
    image_url = seo["og_image"]
    json_ld = render_json_ld(seo, h1, card_content)
    links = share_links(page_url, title)
    related_cards = render_related_cards(steps, step, series_seo or {})
    label_links_html = render_label_links(step)
    pilot_navigation = render_navigation(pilot) if pilot else ""
    pilot_footer_start = '      <footer class="acne-pilot-footer">\n' if pilot else ""
    pilot_footer_end = '\n      </footer>\n' + render_footer(ROOT, page_path) if pilot else ""
    shared_footer = '\n' + render_footer(ROOT, page_path) if show_shared_footer(card_id, card) and not pilot else ""
    prev_step = steps[step_index - 1] if total > 1 else step
    next_step = steps[(step_index + 1) % total] if total > 1 else step
    prev_url = f"../{page_for_image(prev_step)}"
    next_url = f"../{page_for_image(next_step)}"
    calculator_styles = ""
    card_text_styles = ""
    info_heading = (
        f"      <h1>{esc(h1)}</h1>\n"
        f"      <p class=\"meta\">{esc(category_label)} · {step_number}/{total}</p>"
    )
    if card_content:
        info_heading = render_card_text_content(card_content, h1, category_label, step_number, total)
        card_text_styles = """    .card-text-content {
      margin:0 0 18px;
    }
    .card-text-details {
      border:1px solid var(--line);
      border-radius:10px;
      background:#fff;
      overflow:hidden;
    }
    .card-text-details summary {
      display:flex;
      align-items:center;
      gap:8px;
      min-height:44px;
      padding:10px 12px;
      color:var(--brand);
      font-size:.95rem;
      font-weight:700;
      cursor:pointer;
      list-style:none;
    }
    .card-text-details summary::-webkit-details-marker { display:none; }
    .card-text-details summary::before {
      content:"▼";
      display:inline-block;
      font-size:.72rem;
      transition:transform .18s ease;
    }
    .card-text-details[open] summary::before { transform:rotate(180deg); }
    .card-text-details[open] summary { border-bottom:1px solid var(--line); }
    .card-text-body {
      padding:12px;
      color:var(--ink);
      font-size:.95rem;
      line-height:1.65;
    }
    .card-text-body .card-summary {
      margin:0 0 14px;
      color:#475569;
    }
    .card-text-body section + section {
      margin-top:14px;
      padding-top:14px;
      border-top:1px solid var(--line);
    }
    .card-text-body h2 {
      margin:0 0 5px;
      font-size:1rem;
      line-height:1.4;
    }
    .card-text-body section p { margin:0; }
"""
    # Series opt-in: "tool_link": {"title", "url"} shows a tool button beside the H1; url is relative to cards/.
    tool_link = card.get("tool_link") or manual_card.get("tool_link") or {}
    tool_link_title = str(tool_link.get("title") or "").strip() if isinstance(tool_link, dict) else ""
    tool_link_url = str(tool_link.get("url") or "").strip() if isinstance(tool_link, dict) else ""
    if tool_link_title and tool_link_url:
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
        calculator_link = f'<a class="calculator-link" href="{esc(tool_link_url)}">{esc(tool_link_title)}</a>'
        if card_content:
            info_heading = render_card_text_content(
                card_content, h1, category_label, step_number, total, header_link=calculator_link
            )
        else:
            info_heading = f"""      <div class="info-header">
        <div class="info-title">
          <h1>{esc(h1)}</h1>
          <p class="meta">{esc(category_label)} · {step_number}/{total}</p>
        </div>
        {calculator_link}
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
  <script type="application/ld+json">
{json_ld}
  </script>
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
{return_script}
    var cardFavoriteKey = {json.dumps((card.get('favorite_keys') or [f'{card_id}-{i}' for i in range(total)])[step_index])};
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
      var isAdding = index === -1;
      if (isAdding) favorites.push(cardFavoriteKey);
      else favorites.splice(index, 1);
      localStorage.setItem('favImages', JSON.stringify(favorites));
      setFavoriteButtonState();
      showFavoriteToast(isAdding ? '已加入常用圖卡' : '已從常用圖卡移除');
      if (shouldTrackAnalytics()) {{
        gtag('event', isAdding ? 'add_favorite_card' : 'remove_favorite_card', {{
          card_title: cardTitle,
          step_number: {step_number}
        }});
      }}
    }}
    var favoriteToastTimer = null;
    function showFavoriteToast(message) {{
      var toast = document.getElementById('favorite-toast');
      if (!toast) return;
      toast.textContent = message;
      toast.classList.add('show');
      clearTimeout(favoriteToastTimer);
      favoriteToastTimer = setTimeout(function() {{
        toast.classList.remove('show');
      }}, 1800);
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
{HEADER_STYLES}    .page-nav {{
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
{card_text_styles}{calculator_styles}    .share-row {{
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
    .related-list {{
      margin:0;
      padding-left:1.6rem;
    }}
    .related-list li {{ margin:4px 0; }}
    .related-item {{
      display:block;
      padding:10px 8px;
      min-height:44px;
      color:var(--brand);
      line-height:1.5;
      overflow-wrap:anywhere;
      text-decoration:underline;
      text-underline-offset:3px;
    }}
    .related-item[aria-current="page"] {{
      font-weight:700;
      background:#f0f9f9;
      border-radius:6px;
    }}
    .next-series-section {{
      margin-top:20px;
    }}
    .next-topic-group {{
      margin:10px 0 16px;
    }}
    .next-topic-title {{
      font-size:.88rem;
      font-weight:700;
      color:#203b48;
      margin:6px 0;
    }}
    .next-series-list {{
      list-style:disc;
      margin:0 0 6px;
      padding-left:1.6rem;
      line-height:2.2;
    }}
    .next-series-list li {{
      margin:4px 0;
    }}
    .next-series-list a {{
      color:var(--brand);
      text-decoration:underline;
      text-underline-offset:3px;
    }}
    .next-topic-return {{
      margin:6px 0 10px;
    }}
    .next-topic-return a {{
      display:inline-flex;
      align-items:center;
      min-height:36px;
      color:var(--brand);
      font-weight:600;
      font-size:.88rem;
      text-decoration:none;
    }}
    .next-topic-return a:hover {{
      text-decoration:underline;
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
    .qr-title {{
      margin:0 0 6px;
      color:var(--ink);
      font-size:1.05rem;
      line-height:1.35;
    }}
    .qr-hint {{
      margin:0 0 16px;
      color:var(--muted);
      font-size:.9rem;
      line-height:1.45;
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
    .favorite-toast {{
      position:fixed;
      left:50%;
      bottom:26px;
      z-index:30;
      max-width:calc(100vw - 40px);
      padding:11px 16px;
      border-radius:999px;
      background:rgba(38,50,56,.96);
      color:#fff;
      font-size:.95rem;
      font-weight:700;
      line-height:1.35;
      box-shadow:0 8px 24px rgba(0,0,0,.22);
      opacity:0;
      pointer-events:none;
      transform:translate(-50%,12px);
      transition:opacity .2s ease, transform .2s ease;
    }}
    .favorite-toast.show {{
      opacity:1;
      transform:translate(-50%,0);
    }}
    @media (min-width:680px) {{
      .image-stage {{ min-height:calc(100svh - 112px); padding:16px; }}
      .hero-img {{ max-height:calc(100svh - 136px); }}
      .page-arrow {{ width:46px; height:46px; }}
      .info {{ padding:14px 16px 36px; }}
    }}
{topic_nav_styles}{mobile_nav_styles}  </style>
</head>
<body>
  <main>
{header_html}
    <section class="image-stage" aria-label="{esc(title)}">
      <a class="image-side-link prev" href="{esc(prev_url)}" aria-label="上一張"></a>
      <img class="hero-img" src="../{esc(step)}" alt="{esc(image_alt)}" decoding="async" fetchpriority="high">
      <a class="image-side-link next" href="{esc(next_url)}" aria-label="下一張"></a>
    </section>
    <nav class="page-nav" aria-label="同系列翻頁">
      <a class="page-arrow" href="{esc(prev_url)}" aria-label="上一張">‹</a>
      <span class="page-count">{step_number}/{total}</span>
      <a class="page-arrow" href="{esc(next_url)}" aria-label="下一張">›</a>
    </nav>
    <section class="info">
{info_heading}
{label_links_html}{pilot_navigation}{pilot_footer_start}      <div class="section-title">同系列圖卡</div>
      <ol class="related-list" aria-label="同系列圖卡">
        {related_cards}
      </ol>{next_reads_html}{series_links}{pilot_footer_end}
    </section>{shared_footer}
    <div class="qr-modal" id="qr-modal" hidden>
      <div class="qr-box" role="dialog" aria-modal="true" aria-label="圖卡 QR code">
        <div class="qr-title">請患者掃描開啟這張圖卡</div>
        <p class="qr-hint">掃描後會直接打開目前這張衛教圖卡。</p>
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
    <div id="favorite-toast" class="favorite-toast" role="status" aria-live="polite"></div>
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


def render_all_cards_page(cards, seo_index):
    sections = []
    total_pages = 0
    used_ids = set()

    for card_id, card in cards.items():
        if is_scheduled_hidden(card):
            continue
        steps = card.get("steps") or []
        if not steps:
            continue

        series_title = clean_seo_text(card.get("title") or card_id)
        category = card.get("category") or "uncategorized"
        category_label = CATEGORY_LABELS.get(category, category)
        tags = [clean_seo_text(tag) for tag in (card.get("tags") or []) if clean_seo_text(tag)]
        items = []

        for index, step in enumerate(steps):
            if not step:
                continue
            image_id = Path(step).stem
            if image_id in used_ids:
                continue
            used_ids.add(image_id)
            page_path = page_for_image(step)
            seo = seo_index.get(page_path) or fallback_seo_for_card(card_id, card, step, index)
            topic = clean_seo_text(seo.get("h1") or step_topic(card_id, card, step, index))
            description = clean_seo_text(seo.get("meta_description") or "")
            keyword_text = clean_seo_text(seo.get("keywords") or "?".join(tags))
            total_pages += 1
            items.append(
                f"""          <li>
            <a href=\"{esc(page_path)}\">{esc(topic)}</a>
            <p>{esc(description)}</p>
            {f'<small>{esc(keyword_text)}</small>' if keyword_text else ''}
          </li>"""
            )

        if not items:
            continue

        sections.append(
            f"""      <section class=\"series\">
        <h2>{esc(series_title)}</h2>
        <p class=\"series-meta\">{esc(category_label)} ? {len(items)} ???</p>
        <ol>
{chr(10).join(items)}
        </ol>
      </section>"""
        )

    generated_at = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d")
    return f"""<!DOCTYPE html>
<html lang=\"zh-TW\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>?????????{SITE_TITLE}</title>
  <meta name=\"description\" content=\"???????????????????????????????????\">
  <link rel=\"canonical\" href=\"{esc(abs_url('all-cards.html'))}\">
  <style>
    :root {{ color-scheme: light; --brand:#007b83; --ink:#263238; --muted:#607d8b; --line:#dfe7ea; --bg:#f6fafb; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",\"Noto Sans TC\",sans-serif; color:var(--ink); background:var(--bg); line-height:1.65; }}
    header {{ background:#fff; border-bottom:1px solid var(--line); }}
    .wrap {{ width:min(1080px, calc(100% - 32px)); margin:0 auto; }}
    .hero {{ padding:28px 0 22px; }}
    .crumbs {{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:12px; font-size:.95rem; }}
    a {{ color:var(--brand); text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    h1 {{ margin:0 0 8px; font-size:clamp(1.8rem, 4vw, 2.6rem); line-height:1.18; letter-spacing:0; }}
    h2 {{ margin:0; font-size:1.2rem; letter-spacing:0; }}
    .lead {{ margin:0; color:var(--muted); max-width:760px; }}
    .stats {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:16px; color:var(--muted); font-size:.95rem; }}
    main {{ padding:24px 0 44px; }}
    .series {{ padding:18px 0 20px; border-bottom:1px solid var(--line); }}
    .series-meta {{ margin:2px 0 12px; color:var(--muted); font-size:.92rem; }}
    ol {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:12px 18px; list-style:none; padding:0; margin:0; }}
    li {{ min-width:0; padding:0; }}
    li a {{ display:inline-block; font-weight:700; }}
    li p {{ margin:4px 0 0; color:#455a64; font-size:.94rem; }}
    small {{ display:block; margin-top:4px; color:var(--muted); font-size:.82rem; overflow-wrap:anywhere; }}
    footer {{ padding:20px 0 32px; color:var(--muted); font-size:.9rem; }}
  </style>
</head>
<body>
  <header>
    <div class=\"wrap hero\">
      <nav class=\"crumbs\" aria-label=\"????\">
        <a href=\"./\">????</a>
        <a href=\"./public.html\">??????</a>
      </nav>
      <h1>????????</h1>
      <p class=\"lead\">????????????????????????????????????????</p>
      <div class=\"stats\">
        <span>? {total_pages} ???</span>
        <span>?????{generated_at}</span>
      </div>
    </div>
  </header>
  <main>
    <div class=\"wrap\">
{chr(10).join(sections)}
    </div>
  </main>
  <footer>
    <div class=\"wrap\">? 2026 DiamondL ??????</div>
  </footer>
</body>
</html>
"""


def generate_card_pages(cards, seo_index, card_content_index, only_image_ids=None, render_only=False):
    pilot_pages = load_navigation(ROOT)
    if not render_only:
        CARDS_DIR.mkdir(exist_ok=True)
    if only_image_ids is None and not render_only:
        for old_page in CARDS_DIR.glob("*.html"):
            try:
                old_page.unlink()
            except PermissionError:
                # OneDrive can briefly lock generated files on Windows. Current pages
                # are overwritten below, so a locked stale file should not stop builds.
                pass

    manual_cards = read_manual_cards()
    generated_pages = []
    rendered = {}
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
            if only_image_ids is not None and image_id not in only_image_ids:
                continue
            page_path = page_for_image(step)
            seo = seo_index.get(page_path) or fallback_seo_for_card(card_id, card, step, index)
            card_content = card_content_index.get(step.replace("\\", "/"))
            page_html = render_card_page(card_id, card, step, index, seo, card_content,
                                        render_series_links(card, cards, card_content), seo_index,
                                        pilot=pilot_pages.get(image_id),
                                        cards=cards, manual_cards=manual_cards)
            if render_label_links(step):
                page_html = page_html.replace("  </style>", LABEL_LINK_STYLES + "  </style>", 1)
            if image_id in pilot_pages:
                page_html = page_html.replace("  </style>", ACNE_PILOT_STYLES + footer_styles(ROOT) + "\n  </style>", 1)
            elif show_shared_footer(card_id, card):
                page_html = page_html.replace("  </style>", footer_styles(ROOT) + "\n  </style>", 1)
            rendered[page_path] = page_html
            if not render_only:
                write_if_changed(ROOT / page_path, page_html)
            generated_pages.append(page_path)

    if only_image_ids is None and not render_only:
        write_if_changed(CARDS_DIR / "404.html", render_404_page())
        write_if_changed(ROOT / "404.html", render_404_page())
    return rendered if render_only else generated_pages


def render_series_links(card, cards, card_content=None):
    parts = []
    note = card.get('image_numbering_note')
    if note:
        parts.append(f'<p class="meta">{esc(note)}</p>')
    if card_content and card_content.get('related_links'):
        page_links = []
        for item in card_content['related_links']:
            page_links.append(f'<li><a href="{esc(item["url"])}">{esc(item["title"])}</a></li>')
        if page_links:
            parts.append('<nav aria-label="推薦閱讀"><div class="section-title">推薦閱讀</div><ul style="line-height:2.4; margin:0; padding-left:20px;">' + ''.join(page_links) + '</ul></nav>')
    links = []
    for key in card.get('related_series', []):
        related = cards.get(key)
        if not related or related.get('hidden') or not related.get('steps'):
            continue
        links.append(f'<li><a href="../{esc(page_for_image(related["steps"][0]))}">{esc(related["title"])}</a></li>')
    if links:
        parts.append('<nav aria-label="相關系列"><div class="section-title">相關系列</div><ul style="line-height:2.4; margin:0; padding-left:20px;">' + ''.join(links) + '</ul></nav>')
    return '\n      ' + '\n      '.join(parts) if parts else ''


def markdown_cell(value):
    return clean_seo_text(value).replace("|", "\\|") or "—"


def build_card_text_integration_report(card_content_index):
    rows = []
    success_count = 0
    for image, record in card_content_index.items():
        page_path = ROOT / page_for_image(image)
        expected_title = clean_seo_text(record.get("title"))
        expected_summary = clean_seo_text(record.get("summary"))
        expected_alt = clean_seo_text(record.get("altText"))
        expected_url = clean_seo_text(record.get("url")) or abs_url(page_for_image(image))
        errors = []
        page_html = page_path.read_text(encoding="utf-8") if page_path.exists() else ""

        title_match = re.search(r"<title>(.*?)</title>", page_html, flags=re.DOTALL)
        description_match = re.search(r'<meta name="description" content="(.*?)">', page_html, flags=re.DOTALL)
        h1_matches = re.findall(r"<h1>(.*?)</h1>", page_html, flags=re.DOTALL)
        alt_match = re.search(r'<img class="hero-img"[^>]* alt="(.*?)"', page_html, flags=re.DOTALL)
        canonical_match = re.search(r'<link rel="canonical" href="(.*?)">', page_html, flags=re.DOTALL)

        title_ok = bool(title_match and expected_title and expected_title in html.unescape(title_match.group(1)))
        description_ok = bool(
            description_match and expected_summary
            and html.unescape(description_match.group(1)) == expected_summary
        )
        h1_ok = bool(
            len(h1_matches) == 1 and expected_title
            and html.unescape(h1_matches[0]).strip() == expected_title
        )
        alt_ok = bool(alt_match and expected_alt and html.unescape(alt_match.group(1)) == expected_alt)
        sections = [section for section in (record.get("sections") or []) if isinstance(section, dict)]
        html_text_ok = bool(
            '<article class="card-text-content">' in page_html
            and re.search(r'<details class="card-text-details"(?: open)?>', page_html)
            and '<p class="card-summary">' in page_html
            and expected_summary
            and esc(expected_summary) in page_html
            and sections
            and all(
                f"<h2>{esc(clean_seo_text(section.get('heading')))}</h2>" in page_html
                and f"<p>{esc(clean_seo_text(section.get('text')))}</p>" in page_html
                for section in sections
            )
        )
        canonical_ok = bool(
            canonical_match
            and html.unescape(canonical_match.group(1)) == abs_url(page_for_image(image))
        )

        checks = {
            "title": title_ok,
            "meta description": description_ok,
            "h1": h1_ok,
            "alt": alt_ok,
            "HTML text": html_text_ok,
            "canonical": canonical_ok,
        }
        for label, passed in checks.items():
            if not passed:
                errors.append(f"{label} 未完成")
        if not page_path.exists():
            errors.insert(0, "頁面不存在")
        if not errors:
            success_count += 1

        yes_no = lambda value: "是" if value else "否"
        rows.append(
            "| " + " | ".join([
                markdown_cell(record.get("cardId")),
                markdown_cell(expected_title),
                markdown_cell(expected_url),
                yes_no(title_ok),
                yes_no(description_ok),
                yes_no(h1_ok),
                yes_no(alt_ok),
                yes_no(html_text_ok),
                markdown_cell("；".join(errors) if errors else "無"),
            ]) + " |"
        )

    failure_count = len(card_content_index) - success_count
    report = [
        "# 圖卡文字網頁整合報告",
        "",
        f"- 成功加入文字頁數：{success_count}",
        f"- 失敗頁數：{failure_count}",
        "",
        "| cardId | title | URL | title 完成 | meta description 完成 | h1 完成 | alt 完成 | HTML text 完成 | 錯誤 |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
        *rows,
        "",
    ]
    write_if_changed(CARD_TEXT_REPORT, "\n".join(report))
    return success_count, failure_count


def _page_css_ref(name, page="index.html"):
    """Return the versioned CSS URL (e.g. ./css/base.css?v=7) the page actually links."""
    text = (ROOT / page).read_text(encoding="utf-8")
    match = re.search(rf'\./css/{re.escape(name)}\?v=\d+', text)
    if not match:
        raise RuntimeError(f"{page} 找不到 {name} 的版本參照")
    return match.group(0)


def update_service_worker(cards, generated_pages, retired_pages=(), source_root=None):
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
        "./all-cards.html",
        "./calc.html",
        "./spray_medicine_explorer.html",
        "./suppository_medicine_explorer.html",
        "./oral_liquid_medicine_explorer.html",
        "./inhaler_medicine_explorer.html",
        "./tcm_external_patch_explorer.html",
        "./tcm_external_formula_patterns.html",
        "./css/spray-medicine-explorer.css",
        "./js/spray-medicine-explorer.js",
        "./data/spray_meds_rebuild_20260714/final/spray_meds_final.json",
        "./css/suppository-medicine-explorer.css",
        "./js/suppository-medicine-explorer.js",
        "./data/suppository_meds_rebuild_20260714/final/suppository_meds_final.json",
        "./css/oral-liquid-medicine-explorer.css",
        "./js/oral-liquid-medicine-explorer.js",
        "./data/oral_liquid_meds_rebuild_20260714/final/oral_liquid_meds_final.json",
        "./css/inhaler-medicine-explorer.css",
        "./js/inhaler-medicine-explorer.js",
        "./data/inhaler_meds_20260716/taiwan_inhalers.json",
        "./css/tcm-external-patch-explorer.css",
        "./js/tcm-external-patch-explorer.js",
        "./data/tcm_external_patch_rx_20260730.json",
        "./css/tcm-external-formula-patterns.css",
        "./js/tcm-external-formula-patterns.js",
        "./data/tcm_external_formula_patterns_20260730/external_formula_pattern_analysis.json",
        "./web/taiwan_medicinal_patch_database_v2.html",
        "./health-check-calculator.html",
        "./cancer-marker-calculator.html",
        "./growth-calculator.html",
        "./menstrual-calculator.html",
        "./pregnancy-weight-calculator.html",
        "./10-yr-cv-risk.html",
        "./rx-refillable-date.html",
        "./taiwan_child_growth_data.json",
        "./taiwan_child_growth_data.js",
        "./css/health-tools.css",
        "./css/growth-calculator.css",
        "./css/menstrual-calculator.css",
        "./js/menstrual-calculator.js",
        "./css/pregnancy-weight-calculator.css",
        "./js/pregnancy-weight-calculator.js",
        "./css/rx-refillable-date.css",
        "./icon.png",
        "./404.html",
        "./cards.json",
        "./seo.json",
        "./data/recent-changes.json",
    ]
    cache_items.extend(f"./img/{img}" for img in image_files)
    cache_items.extend(f"./{page}" for page in generated_pages)
    cache_items.extend(f"./{page}" for page in retired_pages)
    cache_items.extend(['./retired-cards.html', './css/card-archive.css', './js/card-archive.js'])
    cache_items.append("./cards/404.html")
    cache_array = ",\n  ".join(json.dumps(item, ensure_ascii=False) for item in cache_items)
    # Only the basic card interface is installed; tools cache on demand.
    core_cache_items = [
        "./",
        "./index.html",
        "./public.html",
        "./all-cards.html",
        "./404.html",
        "./cards.json",
        "./seo.json",
        "./qrious.min.js",
        _page_css_ref("base.css"),
        _page_css_ref("pharmacist.css"),
        _page_css_ref("public.css", "public.html"),
        "./icon.png",
    ]
    core_cache_array = ",\n  ".join(json.dumps(item, ensure_ascii=False) for item in core_cache_items)

    sw_content = sw_path.read_text(encoding="utf-8")
    revised_images = [
        "./" + image for image, record in read_card_content().items()
        if record.get("imageUpdatedAt") and Path(image).name in image_files
    ]
    revised_array = json.dumps(revised_images, ensure_ascii=False, indent=2)
    sw_content = re.sub(
        r"const revisedImageUrls = \[.*?\];",
        f"const revisedImageUrls = {revised_array};",
        sw_content,
        flags=re.DOTALL,
    )
    sw_content = re.sub(
        r"const urlsToCache = \[.*?\];",
        f"const urlsToCache = [\n  {cache_array}\n];",
        sw_content,
        flags=re.DOTALL,
    )
    sw_content = re.sub(
        r"const coreUrlsToCache = \[.*?\];",
        f"const coreUrlsToCache = [\n  {core_cache_array}\n];",
        sw_content,
        flags=re.DOTALL,
    )
    new_version = worker_version(source_root or ROOT, ROOT, sw_content, cache_items + core_cache_items)
    sw_content = re.sub(r"const CACHE_NAME = '.*?';", f"const CACHE_NAME = '{new_version}';", sw_content)
    write_if_changed(sw_path, sw_content)


def update_sitemap(generated_pages, card_content_index):
    content_by_page = {page_for_image(image): content for image, content in card_content_index.items()}
    static_pages = [
        ("", "weekly", "1.0"),
        ("index.html", "weekly", "1.0"),
        ("public.html", "weekly", "0.8"),
        ("about.html", "monthly", "0.5"),
        ("author.html", "monthly", "0.5"),
        ("editorial-policy.html", "monthly", "0.5"),
        ("topics/acne.html", "weekly", "0.8"),
        ("topics/mom.html", "weekly", "0.8"),
        ("all-cards.html", "weekly", "0.8"),
        ("retired-cards.html", "monthly", "0.3"),
        ("calc.html", "monthly", "0.7"),
        ("health-check-calculator.html", "monthly", "0.6"),
        ("cancer-marker-calculator.html", "monthly", "0.6"),
        ("growth-calculator.html", "monthly", "0.6"),
        ("menstrual-calculator.html", "monthly", "0.6"),
        ("pregnancy-weight-calculator.html", "monthly", "0.6"),
        ("10-yr-cv-risk.html", "monthly", "0.6"),
        ("rx-refillable-date.html", "monthly", "0.6"),
    ]
    urls = []
    for path, freq, priority in static_pages:
        urls.append(
            f"""  <url>
    <loc>{esc(abs_url(path))}</loc>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
        )
    for page in generated_pages:
        modified = content_modified_date(content_by_page.get(page), abs_url(page))
        lastmod = f"    <lastmod>{modified}</lastmod>\n" if modified else ""
        urls.append(
            f"""  <url>
    <loc>{esc(abs_url(page))}</loc>
{lastmod}    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>"""
        )

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""
    write_if_changed(ROOT / "sitemap.xml", sitemap)
    write_if_changed(ROOT / "sitemap-main.xml", sitemap)


def update_robots():
    robots = f"""User-agent: *
Allow: /

Sitemap: {abs_url("sitemap-main.xml")}
"""
    write_if_changed(ROOT / "robots.txt", robots)


def generate_recent_changes(cards, root=ROOT):
    cr_path = root / "docs" / "project-management" / "change-requests.csv"
    if not cr_path.exists():
        cr_path = ROOT / "docs" / "project-management" / "change-requests.csv"
    out_path = root / "data" / "recent-changes.json"
    if not cr_path.exists():
        out_path.parent.mkdir(parents=True, exist_ok=True)
        write_if_changed(out_path, "[]\n")
        return []

    with cr_path.open(encoding="utf-8-sig", newline="") as f:
        requests = list(csv.DictReader(f))

    entries = []
    for r in requests:
        if r.get("status") != "completed":
            continue
        req_type = r.get("request_type")
        if req_type not in {"新增系列", "系列追加圖卡"}:
            continue

        related = [t.strip() for t in r.get("related_ids", "").split("|") if t.strip()]
        series_ids = [t[7:] for t in related if t.startswith("series:")]
        page_ids = [t[5:] for t in related if t.startswith("page:")]

        if not series_ids:
            continue

        matched_sid = None
        for sid in series_ids:
            if sid in cards:
                card = cards[sid]
                if card.get("category") == "public_education" and not card.get("hidden"):
                    matched_sid = sid
                    break

        if not matched_sid:
            continue

        card = cards[matched_sid]
        steps = card.get("steps") or []
        step_stems = [Path(s).stem for s in steps]

        affected_in_series = [pid for pid in page_ids if pid in step_stems]
        if not affected_in_series:
            affected_in_series = page_ids

        first_page_id = affected_in_series[0] if affected_in_series else ""
        first_step_index = 0
        if first_page_id in step_stems:
            first_step_index = step_stems.index(first_page_id)

        first_image = steps[first_step_index] if first_step_index < len(steps) else ""
        count = len(affected_in_series)

        entries.append({
            "request_id": r["request_id"],
            "completed_at": r["completed_at"],
            "request_type": req_type,
            "series_id": matched_sid,
            "series_title": card.get("title", matched_sid),
            "card_count": count,
            "first_page_id": first_page_id,
            "first_step_index": first_step_index,
            "first_image": first_image
        })

    entries.sort(key=lambda x: (x["completed_at"], x["request_id"]), reverse=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_if_changed(out_path, json.dumps(entries, ensure_ascii=False, indent=2) + "\n")
    return entries


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build static pteduimg card pages.")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--only",
        nargs="+",
        metavar="IMAGE_ID",
        help="Regenerate only the listed card image IDs without updating site indexes.",
    )
    modes.add_argument("--incremental", nargs="+", metavar="IMAGE_ID",
                       help="Build affected pages and complete indexes; reject unsafe changes.")
    args = parser.parse_args(argv)
    if args.incremental:
        import sys
        try:
            run_incremental(sys.modules[__name__], {Path(value).stem for value in args.incremental})
        except (ValueError, OSError) as error:
            parser.error(str(error))
        return
    only_image_ids = {Path(value).stem for value in args.only} if args.only else None

    cards = read_cards()
    retired = read_retired_cards(ROOT, cards)
    retired_images = {entry['image'] for entry in retired}
    card_content_index = {image: content for image, content in read_card_content().items() if image not in retired_images}
    seo_index = build_seo_index(cards, card_content_index, write_output=only_image_ids is None)
    generated_pages = generate_card_pages(cards, seo_index, card_content_index, only_image_ids)
    if only_image_ids is not None:
        generated_ids = {Path(page).stem for page in generated_pages}
        missing_ids = sorted(only_image_ids - generated_ids)
        if missing_ids:
            parser.error("unknown or unavailable image IDs: " + ", ".join(missing_ids))
        print(f"Generated {len(generated_pages)} selected static card pages.")
        return
    for homepage in ('index.html', 'public.html'):
        sync_footer(ROOT, write=True, page=homepage)
    write_retired_pages(ROOT, retired, BASE_URL)
    write_if_changed(ROOT / "all-cards.html", render_all_cards_page(cards, seo_index), preserve_index_date=True)
    text_success, text_failures = build_card_text_integration_report(card_content_index)
    update_sitemap(generated_pages, card_content_index)
    update_robots()
    generate_recent_changes(cards, ROOT)
    update_service_worker(cards, generated_pages, [entry['page'] for entry in retired])
    save_baseline(ROOT)
    print(f"Generated {len(generated_pages)} static card pages.")
    print(f"Preserved {len(retired)} retired URLs and updated retired-cards.html.")
    print(f"Integrated static text for {text_success} card pages ({text_failures} failures).")
    print("Updated all-cards.html, seo.json, sitemap.xml, sitemap-main.xml, robots.txt, and sw.js.")


if __name__ == "__main__":
    main()
