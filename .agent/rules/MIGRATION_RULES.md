# Migration Rules

> These rules are MANDATORY for all agents working on the LegacyLift migration.

## 1. Code Quality
*   **TypeScript Strictness**: `strict: true` in `tsconfig.json`. No `any`. Use `unknown` with narrowing if necessary.
*   **Comments**: Do NOT copy VB6 comments unless they explain complex business logic. Remove "Created by" headers.
*   **Formatting**: Prettier default settings.

## 2. Architecture
*   **No Logic in Controllers**: Controllers inputs -> Service -> Output.
*   **No SQL in Code**: Use Prisma ORM methods. `db.query("SELECT...")` is forbidden.
*   **Signals**: All Angular components uses Signals for state.

## 3. Database
*   **WAL Mode**: SQLite must be in WAL mode.
*   **UTC/ISO**: All dates must be stored as ISO strings or Unix Timestamps (BigInt).
*   **Soft Deletes**: If the VB6 app had a `Deleted` flag, implement it as `deletedAt: DateTime?`.

## 4. UX/UI
*   **Responsive**: All forms must work on Mobile (375px+).
*   **Feedback**: Long operations must show a Spinner/Skeleton.
*   **Theme**: Use the defined Angular Material Theme.
