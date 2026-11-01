"""Scoped structural rule fingerprints. Never imports or executes the builder."""
import ast
import hashlib
import json
import re

VERSION = "2"
MANIFEST = "docs/project-management/rules-v2.json"


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def text(root, name):
    return (root / name).read_text(encoding="utf-8-sig")


def source_hash(root, name):
    return hashlib.sha256(text(root, name).encode()).hexdigest()


def closure(root, filename, roots):
    """Hash AST definitions plus their transitive module-local dependencies.

    Unresolved names are imports/builtins; import declarations are included.
    No source code is evaluated. Missing roots fail closed.
    """
    tree = ast.parse(text(root, filename))
    definitions = {}
    imports = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.dump(node, include_attributes=False))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definitions[node.name] = node
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for child in ast.walk(target):
                    if isinstance(child, ast.Name):
                        definitions[child.id] = node
        elif not isinstance(node, ast.Expr):
            # Conditional imports or future executable module initialization:
            # conservatively retain them rather than silently omit dependencies.
            imports.append(ast.dump(node, include_attributes=False))
    missing = set(roots) - definitions.keys()
    if missing:
        raise ValueError(f"{filename}: missing fingerprint roots {sorted(missing)}")
    pending = list(roots)
    found = {}
    while pending:
        name = pending.pop()
        if name in found or name not in definitions:
            continue
        node = definitions[name]
        found[name] = ast.dump(node, include_attributes=False)
        pending.extend(n.id for n in ast.walk(node) if isinstance(n, ast.Name))
    return digest({"definitions": found, "imports": imports})


def domains(root):
    page = closure(root, "build.py", ["generate_card_pages", "fallback_seo_for_card",
                                     "normalize_card_seo", "apply_card_content_seo"])
    return {
        "page": digest({"build": page, "header": source_hash(root, "scripts/site_header.py")}),
        "footer": digest({"code": source_hash(root, "scripts/site_footer.py"),
                          "template": source_hash(root, "templates/site-footer.html"),
                          "styles": re.findall(r'\.site-footer(?: a(?::active)?)?\s*\{[^}]*\}',
                                               text(root, "css/base.css"))}),
        "acne_topic": closure(root, "scripts/acne_pilot.py", ["is_acne_topic", "render_topic_return"]),
        "pilot": digest({"code": closure(root, "scripts/acne_pilot.py",
                                          ["load_navigation", "render_navigation", "STYLES"]),
                         "navigation": json.loads(text(root, "data/acne_navigation.json"))}),
        "retirement": source_hash(root, "scripts/card_archive.py"),
        # Global generation also consumes page rendering/SEO. Conservative whole-file
        # coverage here retains orchestrator, PWA, index, sitemap and merge safeguards.
        "global": digest({name: source_hash(root, name) for name in [
            "build.py", "scripts/incremental_build.py", "scripts/card_archive.py",
            "scripts/site_footer.py", "scripts/site_header.py", "scripts/acne_pilot.py",
            "templates/site-footer.html", "data/acne_navigation.json", "css/base.css"]}),
        "engine": source_hash(root, "scripts/rule_fingerprints.py"),
    }


def applicable(row, cards, navigation, root):
    if row["visibility"] == "retired":
        return ["engine", "retirement"]
    card = cards[row["primary_series_id"]]
    result = ["engine", "page"]
    acne = "acne" in card.get("topics", []) or row["primary_series_id"] == "rosacea_care"
    if acne:
        result.append("acne_topic")
    # Include legacy output actually using the footer as well as generator opt-ins.
    html = text(root, row["page_path"]) if (root / row["page_path"]).is_file() else ""
    if card.get("showFooter") or acne or 'class="site-footer"' in html:
        result.append("footer")
    if row["page_id"] in {p["page_id"] for p in navigation["pages"]}:
        result.extend(["pilot", "footer"])
    return sorted(set(result))


def page_hash(row, cards, navigation, root, values):
    return digest({name: values[name] for name in applicable(row, cards, navigation, root)})
