# Vento Refresh

Use this mode for cross-asset factual drift audit and update orchestration after project changes.

Refresh is not a replacement for Skills or Roadmap mode. It decides which Vento assets are stale and recommends an update order.

## Workflow

1. Read current project structure, config, docs, tests, and relevant changed files.
2. Read existing Vento assets.
3. If an architecture manifest exists, run the architecture drift check described in `references/architecture.md`.
4. If a flow manifest exists, run the flow drift check described in `references/flows.md`.
5. Compare current facts with project guidance. For roadmap items implemented since
   the last refresh, check that the item status, linked spec status, and
   current-state or construct docs were updated.
6. Report drift by asset, including architecture and flow diagrams when applicable.
7. Recommend updates and order.
8. Ask for write approval before changing files.
9. Route detailed edits to the appropriate mode: Bootstrap, Skills, Roadmap, Architecture, or Flows.

## Output Shape

Include:

- project changes observed
- assets checked
- drift found
- architecture density budgets, render/visual status, and project-map registration, when initialized
- affected flow scenarios, Mermaid render/visual status, and project-map registration, when initialized
- planning assets: missing spec links, stale spec statuses, and legacy planning paths as migration candidates
- recommended updates
- suggested order
- items needing user approval
- items intentionally left unchanged

Use Refresh when the user does not know which Vento asset is stale.

If no architecture manifest or diagram exists, report that architecture maintenance is
not initialized and skip diagram creation. Do not bootstrap an architecture diagram
implicitly during refresh.

If no flow manifest exists, report that flow maintenance is not initialized and skip
flow creation. Do not infer that every project needs flow assets.

If legacy planning paths such as `docs/superpowers/` exist, propose a migration in
the report and leave the files in place. Migrate only after explicit approval, per
`references/roadmap.md`.
