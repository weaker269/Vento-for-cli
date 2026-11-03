# Vento Roadmap

Use this mode for project roadmap lifecycle and its linked design specs: init, update, replace, rotate, status, archive, deprecate, spec, and migration of unfinished work.

## Actions

- `init`: create the first active roadmap.
- `update`: update the current active roadmap without replacing it.
- `replace`: create a new active roadmap and mark the old one deprecated.
- `rotate`: replace an oversized active roadmap, usually after the line-count gate triggers.
- `status`: read-only summary of active/deprecated roadmap state.
- `spec`: create or update the optional design spec linked from a roadmap item.

## Planning Chain

```text
Roadmap -> Spec (optional) -> Implementation -> Roadmap update
```

The chain applies to work worth tracking, not to every change. Small or
self-contained requests go straight to implementation without a roadmap entry. The
agent judges from scope, risk, and whether the work spans sessions or needs
prioritization; Vento does not require a roadmap item for any change.

- **Roadmap** answers "what should be done". The active roadmap is the single place
  for tracked demand, not a log of every change.
- **Spec** answers "how it should be designed". Write one only when the item
  involves design trade-offs, a shared contract/schema/protocol change, a
  cross-module boundary, or a decision future agents should not re-litigate. Other
  tracked items need only their roadmap entry.
- **Implementation** follows the roadmap item and its spec. Current-state docs
  answer "what is true in current code".
- **Roadmap update** closes the loop: update the item status, link commits and
  validation evidence, set the spec status, and move new current facts into
  current-state or construct docs.

Do not put unimplemented roadmap plans into current-state docs.

## Specs

- Default path: `docs/productization/specs/YYYY-MM-DD-<topic>.md`. Projects using
  the lightweight `docs/roadmap/active-roadmap.md` fallback use
  `docs/roadmap/specs/`.
- Create specs from `assets/spec.template.md`.
- Link the spec from its roadmap item and name the roadmap item in the spec.
- Track `Status:` as `Draft`, `Accepted`, `Implemented`, or `Superseded`. A
  superseded spec points to its replacement.
- A spec is a decision record, not a current-fact source. Current code wins over
  specs; after implementation, record current facts in current-state or construct
  docs instead of continuing to edit the spec as documentation.

## Execution Plans

Step-by-step execution plans are transient by default. Keep them in the agent's
visible task plan or the conversation, not in the repository.

Persist a plan only when the work spans multiple sessions or agents, such as a
staged migration or cutover. Store it as
`docs/productization/plans/YYYY-MM-DD-<topic>.md`, link it from the roadmap item,
and mark it completed when the item closes. A persisted plan is never a current-fact
source.

## External Workflow Tools

Vento does not depend on external workflow plugins such as Superpowers. Whichever
tool helped produce a design or plan, file the result under the Vento paths above.
Project guidance should not require an external workflow for ordinary tasks.

Tool-specific directories such as `docs/superpowers/specs/` and
`docs/superpowers/plans/` are legacy planning paths:

- keep existing links resolvable and do not move files implicitly;
- write new specs to the Vento spec path;
- Refresh and Validate report legacy paths as migration candidates, not failures;
- migrate only after explicit approval, moving files and updating every repository
  reference in the same change.

## Replacement Rules

When replacing a roadmap:

1. Read the active roadmap.
2. Confirm the user wants replacement rather than an update.
3. Preserve the old roadmap as deprecated; do not delete it.
4. Create a new active roadmap.
5. Migrate all unfinished items.
6. Keep completed, cancelled, rejected, deprecated, and superseded items in the old roadmap only.
7. Move unclear-status items into `Needs Triage`.
8. Report migration counts and unresolved ambiguity.

## Roadmap Rotation Gate

After every active roadmap update, count lines. If the active roadmap exceeds 2000 lines, report the line count and ask whether to rotate to a new active roadmap.

Rotation is a soft gate. Do not silently replace the roadmap unless the user explicitly requested direct replacement.

If rotation is approved:

- mark the old roadmap deprecated and keep it
- create a new active roadmap
- migrate all unfinished items
- verify that no unfinished item was dropped

Suggested migration report:

- pending items before rotation
- migrated into new roadmap
- needs triage
- retained in old roadmap
- dropped without migration

`Dropped without migration` must be zero before claiming migration is complete.

