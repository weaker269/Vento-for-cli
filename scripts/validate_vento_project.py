#!/usr/bin/env python3
"""Compatibility entrypoint for the Vento validation script."""

from __future__ import annotations

import runpy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "vento" / "scripts" / "validate_vento_project.py"


if __name__ == "__main__":
    runpy.run_path(str(SCRIPT), run_name="__main__")
