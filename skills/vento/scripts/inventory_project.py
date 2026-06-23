#!/usr/bin/env python3
"""Print a lightweight JSON inventory for a project."""

from __future__ import annotations

import json
from pathlib import Path


ROOT_MARKERS = [
    "AGENTS.md",
    "README.md",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "Makefile",
]

DOC_DIRS = ["docs", ".agents", ".github", "src", "tests", "test"]


def existing(paths: list[str], root: Path) -> list[str]:
    return [path for path in paths if (root / path).exists()]


def main() -> int:
    root = Path.cwd()
    files = existing(ROOT_MARKERS, root)
    dirs = existing(DOC_DIRS, root)
    scripts = {}

    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
            raw_scripts = data.get("scripts", {})
            if isinstance(raw_scripts, dict):
                scripts = {str(key): str(value) for key, value in raw_scripts.items()}
        except json.JSONDecodeError:
            scripts = {"_error": "package.json is not valid JSON"}

    print(
        json.dumps(
            {
                "root": str(root),
                "root_files": files,
                "directories": dirs,
                "package_scripts": scripts,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
