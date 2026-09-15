# Claude Code Compatibility

Vento is distributed to Claude Code as a regular Claude Code plugin. The plugin
package and project-level bridges have different responsibilities:

```text
Vento plugin package
├── .claude-plugin/plugin.json
├── .claude-plugin/marketplace.json
└── skills/vento/SKILL.md          -> /vento:vento

Claude Code-first target
├── CLAUDE.md                      -> authoritative guidance
└── .claude/skills                 -> authoritative project skills

Codex-first target after Claude is added
├── AGENTS.md                      -> authoritative guidance
├── CLAUDE.md                      -> @AGENTS.md pointer
├── .agents/skills                 -> authoritative project skills
└── .claude/skills                 -> ../.agents/skills symlink
```

## Package requirements

- Keep `skills/` at the plugin root; do not nest it under `.claude-plugin/`.
- Keep `.claude-plugin/plugin.json` and marketplace metadata at the documented
  paths.
- Keep the plugin's skill content agent-neutral. Do not create a second Claude-only
  copy of Vento rules or project facts.
- Keep the marketplace entry version aligned with `.claude-plugin/plugin.json`.
- After source changes, update the marketplace checkout and plugin cache through
  Claude Code's CLI; do not hand-edit `~/.claude/plugins/cache`.

## Installation and update contract

For a local checkout:

```bash
claude plugin marketplace add /home/wenct/myself/vento
claude plugin install vento@vento --scope user --yes
claude plugin enable vento@vento --scope user
```

For an existing installation:

```bash
claude plugin marketplace update vento
claude plugin update vento@vento --scope user --yes
```

Verify both the installed selector and the skill inventory:

```bash
claude plugin list --json
claude plugin details vento@vento
```

The plugin is active in a new Claude Code session after installation or update.

## Project bridge contract

Vento uses native-first initialization:

- In a new Claude Code project, create `CLAUDE.md` directly from the Claude-native
  template. Do not create `AGENTS.md` merely for portability.
- Keep new Claude-first project skills in `.claude/skills`.
- If Codex is later added, keep Claude's files authoritative. Create a pointer-only
  `AGENTS.md` that instructs Codex to read `CLAUDE.md`, and link
  `.agents/skills -> ../.claude/skills` when project skills exist.
- If Codex was initialized first, create `CLAUDE.md` containing `@AGENTS.md` and
  link `.claude/skills -> ../.agents/skills` when Claude Code is added.

If either side already exists with independent content, report a split-brain
conflict and do not replace it silently. Never create circular imports or two skill
symlinks that point at each other.

## Validation boundaries

`validate_claude_plugin.py` checks the repository package shape and metadata. It
does not prove that a particular user's Claude Code session has reloaded the
plugin. Confirm that separately with `claude plugin list --json`,
`claude plugin details`, and a new session invoking `/vento:vento`.
