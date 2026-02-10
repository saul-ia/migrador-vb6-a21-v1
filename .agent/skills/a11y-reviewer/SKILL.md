---
name: a11y-reviewer
description: Automated accessibility audit for migrated Angular applications. WCAG 2.1 AA compliance checker.
---

# Accessibility Reviewer Skill v1.0

## Purpose

Automated WCAG 2.1 Level AA compliance checks for Angular applications migrated from VB6.
VB6 desktop apps have zero web accessibility — this skill ensures the migration adds it.

## When to Use

Run after Phase 3 (frontend generation) as part of quality gates.

## Accessibility Rules

### Critical (Block Deployment)

| ID | Rule | What to Check |
|----|------|---------------|
| A11Y-001 | All images have `alt` attributes | `<img>` without `alt` |
| A11Y-002 | Form inputs have labels | `<input>` without `<label>` or `aria-label` |
| A11Y-003 | Buttons have accessible names | `<button>` without text or `aria-label` |
| A11Y-004 | Color contrast ratio ≥ 4.5:1 | Text on background colors |
| A11Y-005 | Page has exactly one `<h1>` | Multiple or missing `<h1>` |
| A11Y-006 | Heading hierarchy is correct | Skipping levels (h1 → h3) |
| A11Y-007 | Interactive elements are keyboard accessible | Missing `tabindex` or handlers |
| A11Y-008 | ARIA roles are valid | Invalid `role` attributes |

### Warning (Review Recommended)

| ID | Rule | What to Check |
|----|------|---------------|
| A11Y-W01 | Skip navigation link | Missing "skip to content" |
| A11Y-W02 | Focus indicators visible | `outline: none` without alternative |
| A11Y-W03 | Language attribute set | Missing `lang` on `<html>` |
| A11Y-W04 | Tables have headers | `<table>` without `<th>` |
| A11Y-W05 | Error messages are announced | Missing `aria-live` regions |

## VB6 → Angular A11y Mapping

| VB6 Control | Angular Equivalent | A11y Requirement |
|-------------|-------------------|------------------|
| `Label` | `<label for="...">` | Must reference input |
| `TextBox` | `<input>` + `<label>` | Label + aria-describedby |
| `CommandButton` | `<button>` | Visible text or aria-label |
| `ComboBox` | `<mat-select>` | Label + aria-label |
| `DataGrid` | `<mat-table>` | Column headers in `<th>` |
| `MsgBox` | `MatDialog` | Focus trap + aria-modal |

## Usage

```bash
python .agent/skills/a11y-reviewer/scripts/a11y_audit.py \
  --input ${OUTPUT_DIR}/apps/frontend/src \
  --output ${ANALYSIS_DIR}/a11y-report.json \
  --html ${ANALYSIS_DIR}/A11Y_REPORT.html
```

## Output

- `${ANALYSIS_DIR}/a11y-report.json` — Machine-readable results
- `${ANALYSIS_DIR}/A11Y_REPORT.html` — Visual HTML report
