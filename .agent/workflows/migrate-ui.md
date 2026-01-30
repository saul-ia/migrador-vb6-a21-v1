---
description: Migrates a specific VB6 Form to an Angular Component.
---

# Migrate UI Workflow

Input: `FORM_NAME` (e.g., Login.frm)

1.  **Parse**: Call `vb6-analyst` to read `src/vb6/FORM_NAME`.
    *   Output: `specs/FORM_NAME.json`
2.  **Generate**: Call `angular-architect` with the JSON spec.
    *   Output: `src/app/components/FORM_NAME/`
3.  **Verify**: Run `ng lint` on the new component.
4.  **Wait**: Pause for user review of the generated UI.
