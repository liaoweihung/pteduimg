import datetime as dt
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2.credentials import Credentials


ROOT = Path(__file__).resolve().parents[1]
CARDS_PATH = ROOT / "cards.json"
REPORT_MD_PATH = ROOT / "reports" / "card-popularity.md"
REPORT_JSON_PATH = ROOT / "reports" / "card-popularity.json"
TAIPEI = ZoneInfo("Asia/Taipei")
WINDOW_HOURS = [24, 48, 72, 96, 120]


def fail(message):
    print(f"錯誤：{message}", file=sys.stderr)
    raise SystemExit(1)


def load_cards():
    with open(CARDS_PATH, "r", encoding="utf-8") as file:
        cards = json.load(file)

    visible = {}
    title_to_id = {}
    for card_id, item in cards.items():
        if item.get("hidden"):
            continue
        title = item.get("title") or card_id
        visible[card_id] = {
            "id": card_id,
            "title": title,
            "category": item.get("category", ""),
            "order": item.get("order", 9999),
        }
        title_to_id[title] = card_id
    return visible, title_to_id


def run_git(args):
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def estimate_first_seen_times(card_ids):
    first_seen = {}
    log = run_git(["log", "--reverse", "--format=%H%x09%aI", "--", "cards.json"])
    if not log:
        return first_seen

    remaining = set(card_ids)
    for line in log.splitlines():
        if not remaining:
            break
        commit, _, iso_time = line.partition("\t")
        content = run_git(["show", f"{commit}:cards.json"])
        if not content:
            continue
        try:
            snapshot = json.loads(content)
        except json.JSONDecodeError:
            continue
        seen_now = remaining.intersection(snapshot.keys())
        for card_id in seen_now:
            try:
                first_seen[card_id] = dt.datetime.fromisoformat(iso_time).astimezone(TAIPEI)
            except ValueError:
                first_seen[card_id] = None
        remaining -= seen_now
    return first_seen


def report_cutoff_now():
    now = dt.datetime.now(TAIPEI)
    cutoff = now.replace(hour=4, minute=0, second=0, microsecond=0)
    if now < cutoff:
        cutoff -= dt.timedelta(days=1)
    return cutoff


def load_ga_client():
    property_id = os.environ.get("GA4_PROPERTY_ID", "").strip()
    client_id = os.environ.get("GA4_OAUTH_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GA4_OAUTH_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("GA4_OAUTH_REFRESH_TOKEN", "").strip()

    if not property_id:
        fail("找不到 GA4_PROPERTY_ID。請在 GitHub Secrets 設定 GA4_PROPERTY_ID。")
    missing = [
        name
        for name, value in {
            "GA4_OAUTH_CLIENT_ID": client_id,
            "GA4_OAUTH_CLIENT_SECRET": client_secret,
            "GA4_OAUTH_REFRESH_TOKEN": refresh_token,
        }.items()
        if not value
    ]
    if missing:
        fail(f"找不到 {', '.join(missing)}。請在 GitHub Secrets 設定 OAuth 認證。")

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    return BetaAnalyticsDataClient(credentials=credentials), property_id


def fetch_ga_rows(client, property_id, end_time):
    start_date = (end_time - dt.timedelta(days=21)).date().isoformat()
    end_date = end_time.date().isoformat()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="dateHour"),
            Dimension(name="eventName"),
            Dimension(name="customEvent:card_title"),
            Dimension(name="customEvent:card_id"),
        ],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=100000,
    )

    try:
        response = client.run_report(request)
    except Exception as exc:
        fail(
            "GA4 Data API 查詢失敗。請確認 GA4_PROPERTY_ID、OAuth 認證，"
            "OAuth refresh token，以及自訂維度 card_title / card_id 是否已建立。\n"
            f"完整錯誤：{repr(exc)}"
        )

    rows = []
    for row in response.rows:
        date_hour = row.dimension_values[0].value
        try:
            hour_time = dt.datetime.strptime(date_hour, "%Y%m%d%H").replace(tzinfo=TAIPEI)
        except ValueError:
            continue
        if hour_time >= end_time:
            continue
        rows.append(
            {
                "time": hour_time,
                "event": row.dimension_values[1].value,
                "card_title": row.dimension_values[2].value,
                "card_id": row.dimension_values[3].value,
                "count": int(row.metric_values[0].value or 0),
            }
        )
    return rows


def rows_in_window(rows, end_time, hours):
    start_time = end_time - dt.timedelta(hours=hours)
    return [row for row in rows if start_time <= row["time"] < end_time]


def count_page_views(rows):
    return sum(row["count"] for row in rows if row["event"] == "page_view")


def count_card_clicks(rows):
    counter = Counter()
    for row in rows:
        if row["event"] != "view_instruction_card":
            continue
        title = row["card_title"] or row["card_id"] or "(未命名)"
        counter[title] += row["count"]
    return counter


def count_card_events(rows, event_name):
    counter = Counter()
    for row in rows:
        if row["event"] != event_name:
            continue
        title = row["card_title"] or row["card_id"] or "(未命名)"
        counter[title] += row["count"]
    return counter


def score(value, average):
    if average <= 0:
        return 0.0
    return value / average * 100


def pct(numerator, denominator):
    if denominator <= 0:
        return "0.0%"
    return f"{numerator / denominator * 100:.1f}%"


def recent_cards_table(cards, first_seen, rows, end_time):
    recent = sorted(
        cards.values(),
        key=lambda item: (
            first_seen.get(item["id"]) is not None,
            first_seen.get(item["id"]) or dt.datetime.min.replace(tzinfo=TAIPEI),
            -item.get("order", 9999),
        ),
        reverse=True,
    )[:20]

    clicks_by_window = {}
    page_views_by_window = {}
    for hours in WINDOW_HOURS:
        window_rows = rows_in_window(rows, end_time, hours)
        clicks_by_window[hours] = count_card_clicks(window_rows)
        page_views_by_window[hours] = count_page_views(window_rows)

    average_120 = sum(clicks_by_window[120].get(item["title"], 0) for item in recent) / max(len(recent), 1)
    table = []
    for item in recent:
        first = first_seen.get(item["id"])
        row = {
            "id": item["id"],
            "title": item["title"],
            "first_seen": first.strftime("%Y-%m-%d %H:%M") if first else "未知",
            "windows": {},
            "score_120h": score(clicks_by_window[120].get(item["title"], 0), average_120),
        }
        for hours in WINDOW_HOURS:
            clicks = clicks_by_window[hours].get(item["title"], 0)
            row["windows"][hours] = {
                "clicks": clicks,
                "site_views": page_views_by_window[hours],
                "ratio": pct(clicks, page_views_by_window[hours]),
            }
        table.append(row)
    return table


def top_cards_tables(rows, end_time):
    tables = {}
    for hours in WINDOW_HOURS:
        window_rows = rows_in_window(rows, end_time, hours)
        clicks = count_card_clicks(window_rows)
        site_views = count_page_views(window_rows)
        top = clicks.most_common(20)
        average = sum(count for _, count in top) / max(len(top), 1)
        tables[hours] = [
            {
                "rank": index + 1,
                "title": title,
                "clicks": count,
                "site_views": site_views,
                "ratio": pct(count, site_views),
                "score": score(count, average),
            }
            for index, (title, count) in enumerate(top)
        ]
    return tables


def daily_top20_streak(rows, end_time, days=14):
    daily_sets = []
    for offset in range(days, 0, -1):
        day_end = end_time - dt.timedelta(days=offset - 1)
        day_rows = rows_in_window(rows, day_end, 24)
        top_titles = {title for title, _ in count_card_clicks(day_rows).most_common(20)}
        daily_sets.append(top_titles)
    if not daily_sets:
        return []
    return sorted(set.intersection(*daily_sets)) if all(daily_sets) else []


def rising_cards_72h(rows, end_time):
    current_clicks = count_card_clicks(rows_in_window(rows, end_time, 72))
    previous_end = end_time - dt.timedelta(hours=72)
    previous_clicks = count_card_clicks(rows_in_window(rows, previous_end, 72))

    current_rank = {title: index + 1 for index, (title, _) in enumerate(current_clicks.most_common())}
    previous_rank = {title: index + 1 for index, (title, _) in enumerate(previous_clicks.most_common())}
    default_previous = max(len(previous_rank), 20) + 1
    rising = []
    for title, rank in current_rank.items():
        old_rank = previous_rank.get(title, default_previous)
        improvement = old_rank - rank
        if improvement > 0:
            rising.append(
                {
                    "title": title,
                    "rank": rank,
                    "previous_rank": old_rank if title in previous_rank else "未進榜",
                    "improvement": improvement,
                    "clicks": current_clicks[title],
                    "previous_clicks": previous_clicks.get(title, 0),
                }
            )
    return sorted(rising, key=lambda item: (-item["improvement"], item["rank"]))[:20]


def write_markdown(report):
    def md_table(headers, rows):
        output = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        output.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
        return "\n".join(output)

    lines = [
        "# 圖卡熱門度自動報表",
        "",
        f"- 統計切點：{report['cutoff_taipei']}（台灣時間）",
        "- 網站瀏覽分母：GA4 `page_view`",
        "- 圖卡點擊分子：GA4 `view_instruction_card`",
        "- 相對分數：同表平均點擊數 = 100，兩倍平均 = 200，一半平均 = 50",
        "",
        "## 1. 最近上架 20 張圖卡",
        "",
    ]

    recent_rows = []
    for item in report["recent_cards"]:
        recent_rows.append(
            [
                item["title"],
                item["first_seen"],
                item["windows"]["24"]["clicks"],
                item["windows"]["24"]["ratio"],
                item["windows"]["48"]["clicks"],
                item["windows"]["48"]["ratio"],
                item["windows"]["72"]["clicks"],
                item["windows"]["72"]["ratio"],
                item["windows"]["96"]["clicks"],
                item["windows"]["96"]["ratio"],
                item["windows"]["120"]["clicks"],
                item["windows"]["120"]["ratio"],
                f"{item['score_120h']:.1f}",
            ]
        )
    lines.append(
        md_table(
            ["圖卡", "推估上架", "24h", "24h比", "48h", "48h比", "72h", "72h比", "96h", "96h比", "120h", "120h比", "120h分數"],
            recent_rows,
        )
    )

    lines.extend(["", "## 2. 網站整體熱門圖卡", ""])
    for hours in WINDOW_HOURS:
        lines.extend([f"### 過去 {hours} 小時前 20 名", ""])
        rows = [
            [item["rank"], item["title"], item["clicks"], item["ratio"], f"{item['score']:.1f}"]
            for item in report["top_cards"][str(hours)]
        ]
        lines.append(md_table(["排名", "圖卡", "點擊", "點擊/瀏覽", "相對分數"], rows))
        lines.append("")

    lines.extend(["## 3. 過去 14 天每天都在前 20 的圖卡", ""])
    if report["daily_top20_all_14_days"]:
        lines.extend(f"- {title}" for title in report["daily_top20_all_14_days"])
    else:
        lines.append("- 無")

    lines.extend(["", "## 4. 最近 72 小時排名往前的圖卡", ""])
    if report["rising_72h"]:
        rows = [
            [item["title"], item["previous_rank"], item["rank"], item["improvement"], item["previous_clicks"], item["clicks"]]
            for item in report["rising_72h"]
        ]
        lines.append(md_table(["圖卡", "前 72h 排名", "近 72h 排名", "進步名次", "前 72h 點擊", "近 72h 點擊"], rows))
    else:
        lines.append("- 無")

    REPORT_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    cards, _ = load_cards()
    first_seen = estimate_first_seen_times(cards.keys())
    end_time = report_cutoff_now()
    client, property_id = load_ga_client()
    rows = fetch_ga_rows(client, property_id, end_time)

    report = {
        "cutoff_taipei": end_time.strftime("%Y-%m-%d %H:%M"),
        "recent_cards": recent_cards_table(cards, first_seen, rows, end_time),
        "top_cards": {str(hours): table for hours, table in top_cards_tables(rows, end_time).items()},
        "daily_top20_all_14_days": daily_top20_streak(rows, end_time),
        "rising_72h": rising_cards_72h(rows, end_time),
    }

    REPORT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report)
    print(f"已產生 {REPORT_MD_PATH.relative_to(ROOT)}")
    print(f"已產生 {REPORT_JSON_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
