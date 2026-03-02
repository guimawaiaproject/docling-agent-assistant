#!/usr/bin/env python3
"""
Analyse Spline — Docling
Scanne le projet pour identifier les meilleurs emplacements pour des composants Spline 3D.

Usage: python scripts/analyze_spline_opportunities.py [--output FILE]
"""

import argparse
import re
from pathlib import Path

# Patterns : (regex, type_composant, priorite, description)
PATTERNS = [
    # Hero / landing
    (r"<h1[^>]*>[\s\S]*?</h1>", "hero", "haute", "Titre principal — candidat pour logo 3D ou scène hero"),
    (r"className=.*hero|hero.*className", "hero", "haute", "Section hero explicite"),
    # Empty states
    (r"length === 0|\.length === 0|filtered\.length === 0|history\.length === 0", "empty-state", "haute", "Empty state — illustration 3D légère"),
    (r"Aucun produit trouvé|Aucune facture|Aucun résultat", "empty-state", "haute", "Message vide — zone pour 3D"),
    # Pages principales
    (r"ScanPage|scan.*page", "landing", "haute", "Page scan — hero ou onboarding 3D"),
    (r"CataloguePage|catalogue.*page", "showcase", "moyenne", "Catalogue — mockup ou icône 3D"),
    (r"ValidationPage|validation.*page", "workflow", "moyenne", "Validation — feedback visuel 3D"),
    # Modals / overlays
    (r"Modal|modal|Dialog|dialog", "modal", "moyenne", "Modal — accent 3D possible"),
    # Boutons CTA importants
    (r"Scanner une facture|Lancer|Photographier", "cta", "moyenne", "CTA principal — icône 3D"),
    # Sections marketing
    (r"text-center|flex flex-col items-center", "centered", "basse", "Section centrée — espace pour 3D"),
]


def scan_file(filepath: Path) -> list[dict]:
    """Analyse un fichier et retourne les opportunités Spline."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    opportunities = []

    for regex, comp_type, priority, desc in PATTERNS:
        for m in re.finditer(regex, content, re.IGNORECASE | re.MULTILINE):
            line_num = content[: m.start()].count("\n") + 1
            start = max(0, m.start() - 30)
            end = min(len(content), m.end() + 50)
            snippet = content[start:end].replace("\n", " ").strip()
            if len(snippet) > 80:
                snippet = snippet[:77] + "..."

            opportunities.append({
                "file": str(filepath),
                "line": line_num,
                "type": comp_type,
                "priority": priority,
                "description": desc,
                "snippet": snippet,
            })

    return opportunities


def main():
    parser = argparse.ArgumentParser(description="Analyse les opportunités Spline dans le projet")
    parser.add_argument("--output", "-o", type=Path, help="Fichier de sortie (Markdown)")
    parser.add_argument("paths", nargs="*", default=["apps/pwa/src"], help="Dossiers à scanner")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    all_opps = []
    seen = set()

    for path_str in args.paths:
        path = root / path_str
        if not path.exists():
            continue
        files = list(path.rglob("*.jsx")) + list(path.rglob("*.tsx"))
        for f in files:
            if "__tests__" in str(f) or "node_modules" in str(f):
                continue
            for opp in scan_file(f):
                key = (opp["file"], opp["line"], opp["type"])
                if key not in seen:
                    seen.add(key)
                    all_opps.append(opp)

    # Trier : priorité haute > moyenne > basse, puis fichier, ligne
    order = {"haute": 0, "moyenne": 1, "basse": 2}
    all_opps.sort(key=lambda x: (order.get(x["priority"], 3), x["file"], x["line"]))

    lines = [
        "# Rapport d'opportunités Spline — Docling",
        "",
        "> Généré par `python scripts/analyze_spline_opportunities.py`",
        "",
        f"**{len(all_opps)} opportunités** détectées.",
        "",
        "## Résumé par priorité",
        "",
    ]

    by_priority = {}
    for o in all_opps:
        p = o["priority"]
        by_priority[p] = by_priority.get(p, 0) + 1
    for p in ["haute", "moyenne", "basse"]:
        if p in by_priority:
            lines.append(f"- **{p}** : {by_priority[p]}")

    lines.extend(["", "## Détail des opportunités", ""])

    current_file = None
    for o in all_opps:
        f = o["file"]
        rel = Path(f).relative_to(root) if root in Path(f).parents else f
        if f != current_file:
            current_file = f
            lines.append(f"### {rel}")
            lines.append("")
        lines.append(f"- **Ligne {o['line']}** — [{o['priority']}] {o['type']}")
        lines.append(f"  - {o['description']}")
        lines.append(f"  - Extrait : `{o['snippet'][:70]}...`" if len(o["snippet"]) > 70 else f"  - Extrait : `{o['snippet']}`")
        lines.append("")

    lines.extend([
        "## Types de composants Spline recommandés",
        "",
        "| Type | Usage | Source |",
        "|------|-------|--------|",
        "| hero | Titre, landing | Library, Community |",
        "| empty-state | États vides | Scène légère, icône 3D |",
        "| logo | Branding | 3D Logo, Spell AI |",
        "| showcase | Produit, démo | 3D Mockup |",
        "| cta | Boutons importants | 3D Icons |",
        "",
        "## Prochaines étapes",
        "",
        "1. Choisir une opportunité prioritaire",
        "2. Créer ou remixer une scène sur [spline.design](https://spline.design/)",
        "3. Exporter en React et intégrer via l'agent Spline Expert",
        "",
        "Référence : `.cursor/agents/spline-expert.md`",
    ])

    report = "\n".join(lines)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Rapport écrit dans {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
