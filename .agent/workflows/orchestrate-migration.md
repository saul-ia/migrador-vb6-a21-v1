---
description: Master workflow orchestrating the full VB6 to Angular migration in phases. FULLY AUTOMATED with SELF-HEALING tests.
---

// turbo-all

# Orchestrate Migration Workflow v5.0 (Self-Healing)

> [!IMPORTANT]
> This workflow runs **FULLY AUTOMATED** without human confirmation gates.
> All entities will be migrated completely, not just samples.
> **NEW:** Includes **SELF-HEALING** testing - automatically fixes test failures!

## Configuration Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `${VB6_DIR}` | VB6 source code directory | `vb6-apps/` |
| `${OUTPUT_DIR}` | Generated Angular app directory | `my-app/` |
| `${ANALYSIS_DIR}` | Analysis output directory | `analysis/` |

> [!TIP]
> Set these variables before running the workflow to customize paths for your project.

## Migration Phases

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: ANALYSIS (vb6-analyst)                        │
│  Output: Documentation + Flow Analysis                  │
│  ✓ Runs automatically                                   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼ (auto-continue)
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: BACKEND (backend-architect)                   │
│  Output: Prisma + DTOs + Services + Controllers + API   │
│  ✓ ALL entities generated                               │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼ (auto-continue)
┌─────────────────────────────────────────────────────────┐
│  PHASE 3: FRONTEND (angular-architect) - ZONELESS       │
│  Input: swagger.json + VB6 form analysis                │
│  Output: ALL Angular components + services (Signals)    │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼ (auto-continue)
┌─────────────────────────────────────────────────────────┐
│  PHASE 4: TESTING + SELF-HEALING LOOP 🔄                │
│  Generate tests → Run → Analyze failures → Auto-fix     │
│  Max iterations: 5                                      │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼ (auto-continue)
┌─────────────────────────────────────────────────────────┐
│  PHASE 5: QUALITY GATES                                 │
│  Final coverage validation + Production build           │
└─────────────────────────────────────────────────────────┘
```

---

## Execution Mode

| Setting | Value |
|---------|-------|
| **Confirmation Required** | ❌ NO |
| **Migration Scope** | 🔄 COMPLETE (all entities) |
| **Auto-Continue** | ✅ YES |
| **Sample Mode** | ❌ DISABLED |
| **Testing** | ✅ Playwright + Jest |
| **Self-Healing** | ✅ YES (max 5 iterations) |
| **Angular Mode** | ✅ ZONELESS |

---

## Phase 1: Analysis (Auto)

**Agent:** `vb6-analyst`

```bash
python .agent/scripts/vb6_comprehensive_scanner.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/inventory.json --pretty
python .agent/scripts/vb6_metrics_analyzer.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/metrics.json --pretty
python .agent/scripts/vb6_dead_code_detector.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/dead_code.json --pretty
python .agent/scripts/vb6_hardcoded_extractor.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/hardcoded.json --pretty
python .agent/scripts/vb6_dependency_graph.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/deps.json --html ${ANALYSIS_DIR}/GRAPH.html
python .agent/scripts/vb6_schema_extractor.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/schema.json
python .agent/scripts/html_report_generator.py ${ANALYSIS_DIR}/inventory.json -o ${ANALYSIS_DIR}/REPORT.html

# Extract flows for E2E testing
python .agent/skills/e2e-verification/scripts/vb6_flow_analyzer.py --input ${VB6_DIR}/ --output ${ANALYSIS_DIR}/flows.json
```

**Output:** All 8 Markdown documents + HTML report + flows.json
**Next:** Auto-continue to Phase 2

---

## Phase 2: Backend (Auto)

**Agent:** `backend-architect`

**Generate ALL entities:**
1. `prisma/schema.prisma` - Complete schema with ALL tables
2. `backend/types/*.dto.ts` - DTOs for ALL entities
3. `backend/services/*.service.ts` - Services for ALL entities
4. `backend/controllers/*.controller.ts` - Controllers for ALL entities
5. `backend/routes/*.routes.ts` - Routes for ALL entities
6. `swagger.json` - Complete API specification

**Validation (auto):**
```bash
npx prisma validate
npx prisma migrate dev --name init
npx prisma generate
npx tsc --noEmit
```

**Next:** Auto-continue to Phase 3

---

## Phase 3: Frontend - ZONELESS (Auto)

**Agent:** `angular-architect` (v4.0 Zoneless)

**Generate ALL components with:**
- ✅ `standalone: true`
- ✅ `changeDetection: ChangeDetectionStrategy.OnPush`
- ✅ All state using `signal()`
- ✅ `provideExperimentalZonelessChangeDetection()` in app.config

**Validation (auto):**
```bash
ng lint
ng build --configuration development
```

**Next:** Auto-continue to Phase 4

---

## Phase 4: Testing + Self-Healing Loop 🔄

**Agent:** `testing-verifier` (v2.0 Self-Healing)

### Step 4.1: Generate Tests
```bash
# E2E Tests
python .agent/skills/e2e-verification/scripts/generate_e2e_specs.py \
  --flows ${ANALYSIS_DIR}/flows.json \
  --output ${OUTPUT_DIR}/tests/e2e

# Unit Tests
python .agent/skills/quality-gates/scripts/generate_jest_specs.py \
  --services ${OUTPUT_DIR}/apps/backend/src/services \
  --controllers ${OUTPUT_DIR}/apps/backend/src/controllers \
  --angular-services ${OUTPUT_DIR}/apps/frontend/src/app/services \
  --angular-components ${OUTPUT_DIR}/apps/frontend/src/app/components \
  --output ${OUTPUT_DIR}/tests/unit

# Install Playwright
cd ${OUTPUT_DIR} && npx playwright install chromium
```

### Step 4.2: Self-Healing Loop (Max 5 Iterations)

```
┌──────────────────────────────────────────────────────────────┐
│  FOR iteration = 1 TO 5:                                      │
│                                                               │
│    1. RUN tests (capture output)                              │
│       npm test -- --coverage 2>&1 | tee analysis/unit.txt    │
│       npx playwright test 2>&1 | tee analysis/e2e.txt        │
│                                                               │
│    2. CHECK: All tests pass?                                  │
│       IF YES → EXIT LOOP ✅                                   │
│       IF NO  → CONTINUE to step 3                             │
│                                                               │
│    3. ANALYZE failures                                        │
│       python test_failure_analyzer.py --input analysis/*.txt  │
│       → Creates repair_plan_XXX.json                          │
│                                                               │
│    4. APPLY auto-fixes                                        │
│       Read repair_plan_XXX.json                               │
│       For each auto-fixable error:                            │
│         - View file with problem                              │
│         - Apply fix using replace_file_content                │
│         - Log change                                          │
│                                                               │
│    5. LOOP to step 1 with iteration++                         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Self-Healing Commands

```bash
# Run tests with output capture
cd ${OUTPUT_DIR}/apps/backend && npm test -- --coverage 2>&1 | tee ${ANALYSIS_DIR}/unit-output.txt
cd ${OUTPUT_DIR}/apps/frontend && npm test -- --coverage 2>&1 | tee ${ANALYSIS_DIR}/frontend-output.txt
cd ${OUTPUT_DIR} && npx playwright test 2>&1 | tee ${ANALYSIS_DIR}/e2e-output.txt

# Analyze failures and create repair plan
python .agent/skills/quality-gates/scripts/test_failure_analyzer.py \
  --input analysis/unit-output.txt \
  --output analysis/repairs \
  --max-iterations 5

python .agent/skills/quality-gates/scripts/test_failure_analyzer.py \
  --input analysis/e2e-output.txt \
  --output analysis/repairs \
  --max-iterations 5
```

### Auto-Fixable Patterns

| Error | Detection | Auto-Fix |
|-------|-----------|----------|
| Missing import | `Cannot find module` | Add import statement |
| Missing provider | `NullInjectorError` | Add to providers |
| Zoneless violation | `NG0100` | Use `effect()` |
| Missing signal | `Cannot read undefined` | Initialize signal |
| OnPush missing | `NG0500/501` | Add OnPush |
| Selector mismatch | `Timeout waiting` | Update selector |

**Next:** Auto-continue to Phase 5

---

## Phase 5: Quality Gates + Reports (Auto)

**Final Validation:**
```bash
# Generate self-healing repair report (HTML + JSON)
python .agent/skills/quality-gates/scripts/repair_report_generator.py \
  --repairs-dir analysis/repairs \
  --output analysis/REPAIR_REPORT.html \
  --json-output analysis/repair-summary.json \
  --max-iterations 5

# Validate coverage
python .agent/skills/quality-gates/scripts/coverage_validator.py \
  --backend ${OUTPUT_DIR}/coverage/backend/coverage-summary.json \
  --frontend ${OUTPUT_DIR}/coverage/frontend/coverage-summary.json \
  --threshold 80 \
  --output ${ANALYSIS_DIR}/coverage-report.md \
  --strict

# Final production build
ng build --configuration production
```

### Generated Reports
| Report | Path | Contents |
|--------|------|----------|
| **Repair Report** | `analysis/REPAIR_REPORT.html` | Errors repaired, iterations, status |
| **Coverage Report** | `analysis/coverage-report.md` | Test coverage metrics |
| **Repair Summary** | `analysis/repair-summary.json` | JSON for automation |

---

## Execution Command

To run the complete migration with self-healing:

```bash
# From project root
/orchestrate-migration
```

The migration will:
1. ✅ Run all analysis scripts (including flow extraction)
2. ✅ Generate complete backend (all entities)
3. ✅ Generate complete frontend (ZONELESS, all components)
4. ✅ Generate all tests (Playwright E2E + Jest Unit)
5. ✅ **AUTO-REPAIR** test failures (max 5 iterations **PER ERROR**)
6. ✅ Generate `REPAIR_REPORT.html` with detailed status
7. ✅ Validate coverage and produce final report

**The process NEVER blocks** - errors that can't be fixed after 5 attempts are logged and skipped.

---

## Quality Thresholds

| Metric | Minimum | Blocks Deployment |
|--------|---------|-------------------|
| Line Coverage | 80% | ✅ Yes |
| Branch Coverage | 70% | ✅ Yes |
| E2E Flow Coverage | 100% | ✅ Yes |
| Build Success | Required | ✅ Yes |
| Lint Errors | 0 | ✅ Yes |
| Max Repair Iterations | 5 | ⚠️ Escalate if exceeded |

---

## Exit Conditions

| Status | Description | Action |
|--------|-------------|--------|
| ✅ SUCCESS | All tests pass, coverage met | Complete |
| ⚠️ PARTIAL | Some manual fixes needed | Review `analysis/repairs/` |
| ❌ MAX_ITERATIONS | 5 repair cycles exceeded | Manual intervention required |

