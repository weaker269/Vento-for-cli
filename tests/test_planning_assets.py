from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "vento" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import validate_vento_project


class PlanningAssetsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="vento-planning-")
        self.project = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write(self, relative: str, content: str) -> None:
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_roadmap_links_must_resolve(self) -> None:
        self.write("docs/productization/specs/2026-11-03-search.md", "# Spec\n\nStatus: Accepted\n")
        self.write(
            "docs/productization/active-roadmap.md",
            "\n".join(
                [
                    "# Active Roadmap",
                    "- Spec (optional): `docs/productization/specs/2026-11-03-search.md`",
                    "- Spec: `docs/productization/specs/YYYY-MM-DD-<topic>.md`",
                    "Plan: [实施计划](../productization/plans/2026-11-03-search-plan.md)",
                    "Parent Spec: [设计](specs/2026-11-03-search.md#decision)",
                    "- Spec (optional):",
                ]
            )
            + "\n",
        )

        issues, _ = validate_vento_project.check_planning_assets(self.project)

        self.assertEqual(1, len(issues))
        self.assertIn("../productization/plans/2026-11-03-search-plan.md", issues[0])

    def test_spec_status_must_be_recognized(self) -> None:
        self.write("docs/productization/specs/2026-11-03-ok.md", "# Spec\n\nStatus: `Implemented`\n")
        self.write("docs/productization/specs/2026-11-03-missing.md", "# Spec\n")
        self.write("docs/productization/specs/README.md", "# Specs\n")

        issues, warnings = validate_vento_project.check_planning_assets(self.project)

        self.assertEqual([], issues)
        self.assertEqual(1, len(warnings))
        self.assertIn("2026-11-03-missing.md", warnings[0])

    def test_legacy_planning_path_is_a_warning_not_a_failure(self) -> None:
        self.write("docs/superpowers/specs/2026-06-01-old-design.md", "# Old\n")
        self.write(
            "docs/productization/active-roadmap.md",
            "Spec: `docs/superpowers/specs/2026-06-01-old-design.md`\n",
        )

        issues, warnings = validate_vento_project.check_planning_assets(self.project)

        self.assertEqual([], issues)
        self.assertTrue(any("legacy tool-specific planning path" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
