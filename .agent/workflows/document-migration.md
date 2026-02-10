---
description: Generate interactive HTML migration reports. Scans all phase artifacts and produces visual dashboard in results/. FULLY AUTOMATED.
---

// turbo-all

# Document Migration Workflow v1.0 (Fully Automated)

## Execution Mode

| Setting | Value |
|---------|-------|
| **Confirmation Required** | ❌ NO |
| **Scope** | 🔄 ALL PHASES |
| **Auto-Continue** | ✅ YES |

---

## Step 1: Create Output Directory

```bash
mkdir -p results
```

---

## Step 2: Scan Migration Artifacts

Agent `migration-documenter` scans:

| Phase | Directory | Artifacts |
|-------|-----------|-----------|
| Analysis | `analysis/` | `*.json`, `VB6_*.md` |
| Database | `prisma/` | `schema.prisma` |
| Backend | `backend/src/` | services, controllers, routes |
| Frontend | `src/app/` | components, services |
| Testing | `analysis/` | test output, coverage JSON |

---

## Step 3: Generate HTML Reports (Auto)

```bash
python .agent/skills/migration-reporting/scripts/migration_report_generator.py \
  --project-dir . \
  --analysis-dir ./analysis \
  --output ./results/MIGRATION_REPORT.html
```

---

## Step 4: Verify Output (Auto)

```bash
# Verify report was generated
ls -la results/MIGRATION_REPORT.html

# Verify file is non-empty
test -s results/MIGRATION_REPORT.html && echo "✅ Report generated successfully" || echo "❌ Report is empty"
```

---

## Output Structure

```
results/
└── MIGRATION_REPORT.html    # Interactive dashboard with:
    ├── Phase progress overview
    ├── Statistics cards
    ├── Analysis artifacts table
    ├── Database model mapping
    ├── Backend API inventory
    ├── Frontend component inventory
    └── Test coverage metrics
```

---

## When to Use

- After completing any migration phase (partial reports are supported)
- After running `/orchestrate-migration` (full report)
- After running `/audit-legacy` (analysis-only report)
- Anytime stakeholders need a visual summary of migration progress

---

## Auto-Continue

After report generation, display the output path and open instructions.

**No confirmation required.**
