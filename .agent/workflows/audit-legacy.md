---
description: Analyzes the VB6 codebase to generate a migration report.
---

# Audit Legacy Workflow

1.  **Initialize**: Check if `src/vb6` folder exists.
2.  **Scan Forms**: Run `vb6-analyst` on all `*.frm` files.
    *   Count controls.
    *   List external dependencies.
3.  **Scan Modules**: Run `vb6-analyst` on `*.bas` files.
    *   List global variables.
4.  **Report**: Generate `AUDIT_REPORT.md` summarizing complexity and "Unknowns".
