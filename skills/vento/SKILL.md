---
name: vento
description: Apply the Vento portable AI project collaboration framework. Use when setting up, auditing, refreshing, validating, or maintaining project-level AGENTS.md or CLAUDE.md, native project skills, current-state docs, construct docs, architecture maps, roadmap lifecycle, project skill lifecycle, or related AI collaboration rules. Also use when the user asks to initialize, inspect, update, or review an architecture diagram; create, update, replace, rotate, archive, deprecate, or migrate a project roadmap; create, update, audit, validate, or deprecate project skills; validate framework files; or refresh project knowledge after code changes.
---

# Vento

Vento is a portable AI project collaboration framework. It helps coding agents such as Codex and Claude Code build and maintain project-specific guidance so future agents can understand, modify, debug, test, and extend a codebase without stale assumptions or duplicated work.

Vento migrates the framework method, not facts from another project. Always rediscover facts from the current repository before writing project guidance.

## Mode Routing

Choose exactly one primary mode from the user's request:

- **Bootstrap**: first-time setup or baseline project AI guidance. Read `references/bootstrap.md`.
- **Skills**: create, update, audit, validate, refresh, split, merge, or deprecate native project skills. Read `references/skills.md`.
- **Roadmap**: initialize, update, replace, rotate, archive, deprecate, inspect, or migrate a project roadmap. Read `references/roadmap.md`.
- **Architecture**: initialize, inspect, review, and maintain a project architecture diagram. Read `references/architecture.md`.
- **Validate**: read-only structural checks for Vento assets. Read `references/validate.md`.
- **Refresh**: cross-asset factual drift audit and update orchestration after project changes. Read `references/refresh.md`.

Treat these slash-like phrases as aliases, even when no real slash command exists:

- `/vento-bootstrap` -> Bootstrap mode
- `/vento-skills` -> Skills mode
- `/vento-roadmap` -> Roadmap mode
- `/vento-architecture` -> Architecture mode
- `/vento-validate` -> Validate mode
- `/vento-refresh` -> Refresh mode

## Shared Rules

- Default to read-only audit. Create or edit files only after explicit user approval.
- Use current code, config, tests, docs, and user-confirmed facts as evidence. Do not invent project capabilities.
- Keep current facts separate from future plans.
- Keep Vento assets scoped: the authoritative native guidance file (`AGENTS.md` for Codex-first or `CLAUDE.md` for Claude-first) for hard rules and entry points, its native project skill directory for task scenarios, current-state docs for concise current facts, construct docs for system flows, and roadmap for future demand.
- When architecture maintenance is initialized, register its manifest and human-facing entrypoint in the current-state/project map and validate per-view readability; do not leave diagrams as isolated files.
- Initialize guidance in the active host's native files. Only create cross-agent bridges when a second host is added, and keep the first initialized guidance/skills as the authoritative source. Follow `references/bootstrap.md`.
- Do not create generic project skills. A project skill must encode project-specific files, reuse points, risks, or validation choices.
- Preserve existing useful content and user edits. Update incrementally.
- If Vento output affects long-lived project guidance, explain what was updated and what was intentionally left unchanged.

## Bundled Resources

- Paths in this section are relative to this skill directory.
- Use templates in `assets/` when creating project files.
- Use `scripts/inventory_project.py` for a lightweight project inventory when helpful.
- Use `scripts/validate_vento_project.py` for deterministic Vento structure checks when possible.
