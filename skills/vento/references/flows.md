# Vento Flow Diagram Maintenance

Use this mode for long-lived diagrams that explain how implemented system behavior
unfolds over time. Architecture mode owns stable structure and deployment boundaries;
Flow mode owns ordered execution, decisions, branches, messages, and lifecycle state.

## Opt-in lifecycle

Flow assets are opt-in. Do not create them during Bootstrap, Refresh, or ordinary
code changes unless the user explicitly initializes or requests flow maintenance.

1. Discover the implemented behavior from current code, tests, schemas, config, and
   construct docs.
2. Select a question and audience before selecting a notation.
3. Build `flow-model.json` from source-backed steps, messages, or states.
4. Register the selected assets in `flows.json` and link the flow directory from the
   current-state/project map.
5. Generate Mermaid sources with `flows.py render`.
6. Render Mermaid to SVG or PNG with an available Mermaid renderer and inspect the
   result visually. Record rendering and visual review separately.

Flow maintenance is manual and agent-driven. Refresh reports drift and proposes
updates; it does not silently rewrite flow models or generated diagrams.

## Canonical assets

Prefer this layout:

```text
docs/construct/flows/
├── README.md
├── flows.json
├── flow-model.json
├── system-overview.mmd
└── scenarios/
    ├── important-use-case.sequence.mmd
    └── object-lifecycle.state.mmd
```

Use `assets/flows.template.json` for the manifest,
`assets/flow-model.template.json` for the semantic model, and
`assets/flows-readme.template.md` for the human-facing entrypoint. Mermaid sources
are generated, reviewable projections. SVG, PNG, and interactive HTML are derived
artifacts and should be committed only when the project has a distribution need.

When an architecture model exists, reference it with `architecture_model` and use
its stable component IDs from flow steps and participants. Do not merge structural
dependencies and ordered behavior into one generic edge list.

## Select the diagram type

- **Flowchart**: use for an end-to-end operating overview, staged work, decisions,
  success paths, and failure paths.
- **Sequence**: use when call order, request/response boundaries, async messages, or
  error returns are the maintenance question.
- **State**: use when legal states and event-driven transitions determine behavior.
- **Architecture**: route context, container, deployment, topology, and stable
  component relationships back to Architecture mode.

UML is a notation family, not a renderer. Mermaid is the default renderer for flow,
sequence, and state assets because its text source is easy to review and synchronize.
Use PlantUML only when the target project already relies on it or requires UML
semantics that Mermaid cannot express. Use draw.io when spatial topology and manual
layout are more important than ordered behavior.

## Modeling contract

Every scenario contains `id`, `title`, `type`, `question`, `audience`, evidence, and
type-specific behavior:

- `flowchart`: phases, steps, and transitions. Include at least one `start` and one
  `end` step. Use `decision` only for an actual branch and label branch conditions.
- `sequence`: participants and messages in execution order. Use short message labels;
  keep payload schemas and implementation detail in linked construct docs.
- `state`: states and transitions. Mark at least one initial and one terminal state;
  label transitions with the event or condition that causes them.

Use nouns for participants and states, verbs for steps and messages, and short labels
on transitions. A main overview should explain the primary operating path, not every
module, table, retry, and exception. Move detail into scenario-specific diagrams.

Represent current implementation and future design separately. A `current` scenario
must have evidence in the active codebase. Proposed behavior belongs in a roadmap or
design artifact unless the user explicitly requests a proposed flow diagram.

## Commands

Run from the Vento source tree:

```bash
python3 skills/vento/scripts/flows.py status .
python3 skills/vento/scripts/flows.py check .
python3 skills/vento/scripts/flows.py check . --base-ref origin/main
python3 skills/vento/scripts/flows.py render .
python3 skills/vento/scripts/flows.py render . --scenario system-overview
```

`status` validates the manifest, semantic model, registered Mermaid assets,
documentation integration, and recorded verification states. `check` classifies
changed files as flow assets, potentially flow-impacting sources, or unrelated.
`render` deterministically projects the selected scenario into Mermaid source; it
does not claim that Mermaid was rendered or visually reviewed.

## Rendering and visual verification

Generating `.mmd` is not visual verification. Use the Mermaid renderer already
adopted by the target project when possible. If no renderer is available, keep the
source and report both statuses as `unverified` rather than substituting another
format silently.

Record these states per asset in `flows.json`:

- `verification.render.status`: whether a real SVG/PNG/HTML render was produced.
- `verification.visual_review.status`: whether the rendered artifact was inspected.
- `verification.visual_review.reviewed_at`: required when visual review passed.

During visual review, check the actual output at its intended reading size:

- one primary reading direction;
- no clipped nodes or labels;
- no labels covering nodes or unrelated edges;
- decisions have visible branch conditions;
- the primary path is distinguishable from errors and optional branches;
- text remains readable without opening the source model;
- a diagram that cannot remain legible is split into an overview and linked scenarios.

An unrendered asset is structurally maintainable but not visually verified.

## Project-map integration and drift

Link `flows.json`, the flow directory, or its main overview from the configured
current-state document, construct index, and authoritative guidance entrypoint. Keep
detailed steps in the flow assets rather than copying them into `AGENTS.md` or
`CLAUDE.md`.

Flow-impacting changes normally include registered source paths, request handling,
orchestration, state transitions, async boundaries, error handling, persistence
timing, and external calls. Styling, copy, and unrelated tests should not trigger a
flow update unless they change one of those behaviors.

When drift is found, update only the affected scenarios. Preserve stable scenario,
component, step, participant, and state IDs where the represented concept still
exists. Report model changes, regenerated Mermaid assets, render status, and visual
review status separately.

## Interactive operating map

Search, progressive expansion, detail panels, and playback may later be generated
from the same flow model as an interactive HTML view. Do not maintain a separate
hand-authored interactive truth source. Interactive output is optional and does not
replace the Mermaid source or scenario evidence.
