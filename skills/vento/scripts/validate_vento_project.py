#!/usr/bin/env python3
"""Run lightweight structural checks for Vento project assets."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from architecture import diagram_metrics, documentation_integration, find_manifest, validate_manifest


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


def check_cross_agent_bridge(root: Path) -> list[str]:
    """Warn when Claude Code cannot auto-load AGENTS.md or discover .agents/skills."""
    warnings: list[str] = []
    claude_md = root / "CLAUDE.md"
    claude_skills = root / ".claude" / "skills"

    if (root / "AGENTS.md").exists():
        if not claude_md.exists():
            warnings.append(
                f"{claude_md}: missing; create an `@AGENTS.md` import stub so Claude Code auto-loads AGENTS.md"
            )
        elif "@AGENTS.md" not in claude_md.read_text():
            warnings.append(
                f"{claude_md}: lacks the `@AGENTS.md` import; Claude Code will not auto-load AGENTS.md"
            )

    if (root / ".agents" / "skills").exists():
        if claude_skills.is_symlink():
            pass
        elif claude_skills.is_dir():
            warnings.append(
                f"{claude_skills}: real directory, not a bridge symlink; may diverge from .agents/skills"
            )
        else:
            warnings.append(
                f"{claude_skills}: missing; symlink to ../.agents/skills so Claude Code discovers project skills"
            )

    return warnings


def check_architecture(root: Path) -> tuple[list[str], list[str]]:
    """Validate opt-in architecture manifests without requiring draw.io."""
    issues: list[str] = []
    warnings: list[str] = []
    manifest, data, parse_errors = find_manifest(root)
    issues.extend(parse_errors)
    if manifest is None or data is None:
        return issues, warnings
    issues.extend(validate_manifest(root, manifest, data))
    if not (manifest.parent / "README.md").exists():
        warnings.append(
            f"{manifest}: architecture README.md is missing; add a human-facing scope and provenance entry"
        )
    integration = documentation_integration(root, manifest, data)
    if not integration["configured"]:
        warnings.append(
            f"{manifest}: architecture is not linked from a current-state/map document"
        )
    for value in integration["missing"]:
        warnings.append(f"{manifest}: missing integration target {value}")
    for value in integration["unlinked"]:
        warnings.append(f"{manifest}: integration target does not link architecture assets: {value}")
    metrics = diagram_metrics(root, data)
    if isinstance(metrics, dict) and "error" not in metrics:
        for view, result in metrics.items():
            for finding in result["readability_issues"]:
                warnings.append(f"{manifest}: view {view} exceeds readability contract ({finding})")
    return issues, warnings


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
    warnings.extend(check_cross_agent_bridge(root))
    architecture_issues, architecture_warnings = check_architecture(root)
    issues.extend(architecture_issues)
    warnings.extend(architecture_warnings)

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
