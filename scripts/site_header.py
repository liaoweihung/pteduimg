"""Shared static top navigation for card pages and standalone content pages."""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render_header(return_navigation, tools='', css_class='top-actions acne-topic-actions'):
    content = f'    <div class="{html.escape(css_class, quote=True)}">\n      {return_navigation}\n'
    return content + (tools + '\n' if tools else '') + '    </div>'


def render_home_navigation(href):
    return ('<nav class="topic-return-nav" aria-label="返回導覽">'
            f'<a class="pill" href="{html.escape(href, quote=True)}">返回首頁</a></nav>')


def sync_hub_header(root=ROOT, write=False):
    path = root / 'topics/acne.html'
    source = path.read_text(encoding='utf-8')
    replacements = {
        r'<!-- shared-header:start -->.*?<!-- shared-header:end -->':
            '<!-- shared-header:start -->\n' + render_header(render_home_navigation('../public.html')) + '\n  <!-- shared-header:end -->',
        r'/\* shared-header-styles:start \*/.*?/\* shared-header-styles:end \*/':
            '/* shared-header-styles:start */\n' + HEADER_STYLES + RETURN_STYLES + '\n    /* shared-header-styles:end */',
    }
    updated = source
    for pattern, replacement in replacements.items():
        if len(re.findall(pattern, updated, re.S)) != 1:
            raise ValueError('Hub must have one shared Header and style marker pair')
        updated = re.sub(pattern, lambda _: replacement, updated, flags=re.S)
    if updated == source:
        return True
    if write:
        path.write_text(updated, encoding='utf-8', newline='\n')
        return True
    return False


HEADER_STYLES = """    .top-actions {
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
    }
    .action-cluster {
      display:flex;
      gap:6px;
      overflow-x:auto;
    }
    .pill {
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
    }
    .pill:hover,
    .pill:focus-visible {
      background:rgba(255,255,255,.82);
      color:var(--ink);
    }
    .pill.active {
      background:rgba(0,123,131,.62);
      border-color:rgba(0,123,131,.2);
      color:#fff;
    }
    .icon-pill {
      justify-content:center;
      width:34px;
      min-width:34px;
      padding:0;
      font-size:1.15rem;
      line-height:1;
    }
"""
RETURN_STYLES = """
    .acne-topic-actions { flex-wrap:wrap; }
    .acne-topic-actions .action-cluster { flex:none; margin-left:auto; }
    .topic-return-nav { display:flex; gap:6px; max-width:100%; }
    .topic-return-nav .pill { min-height:44px; padding:8px; line-height:1.4; }
    .topic-return-nav a { white-space:normal; color:#00676e; }
    .topic-return-nav .pill:focus-visible { outline:2px solid var(--brand); outline-offset:2px; }
"""

if __name__ == '__main__':
    import sys
    if not sync_hub_header(write='--write' in sys.argv):
        sys.exit('Hub Header differs from shared source; run with --write')
    print('Hub Header matches the shared card Header source.')
