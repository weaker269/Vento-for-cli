#!/usr/bin/env python3
"""Run lightweight structural checks for Vento project assets."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from architecture import (
    discover_authoritative_guidance,
    documentation_integration,
    find_manifest,
    validate_manifest,
    verification_status,
    view_budget,
)
import flows


FRONTMATTER_RE = re.compile(r"^---\n(?P<body>.*?)\n---\n", re.DOTALL)
CURRENT_STATE_NAME_RE = re.compile(r"(?:^|[-_])(?:codebase-)?current-state(?:[-_]|$)", re.IGNORECASE)


def check_guidance(path: Path) -> tuple[list[str], list[str]]:
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
        warnings.append(f"{path}: {len(lines)} lines; project guidance may be carrying current-state detail")

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
    """Validate native-only guidance or a one-way bridge to the first host."""
    warnings: list[str] = []
    agents_skills = root / ".agents" / "skills"
    claude_skills = root / ".claude" / "skills"

    _, guidance_error = discover_authoritative_guidance(root)
    if guidance_error:
        warnings.append(f"{root}: {guidance_error}")

    agents_present = agents_skills.exists() or agents_skills.is_symlink()
    claude_present = claude_skills.exists() or claude_skills.is_symlink()
    if agents_present and claude_present:
        if agents_skills.is_symlink() and claude_skills.is_symlink():
            warnings.append(
                f"{root}: both project skill directories are symlinks; circular or missing authority is likely"
            )
        elif agents_skills.is_symlink():
            if agents_skills.resolve() != claude_skills.resolve():
                warnings.append(f"{agents_skills}: does not point to Claude Code's authoritative skills")
        elif claude_skills.is_symlink():
            if claude_skills.resolve() != agents_skills.resolve():
                warnings.append(f"{claude_skills}: does not point to Codex's authoritative skills")
        else:
            warnings.append(
                f"{root}: .agents/skills and .claude/skills are independent directories; "
                "reconcile split-brain explicitly"
            )
    elif agents_skills.is_symlink() and not agents_skills.exists():
        warnings.append(f"{agents_skills}: broken skill bridge")
    elif claude_skills.is_symlink() and not claude_skills.exists():
        warnings.append(f"{claude_skills}: broken skill bridge")

    return warnings


def project_skill_files(root: Path) -> list[Path]:
    """Return unique project skills from either host's authoritative directory."""
    files: dict[Path, Path] = {}
    for skills_root in (root / ".agents" / "skills", root / ".claude" / "skills"):
        if not skills_root.exists():
            continue
        for skill_md in sorted(skills_root.glob("*/SKILL.md")):
            files.setdefault(skill_md.resolve(), skill_md)
    return list(files.values())


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
    budget = view_budget(root, data)
    if isinstance(budget, dict) and "error" not in budget:
        for view, result in budget.items():
            for finding in result["budget_issues"]:
                warnings.append(f"{manifest}: view {view} exceeds density budget ({finding})")
    if data.get("status") == "active":
        verification = verification_status(issues, budget, data)
        for key in ("semantic_status", "render_status", "visual_status"):
            if verification[key] == "failed":
                issues.append(f"{manifest}: {key} is failed")
            elif verification[key] == "unverified":
                warnings.append(f"{manifest}: {key} is unverified")
    return issues, warnings


def check_flows(root: Path) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    manifest, data, parse_errors = flows.find_manifest(root)
    issues.extend(parse_errors)
    if manifest is None or data is None:
        return issues, warnings
    issues.extend(flows.validate_manifest(root, manifest, data))
    if not (manifest.parent / "README.md").exists():
        warnings.append(f"{manifest}: flow README.md is missing; add scope, scenarios, and provenance")
    integration = flows.documentation_integration(root, manifest, data)
    if not integration["configured"]:
        warnings.append(f"{manifest}: flows are not linked from a current-state/map document")
    for value in integration["missing"]:
        warnings.append(f"{manifest}: missing integration target {value}")
    for value in integration["unlinked"]:
        warnings.append(f"{manifest}: integration target does not link flow assets: {value}")
    if data.get("status") == "active":
        for asset_id, verification in flows.asset_verification(data).items():
            for key in ("render_status", "visual_status"):
                if verification[key] == "failed":
                    issues.append(f"{manifest}: flow asset {asset_id} {key} is failed")
                elif verification[key] == "unverified":
                    warnings.append(f"{manifest}: flow asset {asset_id} {key} is unverified")
    return issues, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    issues: list[str] = []
    warnings: list[str] = []

    for guidance in (root / "AGENTS.md", root / "CLAUDE.md"):
        if guidance.exists():
            guidance_issues, guidance_warnings = check_guidance(guidance)
            issues.extend(guidance_issues)
            warnings.extend(guidance_warnings)

    for skill_md in project_skill_files(root):
        issues.extend(check_skill(skill_md))

    warnings.extend(check_construct_boundaries(root))
    warnings.extend(check_cross_agent_bridge(root))
    architecture_issues, architecture_warnings = check_architecture(root)
    issues.extend(architecture_issues)
    warnings.extend(architecture_warnings)
    flow_issues, flow_warnings = check_flows(root)
    issues.extend(flow_issues)
    warnings.extend(flow_warnings)

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
