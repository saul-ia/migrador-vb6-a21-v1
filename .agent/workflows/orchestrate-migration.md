---
description: Master workflow orchestrating the full VB6 to Angular migration in phases.
---

// turbo-all

# Orchestrate Migration Workflow v2.0

## Migration Phases

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: ANALYSIS (vb6-analyst)                        │
│  Output: Documentation ONLY                             │
│  ✓ No code generation                                   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
                  [Human Review]
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: BACKEND (backend-architect)                   │
│  Output: Prisma + DTOs + Services + Controllers + API   │
│  ✓ Unified DB + Backend                                 │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
                  [swagger.json]
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE 3: FRONTEND (angular-architect)                  │
│  Input: swagger.json + VB6 form analysis                │
│  Output: Angular components + services                  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE 4: VERIFICATION                                  │
│  Testing + Quality checks                               │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 1: Analysis

**Agent:** `vb6-analyst`
**Workflow:** `/audit-legacy`

```bash
# Run all analysis scripts
python .agent/scripts/vb6_comprehensive_scanner.py "source" -o analysis/inventory.json --pretty
python .agent/scripts/vb6_metrics_analyzer.py "source" -o analysis/metrics.json --pretty
python .agent/scripts/vb6_dead_code_detector.py "source" -o analysis/dead_code.json --pretty
python .agent/scripts/vb6_hardcoded_extractor.py "source" -o analysis/hardcoded.json --pretty
python .agent/scripts/vb6_dependency_graph.py "source" -o analysis/deps.json --html analysis/GRAPH.html
python .agent/scripts/vb6_schema_extractor.py "source" -o analysis/schema.json --pretty
```

**Output Artifacts:**
- `VB6_INVENTORY.md`
- `VB6_LOGIC_ANALYSIS.md`
- `VB6_DEPENDENCIES.md`
- `VB6_RISKS.md`
- `VB6_DATABASE.md`
- `VB6_CLASSIFICATION.md`
- `VB6_SEAMS.md`
- `VB6_ROADMAP.md`

**Gate:** ⏸️ Human review required before Phase 2

---

## Phase 2: Backend

**Agent:** `backend-architect`

**Input:** Analysis artifacts (VB6_DATABASE.md, VB6_LOGIC_ANALYSIS.md)

**Generation Order:**
1. `prisma/schema.prisma`
2. `backend/types/*.dto.ts`
3. `backend/services/*.service.ts`
4. `backend/controllers/*.controller.ts`
5. `backend/routes/*.routes.ts`
6. `swagger.json`

**Validation:**
```bash
npx prisma validate
npx prisma generate
npx tsc --noEmit
```

**Gate:** Backend must compile and Swagger must be valid

---

## Phase 3: Frontend

**Agent:** `angular-architect`

**Input:** 
- `swagger.json` (from Phase 2)
- `VB6_LOGIC_ANALYSIS.md` (UI patterns)

**Generation Order:**
1. `src/app/models/*.ts`
2. `src/app/services/*.service.ts`
3. `src/app/components/**/*`
4. `src/app/app.routes.ts`

**Validation:**
```bash
ng lint
ng build --configuration development
```

---

## Phase 4: Verification

```bash
# Backend tests
npm run test:backend

# Frontend tests
ng test --watch=false

# E2E tests
ng e2e

# Build production
ng build --configuration production
```

---

## Quick Reference: Agents

| Phase | Agent | Purpose |
|-------|-------|---------|
| 1 | `vb6-analyst` | Analysis, documentation ONLY |
| 2 | `backend-architect` | Unified DB + API generation |
| 3 | `angular-architect` | Frontend from Swagger contract |
