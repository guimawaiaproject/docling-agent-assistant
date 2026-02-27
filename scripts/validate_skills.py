#!/usr/bin/env python3
"""
Validate Agent Skills — Docling
Vérifie que les SKILL.md respectent le format Agent Skills (agentskills.io).
Usage: python scripts/validate_skills.py [path...]
"""

import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict | None:
    """Extrait le YAML frontmatter entre --- et ---."""
    lines = content.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.strip().startswith("#"):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def validate_skill(skill_dir: Path) -> list[str]:
    """Valide un répertoire skill. Retourne la liste des erreurs."""
    errors = []
    skill_path = skill_dir / "SKILL.md"

    if not skill_path.exists():
        errors.append(f"{skill_dir}: SKILL.md manquant")
        return errors

    content = skill_path.read_text(encoding="utf-8")
    front = parse_frontmatter(content)

    if not front:
        errors.append(f"{skill_path}: frontmatter YAML manquant (--- ... ---)")
        return errors

    # name: requis, 1-64 chars, lowercase alphanumeric + hyphens
    name = front.get("name")
    if not name:
        errors.append(f"{skill_path}: champ 'name' requis dans le frontmatter")
    elif len(name) > 64:
        errors.append(f"{skill_path}: 'name' doit faire ≤ 64 caractères")
    elif not re.match(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$", name):
        errors.append(
            f"{skill_path}: 'name' doit être lowercase, alphanumérique et tirets uniquement, pas de -- ni - en début/fin"
        )
    elif skill_dir.name != name:
        errors.append(f"{skill_path}: le nom du dossier ({skill_dir.name}) doit correspondre à name ({name})")

    # description: requis, max 1024 chars
    desc = front.get("description")
    if not desc:
        errors.append(f"{skill_path}: champ 'description' requis dans le frontmatter")
    elif len(desc) > 1024:
        errors.append(f"{skill_path}: 'description' doit faire ≤ 1024 caractères")

    # Vérifier que le body n'est pas vide
    body_start = content.find("\n---\n", 4)
    if body_start != -1:
        body = content[body_start + 5:].strip()
        if len(body) < 50:
            errors.append(f"{skill_path}: le corps du skill semble trop court (< 50 caractères)")

    return errors


def discover_skills(base: Path) -> list[Path]:
    """Découvre tous les répertoires contenant SKILL.md."""
    skills = []
    for d in base.iterdir():
        if d.is_dir() and (d / "SKILL.md").exists():
            skills.append(d)
    return sorted(skills)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    search_dirs = [
        repo_root / ".agents" / "skills",
        repo_root / ".cursor" / "skills",
    ]

    # Chemins passés en argument
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1:]]
    else:
        paths = []
        for sd in search_dirs:
            if sd.exists():
                paths.extend(discover_skills(sd))

    if not paths:
        print("Aucun skill trouvé dans .agents/skills/ ou .cursor/skills/")
        return 0

    all_errors = []
    for p in paths:
        if p.is_file() and p.name == "SKILL.md":
            p = p.parent
        if (p / "SKILL.md").exists():
            errs = validate_skill(p)
            all_errors.extend(errs)

    if all_errors:
        print("Validation échouée:")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print(f"Validation réussie ({len(paths)} skill(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
