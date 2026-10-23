"""Read-only project-management checks. Stdlib only; never imports build.py.

Default: verify the complete management snapshot with full diagnostics. --propose
prints ONLY machine fields for changed/new pages, for a human-reviewed merge.
Validation never changes project sources or clinical review decisions. An explicit
--report-file writes a full diagnostic report to the requested path.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parents[1]
PM = "docs/project-management"
BASE = "https://liaoweihung.github.io/pteduimg/"
RULE_FILES = ["build.py", "scripts/site_footer.py", "templates/site-footer.html",
              "scripts/acne_pilot.py", "data/acne_navigation.json", "scripts/site_header.py"]
MANUAL_FIELDS = ["medical_review_status", "medical_review_evidence", "reviewer",
                 "review_date", "reviewed_content_sha256", "documented_status",
                 "audit_ids", "history_note", "seo_aeo_status", "known_issue_ids",
                 "review_required", "review_reason", "last_human_confirmed_at"]
MACHINE_FIELDS = ["page_id", "page_path", "url", "title", "primary_series_id",
                  "series_ids", "image_path", "favorite_keys", "visibility",
                  "generated_state", "text_status", "reference_status", "date_status",
                  "seo_basic_status", "jsonld_status", "footer_status",
                  "source_needs_medical_review", "content_sha256", "source_sha256",
                  "rules_sha256", "checked_at", "evidence_sources"]
MACHINE_STATES = {"machine_pass", "missing", "partial", "invalid", "unknown", "not_applicable"}
REL_TYPES = {
    "has_subtopic": ({"topic"}, {"subtopic"}),
    "contains_series": ({"subtopic"}, {"series"}),
    "has_card": ({"series"}, {"page"}),
    "shares_card": ({"topic", "subtopic"}, {"page"}),
    "further_reading": ({"page", "topic", "subtopic"}, {"page", "topic"}),
    "differential": ({"page", "topic", "subtopic"}, {"page", "topic"}),
    "related_tool": ({"page", "topic", "subtopic"}, {"tool"}),
    "topic_return": ({"page"}, {"topic"}),
}
REQUEST_TYPES = {"新增圖卡", "修改醫療內容", "SEO/AEO", "作者或審閱者", "網站連結",
                 "賣場連結", "疾病主題", "計算器", "資料庫", "網站功能"}
REQUEST_STATES = {"registered", "needs_confirmation", "approved", "in_progress",
                  "blocked", "completed", "cancelled"}


def read_json(root, path):
    return json.loads((root / path).read_text(encoding="utf-8-sig"))


def read_csv(root, path):
    with (root / path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if any(None in row or any(v is None for v in row.values()) for row in rows):
            raise ValueError(f"{path}: malformed CSV row")
        return rows


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def file_hash(root, path):
    p = root / path
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "missing"


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(source)
        self.source = source

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def attrs(self, tag, **wanted):
        return [a for t, a in self.tags if t == tag and all(a.get(k) == v for k, v in wanted.items())]

    def has_class(self, tag, cls):
        return any(cls in a.get("class", "").split() for a in self.attrs(tag))


def machine_snapshot(root, checked_at):
    cards = read_json(root, "cards.json")
    manual = read_json(root, "cards.manual.json")
    retired = read_json(root, "cards.retired.json")
    records = read_json(root, "data/card_content.json")
    content = defaultdict(list)
    members = defaultdict(list)
    errors = []
    for record in records:
        content[record["image"]].append(record)
    for sid, card in cards.items():
        if len(card.get("steps", [])) != len(set(card.get("steps", []))):
            errors.append(f"{sid}: duplicate image within series")
        for index, image in enumerate(card.get("steps", [])):
            members[Path(image).stem].append((sid, card, index, image))
    retired_by_id = {Path(x["page"]).stem: x for x in retired}
    if len(retired_by_id) != len(retired):
        errors.append("duplicate retired page IDs")
    rules_hash = digest({p: file_hash(root, p) for p in RULE_FILES})
    rows = []
    for pid in sorted(set(members) | set(retired_by_id)):
        group = members.get(pid, [])
        old = retired_by_id.get(pid)
        if old and group:
            errors.append(f"{pid}: retired page also in active steps")
        images = {m[3] for m in group}
        if len(images) > 1:
            errors.append(f"{pid}: filename stem collision: {sorted(images)}")
        image = old["image"] if old else group[0][3]
        path = old["page"] if old else f"cards/{pid}.html"
        url = BASE + quote(path)
        recs = content.get(image, [])
        high = [r for r in recs if r.get("matchConfidence") == "high"]
        if len(recs) > 1:
            errors.append(f"{pid}: multiple card_content records")
        record = high[-1] if high else {}
        eligible = [g for g in group if not (g[1].get("hidden") is True and g[1].get("publish_at"))]
        primary = (eligible or group)[0] if group else None
        visibility = ("retired" if old else "current" if any(not g[1].get("hidden") for g in group)
                      else "hidden")
        expected_page = bool(old or eligible)
        exists = (root / path).is_file()
        if expected_page and not exists:
            errors.append(f"{pid}: expected HTML missing")
        if not expected_page and exists:
            errors.append(f"{pid}: scheduled hidden HTML exists")
        if not (root / image).is_file():
            errors.append(f"{pid}: image missing")
        source = (root / path).read_text(encoding="utf-8-sig") if exists else ""
        doc = Page(source)
        decoded = unescape(source)
        h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", source, re.S | re.I)
        title = unescape(re.sub(r"<[^>]+>", "", h1[1])).strip() if h1 else (
            old["title"] if old else record.get("title") or primary[1]["title"])
        text_present = doc.has_class("article", "card-text-content")
        text_parts = [record.get("summary", "")] + [s.get("text", "") for s in record.get("sections", [])]
        article = re.search(r'<article\b[^>]*class="card-text-content"[^>]*>(.*?)</article>', decoded, re.S)
        visible_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", article[1] if article else ""))
        text_ok = (text_present and bool(record.get("summary")) and bool(record.get("sections"))
                   and all(t and re.sub(r"\s+", " ", t).strip() in visible_text for t in text_parts))
        refs = record.get("references", [])
        hrefs = {a.get("href") for a in doc.attrs("a")}
        refs_ok = refs and all(r.get("title") and urlparse(r.get("url", "")).scheme in {"https", "http"}
                               and r["url"] in hrefs for r in refs)
        dates_ok = (bool(record.get("updatedAt")) and bool(record.get("sourceCheckedAt"))
                    and f"內容更新：{record['updatedAt']}" in visible_text
                    and f"資料查核：{record['sourceCheckedAt']}" in visible_text)
        canon = doc.attrs("link", rel="canonical")
        seo_ok = (bool(re.search(r"<title>[^<]+</title>", source)) and len(doc.attrs("h1")) == 1
                  and any(a.get("content") for a in doc.attrs("meta", name="description"))
                  and any(a.get("href") == url for a in canon)
                  and all(any(a.get("content") for a in doc.attrs("meta", property=k))
                          for k in ["og:title", "og:description", "og:image", "og:url"]))
        blocks = re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', source, re.S | re.I)
        ld_status = "missing"
        if blocks:
            try:
                parsed = [json.loads(b) for b in blocks]
                ld_status = "machine_pass" if all(isinstance(x, (dict, list)) for x in parsed) else "invalid"
            except ValueError:
                ld_status = "invalid"
        footers = [a for a in doc.attrs("footer") if "site-footer" in a.get("class", "").split()]
        footer_ok = len(footers) == 1 and all(any(h and h.endswith(p) for h in hrefs)
                                               for p in ["about.html", "author.html", "editorial-policy.html"])
        favs = {}
        for sid, c, i, _ in group:
            keys = c.get("favorite_keys") or []
            favs[sid] = keys[i] if i < len(keys) and keys[i] else f"{sid}-{i}"
        evidence = ["cards.retired.json" if old else "cards.json", "cards.manual.json", path,
                    image, "data/card_content.json", "scripts/check_project_management.py"]
        payload = {"memberships": [{"id": s, "index": i, "data": c, "manual": manual.get(s)}
                                   for s, c, i, _ in group], "retired": old, "records": recs,
                   "html": file_hash(root, path), "image": file_hash(root, image)}
        row = dict(zip(MACHINE_FIELDS, [""] * len(MACHINE_FIELDS)))
        row.update(page_id=pid, page_path=path, url=url, title=title,
                   primary_series_id=primary[0] if primary else "unknown",
                   series_ids=compact([g[0] for g in group]), image_path=image,
                   favorite_keys=compact(favs), visibility=visibility,
                   generated_state="present" if exists else "pending" if not expected_page else "missing",
                   text_status="machine_pass" if text_ok else "partial" if text_present else "missing",
                   reference_status="machine_pass" if refs_ok else "partial" if refs else "missing",
                   date_status="machine_pass" if dates_ok else "partial" if any(record.get(k) for k in ["updatedAt", "sourceCheckedAt"]) else "missing",
                   seo_basic_status="machine_pass" if seo_ok else "partial" if exists else "unknown",
                   jsonld_status=ld_status, footer_status="machine_pass" if footer_ok else "partial" if footers else "missing",
                   source_needs_medical_review=compact(record.get("needsMedicalReview", "unknown")),
                   content_sha256=digest({"records": recs, "image": file_hash(root, image)}),
                   source_sha256=digest(payload), rules_sha256=rules_hash,
                   checked_at=checked_at, evidence_sources=compact(evidence))
        if old or not expected_page:
            for field in ["text_status", "reference_status", "date_status", "seo_basic_status", "jsonld_status", "footer_status"]:
                row[field] = "not_applicable"
        rows.append(row)
    expected = {r["page_path"] for r in rows if r["generated_state"] != "pending"}
    actual = {p.relative_to(root).as_posix() for p in (root / "cards").glob("*.html") if p.name != "404.html"}
    errors += [f"orphan card HTML: {p}" for p in sorted(actual - expected)]
    return rows, errors


def load_model(root):
    return {"inventory": read_csv(root, f"{PM}/page-inventory.csv"),
            "requests": read_csv(root, f"{PM}/change-requests.csv"),
            "relations": read_csv(root, f"{PM}/content-relations.csv"),
            "topics": read_json(root, f"{PM}/content-topics.json"),
            "audits": read_json(root, f"{PM}/audit-register.json")}


def validate(root, model, live):
    errors, warnings = [], []
    inv, requests, relations = (model[k] for k in ["inventory", "requests", "relations"])
    topics, audits = model["topics"], model["audits"]["reports"]
    cards = read_json(root, "cards.json")

    def demand(ok, message):
        if not ok:
            errors.append(message)

    def valid_date(value, unknown=False):
        if value == "unknown":
            return unknown
        try:
            return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)) and date.fromisoformat(value).isoformat() == value
        except (ValueError, TypeError):
            return False

    def unique(rows, key, label):
        counts = Counter(r.get(key, "") for r in rows)
        demand("" not in counts, f"{label}: empty {key}")
        for value, count in counts.items():
            demand(count == 1, f"{label}: duplicate {value}")

    def evidence(value, context, allow_unknown=False):
        if value == "unknown" and allow_unknown:
            return
        demand(isinstance(value, str) and bool(value.strip()), f"{context}: missing evidence")
        if not isinstance(value, str) or not value.strip():
            return
        for item in value.split("|"):
            path = item.split("#")[0]
            if path.startswith("https://"):
                continue
            demand((root / path).is_file(), f"{context}: evidence path missing: {path}")

    for rows, key, label in [(inv, "page_id", "inventory"), (requests, "request_id", "requests"),
                             (relations, "relation_id", "relations"), (audits, "audit_id", "audits"),
                             (topics["nodes"], "id", "topic nodes")]:
        unique(rows, key, label)
    current = {r["page_id"]: r for r in live}
    stored = {r["page_id"]: r for r in inv}
    demand(set(current) == set(stored), f"inventory IDs differ: missing={sorted(set(current)-set(stored))}; extra={sorted(set(stored)-set(current))}")
    request_ids = {r["request_id"] for r in requests}
    audit_ids = {a["audit_id"] for a in audits}
    for row in inv:
        pid = row["page_id"]
        demand(set(row) == set(MACHINE_FIELDS + MANUAL_FIELDS), f"{pid}: inventory columns differ")
        for field in MACHINE_FIELDS:
            if field != "checked_at" and pid in current:
                demand(row.get(field) == current[pid][field], f"{pid}: machine field drift: {field}")
        demand(valid_date(row.get("checked_at", "")), f"{pid}: invalid checked_at")
        demand(valid_date(row.get("last_human_confirmed_at", ""), True), f"{pid}: invalid last_human_confirmed_at")
        for field in ["text_status", "reference_status", "date_status", "seo_basic_status", "jsonld_status", "footer_status"]:
            demand(row.get(field) in MACHINE_STATES, f"{pid}: invalid {field}")
        demand(row.get("medical_review_status") in {"unknown", "pending_pharmacist", "pharmacist_reviewed", "conflict"}, f"{pid}: invalid medical_review_status")
        demand(row.get("documented_status") in {"unknown", "documented_complete", "historical_only", "conflict"}, f"{pid}: invalid documented_status")
        demand(row.get("seo_aeo_status") in {"unknown", "documented_complete", "pending", "conflict"}, f"{pid}: invalid seo_aeo_status")
        demand(row.get("review_required") in {"yes", "no", "unknown"}, f"{pid}: invalid review_required")
        if row.get("medical_review_status") == "pharmacist_reviewed":
            for f in ["reviewer", "review_date", "reviewed_content_sha256"]:
                demand(row.get(f) not in {"", "unknown"}, f"{pid}: signed review missing {f}")
            demand(valid_date(row.get("review_date", "")), f"{pid}: invalid review_date")
            evidence(row.get("medical_review_evidence", ""), pid)
            demand(row.get("reviewed_content_sha256") == row.get("content_sha256"), f"{pid}: pharmacist review is stale; preserve historical signoff and request delta review")
        elif row.get("medical_review_evidence") not in {"", "unknown"}:
            evidence(row["medical_review_evidence"], pid)
        if row.get("medical_review_status") == "conflict" or row.get("documented_status") == "conflict":
            demand(row.get("known_issue_ids") not in {"", "unknown"}, f"{pid}: conflict needs an issue")
        if row.get("review_required") == "yes":
            demand(row.get("review_reason") not in {"", "unknown"}, f"{pid}: review reason missing")
        for rid in filter(None, row.get("known_issue_ids", "").split("|")):
            demand(rid in request_ids, f"{pid}: unknown request {rid}")
        aids = list(filter(None, row.get("audit_ids", "").split("|")))
        demand(set(aids) <= audit_ids, f"{pid}: unknown audit")
        if row.get("documented_status") == "documented_complete":
            demand(bool(aids), f"{pid}: documented complete without audit")
        for ev in json.loads(row["evidence_sources"]):
            # Pending HTML legitimately does not exist yet.
            if ev == row["page_path"] and row["generated_state"] == "pending":
                continue
            evidence(ev, pid)

    nodes = {n["id"]: n for n in topics["nodes"]}
    def kind(node_id):
        prefix, sep, raw = node_id.partition(":")
        if prefix == "page" and raw in stored:
            return "page"
        if prefix == "series" and raw in cards:
            return "series"
        if node_id in nodes:
            return nodes[node_id]["kind"]
        return None

    for n in nodes.values():
        demand(n["kind"] in {"topic", "subtopic", "tool"}, f"{n['id']}: invalid kind")
        demand(n["status"] in {"formal_page", "planned", "collection_only", "existing_tool"}, f"{n['id']}: invalid topic status")
        demand(n["id"].startswith(n["kind"] + ":"), f"{n['id']}: invalid namespace")
        if n["status"] in {"formal_page", "existing_tool"}:
            demand(bool(n.get("page_path")) and (root / n["page_path"].split("#")[0]).is_file(), f"{n['id']}: missing formal page")
            path, sep, anchor = n.get("page_path", "").partition("#")
            if sep and (root / path).is_file():
                demand(any(a.get("id") == anchor for _,a in Page((root/path).read_text(encoding="utf-8-sig")).tags), f"{n['id']}: missing section anchor")
        else:
            demand(not n.get("page_path"), f"{n['id']}: unpublished collection/proposal must not claim a page")
        evidence(n.get("evidence", ""), n["id"])
    edges = set()
    for r in relations:
        edge = (r["source_id"], r["relation_type"], r["target_id"])
        demand(edge not in edges, f"{r['relation_id']}: duplicate relation")
        edges.add(edge)
        types = REL_TYPES.get(r["relation_type"])
        demand(bool(types) and kind(r["source_id"]) in types[0] and kind(r["target_id"]) in types[1], f"{r['relation_id']}: invalid relation endpoints/type")
        demand(r["status"] in {"source_observed", "documented_proposal", "management_mapping"}, f"{r['relation_id']}: invalid relation status")
        demand(r["origin"] in {"management", "series_membership", "pilot_navigation", "hub_link"}, f"{r['relation_id']}: invalid origin")
        evidence(r["evidence"], r["relation_id"])
        if r["target_id"].startswith("page:") and r["target_id"][5:] in stored:
            demand(stored[r["target_id"][5:]]["visibility"] != "retired", f"{r['relation_id']}: relation targets retired card")
    expected_members = {("series:"+s, "has_card", "page:"+Path(i).stem) for s,c in cards.items() for i in c.get("steps", [])}
    demand({e for e in edges if e[1] == "has_card"} == expected_members, "series/card relations differ from cards.json")
    navigation = read_json(root, "data/acne_navigation.json")["pages"]
    pilot_edges = set()
    for page in navigation:
        source = "page:"+page["page_id"]
        pilot_path = root / f"cards/{page['page_id']}.html"
        pilot_hrefs = {a.get('href') for a in Page(pilot_path.read_text(encoding='utf-8-sig')).attrs('a')} if pilot_path.is_file() else set()
        for q in page["next_questions"]:
            target = "page:"+Path(q["target"]).stem
            pilot_edges.add((source,"further_reading",target))
            demand((source,"further_reading",target) in edges, f"{source}: missing Pilot question relation")
            demand('../'+q['target'] in pilot_hrefs, f"{source}: Pilot HTML link missing: {q['target']}")
        pilot_edges.add((source,"topic_return","topic:acne"))
        demand((source,"topic_return","topic:acne") in edges, f"{source}: missing Pilot return")
        demand('../'+page['topic_hub'] in pilot_hrefs, f"{source}: Pilot HTML topic return missing")
    pilot_ids = {"page:"+p["page_id"] for p in navigation}
    observed = {r["source_id"] for r in relations if r["origin"] == "pilot_navigation"}
    demand(observed == pilot_ids, "Pilot scope differs from authoritative navigation")
    demand({(r['source_id'],r['relation_type'],r['target_id']) for r in relations if r['origin']=='pilot_navigation'} == pilot_edges, "Pilot relation set differs from authoritative navigation")
    acne_subtopics = {target for source,typ,target in edges if source == 'topic:acne' and typ == 'has_subtopic'}
    acne_series = {target[7:] for source,typ,target in edges if source in acne_subtopics and typ == 'contains_series'}
    authoritative_acne = {sid for sid,c in cards.items() if 'acne' in c.get('topics',[]) or sid == 'rosacea_care'}
    demand(acne_series == authoritative_acne, "Acne hierarchy series differ from existing topic scope")

    for r in requests:
        rid = r["request_id"]
        demand(bool(re.fullmatch(r"CR-\d{4}-\d{3,}", rid)), f"{rid}: invalid request ID")
        demand(r["request_type"] in REQUEST_TYPES, f"{rid}: invalid request type")
        demand(r["status"] in REQUEST_STATES, f"{rid}: invalid request status")
        demand(valid_date(r["proposed_at"]), f"{rid}: invalid proposed_at")
        demand(valid_date(r["completed_at"], True), f"{rid}: invalid completed_at")
        demand(r["priority"] in {"P0", "P1", "P2", "P3"}, f"{rid}: invalid priority")
        demand(r["approval"] in {"not_approved", "approved", "not_required"}, f"{rid}: invalid approval")
        for f in ["needs_pharmacist", "author_permission", "commercial_disclosure"]:
            demand(r[f] in {"yes", "no", "unknown"}, f"{rid}: invalid {f}")
        evidence(r["evidence"], rid)
        for target in filter(None,r["related_ids"].split("|")):
            demand(kind(target) is not None, f"{rid}: missing related target {target}")
        if r["status"] == "completed":
            demand(r["completed_at"] != "unknown" and r["validation_result"] != "unknown", f"{rid}: completion needs date and validation")
            demand(r["approval"] in {"approved", "not_required"}, f"{rid}: completed without approval")
        if r["status"] in {"approved", "in_progress"}:
            demand(r["approval"] in {"approved", "not_required"}, f"{rid}: work started without approval")
    for a in audits:
        evidence(a["path"], a["audit_id"])
        demand(a["validity"] in {"historical_only", "partially_superseded", "current_structural", "conflict", "unknown"}, f"{a['audit_id']}: invalid validity")
        demand(valid_date(a["audit_date"], True), f"{a['audit_id']}: invalid audit_date")
        demand(file_hash(root, a["path"]) == a["sha256"], f"{a['audit_id']}: report changed; append history and reassess affected claims")
        if a["audit_date"] == "unknown":
            warnings.append(f"{a['audit_id']}: audit date unknown (not inferred from filesystem date)")
    if any(r["medical_review_status"] != "pharmacist_reviewed" for r in inv if r["visibility"] != "retired"):
        warnings.append("Clinical signoff is incomplete/unknown; structural checks do not certify medical accuracy.")
    return errors, warnings


DIAGNOSTIC_SCHEMA = 1
DIAGNOSTIC_PATTERNS = (
    (re.compile(r"^([^:]+): machine field drift: ([a-z0-9_]+)$"), "machine_field_drift"),
    (re.compile(r"^([^:]+): evidence path missing: (.+)$"), "evidence_path_missing"),
    (re.compile(r"^([^:]+): report changed; append history and reassess affected claims$"), "report_changed"),
)


def diagnostic_identity(message):
    """Use issue scope and type, not the changing number of total errors."""
    for pattern, category in DIAGNOSTIC_PATTERNS:
        match = pattern.fullmatch(message)
        if match:
            return category, "|".join((category, *match.groups()))
    # An unfamiliar error must remain visible, even if it was in the baseline.
    return "unclassified", "unclassified|" + hashlib.sha256(message.encode("utf-8")).hexdigest()


def diagnostics_from_errors(errors):
    grouped = {}
    for message in errors:
        category, identity = diagnostic_identity(message)
        item = grouped.setdefault(identity, {"id": identity, "category": category,
                                             "message": message, "count": 0})
        if item["message"] != message:
            # Never conflate changed wording under the same stable issue ID.
            identity += "|" + hashlib.sha256(message.encode("utf-8")).hexdigest()
            item = grouped.setdefault(identity, {"id": identity, "category": category,
                                                 "message": message, "count": 0})
        item["count"] += 1
    return sorted(grouped.values(), key=lambda item: item["id"])


def load_baseline(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: invalid management diagnostic baseline")
    if data.get("validator") != "check_project_management" or data.get("schema_version") != DIAGNOSTIC_SCHEMA:
        raise ValueError(f"{path}: incompatible management diagnostic baseline")
    items = data.get("diagnostics")
    raw_errors = data.get("errors")
    if (not isinstance(raw_errors, list) or
        any(not isinstance(message, str) for message in raw_errors) or
        data.get("error_count") != len(raw_errors) or
        items != diagnostics_from_errors(raw_errors)):
        raise ValueError(f"{path}: inconsistent diagnostic baseline")
    return items


def compare_diagnostics(current, baseline):
    now = {item["id"]: item for item in current}
    old = {item["id"]: item for item in baseline}
    added = [now[key] for key in sorted(now.keys() - old.keys())]
    resolved = [old[key] for key in sorted(old.keys() - now.keys())]
    worsened = [now[key] for key in sorted(now.keys() & old.keys())
                if now[key]["count"] > old[key]["count"] or
                now[key]["message"] != old[key]["message"] or
                now[key]["category"] != old[key]["category"]]
    persistent = [now[key] for key in sorted(now.keys() & old.keys())]
    return {"new": added, "resolved": resolved, "worsened": worsened,
            "persistent": persistent}


def print_summary(errors, warnings, diagnostics, comparison, report_file):
    categories = Counter()
    for item in diagnostics:
        categories[item["category"]] += item["count"]
    print(f"Management errors: {len(errors)}; warnings: {len(warnings)}; "
          f"status: {'FAIL' if errors else 'PASS'} (exit code unchanged).")
    print("Categories: " + (", ".join(f"{key}={value}" for key, value in sorted(categories.items())) or "none"))
    if comparison is None:
        print("Baseline: none supplied; new and resolved errors cannot be determined.")
    else:
        print("Baseline difference: " + ", ".join(
            f"{key}={len(comparison[key])}" for key in ("new", "resolved", "worsened", "persistent")))
        for label in ("new", "worsened", "resolved"):
            for item in comparison[label]:
                print(f"{label.upper()}: {item['id']} ({item['count']}): {item['message']}")
    for item in diagnostics:
        if item["category"] == "unclassified":
            print(f"UNCLASSIFIED: {item['id']} ({item['count']}): {item['message']}")
    print(f"Full diagnostics: {report_file}" if report_file else
          "Full diagnostics: rerun without --summary or supply --report-file PATH.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--propose", action="store_true", help="print machine-only delta JSON to stdout; never overwrite manual columns")
    parser.add_argument("--page", action="append", default=[], help="filter proposal by exact page ID; repeatable")
    parser.add_argument("--summary", action="store_true", help="summarize full validation errors without listing known errors")
    parser.add_argument("--report-file", type=Path, help="write complete JSON diagnostics to an explicitly chosen path")
    parser.add_argument("--baseline-file", type=Path, help="compare stable issue IDs with an explicitly supplied, reviewed report")
    args = parser.parse_args()
    if args.propose and (args.summary or args.report_file or args.baseline_file):
        parser.error("--propose cannot be combined with full-validation output options")
    if args.report_file and args.baseline_file and args.report_file.resolve() == args.baseline_file.resolve():
        parser.error("--report-file must not overwrite --baseline-file")
    root = args.root.resolve()
    from datetime import datetime
    from zoneinfo import ZoneInfo
    # Windows without tzdata: Asia/Taipei has fixed UTC+08 in this project period.
    try:
        now = datetime.now(ZoneInfo("Asia/Taipei"))
    except Exception:
        from datetime import timezone, timedelta
        now = datetime.now(timezone(timedelta(hours=8)))
    try:
        live, source_errors = machine_snapshot(root, now.date().isoformat())
        model = load_model(root)
        if args.propose:
            previous = {r["page_id"]: r for r in model["inventory"]}
            unknown_ids = set(args.page) - {r['page_id'] for r in live}
            if unknown_ids:
                raise ValueError(f"Unknown --page IDs: {sorted(unknown_ids)}")
            changed = [r for r in live if (not args.page or r["page_id"] in args.page)
                       and (r["page_id"] not in previous or any(r[k] != previous[r["page_id"]].get(k) for k in MACHINE_FIELDS if k != "checked_at"))]
            print(json.dumps({"machine_field_proposals": changed,
                              "removed_ids_require_manual_retirement_check": sorted(set(previous)-{r['page_id'] for r in live}),
                              "source_errors": source_errors}, ensure_ascii=False, indent=2))
            return bool(source_errors)
        errors, warnings = validate(root, model, live)
        errors = source_errors + errors
        diagnostics = diagnostics_from_errors(errors)
        baseline = load_baseline(args.baseline_file) if args.baseline_file else None
        comparison = compare_diagnostics(diagnostics, baseline) if baseline is not None else None
        counts = Counter(r["visibility"] for r in live)
        if args.report_file:
            report = {"validator": "check_project_management", "schema_version": DIAGNOSTIC_SCHEMA,
                      "checked_at": now.isoformat(), "inventory_count": len(live),
                      "visibility": dict(counts), "relations_count": len(model["relations"]),
                      "reports_count": len(model["audits"]["reports"]),
                      "requests_count": len(model["requests"]), "error_count": len(errors),
                      "errors": errors, "warnings": warnings, "diagnostics": diagnostics,
                      "baseline_difference": comparison}
            args.report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.summary:
            print_summary(errors, warnings, diagnostics, comparison, args.report_file)
        else:
            print(f"Inventory: {len(live)} unique pages; visibility={dict(counts)}")
            print(f"Relations: {len(model['relations'])}; reports: {len(model['audits']['reports'])}; requests: {len(model['requests'])}")
            for warning in warnings:
                print("NOTE:", warning)
            for error in errors:
                print("ERROR:", error)
            suffix = (f"Diagnostic report written: {args.report_file}." if args.report_file else
                      "Read-only; no files written.")
            print(f"{'FAIL' if errors else 'PASS'}: {len(errors)} management validation errors. {suffix}")
        return bool(errors)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL: invalid or missing input: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
