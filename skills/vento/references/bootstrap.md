# Vento Bootstrap

Use this mode when a project is first adopting Vento or needs a baseline AI collaboration skeleton.

## Scope

Bootstrap may propose or create:

- the active host's native guidance (`AGENTS.md` for Codex or `CLAUDE.md` for Claude Code)
- the active host's native project skill directory when Skills mode later needs it
- cross-agent bridge files only when a second host is explicitly added
- a concise current-state document
- optional construct doc skeletons
- optional roadmap recommendation
- recommendations for future project skills

Bootstrap must not create a full native project skill set (`.agents/skills` or `.claude/skills`) or manage roadmap replacement. Use Skills or Roadmap mode for those.

## Default Paths

Prefer these paths unless the target project already has a clear, compatible convention:

- current-state doc: `docs/productization/codebase-current-state.md`
- lightweight fallback current-state doc: `docs/codebase-current-state.md`
- construct docs: `docs/construct/<topic>.md`
- active roadmap: `docs/productization/active-roadmap.md`
- lightweight fallback active roadmap: `docs/roadmap/active-roadmap.md`
- optional specs: `docs/productization/specs/YYYY-MM-DD-<topic>.md` (fallback `docs/roadmap/specs/`), created only when a roadmap item needs a design decision

Do not place the codebase current-state entrypoint under `docs/construct/`. Construct docs are topic-based human-facing system construction documents, not the AI/agent current-state entrypoint.

## Cross-Agent Bridge

Vento assets are agent-neutral, but loading is host-specific. Codex natively reads
`AGENTS.md` and `.agents/skills`; Claude Code natively reads `CLAUDE.md` and
`.claude/skills`. Use native-first initialization:

- If neither host has guidance, initialize only the active host's native files.
- A first-time Claude Code bootstrap creates `CLAUDE.md`; it does not create
  `AGENTS.md` or force `@AGENTS.md`.
- A first-time Codex bootstrap creates `AGENTS.md`; it does not create `CLAUDE.md`.
- A project using only one host does not need bridge files and must not receive
  missing-bridge warnings.

When the second host is explicitly added, preserve whichever host was initialized
first as the authoritative source:

- **Codex first**: create `CLAUDE.md` with `@AGENTS.md`; if project skills exist,
  create `.claude/skills -> ../.agents/skills`.
- **Claude Code first**: create a pointer-only `AGENTS.md` that instructs Codex to
  read and follow `CLAUDE.md`; if project skills exist, create
  `.agents/skills -> ../.claude/skills`.
- Codex has no portable, documented `@CLAUDE.md` import equivalent. Do not present
  the pointer-only `AGENTS.md` as a native import; it is an explicit read-first
  instruction.
- If both guidance files or both skill directories already contain independent
  content, report a split-brain conflict. Do not replace, merge, or choose an
  authority without user approval.
- Never create circular bridges or two symlinks that point at each other.

Use `assets/CLAUDE.template.md` for Claude-native initialization,
`assets/CLAUDE.agents-bridge.template.md` for Codex-first bridging, and
`assets/AGENTS.claude-bridge.template.md` for Claude-first bridging.

## Workflow

1. Read existing guidance first: `AGENTS.md`, `CLAUDE.md`, `.agents/skills`, `.claude/skills`, README, docs, package/build/test config, CI config, main entry files, schema or route files if present.
2. Build a short project inventory with real paths and commands.
3. Determine the host state: uninitialized, Codex-native, Claude-native,
   Codex-authoritative portable, Claude-authoritative portable, or split-brain.
4. Sort findings by destination before writing:
   - policy, authorization, context pointers, architecture guardrails, and completion gates -> the active authoritative guidance file
   - project inventory, module map, technical stack, detailed commands, and current implementation facts -> current-state docs
   - task-specific workflows, reuse points, and validation matrices -> project skills
   - future demand and priority -> roadmap
   - design decisions for a specific roadmap item -> a spec linked from that item
5. Identify stable boundaries, high-risk areas, core commands, reusable entry points, and missing facts.
6. Propose the Vento asset plan before writing. Propose bridges only when adding a second host.
7. After explicit write approval, create or update only the agreed baseline files.
8. Report the authoritative host, what was created, what was skipped, and what facts remain unconfirmed.

## Output Rules

- Treat the authoritative `AGENTS.md` or `CLAUDE.md` as policy-first, not inventory-first.
- Keep the authoritative guidance executable and concise: behavior rules, current-fact entry points, high-risk architecture guardrails, and Vento maintenance gates.
- If creating guidance and current-state docs, write current implementation facts into current-state first and make the authoritative guidance point to it.
- If creating construct docs, create only topic-specific skeletons that explain implemented flows, state transitions, data locations, or invariants.
- Do not put full module maps, API route lists, docs inventories, business data definitions, or detailed command matrices in the authoritative guidance file.
- Do not move detailed subsystem guidance into the authoritative guidance file; use current-state docs or propose project skills instead.
- Keep guidance commands to core install/build/typecheck/test/start commands.
- Do not write future roadmap items into current-state docs.
- Do not copy facts from another repository.
