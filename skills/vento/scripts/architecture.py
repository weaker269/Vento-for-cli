#!/usr/bin/env python3
"""Inspect and classify opt-in Vento architecture diagram maintenance."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SCHEMA = "vento/architecture/v1"
MODEL_SCHEMA = "vento/architecture-model/v1"
DEFAULT_MANIFESTS = (
    Path("docs/construct/architecture/architecture.json"),
    Path("docs/architecture/architecture.json"),
    Path(".vento/architecture.json"),
)
ARCHITECTURE_NAMES = {
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "openapi.yaml",
    "openapi.yml",
    "openapi.json",
    "schema.sql",
    "architecture.json",
}
ARCHITECTURE_DIRS = {
    ".github/workflows",
    "deploy",
    "deployment",
    "infra",
    "infrastructure",
    "k8s",
    "kubernetes",
    "migrations",
    "terraform",
}
CURRENT_STATE_CANDIDATES = (
    Path("docs/productization/codebase-current-state.md"),
    Path("docs/codebase-current-state.md"),
)
VIEW_LIMITS = {
    "executive": (8, 12),
    "system": (12, 20),
    "context": (8, 12),
    "container": (12, 20),
    "dynamic": (12, 20),
    "deployment": (14, 24),
    "dataflow": (14, 24),
    "security": (14, 24),
}
CLAUDE_AUTHORITY_MARKER = "vento-bridge: authoritative=CLAUDE.md"


def repo_path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"path must be repository-relative: {value}")
    return root / path


def discover_authoritative_guidance(root: Path) -> tuple[str | None, str | None]:
    agents_md = root / "AGENTS.md"
    claude_md = root / "CLAUDE.md"
    agents_exists = agents_md.exists()
    claude_exists = claude_md.exists()
    agents_text = agents_md.read_text(encoding="utf-8", errors="replace") if agents_exists else ""
    claude_text = claude_md.read_text(encoding="utf-8", errors="replace") if claude_exists else ""
    agents_to_claude = CLAUDE_AUTHORITY_MARKER in agents_text
    claude_to_agents = "@AGENTS.md" in claude_text

    if claude_to_agents and not agents_exists:
        return None, "CLAUDE.md imports missing AGENTS.md"
    if agents_to_claude and not claude_exists:
        return None, "AGENTS.md points to missing CLAUDE.md"

    if agents_exists and not claude_exists:
        return "AGENTS.md", None
    if claude_exists and not agents_exists:
        return "CLAUDE.md", None
    if not agents_exists and not claude_exists:
        return None, None

    if agents_to_claude and claude_to_agents:
        return None, "AGENTS.md and CLAUDE.md form a circular authority bridge"
    if agents_to_claude:
        return "CLAUDE.md", None
    if claude_to_agents:
        return "AGENTS.md", None
    return None, "AGENTS.md and CLAUDE.md contain independent guidance; resolve authority or pass --guidance"


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


def validate_curated_model(path: Path, model: dict) -> list[str]:
    issues: list[str] = []
    if model.get("schema") != MODEL_SCHEMA:
        issues.append(f"{path}: schema must be {MODEL_SCHEMA}")
    components = model.get("components")
    if not isinstance(components, list) or not components:
        issues.append(f"{path}: components must be a non-empty list")
    else:
        ids = [item.get("id") for item in components if isinstance(item, dict)]
        if len(ids) != len(components) or not all(isinstance(value, str) for value in ids):
            issues.append(f"{path}: every component must have a string id")
        if len(set(ids)) != len(ids):
            issues.append(f"{path}: component ids must be unique")
    relationships = model.get("relationships", [])
    if not isinstance(relationships, list):
        issues.append(f"{path}: relationships must be a list")
    else:
        for index, relationship in enumerate(relationships):
            if not isinstance(relationship, dict) or not all(
                isinstance(relationship.get(field), str) for field in ("id", "from", "to")
            ):
                issues.append(f"{path}: relationships[{index}] must contain id, from, and to strings")
    views = model.get("views")
    if not isinstance(views, list) or not views:
        issues.append(f"{path}: views must be a non-empty list")
    return issues


def validate_manifest(root: Path, path: Path, data: dict) -> list[str]:
    issues: list[str] = []
    if data.get("schema") != SCHEMA:
        issues.append(f"{path}: schema must be {SCHEMA}")
    if data.get("status") not in {"active", "disabled"}:
        issues.append(f"{path}: status must be active or disabled")

    for field, suffix in (("diagram", ".drawio"), ("model", ".json")):
        value = data.get(field)
        if value is None and field == "model":
            continue
        if not isinstance(value, str):
            issues.append(f"{path}: {field} must be a repository-relative string")
            continue
        try:
            target = repo_path(root, value)
        except ValueError as exc:
            issues.append(f"{path}: {exc}")
            continue
        if not value.lower().endswith(suffix):
            issues.append(f"{path}: {field} must end with {suffix}")
        if not target.exists():
            issues.append(f"{path}: missing {field} artifact {value}")

    sources = data.get("sources", [])
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

    views = data.get("views", [])
    if not isinstance(views, list) or not all(isinstance(view, (str, dict)) for view in views):
        issues.append(f"{path}: views must be a list of strings or view objects")

    engine = data.get("engine")
    if not isinstance(engine, dict) or engine.get("name") != "drawio-skill":
        issues.append(f"{path}: engine.name must be drawio-skill")

    integration = data.get("integration")
    if integration is not None and not isinstance(integration, dict):
        issues.append(f"{path}: integration must be an object")

    modeling = data.get("modeling")
    if modeling is not None:
        if not isinstance(modeling, dict) or modeling.get("source_of_truth") not in {"curated", "drawio_ir"}:
            issues.append(f"{path}: modeling.source_of_truth must be curated or drawio_ir")

    contracts = data.get("view_contracts")
    if contracts is not None:
        if not isinstance(contracts, list):
            issues.append(f"{path}: view_contracts must be a list")
        else:
            for index, contract in enumerate(contracts):
                if not isinstance(contract, dict) or not isinstance(contract.get("id"), str):
                    issues.append(f"{path}: view_contracts[{index}] must contain a string id")
                    continue
                for field in ("max_nodes", "max_edges"):
                    if field in contract and not isinstance(contract[field], int):
                        issues.append(f"{path}: view_contracts[{index}].{field} must be an integer")

    curated_model = data.get("curated_model")
    if isinstance(modeling, dict) and modeling.get("source_of_truth") == "curated" and not curated_model:
        issues.append(f"{path}: curated modeling requires curated_model")
    if curated_model is not None:
        if not isinstance(curated_model, str):
            issues.append(f"{path}: curated_model must be a repository-relative string")
        else:
            try:
                model_path = repo_path(root, curated_model)
            except ValueError as exc:
                issues.append(f"{path}: {exc}")
            else:
                if not model_path.exists():
                    issues.append(f"{path}: missing curated model {curated_model}")
                else:
                    try:
                        model = json.loads(model_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError) as exc:
                        issues.append(f"{path}: cannot read curated model ({exc})")
                    else:
                        if not isinstance(model, dict):
                            issues.append(f"{path}: curated model root must be an object")
                        else:
                            issues.extend(validate_curated_model(model_path, model))
    return issues


def changed_files(root: Path, base_ref: str | None = None) -> tuple[list[str], str | None]:
    if base_ref:
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            return [], f"cannot inspect Git diff from {base_ref} ({exc})"
        return sorted(line for line in result.stdout.splitlines() if line), None

    commands = [
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    values: set[str] = set()
    for command in commands:
        try:
            result = subprocess.run(
                command,
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            return [], f"cannot inspect Git working tree ({exc})"
        values.update(line for line in result.stdout.splitlines() if line)
    return sorted(values), None


def source_paths(data: dict) -> list[str]:
    result: list[str] = []
    for source in data.get("sources", []):
        value = source.get("path") if isinstance(source, dict) else source
        if isinstance(value, str):
            result.append(value.rstrip("/"))
    return result


def classify(path: str, sources: list[str]) -> str:
    normalized = path.replace("\\", "/").lstrip("./")
    if (
        normalized.startswith("docs/construct/architecture/")
        or normalized.startswith("docs/architecture/")
        or normalized.startswith(".vento/architecture")
    ):
        return "architecture_asset_change"
    if any(
        source in {"", "."}
        or normalized == source
        or normalized.startswith(f"{source}/")
        for source in sources
    ):
        return "potentially_architecture_impacting"
    if normalized in ARCHITECTURE_NAMES:
        return "potentially_architecture_impacting"
    if any(normalized == directory or normalized.startswith(f"{directory}/") for directory in ARCHITECTURE_DIRS):
        return "potentially_architecture_impacting"
    if "/migrations/" in f"/{normalized}/" or normalized.startswith("migrations/"):
        return "potentially_architecture_impacting"
    return "unrelated_or_requires_review"


def drawio_skill_locations(root: Path) -> list[str]:
    candidates = []
    environment = Path.home()
    configured = os.environ.get("DRAWIO_SKILL_DIR")
    paths = (
        Path(configured) / "scripts/diagramctl.py" if configured else None,
        root / ".agents/skills/drawio-skill/scripts/diagramctl.py",
        root / ".claude/skills/drawio-skill/scripts/diagramctl.py",
        environment / ".codex/skills/drawio-skill/scripts/diagramctl.py",
        environment / ".claude/skills/drawio-skill/scripts/diagramctl.py",
    )
    for path in paths:
        if path is None:
            continue
        if path.exists():
            candidates.append(str(path))
    return candidates


def documentation_integration(root: Path, manifest_path: Path, data: dict) -> dict:
    integration = data.get("integration", {})
    if not isinstance(integration, dict):
        return {"configured": False, "missing": [], "unlinked": [], "targets": {}}

    manifest_ref = str(manifest_path.relative_to(root))
    architecture_dir_ref = f"{manifest_path.parent.relative_to(root)}/"
    diagram_ref = data.get("diagram")
    targets: dict[str, str] = {}
    missing: list[str] = []
    unlinked: list[str] = []
    for key in ("current_state", "construct_index", "guidance", "agents"):
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
        if (
            manifest_ref not in text
            and architecture_dir_ref not in text
            and (not isinstance(diagram_ref, str) or diagram_ref not in text)
        ):
            unlinked.append(value)
    return {
        "configured": bool(targets),
        "targets": targets,
        "missing": missing,
        "unlinked": unlinked,
    }


def diagram_metrics(root: Path, data: dict) -> dict:
    diagram = data.get("diagram")
    if not isinstance(diagram, str):
        return {"error": "manifest diagram is not configured"}
    try:
        path = repo_path(root, diagram)
    except ValueError as exc:
        return {"error": str(exc)}
    if not path.exists():
        return {"error": f"missing diagram artifact {diagram}"}
    try:
        document = ET.parse(path)
    except (OSError, ET.ParseError) as exc:
        return {"error": f"cannot parse diagram ({exc})"}

    contracts = {}
    for contract in data.get("view_contracts") or []:
        if isinstance(contract, dict) and isinstance(contract.get("id"), str):
            contracts[contract["id"]] = contract
    pages: dict[str, dict] = {}
    for page in document.getroot().findall("diagram"):
        page_id = page.get("name") or page.get("id") or "unnamed"
        vertices = [cell for cell in page.findall(".//mxCell") if cell.get("vertex") == "1"]
        edges = [cell for cell in page.findall(".//mxCell") if cell.get("edge") == "1"]
        contract = contracts.get(page_id.lower(), {})
        defaults = VIEW_LIMITS.get(page_id.lower(), (None, None))
        max_nodes = contract.get("max_nodes", defaults[0])
        max_edges = contract.get("max_edges", defaults[1])
        over = []
        if isinstance(max_nodes, int) and len(vertices) > max_nodes:
            over.append(f"nodes {len(vertices)} > {max_nodes}")
        if isinstance(max_edges, int) and len(edges) > max_edges:
            over.append(f"edges {len(edges)} > {max_edges}")
        pages[page_id] = {
            "nodes": len(vertices),
            "edges": len(edges),
            "max_nodes": max_nodes,
            "max_edges": max_edges,
            "readability_issues": over,
        }
    return pages


def architecture_diagrams(root: Path) -> list[str]:
    prefixes = {
        ("docs", "construct", "architecture"),
        ("docs", "architecture"),
    }
    return sorted(
        str(relative)
        for path in root.rglob("*.drawio")
        for relative in [path.relative_to(root)]
        if ".git" not in relative.parts
        and "node_modules" not in relative.parts
        and any(relative.parts[: len(prefix)] == prefix for prefix in prefixes)
    )


def status(root: Path) -> dict:
    manifest_path, manifest, errors = find_manifest(root)
    diagrams = sorted(
        str(path.relative_to(root))
        for path in root.rglob("*.drawio")
        if ".git" not in path.parts and "node_modules" not in path.parts
    )
    result = {
        "root": str(root),
        "initialized": manifest_path is not None,
        "manifest": str(manifest_path.relative_to(root)) if manifest_path else None,
        "diagrams": diagrams,
        "architecture_diagrams": architecture_diagrams(root),
        "drawio_skill": drawio_skill_locations(root),
        "errors": errors,
    }
    if manifest_path and manifest:
        result["manifest_issues"] = validate_manifest(root, manifest_path, manifest)
        result["documentation_integration"] = documentation_integration(root, manifest_path, manifest)
        result["readability"] = diagram_metrics(root, manifest)
        result["diagram"] = manifest.get("diagram")
        result["model"] = manifest.get("model")
        result["curated_model"] = manifest.get("curated_model")
    return result


def check(root: Path, base_ref: str | None = None) -> dict:
    result = status(root)
    files, git_error = changed_files(root, base_ref)
    result["base_ref"] = base_ref
    result["changed_files"] = files
    result["git_error"] = git_error
    if not result["initialized"]:
        result["requires_sync"] = False
        result["requires_documentation_update"] = False
        result["reason"] = "architecture maintenance is not initialized"
        return result
    manifest_path, manifest, _ = find_manifest(root)
    sources = source_paths(manifest or {})
    classified = {path: classify(path, sources) for path in files}
    result["classification"] = classified
    result["potentially_architecture_impacting"] = [
        path for path, kind in classified.items() if kind == "potentially_architecture_impacting"
    ]
    result["architecture_asset_changes"] = [
        path for path, kind in classified.items() if kind == "architecture_asset_change"
    ]
    result["requires_sync"] = bool(result["potentially_architecture_impacting"])
    result["requires_architecture_review"] = bool(
        result["potentially_architecture_impacting"] or result["architecture_asset_changes"]
    )
    integration = result.get("documentation_integration", {})
    result["requires_documentation_update"] = bool(
        not integration.get("configured")
        or integration.get("missing")
        or integration.get("unlinked")
    )
    result["reason"] = (
        "review architecture-impacting changes and propose drawio-skill sync"
        if result["requires_sync"]
        else "review architecture asset changes"
        if result["architecture_asset_changes"]
        else "no configured source or topology path changed"
    )
    result["manifest"] = str(manifest_path.relative_to(root)) if manifest_path else None
    return result


def init_manifest(root: Path, args: argparse.Namespace) -> int:
    target = root / DEFAULT_MANIFESTS[0]
    if target.exists():
        print(f"manifest already exists: {target}", file=sys.stderr)
        return 1
    diagram = args.diagram
    sources = [{"path": value, "kind": args.kind} for value in (args.source or ["src"])]
    curated_model = args.curated_model
    if curated_model is None:
        candidate = "docs/construct/architecture/architecture-model.json"
        if (root / candidate).exists():
            curated_model = candidate
    data = {
        "schema": SCHEMA,
        "status": "active",
        "diagram": diagram,
        "model": args.model,
        "modeling": {
            "source_of_truth": "curated" if curated_model else "drawio_ir",
            "allow_inference": False,
        },
        "sources": sources,
        "views": args.view or ["system"],
        "view_contracts": [
            {
                "id": view,
                "question": f"What does the {view} view explain?",
                "audience": "project maintainers",
                "max_nodes": VIEW_LIMITS.get(view, (None, None))[0],
                "max_edges": VIEW_LIMITS.get(view, (None, None))[1],
            }
            for view in (args.view or ["system"])
        ],
        "engine": {"name": "drawio-skill", "version": args.engine_version},
        "sync": {"preserve_manual_layout": True, "prune": False},
    }
    if curated_model:
        data["curated_model"] = curated_model
    integration = {}
    discovered_state = next((path for path in CURRENT_STATE_CANDIDATES if (root / path).exists()), None)
    discovered_index = Path("docs/construct/README.md") if (root / "docs/construct/README.md").exists() else None
    requested_guidance = args.guidance or args.agents
    discovered_guidance = None
    if not requested_guidance:
        discovered_guidance, guidance_error = discover_authoritative_guidance(root)
        if guidance_error:
            print(f"Cannot initialize architecture integration: {guidance_error}", file=sys.stderr)
            return 2
    for key, value in (
        ("current_state", args.current_state or (str(discovered_state) if discovered_state else None)),
        ("construct_index", args.construct_index or (str(discovered_index) if discovered_index else None)),
        ("guidance", requested_guidance or discovered_guidance),
    ):
        if value:
            integration[key] = value
    if integration:
        data["integration"] = integration
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(target)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "check", "init"))
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--diagram", default="docs/construct/architecture/system.drawio")
    parser.add_argument("--model", default="docs/construct/architecture/system.ir.json")
    parser.add_argument("--curated-model")
    parser.add_argument("--source", action="append")
    parser.add_argument("--kind", default="javascript")
    parser.add_argument("--view", action="append")
    parser.add_argument("--engine-version", default="3.4.0")
    parser.add_argument("--base-ref", help="compare committed changes from BASE_REF...HEAD")
    parser.add_argument("--current-state")
    parser.add_argument("--construct-index")
    parser.add_argument("--guidance", help="authoritative AGENTS.md or CLAUDE.md path")
    parser.add_argument("--agents", help="legacy alias for --guidance")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.command == "status":
        print(json.dumps(status(root), indent=2, ensure_ascii=False))
        return 0
    if args.command == "check":
        print(json.dumps(check(root, args.base_ref), indent=2, ensure_ascii=False))
        return 0
    return init_manifest(root, args)


if __name__ == "__main__":
    raise SystemExit(main())
