# Vento Bootstrap

Use this mode when a project is first adopting Vento or needs a baseline AI collaboration skeleton.

## Scope

Bootstrap may propose or create:

- `AGENTS.md`
- a concise current-state document
- optional construct doc skeletons
- optional roadmap recommendation
- recommendations for future project skills

Bootstrap must not create full `.agents/skills` or manage roadmap replacement. Use Skills or Roadmap mode for those.

## Workflow

1. Read existing guidance first: `AGENTS.md`, README, docs, package/build/test config, CI config, main entry files, schema or route files if present.
2. Build a short project inventory with real paths and commands.
3. Sort findings by destination before writing:
   - policy, authorization, context pointers, architecture guardrails, and completion gates -> `AGENTS.md`
   - project inventory, module map, technical stack, detailed commands, and current implementation facts -> current-state docs
   - task-specific workflows, reuse points, and validation matrices -> project skills
   - future demand and priority -> roadmap
4. Identify stable boundaries, high-risk areas, core commands, reusable entry points, and missing facts.
5. Propose the Vento asset plan before writing.
6. After explicit write approval, create or update only the agreed baseline files.
7. Report what was created, what was skipped, and what facts remain unconfirmed.

## Output Rules

- Treat `AGENTS.md` as policy-first, not inventory-first.
- Keep `AGENTS.md` executable and concise: behavior rules, confirmation boundaries, current-fact entry points, high-risk architecture guardrails, and Vento maintenance gates.
- If creating both `AGENTS.md` and current-state docs, write current implementation facts into current-state first and make `AGENTS.md` point to it.
- Do not put full module maps, API route lists, docs inventories, business data definitions, or detailed command matrices in `AGENTS.md`.
- Do not move detailed subsystem guidance into `AGENTS.md`; use current-state docs or propose project skills instead.
- Keep `AGENTS.md` commands to core install/build/typecheck/test/start commands plus dangerous-command confirmation rules.
- Do not write future roadmap items into current-state docs.
- Do not copy facts from another repository.
