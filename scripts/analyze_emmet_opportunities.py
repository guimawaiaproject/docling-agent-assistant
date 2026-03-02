#!/usr/bin/env python3
"""
Analyse Emmet — Docling
Scanne le projet pour trouver des structures HTML/JSX qui pourraient
être remplacées par des abréviations Emmet pour réduire le code.

Usage: python scripts/analyze_emmet_opportunities.py [--output FILE]
"""

import argparse
import re
from pathlib import Path

# Patterns à détecter : (regex, description, abréviation Emmet suggérée)
PATTERNS = [
    # Skeleton loaders : [1,2,3,...].map avec structure répétée
    (
        r"\[[\d,\s]+\]\.map\s*\(\s*\(\s*\w+\s*\)\s*=>\s*\(\s*\n?\s*<div",
        "Skeleton loader répété (.map avec div)",
        "div.skeleton*N puis remplacer par .map si dynamique",
    ),
    # Stats cards : {label, val, color}.map
    (
        r"\{\s*label[^}]+\}\s*\.map\s*\(\s*\(\s*\{[^}]+\}\s*\)\s*=>",
        "Cartes stats répétées (label/val/color)",
        "div.stat*3>span.label+span.val ou div*3>(span+span)",
    ),
    # Structure div>div>div imbriquée
    (
        r"<div[^>]*>\s*\n\s*<div[^>]*>\s*\n\s*<div[^>]*>",
        "Triple imbrication div>div>div",
        "div>div>div",
    ),
    # div.flex.items-center.gap-X
    (
        r'<div\s+className="[^"]*flex[^"]*items-center[^"]*gap',
        "div flex items-center gap",
        "div.flex.items-center.gap-2",
    ),
    # div.rounded-xl.border
    (
        r'<div\s+className="[^"]*rounded-(xl|2xl|lg)[^"]*border',
        "div rounded + border",
        "div.rounded-xl.border.border-slate-700",
    ),
    # Boutons similaires répétés (3+)
    (
        r'(<button[^>]*className="[^"]*flex[^"]*items-center[^"]*gap[^"]*"[^>]*>[\s\S]*?</button>\s*){3,}',
        "Boutons similaires répétés (3+)",
        "button.flex.items-center.gap-2*N",
    ),
    # ul>li*N
    (
        r"<ul[^>]*>[\s\S]*?<li[^>]*>[\s\S]*?</li>[\s\S]*?<li",
        "ul avec plusieurs li",
        "ul>li*N",
    ),
    # option dans select
    (
        r"<option[^>]*>[\s\S]*?</option>\s*<option",
        "Options select répétées",
        "option*N ou option{Item $}*N",
    ),
    # div.grid avec enfants
    (
        r'<div[^>]*className="[^"]*grid[^"]*grid-cols',
        "Grid avec colonnes",
        "div.grid.grid-cols-N.gap-X",
    ),
    # span répétés (Min, Moy, Max style)
    (
        r"<span[^>]*>\s*\{[^}]+\}\s*</span>\s*<span",
        "Spans similaires répétés",
        "span*N ou span{Label $}*N",
    ),
]


def _sanitize_tag(tag: str) -> str:
    """Restrict to safe HTML tag name (alphanumeric, hyphen) — prevents prompt injection."""
    if not tag:
        return "div"
    safe = "".join(c for c in tag if c.isalnum() or c in "-_")
    return safe[:50] if safe else "div"


def _sanitize_snippet(text: str, max_len: int = 100) -> str:
    """Sanitize source excerpt for safe inclusion in reports/prompts."""
    if not text:
        return ""
    truncated = len(text) > max_len
    s = text[:max_len].replace("\n", " ").strip()
    # Escape braces to prevent template/prompt injection
    s = s.replace("{", "{{").replace("}", "}}")
    return s + ("..." if truncated else "")


def scan_file(filepath: Path) -> list[dict]:
    """Analyse un fichier et retourne les opportunités Emmet trouvées."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return [{"error": str(e)}]

    opportunities = []

    for _i, pattern_info in enumerate(PATTERNS):
        regex, desc, emmet = pattern_info
        for m in re.finditer(regex, content, re.MULTILINE | re.DOTALL):
            # Trouver le numéro de ligne
            line_num = content[: m.start()].count("\n") + 1
            # Extraire un extrait (max 80 chars) — sanitisé pour éviter l'injection
            start = max(0, m.start() - 20)
            end = min(len(content), m.end() + 40)
            snippet = _sanitize_snippet(content[start:end], max_len=100)

            opportunities.append(
                {
                    "file": str(filepath),
                    "line": line_num,
                    "pattern": desc,
                    "emmet": emmet,
                    "snippet": snippet,
                }
            )

    # Détection manuelle : structures répétées dans .map
    map_pattern = re.compile(
        r"\.map\s*\(\s*\(\s*\w+\s*\)\s*=>\s*\(\s*\n?\s*<(\w+)",
        re.MULTILINE,
    )
    for m in map_pattern.finditer(content):
        line_num = content[: m.start()].count("\n") + 1
        raw_tag = m.group(1) if m.lastindex else "div"
        tag = _sanitize_tag(raw_tag)
        raw_snippet = content[max(0, m.start() - 10) : m.end() + 30]
        if not any(o.get("line") == line_num for o in opportunities):
            opportunities.append(
                {
                    "file": str(filepath),
                    "line": line_num,
                    "pattern": f"Structure répétée dans .map (tag: {tag})",
                    "emmet": f"{tag}*N puis adapter au .map",
                    "snippet": _sanitize_snippet(raw_snippet, max_len=100),
                }
            )

    return opportunities


def main():
    parser = argparse.ArgumentParser(description="Analyse les opportunités Emmet dans le projet")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Fichier de sortie (Markdown). Sinon stdout.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["apps/pwa/src", "apps/pwa/index.html"],
        help="Dossiers/fichiers à scanner",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    all_opps = []
    seen = set()

    for path_str in args.paths:
        path = root / path_str
        if not path.exists():
            continue
        files = list(path.rglob("*.jsx")) + list(path.rglob("*.tsx")) + list(path.rglob("*.html"))
        for f in files:
            if "__tests__" in str(f) or "node_modules" in str(f):
                continue
            for opp in scan_file(f):
                if "error" in opp:
                    continue
                key = (opp["file"], opp["line"], opp["pattern"])
                if key not in seen:
                    seen.add(key)
                    all_opps.append(opp)

    # Trier par fichier puis ligne
    all_opps.sort(key=lambda x: (x["file"], x["line"]))

    # Générer le rapport
    lines = [
        "# Rapport d'opportunités Emmet — Docling",
        "",
        f"**{len(all_opps)} opportunités** détectées.",
        "",
        "## Résumé par fichier",
        "",
    ]

    by_file = {}
    for o in all_opps:
        f = o["file"]
        by_file[f] = by_file.get(f, 0) + 1

    for f, count in sorted(by_file.items(), key=lambda x: -x[1]):
        rel = Path(f).relative_to(root) if root in Path(f).parents else f
        lines.append(f"- `{rel}` : **{count}** opportunité(s)")

    lines.extend([
        "",
        "## Détail des opportunités",
        "",
    ])

    current_file = None
    for o in all_opps:
        f = o["file"]
        rel = Path(f).relative_to(root) if root in Path(f).parents else f
        if f != current_file:
            current_file = f
            lines.append(f"### {rel}")
            lines.append("")
        lines.append(f"- **Ligne {o['line']}** — {o['pattern']}")
        lines.append(f"  - Abréviation Emmet : `{o['emmet']}`")
        lines.append(f"  - Extrait : `{o['snippet'][:80]}...`" if len(o["snippet"]) > 80 else f"  - Extrait : `{o['snippet']}`")
        lines.append("")

    lines.extend([
        "## Comment utiliser",
        "",
        "1. Ouvrir le fichier concerné dans Cursor",
        "2. Remplacer le code verbeux par l'abréviation Emmet",
        "3. Appuyer sur **Tab** pour développer",
        "4. Adapter si nécessaire (props, contenu dynamique)",
        "",
        "Référence : [docs.emmet.io](https://docs.emmet.io/)",
    ])

    report = "\n".join(lines)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Rapport écrit dans {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
