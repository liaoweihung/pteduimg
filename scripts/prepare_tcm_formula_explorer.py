"""Install the TCM formula explorer's small index/formula data and product chunks.

The supplied index and formula tables contain legacy Big5 bytes represented as
Latin-1 characters.  Product chunks already contain UTF-8 Chinese and are
copied unchanged so official source text is never rewritten.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tcm_formula_explorer_data_chunks_20260718" / "data" / "tcm_formula_explorer"
TARGET = ROOT / "data" / "tcm_formula_explorer"


def fix_legacy_text(value):
    if isinstance(value, str):
        # Only attempt strings that can be the historical Big5-as-Latin-1 form.
        if any(ord(char) > 127 for char in value) and all(ord(char) <= 255 for char in value):
            try:
                return value.encode("latin-1").decode("big5")
            except UnicodeError:
                pass
        return value
    if isinstance(value, list):
        return [fix_legacy_text(item) for item in value]
    if isinstance(value, dict):
        return {key: fix_legacy_text(item) for key, item in value.items()}
    return value


def main() -> None:
    if not SOURCE.is_dir():
        raise SystemExit(f"Missing source directory: {SOURCE}")
    TARGET.mkdir(parents=True, exist_ok=True)
    for name in ("index.json", "formulas.json"):
        source = SOURCE / name
        data = fix_legacy_text(json.loads(source.read_text(encoding="utf-8")))
        (TARGET / name).write_text(
            json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    for source in SOURCE.glob("products-*.json"):
        shutil.copyfile(source, TARGET / source.name)
    print(f"Installed {len(list(TARGET.glob('products-*.json')))} product chunks in {TARGET}")


if __name__ == "__main__":
    main()
