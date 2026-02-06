---
description: Run automated E2E tests to verify migrated Angular app against VB6 flows
---

# E2E Verification Workflow

This workflow automatically verifies that all VB6 user flows have been correctly migrated to Angular.

## Configuration Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `${VB6_DIR}` | VB6 source directory | `vb6-apps/` |
| `${OUTPUT_DIR}` | Generated Angular app directory | `my-angular-app/` |
| `${ANALYSIS_DIR}` | Analysis output directory | `analysis/` |

## Prerequisites
- VB6 source files in `${VB6_DIR}` directory
- Angular app built and running
- Backend server running

## Steps

### 1. Analyze VB6 Flows
// turbo
```bash
python .agent/skills/e2e-verification/scripts/vb6_flow_analyzer.py --input ${VB6_DIR} --output ${ANALYSIS_DIR}/flows.json
```

### 2. Generate E2E Specs
// turbo
```bash
python .agent/skills/e2e-verification/scripts/generate_e2e_specs.py --flows ${ANALYSIS_DIR}/flows.json --output ${OUTPUT_DIR}/tests/e2e
```

### 3. Install Playwright
// turbo
```bash
cd ${OUTPUT_DIR} && npx playwright install chromium
```

### 4. Start Backend Server
```bash
cd ${OUTPUT_DIR}/apps/backend && npm run start
```

### 5. Start Frontend Server
```bash
cd ${OUTPUT_DIR}/apps/frontend && npm run dev
```

### 6. Run E2E Tests
// turbo
```bash
cd ${OUTPUT_DIR} && npx playwright test
```

### 7. Generate Report
// turbo
```bash
cd ${OUTPUT_DIR} && npx playwright show-report
```

## Output

After running this workflow:
- `${ANALYSIS_DIR}/flows.json` - Extracted VB6 flows
- `${OUTPUT_DIR}/tests/e2e/` - Generated Playwright specs
- `${OUTPUT_DIR}/playwright-report/` - HTML test report

## Troubleshooting

### Tests fail due to selectors
The generated tests use generic selectors. For custom UI, update:
- Button text patterns in `generate_e2e_specs.py`
- Route patterns in `flows.json`

### Server not starting
Ensure ports 3000 (backend) and 4200 (frontend) are free.


