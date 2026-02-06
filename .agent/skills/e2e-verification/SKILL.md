---
name: e2e-verification
description: Generic E2E testing framework for migrated Angular apps. Automatically generates Playwright tests from VB6 flow analysis.
---

# E2E Verification Skill

## Purpose
Automatically verify that ALL user flows from the original VB6 application have been correctly migrated to the Angular app. This skill:
1. Parses VB6 forms to extract navigation and interaction patterns
2. Generates Playwright test specs dynamically
3. Runs browser-based verification of the migrated app

---

## 1. Flow Extraction from VB6

### 1.1 Navigation Flows
Extract from VB6 patterns:
```
FormName.Show          → Route navigation
Unload Me              → Route back/close
MDIForm menu items     → Sidebar/navigation menu
```

### 1.2 User Interactions
Extract from VB6 event handlers:
```
cmdXXX_Click           → Button click actions
txtXXX_Change          → Input field interactions
grillaXXX_Click        → Table/grid row selection
cmdbus_Click           → Search functionality
cmdnue_Click           → Create new entity
cmdmod_Click           → Edit entity
cmdbor_Click           → Delete entity
cmdreg_Click           → Save/submit form
cmdcan_Click           → Cancel operation
cmdsal_Click           → Exit/close
```

### 1.3 Validations
Extract from VB6 validation patterns:
```
MsgBox "...", vbCritical    → Error message expected
MsgBox "...", vbInformation → Success message expected
If fieldName = "" Then      → Required field validation
If RecordCount = 0 Then     → Empty result handling
```

---

## 2. Test Generation Strategy

### 2.1 Generate Flow Map
Run the VB6 flow analyzer to create a JSON map:
```bash
python .agent/scripts/vb6_flow_analyzer.py --input vb6-apps/ --output analysis/flows.json
```

Output structure:
```json
{
  "navigation": [
    {"from": "MDIForm1", "to": "frmCli", "trigger": "socios_Click", "route": "/clientes"}
  ],
  "crud_operations": [
    {"entity": "Cliente", "form": "FRMCLI", "operations": ["create", "read", "update", "delete"]}
  ],
  "validations": [
    {"form": "FrmPres", "field": "txtsocio", "type": "required", "message": "datos requeridos"}
  ]
}
```

### 2.2 Generate Playwright Specs
Run spec generator:
```bash
python .agent/scripts/generate_e2e_specs.py --flows analysis/flows.json --output tests/e2e/
```

### 2.3 Output Structure
```
tests/e2e/
├── auth.spec.ts          # Login/logout flows
├── navigation.spec.ts    # All navigation routes from MDI menu
├── crud/
│   ├── [entity].spec.ts  # Generated per entity (clientes, libros, etc.)
└── workflows/
    └── [workflow].spec.ts # Complex multi-step flows (prestamos, etc.)
```

---

## 3. Test Templates

### 3.1 Navigation Test Template
```typescript
import { test, expect } from '@playwright/test';

// Auto-generated from VB6 MDIForm menu analysis
test.describe('Navigation Flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="password"]', process.env.TEST_PASSWORD || 'admin');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
  });

  // Generated for each menu item
  {{#each navigation}}
  test('navigate to {{route}} from {{trigger}}', async ({ page }) => {
    await page.click('[href="{{route}}"]');
    await expect(page).toHaveURL('{{route}}');
    await expect(page.locator('h1')).toBeVisible();
  });
  {{/each}}
});
```

### 3.2 CRUD Test Template
```typescript
import { test, expect } from '@playwright/test';
import { faker } from '@faker-js/faker';

// Auto-generated for entity: {{entityName}}
test.describe('{{entityName}} CRUD Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="password"]', process.env.TEST_PASSWORD || 'admin');
    await page.click('button[type="submit"]');
    await page.goto('/{{entityRoute}}');
  });

  test('CREATE - should create new {{entityName}}', async ({ page }) => {
    await page.click('button:has-text("Nuevo"), button:has-text("New"), button:has-text("+")');
    await expect(page.locator('.modal-content, [role="dialog"]')).toBeVisible();
    
    // Fill form fields dynamically
    {{#each fields}}
    await page.fill('[name="{{name}}"]', faker.{{fakerMethod}}());
    {{/each}}
    
    await page.click('button[type="submit"]');
    await expect(page.locator('.modal-content, [role="dialog"]')).not.toBeVisible();
  });

  test('READ - should display {{entityName}} list', async ({ page }) => {
    await expect(page.locator('table, .grid, .list')).toBeVisible();
  });

  test('UPDATE - should edit existing {{entityName}}', async ({ page }) => {
    await page.click('button:has-text("✏️"), button:has-text("Edit"), .edit-btn').first();
    await expect(page.locator('.modal-content, [role="dialog"]')).toBeVisible();
    await page.click('button[type="submit"]');
  });

  test('DELETE - should delete {{entityName}}', async ({ page }) => {
    const initialCount = await page.locator('tbody tr, .list-item').count();
    await page.click('button:has-text("🗑️"), button:has-text("Delete"), .delete-btn').first();
    // Confirm deletion if dialog appears
    await page.click('button:has-text("Confirm"), button:has-text("Yes")').catch(() => {});
  });

  test('SEARCH - should filter {{entityName}} list', async ({ page }) => {
    await page.fill('input[placeholder*="Buscar"], input[placeholder*="Search"]', 'test');
    await page.press('input[placeholder*="Buscar"], input[placeholder*="Search"]', 'Enter');
  });
});
```

### 3.3 Workflow Test Template
```typescript
import { test, expect } from '@playwright/test';

// Auto-generated for workflow: {{workflowName}}
// VB6 Source: {{vb6Form}}
test.describe('{{workflowName}} Workflow', () => {
  test('complete workflow: {{description}}', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="password"]', process.env.TEST_PASSWORD || 'admin');
    await page.click('button[type="submit"]');
    
    {{#each steps}}
    // Step {{stepNumber}}: {{description}}
    // VB6: {{vb6Handler}}
    {{#if isNavigation}}
    await page.goto('{{route}}');
    {{/if}}
    {{#if isClick}}
    await page.click('{{selector}}');
    {{/if}}
    {{#if isFill}}
    await page.fill('{{selector}}', '{{value}}');
    {{/if}}
    {{#if isSelect}}
    await page.selectOption('{{selector}}', '{{value}}');
    {{/if}}
    {{#if hasExpectation}}
    await expect(page.locator('{{expectSelector}}')).{{expectMethod}}();
    {{/if}}
    {{/each}}
  });
});
```

---

## 4. Validation Assertions

### 4.1 Required Field Validation
```typescript
test('should show error for empty required fields', async ({ page }) => {
  await page.click('button:has-text("Nuevo")');
  await page.click('button[type="submit"]');
  
  // Expect HTML5 validation or custom error
  const invalidFields = await page.locator(':invalid, .error, .invalid').count();
  expect(invalidFields).toBeGreaterThan(0);
});
```

### 4.2 Entity Pre-Validation (VB6 MsgBox pattern)
```typescript
test('should warn when entity has pending items', async ({ page }) => {
  // Select entity with pending items
  await page.selectOption('[name="clienteId"]', { index: 1 });
  
  // Expect warning message (migrated from VB6 MsgBox)
  await expect(page.locator('.warning-box, .alert-warning')).toBeVisible();
});
```

---

## 5. Running Tests

### 5.1 Playwright Configuration
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  retries: 2,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:4200',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
  webServer: [
    {
      command: 'npm run start --prefix apps/backend',
      port: 3000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run dev --prefix apps/frontend',
      port: 4200,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
```

### 5.2 Run Commands
```bash
# Install Playwright
npx playwright install

# Run all E2E tests
npx playwright test

# Run with UI mode
npx playwright test --ui

# Run specific flow
npx playwright test navigation.spec.ts

# Generate HTML report
npx playwright show-report
```

---

## 6. Integration with Migration Workflow

Add to `/orchestrate-migration` workflow:
```markdown
## Phase 5: E2E Verification
1. Generate flow map from VB6 analysis
2. Generate Playwright specs from flows
3. Run E2E tests
4. Generate verification report
5. Flag any failed flows for manual review
```

---

## 7. Verification Report

Output: `analysis/e2e-verification-report.html`

Includes:
- ✅ Passed flows with screenshots
- ❌ Failed flows with video recordings
- ⚠️ Skipped flows (manual verification required)
- 📊 Coverage percentage (flows tested / flows detected)

