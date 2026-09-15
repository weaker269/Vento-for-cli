# Vento Refresh

Use this mode for cross-asset factual drift audit and update orchestration after project changes.

Refresh is not a replacement for Skills or Roadmap mode. It decides which Vento assets are stale and recommends an update order.

## Workflow

1. Read current project structure, config, docs, tests, and relevant changed files.
2. Read existing Vento assets.
3. If an architecture manifest exists, run the architecture drift check described in `references/architecture.md`.
4. Compare current facts with project guidance.
5. Report drift by asset, including architecture diagrams when applicable.
6. Recommend updates and order.
7. Ask for write approval before changing files.
8. Delegate detailed edits to the appropriate mode when useful: Bootstrap, Skills, Roadmap, or Architecture.

## Output Shape

Include:

- project changes observed
- assets checked
- drift found
- architecture view readability and project-map registration, when initialized
- recommended updates
- suggested order
- items needing user approval
- items intentionally left unchanged

Use Refresh when the user does not know which Vento asset is stale.

If no architecture manifest or diagram exists, report that architecture maintenance is
not initialized and skip diagram creation. Do not bootstrap an architecture diagram
implicitly during refresh.
