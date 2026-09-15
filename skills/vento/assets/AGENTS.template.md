# Project Agent Rules

This file is the project-level behavior entry for AI agents. It is policy-first, not an implementation inventory. Current code facts live in the current-state document and source code.

## Project Identity

- Project:
- Current facts entry: `docs/productization/codebase-current-state.md`
- Primary source roots:

Keep this section short. Do not describe subsystem details here.

## Working Rules

- Default language:
- Modification authorization:
- High-risk operations requiring confirmation:
- Secrets and environment rules:

## Context Entry Points

- Current state: `docs/productization/codebase-current-state.md`
- Project skills:
- Construct docs: `docs/construct/`
- Architecture assets (when initialized): `docs/construct/architecture/`
- Source roots:
- Tests:
- Config/schema:

List only top-level roots or truth-source paths. Put detailed module maps, route lists, and docs inventories in current-state docs or project skills. Keep construct docs for topic-specific human-facing system construction, not the codebase current-state entrypoint.

## Core Commands

```bash
# install

# build

# typecheck

# test
```

Keep only commands most agents need. Put task-specific validation matrices in project skills.

## Architecture Guardrails

- Project-wide invariant:
- High-risk boundary:
- Obsolete path not to restore:

Keep this section to project-wide guardrails. Put subsystem-specific guidance in current-state docs or project skills.

## Vento Maintenance Gate

After code changes, check whether the change affects:

- `AGENTS.md`
- `.agents/skills`
- current-state docs
- construct docs
- architecture manifest and `.drawio`/Diagram IR assets
- roadmap

Explain what was updated or why no Vento asset update was needed.
If architecture maintenance is initialized, also verify that the current-state/map
entry still links the architecture manifest and that affected views remain within
their readability contracts.
