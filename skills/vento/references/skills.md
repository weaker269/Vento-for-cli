# Vento Skills

Use this mode for native project skill lifecycle work: audit, propose, create,
update, refresh, validate, split, merge, or deprecate. Use `.agents/skills` in a
Codex-first project and `.claude/skills` in a Claude Code-first project.

## Actions

- `audit`: read-only review of existing project skills and missing task scenarios.
- `propose`: recommend skills to create, update, merge, split, or deprecate.
- `create`: create a project-specific skill after confirming the scenario is real.
- `update`: incrementally update an existing project skill using current code facts.
- `refresh`: batch update project skills after architecture or workflow changes.
- `validate`: check skill structure, triggers, paths, commands, and scope.
- `deprecate`: mark a project skill obsolete only with explicit user approval.

## Creation Criteria

Create a project skill only when at least one is true:

- The task scenario is frequent or risky.
- The project has non-obvious files, commands, APIs, workflows, or invariants.
- Future agents are likely to repeat investigation or restore obsolete paths.
- Focused validation choices are project-specific.

Do not create a skill for generic engineering advice.

Create the first project skill in the active authoritative host's native directory.
Only add the opposite host's symlink when that second host is explicitly added, per
the native-first bridge rules in `bootstrap.md`.

## Required Project Skill Content

Each project skill should include:

- clear trigger scenario in frontmatter `description`
- files or directories to read first
- recommended workflow
- reusable project modules, helpers, services, commands, or components
- forbidden paths, obsolete patterns, or high-risk mistakes
- focused validation guidance
- known unknowns if any

## Update Rules

- Preserve useful existing content.
- Remove or correct stale facts.
- Prefer current code over old docs.
- Keep references to real files and commands.
- Avoid large omnibus skills. Split by task scenario when content grows across unrelated domains.
