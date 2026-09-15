# Vento Validate

Use this mode for read-only structural checks of Vento project assets.

## Checks

Validate may inspect:

- `AGENTS.md`
- `CLAUDE.md` and `.claude/skills` cross-agent bridge files
- the Vento `.claude-plugin` manifest, marketplace entry, and Claude Code skill package
- `.agents/skills/*/SKILL.md`
- opt-in architecture manifests and their repository-relative diagram/IR artifacts
- current-state docs
- construct docs
- active and deprecated roadmaps
- package/build/test/CI config referenced by docs

## What To Report

- missing or invalid project skill frontmatter
- unclear project skill triggers
- referenced paths that do not exist
- commands mentioned in Vento docs but absent from project config
- `AGENTS.md` that reads like current-state: full module maps, route inventories, docs inventories, detailed command matrices, or business data definitions
- placeholder text left in generated files
- current-state docs containing future plans
- roadmap content treated as current code fact
- active roadmap over 2000 lines
- deprecated roadmap referenced as the active source
- obvious facts copied from a different project
- `AGENTS.md` present but `CLAUDE.md` missing or lacking the `@AGENTS.md` import (Claude Code will not auto-load project rules)
- `.agents/skills` present but the `.claude/skills` bridge symlink missing (Claude Code will not discover project skills)
- `.claude/skills` existing as a real directory that may diverge from `.agents/skills`

Do not modify files in validate mode unless the user explicitly changes the request.
