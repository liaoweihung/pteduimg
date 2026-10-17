from pathlib import Path
import re
root = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent
for source, target, label in [('index.html','pharmacist.html','藥師版'),('public.html','public.html','民眾版')]:
    text = (root/source).read_text(encoding='utf-8')
    text = text.replace('<head>', '<head>\n    <base href="../../">\n    <meta name="robots" content="noindex,nofollow">', 1)
    text = text.replace('</head>', '<link rel="stylesheet" href="output/brand-header-preview/brand-header.css?v=2">\n</head>')
    text = re.sub(r'<header>.*?</header>', f'''<header class="brand-header">
    <img src="output/brand-header-preview/logo.png" alt="紅臉黑鬍子微笑 Logo" class="header-icon" width="48" height="48">
    <div class="brand-copy"><span class="brand-name">藥局衛教助手</span><small class="brand-edition">{label}</small></div>
</header>''', text, count=1, flags=re.S)
    text = text.replace("document.querySelector('header span').innerText = meta.title;", "document.querySelector('.brand-name').innerText = '藥局衛教助手';")
    text = text.replace('./index.html', './output/brand-header-preview/pharmacist.html').replace('./public.html', './output/brand-header-preview/public.html')
    # Top-level version switches always open at the top; related-topic links retain their targeting.
    text = re.sub(r'(href="[^"]+)\?focus=related-(?:public|pharmacist)(" id="nav-(?:pharmacist|public)")', r'\1\2', text)
    text = text.replace("if ('serviceWorker' in navigator)", "if (false /* 獨立預覽不註冊 Service Worker */)")
    text = text.replace('localStorage', 'sessionStorage')
    text = text.replace('<title>', '<title>頁首預覽｜', 1)
    text = '\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n'
    (out/target).write_text(text, encoding='utf-8')
print('Created two independent preview copies.')
