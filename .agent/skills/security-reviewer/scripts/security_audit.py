#!/usr/bin/env python3
"""
Security Audit Scanner for migrated Angular + Express applications.
Scans source code for OWASP Top 10 vulnerabilities.
Generic: works with any project directory.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# ─── Security Rules ────────────────────────────────────────────────
CRITICAL_RULES = [
    {
        'id': 'SEC-001',
        'name': 'Unsafe innerHTML usage',
        'severity': 'CRITICAL',
        'patterns': [r'innerHTML\s*=', r'bypassSecurityTrustHtml', r'\[innerHTML\]\s*='],
        'extensions': ['.ts', '.html'],
        'description': 'Using innerHTML with dynamic content allows XSS attacks',
        'fix': 'Use Angular text binding [innerText] or DomSanitizer'
    },
    {
        'id': 'SEC-002',
        'name': 'eval() or Function constructor',
        'severity': 'CRITICAL',
        'patterns': [r'\beval\s*\(', r'new\s+Function\s*\(', r'setTimeout\s*\(\s*["\']'],
        'extensions': ['.ts', '.js'],
        'description': 'eval() allows arbitrary code execution',
        'fix': 'Refactor to avoid dynamic code evaluation'
    },
    {
        'id': 'SEC-003',
        'name': 'Hardcoded secrets',
        'severity': 'CRITICAL',
        'patterns': [
            r'(?:password|secret|api_?key|token)\s*[:=]\s*["\'][^"\']{8,}["\']',
            r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',
        ],
        'extensions': ['.ts', '.js', '.json'],
        'description': 'Secrets should never be hardcoded in source',
        'fix': 'Use environment variables via process.env or .env files'
    },
    {
        'id': 'SEC-004',
        'name': 'Raw SQL queries',
        'severity': 'CRITICAL',
        'patterns': [r'\$queryRaw', r'\$executeRaw', r'\.query\s*\(\s*[`"\'].*\+', r'db\.run\s*\('],
        'extensions': ['.ts', '.js'],
        'description': 'Raw SQL is vulnerable to injection attacks',
        'fix': 'Use Prisma ORM methods exclusively'
    },
    {
        'id': 'SEC-005',
        'name': 'CORS wildcard in production',
        'severity': 'CRITICAL',
        'patterns': [r'origin\s*:\s*["\']?\*["\']?', r'cors\(\s*\)'],
        'extensions': ['.ts', '.js'],
        'description': 'Wildcard CORS allows any origin to access the API',
        'fix': 'Specify allowed origins explicitly'
    },
    {
        'id': 'SEC-006',
        'name': 'JWT without expiration',
        'severity': 'CRITICAL',
        'patterns': [r'jwt\.sign\s*\([^)]*\)\s*(?!.*expiresIn)'],
        'extensions': ['.ts', '.js'],
        'description': 'JWT tokens without expiration never expire',
        'fix': 'Add expiresIn option to jwt.sign()'
    },
    {
        'id': 'SEC-007',
        'name': 'Logging sensitive data',
        'severity': 'CRITICAL',
        'patterns': [r'console\.log\s*\(.*(?:password|token|secret|credential)', r'logger\.info\s*\(.*password'],
        'extensions': ['.ts', '.js'],
        'description': 'Logging passwords or tokens exposes them in logs',
        'fix': 'Never log sensitive fields; redact if necessary'
    },
    {
        'id': 'SEC-008',
        'name': 'HTTP in production config',
        'severity': 'CRITICAL',
        'patterns': [r'http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)'],
        'extensions': ['.ts', '.js', '.json'],
        'description': 'HTTP URLs in production are unencrypted',
        'fix': 'Use HTTPS for all production URLs'
    },
]

WARNING_RULES = [
    {
        'id': 'SEC-W01',
        'name': 'Missing input validation',
        'severity': 'WARNING',
        'check_type': 'dependency',
        'package': 'express-validator',
        'description': 'Backend endpoints should validate all input'
    },
    {
        'id': 'SEC-W02',
        'name': 'Missing rate limiting',
        'severity': 'WARNING',
        'check_type': 'dependency',
        'package': 'express-rate-limit',
        'description': 'Auth endpoints should have rate limiting'
    },
    {
        'id': 'SEC-W03',
        'name': 'Missing Helmet.js',
        'severity': 'WARNING',
        'check_type': 'dependency',
        'package': 'helmet',
        'description': 'Helmet sets secure HTTP headers'
    },
]

class SecurityAuditor:
    def __init__(self):
        self.findings: List[Dict] = []
        self.files_scanned = 0

    def scan_file(self, file_path: Path, rules: List[Dict]) -> List[Dict]:
        """Scan a single file against pattern-based rules."""
        findings = []
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
        except Exception:
            return findings

        ext = file_path.suffix
        self.files_scanned += 1

        for rule in rules:
            if ext not in rule.get('extensions', []):
                continue
            for pattern in rule.get('patterns', []):
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith('//') or line.strip().startswith('*'):
                        continue
                    if re.search(pattern, line, re.IGNORECASE):
                        findings.append({
                            'rule_id': rule['id'],
                            'rule_name': rule['name'],
                            'severity': rule['severity'],
                            'file': str(file_path),
                            'line': i,
                            'content': line.strip()[:120],
                            'description': rule['description'],
                            'fix': rule.get('fix', 'Review manually'),
                        })
        return findings

    def scan_directory(self, directory: Path, rules: List[Dict]) -> None:
        """Recursively scan a directory."""
        if not directory.exists():
            return
        skip_dirs = {'node_modules', '.git', 'dist', 'coverage', '.angular'}
        for file_path in directory.rglob('*'):
            if any(s in file_path.parts for s in skip_dirs):
                continue
            if file_path.is_file() and file_path.suffix in ['.ts', '.js', '.html', '.json']:
                findings = self.scan_file(file_path, rules)
                self.findings.extend(findings)

    def check_dependencies(self, backend_dir: Path) -> None:
        """Check for missing security dependencies."""
        pkg_file = backend_dir / 'package.json'
        if not pkg_file.exists():
            return
        try:
            pkg = json.loads(pkg_file.read_text(encoding='utf-8'))
            all_deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        except Exception:
            return

        for rule in WARNING_RULES:
            if rule.get('check_type') == 'dependency':
                if rule['package'] not in all_deps:
                    self.findings.append({
                        'rule_id': rule['id'],
                        'rule_name': rule['name'],
                        'severity': rule['severity'],
                        'file': str(pkg_file),
                        'line': 0,
                        'content': f'Missing package: {rule["package"]}',
                        'description': rule['description'],
                        'fix': f'npm install {rule["package"]}',
                    })

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
            'passed': len(critical) == 0,
            'findings': self.findings,
        }

    def generate_html(self, report: Dict, output_path: str) -> None:
        """Generate visual HTML report."""
        status = '✅ PASSED' if report['passed'] else '❌ FAILED'
        status_color = '#10b981' if report['passed'] else '#ef4444'

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
                <td><code>{f['content'][:80]}</code></td>
                <td style="color:#10b981">{f['fix']}</td>
            </tr>'''

        html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Security Audit Report</title>
<style>
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #f1f5f9; padding: 2rem; }}
    h1 {{ background: linear-gradient(90deg, #ef4444, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .status {{ font-size: 2rem; color: {status_color}; margin: 1rem 0; }}
    .stats {{ display: flex; gap: 1rem; margin: 2rem 0; }}
    .stat {{ background: #1e293b; padding: 1.5rem; border-radius: 1rem; text-align: center; flex: 1; }}
    .stat-value {{ font-size: 2.5rem; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #334155; }}
    th {{ background: #1e293b; text-transform: uppercase; font-size: 0.75rem; color: #94a3b8; }}
    code {{ background: #334155; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.85rem; }}
</style></head><body>
<h1>🔒 Security Audit Report</h1>
<div class="status">{status}</div>
<div class="stats">
    <div class="stat"><div class="stat-value">{report['files_scanned']}</div><div>Files Scanned</div></div>
    <div class="stat"><div class="stat-value" style="color:#ef4444">{report['critical']}</div><div>Critical</div></div>
    <div class="stat"><div class="stat-value" style="color:#f59e0b">{report['warnings']}</div><div>Warnings</div></div>
</div>
<table><thead><tr><th>Severity</th><th>Rule</th><th>Name</th><th>Location</th><th>Finding</th><th>Fix</th></tr></thead>
<tbody>{rows if rows else '<tr><td colspan="6" style="text-align:center;color:#10b981">✅ No security issues found!</td></tr>'}</tbody></table>
<footer style="margin-top:2rem;color:#94a3b8;text-align:center">Generated: {report['timestamp']}</footer>
</body></html>'''

        Path(output_path).write_text(html, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Security audit for migrated code')
    parser.add_argument('--frontend', required=True, help='Frontend source directory')
    parser.add_argument('--backend', required=True, help='Backend source directory')
    parser.add_argument('--output', required=True, help='JSON output path')
    parser.add_argument('--html', help='HTML report output path')
    args = parser.parse_args()

    auditor = SecurityAuditor()

    print('🔒 Security Audit Scanner v1.0')
    print('=' * 50)

    # Scan frontend
    frontend_dir = Path(args.frontend)
    if frontend_dir.exists():
        print(f'📂 Scanning frontend: {frontend_dir}')
        auditor.scan_directory(frontend_dir, CRITICAL_RULES)

    # Scan backend
    backend_dir = Path(args.backend)
    if backend_dir.exists():
        print(f'📂 Scanning backend: {backend_dir}')
        auditor.scan_directory(backend_dir, CRITICAL_RULES)
        # Check for parent package.json (one level up from src)
        auditor.check_dependencies(backend_dir.parent)

    # Generate report
    report = auditor.generate_report()

    # Save JSON
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'\n📊 Results: {report["files_scanned"]} files scanned')
    print(f'   🔴 Critical: {report["critical"]}')
    print(f'   🟡 Warnings: {report["warnings"]}')

    # Generate HTML
    if args.html:
        auditor.generate_html(report, args.html)
        print(f'   📄 HTML: {args.html}')

    status = '✅ PASSED' if report['passed'] else '❌ FAILED'
    print(f'\n{status}')

    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
