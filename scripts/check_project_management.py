"""Project-management checks and scoped machine-field merge. Stdlib only; never imports build.py.

Default: read-only verification of the complete management snapshot with full diagnostics.
--propose prints ONLY machine fields for changed/new pages (read-only), computing only
requested pages when --page is supplied. --apply-machine --page <ID> merges ONLY
MACHINE_FIELDS for specified existing rows in page-inventory.csv, asserting zero change
to all MANUAL_FIELDS and non-target rows before and after writing. Validation never
changes project sources or clinical review decisions. An explicit --report-file writes a
full diagnostic report to the requested path.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlparse

try:
    from scripts import rule_fingerprints as rules_v2
except ImportError:
    import rule_fingerprints as rules_v2

ROOT = Path(__file__).resolve().parents[1]
PM = "docs/project-management"
REMOVED_SERIES = f"{PM}/removed-series.json"
BASE = "https://liaoweihung.github.io/pteduimg/"
RULE_FILES = ["build.py", "scripts/site_footer.py", "templates/site-footer.html",
              "scripts/acne_pilot.py", "data/acne_navigation.json", "scripts/site_header.py"]
MANUAL_FIELDS = ["medical_review_status", "medical_review_evidence", "reviewer",
                 "review_date", "reviewed_content_sha256", "documented_status",
                 "audit_ids", "history_note", "seo_aeo_status", "known_issue_ids",
                 "review_required", "review_reason", "last_human_confirmed_at"]
MACHINE_FIELDS = ["page_id", "page_path", "url", "title", "primary_series_id",
                  "series_ids", "image_path", "favorite_keys", "visibility",
                  "generated_state", "added_at", "added_cr", "last_updated_at",
                  "last_updated_cr", "text_status", "reference_status", "date_status",
                  "seo_basic_status", "jsonld_status", "footer_status",
                  "source_needs_medical_review", "content_sha256", "source_sha256",
                  "rules_sha256", "rules_version", "rules_v1_sha256", "checked_at", "evidence_sources"]
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
REQUEST_TYPES = {"新增系列", "系列追加圖卡", "修改既有圖卡", "新增圖卡", "修改醫療內容", "SEO/AEO",
                 "作者或審閱者", "網站連結", "賣場連結", "疾病主題", "計算器", "資料庫", "網站功能"}
CARD_REQUEST_TYPES = {"新增系列", "系列追加圖卡", "修改既有圖卡"}
REQUEST_STATES = {"registered", "needs_confirmation", "approved", "in_progress",
                  "blocked", "completed", "cancelled"}


def read_json(root, path):
    return json.loads((root / path).read_text(encoding="utf-8-sig"))


def read_csv_with_meta(root, path):
    raw = (root / path).read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    crlf = raw.count(b"\r\n")
    lf_only = raw.count(b"\n") - crlf
    newline = "\r\n" if crlf >= lf_only else "\n"
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fieldnames = list(reader.fieldnames or [])
    rows = list(reader)
    if not fieldnames or any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"{path}: malformed CSV row")
    return rows, fieldnames, has_bom, newline


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



def audit_report_hash(root, record):
    """Explicit report-only EOL normalization; page and clinical hashes stay byte-exact."""
    path = root / record["path"]
    if not path.is_file():
        return "missing"
    data = path.read_bytes()
    mode = record.get("sha256_normalization", "bytes")
    if mode == "lf":
        data = data.replace(b"\r\n", b"\n")
    elif mode != "bytes":
        return "invalid-normalization"
    return hashlib.sha256(data).hexdigest()


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


def _machine_snapshot(root, checked_at, page_ids=None):
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
    all_live_ids = set(members) | set(retired_by_id)
    if page_ids is not None:
        requested = set(page_ids)
        unknown_ids = requested - all_live_ids
        if unknown_ids:
            raise ValueError(f"Unknown --page IDs: {sorted(unknown_ids)}")
        target_pids = sorted(requested)
    else:
        target_pids = sorted(all_live_ids)
    v2 = (root / rules_v2.MANIFEST).is_file()
    rules_hash = None if v2 else digest({p: file_hash(root, p) for p in RULE_FILES})
    rule_values = rules_v2.domains(root) if v2 else None
    registry = read_json(root, rules_v2.MANIFEST) if v2 else None
    navigation = read_json(root, "data/acne_navigation.json")
    requests_path = root / PM / "change-requests.csv"
    card_additions = defaultdict(list)
    card_updates = defaultdict(list)
    if requests_path.is_file():
        with requests_path.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("status") == "completed":
                    req_type = r.get("request_type")
                    c_at = r.get("completed_at", "")
                    rid = r.get("request_id", "")
                    if req_type in {"新增系列", "系列追加圖卡"}:
                        for target in r.get("related_ids", "").split("|"):
                            target = target.strip()
                            if target.startswith("page:"):
                                card_additions[target[5:]].append((c_at, rid))
                    if req_type in {"新增系列", "系列追加圖卡", "修改既有圖卡"}:
                        for target in r.get("related_ids", "").split("|"):
                            target = target.strip()
                            if target.startswith("page:"):
                                card_updates[target[5:]].append((c_at, rid))
    image_hashes = {}
    rows = []
    for pid in target_pids:
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
        img_hash = image_hashes.get(image)
        if img_hash is None:
            img_hash = file_hash(root, image)
            image_hashes[image] = img_hash
        if img_hash == "missing":
            errors.append(f"{pid}: image missing")
        if exists:
            html_bytes = (root / path).read_bytes()
            source = html_bytes.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
            html_hash = hashlib.sha256(html_bytes).hexdigest()
        else:
            source = ""
            html_hash = "missing"
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
                   "html": html_hash, "image": img_hash}
        if card_additions.get(pid):
            adds = sorted(card_additions[pid], key=lambda x: (x[0], x[1]))
            added_at, added_cr = adds[0]
        else:
            added_at, added_cr = "pre-system", "pre-system"

        if card_updates.get(pid):
            upds = sorted(card_updates[pid], key=lambda x: (x[0], x[1]))
            last_updated_at, last_updated_cr = upds[-1]
        else:
            last_updated_at, last_updated_cr = "pre-system", "pre-system"

        row = dict(zip(MACHINE_FIELDS, [""] * len(MACHINE_FIELDS)))
        row.update(page_id=pid, page_path=path, url=url, title=title,
                   primary_series_id=primary[0] if primary else "unknown",
                   series_ids=compact([g[0] for g in group]), image_path=image,
                   favorite_keys=compact(favs), visibility=visibility,
                   generated_state="present" if exists else "pending" if not expected_page else "missing",
                   added_at=added_at, added_cr=added_cr,
                   last_updated_at=last_updated_at, last_updated_cr=last_updated_cr,
                   text_status="machine_pass" if text_ok else "partial" if text_present else "missing",
                   reference_status="machine_pass" if refs_ok else "partial" if refs else "missing",
                   date_status="machine_pass" if dates_ok else "partial" if any(record.get(k) for k in ["updatedAt", "sourceCheckedAt"]) else "missing",
                   seo_basic_status="machine_pass" if seo_ok else "partial" if exists else "unknown",
                   jsonld_status=ld_status, footer_status="machine_pass" if footer_ok else "partial" if footers else "missing",
                   source_needs_medical_review=compact(record.get("needsMedicalReview", "unknown")),
                   content_sha256=digest({"records": recs, "image": img_hash}),
                   source_sha256=digest(payload), rules_sha256=rules_hash or "",
                   checked_at=checked_at, evidence_sources=compact(evidence))
        if old or not expected_page:
            for field in ["text_status", "reference_status", "date_status", "seo_basic_status", "jsonld_status", "footer_status"]:
                row[field] = "not_applicable"
        row["rules_version"] = "2" if v2 else "1"
        row["rules_v1_sha256"] = registry["v1_by_page"].get(pid, "unknown") if v2 else "unknown"
        if v2:
            row["rules_sha256"] = rules_v2.page_hash(row, cards, navigation, root, rule_values)
        rows.append(row)
    expected = set()
    for pid in all_live_ids:
        old = retired_by_id.get(pid)
        if old:
            expected.add(old["page"])
            continue
        group = members.get(pid, [])
        eligible = any(not (g[1].get("hidden") is True and g[1].get("publish_at")) for g in group)
        path = f"cards/{pid}.html"
        if eligible or (root / path).is_file():
            expected.add(path)
    actual = {p.relative_to(root).as_posix() for p in (root / "cards").glob("*.html") if p.name != "404.html"}
    errors += [f"orphan card HTML: {p}" for p in sorted(actual - expected)]
    return rows, errors, all_live_ids


def machine_snapshot(root, checked_at, page_ids=None):
    rows, errors, _ = _machine_snapshot(root, checked_at, page_ids=page_ids)
    return rows, errors


def _verify_machine_apply_invariants(before_rows, after_rows, fieldnames, target_ids):
    if not set(MACHINE_FIELDS).isdisjoint(MANUAL_FIELDS):
        raise RuntimeError("MACHINE_FIELDS and MANUAL_FIELDS overlap")
    if len(before_rows) != len(after_rows):
        raise RuntimeError(f"Row count changed: {len(before_rows)} -> {len(after_rows)}")
    machine_set = set(MACHINE_FIELDS)
    manual_present = [f for f in MANUAL_FIELDS if f in fieldnames]
    for idx, (before, after) in enumerate(zip(before_rows, after_rows)):
        pid = before.get("page_id")
        if after.get("page_id") != pid:
            raise RuntimeError(f"Row {idx} page_id order changed: {pid!r} -> {after.get('page_id')!r}")
        for field in manual_present:
            if after.get(field) != before.get(field):
                raise RuntimeError(
                    f"MANUAL_FIELDS violation on {pid}.{field}: {before.get(field)!r} -> {after.get(field)!r}"
                )
        if pid not in target_ids:
            if after != before:
                changed_keys = sorted(k for k in fieldnames if after.get(k) != before.get(k))
                raise RuntimeError(f"Non-target page modified: {pid} ({changed_keys})")
        else:
            for field in fieldnames:
                if after.get(field) != before.get(field) and field not in machine_set:
                    raise RuntimeError(f"Non-whitelist field modified on {pid}: {field}")


def apply_machine_fields(root, page_ids, checked_at):
    """Update ONLY MACHINE_FIELDS for specified existing rows in page-inventory.csv.

    Refuses full-table writes, unknown/missing rows, and source errors. Verifies
    zero change to every MANUAL_FIELDS cell and non-target row before and after write.
    """
    target_order = list(dict.fromkeys(page_ids or []))
    if not target_order:
        raise ValueError("--apply-machine requires at least one --page ID; full-table overwrite is forbidden")
    target_ids = set(target_order)
    live, source_errors, _ = _machine_snapshot(root, checked_at, page_ids=target_ids)
    if source_errors:
        raise ValueError(f"Refusing --apply-machine due to source errors: {source_errors}")
    inv_rel = f"{PM}/page-inventory.csv"
    before_rows, fieldnames, has_bom, newline = read_csv_with_meta(root, inv_rel)
    if "page_id" not in fieldnames:
        raise ValueError(f"{inv_rel}: missing page_id column")
    missing_manual_cols = [f for f in MANUAL_FIELDS if f not in fieldnames]
    if missing_manual_cols:
        raise ValueError(f"{inv_rel}: missing MANUAL_FIELDS columns: {missing_manual_cols}")
    counts = Counter(r.get("page_id", "") for r in before_rows)
    if "" in counts or any(c != 1 for c in counts.values()):
        raise ValueError(f"{inv_rel}: empty or duplicate page_id")
    existing_ids = set(counts)
    missing_in_inv = sorted(target_ids - existing_ids)
    if missing_in_inv:
        raise ValueError(
            "Page IDs missing from page-inventory.csv (add row with manual fields first; "
            f"--apply-machine never creates manual fields): {missing_in_inv}"
        )
    live_by_id = {r["page_id"]: r for r in live}
    machine_updatable = [f for f in MACHINE_FIELDS if f != "page_id" and f in fieldnames]
    compare_fields = [f for f in machine_updatable if f != "checked_at"]
    after_rows = [dict(row) for row in before_rows]
    applied_pages = []
    unchanged_pages = []
    updated_fields_by_page = {}
    for row in after_rows:
        pid = row["page_id"]
        if pid not in target_ids:
            continue
        target_live = live_by_id[pid]
        if not any(row.get(f) != target_live[f] for f in compare_fields):
            unchanged_pages.append(pid)
            continue
        changed_fields = []
        for field in machine_updatable:
            if row.get(field) != target_live[field]:
                row[field] = target_live[field]
                changed_fields.append(field)
        applied_pages.append(pid)
        updated_fields_by_page[pid] = changed_fields
    _verify_machine_apply_invariants(before_rows, after_rows, fieldnames, target_ids)
    if applied_pages:
        buf = io.StringIO(newline="")
        writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator=newline, extrasaction="raise")
        writer.writeheader()
        writer.writerows(after_rows)
        raw_out = (b"\xef\xbb\xbf" if has_bom else b"") + buf.getvalue().encode("utf-8")
        inv_path = root / inv_rel
        tmp_path = inv_path.with_name(f"{inv_path.name}.tmp.{os.getpid()}")
        try:
            tmp_path.write_bytes(raw_out)
            os.replace(tmp_path, inv_path)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise
        reloaded_rows, reloaded_fields, _, _ = read_csv_with_meta(root, inv_rel)
        if reloaded_fields != fieldnames:
            raise RuntimeError("Post-write header mismatch in page-inventory.csv")
        _verify_machine_apply_invariants(before_rows, reloaded_rows, fieldnames, target_ids)
        reloaded_by_id = {r["page_id"]: r for r in reloaded_rows}
        for pid in target_ids:
            remaining = [f for f in compare_fields if reloaded_by_id[pid].get(f) != live_by_id[pid][f]]
            if remaining:
                raise RuntimeError(f"Post-write verification failed for {pid}: remaining drift {remaining}")
    return {
        "applied_pages": applied_pages,
        "unchanged_pages": unchanged_pages,
        "updated_fields_by_page": updated_fields_by_page,
        "manual_fields_verified_unchanged": True,
        "written": bool(applied_pages),
    }


def load_model(root):
    return {"inventory": read_csv(root, f"{PM}/page-inventory.csv"),
            "requests": read_csv(root, f"{PM}/change-requests.csv"),
            "relations": read_csv(root, f"{PM}/content-relations.csv"),
            "topics": read_json(root, f"{PM}/content-topics.json"),
            "audits": read_json(root, f"{PM}/audit-register.json"),
            "removed_series": read_removed_series(root)}


def read_removed_series(root):
    """Series removed from cards.json; historical CRs may still reference them."""
    path = root / REMOVED_SERIES
    if not path.is_file():
        return {"schema_version": 1, "series": []}
    return json.loads(path.read_text(encoding="utf-8-sig"))


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
    removed_data = model.get("removed_series") or {"schema_version": 1, "series": []}
    removed_list = removed_data.get("series") if isinstance(removed_data, dict) else None
    demand(isinstance(removed_data, dict) and removed_data.get("schema_version") == 1,
           "removed-series: schema_version must be 1")
    demand(isinstance(removed_list, list), "removed-series: series must be a list")
    removed_ids = set()
    for item in removed_list if isinstance(removed_list, list) else []:
        if not isinstance(item, dict):
            demand(False, "removed-series: entry must be an object")
            continue
        sid = str(item.get("id") or "")
        for field in ["id", "title", "removed_at", "reason", "request_id"]:
            demand(isinstance(item.get(field), str) and bool(item[field].strip()), f"removed-series {sid or '?'}: missing {field}")
        demand(sid not in removed_ids, f"removed-series: duplicate {sid}")
        demand(valid_date(item.get("removed_at")), f"removed-series {sid}: invalid removed_at")
        demand(item.get("request_id") in request_ids, f"removed-series {sid}: unknown request {item.get('request_id')}")
        demand(sid not in cards, f"removed series still in cards.json: {sid}")
        removed_ids.add(sid)
    audit_ids = {a["audit_id"] for a in audits}
    if (root / rules_v2.MANIFEST).is_file():
        registry = read_json(root, rules_v2.MANIFEST)
        demand(registry.get("version") == 2, "rules-v2: invalid version")
        demand(set(registry["v1_by_page"]) == set(stored), "rules-v2: historical page IDs differ")
        demand(digest(registry["v1_by_page"]) == registry["v1_mapping_sha256"], "rules-v2: historical mapping changed")
        for domain, value in rules_v2.domains(root).items():
            demand(registry["domains"].get(domain) == value, f"rules-v2: domain drift: {domain}")
    for row in inv:
        pid = row["page_id"]
        legacy = not (root / rules_v2.MANIFEST).is_file() and "rules_version" not in row
        expected_fields = set(MACHINE_FIELDS + MANUAL_FIELDS) - ({"rules_version", "rules_v1_sha256"} if legacy else set())
        demand(set(row) == expected_fields, f"{pid}: inventory columns differ")
        for field in MACHINE_FIELDS:
            if field != "checked_at" and pid in current and not (legacy and field in {"rules_version", "rules_v1_sha256"}):
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
        # Removed series stay valid CR targets, but are not valid relation endpoints.
        if prefix == "series" and raw in removed_ids:
            return "removed_series"
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
        # Cancelled work never created its series/pages, so its targets need not exist.
        cancelled = r["status"] == "cancelled"
        for target in filter(None,r["related_ids"].split("|")):
            demand(cancelled or kind(target) is not None, f"{rid}: missing related target {target}")
        if r["status"] == "completed":
            demand(r["completed_at"] != "unknown" and r["validation_result"] != "unknown", f"{rid}: completion needs date and validation")
            demand(r["approval"] in {"approved", "not_required"}, f"{rid}: completed without approval")
        if r["status"] in {"approved", "in_progress"}:
            demand(r["approval"] in {"approved", "not_required"}, f"{rid}: work started without approval")
        if r["request_type"] in CARD_REQUEST_TYPES:
            related = [t.strip() for t in r["related_ids"].split("|") if t.strip()]
            has_series = any(t.startswith("series:") for t in related)
            has_page = any(t.startswith("page:") for t in related)
            demand(cancelled or has_series, f"{rid}: missing series ID in related_ids")
            demand(cancelled or has_page, f"{rid}: missing page ID in related_ids")
            if r["status"] == "completed":
                demand(r.get("completed_at") not in {"", "unknown"} and valid_date(r.get("completed_at")),
                       f"{rid}: completed card request missing completed_at")
    for a in audits:
        evidence(a["path"], a["audit_id"])
        demand(a["validity"] in {"historical_only", "partially_superseded", "current_structural", "conflict", "unknown"}, f"{a['audit_id']}: invalid validity")
        demand(valid_date(a["audit_date"], True), f"{a['audit_id']}: invalid audit_date")
        demand(a.get("sha256_normalization", "bytes") in {"bytes", "lf"}, f"{a['audit_id']}: invalid hash normalization")
        demand(audit_report_hash(root, a) == a["sha256"], f"{a['audit_id']}: report changed; append history and reassess affected claims")
        for prior in a.get("previous_versions", []):
            if prior.get("preserved_snapshot"):
                snapshot = prior["preserved_snapshot"]
                evidence(snapshot, a["audit_id"] + " historical snapshot")
                demand(file_hash(root, snapshot) == prior["sha256"],
                       f"{a['audit_id']}: historical snapshot hash mismatch")
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


GROUP_PRIORITY = {
    "medical_signoff": 0,
    "evidence_and_audit": 1,
    "manual_and_cr_integrity": 2,
    "unclassified": 3,
    "rules_fingerprint_drift": 4,
    "machine_field_drift": 5,
}
SUBSTANTIVE_GROUPS = ("medical_signoff", "evidence_and_audit", "manual_and_cr_integrity")
DRIFT_GROUPS = ("machine_field_drift", "rules_fingerprint_drift")
HIGH_PRIORITY_MEDICAL_PATTERNS = (
    re.compile(r"^[^:]+: pharmacist review is stale;"),
    re.compile(r"^[^:]+: signed review missing "),
    re.compile(r"^[^:]+: invalid medical_review_status$"),
    re.compile(r"^[^:]+: invalid review_date$"),
    re.compile(r"^[^:]+: conflict needs an issue$"),
    re.compile(r"^[^:]+: review reason missing$"),
    re.compile(r"^[^:]+: missing evidence$"),
    re.compile(r"^[^:]+: historical snapshot hash mismatch$"),
)
SUMMARY_CLASSIFIERS = (
    (re.compile(r"^([^:]+): (pharmacist review is stale;.+|signed review missing .+|invalid (?:medical_review_status|review_date|review_required|last_human_confirmed_at)|review reason missing|conflict needs an issue)$"), "medical_signoff"),
    (re.compile(r"^([^:]+): (missing evidence|evidence path missing: .+|report changed;.+|historical snapshot hash mismatch|documented complete without audit|unknown audit)$"), "evidence_and_audit"),
    (re.compile(r"^rules-v2: (domain drift: [a-z0-9_]+|historical page IDs differ)$"), "rules_fingerprint_drift"),
    (re.compile(r"^([^:]+): (invalid (?:documented_status|seo_aeo_status|checked_at|text_status|reference_status|date_status|seo_basic_status|jsonld_status|footer_status|kind|topic status|namespace|relation endpoints/type|relation status|origin|request ID|request type|request status|proposed_at|completed_at|priority|approval|needs_pharmacist|author_permission|commercial_disclosure|validity|audit_date|hash normalization)|unknown request .+|missing related target .+|completion needs date and validation|completed without approval|work started without approval|missing (?:series|page) ID in related_ids|completed card request missing completed_at|duplicate .+|empty .+|inventory columns differ|missing formal page|missing section anchor|unpublished collection/proposal must not claim a page|relation targets retired card|missing Pilot .+|Pilot HTML .+|retired page also in active steps|filename stem collision: .+|multiple card_content records|expected HTML missing|scheduled hidden HTML exists|image missing|duplicate image within series)$"), "manual_and_cr_integrity"),
    (re.compile(r"^removed-series(?: [^:]+)?: .+$"), "manual_and_cr_integrity"),
    (re.compile(r"^(inventory IDs differ:|removed series still in cards\.json:|series/card relations differ|Pilot scope differs|Pilot relation set differs|Acne hierarchy series differ|duplicate retired page IDs|orphan card HTML: )"), "manual_and_cr_integrity"),
)
RESOLVED_DETAIL_LIMIT = 10


def classify_diagnostic(item):
    """Display-layer semantic classification; never alters stable diagnostic IDs."""
    message = item["message"]
    category = item["category"]
    high_priority = any(p.search(message) for p in HIGH_PRIORITY_MEDICAL_PATTERNS)
    if category == "machine_field_drift":
        parts = item["id"].split("|")
        scope = parts[1] if len(parts) > 1 else ""
        subtype = parts[2] if len(parts) > 2 else "unknown"
        return {"group": "machine_field_drift", "subtype": subtype, "scope": scope, "high_priority": False}
    if category in {"evidence_path_missing", "report_changed"}:
        parts = item["id"].split("|")
        scope = parts[1] if len(parts) > 1 else ""
        return {"group": "evidence_and_audit", "subtype": category, "scope": scope, "high_priority": high_priority}
    for pattern, group in SUMMARY_CLASSIFIERS:
        match = pattern.match(message)
        if not match:
            continue
        if group == "rules_fingerprint_drift":
            detail = match.group(1)
            if detail.startswith("domain drift: "):
                return {"group": group, "subtype": f"domain:{detail.split(': ', 1)[1]}", "scope": "rules-v2", "high_priority": False}
            return {"group": group, "subtype": "historical_page_ids_differ", "scope": "rules-v2", "high_priority": False}
        if match.lastindex and match.lastindex >= 2:
            scope, detail = match.group(1), match.group(2)
            subtype = detail.split(":", 1)[0]
            if subtype.startswith("unknown request "):
                subtype = "unknown request"
            elif subtype.startswith("signed review missing "):
                subtype = "signed review missing"
            elif subtype.startswith("missing related target "):
                subtype = "missing related target"
            elif subtype.startswith("pharmacist review is stale"):
                subtype = "pharmacist review is stale"
            return {"group": group, "subtype": subtype, "scope": scope, "high_priority": high_priority}
        return {"group": group, "subtype": message.split(":", 1)[0], "scope": "", "high_priority": high_priority}
    return {"group": "unclassified", "subtype": "unclassified", "scope": "", "high_priority": True}


def _print_grouped_summary(items, heading_prefix):
    substantive = defaultdict(list)
    drift = defaultdict(list)
    high_priority_items = []
    for item in items:
        info = classify_diagnostic(item)
        group = info["group"]
        if group in DRIFT_GROUPS:
            drift[group].append((item, info))
        elif group in SUBSTANTIVE_GROUPS:
            substantive[group].append((item, info))
            if info["high_priority"]:
                high_priority_items.append((item, info))
    substantive_total = sum(item["count"] for entries in substantive.values() for item, _ in entries)
    drift_total = sum(item["count"] for entries in drift.values() for item, _ in entries)
    sub_heading = f"{heading_prefix}substantive issues" if heading_prefix else "Substantive issues"
    drift_heading = f"{heading_prefix}mechanical drift" if heading_prefix else "Historical mechanical drift"
    print(f"[{sub_heading}: {substantive_total}]")
    if substantive_total == 0:
        print("  (none)")
    else:
        for group in SUBSTANTIVE_GROUPS:
            entries = substantive.get(group)
            if not entries:
                continue
            total = sum(item["count"] for item, _ in entries)
            subtypes = Counter()
            scopes = sorted({info["scope"] for _, info in entries if info["scope"]})
            for item, info in entries:
                subtypes[info["subtype"]] += item["count"]
            breakdown = ", ".join(f"{k}={v}" for k, v in subtypes.most_common())
            scope_note = ""
            if scopes:
                sample = ", ".join(scopes[:5])
                more = f" +{len(scopes) - 5} more" if len(scopes) > 5 else ""
                scope_note = f" | scopes ({len(scopes)}): {sample}{more}"
            print(f"  {group} ({total}): {breakdown}{scope_note}")
        for item, info in sorted(high_priority_items, key=lambda pair: (GROUP_PRIORITY[pair[1]["group"]], pair[0]["id"])):
            print(f"  HIGH-PRIORITY [{info['group']}]: {item['id']} ({item['count']}): {item['message']}")
    print(f"[{drift_heading}: {drift_total}]")
    if drift_total == 0:
        print("  (none)")
    else:
        for group in DRIFT_GROUPS:
            entries = drift.get(group)
            if not entries:
                continue
            total = sum(item["count"] for item, _ in entries)
            subtypes = Counter()
            for item, info in entries:
                subtypes[info["subtype"]] += item["count"]
            breakdown = ", ".join(f"{k}={v}" for k, v in subtypes.most_common())
            print(f"  {group} ({total}): {breakdown}")


def print_summary(errors, warnings, diagnostics, comparison, report_file):
    categories = Counter()
    for item in diagnostics:
        categories[item["category"]] += item["count"]
    print(f"Management errors: {len(errors)}; warnings: {len(warnings)}; "
          f"status: {'FAIL' if errors else 'PASS'} (exit code unchanged).")
    if comparison is None:
        print("Baseline: none supplied; new and resolved errors cannot be determined.")
        _print_grouped_summary(diagnostics, "")
    else:
        print("Baseline difference: " + ", ".join(
            f"{key}={len(comparison[key])}" for key in ("new", "resolved", "worsened", "persistent")))
        action_new = sorted(comparison["new"], key=lambda it: (GROUP_PRIORITY[classify_diagnostic(it)["group"]], it["id"]))
        action_worsened = sorted(comparison["worsened"], key=lambda it: (GROUP_PRIORITY[classify_diagnostic(it)["group"]], it["id"]))
        print(f"[Action required (this change): new={len(action_new)}, worsened={len(action_worsened)}]")
        if not action_new and not action_worsened:
            print("  (none)")
        for item in action_new:
            group = classify_diagnostic(item)["group"]
            print(f"NEW: [{group}] {item['id']} ({item['count']}): {item['message']}")
        for item in action_worsened:
            group = classify_diagnostic(item)["group"]
            print(f"WORSENED: [{group}] {item['id']} ({item['count']}): {item['message']}")
        resolved = sorted(comparison["resolved"], key=lambda it: (GROUP_PRIORITY[classify_diagnostic(it)["group"]], it["id"]))
        if resolved:
            if len(resolved) <= RESOLVED_DETAIL_LIMIT:
                for item in resolved:
                    group = classify_diagnostic(item)["group"]
                    print(f"RESOLVED: [{group}] {item['id']} ({item['count']}): {item['message']}")
            else:
                res_groups = Counter()
                for item in resolved:
                    res_groups[classify_diagnostic(item)["group"]] += item["count"]
                summary_str = ", ".join(f"{k}={v}" for k, v in res_groups.most_common())
                print(f"RESOLVED SUMMARY ({len(resolved)} items): {summary_str}")
                for item in resolved[:5]:
                    group = classify_diagnostic(item)["group"]
                    print(f"RESOLVED: [{group}] {item['id']} ({item['count']}): {item['message']}")
                print(f"  ... ({len(resolved) - 5} more resolved items; see --report-file for full list)")
        _print_grouped_summary(comparison["persistent"], "Persistent ")
    for item in diagnostics:
        if classify_diagnostic(item)["group"] == "unclassified":
            print(f"UNCLASSIFIED: {item['id']} ({item['count']}): {item['message']}")
    print("Categories: " + (", ".join(f"{key}={value}" for key, value in sorted(categories.items())) or "none"))
    print(f"Full diagnostics: {report_file}" if report_file else
          "Full diagnostics: rerun without --summary or supply --report-file PATH.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--propose", action="store_true", help="print machine-only delta JSON to stdout; never overwrite manual columns")
    parser.add_argument("--apply-machine", action="store_true", help="write ONLY MACHINE_FIELDS for --page IDs into page-inventory.csv; requires --page and asserts zero change to MANUAL_FIELDS")
    parser.add_argument("--page", action="append", default=[], help="exact page ID for --propose or --apply-machine; repeatable")
    parser.add_argument("--summary", action="store_true", help="summarize full validation errors prioritizing new/worsened and substantive clinical/evidence issues")
    parser.add_argument("--report-file", type=Path, help="write complete JSON diagnostics to an explicitly chosen path")
    parser.add_argument("--baseline-file", type=Path, help="compare stable issue IDs with an explicitly supplied, reviewed report")
    args = parser.parse_args()
    if args.propose and args.apply_machine:
        parser.error("--propose and --apply-machine cannot be combined")
    if args.apply_machine and not args.page:
        parser.error("--apply-machine requires at least one --page ID; full-table overwrite is forbidden")
    if (args.propose or args.apply_machine) and (args.summary or args.report_file or args.baseline_file):
        parser.error("--propose/--apply-machine cannot be combined with full-validation output options")
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
        today = now.date().isoformat()
        if args.apply_machine:
            result = apply_machine_fields(root, args.page, today)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.propose:
            page_filter = set(args.page) if args.page else None
            live, source_errors, all_live_ids = _machine_snapshot(root, today, page_ids=page_filter)
            previous = {r["page_id"]: r for r in read_csv(root, f"{PM}/page-inventory.csv")}
            changed = [r for r in live if (r["page_id"] not in previous or
                                           any(r[k] != previous[r["page_id"]].get(k) for k in MACHINE_FIELDS if k != "checked_at"))]
            print(json.dumps({"machine_field_proposals": changed,
                              "removed_ids_require_manual_retirement_check": sorted(set(previous) - all_live_ids),
                              "source_errors": source_errors}, ensure_ascii=False, indent=2))
            return bool(source_errors)
        live, source_errors = machine_snapshot(root, today)
        model = load_model(root)
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
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print(f"FAIL: invalid or missing input: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
