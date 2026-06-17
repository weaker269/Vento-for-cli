# Project Skill Rules

Project skills are long-lived task indexes for future agents.

## Good Project Skills

Good skills are specific to a project scenario:

- local development and environment setup
- test selection and validation
- backend route/auth/security boundaries
- frontend UI and DTO conventions
- data model and resource lifecycle
- deployment or production troubleshooting
- capability or integration workflows
- runtime or protocol boundaries

Only create categories that exist in the current project.

## Bad Project Skills

Avoid skills that only say:

- write clean code
- follow SOLID
- run tests
- use clear names

Those belong in general instructions, not project skills, unless tied to project-specific files or commands.

## Deprecation

When a skill becomes obsolete, prefer marking it deprecated or moving it to an archive path with a replacement pointer. Delete only when the user explicitly asks.

