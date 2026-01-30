---
name: legacy-decoding
description: Techniques for parsing and decoding VB6 codebase artifacts.
allowed-tools: view_file, grep_search
---

# Legacy Decoding Manual

## The "FRM" Format
VB6 Forms (`.frm`) are structured text files.
*   **Header**: `VERSION 5.00`
*   **Object Definitions**: `Begin VB.Form Form1 ... End`
*   **Properties**: Nested within objects. `Caption = "Hello"`.
*   **Code**: After the object definitions, the VBA code begins.

## Key Patterns to Detect
1.  **Control Arrays**: `TEXTBOX(0)`, `TEXTBOX(1)`. Map these to `<input *ngFor...>`
2.  **Twips**: VB6 uses Twips (1/1440 inch).
    *   Formula: `Pixels = Twips / 15` (approx).
3.  **Events**:
    *   `Form_Load` -> `ngOnInit`
    *   `Command_Click` -> `(click)="save()"`
    *   `LostFocus` -> `(blur)`

## Common Traps
*   `On Error Resume Next`: This swallows errors. When migrating, remove it and add proper Try/Catch or let errors bubble up.
*   `DoEvents`: Used to keep UI responsive. In JS/Angular, this is handled by the Event Loop automatically. Remove it.
