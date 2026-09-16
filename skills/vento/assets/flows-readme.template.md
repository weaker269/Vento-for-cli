# Project Operating Flows

## Purpose and scope

Describe which implemented system behaviors these flow assets explain, who should
read them, and which behavior is intentionally outside the current scope.

## Registered assets

- `flows.json`: Vento lifecycle manifest, source scopes, renderer, and verification status.
- `flow-model.json`: evidence-backed scenarios, ordered behavior, decisions, messages, and states.
- `system-overview.mmd`: generated Mermaid overview of the primary operating path.

Add scenario-specific Mermaid files only when they answer a separate maintenance or
troubleshooting question. Link them from this list.

## Evidence and maintenance

List the primary source, tests, schemas, configuration, and construct documents used
to confirm the represented behavior. Keep current implementation separate from future
design. Run `flows.py check` after behavior changes and update only affected scenarios.

Generating Mermaid source does not prove visual readability. Record real rendering
and visual review in `flows.json`; leave them `unverified` when no rendered artifact
was inspected.
