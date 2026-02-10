#!/usr/bin/env python3
"""
Parity Checker for VB6 → Angular migration.
Ensures every VB6 form, function, and data entity has a modern equivalent.
Generic: works with any project directory.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set


class VB6Inventory:
    """Extract inventory of VB6 forms, modules, and functions."""

    def __init__(self, vb6_dir: Path):
        self.vb6_dir = vb6_dir
        self.forms: List[str] = []
        self.modules: List[str] = []
        self.functions: List[Dict] = []
        self.db_tables: List[str] = []

    def scan(self) -> None:
        """Scan VB6 directory for all artifacts."""
        if not self.vb6_dir.exists():
            print(f'⚠️  VB6 directory not found: {self.vb6_dir}')
            return

        for file_path in self.vb6_dir.rglob('*'):
            ext = file_path.suffix.lower()
            if ext == '.frm':
                self.forms.append(file_path.stem)
                self._extract_functions(file_path)
            elif ext == '.bas':
                self.modules.append(file_path.stem)
                self._extract_functions(file_path)
            elif ext == '.cls':
                self.modules.append(file_path.stem)
                self._extract_functions(file_path)

    def _extract_functions(self, file_path: Path) -> None:
        """Extract public functions/subs from a VB6 file."""
        try:
            content = file_path.read_text(encoding='latin-1', errors='ignore')
        except Exception:
            return

        for match in re.finditer(
            r'(?:Public|Private)?\s*(Function|Sub)\s+(\w+)',
            content, re.IGNORECASE
        ):
            func_type = match.group(1)
            func_name = match.group(2)
            # Skip event handlers (Form_Load, etc.)
            if '_' in func_name and any(func_name.startswith(p) for p in ['Form_', 'cmd', 'txt', 'lst', 'cbo', 'tmr', 'mnu']):
                continue
            self.functions.append({
                'name': func_name,
                'type': func_type,
                'file': file_path.stem,
                'source': str(file_path),
            })

    def load_from_analysis(self, analysis_dir: Path) -> None:
        """Load inventory from analysis JSON files if available."""
        inventory_file = analysis_dir / 'inventory.json'
        if inventory_file.exists():
            try:
                data = json.loads(inventory_file.read_text(encoding='utf-8'))
                # Extract forms
                for form in data.get('forms', []):
                    name = form if isinstance(form, str) else form.get('name', '')
                    if name and name not in self.forms:
                        self.forms.append(name)
                # Extract modules
                for mod in data.get('modules', []):
                    name = mod if isinstance(mod, str) else mod.get('name', '')
                    if name and name not in self.modules:
                        self.modules.append(name)
            except Exception:
                pass

        schema_file = analysis_dir / 'schema.json'
        if schema_file.exists():
            try:
                data = json.loads(schema_file.read_text(encoding='utf-8'))
                if isinstance(data, dict):
                    self.db_tables = list(data.get('tables', {}).keys())
                    if not self.db_tables and 'entities' in data:
                        self.db_tables = [e.get('name', '') for e in data['entities'] if e.get('name')]
            except Exception:
                pass


class ModernInventory:
    """Extract inventory of Angular components, services, and Prisma models."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.components: List[str] = []
        self.services: List[str] = []
        self.prisma_models: List[str] = []
        self.routes: List[str] = []

    def scan(self) -> None:
        """Scan modern project for all artifacts."""
        frontend = self.output_dir / 'apps' / 'frontend' / 'src'
        backend = self.output_dir / 'apps' / 'backend' / 'src'

        # Angular components
        if frontend.exists():
            for ts_file in frontend.rglob('*.component.ts'):
                name = ts_file.stem.replace('.component', '')
                self.components.append(name)

            # Angular services
            for ts_file in frontend.rglob('*.service.ts'):
                name = ts_file.stem.replace('.service', '')
                self.services.append(name)

        # Backend routes
        if backend.exists():
            for ts_file in backend.rglob('*.routes.ts'):
                name = ts_file.stem.replace('.routes', '')
                self.routes.append(name)

        # Prisma models
        prisma_schema = self.output_dir / 'apps' / 'backend' / 'prisma' / 'schema.prisma'
        if not prisma_schema.exists():
            prisma_schema = self.output_dir / 'prisma' / 'schema.prisma'
        if prisma_schema.exists():
            try:
                content = prisma_schema.read_text(encoding='utf-8')
                for match in re.finditer(r'model\s+(\w+)\s*\{', content):
                    self.prisma_models.append(match.group(1))
            except Exception:
                pass


class ParityChecker:
    """Compare VB6 and modern inventories to find gaps."""

    # Common VB6 form → Angular component name mappings
    FORM_MAPPINGS = {
        'frm': '', 'form': '', 'dlg': '', 'dialog': '',
    }

    def __init__(self):
        self.findings: List[Dict] = []

    def check_parity(self, vb6: VB6Inventory, modern: ModernInventory) -> None:
        """Run all parity checks."""
        self._check_forms(vb6, modern)
        self._check_tables(vb6, modern)
        self._check_business_logic(vb6, modern)

    def _normalize_name(self, name: str) -> str:
        """Normalize VB6 names to match Angular naming conventions."""
        n = name.lower()
        # Remove common VB6 prefixes
        for prefix in ['frm', 'form', 'dlg', 'mod', 'cls', 'bas']:
            if n.startswith(prefix) and len(n) > len(prefix):
                n = n[len(prefix):]
        # Remove underscores, convert to lowercase
        n = n.replace('_', '').strip()
        return n

    def _check_forms(self, vb6: VB6Inventory, modern: ModernInventory) -> None:
        """Check that every VB6 form has an Angular component."""
        modern_names = {self._normalize_name(c) for c in modern.components}
        # Add common aliases
        modern_names_expanded = set()
        for name in modern_names:
            modern_names_expanded.add(name)
            modern_names_expanded.add(name.replace('-', ''))
            modern_names_expanded.add(name.replace('list', ''))
            modern_names_expanded.add(name.replace('form', ''))

        for form in vb6.forms:
            norm = self._normalize_name(form)
            # Check for any partial match
            matched = any(
                norm in m or m in norm or
                norm.rstrip('s') == m.rstrip('s')
                for m in modern_names_expanded
                if len(m) > 2
            )
            if not matched:
                self.findings.append({
                    'rule_id': 'PAR-001',
                    'rule_name': 'VB6 form without Angular component',
                    'severity': 'CRITICAL',
                    'vb6_artifact': form,
                    'vb6_type': 'Form (.frm)',
                    'expected_modern': f'{norm}.component.ts',
                    'description': f'VB6 form "{form}" has no corresponding Angular component',
                    'fix': f'Create Angular component: ng generate component {norm}',
                })

    def _check_tables(self, vb6: VB6Inventory, modern: ModernInventory) -> None:
        """Check that every DB table has a Prisma model."""
        modern_models = {m.lower() for m in modern.prisma_models}
        modern_routes = {r.lower() for r in modern.routes}

        for table in vb6.db_tables:
            norm = table.lower().strip()
            if not norm:
                continue
            if norm not in modern_models and norm.rstrip('s') not in modern_models:
                self.findings.append({
                    'rule_id': 'PAR-002',
                    'rule_name': 'DB table without Prisma model',
                    'severity': 'CRITICAL',
                    'vb6_artifact': table,
                    'vb6_type': 'Database Table',
                    'expected_modern': f'model {table.capitalize()} {{ ... }}',
                    'description': f'Access table "{table}" has no Prisma model',
                    'fix': f'Add model {table.capitalize()} to prisma/schema.prisma',
                })

            if norm not in modern_routes and norm.rstrip('s') not in modern_routes:
                self.findings.append({
                    'rule_id': 'PAR-003',
                    'rule_name': 'DB table without API route',
                    'severity': 'WARNING',
                    'vb6_artifact': table,
                    'vb6_type': 'Database Table',
                    'expected_modern': f'{norm}.routes.ts',
                    'description': f'Access table "{table}" has no backend API route',
                    'fix': f'Create route file: {norm}.routes.ts',
                })

    def _check_business_logic(self, vb6: VB6Inventory, modern: ModernInventory) -> None:
        """Check that public VB6 functions have modern counterparts."""
        modern_services = {s.lower() for s in modern.services}

        # Group functions by module
        module_functions: Dict[str, int] = {}
        for func in vb6.functions:
            mod = func['file']
            module_functions[mod] = module_functions.get(mod, 0) + 1

        for module, count in module_functions.items():
            norm = self._normalize_name(module)
            if norm not in modern_services and not any(norm in s for s in modern_services):
                self.findings.append({
                    'rule_id': 'PAR-004',
                    'rule_name': 'VB6 module without Angular service',
                    'severity': 'WARNING',
                    'vb6_artifact': module,
                    'vb6_type': f'Module ({count} functions)',
                    'expected_modern': f'{norm}.service.ts',
                    'description': f'VB6 module "{module}" ({count} functions) has no Angular service',
                    'fix': f'Create service: ng generate service {norm}',
                })

    def generate_report(self, vb6: VB6Inventory, modern: ModernInventory) -> Dict:
        """Generate summary report."""
        critical = [f for f in self.findings if f['severity'] == 'CRITICAL']
        warnings = [f for f in self.findings if f['severity'] == 'WARNING']

        total_vb6 = len(vb6.forms) + len(vb6.db_tables) + len(vb6.modules)
        total_modern = len(modern.components) + len(modern.prisma_models) + len(modern.services)

        parity_pct = 0
        if total_vb6 > 0:
            parity_pct = round(max(0, (1 - len(critical) / total_vb6)) * 100, 1)

        return {
            'timestamp': datetime.now().isoformat(),
            'vb6_inventory': {
                'forms': len(vb6.forms),
                'modules': len(vb6.modules),
                'functions': len(vb6.functions),
                'db_tables': len(vb6.db_tables),
            },
            'modern_inventory': {
                'components': len(modern.components),
                'services': len(modern.services),
                'prisma_models': len(modern.prisma_models),
                'routes': len(modern.routes),
            },
            'parity_percentage': parity_pct,
            'total_findings': len(self.findings),
            'critical': len(critical),
            'warnings': len(warnings),
            'passed': len(critical) == 0,
            'findings': self.findings,
        }

    def generate_html(self, report: Dict, output_path: str) -> None:
        """Generate visual HTML report."""
        status = '✅ PASSED' if report['passed'] else '❌ FAILED'
        status_color = '#10b981' if report['passed'] else '#ef4444'
        parity_color = '#10b981' if report['parity_percentage'] >= 90 else '#f59e0b' if report['parity_percentage'] >= 70 else '#ef4444'

        rows = ''
        for f in sorted(self.findings, key=lambda x: 0 if x['severity'] == 'CRITICAL' else 1):
            sev_color = '#ef4444' if f['severity'] == 'CRITICAL' else '#f59e0b'
            sev_icon = '🔴' if f['severity'] == 'CRITICAL' else '🟡'
            rows += f'''<tr>
                <td style="color:{sev_color}">{sev_icon} {f['severity']}</td>
                <td><code>{f['rule_id']}</code></td>
                <td>{f['vb6_artifact']}</td>
                <td>{f['vb6_type']}</td>
                <td><code>{f['expected_modern']}</code></td>
                <td style="color:#10b981">{f['fix']}</td>
            </tr>'''

        vb6 = report['vb6_inventory']
        mod = report['modern_inventory']

        html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Parity Check Report</title>
<style>
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #f1f5f9; padding: 2rem; }}
    h1 {{ background: linear-gradient(90deg, #10b981, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .status {{ font-size: 2rem; color: {status_color}; margin: 1rem 0; }}
    .parity {{ font-size: 3rem; font-weight: 700; color: {parity_color}; text-align: center; margin: 1rem 0; }}
    .inventory {{ display: flex; gap: 2rem; margin: 2rem 0; }}
    .inv-section {{ background: #1e293b; padding: 1.5rem; border-radius: 1rem; flex: 1; }}
    .inv-section h3 {{ margin-top: 0; color: #94a3b8; text-transform: uppercase; font-size: 0.75rem; }}
    .inv-item {{ display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155; }}
    .inv-value {{ font-weight: 700; font-size: 1.5rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #334155; }}
    th {{ background: #1e293b; text-transform: uppercase; font-size: 0.75rem; color: #94a3b8; }}
    code {{ background: #334155; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.85rem; }}
</style></head><body>
<h1>🔄 Migration Parity Report</h1>
<div class="status">{status}</div>
<div class="parity">{report['parity_percentage']}% Parity</div>
<div class="inventory">
    <div class="inv-section">
        <h3>VB6 Source</h3>
        <div class="inv-item"><span>Forms</span><span class="inv-value">{vb6['forms']}</span></div>
        <div class="inv-item"><span>Modules</span><span class="inv-value">{vb6['modules']}</span></div>
        <div class="inv-item"><span>Functions</span><span class="inv-value">{vb6['functions']}</span></div>
        <div class="inv-item"><span>DB Tables</span><span class="inv-value">{vb6['db_tables']}</span></div>
    </div>
    <div class="inv-section">
        <h3>Angular Target</h3>
        <div class="inv-item"><span>Components</span><span class="inv-value">{mod['components']}</span></div>
        <div class="inv-item"><span>Services</span><span class="inv-value">{mod['services']}</span></div>
        <div class="inv-item"><span>Prisma Models</span><span class="inv-value">{mod['prisma_models']}</span></div>
        <div class="inv-item"><span>API Routes</span><span class="inv-value">{mod['routes']}</span></div>
    </div>
</div>
<h2>Findings</h2>
<table><thead><tr><th>Severity</th><th>Rule</th><th>VB6 Item</th><th>Type</th><th>Expected Modern</th><th>Fix</th></tr></thead>
<tbody>{rows if rows else '<tr><td colspan="6" style="text-align:center;color:#10b981">✅ Full parity achieved!</td></tr>'}</tbody></table>
<footer style="margin-top:2rem;color:#94a3b8;text-align:center">Generated: {report['timestamp']}</footer>
</body></html>'''

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(html, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Check migration parity between VB6 and Angular')
    parser.add_argument('--vb6', required=True, help='VB6 source directory')
    parser.add_argument('--modern', required=True, help='Modern app output directory')
    parser.add_argument('--analysis', help='Analysis directory with inventory.json and schema.json')
    parser.add_argument('--output', required=True, help='JSON output path')
    parser.add_argument('--html', help='HTML report output path')
    args = parser.parse_args()

    print('🔄 Parity Checker v1.0')
    print('=' * 50)

    # Scan VB6
    vb6 = VB6Inventory(Path(args.vb6))
    vb6.scan()
    if args.analysis:
        vb6.load_from_analysis(Path(args.analysis))
    print(f'📦 VB6: {len(vb6.forms)} forms, {len(vb6.modules)} modules, {len(vb6.functions)} functions, {len(vb6.db_tables)} tables')

    # Scan modern
    modern = ModernInventory(Path(args.modern))
    modern.scan()
    print(f'🅰️  Modern: {len(modern.components)} components, {len(modern.services)} services, {len(modern.prisma_models)} models, {len(modern.routes)} routes')

    # Check parity
    checker = ParityChecker()
    checker.check_parity(vb6, modern)

    # Generate report
    report = checker.generate_report(vb6, modern)

    # Save JSON
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding='utf-8')

    print(f'\n📊 Parity: {report["parity_percentage"]}%')
    print(f'   🔴 Critical: {report["critical"]}')
    print(f'   🟡 Warnings: {report["warnings"]}')

    # Generate HTML
    if args.html:
        checker.generate_html(report, args.html)
        print(f'   📄 HTML: {args.html}')

    status = '✅ PASSED' if report['passed'] else '❌ FAILED'
    print(f'\n{status}')

    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
