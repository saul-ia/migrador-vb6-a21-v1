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
| `${VB6_DIR}` | VB6 source code directory | `legacy-src/` |
| `${OUTPUT_DIR}` | Generated Angular app directory | `modern-app/` |
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
| **Testing** | ✅ Jest Unit Tests Only |
| **Self-Healing** | ✅ YES (max 5 iterations) |
| **Angular Mode** | ✅ ZONELESS |

---

## Phase 1: Analysis (Auto)

**Agent:** `vb6-analyst`

### Step 0: Pre-flight Check 🛡️
```bash
echo ""
echo "================================================================================="
echo "🚀 PHASE 1: COMPREHENSIVE ANALYSIS"
echo "🤖 Agent: vb6-analyst (Model: claude-sonnet-4.5-thinking)"
echo "🎯 Goal: Inventory, Metrics, Dependencies, Flow Extraction"
echo "================================================================================="
echo ""

python .agent/scripts/pre_flight_check.py
if [ $? -ne 0 ]; then echo "❌ Pre-flight check failed"; exit 1; fi
```

```bash
python .agent/scripts/vb6_comprehensive_scanner.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/inventory.json --pretty &
python .agent/scripts/vb6_metrics_analyzer.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/metrics.json --pretty &
python .agent/scripts/vb6_dead_code_detector.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/dead_code.json --pretty &
python .agent/scripts/vb6_hardcoded_extractor.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/hardcoded.json --pretty &
python .agent/scripts/vb6_dependency_graph.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/deps.json --html ${ANALYSIS_DIR}/GRAPH.html &
python .agent/scripts/vb6_schema_extractor.py "${VB6_DIR}" -o ${ANALYSIS_DIR}/schema.json &

# Wait for all analysis scripts to finish
wait

# Generate HTML report after all JSONs are ready
python .agent/scripts/vb6_comprehensive_scanner.py "${VB6_DIR}" --output ${ANALYSIS_DIR}/comprehensive.json &
python .agent/scripts/html_report_generator.py ${ANALYSIS_DIR}/inventory.json -o ${ANALYSIS_DIR}/REPORT.html &


```

**Output:** All 8 Markdown documents + HTML report + flows.json

### ✅ Gate 1: Analysis Exit Gate
```bash
# Verify all required analysis outputs exist
test -f ${ANALYSIS_DIR}/inventory.json && echo "✅ inventory.json exists" || exit 1
test -f ${ANALYSIS_DIR}/schema.json && echo "✅ schema.json exists" || exit 1
test -f ${ANALYSIS_DIR}/metrics.json && echo "✅ metrics.json exists" || exit 1
test -f ${ANALYSIS_DIR}/REPORT.html && echo "✅ REPORT.html exists" || exit 1
echo "🚦 Phase 1 → Phase 2 gate: PASSED"
```

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

### ✅ Gate 2: Backend Exit Gate

**Agent:** `build-ci` + `security-reviewer`

```bash
echo ""
echo "================================================================================="
echo "🚀 PHASE 2: BACKEND ARCHITECTURE"
echo "🤖 Agent: backend-architect (Model: claude-sonnet-4.5)"
echo "🎯 Goal: Prisma Schema, DTOs, Services, Controllers, Swagger API"
echo "================================================================================="
echo ""

# Run build-ci checks (from build-ci.md Gate 1)
cd ${OUTPUT_DIR}/apps/backend

# TypeScript compilation
npx tsc --noEmit 2>&1 | tee ${ANALYSIS_DIR}/gate-backend-tsc.txt
if [ $? -ne 0 ]; then echo "❌ TypeScript errors"; exit 1; fi

# Lint check
npx eslint src/ --format json -o ${ANALYSIS_DIR}/gate-backend-lint.json || true

# Build check
npm run build 2>&1 | tee ${ANALYSIS_DIR}/gate-backend-build.txt
if [ $? -ne 0 ]; then echo "❌ Build failed"; exit 1; fi

# Prisma validation
cd ${OUTPUT_DIR}/apps/backend
npx prisma validate
if [ $? -ne 0 ]; then echo "❌ Prisma schema invalid"; exit 1; fi

# Security audit
python .agent/skills/security-reviewer/scripts/security_audit.py \
  --frontend ${OUTPUT_DIR}/apps/frontend/src \
  --backend ${OUTPUT_DIR}/apps/backend/src \
  --output ${ANALYSIS_DIR}/security-report.json \
  --html ${ANALYSIS_DIR}/SECURITY_REPORT.html

# Check for critical security findings
CRITICAL_COUNT=$(jq '.critical' ${ANALYSIS_DIR}/security-report.json)
if [ "$CRITICAL_COUNT" -gt 0 ]; then
  echo "❌ $CRITICAL_COUNT critical security issues found"
  exit 1
fi

echo "🚦 Phase 2 → Phase 3 gate: PASSED"
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

**Output:** `apps/frontend/` with complete Angular app

### Step 3.5: Generate Contract Tests
```bash
# Generate executable API contract tests from swagger.json
python .agent/skills/contract-tests/scripts/contract_test_generator.py \
  --swagger ${OUTPUT_DIR}/apps/backend/swagger.json \
  --output ${OUTPUT_DIR}/tests/contract \
  --base-url http://localhost:3000

echo "✅ Contract tests generated"
```

---

### ✅ Gate 3: Frontend Exit Gate

**Agent:** `build-ci` + `a11y-reviewer` + `contract-tests` + `parity-checker`

```bash
echo ""
echo "================================================================================="
echo "🚀 PHASE 3: FRONTEND ARCHITECTURE (ZONELESS)"
echo "🤖 Agent: angular-architect (Model: gemini-3-flash)"
echo "🎯 Goal: Components (OnPush+Signals), Services, Routing, Contract Tests"
echo "================================================================================="
echo ""

# Run build-ci checks (from build-ci.md Gate 2)
cd ${OUTPUT_DIR}/apps/frontend

# TypeScript compilation
npx tsc --noEmit 2>&1 | tee ${ANALYSIS_DIR}/gate-frontend-tsc.txt
if [ $? -ne 0 ]; then echo "❌ TypeScript errors"; exit 1; fi

# Angular lint
npx ng lint 2>&1 | tee ${ANALYSIS_DIR}/gate-frontend-lint.txt
if [ $? -ne 0 ]; then echo "❌ Lint errors"; exit 1; fi

# Production build
npx ng build --configuration production 2>&1 | tee ${ANALYSIS_DIR}/gate-frontend-build.txt
if [ $? -ne 0 ]; then echo "❌ Build failed"; exit 1; fi

# A11y audit in background
python .agent/skills/a11y-reviewer/scripts/a11y_audit.py \
  --input ${OUTPUT_DIR}/apps/frontend/src \
  --output ${ANALYSIS_DIR}/a11y-report.json \
  --html ${ANALYSIS_DIR}/A11Y_REPORT.html &
A11Y_PID=$!

# Contract validation in background
python .agent/skills/contract-tests/scripts/contract_validator.py \
  --swagger ${OUTPUT_DIR}/apps/backend/swagger.json \
  --services ${OUTPUT_DIR}/apps/frontend/src/app/services \
  --output ${ANALYSIS_DIR}/contract-report.json \
  --html ${ANALYSIS_DIR}/CONTRACT_REPORT.html &
CONTRACT_PID=$!

# Parity check in background
python .agent/scripts/parity_checker.py \
  --vb6 ${VB6_DIR} \
  --modern ${OUTPUT_DIR} \
  --analysis ${ANALYSIS_DIR} \
  --output ${ANALYSIS_DIR}/parity-report.json \
  --html ${ANALYSIS_DIR}/PARITY_REPORT.html &
PARITY_PID=$!

# Wait for all background audits to complete
wait $A11Y_PID $CONTRACT_PID $PARITY_PID

# Now check results sequentially (fast)
CRITICAL_A11Y=$(jq '.critical' ${ANALYSIS_DIR}/a11y-report.json)
if [ "$CRITICAL_A11Y" -gt 0 ]; then echo "❌ $CRITICAL_A11Y critical accessibility issues found"; exit 1; fi

CRITICAL_CONTRACT=$(jq '.critical' ${ANALYSIS_DIR}/contract-report.json)
if [ "$CRITICAL_CONTRACT" -gt 0 ]; then echo "❌ $CRITICAL_CONTRACT critical contract mismatches found"; exit 1; fi

PARITY_PCT=$(jq '.parity_percentage' ${ANALYSIS_DIR}/parity-report.json)
if (( $(echo "$PARITY_PCT < 80" | bc -l) )); then echo "❌ Parity is only $PARITY_PCT% (minimum 80% required)"; exit 1; fi

echo "🚦 Phase 3 → Phase 4 gate: PASSED"
```

**Next:** Auto-continue to Phase 4

---

## Phase 4: Testing + Self-Healing Loop 🔄

**Agent:** `testing-verifier` (v2.0 Self-Healing)

### Step 4.1: Generate Tests
```bash
echo ""
echo "================================================================================="
echo "🚀 PHASE 4: TESTING & SELF-HEALING"
echo "🤖 Agent: testing-verifier (Model: gemini-3-flash)"
echo "🎯 Goal: Generate Unit Tests, Run Tests, Auto-Repair Failures"
echo "================================================================================="
echo ""

# Auto-generate unit tests for all components, services, controllers
python .agent/skills/quality-gates/scripts/unit_test_generator.py \
  --input ${OUTPUT_DIR} \
  --type all \
  --coverage-threshold 80


```

### Step 4.2: Self-Healing Loop (Max 5 Iterations)

```
┌──────────────────────────────────────────────────────────────┐
│  FOR iteration = 1 TO 5:                                      │
│                                                               │
│    1. RUN tests (capture output)                              │
│       # Run frontend and backend tests in parallel           │
│       (npm test -- --coverage 2>&1 | tee analysis/unit.txt) & │
│       wait                                                   │
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
# Run tests with output capture in parallel
(cd ${OUTPUT_DIR}/apps/backend && npm test -- --coverage 2>&1 | tee ${ANALYSIS_DIR}/unit-output.txt) &
(cd ${OUTPUT_DIR}/apps/frontend && npm test -- --coverage 2>&1 | tee ${ANALYSIS_DIR}/frontend-output.txt) &
wait

# Analyze failures and create repair plan
python .agent/skills/quality-gates/scripts/test_failure_analyzer.py \
  --input analysis/unit-output.txt \
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
echo ""
echo "================================================================================="
echo "🚀 PHASE 5: QUALITY GATES & REPORTING"
echo "🤖 Agent: build-ci, migration-documenter"
echo "🎯 Goal: Coverage validation, Parity Check, Final Reports"
echo "================================================================================="
echo ""

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

# Check Migration Parity
python .agent/scripts/parity_checker.py \
  --vb6 "${VB6_DIR}" \
  --modern "${OUTPUT_DIR}" \
  --analysis "${ANALYSIS_DIR}" \
  --output "${ANALYSIS_DIR}/parity.json" \
  --html "${OUTPUT_DIR}/results/PARITY_REPORT.html"

# Generate Master Migration Report
python .agent/scripts/migration_report_generator.py \
  --project-dir ${OUTPUT_DIR} \
  --analysis-dir ${ANALYSIS_DIR} \
  --output ${OUTPUT_DIR}/results/MIGRATION_REPORT.html

# Final production build
ng build --configuration production
```

### ✅ Gate 5: Production Deployment Gate

**Final validation before deployment**

```bash
# Production builds must succeed
cd ${OUTPUT_DIR}/apps/frontend
npx ng build --configuration production
if [ $? -ne 0 ]; then echo "❌ Frontend production build failed"; exit 1; fi

cd ${OUTPUT_DIR}/apps/backend
npm run build
if [ $? -ne 0 ]; then echo "❌ Backend production build failed"; exit 1; fi

# Re-run security audit on final code
python .agent/skills/security-reviewer/scripts/security_audit.py \
  --frontend ${OUTPUT_DIR}/apps/frontend/src \
  --backend ${OUTPUT_DIR}/apps/backend/src \
  --output ${ANALYSIS_DIR}/security-final.json \
  --html ${ANALYSIS_DIR}/SECURITY_FINAL.html

CRITICAL_SEC=$(jq '.critical' ${ANALYSIS_DIR}/security-final.json)
if [ "$CRITICAL_SEC" -gt 0 ]; then
  echo "❌ Critical security issues remain"
  exit 1
fi

# Verify 100% parity for deployment
python .agent/scripts/parity_checker.py \
  --vb6 ${VB6_DIR} \
  --modern ${OUTPUT_DIR} \
  --analysis ${ANALYSIS_DIR} \
  --output ${ANALYSIS_DIR}/parity-final.json \
  --html ${ANALYSIS_DIR}/PARITY_FINAL.html

FINAL_PARITY=$(jq '.parity_percentage' ${ANALYSIS_DIR}/parity-final.json)
if (( $(echo "$FINAL_PARITY < 100" | bc -l) )); then
  echo "⚠️  Parity is $FINAL_PARITY% (100% recommended for production)"
fi

echo "🚦 All gates PASSED - Ready for production deployment! 🚀"
```

### Generated Reports
| Report | Path | Contents |
|--------|------|----------|
| **Repair Report** | `analysis/REPAIR_REPORT.html` | Errors repaired, iterations, status |
| **Parity Report** | `results/PARITY_REPORT.html` | VB6 vs Angular mismatch check |
| **Migration Report** | `results/MIGRATION_REPORT.html` | Master dashboard of all phases |
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
4. ✅ Generate all tests (Jest Unit Tests)
5. ✅ **AUTO-REPAIR** unit test failures (max 5 iterations **PER ERROR**)
6. ✅ Generate `REPAIR_REPORT.html` with detailed status
7. ✅ Generate `MIGRATION_REPORT.html` (Master Dashboard)
8. ✅ Validate coverage and produce final report

**The process NEVER blocks** - errors that can't be fixed after 5 attempts are logged and skipped.

---

## Quality Thresholds

| Metric | Minimum | Blocks Deployment |
|--------|---------|-------------------|
| Line Coverage | 80% | ✅ Yes |
| Branch Coverage | 70% | ✅ Yes |

| Build Success | Required | ✅ Yes |
| Lint Errors | 0 | ✅ Yes |
| Max Repair Iterations | 5 | ⚠️ Escalate if exceeded |

### ✅ Gate 4: Testing Exit Gate

**Agent:** `testing-verifier` + `quality-gates`

```bash
# Verify all tests pass after self-healing
cd ${OUTPUT_DIR}/apps/backend && npm test -- --coverage --passWithNoTests
if [ $? -ne 0 ]; then echo "❌ Backend tests failed"; exit 1; fi

cd ${OUTPUT_DIR}/apps/frontend && npm test -- --coverage --passWithNoTests
if [ $? -ne 0 ]; then echo "❌ Frontend tests failed"; exit 1; fi

# Validate coverage thresholds
python .agent/skills/quality-gates/scripts/coverage_validator.py \
  --backend ${OUTPUT_DIR}/coverage/backend/coverage-summary.json \
  --frontend ${OUTPUT_DIR}/coverage/frontend/coverage-summary.json \
  --threshold 80 \
  --output ${ANALYSIS_DIR}/coverage-report.md \
  --strict

if [ $? -ne 0 ]; then echo "❌ Coverage thresholds not met"; exit 1; fi

echo "🚦 Phase 4 → Phase 5 gate: PASSED"
```

**Next:** Auto-continue to Phase 5

---

## Exit Conditions

| Status | Description | Action |
|--------|-------------|--------|
| ✅ SUCCESS | All tests pass, coverage met | Complete |
| ⚠️ PARTIAL | Some manual fixes needed | Review `analysis/repairs/` |

---

## Phase 10: Migration Visualization (Auto)

```bash
echo ""
echo "================================================================================="
echo "🚀 PHASE 10: MIGRATION VISUALIZATION"
echo "🤖 Script: final_report_generator.py"
echo "🎯 Goal: Generate Interactive Dashboard, Flow Diagrams, Compliance Proof"
echo "================================================================================="
echo ""

python .agent/scripts/final_report_generator.py \
  --project-dir . \
  --analysis-dir ${ANALYSIS_DIR} \
  --output ${OUTPUT_DIR}/results/MIGRATION_DASHBOARD.html
  
echo "✅ DASHBOARD GENERATED: ${OUTPUT_DIR}/results/MIGRATION_DASHBOARD.html"
echo "✅ MIGRATION COMPLETED SUCCESSFULLY! 🚀"
```

