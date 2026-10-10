"""Opt-in rendering and structural checks for the four-page acne pilot."""
from __future__ import annotations

import html
import json
import re
import sys
import posixpath
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT_IDS = {"acne_stage", "acne_topicals_02_retinoids",
             "acne_patch_when_to_use", "acne_patch_broken_skin"}
HUB = "topics/acne.html"
try:
    from scripts.site_header import RETURN_STYLES as TOP_NAV_STYLES
except ModuleNotFoundError:
    from site_header import RETURN_STYLES as TOP_NAV_STYLES



def is_acne_topic(card_id, card):
    # Rosacea is an explicitly included extension, not general acne medication.
    return "acne" in card.get("topics", []) or card_id == "rosacea_care"


def render_topic_return(page_path):
    href = posixpath.relpath(HUB, posixpath.dirname(page_path.replace('\\', '/')) or '.')
    return ('<nav class="topic-return-nav" aria-label="返回導覽">'
            '<button class="pill" type="button" onclick="returnToCardHome()">返回首頁</button>'
            f'<a class="pill" href="{html.escape(href, quote=True)}">返回青春痘完整主題頁面</a></nav>')


STYLES = """
    .card-text-content { margin-bottom:0; }
    .card-text-details { border:0; border-radius:0; background:transparent; }
    .card-text-details summary { padding:8px 0; }
    .card-text-details summary::before { content:"▶"; }
    .card-text-details[open] summary::before { transform:rotate(90deg); }
    .acne-next { margin:22px 0 0; }
    .acne-next h2 { margin:0 0 4px; font-size:.95rem; font-weight:600; }
    .acne-questions { list-style:none; margin:0; padding:0; }
    .acne-questions li + li { border-top:1px solid var(--line); }
    .acne-questions a { display:flex; align-items:center; justify-content:space-between;
      gap:14px; min-height:48px; padding:11px 0; font-size:.95rem; font-weight:400;
      color:var(--ink); text-decoration:none; line-height:1.5; overflow-wrap:anywhere; }
    .acne-questions a::after { content:"›"; flex:none; color:var(--muted); font-size:1.2rem; }
    .acne-questions a:hover { color:var(--brand); text-decoration:underline; text-underline-offset:3px; }
    .acne-next a:focus-visible, .acne-topic-link a:focus-visible {
      outline:2px solid var(--brand); outline-offset:3px; }
    .acne-topic-link { margin:18px 0 24px; font-size:.84rem; }
    .acne-topic-link a { color:var(--muted); text-underline-offset:3px;
      display:inline-flex; align-items:center; gap:6px; min-height:44px; padding:8px 0; }
    .acne-topic-link a::after { content:"→"; }
    .acne-topic-link a:hover { color:var(--brand); }
    .acne-pilot-footer { border-top:1px solid var(--line); padding-top:18px; }
"""


def load_navigation(root=ROOT):
    data = json.loads((root / "data/acne_navigation.json").read_text(encoding="utf-8"))
    pages = data["pages"]
    if data.get("version") != 1 or len(pages) != 4 or {p["page_id"] for p in pages} != PILOT_IDS:
        raise ValueError("acne_navigation: expected exactly the four approved pilot page IDs")
    cards = json.loads((root / "cards.json").read_text(encoding="utf-8"))
    active = {f"cards/{Path(s).stem}.html" for c in cards.values()
              if not (c.get("hidden") and c.get("publish_at")) for s in c.get("steps", [])}
    for page in pages:
        questions = page["next_questions"]
        if page["topic_hub"] != HUB or not 2 <= len(questions) <= 3:
            raise ValueError(f'{page["page_id"]}: expected 2–3 questions and the pilot hub')
        targets = [q["target"] for q in questions]
        if len(set(targets)) != len(targets):
            raise ValueError(f'{page["page_id"]}: duplicate question target')
        for q in questions:
            if not q["label"].strip().endswith(("？", "?")):
                raise ValueError(f'{page["page_id"]}: label must be a user question')
            if q["target"] not in active or q["target"] == f'cards/{page["page_id"]}.html':
                raise ValueError(f'{page["page_id"]}: target must be another active card: {q["target"]}')
        for target in targets + [page["topic_hub"]]:
            if not (root / target).is_file():
                raise ValueError(f'{page["page_id"]}: missing target: {target}')
    return {p["page_id"]: p for p in pages}


def render_navigation(page):
    items = "\n".join(f'          <li><a href="../{html.escape(q["target"], quote=True)}">'
                      f'{html.escape(q["label"])}</a></li>' for q in page["next_questions"])
    return f'''      <nav class="acne-next" aria-labelledby="acne-next-heading">
        <h2 id="acne-next-heading">你可能想知道</h2>
        <ul class="acne-questions">
{items}
        </ul>
      </nav>
      <p class="acne-topic-link"><a href="../{html.escape(page["topic_hub"], quote=True)}">查看青春痘完整主題</a></p>
'''


class Document(HTMLParser):
    """Small structural reader using stdlib; checks real tags, not CSS/comment text."""
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.nodes, self.stack = [], []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "start": len(self.nodes),
                "end": None, "parents": self.stack.copy(), "text": ""}
        self.nodes.append(node)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(node["start"])
        else:
            node["end"] = len(self.nodes)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.nodes[self.stack[i]]["tag"] == tag:
                for index in self.stack[i:]:
                    self.nodes[index]["end"] = len(self.nodes)
                del self.stack[i:]
                break

    def handle_data(self, text):
        for index in self.stack:
            self.nodes[index]["text"] += text

    def by_class(self, name):
        return [n for n in self.nodes if name in n["attrs"].get("class", "").split()]

    def inside(self, node, tag):
        return [n for n in self.nodes if n["tag"] == tag and node["start"] in n["parents"]]


def check_page(source, page):
    doc, errors, blocks = Document(source), [], []
    classes = ["image-stage", "page-nav", "card-text-details", "acne-next", "acne-topic-link", "acne-pilot-footer"]
    tags = ["section", "nav", "details", "nav", "p", "footer"]
    for name, tag in zip(classes, tags):
        found = doc.by_class(name)
        if len(found) != 1 or found[0]["tag"] != tag:
            errors.append(f"expected one {tag}.{name}")
        else:
            blocks.append(found[0])
    if len(blocks) != 6:
        return errors
    if any(a["end"] is None or a["end"] > b["start"] for a, b in zip(blocks, blocks[1:])):
        errors.append("block order/nesting must be image → series → text → questions → hub → footer")
    image, series, details, questions, hub, footer = blocks
    if "open" in details["attrs"] or not doc.inside(details, "summary"):
        errors.append("text details must keep its summary and be collapsed by default")
    if len(doc.inside(image, "img")) != 1 or len(doc.inside(series, "a")) != 2:
        errors.append("image or previous/next series navigation missing")
    if [n["text"].strip() for n in doc.inside(details, "summary")] != ["文字版重點"]:
        errors.append("text disclosure summary changed")
    if [n["text"].strip() for n in doc.inside(questions, "h2")] != ["你可能想知道"]:
        errors.append("next questions heading changed")
    for block in blocks:
        if "hidden" in block["attrs"] or any("hidden" in doc.nodes[i]["attrs"] for i in block["parents"]):
            errors.append("required block must not be hidden")
    if any(doc.nodes[i]["tag"] == "details" for i in questions["parents"] + hub["parents"]):
        errors.append("questions and hub must remain outside collapsed details")
    actual = [(n["text"].strip(), n["attrs"].get("href")) for n in doc.inside(questions, "a")]
    if not 2 <= len(actual) <= 3:
        errors.append("next questions must contain 2–3 links")
    expected = [(q["label"], "../" + q["target"]) for q in page["next_questions"]]
    if actual != expected:
        errors.append("question labels/targets/order differ from acne_navigation.json")
    if [(n["text"].strip(), n["attrs"].get("href")) for n in doc.inside(hub, "a")] != [("查看青春痘完整主題", "../" + page["topic_hub"])]:
        errors.append("topic hub link differs from navigation data")
    if not doc.inside(footer, "ol"):
        errors.append("original same-series footer list missing")
    return errors


def check_pilot(root=ROOT, self_test=False):
    errors = []
    try:
        pages = load_navigation(root)
        cards = json.loads((root / "cards.json").read_text(encoding="utf-8"))
        for card_id, card in cards.items():
            if not is_acne_topic(card_id, card) or (card.get("hidden") and card.get("publish_at")):
                continue
            for step in card.get("steps", []):
                path = f"cards/{Path(step).stem}.html"
                source = (root / path).read_text(encoding="utf-8")
                if source.count(render_topic_return(path)) != 1:
                    errors.append(f"{path}: expected home and acne Hub links together in top navigation")
        for page_id, page in pages.items():
            source = (root / f"cards/{page_id}.html").read_text(encoding="utf-8")
            errors.extend(f"cards/{page_id}.html: {e}" for e in check_page(source, page))
            doc = Document(source)
            series = next(c for c in cards.values() if any(Path(s).stem == page_id for s in c.get("steps", [])))
            steps = series["steps"]
            index = next(i for i, s in enumerate(steps) if Path(s).stem == page_id)
            expected = [f"../cards/{Path(steps[i]).stem}.html" for i in [index-1, (index+1) % len(steps)]]
            for block_class in ["page-nav", "image-stage"]:
                for block in doc.by_class(block_class):
                    if [n["attrs"].get("href") for n in doc.inside(block, "a")] != expected:
                        errors.append(f"{page_id}: {block_class} no longer follows series previous/next")
            for block in doc.by_class("acne-pilot-footer"):
                lists = doc.inside(block, "ol")
                if len(lists) != 1 or [n["attrs"].get("href") for n in doc.inside(lists[0], "a")] != [f"../cards/{Path(s).stem}.html" for s in steps]:
                    errors.append(f"{page_id}: footer no longer preserves complete series list")
            if self_test:
                nav = re.search(r'      <nav class="acne-next".*?</nav>\n', source, re.S).group()
                mutations = [source.replace(nav, "").replace('<details class="card-text-details"', nav + '<details class="card-text-details"'),
                             source.replace('<details class="card-text-details">', '<details class="card-text-details" open>'),
                             source.replace('class="page-nav"', 'class="missing-series"'),
                             source.replace('class="acne-topic-link"', 'class="missing-hub"'),
                             source.replace('</ul>\n      </nav>', '<li><a href="../cards/comedo.html">Extra question?</a></li></ul>\n      </nav>', 1)]
                if any(not check_page(s, page) for s in mutations):
                    errors.append(f"{page_id}: checker mutation self-test failed")
        hub = Document((root / HUB).read_text(encoding="utf-8"))
        crumbs = hub.by_class("topic-return-nav")
        if len(crumbs) != 1 or [(n["text"].strip(), n["attrs"].get("href")) for n in hub.inside(crumbs[0], "a")] != [("返回首頁", "../public.html")]:
            errors.append(f"{HUB}: top navigation must only return home, without a self-link")
        try:
            from scripts.site_header import sync_hub_header
        except ModuleNotFoundError:
            from site_header import sync_hub_header
        if not sync_hub_header(root):
            errors.append(f"{HUB}: Header differs from shared card Header source")
        headings = [n["text"] for n in hub.nodes if n["tag"] == "h2"]
        if headings != ["青春痘的正確洗臉", "認識青春痘與粉刺", "痘痘藥與使用方式", "痘痘貼與破皮照護", "其他相關問題"]:
            errors.append(f"{HUB}: expected five topic sections with face washing first")
        more = hub.by_class("more-cards")
        if len(more) != 4 or any(n["tag"] != "details" or "open" in n["attrs"] for n in more):
            errors.append(f"{HUB}: expected four collapsed card-list extensions")
        if any(hub.inside(n, "h2") or hub.inside(n, "h3") for n in more):
            errors.append(f"{HUB}: topic and subgroup headings must remain visible")
        for n in hub.nodes:
            if n["tag"] == "ul" and not any(hub.nodes[i]["tag"] in ("details", "footer") for i in n["parents"]):
                if len(hub.inside(n, "a")) > 3:
                    errors.append(f"{HUB}: initial card lists must contain at most three links")
        for n in hub.nodes:
            if n["tag"] != "a":
                continue
            if any(hub.nodes[i]["tag"] == "footer" for i in n["parents"]):
                continue  # Shared footer has intentional external site links.
            href = n["attrs"].get("href", "")
            if not href or href.startswith(("#", "http:", "https:", "javascript:")) or not (root / "topics" / href).is_file():
                errors.append(f"{HUB}: missing or non-local destination: {href}")
        try:
            from scripts.site_footer import sync_footer
        except ModuleNotFoundError:
            from site_footer import sync_footer
        if not sync_footer(root, page=HUB):
            errors.append(f"{HUB}: footer differs from shared source")
        images = [n for n in hub.nodes if n["tag"] == "img"]
        if len(images) != 5 or any(not (root / "topics" / n["attrs"].get("src", "")).is_file() for n in images):
            errors.append(f"{HUB}: expected five existing topic images")
        elif images[0]["attrs"].get("src") != "../img/acne_face_wash_01.webp":
            errors.append(f"{HUB}: face washing must use the first comic thumbnail")
    except (OSError, ValueError, KeyError, TypeError, StopIteration, AttributeError) as exc:
        errors.append(f"acne pilot: {exc}")
    return errors


if __name__ == "__main__":
    failures = check_pilot(self_test="--self-test" in sys.argv)
    for failure in failures:
        print(f"FAIL {failure}")
    if not failures:
        print("Acne pilot layout passed: 4 pages, order, collapsed details, navigation data and hub links.")
        if "--self-test" in sys.argv:
            print("Mutation self-test passed: misplaced questions, open text, missing series/hub and fourth question rejected.")
    sys.exit(bool(failures))
