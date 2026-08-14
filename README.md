# Vento

Vento is a portable plugin for Codex and Claude Code, bootstrapping and maintaining AI-ready project knowledge.

It provides one main skill, `vento`, with these modes:

- `vento bootstrap`: set up baseline project AI guidance.
- `vento skills`: create, update, audit, validate, or deprecate project `.agents/skills`.
- `vento roadmap`: initialize, update, replace, rotate, or inspect project roadmaps.
- `vento validate`: run read-only structural checks for Vento assets.
- `vento refresh`: audit cross-asset factual drift and plan updates.

## Default Asset Layout

Vento separates AI-facing current facts from human-facing construction docs:

- `AGENTS.md`: project rules, authorization boundaries, entry points, and maintenance gates.
- `.agents/skills/<skill-name>/SKILL.md`: task-specific project playbooks.
- `docs/productization/codebase-current-state.md`: concise AI/agent current-state entrypoint.
- `docs/construct/<topic>.md`: topic-based system construction docs for flows, state, data, and invariants.
- `docs/productization/active-roadmap.md`: active demand and prioritization source.

For lighter projects, `docs/codebase-current-state.md` and `docs/roadmap/active-roadmap.md` are acceptable fallbacks. Do not place the codebase current-state entrypoint under `docs/construct/`.

## Cross-Agent Bridge

`AGENTS.md` and `.agents/skills/` are the source of truth. Codex loads them natively; Claude Code loads `CLAUDE.md` and `.claude/skills/` instead, so Vento bootstrap proposes two pointer-only bridge files:

- `CLAUDE.md` containing a single `@AGENTS.md` import line.
- `.claude/skills` as a relative symlink to `.agents/skills`.

No content is duplicated; both agents read the same assets. `vento validate` reports missing bridge files as warnings.

## Install In Codex

Clone this repository to the standard local plugin path:

```bash
mkdir -p ~/plugins
git clone <repo-url> ~/plugins/vento
```

Ensure the personal marketplace contains this entry at `~/.agents/plugins/marketplace.json`:

```json
{
  "name": "vento",
  "source": {
    "source": "local",
    "path": "./plugins/vento"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

If the marketplace file does not exist, create it with this root shape:

```json
{
  "name": "personal",
  "interface": {
    "displayName": "Personal"
  },
  "plugins": [
    {
      "name": "vento",
      "source": {
        "source": "local",
        "path": "./plugins/vento"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

Then install from the personal marketplace:

```bash
codex plugin add vento@personal
```

Start a new Codex thread after installing or updating the plugin.

## Install In Claude Code

The repository doubles as a Claude Code plugin marketplace via `.claude-plugin/`, coexisting with the Codex layout in `.codex-plugin/`.

Register the marketplace and install:

```bash
claude plugin marketplace add ~/plugins/vento
claude plugin install vento@vento
```

The same commands are available inside a session as `/plugin marketplace add` and `/plugin install`. Start a new Claude Code session after installing or updating the plugin.

## Validate

When the local Codex skill validator is available:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/plugins/vento/skills/vento
```

Vento also includes lightweight local checks:

```bash
python3 skills/vento/scripts/inventory_project.py
python3 skills/vento/scripts/validate_vento_project.py .
```

The root-level `scripts/` entries are compatibility wrappers for the bundled skill scripts.
