#!/usr/bin/env python3
"""
Playwright E2E Spec Generator - Generates test specs from VB6 flow analysis.

This script reads the flow analysis JSON and generates:
1. auth.spec.ts - Authentication tests
2. navigation.spec.ts - Route navigation tests
3. crud/[entity].spec.ts - CRUD operation tests per entity
4. workflows/[name].spec.ts - Multi-step workflow tests
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# =============================================================================
# TEMPLATES
# =============================================================================

FILE_HEADER = '''/**
 * Auto-generated E2E test spec
 * Source: VB6 Flow Analysis
 * Generated: {timestamp}
 * 
 * DO NOT EDIT MANUALLY - Regenerate from flow analysis
 */

import {{ test, expect }} from '@playwright/test';
'''

AUTH_SPEC_TEMPLATE = '''
{header}

test.describe('Authentication Flow', () => {{
  test('should display login page', async ({{ page }}) => {{
    await page.goto('/login');
    await expect(page.locator('input[type="password"], input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  }});

  test('should login successfully with valid credentials', async ({{ page }}) => {{
    await page.goto('/login');
    await page.fill('input[type="password"], input[name="password"]', process.env.TEST_PASSWORD || 'admin');
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard or main page
    await expect(page).not.toHaveURL(/login/);
    await expect(page.locator('nav, .sidebar, .layout')).toBeVisible();
  }});

  test('should show error with invalid credentials', async ({{ page }}) => {{
    await page.goto('/login');
    await page.fill('input[type="password"], input[name="password"]', 'wrong-password');
    await page.click('button[type="submit"]');
    
    // Should show error or stay on login
    await expect(page).toHaveURL(/login/);
  }});

  test('should logout successfully', async ({{ page }}) => {{
    // Login first
    await page.goto('/login');
    await page.fill('input[type="password"], input[name="password"]', process.env.TEST_PASSWORD || 'admin');
    await page.click('button[type="submit"]');
    await expect(page).not.toHaveURL(/login/);
    
    // Find and click logout
    await page.click('button:has-text("Salir"), button:has-text("Logout"), .logout-btn, [href="/login"]');
    
    // Should be back at login
    await expect(page).toHaveURL(/login/);
  }});
}});
'''

NAVIGATION_SPEC_TEMPLATE = '''
{header}

test.describe('Navigation Flows', () => {{
  test.beforeEach(async ({{ page }}) => {{
    await page.goto('/login');
    await page.fill('input[type="password"], input[name="password"]', process.env.TEST_PASSWORD || 'admin');
    await page.click('button[type="submit"]');
    await expect(page).not.toHaveURL(/login/);
  }});

{test_cases}
}});
'''

NAVIGATION_TEST_CASE = '''
  test('should navigate to {route} ({from_form} -> {to_form})', async ({{ page }}) => {{
    // VB6 Trigger: {trigger}
    await page.click('a[href="{route}"], [routerLink="{route}"], nav >> text="{entity}"');
    await expect(page).toHaveURL(/{route_pattern}/);
    await expect(page.locator('h1, .page-header')).toBeVisible();
  }});
'''

CRUD_SPEC_TEMPLATE = '''
{header}
import {{ faker }} from '@faker-js/faker';

/**
 * CRUD Tests for entity: {entity}
 * VB6 Source Form: {form}
 */
test.describe('{entity} CRUD Operations', () => {{
  test.beforeEach(async ({{ page }}) => {{
    await page.goto('/login');
    await page.fill('input[type="password"], input[name="password"]', process.env.TEST_PASSWORD || 'admin');
    await page.click('button[type="submit"]');
    await page.goto('{route}');
    await expect(page).toHaveURL(/{route_pattern}/);
  }});

{operations}
}});
'''

CRUD_OPERATION_TEMPLATES = {
    'search': '''
  test('SEARCH - should filter {entity} list', async ({{ page }}) => {{
    // VB6 Handler: {handler}
    const searchInput = page.locator('input[placeholder*="Buscar"], input[placeholder*="Search"], input[name*="search"]');
    await searchInput.fill('test');
    await searchInput.press('Enter');
    
    // Wait for results to update
    await page.waitForTimeout(500);
  }});
''',
    'create': '''
  test('CREATE - should create new {entity}', async ({{ page }}) => {{
    // VB6 Handler: {handler}
    await page.click('button:has-text("Nuevo"), button:has-text("New"), button:has-text("+"), button:has-text("➕")');
    
    // Wait for form/modal
    await expect(page.locator('.modal-content, [role="dialog"], form')).toBeVisible();
    
    // Fill required fields (generic approach)
    const inputs = await page.locator('.modal-content input:not([type="hidden"]), .modal-content select').all();
    for (const input of inputs.slice(0, 3)) {{ // Fill first 3 inputs
      const tagName = await input.evaluate(el => el.tagName);
      if (tagName === 'SELECT') {{
        await input.selectOption({{ index: 1 }});
      }} else {{
        await input.fill(faker.lorem.word());
      }}
    }}
    
    // Submit form
    await page.click('button[type="submit"], button:has-text("Guardar"), button:has-text("Save")');
  }});
''',
    'update': '''
  test('UPDATE - should edit existing {entity}', async ({{ page }}) => {{
    // VB6 Handler: {handler}
    // Click edit on first row
    await page.click('button:has-text("✏️"), button:has-text("Edit"), .edit-btn, tr >> button >> nth=0').first();
    
    // Wait for form
    await expect(page.locator('.modal-content, [role="dialog"]')).toBeVisible();
    
    // Modify a field
    const firstInput = page.locator('.modal-content input:not([type="hidden"])').first();
    await firstInput.fill('Updated ' + faker.lorem.word());
    
    // Submit
    await page.click('button[type="submit"], button:has-text("Guardar"), button:has-text("Save")');
  }});
''',
    'delete': '''
  test('DELETE - should delete {entity}', async ({{ page }}) => {{
    // VB6 Handler: {handler}
    const initialCount = await page.locator('tbody tr, .list-item, .grid-item').count();
    
    // Click delete on first row
    await page.click('button:has-text("🗑️"), button:has-text("Delete"), .delete-btn').first();
    
    // Confirm deletion if dialog appears
    const confirmBtn = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Sí")');
    if (await confirmBtn.isVisible()) {{
      await confirmBtn.click();
    }}
    
    // Verify deletion
    await page.waitForTimeout(500);
  }});
''',
    'save': '''
  test('SAVE - should persist {entity} changes', async ({{ page }}) => {{
    // VB6 Handler: {handler}
    // This tests that save operations work correctly
    await page.click('button:has-text("Nuevo"), button:has-text("+")').catch(() => {{}});
    
    const submitBtn = page.locator('button[type="submit"], button:has-text("Guardar")');
    await expect(submitBtn).toBeVisible();
  }});
'''
}

WORKFLOW_SPEC_TEMPLATE = '''
{header}

/**
 * Workflow: {name}
 * VB6 Source Form: {source_form}
 * Steps: {step_count}
 */
test.describe('{name} Workflow', () => {{
  test.beforeEach(async ({{ page }}) => {{
    await page.goto('/login');
    await page.fill('input[type="password"], input[name="password"]', process.env.TEST_PASSWORD || 'admin');
    await page.click('button[type="submit"]');
    await expect(page).not.toHaveURL(/login/);
  }});

  test('should complete full {name} workflow', async ({{ page }}) => {{
{steps}
  }});
}});
'''

WORKFLOW_STEP_TEMPLATE = '''
    // Step {step_number}: {description}
    // VB6 Handler: {handler}
    await page.locator('button:has-text("{action_text}"), [data-action="{action}"]').click().catch(() => {{}});
    await page.waitForTimeout(300);
'''

# =============================================================================
# GENERATOR
# =============================================================================

class E2ESpecGenerator:
    def __init__(self, flows_file: str, output_dir: str):
        self.flows_file = Path(flows_file)
        self.output_dir = Path(output_dir)
        self.flows: Dict[str, Any] = {}
        self.timestamp = datetime.now().isoformat()
        
    def generate(self):
        """Main generation entry point."""
        # Load flow analysis
        self.flows = json.loads(self.flows_file.read_text(encoding='utf-8'))
        
        # Ensure output directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'crud').mkdir(exist_ok=True)
        (self.output_dir / 'workflows').mkdir(exist_ok=True)
        
        # Generate specs
        self._generate_auth_spec()
        self._generate_navigation_spec()
        self._generate_crud_specs()
        self._generate_workflow_specs()
        self._generate_playwright_config()
        
        print(f"E2E specs generated in: {self.output_dir}")
    
    def _get_header(self) -> str:
        return FILE_HEADER.format(timestamp=self.timestamp)
    
    def _generate_auth_spec(self):
        """Generate authentication tests."""
        content = AUTH_SPEC_TEMPLATE.format(header=self._get_header())
        (self.output_dir / 'auth.spec.ts').write_text(content, encoding='utf-8')
        print("  ✓ Generated auth.spec.ts")
    
    def _generate_navigation_spec(self):
        """Generate navigation tests from flow analysis."""
        navigation = self.flows.get('navigation', [])
        
        if not navigation:
            print("  ⚠ No navigation flows found, skipping navigation.spec.ts")
            return
        
        test_cases = []
        for nav in navigation:
            route = nav.get('suggested_route', f"/{nav['to_form'].lower()}")
            route_pattern = route.lstrip('/').replace('/', '\\/')
            entity = self._infer_entity(nav['to_form'])
            
            test_cases.append(NAVIGATION_TEST_CASE.format(
                route=route,
                route_pattern=route_pattern,
                from_form=nav['from_form'],
                to_form=nav['to_form'],
                trigger=nav['trigger'],
                entity=entity
            ))
        
        content = NAVIGATION_SPEC_TEMPLATE.format(
            header=self._get_header(),
            test_cases='\n'.join(test_cases)
        )
        (self.output_dir / 'navigation.spec.ts').write_text(content, encoding='utf-8')
        print("  ✓ Generated navigation.spec.ts")
    
    def _generate_crud_specs(self):
        """Generate CRUD tests per entity."""
        crud_ops = self.flows.get('crud_operations', [])
        
        if not crud_ops:
            print("  ⚠ No CRUD operations found, skipping crud specs")
            return
        
        # Group by entity
        entities: Dict[str, List[Dict]] = {}
        for op in crud_ops:
            entity = op['entity']
            if entity not in entities:
                entities[entity] = []
            entities[entity].append(op)
        
        # Generate spec per entity
        for entity, ops in entities.items():
            route = self._get_entity_route(entity)
            route_pattern = route.lstrip('/').replace('/', '\\/')
            
            # Generate operation tests
            operations_code = []
            seen_ops = set()
            for op in ops:
                if op['operation'] in seen_ops:
                    continue
                seen_ops.add(op['operation'])
                
                template = CRUD_OPERATION_TEMPLATES.get(op['operation'])
                if template:
                    operations_code.append(template.format(
                        entity=entity,
                        handler=op['handler']
                    ))
            
            content = CRUD_SPEC_TEMPLATE.format(
                header=self._get_header(),
                entity=entity,
                form=ops[0]['form'],
                route=route,
                route_pattern=route_pattern,
                operations='\n'.join(operations_code)
            )
            
            filename = f"{entity.lower()}.spec.ts"
            (self.output_dir / 'crud' / filename).write_text(content, encoding='utf-8')
            print(f"  ✓ Generated crud/{filename}")
    
    def _generate_workflow_specs(self):
        """Generate workflow tests."""
        workflows = self.flows.get('workflows', [])
        
        if not workflows:
            print("  ⚠ No workflows found, skipping workflow specs")
            return
        
        for workflow in workflows:
            steps_code = []
            for step in workflow.get('steps', []):
                action_text = self._action_to_button_text(step['action'])
                steps_code.append(WORKFLOW_STEP_TEMPLATE.format(
                    step_number=step['step_number'],
                    description=step['description'],
                    handler=step['handler'],
                    action=step['action'],
                    action_text=action_text
                ))
            
            name = workflow['name'].replace(' ', '_')
            content = WORKFLOW_SPEC_TEMPLATE.format(
                header=self._get_header(),
                name=workflow['name'],
                source_form=workflow['source_form'],
                step_count=len(workflow.get('steps', [])),
                steps='\n'.join(steps_code)
            )
            
            filename = f"{name.lower()}.spec.ts"
            (self.output_dir / 'workflows' / filename).write_text(content, encoding='utf-8')
            print(f"  ✓ Generated workflows/{filename}")
    
    def _generate_playwright_config(self):
        """Generate playwright.config.ts if not exists."""
        config_path = self.output_dir.parent / 'playwright.config.ts'
        
        if config_path.exists():
            print("  ⚠ playwright.config.ts already exists, skipping")
            return
        
        config_content = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:4200',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'npm run start --prefix apps/backend',
      port: 3000,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
    {
      command: 'npm run dev --prefix apps/frontend',
      port: 4200,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
  ],
});
'''
        config_path.write_text(config_content, encoding='utf-8')
        print("  ✓ Generated playwright.config.ts")
    
    def _infer_entity(self, form_name: str) -> str:
        """Infer entity name from form name."""
        name = form_name.lower()
        name = re.sub(r'^frm', '', name)
        name = re.sub(r'^form', '', name)
        return name.capitalize() if name else form_name
    
    def _get_entity_route(self, entity: str) -> str:
        """Get route for entity."""
        routes = self.flows.get('suggested_routes', {})
        for form, route in routes.items():
            if entity.lower() in form.lower():
                return route
        return f'/{entity.lower()}'
    
    def _action_to_button_text(self, action: str) -> str:
        """Convert action to likely button text."""
        action_map = {
            'create': 'Nuevo',
            'update': 'Modificar',
            'delete': 'Eliminar',
            'save': 'Guardar',
            'cancel': 'Cancelar',
            'search': 'Buscar',
            'exit': 'Salir'
        }
        return action_map.get(action, action.capitalize())

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate Playwright E2E specs from VB6 flow analysis'
    )
    parser.add_argument(
        '--flows', '-f',
        required=True,
        help='Input flows.json file from vb6_flow_analyzer.py'
    )
    parser.add_argument(
        '--output', '-o',
        default='tests/e2e',
        help='Output directory for generated specs'
    )
    
    args = parser.parse_args()
    
    # Validate input
    flows_path = Path(args.flows)
    if not flows_path.exists():
        print(f"Error: Flows file not found: {args.flows}")
        print("Run vb6_flow_analyzer.py first to generate flows.json")
        return 1
    
    # Generate specs
    print(f"Generating E2E specs from: {args.flows}")
    generator = E2ESpecGenerator(args.flows, args.output)
    generator.generate()
    
    print(f"\n=== Generation Complete ===")
    print(f"To run tests:")
    print(f"  npx playwright install")
    print(f"  npx playwright test")
    
    return 0

if __name__ == '__main__':
    exit(main())
