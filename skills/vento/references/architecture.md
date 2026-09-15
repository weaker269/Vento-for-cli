# Vento Architecture Diagram Maintenance

Use this mode for project architecture diagram lifecycle work. Vento owns the
lifecycle, evidence, authorization, and drift policy. The external
`drawio-skill` owns draw.io XML generation, Diagram IR, layout, synchronization,
rendering, and semantic diagram checks.

## Opt-in lifecycle

Architecture diagrams are opt-in long-lived assets:

1. **Not initialized**: if no architecture manifest or registered diagram exists,
   report that state and do not create a diagram during `bootstrap`, `refresh`, or
   ordinary code changes.
2. **Explicit initialization**: initialize only after the user explicitly asks for
   an architecture diagram. Discover the project's real sources, choose a scope
   and views, generate an editable `.drawio` with drawio-skill, validate it,
   register the manifest, and link it from the project's current-state/map entry.
3. **Maintained**: after initialization, `refresh` checks the manifest's source
   paths and the changed files. Architecture-impacting changes produce a drift
   report and a proposed sync; they do not silently rewrite the diagram.
4. **Approved synchronization**: after explicit write approval, run
   `diagramctl sync` (or the matching drawio-skill workflow), preserve manual
   geometry and annotations, review removals, validate, and report the generated
   artifact paths.

The lifecycle is manual and agent-driven. It is not a file watcher, Git hook,
background task, or automatic updater.

## Canonical project assets

Prefer this layout in the target project:

```text
docs/construct/architecture/
├── README.md
├── architecture.json
├── architecture-model.json
├── system.drawio
└── system.ir.json
```

`architecture.json` is the machine-readable Vento manifest. The `.drawio` file is
the editable human-facing artifact. The IR is optional but strongly recommended
for source-backed incremental synchronization. PNG/SVG/HTML exports are derived
artifacts and should be kept only when the project has a clear distribution need.

The preferred source of truth for overview views is a compact, curated model. Raw
code/IaC import graphs are evidence and detail views, not a substitute for deciding
which boundaries and relationships a human should see first.

Use `assets/architecture-model.template.json` as the Vento model shape. It keeps
components, relationships, evidence, confidence, and view membership separate.
Translate the selected view into drawio-skill Diagram IR for rendering; do not
promote every imported code dependency into the curated model.

The manifest must also describe how the architecture asset is connected to the
project map. Use `integration.current_state`, `integration.construct_index`, and
`integration.agents` when those files exist. Each referenced document must contain
an explicit link or pointer to the architecture manifest or its main diagram.

The manifest schema is `vento/architecture/v1`:

```json
{
  "schema": "vento/architecture/v1",
  "status": "active",
  "diagram": "docs/construct/architecture/system.drawio",
  "model": "docs/construct/architecture/system.ir.json",
  "curated_model": "docs/construct/architecture/architecture-model.json",
  "modeling": {"source_of_truth": "curated", "allow_inference": false},
  "sources": [
    {"path": "src", "kind": "javascript"},
    {"path": "deploy", "kind": "compose"}
  ],
  "views": ["context", "container", "dynamic", "deployment"],
  "view_contracts": [
    {"id": "context", "question": "What is the system boundary?", "audience": "stakeholders", "max_nodes": 8, "max_edges": 12},
    {"id": "container", "question": "What are the major runtime blocks?", "audience": "engineers", "max_nodes": 12, "max_edges": 20}
  ],
  "engine": {"name": "drawio-skill", "version": "3.4.0"},
  "sync": {"preserve_manual_layout": true, "prune": false},
  "integration": {
    "current_state": "docs/productization/codebase-current-state.md",
    "construct_index": "docs/construct/README.md",
    "agents": "AGENTS.md"
  }
}
```

Paths must be repository-relative. Never put credentials, tokens, or private
runtime values in the manifest, Diagram IR, node properties, or provenance.

## Initialization workflow

Before writing anything:

- inspect existing `.drawio`, architecture docs, current-state docs, source roots,
  service entrypoints, API/schema files, and deployment configuration;
- distinguish current implementation facts from inferred or proposed relationships;
- choose the smallest useful scope and name the intended audience and views;
- check whether `drawio-skill` is available and record its pinned version;
- decide which sources are authoritative for future sync.

After generating the diagram, update the existing project map rather than leaving
the asset discoverable only by directory search:

- add a short Architecture Map pointer to the current-state entrypoint;
- add the architecture topic to `docs/construct/README.md` when that index exists;
- add the architecture directory to `AGENTS.md` Context Entry Points when `AGENTS.md`
  exists;
- keep the detailed node/edge inventory in the architecture assets, not in
  `AGENTS.md` or the current-state entrypoint.

Use the external skill's unified CLI when available. Build the overview from the
curated IR after the view contract is agreed:

```bash
# 可选：按 drawio-skill 官方方式安装到当前 Agent 环境
npx skills add Agents365-ai/drawio-skill -g

python3 <drawio-skill>/scripts/diagramctl.py doctor
python3 <drawio-skill>/scripts/diagramctl.py build \
  docs/construct/architecture/system.ir.json --from ir \
  -o docs/construct/architecture/system.drawio
python3 <drawio-skill>/scripts/validate.py \
  docs/construct/architecture/system.drawio --score
```

The exact importer and source kind must come from the current project; do not
guess them from a historical project. If draw.io or Graphviz is unavailable,
report the missing dependency and retain the editable source/IR workflow rather
than silently substituting a flattened image.

Importers may still be used to produce evidence-backed detail graphs. Before
promoting an imported node or edge into a context/container overview, record its
boundary, responsibility, source provenance, and confidence in the curated model.

## View design rules

One model may produce multiple views, but every view must answer one named
question for one audience. Do not create nominally different pages by projecting
the same complete graph with different titles.

- **Context**: show the system, its users, and external systems. Keep implementation
  modules and data-table details out. Default limit: 8 nodes / 12 edges.
- **Container**: show major independently understandable runtime or data boundaries.
  Merge internal helpers and stores into their owning responsibility. Default
  limit: 12 nodes / 20 edges.
- **Dynamic**: show one important use case as an ordered flow. Do not mix multiple
  business scenarios or deployment topology into the same view. Default limit:
  12 participants / 20 interactions.
- **Deployment**: show processes, containers, hosts, networks, and external runtime
  dependencies. Do not repeat every in-process call. Default limit: 14 nodes /
  24 edges.
- **Dataflow/Security/Subsystem detail**: create only when the view answers a
  separate maintenance question. Link it from the context/container view rather
  than expanding the overview.

Every view contract must state its `question`, `audience`, `max_nodes`, and
`max_edges`. If a generated view exceeds its contract, split or re-scope it before
calling it an overview. A visually valid but over-budget view is a warning in
`vento validate`.

## Change and drift workflow

Run the deterministic helper from the Vento source tree:

```bash
python3 skills/vento/scripts/architecture.py status .
python3 skills/vento/scripts/architecture.py check .
# 已提交变更也可指定比较基线：
python3 skills/vento/scripts/architecture.py check . --base-ref origin/main
```

`check` combines the manifest with the current Git working tree and classifies
changed files as architecture-asset changes, potentially architecture-impacting,
or unrelated. Treat the classification as a review prompt, not proof that the
runtime architecture changed. Confirm the evidence in source/config before
synchronizing.

Changes to the diagram, IR, manifest, or architecture README require an
architecture review but do not automatically mean that `diagramctl sync` should
run; a human may have intentionally adjusted the visual layout or documentation.

`status` also reports `documentation_integration` and `readability`. A manifest
with missing or unlinked map targets is an integration drift finding even when the
draw.io XML itself is structurally valid. A view that exceeds its node/edge
contract should be split or deliberately re-scoped before it is treated as an
overview.

如果只发现了 `.drawio` 文件但没有 manifest，视为“发现未注册的架构图”，不视为
已初始化维护；应先由用户明确要求注册/初始化，再补齐来源和同步策略。

Architecture-impacting candidates normally include changes to:

- registered manifest source paths;
- service/module boundaries and entrypoints;
- API, event, protobuf, GraphQL, or database schemas;
- Docker Compose, Kubernetes, Terraform, network, or CI topology;
- authentication, trust boundaries, queues, storage, or external integrations.

Local implementation details, tests, styling, copy, and unrelated generated
files should not trigger a diagram update unless they cross one of those
boundaries.

When synchronizing an existing diagram:

- use `diagramctl sync`, not a full regeneration, for local source changes;
- preserve stable semantic IDs, manual coordinates, styles, and annotations;
- keep removals reviewable by default; use pruning only when explicitly requested;
- run structural validation and inspect a rendered draft when the renderer is
  available;
- report source facts, inferred edges, unresolved conflicts, and validation
  results separately.

## Validation and reporting

`vento validate` checks manifest shape and repository-relative artifact references;
it does not claim that the target project's runtime or architecture is correct.
The drawio-skill validator and semantic rules provide the diagram-level checks.

Every Architecture or Refresh report should state:

- whether maintenance was initialized;
- which manifest and diagram were found;
- changed files and why they may affect the architecture;
- whether drawio-skill was available and which command would run;
- what is verified, inferred, missing, or awaiting user approval;
- what was intentionally left unchanged.
