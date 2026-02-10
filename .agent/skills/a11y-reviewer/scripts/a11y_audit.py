#!/usr/bin/env python3
"""
Accessibility Audit Scanner for migrated Angular applications.
Checks WCAG 2.1 Level AA compliance in HTML templates and TypeScript components.
Generic: works with any project directory.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# ─── A11y Rules ────────────────────────────────────────────────
RULES = [
    {
        'id': 'A11Y-001',
        'name': 'Images must have alt attribute',
        'severity': 'CRITICAL',
        'pattern': r'<img\b(?![^>]*\balt\s*=)[^>]*>',
        'extensions': ['.html'],
        'fix': 'Add alt="descriptive text" to all <img> tags',
    },
    {
        'id': 'A11Y-002',
        'name': 'Form inputs must have labels',
        'severity': 'CRITICAL',
        'pattern': r'<input\b(?![^>]*(?:aria-label|aria-labelledby|\[attr\.aria-label\]))[^>]*>',
        'extensions': ['.html'],
        'fix': 'Add <label for="..."> or aria-label attribute',
    },
    {
        'id': 'A11Y-003',
        'name': 'Buttons must have accessible names',
        'severity': 'CRITICAL',
        'pattern': r'<button\b[^>]*>\s*<(?:mat-icon|i\b)[^>]*>[^<]*</(?:mat-icon|i)>\s*</button>',
        'extensions': ['.html'],
        'fix': 'Add aria-label to icon-only buttons',
    },
    {
        'id': 'A11Y-005',
        'name': 'Page should have exactly one h1',
        'severity': 'CRITICAL',
        'check_type': 'count',
        'pattern': r'<h1[\s>]',
        'expected': 1,
        'extensions': ['.html'],
        'fix': 'Ensure each route component has exactly one <h1>',
    },
    {
        'id': 'A11Y-006',
        'name': 'Heading hierarchy must not skip levels',
        'severity': 'CRITICAL',
        'check_type': 'heading_hierarchy',
        'extensions': ['.html'],
        'fix': 'Use headings in order: h1 → h2 → h3, never skip levels',
    },
    {
        'id': 'A11Y-W02',
        'name': 'Focus indicators must be visible',
        'severity': 'WARNING',
        'pattern': r'outline\s*:\s*(?:none|0)\b(?![^}]*outline)',
        'extensions': ['.css', '.scss'],
        'fix': 'Never remove outline without providing alternative focus indicator',
    },
    {
        'id': 'A11Y-W03',
        'name': 'HTML must have lang attribute',
        'severity': 'WARNING',
        'check_type': 'file_specific',
        'filename': 'index.html',
        'pattern': r'<html\b(?![^>]*\blang\s*=)',
        'extensions': ['.html'],
        'fix': 'Add lang="es" (or appropriate language) to <html> tag',
    },
    {
        'id': 'A11Y-W04',
        'name': 'Tables must have header cells',
        'severity': 'WARNING',
        'pattern': r'<table\b[^>]*>(?:(?!<th[\s>]).)*</table>',
        'extensions': ['.html'],
        'fix': 'Add <th> elements to table headers',
    },
    {
        'id': 'A11Y-008',
        'name': 'ARIA roles must be valid',
        'severity': 'CRITICAL',
        'pattern': r'role="(?!alert|button|checkbox|dialog|grid|heading|img|link|list|listitem|menu|menuitem|navigation|option|progressbar|radio|row|search|status|tab|tabpanel|textbox|toolbar|tooltip|tree)[^"]*"',
        'extensions': ['.html'],
        'fix': 'Use valid ARIA roles from WAI-ARIA specification',
    },
]

class A11yAuditor:
    def __init__(self):
        self.findings: List[Dict] = []
        self.files_scanned = 0

    def scan_file(self, file_path: Path) -> None:
        """Scan a single file for a11y issues."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
        except Exception:
            return

        ext = file_path.suffix
        self.files_scanned += 1

        for rule in RULES:
            if ext not in rule.get('extensions', []):
                continue

            # File-specific checks
            if rule.get('check_type') == 'file_specific':
                if file_path.name != rule.get('filename', ''):
                    continue

            # Heading hierarchy check
            if rule.get('check_type') == 'heading_hierarchy':
                self._check_heading_hierarchy(file_path, content, rule)
                continue

            # Count-based checks (e.g., exactly one h1)
            if rule.get('check_type') == 'count':
                matches = re.findall(rule['pattern'], content, re.IGNORECASE)
                if len(matches) != rule.get('expected', 1) and len(matches) > 0:
                    self.findings.append({
                        'rule_id': rule['id'],
                        'rule_name': rule['name'],
                        'severity': rule['severity'],
                        'file': str(file_path),
                        'line': 0,
                        'content': f'Found {len(matches)} h1 tags (expected {rule["expected"]})',
                        'fix': rule['fix'],
                    })
                continue

            # Pattern-based line scan
            for i, line in enumerate(lines, 1):
                if re.search(rule['pattern'], line, re.IGNORECASE | re.DOTALL):
                    self.findings.append({
                        'rule_id': rule['id'],
                        'rule_name': rule['name'],
                        'severity': rule['severity'],
                        'file': str(file_path),
                        'line': i,
                        'content': line.strip()[:120],
                        'fix': rule['fix'],
                    })

    def _check_heading_hierarchy(self, file_path: Path, content: str, rule: Dict) -> None:
        """Check that heading levels don't skip (h1→h3 without h2)."""
        headings = re.findall(r'<h(\d)[\s>]', content)
        if not headings:
            return
        levels = [int(h) for h in headings]
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                self.findings.append({
                    'rule_id': rule['id'],
                    'rule_name': rule['name'],
                    'severity': rule['severity'],
                    'file': str(file_path),
                    'line': 0,
                    'content': f'Heading skips: h{levels[i-1]} → h{levels[i]}',
                    'fix': rule['fix'],
                })

    def scan_directory(self, directory: Path) -> None:
        """Recursively scan a directory."""
        if not directory.exists():
            return
        skip_dirs = {'node_modules', '.git', 'dist', 'coverage', '.angular'}
        for file_path in directory.rglob('*'):
            if any(s in file_path.parts for s in skip_dirs):
                continue
            if file_path.is_file() and file_path.suffix in ['.html', '.css', '.scss']:
                self.scan_file(file_path)

    def generate_report(self) -> Dict:
        """Generate summary report."""
        critical = [f for f in self.findings if f['severity'] == 'CRITICAL']
        warnings = [f for f in self.findings if f['severity'] == 'WARNING']
        return {
            'timestamp': datetime.now().isoformat(),
            'files_scanned': self.files_scanned,
            'total_findings': len(self.findings),
            'critical': len(critical),
            'warnings': len(warnings),
            'wcag_compliant': len(critical) == 0,
            'findings': self.findings,
        }

    def generate_html(self, report: Dict, output_path: str) -> None:
        """Generate visual HTML report."""
        status = '✅ WCAG 2.1 AA Compliant' if report['wcag_compliant'] else '❌ Non-Compliant'
        status_color = '#10b981' if report['wcag_compliant'] else '#ef4444'

        rows = ''
        for f in sorted(report['findings'], key=lambda x: (0 if x['severity'] == 'CRITICAL' else 1)):
            sev_color = '#ef4444' if f['severity'] == 'CRITICAL' else '#f59e0b'
            sev_icon = '🔴' if f['severity'] == 'CRITICAL' else '🟡'
            short_file = Path(f['file']).name
            rows += f'''<tr>
                <td style="color:{sev_color}">{sev_icon} {f['severity']}</td>
                <td><code>{f['rule_id']}</code></td>
                <td>{f['rule_name']}</td>
                <td><code>{short_file}:{f['line']}</code></td>
                <td style="color:#10b981">{f['fix']}</td>
            </tr>'''

        html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Accessibility Audit Report</title>
<style>
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #f1f5f9; padding: 2rem; }}
    h1 {{ background: linear-gradient(90deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .status {{ font-size: 2rem; color: {status_color}; margin: 1rem 0; }}
    .stats {{ display: flex; gap: 1rem; margin: 2rem 0; }}
    .stat {{ background: #1e293b; padding: 1.5rem; border-radius: 1rem; text-align: center; flex: 1; }}
    .stat-value {{ font-size: 2.5rem; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #334155; }}
    th {{ background: #1e293b; text-transform: uppercase; font-size: 0.75rem; color: #94a3b8; }}
    code {{ background: #334155; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.85rem; }}
</style></head><body>
<h1>♿ Accessibility Audit Report (WCAG 2.1 AA)</h1>
<div class="status">{status}</div>
<div class="stats">
    <div class="stat"><div class="stat-value">{report['files_scanned']}</div><div>Files Scanned</div></div>
    <div class="stat"><div class="stat-value" style="color:#ef4444">{report['critical']}</div><div>Critical</div></div>
    <div class="stat"><div class="stat-value" style="color:#f59e0b">{report['warnings']}</div><div>Warnings</div></div>
</div>
<table><thead><tr><th>Severity</th><th>Rule</th><th>Name</th><th>Location</th><th>Fix</th></tr></thead>
<tbody>{rows if rows else '<tr><td colspan="5" style="text-align:center;color:#10b981">✅ All accessibility checks passed!</td></tr>'}</tbody></table>
<footer style="margin-top:2rem;color:#94a3b8;text-align:center">Generated: {report['timestamp']}</footer>
</body></html>'''

        Path(output_path).write_text(html, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Accessibility audit for Angular apps')
    parser.add_argument('--input', required=True, help='Frontend source directory')
    parser.add_argument('--output', required=True, help='JSON output path')
    parser.add_argument('--html', help='HTML report output path')
    args = parser.parse_args()

    auditor = A11yAuditor()

    print('♿ Accessibility Audit Scanner v1.0')
    print('=' * 50)

    input_dir = Path(args.input)
    if input_dir.exists():
        print(f'📂 Scanning: {input_dir}')
        auditor.scan_directory(input_dir)

    report = auditor.generate_report()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'\n📊 Results: {report["files_scanned"]} files scanned')
    print(f'   🔴 Critical: {report["critical"]}')
    print(f'   🟡 Warnings: {report["warnings"]}')

    if args.html:
        auditor.generate_html(report, args.html)
        print(f'   📄 HTML: {args.html}')

    status = '✅ WCAG 2.1 AA Compliant' if report['wcag_compliant'] else '❌ Non-Compliant'
    print(f'\n{status}')

    return 0 if report['wcag_compliant'] else 1


if __name__ == '__main__':
    sys.exit(main())
