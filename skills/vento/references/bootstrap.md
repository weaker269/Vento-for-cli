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
3. Identify stable boundaries, high-risk areas, local run/test commands, reusable entry points, and missing facts.
4. Propose the Vento asset plan before writing.
5. After explicit write approval, create or update only the agreed baseline files.
6. Report what was created, what was skipped, and what facts remain unconfirmed.

## Output Rules

- Keep `AGENTS.md` executable and concise.
- Do not move detailed subsystem guidance into `AGENTS.md`; propose project skills instead.
- Do not write future roadmap items into current-state docs.
- Do not copy facts from another repository.

