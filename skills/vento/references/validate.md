# Vento Validate

Use this mode for read-only structural checks of Vento project assets.

## Checks

Validate may inspect:

- `AGENTS.md`
- `CLAUDE.md` and `.claude/skills` cross-agent bridge files
- the Vento `.claude-plugin` manifest, marketplace entry, and Claude Code skill package
- `.agents/skills/*/SKILL.md` or `.claude/skills/*/SKILL.md`
- opt-in architecture manifests and their repository-relative diagram/IR artifacts
- opt-in flow manifests, semantic models, Mermaid assets, and recorded visual verification
- current-state docs
- construct docs
- active and deprecated roadmaps
- package/build/test/CI config referenced by docs

## What To Report

- missing or invalid project skill frontmatter
- unclear project skill triggers
- referenced paths that do not exist
- commands mentioned in Vento docs but absent from project config
- authoritative `AGENTS.md` or `CLAUDE.md` that reads like current-state: full module maps, route inventories, docs inventories, detailed command matrices, or business data definitions
- placeholder text left in generated files
- current-state docs containing future plans
- roadmap content treated as current code fact
- active roadmap over 2000 lines
- deprecated roadmap referenced as the active source
- obvious facts copied from a different project
- a native-only Codex or Claude Code project incorrectly reported as missing a bridge
- `CLAUDE.md` importing a missing `AGENTS.md`, or a Claude-authoritative `AGENTS.md` bridge pointing to a missing `CLAUDE.md`
- circular guidance bridges or independent `AGENTS.md`/`CLAUDE.md` files that create split-brain
- broken, circular, or independent `.agents/skills` and `.claude/skills` trees after both hosts are enabled
- architecture density budgets presented as readability proof, or render/visual status left unverified
- flow scenarios with unknown steps, participants, states, or mismatched registered asset types

Do not modify files in validate mode unless the user explicitly changes the request.
