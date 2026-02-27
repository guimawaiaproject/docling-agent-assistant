#!/usr/bin/env python3
"""
Generate <available_skills> XML for agent prompts.
Format compatible with agentskills.io integration.
Usage: python scripts/skills_to_prompt.py
"""

import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict | None:
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


def discover_skills(base: Path) -> list[tuple[Path, dict]]:
    results = []
    for d in base.iterdir():
        if d.is_dir():
            skill_md = d / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text(encoding="utf-8")
                front = parse_frontmatter(content)
                if front and front.get("name") and front.get("description"):
                    results.append((d, front))
    return sorted(results, key=lambda x: x[1].get("name", ""))


def main() -> int:
    repo = Path(__file__).resolve().parent.parent
    search_dirs = [repo / ".agents" / "skills", repo / ".cursor" / "skills"]

    all_skills = []
    for sd in search_dirs:
        if sd.exists():
            for skill_dir, front in discover_skills(sd):
                all_skills.append((skill_dir, front))

    if not all_skills:
        print("<!-- No skills found -->", file=sys.stderr)
        return 1

    print("<available_skills>")
    for skill_dir, front in all_skills:
        name = front.get("name", "")
        desc = front.get("description", "")
        location = (skill_dir / "SKILL.md").resolve()
        print(f'  <skill>')
        print(f'    <name>{name}</name>')
        print(f'    <description>{desc}</description>')
        print(f'    <location>{location}</location>')
        print(f'  </skill>')
    print("</available_skills>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
