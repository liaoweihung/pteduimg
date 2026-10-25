"""Read-only Git-based website change tracker for pteduimg."""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PM = "docs/project-management"
REQUESTS = f"{PM}/change-requests.csv"
TRACKING_START = "183cc0d1b03c00ae67aba102908e3a1877e05bec"

MANAGEMENT_PREFIXES = (f"{PM}/", "skills/pteduimg-card-manager/")
MANAGEMENT_FILES = {
    "AGENTS.md", "scripts/check_project_management.py", "scripts/test_project_management.py",
    "scripts/project_change_tracker.py", "scripts/test_project_change_tracker.py",
    ".github/workflows/project-management-check.yml",
}
SITE_PREFIXES = ("cards/", "img/", "css/", "js/", "assets/", "templates/", "topics/", "web/", "calc/", "dashboard/")
SITE_FILES = {
    "404.html", "all-cards.html", "build.py", "cards.json", "cards.manual.json",
    "cards.retired.json", "index.html", "public.html", "manifest.json", "robots.txt",
    "seo.json", "sitemap.xml", "sitemap-main.xml", "retired-cards.html", "sw.js",
    "data/card_content.json", "data/acne_navigation.json",
}
GENERATED_ONLY_FILES = {"sw.js", "dashboard/index.html", "dashboard/status.json"}


class GitError(RuntimeError):
    pass


def git(root: Path, *args: str, check: bool = True) -> str:
    env = os.environ.copy()
    env.setdefault("GIT_OPTIONAL_LOCKS", "0")
    proc = subprocess.run(
        ["git", "-c", "core.quotepath=false", "-c", "i18n.logOutputEncoding=utf-8", *args],
        cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )
    if check and proc.returncode:
        raise GitError(proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


def normalize(path: str) -> str:
    path = path.strip().replace("\\", "/")
    # Remove relative-directory prefixes, not dots belonging to directory names.
    while path.startswith("./"):
        path = path[2:]
    return path


def is_management_path(path: str) -> bool:
    path = normalize(path)
    return path in MANAGEMENT_FILES or any(path.startswith(prefix) for prefix in MANAGEMENT_PREFIXES)


def is_site_path(path: str, tracked: bool = True) -> bool:
    path = normalize(path)
    if not path or is_management_path(path):
        return False
    if path.startswith(("docs/", "output/", "tests/", ".codex", ".agents/")):
        return False
    if path in SITE_FILES or any(path.startswith(prefix) for prefix in SITE_PREFIXES):
        return True
    if path.startswith("data/") and tracked and Path(path).suffix.lower() in {".json", ".csv"}:
        return True
    if path.startswith(".github/workflows/"):
        return True
    if path.startswith("scripts/"):
        name = Path(path).name
        return name.startswith(("build_", "site_", "publish_", "card_archive")) and name.endswith(".py")
    return "/" not in path and path.lower().endswith(".html")


def classify_areas(files: set[str]) -> list[str]:
    areas: set[str] = set()
    for path in files:
        if path.startswith(("cards/", "img/")) or path in {
            "cards.json", "cards.manual.json", "cards.retired.json", "data/card_content.json"
        }:
            areas.add("圖卡與內容")
        if path in {"index.html", "public.html", "all-cards.html"}:
            areas.add("入口與導覽")
        if path.startswith(("css/", "assets/")) or path == "manifest.json":
            areas.add("外觀與品牌")
        if path in {"seo.json", "sitemap.xml", "sitemap-main.xml", "robots.txt"}:
            areas.add("SEO／索引")
        if path in {"sw.js", "manifest.json"}:
            areas.add("PWA／快取")
        if path.startswith("topics/") or path == "data/acne_navigation.json":
            areas.add("疾病主題")
        if path.startswith(("web/", "calc/", "dashboard/")) or (
            path.startswith("data/") and path not in {"data/card_content.json", "data/acne_navigation.json"}
        ):
            areas.add("工具／資料庫")
        if path.startswith(".github/workflows/"):
            areas.add("自動化")
        if path == "build.py" or path.startswith(("templates/", "scripts/")):
            areas.add("網站產生規則")
    return sorted(areas) or ["其他網站檔案"]


def json_at(root: Path, ref: str, path: str) -> Any:
    raw = git(root, "show", f"{ref}:{path}", check=False)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def json_worktree(root: Path, path: str) -> Any:
    target = root / path
    if not target.is_file():
        return None
    try:
        return json.loads(target.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None


def request_rows_from_text(raw: str) -> dict[str, dict[str, str]]:
    if not raw:
        return {}
    rows = csv.DictReader(io.StringIO(raw.lstrip("\ufeff")))
    return {row["request_id"]: row for row in rows if row.get("request_id")}


def requests_at(root: Path, ref: str) -> dict[str, dict[str, str]]:
    return request_rows_from_text(git(root, "show", f"{ref}:{REQUESTS}", check=False))


def requests_worktree(root: Path) -> dict[str, dict[str, str]]:
    path = root / REQUESTS
    return request_rows_from_text(path.read_text(encoding="utf-8-sig")) if path.is_file() else {}


def changed_request_ids(root: Path, old_ref: str, new_ref: str | None = None) -> list[str]:
    old = requests_at(root, old_ref)
    new = requests_at(root, new_ref) if new_ref else requests_worktree(root)
    return sorted(rid for rid, row in new.items() if old.get(rid) != row)


def commit_request_map(root: Path, requests: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = defaultdict(list)
    for rid, row in requests.items():
        for token in row.get("git_commit", "").replace(",", "|").split("|"):
            token = token.strip()
            if len(token) >= 7 and token not in {"unknown", "same_commit"}:
                resolved = git(root, "rev-parse", "--verify", f"{token}^{{commit}}", check=False).strip()
                if resolved:
                    mapping[resolved].append(rid)
    return mapping


def request_links_commit(root: Path, row: dict[str, str], sha: str) -> bool:
    for token in row.get("git_commit", "").replace(",", "|").split("|"):
        token = token.strip()
        if token == "same_commit":
            return True
        if len(token) >= 7 and token != "unknown":
            resolved = git(root, "rev-parse", "--verify", f"{token}^{{commit}}", check=False).strip()
            if resolved == sha:
                return True
    return False


def changed_files_for_commit(root: Path, sha: str) -> set[str]:
    parents = git(root, "rev-list", "--parents", "-n", "1", sha).split()
    if len(parents) > 2:
        # A merge only adds paths that differ from every parent. Paths copied
        # from another parent are already accounted for by that commit.
        raw = git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "-c", sha)
    else:
        raw = git(root, "show", "--first-parent", "--pretty=format:", "--name-only", sha)
    return {normalize(line) for line in raw.splitlines() if normalize(line)}


def changed_series_and_pages(
    before_cards: Any, after_cards: Any, before_content: Any = None, after_content: Any = None
) -> tuple[set[str], set[str]]:
    before_cards = before_cards if isinstance(before_cards, dict) else {}
    after_cards = after_cards if isinstance(after_cards, dict) else {}
    series = {sid for sid in set(before_cards) | set(after_cards) if before_cards.get(sid) != after_cards.get(sid)}
    pages: set[str] = set()
    for sid in series:
        for card in (before_cards.get(sid), after_cards.get(sid)):
            if isinstance(card, dict):
                pages.update(Path(image).stem for image in card.get("steps", []) if isinstance(image, str))

    def content_map(value: Any) -> dict[str, Any]:
        if not isinstance(value, list):
            return {}
        return {str(row.get("image")): row for row in value if isinstance(row, dict) and row.get("image")}

    old_content = content_map(before_content)
    new_content = content_map(after_content)
    for image in set(old_content) | set(new_content):
        if old_content.get(image) != new_content.get(image):
            pages.add(Path(image).stem)
    return series, pages


def pages_from_paths(files: set[str]) -> set[str]:
    pages: set[str] = set()
    for path in files:
        p = Path(path)
        if path.startswith("cards/") and p.suffix.lower() == ".html" and p.name != "404.html":
            pages.add(p.stem)
        elif path.startswith("img/") and p.suffix.lower() in {".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg"}:
            pages.add(p.stem)
    return pages


def series_for_pages(cards: Any, pages: set[str]) -> set[str]:
    if not isinstance(cards, dict) or not pages:
        return set()
    return {
        sid for sid, card in cards.items()
        if isinstance(card, dict) and any(Path(image).stem in pages for image in card.get("steps", []))
    }


def impact_for_commit(root: Path, sha: str, files: set[str]) -> tuple[list[str], list[str]]:
    parent = f"{sha}^"
    old_cards = json_at(root, parent, "cards.json")
    new_cards = json_at(root, sha, "cards.json")
    old_content = json_at(root, parent, "data/card_content.json")
    new_content = json_at(root, sha, "data/card_content.json")
    series, pages = changed_series_and_pages(old_cards, new_cards, old_content, new_content)
    pages.update(pages_from_paths(files))
    series.update(series_for_pages(new_cards or old_cards, pages))
    return sorted(pages), sorted(series)


def commit_metadata(root: Path, sha: str) -> tuple[str, str]:
    raw = git(root, "show", "-s", "--date=short", "--format=%ad%x00%s", sha).rstrip("\n")
    parts = raw.split("\x00", 1)
    return (parts + [""])[:2]


def history_changes(root: Path, range_spec: str) -> list[dict[str, Any]]:
    shas = [line for line in git(root, "rev-list", "--reverse", range_spec).splitlines() if line]
    explicit_map = commit_request_map(root, requests_worktree(root))
    changes = []
    for sha in shas:
        files = changed_files_for_commit(root, sha)
        site_files = {path for path in files if is_site_path(path, tracked=True)}
        if not site_files:
            continue
        date_value, subject = commit_metadata(root, sha)
        pages, series = impact_for_commit(root, sha, site_files)
        changed_ids = changed_request_ids(root, f"{sha}^", sha) if REQUESTS in files else []
        commit_rows = requests_at(root, sha) if changed_ids else {}
        same_commit_requests = [
            rid for rid in changed_ids
            if rid in commit_rows and request_links_commit(root, commit_rows[rid], sha)
        ]
        request_ids = sorted(set(explicit_map.get(sha, [])) | set(same_commit_requests))
        generated_only = site_files <= GENERATED_ONLY_FILES and (
            "自動化" in subject or "service worker" in subject.lower() or "sw.js" in subject.lower()
        )
        if request_ids:
            coverage = "有需求紀錄"
        elif generated_only:
            coverage = "自動產生後續"
        elif any(is_management_path(path) for path in files):
            coverage = "有管理檔但未連結需求"
        else:
            coverage = "缺少管理連結"
        changes.append({
            "commit": sha, "date": date_value, "subject": subject, "files": sorted(site_files),
            "areas": classify_areas(site_files), "page_ids": pages, "series_ids": series,
            "request_ids": request_ids, "coverage": coverage, "generated_only": generated_only,
        })
    return changes


def current_worktree(root: Path) -> dict[str, Any]:
    staged = {normalize(x) for x in git(root, "diff", "--cached", "--name-only").splitlines() if normalize(x)}
    unstaged = {normalize(x) for x in git(root, "diff", "--name-only").splitlines() if normalize(x)}
    untracked = {normalize(x) for x in git(root, "ls-files", "--others", "--exclude-standard").splitlines() if normalize(x)}
    tracked_files = {normalize(x) for x in git(root, "ls-files").splitlines() if normalize(x)}
    all_files = staged | unstaged | untracked
    site_files = {path for path in all_files if is_site_path(path, tracked=path in tracked_files or path in staged)}
    management_files = {path for path in all_files if is_management_path(path)}
    old_cards = json_at(root, "HEAD", "cards.json")
    new_cards = json_worktree(root, "cards.json")
    old_content = json_at(root, "HEAD", "data/card_content.json")
    new_content = json_worktree(root, "data/card_content.json")
    series, pages = changed_series_and_pages(old_cards, new_cards, old_content, new_content)
    pages.update(pages_from_paths(site_files))
    series.update(series_for_pages(new_cards or old_cards, pages))
    changed_ids = changed_request_ids(root, "HEAD") if REQUESTS in all_files else []
    worktree_requests = requests_worktree(root)
    changed_requests = [
        rid for rid in changed_ids
        if worktree_requests.get(rid, {}).get("git_commit") == "same_commit"
    ]
    generated_only = bool(site_files) and site_files <= GENERATED_ONLY_FILES
    if not site_files:
        coverage = "沒有未提交網站變更"
    elif changed_requests:
        coverage = "有需求紀錄"
    elif generated_only:
        coverage = "自動產生後續"
    elif management_files:
        coverage = "有管理檔但未連結需求"
    else:
        coverage = "缺少管理連結"
    return {
        "files": sorted(site_files), "staged_files": sorted(site_files & staged),
        "unstaged_files": sorted(site_files & unstaged), "untracked_files": sorted(site_files & untracked),
        "management_files": sorted(management_files), "areas": classify_areas(site_files) if site_files else [],
        "page_ids": sorted(pages), "series_ids": sorted(series), "request_ids": changed_requests,
        "coverage": coverage, "generated_only": generated_only,
    }


def upstream_state(root: Path) -> dict[str, Any]:
    upstream = git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False).strip()
    compare = upstream or ("origin/main" if git(root, "rev-parse", "--verify", "origin/main", check=False).strip() else "")
    result: dict[str, Any] = {"upstream": upstream or None, "compared_with": compare or None}
    if compare:
        counts = git(root, "rev-list", "--left-right", "--count", f"HEAD...{compare}", check=False).split()
        if len(counts) == 2:
            result["ahead"] = int(counts[0])
            result["behind"] = int(counts[1])
    return result


def filter_changes(changes: list[dict[str, Any]], page: str | None, series: str | None, request: str | None) -> list[dict[str, Any]]:
    return [
        change for change in changes
        if (not page or page in change["page_ids"])
        and (not series or series in change["series_ids"])
        and (not request or request in change["request_ids"])
    ]


def print_human(report: dict[str, Any], limit: int) -> None:
    print("網站變更自動追蹤（唯讀）")
    print(f"HEAD: {report['head'][:12]}  基準: {report['tracking_start'][:12]}")
    upstream = report["upstream"]
    if upstream.get("compared_with"):
        print(f"與 {upstream['compared_with']} 比較：ahead {upstream.get('ahead', '?')} / behind {upstream.get('behind', '?')}")
    summary = report["summary"]
    print(f"已提交網站變更：{summary['history_changes']}；有管理連結：{summary['covered_history']}；缺少管理連結：{summary['missing_history']}")
    working = report["working_tree"]
    print(f"目前未提交網站檔案：{len(working['files'])}；狀態：{working['coverage']}")
    selected = report["changes"][-limit:] if limit else report["changes"]
    for change in selected:
        requests = ",".join(change["request_ids"]) or "—"
        pages = ",".join(change["page_ids"][:8])
        if len(change["page_ids"]) > 8:
            pages += f"…共{len(change['page_ids'])}頁"
        print(f"- {change['date']} {change['commit'][:8]} {change['subject']}")
        print(f"  {change['coverage']}；CR={requests}；範圍={'、'.join(change['areas'])}")
        if pages:
            print(f"  頁面：{pages}")
    if working["files"]:
        print("- 未提交：")
        print(f"  {working['coverage']}；CR={','.join(working['request_ids']) or '—'}")
        print(f"  檔案：{', '.join(working['files'][:12])}" + ("…" if len(working["files"]) > 12 else ""))
    if report["problems"]:
        print("需要處理：")
        for problem in report["problems"]:
            print(f"- {problem}")
    else:
        print("結果：目前查詢範圍的網站變更都有可追溯管理連結。")


def build_report(root: Path, range_spec: str, include_working: bool, page: str | None, series: str | None, request: str | None) -> dict[str, Any]:
    changes = filter_changes(history_changes(root, range_spec), page, series, request)
    working = current_worktree(root) if include_working else {
        "files": [], "management_files": [], "page_ids": [], "series_ids": [], "request_ids": [],
        "coverage": "未檢查", "generated_only": False, "staged_files": [], "unstaged_files": [],
        "untracked_files": [], "areas": [],
    }
    problems = [f"{change['commit'][:8]} {change['subject']}：缺少管理連結" for change in changes if change["coverage"] in {"缺少管理連結", "有管理檔但未連結需求"}]
    if include_working and working["coverage"] in {"缺少管理連結", "有管理檔但未連結需求"}:
        problems.append(f"目前未提交網站變更：{working['coverage']}")
    covered = sum(change["coverage"] in {"有需求紀錄", "自動產生後續"} for change in changes)
    return {
        "schema_version": 1, "root": str(root), "head": git(root, "rev-parse", "HEAD").strip(),
        "tracking_start": TRACKING_START, "range": range_spec, "upstream": upstream_state(root),
        "summary": {
            "history_changes": len(changes), "covered_history": covered,
            "missing_history": sum(change["coverage"] in {"缺少管理連結", "有管理檔但未連結需求"} for change in changes),
        },
        "filters": {"page": page, "series": series, "request": request},
        "changes": changes, "working_tree": working, "problems": problems,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="直接查詢 Git 中的網站變更及其專案管理連結；不修改任何檔案。")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--range", dest="range_spec", help="Git revision range，例如 BASE..HEAD")
    parser.add_argument("--since", default=TRACKING_START, help="未指定 --range 時使用的起點 commit")
    parser.add_argument("--page", help="只查指定 page_id")
    parser.add_argument("--series", help="只查指定 series_id")
    parser.add_argument("--request", help="只查指定 CR 編號")
    parser.add_argument("--json", action="store_true", help="輸出完整 JSON")
    parser.add_argument("--check", action="store_true", help="若有未連結管理紀錄的網站變更則回傳失敗")
    parser.add_argument("--no-working-tree", action="store_true", help="不檢查目前未提交檔案")
    parser.add_argument("--limit", type=int, default=20, help="文字輸出最多顯示最近幾筆，0 表示全部")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        git(root, "rev-parse", "--is-inside-work-tree")
        range_spec = args.range_spec or f"{args.since}..HEAD"
        if range_spec.startswith("0000000000000000000000000000000000000000.."):
            range_spec = f"{args.since}..{range_spec.split('..', 1)[1]}"
        report = build_report(root, range_spec, not args.no_working_tree, args.page, args.series, args.request)
        print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else "", end="" if args.json else "")
        if not args.json:
            print_human(report, max(args.limit, 0))
        return 1 if args.check and report["problems"] else 0
    except (GitError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
