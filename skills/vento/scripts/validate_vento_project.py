#!/usr/bin/env python3
"""Run lightweight structural checks for Vento project assets."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\n(?P<body>.*?)\n---\n", re.DOTALL)
CURRENT_STATE_NAME_RE = re.compile(r"(?:^|[-_])(?:codebase-)?current-state(?:[-_]|$)", re.IGNORECASE)


def check_agents(path: Path) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    text = path.read_text()
    lines = text.splitlines()

    if "[TODO" in text:
        issues.append(f"{path}: contains TODO placeholder")
    if "## Project Snapshot" in text:
        warnings.append(f"{path}: prefer 'Project Identity' over inventory-style 'Project Snapshot'")
    if "## Key Paths" in text:
        warnings.append(f"{path}: prefer pointer-level 'Context Entry Points' over detailed 'Key Paths'")
    if "## Commands" in text:
        warnings.append(f"{path}: prefer minimal 'Core Commands' over broad command inventories")
    if len(lines) > 180:
        warnings.append(f"{path}: {len(lines)} lines; AGENTS.md may be carrying current-state detail")

    path_refs = len(re.findall(r"`[^`]*(?:apps/|src/|packages/|docs/)[^`]*`", text))
    docs_refs = text.count("docs/")
    command_lines = sum(
        1 for line in lines if re.match(r"^\s*(pnpm|npm|yarn|pytest|uvicorn|python3|cd )\b", line)
    )

    if path_refs > 25:
        warnings.append(f"{path}: {path_refs} inline path references; move detailed module maps to current-state or project skills")
    if docs_refs > 10:
        warnings.append(f"{path}: {docs_refs} docs/ references; move docs inventories to current-state or project-navigation skills")
    if command_lines > 10:
        warnings.append(f"{path}: {command_lines} command lines; move task-specific validation matrices to project skills")

    return issues, warnings


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


def check_construct_boundaries(root: Path) -> list[str]:
    warnings: list[str] = []
    construct_root = root / "docs" / "construct"
    if not construct_root.exists():
        return warnings

    for doc in sorted(construct_root.rglob("*.md")):
        if CURRENT_STATE_NAME_RE.search(doc.stem):
            warnings.append(
                f"{doc}: current-state entrypoint appears to be under docs/construct; "
                "prefer docs/productization/codebase-current-state.md or docs/codebase-current-state.md"
            )

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    issues: list[str] = []
    warnings: list[str] = []

    agents = root / "AGENTS.md"
    if agents.exists():
        agent_issues, agent_warnings = check_agents(agents)
        issues.extend(agent_issues)
        warnings.extend(agent_warnings)

    skills_root = root / ".agents" / "skills"
    if skills_root.exists():
        for skill_md in sorted(skills_root.glob("*/SKILL.md")):
            issues.extend(check_skill(skill_md))

    warnings.extend(check_construct_boundaries(root))

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
        if warnings:
            print("Vento validation warnings:")
            for warning in warnings:
                print(f"- {warning}")
        return 1

    if warnings:
        print("Vento validation passed with warnings:")
        for warning in warnings:
            print(f"- {warning}")
        return 0

    print("Vento validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
