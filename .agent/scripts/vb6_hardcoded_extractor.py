#!/usr/bin/env python3
"""
VB6 Hardcoded Value Extractor
=============================
Finds and catalogs hardcoded values that need parameterization:
- Connection strings
- File paths
- URLs
- Magic numbers
- Hardcoded credentials
- Configuration values
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

PATTERNS = {
    # Connection strings
    'connection_string': re.compile(
        r'"[^"]*(?:Provider|Data Source|Initial Catalog|User ID|Password|DSN|Database)[^"]*"',
        re.IGNORECASE
    ),
    
    # Windows file paths
    'windows_path': re.compile(
        r'"[A-Za-z]:\\[^"]*"'
    ),
    
    # URLs
    'url': re.compile(
        r'"(?:https?://|ftp://|www\.)[^"]*"',
        re.IGNORECASE
    ),
    
    # IP addresses
    'ip_address': re.compile(
        r'"(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?"'
    ),
    
    # Email addresses
    'email': re.compile(
        r'"[^"@]+@[^"@]+\.[^"@]+"'
    ),
    
    # Potential passwords/credentials
    'credential': re.compile(
        r'(?:password|pwd|passwd|secret|api.?key|token)\s*=\s*"[^"]+"',
        re.IGNORECASE
    ),
    
    # Magic numbers (numeric literals > 9 in comparisons/assignments)
    'magic_number': re.compile(
        r'(?<!["\w])(?:=|<|>|<=|>=|<>)\s*(\d{2,})(?!["\w])'
    ),
    
    # Dimension constants
    'dimension': re.compile(
        r'(?:Height|Width|Left|Top|Size)\s*=\s*(\d+)'
    ),
    
    # Limit constants
    'limit_constant': re.compile(
        r'(?:Max|Min|Limit|Count|Size|Length)\s*(?:=|<|>|<=|>=)\s*(\d+)',
        re.IGNORECASE
    ),
    
    # SQL table names (hardcoded)
    'sql_table': re.compile(
        r'(?:FROM|INTO|UPDATE|JOIN)\s+([A-Za-z_]\w*)',
        re.IGNORECASE
    ),
    
    # Registry keys
    'registry': re.compile(
        r'"(?:HKEY_|HKLM|HKCU)[^"]*"',
        re.IGNORECASE
    ),
    
    # Server names
    'server_name': re.compile(
        r'(?:Server|Host|Machine)\s*=\s*"([^"]+)"',
        re.IGNORECASE
    ),
    
    # Port numbers
    'port_number': re.compile(
        r'(?:Port)\s*=\s*(\d+)',
        re.IGNORECASE
    ),
    
    # Date formats
    'date_format': re.compile(
        r'Format\s*\([^,]+,\s*"([^"]+)"'
    ),
    
    # Timeout values
    'timeout': re.compile(
        r'(?:Timeout|Wait|Delay|Interval)\s*=\s*(\d+)',
        re.IGNORECASE
    )
}


class VB6HardcodedExtractor:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.findings = defaultdict(list)
        self.summary = defaultdict(int)
        
    def analyze(self):
        """Main analysis entry point."""
        print(f"🔎 Extracting hardcoded values: {self.source_dir}")
        
        for root, _, files in os.walk(self.source_dir):
            for filename in files:
                filepath = Path(root) / filename
                ext = filepath.suffix.lower()
                
                if ext in ['.frm', '.bas', '.cls', '.ctl']:
                    self._analyze_file(filepath)
        
        results = {
            'summary': {
                'total_findings': sum(self.summary.values()),
                'by_category': dict(self.summary),
                'risk_level': self._assess_risk()
            },
            'findings': {k: v for k, v in self.findings.items() if v}
        }
        
        return results
    
    def _analyze_file(self, filepath):
        """Analyze a single file for hardcoded values."""
        content = self._read_file(filepath)
        if not content:
            return
        
        lines = content.split('\n')
        
        for category, pattern in PATTERNS.items():
            matches = pattern.finditer(content)
            
            for match in matches:
                # Find line number
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''
                
                # Get the matched value
                if match.groups():
                    value = match.group(1)
                else:
                    value = match.group(0)
                
                # Skip if it's in a comment
                if line_content.strip().startswith("'"):
                    continue
                
                # Determine severity
                severity = self._determine_severity(category, value)
                
                finding = {
                    'file': str(filepath.name),
                    'line': line_num,
                    'value': value[:100] + ('...' if len(value) > 100 else ''),
                    'context': line_content[:150],
                    'severity': severity,
                    'recommendation': self._get_recommendation(category)
                }
                
                self.findings[category].append(finding)
                self.summary[category] += 1
    
    def _determine_severity(self, category, value):
        """Determine the severity of a finding."""
        high_severity = ['credential', 'connection_string', 'ip_address', 'server_name']
        medium_severity = ['windows_path', 'url', 'registry', 'port_number']
        
        if category in high_severity:
            return 'HIGH'
        elif category in medium_severity:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_recommendation(self, category):
        """Get recommendation for a category."""
        recommendations = {
            'connection_string': 'Move to environment variable or config file',
            'windows_path': 'Use relative paths or configuration',
            'url': 'Move to configuration/environment',
            'ip_address': 'Use DNS names and configuration',
            'email': 'Move to configuration',
            'credential': '⚠️ SECURITY RISK - Move to secure vault',
            'magic_number': 'Extract to named constant',
            'dimension': 'Consider responsive design values',
            'limit_constant': 'Extract to configuration constant',
            'sql_table': 'Already noted - verify table names',
            'registry': 'Document registry dependencies',
            'server_name': 'Move to configuration',
            'port_number': 'Move to configuration',
            'date_format': 'Consider locale-aware formatting',
            'timeout': 'Extract to configurable constant'
        }
        return recommendations.get(category, 'Review and consider extraction')
    
    def _assess_risk(self):
        """Assess overall risk level."""
        high_count = sum(1 for findings in self.findings.values() 
                        for f in findings if f['severity'] == 'HIGH')
        
        if high_count > 10:
            return 'HIGH'
        elif high_count > 0 or self.summary.get('credential', 0) > 0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _read_file(self, filepath):
        """Read file with proper encoding."""
        for enc in ['utf-8', 'latin1', 'cp1252']:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    return f.read()
            except:
                continue
        return None


def main():
    parser = argparse.ArgumentParser(description="VB6 Hardcoded Value Extractor")
    parser.add_argument("source_dir", help="Directory containing VB6 source code")
    parser.add_argument("-o", "--output", default="vb6_hardcoded.json", help="Output JSON file")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.source_dir):
        print(f"❌ Error: Directory not found: {args.source_dir}")
        return 1
    
    extractor = VB6HardcodedExtractor(args.source_dir)
    results = extractor.analyze()
    
    indent = 2 if args.pretty else None
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=indent, ensure_ascii=False)
    
    print(f"✅ Hardcoded value extraction complete: {args.output}")
    print(f"   🔎 Total findings: {results['summary']['total_findings']}")
    print(f"   ⚠️  Risk level: {results['summary']['risk_level']}")
    
    for category, count in results['summary']['by_category'].items():
        print(f"   📌 {category}: {count}")
    
    return 0


if __name__ == "__main__":
    exit(main())
