#!/usr/bin/env python3
"""Validate Vento's Claude Code plugin package and marketplace metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: Path, errors: list[str]) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: cannot read JSON ({exc})")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: JSON root must be an object")
        return None
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = root / ".claude-plugin" / "plugin.json"
    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    skill_path = root / "skills" / "vento" / "SKILL.md"
    compatibility_files = (
        root / "skills" / "vento" / "references" / "claude-code.md",
        root / "skills" / "vento" / "assets" / "CLAUDE.template.md",
        root / "skills" / "vento" / "assets" / "CLAUDE.agents-bridge.template.md",
        root / "skills" / "vento" / "assets" / "AGENTS.claude-bridge.template.md",
    )
    manifest = read_json(manifest_path, errors) if manifest_path.exists() else None
    marketplace = read_json(marketplace_path, errors) if marketplace_path.exists() else None

    if not manifest_path.exists():
        errors.append(f"{manifest_path}: missing Claude plugin manifest")
    if not marketplace_path.exists():
        errors.append(f"{marketplace_path}: missing Claude marketplace manifest")
    if not skill_path.exists():
        errors.append(f"{skill_path}: missing Vento skill entrypoint")
    for path in compatibility_files:
        if not path.exists():
            errors.append(f"{path}: missing Claude Code compatibility asset")

    version = None
    if manifest is not None:
        if manifest.get("name") != "vento":
            errors.append(f"{manifest_path}: name must be vento")
        version = manifest.get("version")
        if not isinstance(version, str) or not version:
            errors.append(f"{manifest_path}: version must be a non-empty string")
        if "skills" in manifest:
            warnings.append(f"{manifest_path}: omit unsupported skills path overrides; use root skills/")

    if marketplace is not None:
        if marketplace.get("name") != "vento":
            errors.append(f"{marketplace_path}: name must be vento")
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list):
            errors.append(f"{marketplace_path}: plugins must be a list")
        else:
            entries = [item for item in plugins if isinstance(item, dict) and item.get("name") == "vento"]
            if len(entries) != 1:
                errors.append(f"{marketplace_path}: expected exactly one vento plugin entry")
            else:
                entry = entries[0]
                if entry.get("source") != "./":
                    errors.append(f"{marketplace_path}: vento source must be ./ for this repository marketplace")
                if version and entry.get("version") != version:
                    errors.append(f"{marketplace_path}: entry version must match plugin.json ({version})")

    if not (root / "README.md").exists():
        warnings.append(f"{root}: README.md is missing Claude Code installation guidance")
    else:
        readme = (root / "README.md").read_text(encoding="utf-8", errors="ignore")
        if "claude plugin marketplace" not in readme or "claude plugin update" not in readme:
            warnings.append(f"{root / 'README.md'}: incomplete Claude Code install/update guidance")
        if "Native-First Cross-Agent Support" not in readme:
            warnings.append(f"{root / 'README.md'}: native-first project guidance policy is undocumented")

    if errors:
        print("Claude Code plugin validation issues:")
        for error in errors:
            print(f"- {error}")
        if warnings:
            print("Claude Code plugin validation warnings:")
            for warning in warnings:
                print(f"- {warning}")
        return 1

    if warnings:
        print("Claude Code plugin validation passed with warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("Claude Code plugin validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
