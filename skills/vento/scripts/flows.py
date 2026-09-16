#!/usr/bin/env python3
"""Inspect, render, and classify opt-in Vento flow assets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from architecture import changed_files, repo_path


SCHEMA = "vento/flows/v1"
MODEL_SCHEMA = "vento/flow-model/v1"
DEFAULT_MANIFESTS = (
    Path("docs/construct/flows/flows.json"),
    Path("docs/flows/flows.json"),
    Path(".vento/flows.json"),
)
SCENARIO_TYPES = {"flowchart", "sequence", "state"}
STEP_KINDS = {"start", "process", "decision", "store", "end"}
MESSAGE_KINDS = {"sync", "async", "return", "error"}
VERIFICATION_STATUSES = {"unverified", "passed", "failed"}


def find_manifest(root: Path) -> tuple[Path | None, dict | None, list[str]]:
    errors: list[str] = []
    for relative in DEFAULT_MANIFESTS:
        path = root / relative
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: cannot read JSON ({exc})")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path}: manifest root must be an object")
            continue
        return path, data, errors
    return None, None, errors


def load_model(root: Path, data: dict) -> tuple[Path | None, dict | None, list[str]]:
    value = data.get("model")
    if not isinstance(value, str):
        return None, None, ["flow manifest model must be a repository-relative string"]
    try:
        path = repo_path(root, value)
    except ValueError as exc:
        return None, None, [str(exc)]
    if not path.exists():
        return path, None, [f"missing flow model {value}"]
    try:
        model = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return path, None, [f"{path}: cannot read JSON ({exc})"]
    if not isinstance(model, dict):
        return path, None, [f"{path}: model root must be an object"]
    return path, model, []


def validate_references(path: Path, items: list, fields: tuple[str, ...], label: str) -> tuple[list[str], set[str]]:
    issues: list[str] = []
    ids: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            issues.append(f"{path}: {label}[{index}] must be an object")
            continue
        missing = [field for field in fields if not isinstance(item.get(field), str) or not item[field]]
        if missing:
            issues.append(f"{path}: {label}[{index}] requires string fields {', '.join(fields)}")
            continue
        ids.append(item["id"])
    if len(set(ids)) != len(ids):
        issues.append(f"{path}: {label} ids must be unique")
    return issues, set(ids)


def validate_scenario(path: Path, index: int, scenario: dict) -> list[str]:
    issues: list[str] = []
    prefix = f"{path}: scenarios[{index}]"
    for field in ("id", "title", "type", "question"):
        if not isinstance(scenario.get(field), str) or not scenario[field]:
            issues.append(f"{prefix}.{field} must be a non-empty string")
    scenario_type = scenario.get("type")
    if scenario_type not in SCENARIO_TYPES:
        issues.append(f"{prefix}.type must be flowchart, sequence, or state")
        return issues
    audience = scenario.get("audience")
    if not isinstance(audience, list) or not audience or not all(isinstance(value, str) for value in audience):
        issues.append(f"{prefix}.audience must be a non-empty string list")
    if scenario.get("status") not in {"current", "proposed"}:
        issues.append(f"{prefix}.status must be current or proposed")
    evidence = scenario.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(value, str) for value in evidence):
        issues.append(f"{prefix}.evidence must be a non-empty string list")

    if scenario_type == "flowchart":
        steps = scenario.get("steps")
        if not isinstance(steps, list) or not steps:
            issues.append(f"{prefix}.steps must be a non-empty list")
            return issues
        step_issues, step_ids = validate_references(path, steps, ("id", "label", "kind"), f"scenarios[{index}].steps")
        issues.extend(step_issues)
        kinds = {step.get("kind") for step in steps if isinstance(step, dict)}
        invalid_kinds = sorted(str(kind) for kind in kinds if kind not in STEP_KINDS)
        if invalid_kinds:
            issues.append(f"{prefix} contains invalid step kinds: {', '.join(invalid_kinds)}")
        if "start" not in kinds or "end" not in kinds:
            issues.append(f"{prefix} must contain start and end steps")
        phases = scenario.get("phases", [])
        phase_ids: set[str] = set()
        if not isinstance(phases, list):
            issues.append(f"{prefix}.phases must be a list")
        else:
            phase_issues, phase_ids = validate_references(
                path, phases, ("id", "label"), f"scenarios[{index}].phases"
            )
            issues.extend(phase_issues)
        for step_index, step in enumerate(steps):
            if isinstance(step, dict) and step.get("phase") is not None and step.get("phase") not in phase_ids:
                issues.append(f"{prefix}.steps[{step_index}] references an unknown phase")
        transitions = scenario.get("transitions")
        if not isinstance(transitions, list) or not transitions:
            issues.append(f"{prefix}.transitions must be a non-empty list")
        else:
            for transition_index, transition in enumerate(transitions):
                if not isinstance(transition, dict):
                    issues.append(f"{prefix}.transitions[{transition_index}] must be an object")
                    continue
                if transition.get("from") not in step_ids or transition.get("to") not in step_ids:
                    issues.append(f"{prefix}.transitions[{transition_index}] references an unknown step")

    if scenario_type == "sequence":
        participants = scenario.get("participants")
        if not isinstance(participants, list) or not participants:
            issues.append(f"{prefix}.participants must be a non-empty list")
            return issues
        participant_issues, participant_ids = validate_references(
            path, participants, ("id", "label"), f"scenarios[{index}].participants"
        )
        issues.extend(participant_issues)
        messages = scenario.get("messages")
        if not isinstance(messages, list) or not messages:
            issues.append(f"{prefix}.messages must be a non-empty list")
        else:
            for message_index, message in enumerate(messages):
                if not isinstance(message, dict):
                    issues.append(f"{prefix}.messages[{message_index}] must be an object")
                    continue
                if message.get("from") not in participant_ids or message.get("to") not in participant_ids:
                    issues.append(f"{prefix}.messages[{message_index}] references an unknown participant")
                if not isinstance(message.get("label"), str) or not message["label"]:
                    issues.append(f"{prefix}.messages[{message_index}].label must be a non-empty string")
                if message.get("kind", "sync") not in MESSAGE_KINDS:
                    issues.append(f"{prefix}.messages[{message_index}].kind is invalid")

    if scenario_type == "state":
        states = scenario.get("states")
        if not isinstance(states, list) or not states:
            issues.append(f"{prefix}.states must be a non-empty list")
            return issues
        state_issues, state_ids = validate_references(path, states, ("id", "label"), f"scenarios[{index}].states")
        issues.extend(state_issues)
        if not any(state.get("initial") is True for state in states if isinstance(state, dict)):
            issues.append(f"{prefix} must contain an initial state")
        if not any(state.get("terminal") is True for state in states if isinstance(state, dict)):
            issues.append(f"{prefix} must contain a terminal state")
        transitions = scenario.get("transitions")
        if not isinstance(transitions, list):
            issues.append(f"{prefix}.transitions must be a list")
        else:
            for transition_index, transition in enumerate(transitions):
                if not isinstance(transition, dict):
                    issues.append(f"{prefix}.transitions[{transition_index}] must be an object")
                    continue
                if transition.get("from") not in state_ids or transition.get("to") not in state_ids:
                    issues.append(f"{prefix}.transitions[{transition_index}] references an unknown state")
    return issues


def validate_model(path: Path, model: dict) -> list[str]:
    issues: list[str] = []
    if model.get("schema") != MODEL_SCHEMA:
        issues.append(f"{path}: schema must be {MODEL_SCHEMA}")
    scenarios = model.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return issues + [f"{path}: scenarios must be a non-empty list"]
    ids: list[str] = []
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            issues.append(f"{path}: scenarios[{index}] must be an object")
            continue
        if isinstance(scenario.get("id"), str):
            ids.append(scenario["id"])
        issues.extend(validate_scenario(path, index, scenario))
    if len(set(ids)) != len(ids):
        issues.append(f"{path}: scenario ids must be unique")
    return issues


def validate_verification(root: Path, manifest_path: Path, asset: dict, index: int) -> list[str]:
    issues: list[str] = []
    verification = asset.get("verification", {})
    if not isinstance(verification, dict):
        return [f"{manifest_path}: assets[{index}].verification must be an object"]
    for key in ("render", "visual_review"):
        item = verification.get(key, {"status": "unverified"})
        if not isinstance(item, dict) or item.get("status", "unverified") not in VERIFICATION_STATUSES:
            issues.append(
                f"{manifest_path}: assets[{index}].verification.{key}.status must be unverified, passed, or failed"
            )
    render = verification.get("render", {})
    if isinstance(render, dict) and render.get("status") == "passed":
        artifact = render.get("artifact")
        if not isinstance(artifact, str):
            issues.append(f"{manifest_path}: passed render verification requires artifact")
        else:
            try:
                artifact_path = repo_path(root, artifact)
            except ValueError as exc:
                issues.append(f"{manifest_path}: {exc}")
            else:
                if not artifact_path.exists():
                    issues.append(f"{manifest_path}: missing rendered artifact {artifact}")
    visual = verification.get("visual_review", {})
    if isinstance(visual, dict) and visual.get("status") == "passed":
        if not isinstance(visual.get("reviewed_at"), str):
            issues.append(f"{manifest_path}: passed visual review requires reviewed_at")
        if not isinstance(render, dict) or render.get("status") != "passed":
            issues.append(f"{manifest_path}: passed visual review requires passed render verification")
    return issues


def validate_component_references(path: Path, model: dict, component_ids: set[str]) -> list[str]:
    issues: list[str] = []
    for scenario_index, scenario in enumerate(model.get("scenarios", [])):
        if not isinstance(scenario, dict):
            continue
        fields = ("steps", "participants", "states")
        for field in fields:
            for item_index, item in enumerate(scenario.get(field, [])):
                if not isinstance(item, dict) or item.get("component") is None:
                    continue
                if item["component"] not in component_ids:
                    issues.append(
                        f"{path}: scenarios[{scenario_index}].{field}[{item_index}] "
                        f"references unknown architecture component {item['component']}"
                    )
    return issues


def validate_manifest(root: Path, path: Path, data: dict, require_diagrams: bool = True) -> list[str]:
    issues: list[str] = []
    if data.get("schema") != SCHEMA:
        issues.append(f"{path}: schema must be {SCHEMA}")
    if data.get("status") not in {"active", "disabled"}:
        issues.append(f"{path}: status must be active or disabled")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        issues.append(f"{path}: sources must be a non-empty list")
    else:
        for index, source in enumerate(sources):
            value = source.get("path") if isinstance(source, dict) else source
            if not isinstance(value, str):
                issues.append(f"{path}: sources[{index}].path must be a string")
                continue
            try:
                source_path = repo_path(root, value)
            except ValueError as exc:
                issues.append(f"{path}: sources[{index}]: {exc}")
                continue
            if not source_path.exists():
                issues.append(f"{path}: missing source path {value}")

    model_path, model, model_errors = load_model(root, data)
    issues.extend(f"{path}: {error}" for error in model_errors)
    scenario_types: dict[str, str] = {}
    if model_path and model:
        issues.extend(validate_model(model_path, model))
        scenario_types = {
            scenario["id"]: scenario.get("type")
            for scenario in model.get("scenarios", [])
            if isinstance(scenario, dict) and isinstance(scenario.get("id"), str)
        }

    architecture_model = data.get("architecture_model")
    component_ids: set[str] | None = None
    if architecture_model is not None:
        if not isinstance(architecture_model, str):
            issues.append(f"{path}: architecture_model must be a repository-relative string")
        else:
            try:
                architecture_path = repo_path(root, architecture_model)
            except ValueError as exc:
                issues.append(f"{path}: {exc}")
            else:
                if not architecture_path.exists():
                    issues.append(f"{path}: missing architecture model {architecture_model}")
                else:
                    try:
                        architecture_data = json.loads(architecture_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError) as exc:
                        issues.append(f"{path}: cannot read architecture model ({exc})")
                    else:
                        components = architecture_data.get("components") if isinstance(architecture_data, dict) else None
                        if not isinstance(components, list):
                            issues.append(f"{path}: architecture model components must be a list")
                        else:
                            component_ids = {
                                component["id"]
                                for component in components
                                if isinstance(component, dict) and isinstance(component.get("id"), str)
                            }
    if model_path and model and component_ids is not None:
        issues.extend(validate_component_references(model_path, model, component_ids))

    integration = data.get("integration")
    if integration is not None and not isinstance(integration, dict):
        issues.append(f"{path}: integration must be an object")

    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        issues.append(f"{path}: assets must be a non-empty list")
        return issues
    asset_ids: list[str] = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            issues.append(f"{path}: assets[{index}] must be an object")
            continue
        for field in ("id", "scenario", "type", "diagram"):
            if not isinstance(asset.get(field), str) or not asset[field]:
                issues.append(f"{path}: assets[{index}].{field} must be a non-empty string")
        asset_id = asset.get("id")
        if isinstance(asset_id, str):
            asset_ids.append(asset_id)
        scenario_id = asset.get("scenario")
        if scenario_id not in scenario_types:
            issues.append(f"{path}: assets[{index}] references unknown scenario {scenario_id}")
        elif asset.get("type") != scenario_types[scenario_id]:
            issues.append(f"{path}: assets[{index}].type must match scenario type {scenario_types[scenario_id]}")
        renderer = asset.get("renderer")
        if not isinstance(renderer, dict) or renderer.get("name") != "mermaid":
            issues.append(f"{path}: assets[{index}].renderer.name must be mermaid")
        diagram = asset.get("diagram")
        if isinstance(diagram, str):
            try:
                diagram_path = repo_path(root, diagram)
            except ValueError as exc:
                issues.append(f"{path}: {exc}")
            else:
                if not diagram.lower().endswith(".mmd"):
                    issues.append(f"{path}: assets[{index}].diagram must end with .mmd")
                if require_diagrams and not diagram_path.exists():
                    issues.append(f"{path}: missing Mermaid diagram {diagram}")
        issues.extend(validate_verification(root, path, asset, index))
    if len(set(asset_ids)) != len(asset_ids):
        issues.append(f"{path}: asset ids must be unique")
    return issues


def documentation_integration(root: Path, manifest_path: Path, data: dict) -> dict:
    integration = data.get("integration", {})
    if not isinstance(integration, dict):
        return {"configured": False, "targets": {}, "missing": [], "unlinked": []}
    manifest_ref = str(manifest_path.relative_to(root))
    directory_ref = f"{manifest_path.parent.relative_to(root)}/"
    diagram_refs = [asset.get("diagram") for asset in data.get("assets", []) if isinstance(asset, dict)]
    targets: dict[str, str] = {}
    missing: list[str] = []
    unlinked: list[str] = []
    for key in ("current_state", "construct_index", "guidance"):
        value = integration.get(key)
        if not isinstance(value, str):
            continue
        targets[key] = value
        try:
            target = repo_path(root, value)
        except ValueError:
            missing.append(value)
            continue
        if not target.exists():
            missing.append(value)
            continue
        text = target.read_text(encoding="utf-8", errors="ignore")
        if manifest_ref not in text and directory_ref not in text and not any(
            isinstance(diagram, str) and diagram in text for diagram in diagram_refs
        ):
            unlinked.append(value)
    return {"configured": bool(targets), "targets": targets, "missing": missing, "unlinked": unlinked}


def source_paths(data: dict) -> list[str]:
    result: list[str] = []
    for source in data.get("sources", []):
        value = source.get("path") if isinstance(source, dict) else source
        if isinstance(value, str):
            result.append(value.rstrip("/"))
    architecture_model = data.get("architecture_model")
    if isinstance(architecture_model, str):
        result.append(architecture_model)
    return result


def classify(path: str, sources: list[str]) -> str:
    normalized = path.replace("\\", "/").lstrip("./")
    if (
        normalized.startswith("docs/construct/flows/")
        or normalized.startswith("docs/flows/")
        or normalized.startswith(".vento/flows")
    ):
        return "flow_asset_change"
    if any(
        source in {"", "."} or normalized == source or normalized.startswith(f"{source}/")
        for source in sources
    ):
        return "potentially_flow_impacting"
    return "unrelated_or_requires_review"


def asset_verification(data: dict) -> dict:
    result: dict[str, dict] = {}
    for asset in data.get("assets", []):
        if not isinstance(asset, dict) or not isinstance(asset.get("id"), str):
            continue
        verification = asset.get("verification", {})
        if not isinstance(verification, dict):
            verification = {}
        render = verification.get("render", {})
        visual = verification.get("visual_review", {})
        result[asset["id"]] = {
            "render_status": render.get("status", "unverified") if isinstance(render, dict) else "failed",
            "visual_status": visual.get("status", "unverified") if isinstance(visual, dict) else "failed",
        }
    return result


def status(root: Path) -> dict:
    manifest_path, manifest, errors = find_manifest(root)
    result = {
        "root": str(root),
        "initialized": manifest_path is not None,
        "manifest": str(manifest_path.relative_to(root)) if manifest_path else None,
        "errors": errors,
    }
    if manifest_path and manifest:
        result["manifest_issues"] = validate_manifest(root, manifest_path, manifest)
        result["documentation_integration"] = documentation_integration(root, manifest_path, manifest)
        result["verification"] = asset_verification(manifest)
        result["model"] = manifest.get("model")
        result["assets"] = manifest.get("assets", [])
    return result


def check(root: Path, base_ref: str | None = None) -> dict:
    result = status(root)
    files, git_error = changed_files(root, base_ref)
    result["base_ref"] = base_ref
    result["changed_files"] = files
    result["git_error"] = git_error
    if not result["initialized"]:
        result["requires_render"] = False
        result["requires_documentation_update"] = False
        result["reason"] = "flow maintenance is not initialized"
        return result
    manifest_path, manifest, _ = find_manifest(root)
    classified = {path: classify(path, source_paths(manifest or {})) for path in files}
    result["classification"] = classified
    result["potentially_flow_impacting"] = [
        path for path, kind in classified.items() if kind == "potentially_flow_impacting"
    ]
    result["flow_asset_changes"] = [
        path for path, kind in classified.items() if kind == "flow_asset_change"
    ]
    result["requires_render"] = bool(result["potentially_flow_impacting"])
    result["requires_flow_review"] = bool(
        result["potentially_flow_impacting"] or result["flow_asset_changes"]
    )
    integration = result.get("documentation_integration", {})
    result["requires_documentation_update"] = bool(
        not integration.get("configured") or integration.get("missing") or integration.get("unlinked")
    )
    result["reason"] = (
        "review flow-impacting changes and update affected scenarios"
        if result["requires_render"]
        else "review flow asset changes"
        if result["flow_asset_changes"]
        else "no configured flow source changed"
    )
    result["manifest"] = str(manifest_path.relative_to(root)) if manifest_path else None
    return result


def mermaid_id(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value)
    return result if not result[:1].isdigit() else f"n_{result}"


def mermaid_label(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("\n", "<br/>")


def render_flowchart(scenario: dict) -> str:
    direction = scenario.get("direction", "LR")
    lines = [f"flowchart {direction}"]
    steps = scenario["steps"]
    phases = scenario.get("phases", [])
    rendered: set[str] = set()

    def render_step(step: dict, indent: str = "    ") -> None:
        node = mermaid_id(step["id"])
        label = mermaid_label(step["label"])
        shape = {
            "start": f'{node}(["{label}"])',
            "end": f'{node}(["{label}"])',
            "decision": f'{node}{{"{label}"}}',
            "store": f'{node}[("{label}")]',
        }.get(step["kind"], f'{node}["{label}"]')
        lines.append(f"{indent}{shape}")
        rendered.add(step["id"])

    for phase in phases:
        phase_id = mermaid_id(phase["id"])
        lines.append(f'    subgraph {phase_id}["{mermaid_label(phase["label"])}"]')
        for step in steps:
            if step.get("phase") == phase["id"]:
                render_step(step, "        ")
        lines.append("    end")
    for step in steps:
        if step["id"] not in rendered:
            render_step(step)

    for transition in scenario["transitions"]:
        source = mermaid_id(transition["from"])
        target = mermaid_id(transition["to"])
        label = transition.get("label")
        arrow = "-.->" if transition.get("kind") == "error" else "-->"
        if label:
            safe_label = mermaid_label(label).replace("|", "/")
            lines.append(f"    {source} {arrow}|{safe_label}| {target}")
        else:
            lines.append(f"    {source} {arrow} {target}")
    return "\n".join(lines) + "\n"


def render_sequence(scenario: dict) -> str:
    lines = ["sequenceDiagram"]
    for participant in scenario["participants"]:
        lines.append(
            f'    participant {mermaid_id(participant["id"])} as {mermaid_label(participant["label"])}'
        )
    arrows = {"return": "-->>", "async": "-)", "error": "--x"}
    for message in scenario["messages"]:
        arrow = arrows.get(message.get("kind"), "->>")
        lines.append(
            f'    {mermaid_id(message["from"])}{arrow}{mermaid_id(message["to"])}: '
            f'{mermaid_label(message["label"])}'
        )
    return "\n".join(lines) + "\n"


def render_state(scenario: dict) -> str:
    lines = ["stateDiagram-v2"]
    for state in scenario["states"]:
        lines.append(f'    state "{mermaid_label(state["label"])}" as {mermaid_id(state["id"])}')
    for state in scenario["states"]:
        if state.get("initial") is True:
            lines.append(f'    [*] --> {mermaid_id(state["id"])}')
    for transition in scenario["transitions"]:
        label = f' : {mermaid_label(transition["label"])}' if transition.get("label") else ""
        lines.append(
            f'    {mermaid_id(transition["from"])} --> {mermaid_id(transition["to"])}{label}'
        )
    for state in scenario["states"]:
        if state.get("terminal") is True:
            lines.append(f'    {mermaid_id(state["id"])} --> [*]')
    return "\n".join(lines) + "\n"


def render_scenario(scenario: dict) -> str:
    renderer = {
        "flowchart": render_flowchart,
        "sequence": render_sequence,
        "state": render_state,
    }[scenario["type"]]
    return renderer(scenario)


def render(root: Path, scenario_id: str | None = None) -> int:
    manifest_path, manifest, errors = find_manifest(root)
    if errors or manifest_path is None or manifest is None:
        for error in errors or ["flow maintenance is not initialized"]:
            print(error, file=sys.stderr)
        return 1
    issues = validate_manifest(root, manifest_path, manifest, require_diagrams=False)
    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        return 1
    _, model, _ = load_model(root, manifest)
    scenarios = {scenario["id"]: scenario for scenario in model["scenarios"]}
    selected = [asset for asset in manifest["assets"] if scenario_id in {None, asset["scenario"]}]
    if not selected:
        print(f"unknown scenario: {scenario_id}", file=sys.stderr)
        return 1
    for asset in selected:
        target = repo_path(root, asset["diagram"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_scenario(scenarios[asset["scenario"]]), encoding="utf-8")
        print(target)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "check", "render"))
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--base-ref", help="compare committed changes from BASE_REF...HEAD")
    parser.add_argument("--scenario", help="render one scenario id")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.command == "status":
        print(json.dumps(status(root), indent=2, ensure_ascii=False))
        return 0
    if args.command == "check":
        print(json.dumps(check(root, args.base_ref), indent=2, ensure_ascii=False))
        return 0
    return render(root, args.scenario)


if __name__ == "__main__":
    raise SystemExit(main())
