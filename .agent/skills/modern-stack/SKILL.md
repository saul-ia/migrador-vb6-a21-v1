---
name: modern-stack
description: Standards and patterns for the target stack (Angular 21, Node 20, SQLite).
allowed-tools: write_to_file
---

# Modern Stack Guidelines

## Angular 21 (Frontend)
*   **Standalone**: NO `NgModule`. add `imports: [CommonModule, MatButtonModule]` directly in `@Component`.
*   **Signals**:
    ```typescript
    count = signal(0);
    double = computed(() => this.count() * 2);
    update() { this.count.update(n => n + 1); }
    ```
*   **Control Flow**: Use `@if`, `@for`, `@switch` syntax.

## Node.js + Express (Backend)
*   **Architecture**:
    *   DTOs (Data Transfer Objects) for Input/Output.
    *   Service Layer handles business logic.
    *   Controllers only parse request and send response.
*   **Async/Await**: Always use async/await. NO callbacks.

## SQLite + Prisma (Database)
*   **Schema**:
    ```prisma
    model User {
      id    Int     @id @default(autoincrement())
      email String  @unique
      posts Post[]
    }
    ```
*   **Config**: Enable WAL mode for concurrency.
