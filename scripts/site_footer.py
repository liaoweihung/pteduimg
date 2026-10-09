"""Render homepage, Hub and opt-in card footers from templates/site-footer.html.

Run python -B scripts/site_footer.py --write after editing the shared source.
Without --write this checks that homepage and Hub footers are in sync.
Use --page topics/acne.html to sync only the Hub, including its marked styles.
Homepage action buttons are page-local and never included in this source.
"""
from pathlib import Path
import re
import sys
import html
import argparse

ROOT = Path(__file__).resolve().parents[1]
FOOTER = re.compile(r'<footer class="site-footer">.*?</footer>', re.S)


NOTICES = {
    'index.html': '本工具圖文僅供藥師衛教參考，非專業人士務必諮詢藥師建議。',
    'public.html': '圖卡提供一般衛教資訊；個人用藥與照護問題，請諮詢醫師或藥師。',
}


def render_footer(root=ROOT, page='index.html'):
    prefix = '../' * (len(Path(page).parts) - 1) or './'
    return ((root / 'templates/site-footer.html').read_text(encoding='utf-8').rstrip('\n')
            .replace('{{prefix}}', prefix)
            .replace('{{notice}}', html.escape(NOTICES.get(page, NOTICES['index.html']))))


def footer_styles(root=ROOT):
    # Reuse only footer rules, not the global homepage CSS on card pages.
    css = (root / 'css/base.css').read_text(encoding='utf-8')
    return '\n'.join(re.findall(r'\.site-footer(?: a(?::active)?)?\s*\{[^}]*\}', css))


def sync_footer(root=ROOT, write=False, page='index.html'):
    path = root / page
    source = path.read_bytes().decode('utf-8')
    matches = list(FOOTER.finditer(source))
    if len(matches) != 1:
        raise ValueError(f'{page}: expected exactly one site-footer')
    expected = render_footer(root, page)
    if '\r\n' in source:
        expected = expected.replace('\n', '\r\n')
    match = matches[0]
    updated = source[:match.start()] + expected + source[match.end():]
    # Standalone pages can opt into the same footer styles without homepage CSS.
    style_pattern = r'/\* shared-footer-styles:start \*/.*?/\* shared-footer-styles:end \*/'
    styles = '/* shared-footer-styles:start */\n' + footer_styles(root) + '\n    /* shared-footer-styles:end */'
    if '\r\n' in source:
        styles = styles.replace('\n', '\r\n')
    updated = re.sub(style_pattern, lambda _: styles, updated, flags=re.S)
    if source == updated:
        return True
    if write:
        path.write_bytes(updated.encode('utf-8'))
        return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--page', action='append', choices=[*NOTICES, 'topics/acne.html'])
    args = parser.parse_args()
    for page in args.page or [*NOTICES, 'topics/acne.html']:
        if not sync_footer(write=args.write, page=page):
            sys.exit(f'{page} footer differs from shared source; run with --write')
    print('Selected footers match shared source.')
