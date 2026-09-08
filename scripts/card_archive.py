"""Generate the searchable retirement log and compatible historical card URLs."""
import datetime
import html
import json
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def read_retired_cards(root, cards):
    path = root / 'cards.retired.json'
    records = json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
    active = {'cards/' + Path(image).stem + '.html' for card in cards.values() for image in card.get('steps', [])}
    seen = set()
    for item in records:
        page, image = item['page'], item['image']
        if not image.startswith('img/') or '..' in Path(image).parts or not (root / image).is_file():
            raise ValueError(f'Invalid retired image: {image}')
        if page != 'cards/' + Path(image).stem + '.html' or page in seen or page in active:
            raise ValueError(f'Duplicate or active retired URL: {page}')
        datetime.date.fromisoformat(item['retired_at'])
        if not item['title'] or not item['reason'] or not item['replacements']:
            raise ValueError(f'Incomplete retired record: {page}')
        if any(link['page'] not in active for link in item['replacements']):
            raise ValueError(f'Retired page has missing replacement: {page}')
        seen.add(page)
    return records


def document(title, description, page, content, base_url, prefix='', noindex=False):
    return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}｜藥局衛教助手</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="{'noindex, follow' if noindex else 'index, follow'}">
  <link rel="canonical" href="{esc(base_url + page)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}｜藥局衛教助手">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(base_url + page)}">
  <meta property="og:image" content="{esc(base_url)}icon.png">
  <link rel="icon" href="{prefix}icon.png">
  <link rel="stylesheet" href="{prefix}css/card-archive.css">
  <script defer src="{prefix}js/card-archive.js"></script>
</head>
<body>
  <header><nav aria-label="頁面導覽"><a href="{prefix}public.html">← 民眾版圖卡</a><a href="{prefix}retired-cards.html">退出圖卡紀錄</a></nav></header>
  <main>{content}</main>
  <footer>歷史圖卡保留供查找；使用衛教資訊請優先參考目前版本。</footer>
  <button id="archive-update" hidden type="button">有新版本，按這裡更新</button>
</body>
</html>
'''


def replacement_list(record, prefix=''):
    return '<ul class="replacement-list">' + ''.join(
        f'<li><a href="{prefix}{esc(link["page"])}">{esc(link["title"])} <span aria-hidden="true">→</span></a></li>'
        for link in record['replacements']) + '</ul>'


def write_retired_pages(root, records, base_url):
    blocks = []
    for record in sorted(records, key=lambda item: item['retired_at'], reverse=True):
        page = record['page']
        anchor = Path(page).stem
        url = base_url + page
        search = ' '.join([record['title'], record['reason'], url, record['original_series'], *record.get('tags', [])])
        blocks.append(f'''<article class="archive-record" id="{esc(anchor)}" data-search="{esc(search)}">
  <div class="record-meta"><span class="status">已退出主要目錄</span><time datetime="{esc(record['retired_at'])}">{esc(record['retired_at'])}</time></div>
  <h2>{esc(record['title'])}</h2>
  <p class="original-series">原系列：{esc(record['original_series'])}</p>
  <p class="reason">{esc(record['reason'])}</p>
  <p class="url-label">保留的舊網址</p><a class="old-url" href="{esc(page)}">{esc(url)}</a>
  <h3>目前建議閱讀</h3>{replacement_list(record)}
  <a class="history-link" href="{esc(page)}">查看退出說明與歷史圖卡</a>
</article>''')
        content = f'''<p class="eyebrow">圖卡版本紀錄</p><h1>{esc(record['title'])}</h1>
<section class="retirement-notice"><span class="status">已退出主要目錄</span>
<p>這張圖卡已於 <time datetime="{esc(record['retired_at'])}">{esc(record['retired_at'])}</time> 退出主要目錄，舊網址保留供查找。</p>
<p>{esc(record['reason'])}</p><h2>請優先閱讀目前版本</h2>{replacement_list(record, '../')}
<p><a href="../retired-cards.html#{esc(anchor)}">查看完整退出紀錄</a></p></section>
<details class="historical-image"><summary>展開歷史圖卡（內容未更新）</summary>
<p>以下保留退出時的圖片，供版本比對；請優先閱讀上方目前版本。</p>
<img src="../{esc(record['image'])}" alt="歷史圖卡：{esc(record['title'])}" loading="lazy"></details>'''
        (root / page).write_text(document(record['title'] + '（已退出）', record['reason'], page, content, base_url, '../', True), encoding='utf-8', newline='\n')
    content = f'''<p class="eyebrow">藥局衛教助手 · 版本紀錄</p><h1>退出圖卡紀錄</h1>
<p class="intro">查找已退出主要目錄的圖卡、原始網址與替代內容。退出的圖卡仍保留舊網址，並在原頁清楚說明原因。</p>
<section class="search-panel" aria-label="搜尋退出紀錄"><label for="archive-search">搜尋標題、關鍵字或舊網址</label>
<div class="search-row"><input id="archive-search" type="search" placeholder="例如：粉刺、acne_dailycare_2" autocomplete="off"><button id="clear-search" type="button" hidden>清除</button></div>
<p id="archive-count" role="status">共 {len(records)} 筆退出紀錄</p></section>
<div class="archive-records">{''.join(blocks)}</div><p id="no-results" hidden>找不到符合的紀錄，請換個關鍵字或清除搜尋。</p>
<noscript><p>目前列出全部紀錄，可使用瀏覽器的「在頁面中尋找」。</p></noscript>'''
    (root / 'retired-cards.html').write_text(document('退出圖卡紀錄', '查找已退出主要目錄的圖卡、舊網址、退出原因與新版閱讀入口。', 'retired-cards.html', content, base_url), encoding='utf-8', newline='\n')
