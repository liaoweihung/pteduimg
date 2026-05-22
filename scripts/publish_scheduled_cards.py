from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CARDS_JSON = ROOT / "cards.json"
CARDS_MANUAL_JSON = ROOT / "cards.manual.json"
CHANGELOG = ROOT / "CHANGELOG.md"


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_datetime(value: str) -> dt.datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("empty datetime")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = dt.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone(dt.timedelta(hours=8)))
    return parsed.astimezone(dt.timezone.utc)


def now_utc(value: str | None) -> dt.datetime:
    if value:
        return parse_datetime(value)
    return dt.datetime.now(dt.timezone.utc)


def due_hidden_cards(cards: dict[str, Any], current_time: dt.datetime) -> list[tuple[str, dict[str, Any]]]:
    due: list[tuple[str, dict[str, Any]]] = []
    for card_id, card in cards.items():
        if not isinstance(card, dict):
            continue
        if card.get("hidden") is not True:
            continue
        publish_at = card.get("publish_at")
        if not publish_at:
            continue
        publish_time = parse_datetime(str(publish_at))
        if publish_time <= current_time:
            due.append((card_id, card))
    return due


def apply_publication(cards: dict[str, Any], manual: dict[str, Any], due: list[tuple[str, dict[str, Any]]]) -> None:
    for card_id, _card in due:
        cards[card_id]["hidden"] = False
        if isinstance(manual.get(card_id), dict):
            manual[card_id]["hidden"] = False


def count_steps(card: dict[str, Any]) -> int:
    steps = card.get("steps")
    return len(steps) if isinstance(steps, list) else 0


def changelog_entry(date_text: str, due: list[tuple[str, dict[str, Any]]]) -> str:
    lines = [f"## {date_text}", "", "### 新增圖卡"]
    for _card_id, card in due:
        title = card.get("title") or "未命名圖卡"
        total = count_steps(card)
        if total:
            lines.append(f"- {title}：定時公開 {total} 張圖卡。")
        else:
            lines.append(f"- {title}：定時公開。")
    lines.append("")
    return "\n".join(lines)


def insert_changelog_entry(changelog: str, date_text: str, due: list[tuple[str, dict[str, Any]]]) -> str:
    entry = changelog_entry(date_text, due)
    additions = []
    for _card_id, card in due:
        title = card.get("title") or "未命名圖卡"
        total = count_steps(card)
        additions.append(f"- {title}：定時公開 {total} 張圖卡。" if total else f"- {title}：定時公開。")
    addition_text = "\n".join(additions)
    date_heading = f"## {date_text}"
    heading_match = re.search(rf"^{re.escape(date_heading)}\s*$", changelog, flags=re.MULTILINE)
    if heading_match:
        next_heading = re.search(r"^## \d{4}-\d{2}-\d{2}\s*$", changelog[heading_match.end() :], flags=re.MULTILINE)
        section_end = heading_match.end() + next_heading.start() if next_heading else len(changelog)
        section = changelog[heading_match.start() : section_end]

        new_card_heading = re.search(r"^### 新增圖卡\s*$", section, flags=re.MULTILINE)
        if new_card_heading:
            insert_at = heading_match.start() + new_card_heading.end()
            return changelog[:insert_at] + "\n" + addition_text + changelog[insert_at:]

        insert_at = heading_match.end()
        return changelog[:insert_at] + "\n\n### 新增圖卡\n" + addition_text + "\n" + changelog[insert_at:]

    first_date = re.search(r"^## \d{4}-\d{2}-\d{2}\s*$", changelog, flags=re.MULTILINE)
    if not first_date:
        return changelog.rstrip() + "\n\n" + entry
    return changelog[: first_date.start()] + entry + "\n" + changelog[first_date.start() :]


def update_changelog(due: list[tuple[str, dict[str, Any]]], current_time: dt.datetime) -> None:
    if not CHANGELOG.exists():
        return
    changelog = CHANGELOG.read_text(encoding="utf-8")
    date_text = current_time.astimezone(dt.timezone(dt.timedelta(hours=8))).strftime("%Y-%m-%d")
    CHANGELOG.write_text(insert_changelog_entry(changelog, date_text, due), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish hidden cards when their publish_at time has arrived.")
    parser.add_argument("--now", help="Override current time for testing, for example 2026-06-01T09:00:00+08:00.")
    parser.add_argument("--dry-run", action="store_true", help="Show due cards without writing files.")
    parser.add_argument("--no-changelog", action="store_true", help="Do not update CHANGELOG.md.")
    args = parser.parse_args()

    cards = load_json(CARDS_JSON)
    manual = load_json(CARDS_MANUAL_JSON)
    current_time = now_utc(args.now)
    due = due_hidden_cards(cards, current_time)

    if not due:
        print("No scheduled cards are due.")
        return 0

    print("Scheduled cards due for publication:")
    for card_id, card in due:
        print(f"- {card_id}: {card.get('title', card_id)} ({card.get('publish_at')})")

    if args.dry_run:
        return 0

    apply_publication(cards, manual, due)
    write_json(CARDS_JSON, cards)
    write_json(CARDS_MANUAL_JSON, manual)
    if not args.no_changelog:
        update_changelog(due, current_time)
    print(f"Published {len(due)} scheduled card series.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
