#!/usr/bin/env python3
"""Run lightweight structural checks for Vento project assets."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\n(?P<body>.*?)\n---\n", re.DOTALL)


def check_skill(path: Path) -> list[str]:
    issues: list[str] = []
    text = path.read_text()
    match = FRONTMATTER_RE.match(text)
    if not match:
        return [f"{path}: missing YAML frontmatter"]

    body = match.group("body")
    if not re.search(r"^name:\s*\S+", body, re.MULTILINE):
        issues.append(f"{path}: missing name in frontmatter")
    if not re.search(r"^description:\s*\S+", body, re.MULTILINE):
        issues.append(f"{path}: missing description in frontmatter")
    if "[TODO" in text or "TODO:" in text:
        issues.append(f"{path}: contains TODO placeholder")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    issues: list[str] = []

    agents = root / "AGENTS.md"
    if agents.exists() and "[TODO" in agents.read_text():
        issues.append(f"{agents}: contains TODO placeholder")

    skills_root = root / ".agents" / "skills"
    if skills_root.exists():
        for skill_md in sorted(skills_root.glob("*/SKILL.md")):
            issues.extend(check_skill(skill_md))

    roadmap = root / "docs" / "roadmap" / "active-roadmap.md"
    productization_roadmap = root / "docs" / "productization" / "active-roadmap.md"
    for candidate in [roadmap, productization_roadmap]:
        if candidate.exists():
            line_count = len(candidate.read_text().splitlines())
            if line_count > 2000:
                issues.append(f"{candidate}: {line_count} lines, exceeds Vento roadmap rotation gate")

    if issues:
        print("Vento validation issues:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Vento validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
