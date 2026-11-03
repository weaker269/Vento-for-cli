# Project Claude Code Rules

This file is the project-level behavior entry for Claude Code. It is policy-first,
not an implementation inventory. Current code facts live in the current-state
document and source code.

## Project Identity

- Project:
- Current facts entry: `docs/productization/codebase-current-state.md`
- Primary source roots:

## Working Rules

- Default language:
- Secrets and environment rules:

## Context Entry Points

- Current state: `docs/productization/codebase-current-state.md`
- Project skills: `.claude/skills/`
- Construct docs: `docs/construct/`
- Architecture assets (when initialized): `docs/construct/architecture/`
- Flow assets (when initialized): `docs/construct/flows/`
- Planning (read only for planning or design tasks): `docs/productization/active-roadmap.md` and its linked specs
- Source roots:
- Tests:
- Config/schema:

## Core Commands

```bash
# install

# build

# typecheck

# test
```

## Architecture Guardrails

- Project-wide invariant:
- High-risk boundary:
- Obsolete path not to restore:

## Vento Maintenance Gate

After code changes, check whether the change affects:

- `CLAUDE.md`
- `.claude/skills`
- current-state docs
- construct docs
- architecture manifest and `.drawio`/Diagram IR assets
- flow manifest, semantic model, and Mermaid assets
- roadmap item status and linked spec status

Explain what was updated or why no Vento asset update was needed.
If architecture maintenance is initialized, also verify that the current-state/map
entry still links the architecture manifest, affected views remain within their
density budgets, and render/visual status is reported honestly. If flow maintenance
is initialized, identify the affected scenarios and keep Mermaid render and visual
review status separate.
