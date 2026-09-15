# Vento

Vento is a portable plugin for Codex and Claude Code, bootstrapping and maintaining AI-ready project knowledge.

It provides one main skill, `vento`, with these modes:

- `vento bootstrap`: set up baseline project AI guidance.
- `vento skills`: create, update, audit, validate, or deprecate project skills in the authoritative host's native directory.
- `vento roadmap`: initialize, update, replace, rotate, or inspect project roadmaps.
- `vento architecture`: initialize, inspect, review, and maintain project architecture diagrams.
- `vento validate`: run read-only structural checks for Vento assets.
- `vento refresh`: audit cross-asset factual drift and plan updates.

## Default Asset Layout

Vento separates AI-facing current facts from human-facing construction docs:

- `AGENTS.md` or `CLAUDE.md`: the first host's native project rules, authorization boundaries, entry points, and maintenance gates.
- `.agents/skills/<skill-name>/SKILL.md` or `.claude/skills/<skill-name>/SKILL.md`: task-specific project playbooks owned by the first host.
- `docs/productization/codebase-current-state.md`: concise AI/agent current-state entrypoint.
- `docs/construct/<topic>.md`: topic-based system construction docs for flows, state, data, and invariants.
- `docs/construct/architecture/`: optional architecture diagram assets and their Vento maintenance manifest.
  The recommended set is `architecture.json` + `architecture-model.json` + generated
  `system.ir.json`/`system.drawio` views.
- `docs/productization/active-roadmap.md`: active demand and prioritization source.

For lighter projects, `docs/codebase-current-state.md` and `docs/roadmap/active-roadmap.md` are acceptable fallbacks. Do not place the codebase current-state entrypoint under `docs/construct/`.

## Native-First Cross-Agent Support

Vento initializes only the active host's native project assets:

- Codex-first project: `AGENTS.md` and `.agents/skills`.
- Claude Code-first project: `CLAUDE.md` and `.claude/skills`.

It does not create `AGENTS.md` during a Claude-only bootstrap, and it does not
create `CLAUDE.md` during a Codex-only bootstrap. When the second host is later
added, Vento preserves the first host as authoritative and creates pointers rather
than duplicate rule/skill copies:

- Codex first: `CLAUDE.md` imports `@AGENTS.md`, and `.claude/skills` may link to
  `../.agents/skills`.
- Claude Code first: a pointer-only `AGENTS.md` tells Codex to read `CLAUDE.md`,
  and `.agents/skills` may link to `../.claude/skills`.

If both sides already contain independent content, Vento reports a split-brain
conflict and waits for an explicit authority/merge decision. `vento validate`
accepts native-only projects and validates bridges only when both hosts are present.

Claude Code loads the installed plugin's `skills/` directory as namespaced skills
such as `/vento:vento`. A plugin-root `CLAUDE.md` is not used as project context;
the target project's own `CLAUDE.md` remains the Claude-native guidance entrypoint.

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
claude plugin marketplace add /home/wenct/myself/vento
claude plugin install vento@vento --scope user --yes
```

For a Git checkout, replace the local path with the repository path or GitHub
source accepted by `claude plugin marketplace add`. The same commands are
available inside a session as `/plugin marketplace add` and `/plugin install`.

Verify the installed plugin and its skill inventory:

```bash
claude plugin list --json
claude plugin details vento@vento
```

When the marketplace source changes, update the existing installation instead of
creating a second copy:

```bash
claude plugin marketplace update vento
claude plugin update vento@vento --scope user --yes
claude plugin enable vento@vento --scope user
```

If an older cache or a disabled selector is blocking the new version, use the
scoped reinstall flow:

```bash
claude plugin uninstall vento@vento --scope user
claude plugin install vento@vento --scope user --yes
claude plugin enable vento@vento --scope user
```

Start a new Claude Code session after install or update. The plugin skill is
invoked with the namespace `/vento:vento`; project-specific rules continue to be
loaded from the target project's native `CLAUDE.md` or `AGENTS.md`, not copied
into the plugin.

Validate the Claude package from the Vento source tree:

```bash
python3 scripts/validate_claude_plugin.py .
claude plugin validate .
```

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

Architecture diagrams are opt-in project assets. Use Architecture mode only after an
explicit initialization request. Once a project has a manifest at
`docs/construct/architecture/architecture.json` (or a documented compatible path),
`vento refresh` checks architecture-impacting changes and proposes an incremental
drawio-skill sync. It does not create a diagram for projects that have not opted in.
The manifest also records its links into the current-state document, construct index,
and the authoritative `AGENTS.md` or `CLAUDE.md` when guidance exists; an unlinked diagram is reported as
documentation drift rather than being treated as a complete project map.

Prefer a small set of purpose-specific views over one source dump. A context view
should answer the system-boundary question, a container view should answer the
major-runtime-block question, and dynamic/deployment/data views should be created
only when they answer a separate question. Use `view_contracts` in the manifest to
set the intended audience, question, and node/edge limits for each view.

The root-level `scripts/` entries are compatibility wrappers for the bundled skill scripts.
