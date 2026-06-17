# Vento Validate

Use this mode for read-only structural checks of Vento project assets.

## Checks

Validate may inspect:

- `AGENTS.md`
- `.agents/skills/*/SKILL.md`
- current-state docs
- construct docs
- active and deprecated roadmaps
- package/build/test/CI config referenced by docs

## What To Report

- missing or invalid project skill frontmatter
- unclear project skill triggers
- referenced paths that do not exist
- commands mentioned in Vento docs but absent from project config
- placeholder text left in generated files
- current-state docs containing future plans
- roadmap content treated as current code fact
- active roadmap over 2000 lines
- deprecated roadmap referenced as the active source
- obvious facts copied from a different project

Do not modify files in validate mode unless the user explicitly changes the request.

