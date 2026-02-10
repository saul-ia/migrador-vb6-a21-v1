#!/usr/bin/env python3
"""
Contract Validator for Angular + Express applications.
Validates frontend service calls match backend API contract (swagger.json).
Generic: works with any project directory.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set


class SwaggerParser:
    """Parses swagger.json / openapi.json to extract API contract."""

    def __init__(self, swagger_path: Path):
        self.swagger_path = swagger_path
        self.endpoints: List[Dict] = []

    def parse(self) -> List[Dict]:
        """Parse swagger file and extract all endpoints."""
        try:
            data = json.loads(self.swagger_path.read_text(encoding='utf-8'))
        except Exception as e:
            print(f'⚠️  Could not parse swagger file: {e}')
            return []

        paths = data.get('paths', {})
        components = data.get('components', {}).get('schemas', {})
        # Also support Swagger 2.0 definitions
        definitions = data.get('definitions', {})
        schemas = {**definitions, **components}

        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ('get', 'post', 'put', 'patch', 'delete'):
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'operationId': details.get('operationId', ''),
                        'parameters': [],
                        'request_body_fields': [],
                        'response_fields': [],
                    }

                    # Extract query/path parameters
                    for param in details.get('parameters', []):
                        endpoint['parameters'].append({
                            'name': param.get('name', ''),
                            'in': param.get('in', ''),
                            'required': param.get('required', False),
                        })

                    # Extract request body fields (OpenAPI 3.x)
                    req_body = details.get('requestBody', {})
                    if req_body:
                        content = req_body.get('content', {})
                        json_schema = content.get('application/json', {}).get('schema', {})
                        endpoint['request_body_fields'] = self._extract_fields(json_schema, schemas)

                    # Swagger 2.0: body parameter
                    for param in details.get('parameters', []):
                        if param.get('in') == 'body':
                            schema = param.get('schema', {})
                            endpoint['request_body_fields'] = self._extract_fields(schema, schemas)

                    # Extract response fields (200/201)
                    for code in ['200', '201']:
                        resp = details.get('responses', {}).get(code, {})
                        resp_content = resp.get('content', {}).get('application/json', {}).get('schema', {})
                        if resp_content:
                            endpoint['response_fields'] = self._extract_fields(resp_content, schemas)
                            break
                        # Swagger 2.0
                        resp_schema = resp.get('schema', {})
                        if resp_schema:
                            endpoint['response_fields'] = self._extract_fields(resp_schema, schemas)
                            break

                    self.endpoints.append(endpoint)

        return self.endpoints

    def _extract_fields(self, schema: Dict, definitions: Dict) -> List[str]:
        """Extract field names from a JSON schema, resolving $ref."""
        if not schema:
            return []
        # Resolve $ref
        ref = schema.get('$ref', '')
        if ref:
            ref_name = ref.split('/')[-1]
            schema = definitions.get(ref_name, {})

        # Array items
        if schema.get('type') == 'array':
            return self._extract_fields(schema.get('items', {}), definitions)

        # Object properties
        props = schema.get('properties', {})
        return list(props.keys())


class AngularServiceScanner:
    """Scans Angular service files to extract HTTP calls."""

    HTTP_CALL_PATTERN = re.compile(
        r'this\.http\.(get|post|put|patch|delete)\s*[<(]'
        r'[^)]*?[\'"`]([^\'"`]+)[\'"`]',
        re.IGNORECASE | re.DOTALL
    )

    URL_PATTERN = re.compile(
        r'[\'"`](/api/[^\s\'"`]+)[\'"`]',
    )

    def __init__(self, services_dir: Path):
        self.services_dir = services_dir
        self.calls: List[Dict] = []

    def scan(self) -> List[Dict]:
        """Scan all Angular service files for HTTP calls."""
        if not self.services_dir.exists():
            print(f'⚠️  Services directory not found: {self.services_dir}')
            return []

        for ts_file in self.services_dir.rglob('*.ts'):
            if 'spec' in ts_file.name or 'test' in ts_file.name:
                continue
            self._scan_file(ts_file)

        return self.calls

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single TypeScript file for HTTP calls."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
        except Exception:
            return

        # Multi-line aware: join content for regex
        full_text = content

        # Find HttpClient calls
        for match in self.HTTP_CALL_PATTERN.finditer(full_text):
            method = match.group(1).upper()
            url = match.group(2)
            line_num = full_text[:match.start()].count('\n') + 1
            self.calls.append({
                'file': str(file_path),
                'line': line_num,
                'method': method,
                'url': self._normalize_url(url),
                'raw_url': url,
            })

        # Also check for URL strings used in fetch/apiService patterns
        for i, line in enumerate(lines, 1):
            # Pattern: this.api.get('/api/...') or similar
            api_match = re.search(r'this\.\w+\.(get|post|put|patch|delete)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', line, re.IGNORECASE)
            if api_match:
                method = api_match.group(1).upper()
                url = api_match.group(2)
                # Avoid duplicates
                if not any(c['line'] == i and c['file'] == str(file_path) for c in self.calls):
                    self.calls.append({
                        'file': str(file_path),
                        'line': i,
                        'method': method,
                        'url': self._normalize_url(url),
                        'raw_url': url,
                    })

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by replacing dynamic segments with placeholders."""
        # Replace ${...} template literals
        url = re.sub(r'\$\{[^}]+\}', '{id}', url)
        # Replace numeric segments
        url = re.sub(r'/\d+', '/{id}', url)
        return url


class ContractValidator:
    """Validates that frontend calls match backend API contract."""

    def __init__(self):
        self.findings: List[Dict] = []

    def validate(self, swagger_endpoints: List[Dict], frontend_calls: List[Dict]) -> None:
        """Run all contract validation checks."""
        swagger_paths = {(e['path'], e['method']) for e in swagger_endpoints}
        frontend_paths = set()

        for call in frontend_calls:
            norm_url = call['url']
            method = call['method']
            frontend_paths.add((norm_url, method))

            # CT-001: Frontend calls non-existent endpoint
            matched = self._find_matching_endpoint(norm_url, method, swagger_endpoints)
            if not matched:
                self.findings.append({
                    'rule_id': 'CT-001',
                    'rule_name': 'Frontend calls non-existent endpoint',
                    'severity': 'CRITICAL',
                    'file': call['file'],
                    'line': call['line'],
                    'content': f'{method} {call["raw_url"]}',
                    'description': f'Frontend calls {method} {norm_url} but it does not exist in swagger.json',
                    'fix': f'Add {method} {norm_url} to backend routes or fix the URL in the service',
                })
                continue

            # CT-002: HTTP method mismatch (handled implicitly by matching)
            # CT-006: Check for similar-but-not-exact paths (typos)
            if not matched and self._find_similar_endpoint(norm_url, swagger_endpoints):
                similar = self._find_similar_endpoint(norm_url, swagger_endpoints)
                self.findings.append({
                    'rule_id': 'CT-006',
                    'rule_name': 'URL path mismatch (possible typo)',
                    'severity': 'CRITICAL',
                    'file': call['file'],
                    'line': call['line'],
                    'content': f'{method} {call["raw_url"]}',
                    'description': f'Did you mean {similar["path"]}?',
                    'fix': f'Change URL to {similar["path"]}',
                })

        # CT-005: Backend endpoint not called by any frontend service
        for endpoint in swagger_endpoints:
            path = endpoint['path']
            method = endpoint['method']
            if not any(self._path_matches(path, c[0]) for c in frontend_paths if c[1] == method):
                self.findings.append({
                    'rule_id': 'CT-005',
                    'rule_name': 'Backend endpoint not called by frontend',
                    'severity': 'INFO',
                    'file': 'swagger.json',
                    'line': 0,
                    'content': f'{method} {path}',
                    'description': f'No Angular service calls {method} {path}',
                    'fix': 'Verify this endpoint is needed or create a frontend service call',
                })

    def _find_matching_endpoint(self, url: str, method: str, endpoints: List[Dict]) -> Optional[Dict]:
        """Find a swagger endpoint matching the given URL and method."""
        for ep in endpoints:
            if ep['method'] == method and self._path_matches(ep['path'], url):
                return ep
        return None

    def _path_matches(self, swagger_path: str, frontend_path: str) -> bool:
        """Check if swagger path matches frontend path (with parameter placeholders)."""
        # Normalize both paths
        swagger_parts = swagger_path.strip('/').split('/')
        frontend_parts = frontend_path.strip('/').split('/')

        if len(swagger_parts) != len(frontend_parts):
            return False

        for sw, fe in zip(swagger_parts, frontend_parts):
            # Swagger uses {param}, frontend might use {id} or actual values
            if sw.startswith('{') or fe.startswith('{'):
                continue
            if sw.lower() != fe.lower():
                return False
        return True

    def _find_similar_endpoint(self, url: str, endpoints: List[Dict]) -> Optional[Dict]:
        """Find a similar endpoint (potential typo)."""
        url_parts = url.strip('/').split('/')
        best_match = None
        best_score = 0

        for ep in endpoints:
            ep_parts = ep['path'].strip('/').split('/')
            if len(ep_parts) != len(url_parts):
                continue
            score = sum(1 for a, b in zip(ep_parts, url_parts) if a == b or a.startswith('{'))
            if score > best_score and score >= len(url_parts) - 1:
                best_score = score
                best_match = ep

        return best_match

    def generate_report(self, swagger_count: int, frontend_count: int) -> Dict:
        """Generate summary report."""
        critical = [f for f in self.findings if f['severity'] == 'CRITICAL']
        warnings = [f for f in self.findings if f['severity'] == 'WARNING']
        info = [f for f in self.findings if f['severity'] == 'INFO']
        return {
            'timestamp': datetime.now().isoformat(),
            'swagger_endpoints': swagger_count,
            'frontend_calls': frontend_count,
            'total_findings': len(self.findings),
            'critical': len(critical),
            'warnings': len(warnings),
            'info': len(info),
            'passed': len(critical) == 0,
            'findings': self.findings,
        }

    def generate_html(self, report: Dict, output_path: str) -> None:
        """Generate visual HTML report."""
        status = '✅ PASSED' if report['passed'] else '❌ FAILED'
        status_color = '#10b981' if report['passed'] else '#ef4444'

        rows = ''
        for f in sorted(report['findings'], key=lambda x: {'CRITICAL': 0, 'WARNING': 1, 'INFO': 2}.get(x['severity'], 3)):
            sev_colors = {'CRITICAL': '#ef4444', 'WARNING': '#f59e0b', 'INFO': '#3b82f6'}
            sev_icons = {'CRITICAL': '🔴', 'WARNING': '🟡', 'INFO': '🔵'}
            sev_color = sev_colors.get(f['severity'], '#94a3b8')
            sev_icon = sev_icons.get(f['severity'], '⚪')
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
<html lang="en"><head><meta charset="UTF-8"><title>Contract Validation Report</title>
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
<h1>📋 API Contract Validation Report</h1>
<div class="status">{status}</div>
<div class="stats">
    <div class="stat"><div class="stat-value">{report['swagger_endpoints']}</div><div>Swagger Endpoints</div></div>
    <div class="stat"><div class="stat-value">{report['frontend_calls']}</div><div>Frontend Calls</div></div>
    <div class="stat"><div class="stat-value" style="color:#ef4444">{report['critical']}</div><div>Critical</div></div>
    <div class="stat"><div class="stat-value" style="color:#f59e0b">{report['warnings']}</div><div>Warnings</div></div>
    <div class="stat"><div class="stat-value" style="color:#3b82f6">{report['info']}</div><div>Info</div></div>
</div>
<table><thead><tr><th>Severity</th><th>Rule</th><th>Name</th><th>Location</th><th>Finding</th><th>Fix</th></tr></thead>
<tbody>{rows if rows else '<tr><td colspan="6" style="text-align:center;color:#10b981">✅ All contracts match!</td></tr>'}</tbody></table>
<footer style="margin-top:2rem;color:#94a3b8;text-align:center">Generated: {report['timestamp']}</footer>
</body></html>'''

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(html, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Validate frontend-backend API contract')
    parser.add_argument('--swagger', required=True, help='Path to swagger.json / openapi.json')
    parser.add_argument('--services', required=True, help='Angular services directory')
    parser.add_argument('--output', required=True, help='JSON output path')
    parser.add_argument('--html', help='HTML report output path')
    args = parser.parse_args()

    print('📋 Contract Validator v1.0')
    print('=' * 50)

    # Parse Swagger
    swagger_parser = SwaggerParser(Path(args.swagger))
    endpoints = swagger_parser.parse()
    print(f'📄 Swagger endpoints found: {len(endpoints)}')

    # Scan Angular services
    scanner = AngularServiceScanner(Path(args.services))
    calls = scanner.scan()
    print(f'🅰️  Frontend HTTP calls found: {len(calls)}')

    # Validate contract
    validator = ContractValidator()
    validator.validate(endpoints, calls)

    # Generate report
    report = validator.generate_report(len(endpoints), len(calls))

    # Save JSON
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding='utf-8')

    print(f'\n📊 Results:')
    print(f'   🔴 Critical: {report["critical"]}')
    print(f'   🟡 Warnings: {report["warnings"]}')
    print(f'   🔵 Info: {report["info"]}')

    # Generate HTML
    if args.html:
        validator.generate_html(report, args.html)
        print(f'   📄 HTML: {args.html}')

    status = '✅ PASSED' if report['passed'] else '❌ FAILED'
    print(f'\n{status}')

    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
