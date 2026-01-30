---
description: The Master Workflow. Orchestrates the full end-to-end migration.
---

# Orchestrate Migration Workflow

1.  **Audit Phase**: Trigger workflow `/audit`.
    *   Blocking: Wait for user approval of Audit Report.
2.  **Database Phase**: Trigger workflow `/migrate-db`.
    *   Blocking: detailed schema review.
3.  **Backend Phase**:
    *   For each Table in DB:
        *   Generate DTOs.
        *   Generate Service.
        *   Generate Controller.
4.  **Frontend Phase**:
    *   For each Form in Audit:
        *   Trigger workflow `/migrate-ui`.
5.  **Final Verification**: Run `npm test` and `ng e2e`.
