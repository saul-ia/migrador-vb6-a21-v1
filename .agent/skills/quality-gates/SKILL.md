---
name: quality-gates
description: Validation rules to ensure migration quality.
allowed-tools: run_command
---

# Quality Gates

Before marking any migration task as "Done":

## Frontend Checks
1.  **Linting**: Run `ng lint`. No errors allowed.
2.  **Compiling**: Run `ng build`. Must succeed.
3.  **Responsive**: Check layouts on mobile viewport width (375px) via DevTools logic.

## Backend Checks
1.  **Types**: Run `tsc --noEmit`. No strict type errors.
2.  **Tests**: Run `npm test`. All generated tests must pass.
3.  **Security**: No hardcoded secrets.

## Database Checks
1.  **Integrity**: Foreign keys must be valid. No orphaned records from the migration.
2.  **Data Loss**: `Count(Source Rows)` == `Count(Target Rows)`.
