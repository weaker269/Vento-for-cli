# Vento

Vento is a portable Codex plugin for bootstrapping and maintaining AI-ready project knowledge.

It provides one main skill, `vento`, with these modes:

- `vento bootstrap`: set up baseline project AI guidance.
- `vento skills`: create, update, audit, validate, or deprecate project `.agents/skills`.
- `vento roadmap`: initialize, update, replace, rotate, or inspect project roadmaps.
- `vento validate`: run read-only structural checks for Vento assets.
- `vento refresh`: audit cross-asset factual drift and plan updates.

## Install As A Local Personal Plugin

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

## Validate

When the local Codex system validators are available:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py ~/plugins/vento
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/plugins/vento/skills/vento
```

Vento also includes lightweight local checks:

```bash
python3 scripts/inventory_project.py
python3 scripts/validate_vento_project.py .
```

