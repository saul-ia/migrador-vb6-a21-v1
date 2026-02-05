#!/usr/bin/env python3
"""
VB6 Metrics Analyzer
====================
Calculates code quality metrics for VB6 codebases:
- Cyclomatic Complexity
- Lines of Code (LOC)
- Comment Ratio
- Control Count per Form
- Function/Sub Count
- Nesting Depth
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

# ============================================================================
# METRIC PATTERNS
# ============================================================================

PATTERNS = {
    # Decision points for cyclomatic complexity
    'decision_if': re.compile(r'\bIf\b.*\bThen\b', re.IGNORECASE),
    'decision_elseif': re.compile(r'\bElseIf\b', re.IGNORECASE),
    'decision_case': re.compile(r'\bCase\b(?!\s+Else)', re.IGNORECASE),
    'decision_for': re.compile(r'\bFor\b', re.IGNORECASE),
    'decision_do': re.compile(r'\bDo\b\s+(While|Until)', re.IGNORECASE),
    'decision_while': re.compile(r'\bWhile\b', re.IGNORECASE),
    'decision_and': re.compile(r'\bAnd\b', re.IGNORECASE),
    'decision_or': re.compile(r'\bOr\b', re.IGNORECASE),
    
    # Code structure
    'sub_function': re.compile(r'(Private|Public)?\s*(Sub|Function)\s+(\w+)', re.IGNORECASE),
    'end_sub': re.compile(r'End\s+(Sub|Function)', re.IGNORECASE),
    'property': re.compile(r'(Property\s+(Get|Let|Set))\s+(\w+)', re.IGNORECASE),
    
    # Comments
    'comment_line': re.compile(r"^\s*'.*$", re.MULTILINE),
    'comment_rem': re.compile(r'^\s*Rem\s+', re.IGNORECASE | re.MULTILINE),
    
    # Controls (in FRM files)
    'control': re.compile(r'Begin\s+(\w+)\.(\w+)\s+(\w+)', re.IGNORECASE),
    
    # Error handling
    'on_error_resume': re.compile(r'On\s+Error\s+Resume\s+Next', re.IGNORECASE),
    'on_error_goto': re.compile(r'On\s+Error\s+GoTo\s+(\w+)', re.IGNORECASE),
    
    # Nesting indicators
    'nesting_start': re.compile(r'\b(If|For|Do|While|With|Select)\b', re.IGNORECASE),
    'nesting_end': re.compile(r'\b(End\s+If|Next|Loop|Wend|End\s+With|End\s+Select)\b', re.IGNORECASE),
    
    # Magic numbers
    'magic_number': re.compile(r'[=<>]\s*(\d{2,})\b'),
    
    # Hardcoded strings
    'hardcoded_path': re.compile(r'"[A-Za-z]:\\[^"]*"'),
    'connection_string': re.compile(r'"[^"]*(?:Provider|Data Source|DSN)[^"]*"', re.IGNORECASE),
}


class VB6MetricsAnalyzer:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.metrics = {
            'summary': {},
            'files': [],
            'functions': [],
            'complexity_distribution': {'low': 0, 'medium': 0, 'high': 0, 'very_high': 0},
            'risk_indicators': []
        }
    
    def analyze(self):
        """Main analysis entry point."""
        print(f"📊 Analyzing metrics: {self.source_dir}")
        
        total_loc = 0
        total_comments = 0
        total_functions = 0
        total_complexity = 0
        
        for root, _, files in os.walk(self.source_dir):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in ['.frm', '.bas', '.cls', '.ctl']:
                    filepath = Path(root) / filename
                    file_metrics = self._analyze_file(filepath)
                    self.metrics['files'].append(file_metrics)
                    
                    total_loc += file_metrics['loc']
                    total_comments += file_metrics['comment_lines']
                    total_functions += file_metrics['function_count']
                    total_complexity += file_metrics['total_complexity']
        
        # Summary
        file_count = len(self.metrics['files'])
        self.metrics['summary'] = {
            'total_files': file_count,
            'total_loc': total_loc,
            'total_comment_lines': total_comments,
            'comment_ratio': round(total_comments / max(total_loc, 1) * 100, 2),
            'total_functions': total_functions,
            'average_complexity': round(total_complexity / max(total_functions, 1), 2),
            'average_loc_per_file': round(total_loc / max(file_count, 1), 2),
            'complexity_distribution': self.metrics['complexity_distribution'],
            'risk_score': self._calculate_risk_score()
        }
        
        return self.metrics
    
    def _analyze_file(self, filepath):
        """Analyze a single VB6 file."""
        content = self._read_file(filepath)
        if not content:
            return self._empty_metrics(filepath)
        
        lines = content.split('\n')
        
        # Basic counts
        loc = len([l for l in lines if l.strip() and not l.strip().startswith("'")])
        blank_lines = len([l for l in lines if not l.strip()])
        comment_lines = len(PATTERNS['comment_line'].findall(content))
        
        # Control count (for forms)
        controls = PATTERNS['control'].findall(content)
        control_count = len(controls)
        
        # Function analysis
        functions = self._analyze_functions(content)
        total_complexity = sum(f['complexity'] for f in functions)
        
        # Error handling
        resume_next = len(PATTERNS['on_error_resume'].findall(content))
        error_goto = len(PATTERNS['on_error_goto'].findall(content))
        
        # Nesting depth
        max_nesting = self._calculate_max_nesting(content)
        
        # Risk indicators
        if resume_next > 0:
            self.metrics['risk_indicators'].append({
                'file': str(filepath.name),
                'type': 'On Error Resume Next',
                'count': resume_next,
                'risk': 'MEDIUM'
            })
        
        if control_count > 50:
            self.metrics['risk_indicators'].append({
                'file': str(filepath.name),
                'type': 'High Control Count',
                'count': control_count,
                'risk': 'HIGH'
            })
        
        if max_nesting > 5:
            self.metrics['risk_indicators'].append({
                'file': str(filepath.name),
                'type': 'Deep Nesting',
                'count': max_nesting,
                'risk': 'MEDIUM'
            })
        
        return {
            'name': filepath.name,
            'path': str(filepath),
            'type': filepath.suffix.lower(),
            'loc': loc,
            'blank_lines': blank_lines,
            'comment_lines': comment_lines,
            'comment_ratio': round(comment_lines / max(loc, 1) * 100, 2),
            'control_count': control_count,
            'function_count': len(functions),
            'total_complexity': total_complexity,
            'average_complexity': round(total_complexity / max(len(functions), 1), 2),
            'max_nesting_depth': max_nesting,
            'on_error_resume_next': resume_next,
            'on_error_goto': error_goto,
            'functions': functions
        }
    
    def _analyze_functions(self, content):
        """Analyze functions and calculate cyclomatic complexity."""
        functions = []
        
        # Split content by function/sub boundaries
        func_matches = list(PATTERNS['sub_function'].finditer(content))
        
        for i, match in enumerate(func_matches):
            func_name = match.group(3)
            func_type = match.group(2)
            visibility = match.group(1) or 'Private'
            
            # Find function end
            start_pos = match.end()
            end_match = PATTERNS['end_sub'].search(content, start_pos)
            end_pos = end_match.start() if end_match else len(content)
            
            func_body = content[start_pos:end_pos]
            
            # Calculate complexity
            complexity = self._calculate_complexity(func_body)
            loc = len([l for l in func_body.split('\n') if l.strip()])
            
            # Classify complexity
            if complexity <= 5:
                self.metrics['complexity_distribution']['low'] += 1
                complexity_level = 'LOW'
            elif complexity <= 10:
                self.metrics['complexity_distribution']['medium'] += 1
                complexity_level = 'MEDIUM'
            elif complexity <= 20:
                self.metrics['complexity_distribution']['high'] += 1
                complexity_level = 'HIGH'
            else:
                self.metrics['complexity_distribution']['very_high'] += 1
                complexity_level = 'VERY_HIGH'
            
            functions.append({
                'name': func_name,
                'type': func_type,
                'visibility': visibility,
                'complexity': complexity,
                'complexity_level': complexity_level,
                'loc': loc
            })
            
            self.metrics['functions'].append({
                'name': func_name,
                'file': 'current',  # Will be updated
                'complexity': complexity,
                'complexity_level': complexity_level,
                'loc': loc
            })
        
        return functions
    
    def _calculate_complexity(self, code):
        """Calculate cyclomatic complexity for a code block."""
        complexity = 1  # Base complexity
        
        complexity += len(PATTERNS['decision_if'].findall(code))
        complexity += len(PATTERNS['decision_elseif'].findall(code))
        complexity += len(PATTERNS['decision_case'].findall(code))
        complexity += len(PATTERNS['decision_for'].findall(code))
        complexity += len(PATTERNS['decision_do'].findall(code))
        complexity += len(PATTERNS['decision_while'].findall(code))
        complexity += len(PATTERNS['decision_and'].findall(code))
        complexity += len(PATTERNS['decision_or'].findall(code))
        
        return complexity
    
    def _calculate_max_nesting(self, content):
        """Calculate maximum nesting depth."""
        max_depth = 0
        current_depth = 0
        
        for line in content.split('\n'):
            # Count nesting increases
            starts = len(PATTERNS['nesting_start'].findall(line))
            ends = len(PATTERNS['nesting_end'].findall(line))
            
            current_depth += starts
            max_depth = max(max_depth, current_depth)
            current_depth = max(0, current_depth - ends)
        
        return max_depth
    
    def _calculate_risk_score(self):
        """Calculate overall migration risk score (0-100)."""
        score = 0
        
        # Factor 1: Average complexity (up to 30 points)
        avg_complexity = self.metrics['summary'].get('average_complexity', 0)
        score += min(30, avg_complexity * 2)
        
        # Factor 2: Low comment ratio (up to 20 points)
        comment_ratio = self.metrics['summary'].get('comment_ratio', 0)
        if comment_ratio < 10:
            score += 20
        elif comment_ratio < 20:
            score += 10
        
        # Factor 3: High complexity functions (up to 25 points)
        high = self.metrics['complexity_distribution'].get('high', 0)
        very_high = self.metrics['complexity_distribution'].get('very_high', 0)
        score += min(25, (high * 2) + (very_high * 5))
        
        # Factor 4: Risk indicators (up to 25 points)
        risk_count = len(self.metrics['risk_indicators'])
        score += min(25, risk_count * 5)
        
        return min(100, score)
    
    def _read_file(self, filepath):
        """Read file with proper encoding."""
        for enc in ['utf-8', 'latin1', 'cp1252']:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    return f.read()
            except:
                continue
        return None
    
    def _empty_metrics(self, filepath):
        """Return empty metrics for unreadable files."""
        return {
            'name': filepath.name,
            'path': str(filepath),
            'type': filepath.suffix.lower(),
            'loc': 0,
            'blank_lines': 0,
            'comment_lines': 0,
            'comment_ratio': 0,
            'control_count': 0,
            'function_count': 0,
            'total_complexity': 0,
            'average_complexity': 0,
            'max_nesting_depth': 0,
            'on_error_resume_next': 0,
            'on_error_goto': 0,
            'functions': []
        }


def main():
    parser = argparse.ArgumentParser(description="VB6 Metrics Analyzer")
    parser.add_argument("source_dir", help="Directory containing VB6 source code")
    parser.add_argument("-o", "--output", default="vb6_metrics.json", help="Output JSON file")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.source_dir):
        print(f"❌ Error: Directory not found: {args.source_dir}")
        return 1
    
    analyzer = VB6MetricsAnalyzer(args.source_dir)
    metrics = analyzer.analyze()
    
    indent = 2 if args.pretty else None
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=indent, ensure_ascii=False)
    
    print(f"✅ Metrics analysis complete: {args.output}")
    print(f"   📊 Files analyzed: {metrics['summary']['total_files']}")
    print(f"   📝 Total LOC: {metrics['summary']['total_loc']}")
    print(f"   🔧 Functions: {metrics['summary']['total_functions']}")
    print(f"   📈 Avg Complexity: {metrics['summary']['average_complexity']}")
    print(f"   ⚠️  Risk Score: {metrics['summary']['risk_score']}/100")
    
    return 0


if __name__ == "__main__":
    exit(main())
