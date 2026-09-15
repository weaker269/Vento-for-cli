# Vento Asset Boundaries

Use these boundaries when creating or reviewing Vento project assets.

## Default Layout

Prefer this layout unless the target project already has a clear, compatible convention:

- native authoritative guidance: `AGENTS.md` (Codex-first) or `CLAUDE.md` (Claude Code-first)
- native authoritative skills: `.agents/skills/<skill-name>/SKILL.md` or `.claude/skills/<skill-name>/SKILL.md`
- `docs/productization/codebase-current-state.md`
- `docs/construct/<topic>.md`
- `docs/productization/active-roadmap.md`

For lighter projects, `docs/codebase-current-state.md` and `docs/roadmap/active-roadmap.md` are acceptable fallbacks.

Do not put the codebase current-state entrypoint in `docs/construct/`. The current-state document and construct docs both describe current code facts, but they serve different readers and should remain separate.

## Authoritative Guidance

Use for hard rules, authorization boundaries, current-fact entry points, high-risk architecture guardrails, core commands, and completion gates.

The first host's native `AGENTS.md` or `CLAUDE.md` is policy-first, not
inventory-first. It should tell an agent how to work safely in the project and
where to read current facts. Add the opposite host through a pointer-only bridge;
do not create two independently maintained policy files.

Keep only pointer-level facts:

- one-sentence project identity
- current-state doc path
- top-level source roots or truth-source paths
- core install/build/typecheck/test/start commands
- dangerous operations requiring confirmation
- project-wide architecture guardrails
- Vento maintenance gate

Do not use the authoritative guidance file as a complete architecture manual,
module map, route inventory, docs index, or task-specific test matrix.

## Project Skills

Use for task-specific AI guidance. A project skill should answer what to read, what to reuse, what not to break, and how to validate a scenario.

Use `.agents/skills` for Codex-first projects and `.claude/skills` for Claude
Code-first projects. When the second host is added, symlink its native discovery
path to the first host's authoritative skill directory.

Do not create project skills for generic advice.

## Current-State Docs

Use for concise current code facts: what the project is, where truth lives, technical stack, module map, key paths, commands, and which historical paths are obsolete.

The current-state doc is the AI/agent entrypoint after the authoritative guidance
file. It should be a concise map that points agents to source truth, project
skills, construct docs, and validation commands.

Do not include future plans or unimplemented roadmap items.

## Construct Docs

Use for human-readable system construction: flows, state transitions, data locations, and invariants.

Construct docs are topic-based. Use them for implemented subsystem explanations such as data model, auth flow, runtime lifecycle, send-message flow, resource lifecycle, or deployment flow.

Do not turn construct docs into task logs, roadmap items, or the codebase current-state entrypoint.

## Roadmap

Use for demand and prioritization: what to do, status, acceptance, and links to specs, plans, commits, or validation evidence.

Do not treat deprecated roadmaps as active planning sources.
