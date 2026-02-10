---
name: migration-reporting
description: Migration documentation and HTML report generation. Scans migration artifacts across all phases and produces interactive visual reports.
allowed-tools: view_file, list_dir, grep_search, run_command, write_to_file
---

# Migration Reporting

> Visual documentation for VB6-to-Angular migration processes.
> **Produce clear, traceable, interactive HTML reports.**

---

## 🎯 Selective Reading Rule

**Read ONLY files relevant to the request!** Check the content map, find what you need.

---

## 📑 Content Map

| File | Description | When to Read |
|------|-------------|--------------|
| `SKILL.md` | This file — principles and overview | Always |
| `scripts/migration_report_generator.py` | HTML report generator script | When generating reports |

---

## Core Principles

### 1. Traceability

Every migrated artifact must trace back to its VB6 origin:

```
VB6 Form (frmClientes.frm)
  → Angular Component (clientes-list.component.ts)
  → Backend Service (clientes.service.ts)
  → Prisma Model (Cliente)
  → API Route (/api/clientes)
```

### 2. Phase-by-Phase Reporting

Migration has 5 phases. Each phase gets its own section:

| Phase | Input Artifacts | Report Content |
|-------|----------------|----------------|
| **1. Analysis** | `analysis/*.json`, `VB6_*.md` | File inventory, metrics, risks |
| **2. Database** | `schema.prisma`, seed logs | Table mapping, type conversions |
| **3. Backend** | Services, controllers, routes | API endpoints, CRUD coverage |
| **4. Frontend** | Components, services, templates | Component tree, form mapping |
| **5. Testing** | Test output, coverage JSON | Pass/fail, coverage % |

### 3. Visual Clarity

Reports use:
- ✅ Green for completed/passing items
- ⚠️ Amber for warnings/partial items
- ❌ Red for failures/missing items
- Progress bars for phase completion
- Cards for grouped information
- Tables for entity mappings

### 4. Self-Contained HTML

Reports are single-file HTML with embedded CSS. No external dependencies — they open in any browser offline.

---

## Report Sections

### Main Dashboard

| Section | Data Source |
|---------|------------|
| Phase Progress | Scan all phase directories |
| Entity Map | `VB6_INVENTORY.md` + Angular component list |
| Database Map | `VB6_DATABASE.md` + `schema.prisma` |
| API Summary | `swagger.json` or route file scan |
| Test Results | Test output logs + coverage JSON |
| Risk Registry | `VB6_RISKS.md` |

### Phase Detail Pages

Each phase page includes:
- Objectives and scope
- Artifact inventory (files generated)
- Before/after comparison
- Metrics (LOC, entity count, coverage)
- Status indicators

---

## Script

| Script | Purpose | Command |
|--------|---------|---------|
| `scripts/migration_report_generator.py` | Generate HTML migration reports | `python scripts/migration_report_generator.py --project-dir <path> --analysis-dir <path> --output <path>/results/MIGRATION_REPORT.html` |

---

## Anti-Patterns

❌ Placeholder text in reports ("TODO", "TBD", "Coming soon")
❌ External CSS/JS dependencies
❌ Reports without timestamps
❌ Missing phase sections
❌ Entity counts that don't match source

---

## Decision Checklist

Before generating reports:

- [ ] All migration phases have completed (or have partial output)?
- [ ] Analysis artifacts exist?
- [ ] Backend artifacts exist?
- [ ] Frontend artifacts exist?
- [ ] Test output exists?
- [ ] Output path (results/) is writable?

---

> **Remember:** Migration reports are the project's historical record. They must be accurate, complete, and visually clear enough for any stakeholder to understand the migration outcome at a glance.
