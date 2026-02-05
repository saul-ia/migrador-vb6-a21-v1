# Audit Report: Biblioteca Migration

**Date**: 2026-02-03
**Source**: `vb6-apps/Biblioteca`
**Target**: `angular-app`

## 📊 Executive Summary
The legacy application is a standard **VB6 MDI (Multiple Document Interface)** system. It relies on a central Module for global logic and database connections.

| Metric | Count | Details |
| :--- | :--- | :--- |
| **Forms** | 2 | `Form1.frm`, `MDIForm1.frm` |
| **Modules** | 1 | `Module1.bas` |
| **Classes** | 0 | None found |
| **Database** | 1 | Access (`.mdb`) implied by logic |

## 🏗️ Structural Analysis

### 1. Forms
*   **MDIForm1**: Acts as the main shell/container.
    *   *Migration Stragegy*: Convert to `AppComponent` with `MatSidenav` or `MatToolbar` for navigation.
*   **Form1**: A child window.
    *   *Migration Strategy*: Convert to a routed Feature Component (`/form1`).

### 2. Logic (Module1.bas)
*   Contains global utility functions.
*   **Findings**:
    *   Database connection strings detected (`Provider=Microsoft...`).
    *   UI manipulation logic (`.Enabled = False`).
*   *Migration Strategy*:
    *   Move DB logic to `Backend/Services`.
    *   Move UI helpers to `Frontend/Shared/Utils`.

## ⚠️ Unknowns & Risks
*   **Third-party Controls**: None detected in scan.
*   **Database Path**: Hardcoded connection strings might need extraction to `.env`.

## ✅ Recommendation
Proceed with the **Standard Migration Plan**:
1.  **DB**: Migrate Access to SQLite.
2.  **Back**: Generate Services from new DB schema.
3.  **Front**: Recreate Forms using Angular Material v21.
