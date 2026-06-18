# Vento Asset Boundaries

Use these boundaries when creating or reviewing Vento project assets.

## AGENTS.md

Use for hard rules, authorization boundaries, current-fact entry points, high-risk architecture guardrails, core commands, and completion gates.

AGENTS.md is policy-first, not inventory-first. It should tell an agent how to work safely in the project and where to read current facts.

Keep only pointer-level facts:

- one-sentence project identity
- current-state doc path
- top-level source roots or truth-source paths
- core install/build/typecheck/test/start commands
- dangerous operations requiring confirmation
- project-wide architecture guardrails
- Vento maintenance gate

Do not use AGENTS.md as a complete architecture manual, module map, route inventory, docs index, or task-specific test matrix.

## .agents/skills

Use for task-specific AI guidance. A project skill should answer what to read, what to reuse, what not to break, and how to validate a scenario.

Do not create project skills for generic advice.

## Current-State Docs

Use for concise current code facts: what the project is, where truth lives, technical stack, module map, key paths, commands, and which historical paths are obsolete.

Do not include future plans or unimplemented roadmap items.

## Construct Docs

Use for human-readable system construction: flows, state transitions, data locations, and invariants.

Do not turn construct docs into task logs.

## Roadmap

Use for demand and prioritization: what to do, status, acceptance, and links to specs, plans, commits, or validation evidence.

Do not treat deprecated roadmaps as active planning sources.
