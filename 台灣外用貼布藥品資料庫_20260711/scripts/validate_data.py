import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'source'/'processed'/'validation_summary.json'
print(p.read_text(encoding='utf-8'))
