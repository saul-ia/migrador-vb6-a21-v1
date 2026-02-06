---
description: Deep analysis of VB6 codebase. Produces documentation artifacts. FULLY AUTOMATED.
---

// turbo-all

# Audit Legacy Workflow v6.0 (Fully Automated)

## Execution Mode

| Setting | Value |
|---------|-------|
| **Confirmation Required** | ❌ NO |
| **Auto-Continue** | ✅ YES |

---

## Step 1: Create Output Directory

```bash
mkdir -p analysis
```

---

## Step 2: Run All Scanners (Auto)

```bash
python .agent/scripts/vb6_comprehensive_scanner.py "vb6-source" -o analysis/01_inventory.json --pretty
python .agent/scripts/vb6_metrics_analyzer.py "vb6-source" -o analysis/02_metrics.json --pretty
python .agent/scripts/vb6_dead_code_detector.py "vb6-source" -o analysis/03_dead_code.json --pretty
python .agent/scripts/vb6_hardcoded_extractor.py "vb6-source" -o analysis/04_hardcoded.json --pretty
python .agent/scripts/vb6_dependency_graph.py "vb6-source" -o analysis/05_dependencies.json --html analysis/DEPENDENCY_GRAPH.html
python .agent/scripts/vb6_schema_extractor.py "vb6-source" -o analysis/06_schema.json --pretty
python .agent/scripts/html_report_generator.py analysis/01_inventory.json -o analysis/ANALYSIS_REPORT.html
```

---

## Step 3: Generate Documentation (Auto)

Agent `vb6-analyst` generates:

| Document | Purpose |
|----------|---------|
| `VB6_INVENTORY.md` | Complete file catalog |
| `VB6_LOGIC_ANALYSIS.md` | Code classification |
| `VB6_DEPENDENCIES.md` | Coupling matrix |
| `VB6_RISKS.md` | Risk assessment |
| `VB6_DATABASE.md` | Schema documentation |
| `VB6_CLASSIFICATION.md` | Migration priority |
| `VB6_SEAMS.md` | Strangler Pattern points |
| `VB6_ROADMAP.md` | Migration order |

---

## Step 4: Auto-Continue

After analysis completes, automatically proceed to:
- `/migrate-db` for database migration
- `/migrate-ui` for UI component generation

**No human review gate.** Analysis artifacts are produced for reference but execution continues.

---

## Output Structure

```
analysis/
├── 01_inventory.json
├── 02_metrics.json
├── 03_dead_code.json
├── 04_hardcoded.json
├── 05_dependencies.json
├── 06_schema.json
├── DEPENDENCY_GRAPH.html
├── ANALYSIS_REPORT.html
├── VB6_INVENTORY.md
├── VB6_LOGIC_ANALYSIS.md
├── VB6_DEPENDENCIES.md
├── VB6_RISKS.md
├── VB6_DATABASE.md
├── VB6_CLASSIFICATION.md
├── VB6_SEAMS.md
└── VB6_ROADMAP.md
```
