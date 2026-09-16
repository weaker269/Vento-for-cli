from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "vento" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import architecture
import flows
import validate_vento_project


class DiagramLifecycleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="vento-diagrams-")
        self.project = Path(self.temp_dir.name)
        (self.project / "src").mkdir()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write(self, relative: str, content: str) -> None:
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_json(self, relative: str, value: dict) -> None:
        self.write(relative, json.dumps(value, ensure_ascii=False, indent=2) + "\n")

    def test_architecture_budget_is_not_reported_as_readability(self) -> None:
        self.write(
            "docs/construct/architecture/system.drawio",
            '<mxfile><diagram id="context" name="Context"><mxGraphModel><root>'
            '<mxCell id="0"/><mxCell id="1" parent="0"/>'
            '<mxCell id="service" vertex="1" parent="1"/>'
            '</root></mxGraphModel></diagram></mxfile>',
        )
        self.write_json(
            "docs/construct/architecture/architecture.json",
            {
                "schema": architecture.SCHEMA,
                "status": "active",
                "diagram": "docs/construct/architecture/system.drawio",
                "sources": [{"path": "src", "kind": "python"}],
                "views": ["context"],
                "view_contracts": [{"id": "context", "max_nodes": 8, "max_edges": 12}],
                "engine": {"name": "drawio-skill", "version": "3.4.0"},
            },
        )

        result = architecture.status(self.project)

        self.assertNotIn("readability", result)
        self.assertEqual([], result["view_budget"]["Context"]["budget_issues"])
        self.assertEqual("passed", result["verification"]["structural_status"])
        self.assertEqual("unverified", result["verification"]["render_status"])
        self.assertEqual("unverified", result["verification"]["visual_status"])

    def test_flow_model_renders_flowchart_sequence_and_state(self) -> None:
        model = {
            "schema": flows.MODEL_SCHEMA,
            "scenarios": [
                {
                    "id": "overview",
                    "title": "Overview",
                    "type": "flowchart",
                    "question": "How does the request complete?",
                    "audience": ["maintainers"],
                    "status": "current",
                    "evidence": ["src"],
                    "direction": "LR",
                    "phases": [{"id": "run", "label": "Run"}],
                    "steps": [
                        {"id": "start", "label": "Receive", "kind": "start", "phase": "run"},
                        {"id": "choose", "label": "Use tool?", "kind": "decision", "phase": "run"},
                        {"id": "done", "label": "Return", "kind": "end", "phase": "run"},
                    ],
                    "transitions": [
                        {"from": "start", "to": "choose"},
                        {"from": "choose", "to": "done", "label": "no"},
                    ],
                },
                {
                    "id": "call-tool",
                    "title": "Call tool",
                    "type": "sequence",
                    "question": "Who calls the provider?",
                    "audience": ["maintainers"],
                    "status": "current",
                    "evidence": ["src"],
                    "participants": [
                        {"id": "api", "label": "API"},
                        {"id": "provider", "label": "Provider"},
                    ],
                    "messages": [
                        {"from": "api", "to": "provider", "label": "invoke", "kind": "sync"},
                        {"from": "provider", "to": "api", "label": "result", "kind": "return"},
                    ],
                },
                {
                    "id": "job-state",
                    "title": "Job state",
                    "type": "state",
                    "question": "How does a job finish?",
                    "audience": ["maintainers"],
                    "status": "current",
                    "evidence": ["src"],
                    "states": [
                        {"id": "queued", "label": "Queued", "initial": True},
                        {"id": "finished", "label": "Finished", "terminal": True},
                    ],
                    "transitions": [{"from": "queued", "to": "finished", "label": "complete"}],
                },
            ],
        }
        assets = [
            self.asset("overview", "flowchart"),
            self.asset("call-tool", "sequence"),
            self.asset("job-state", "state"),
        ]
        manifest = {
            "schema": flows.SCHEMA,
            "status": "active",
            "model": "docs/construct/flows/flow-model.json",
            "sources": [{"path": "src", "kind": "python"}],
            "assets": assets,
        }
        self.write_json("docs/construct/flows/flow-model.json", model)
        self.write_json("docs/construct/flows/flows.json", manifest)
        self.write("docs/construct/flows/README.md", "# Flows\n")

        self.assertEqual(0, flows.render(self.project))

        overview = (self.project / assets[0]["diagram"]).read_text()
        sequence = (self.project / assets[1]["diagram"]).read_text()
        state = (self.project / assets[2]["diagram"]).read_text()
        self.assertIn("flowchart LR", overview)
        self.assertIn('choose{"Use tool?"}', overview)
        self.assertIn("sequenceDiagram", sequence)
        self.assertIn("provider-->>api: result", sequence)
        self.assertIn("stateDiagram-v2", state)
        self.assertIn("[*] --> queued", state)
        self.assertEqual([], flows.validate_manifest(self.project, self.project / "docs/construct/flows/flows.json", manifest))

        issues, warnings = validate_vento_project.check_flows(self.project)
        self.assertEqual([], issues)
        self.assertTrue(any("render_status is unverified" in warning for warning in warnings))
        self.assertTrue(any("visual_status is unverified" in warning for warning in warnings))

    def test_flow_validation_rejects_unknown_transition_step(self) -> None:
        path = self.project / "flow-model.json"
        model = {
            "schema": flows.MODEL_SCHEMA,
            "scenarios": [
                {
                    "id": "broken",
                    "title": "Broken",
                    "type": "flowchart",
                    "question": "What is broken?",
                    "audience": ["maintainers"],
                    "status": "current",
                    "evidence": ["src"],
                    "steps": [
                        {"id": "start", "label": "Start", "kind": "start"},
                        {"id": "end", "label": "End", "kind": "end"},
                    ],
                    "transitions": [{"from": "start", "to": "missing"}],
                }
            ],
        }

        issues = flows.validate_model(path, model)

        self.assertTrue(any("unknown step" in issue for issue in issues))

    @staticmethod
    def asset(scenario: str, scenario_type: str) -> dict:
        return {
            "id": scenario,
            "scenario": scenario,
            "type": scenario_type,
            "diagram": f"docs/construct/flows/{scenario}.mmd",
            "renderer": {"name": "mermaid"},
            "verification": {
                "render": {"status": "unverified", "artifact": None},
                "visual_review": {"status": "unverified", "reviewed_at": None},
            },
        }


if __name__ == "__main__":
    unittest.main()
