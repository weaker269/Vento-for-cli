# Vento Roadmap

Use this mode for project roadmap lifecycle: init, update, replace, rotate, status, archive, deprecate, and migration of unfinished work.

## Actions

- `init`: create the first active roadmap.
- `update`: update the current active roadmap without replacing it.
- `replace`: create a new active roadmap and mark the old one deprecated.
- `rotate`: replace an oversized active roadmap, usually after the line-count gate triggers.
- `status`: read-only summary of active/deprecated roadmap state.

## Roadmap Boundaries

- Roadmap answers "what should be done".
- Spec answers "how it should be designed".
- Plan answers "how to execute it".
- Current-state docs answer "what is true in current code".

Do not put unimplemented roadmap plans into current-state docs.

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

