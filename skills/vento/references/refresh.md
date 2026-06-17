# Vento Refresh

Use this mode for cross-asset factual drift audit and update orchestration after project changes.

Refresh is not a replacement for Skills or Roadmap mode. It decides which Vento assets are stale and recommends an update order.

## Workflow

1. Read current project structure, config, docs, tests, and relevant changed files.
2. Read existing Vento assets.
3. Compare current facts with project guidance.
4. Report drift by asset.
5. Recommend updates and order.
6. Ask for write approval before changing files.
7. Delegate detailed edits to the appropriate mode when useful: Bootstrap, Skills, or Roadmap.

## Output Shape

Include:

- project changes observed
- assets checked
- drift found
- recommended updates
- suggested order
- items needing user approval
- items intentionally left unchanged

Use Refresh when the user does not know which Vento asset is stale.

