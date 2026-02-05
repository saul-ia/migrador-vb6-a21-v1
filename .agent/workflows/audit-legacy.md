---
description: Deep analysis of VB6 codebase. Produces ONLY documentation artifacts. NO code generation.
---

// turbo-all

# Audit Legacy Workflow v5.0 (Analysis-Only)

## ⚠️ CRITICAL: This phase produces DOCUMENTATION ONLY

**Output:** Markdown reports, JSON data, HTML visualizations
**NOT Output:** Angular code, TypeScript, backend code

---

## Phase Objective

Perform **exhaustive analysis** to fully understand the legacy codebase before ANY code is written. All findings documented for human review.

---

## Step 1: Automated Scanning

```bash
cd migrador-vb6-a21-v1

# Create output directory
mkdir -p analysis_output

# 1. File inventory
python .agent/scripts/vb6_comprehensive_scanner.py "path/to/vb6" \
    -o analysis_output/01_inventory.json --pretty

# 2. Metrics analysis
python .agent/scripts/vb6_metrics_analyzer.py "path/to/vb6" \
    -o analysis_output/02_metrics.json --pretty

# 3. Dead code detection
python .agent/scripts/vb6_dead_code_detector.py "path/to/vb6" \
    -o analysis_output/03_dead_code.json --pretty

# 4. Hardcoded values
python .agent/scripts/vb6_hardcoded_extractor.py "path/to/vb6" \
    -o analysis_output/04_hardcoded.json --pretty

# 5. Dependency graph
python .agent/scripts/vb6_dependency_graph.py "path/to/vb6" \
    -o analysis_output/05_dependencies.json \
    --html analysis_output/DEPENDENCY_GRAPH.html --pretty

# 6. Schema extraction
python .agent/scripts/vb6_schema_extractor.py "path/to/vb6" \
    -o analysis_output/06_schema.json --pretty

# 7. Visual report
python .agent/scripts/html_report_generator.py analysis_output/01_inventory.json \
    -o analysis_output/VB6_AUDIT_REPORT.html
```

---

## Step 2: Agent Analysis (NO CODE)

Using the JSON outputs, the agent produces these **documentation artifacts**:

| Artifact | Content |
|----------|---------|
| `VB6_INVENTORY.md` | Complete file catalog |
| `VB6_LOGIC_ANALYSIS.md` | Business rules, UI, data access |
| `VB6_DEPENDENCIES.md` | Coupling matrix, hub modules |
| `VB6_RISKS.md` | Risk assessment table |
| `VB6_DATABASE.md` | Schema, tables, relationships |
| `VB6_CLASSIFICATION.md` | Early/Coexist/Defer categories |
| `VB6_SEAMS.md` | Strangler pattern intercept points |
| `VB6_ROADMAP.md` | Migration order and timeline |

---

## Step 3: Human Review

Before proceeding to any code generation phase:
1. Review all generated artifacts
2. Validate classifications
3. Adjust priorities
4. Approve roadmap

---

## Output Directory Structure

```
analysis_output/
├── 01_inventory.json
├── 02_metrics.json
├── 03_dead_code.json
├── 04_hardcoded.json
├── 05_dependencies.json
├── 06_schema.json
├── VB6_AUDIT_REPORT.html
├── DEPENDENCY_GRAPH.html
├── VB6_INVENTORY.md
├── VB6_LOGIC_ANALYSIS.md
├── VB6_DEPENDENCIES.md
├── VB6_RISKS.md
├── VB6_DATABASE.md
├── VB6_CLASSIFICATION.md
├── VB6_SEAMS.md
└── VB6_ROADMAP.md
```

---

## ✅ Phase Complete When

- [ ] All scripts executed successfully
- [ ] All JSON files generated
- [ ] All markdown artifacts created
- [ ] Human review completed
- [ ] Migration roadmap approved

**ONLY THEN proceed to code generation phases.**
