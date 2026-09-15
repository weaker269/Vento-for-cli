from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "vento" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import architecture
import validate_vento_project


class NativeFirstTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="vento-native-first-")
        self.project = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write(self, relative: str, content: str) -> None:
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_native_only_projects_keep_their_own_authority(self) -> None:
        cases = (
            ("AGENTS.md", "# Codex\n", "AGENTS.md"),
            ("CLAUDE.md", "# Claude Code\n", "CLAUDE.md"),
        )
        for path, content, expected in cases:
            with self.subTest(path=path):
                self.write(path, content)
                guidance, error = architecture.discover_authoritative_guidance(self.project)
                self.assertEqual(expected, guidance)
                self.assertIsNone(error)
                self.assertEqual([], validate_vento_project.check_cross_agent_bridge(self.project))
                (self.project / path).unlink()

    def test_codex_first_bridge_keeps_agents_authoritative(self) -> None:
        self.write("AGENTS.md", "# Codex\n")
        self.write("CLAUDE.md", "@AGENTS.md\n")

        guidance, error = architecture.discover_authoritative_guidance(self.project)

        self.assertEqual("AGENTS.md", guidance)
        self.assertIsNone(error)
        self.assertEqual([], validate_vento_project.check_cross_agent_bridge(self.project))

    def test_claude_first_bridge_keeps_claude_authoritative(self) -> None:
        self.write("CLAUDE.md", "# Claude Code\n")
        self.write(
            "AGENTS.md",
            "<!-- vento-bridge: authoritative=CLAUDE.md -->\nRead and follow `CLAUDE.md`.\n",
        )

        guidance, error = architecture.discover_authoritative_guidance(self.project)

        self.assertEqual("CLAUDE.md", guidance)
        self.assertIsNone(error)
        self.assertEqual([], validate_vento_project.check_cross_agent_bridge(self.project))

    def test_independent_guidance_is_reported_as_split_brain(self) -> None:
        self.write("AGENTS.md", "# Codex\n")
        self.write("CLAUDE.md", "# Claude Code\n")

        guidance, error = architecture.discover_authoritative_guidance(self.project)

        self.assertIsNone(guidance)
        self.assertIn("independent guidance", error)
        warnings = validate_vento_project.check_cross_agent_bridge(self.project)
        self.assertTrue(any("independent guidance" in warning for warning in warnings))

    def test_claude_native_architecture_uses_claude_assets(self) -> None:
        self.write("CLAUDE.md", "# Claude Code\n")
        self.write(".claude/skills/drawio-skill/scripts/diagramctl.py", "# tool\n")
        args = argparse.Namespace(
            diagram="docs/construct/architecture/system.drawio",
            model="docs/construct/architecture/system.ir.json",
            curated_model=None,
            source=[],
            kind="javascript",
            view=[],
            engine_version="3.4.0",
            current_state=None,
            construct_index=None,
            guidance=None,
            agents=None,
        )

        result = architecture.init_manifest(self.project, args)

        self.assertEqual(0, result)
        manifest_path = self.project / "docs/construct/architecture/architecture.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual("CLAUDE.md", manifest["integration"]["guidance"])
        locations = architecture.drawio_skill_locations(self.project)
        self.assertTrue(any(".claude/skills/drawio-skill" in path for path in locations))


if __name__ == "__main__":
    unittest.main()
