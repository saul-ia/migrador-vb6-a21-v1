#!/usr/bin/env python3
"""
Coverage Validator - Validates test coverage against thresholds.

This script:
1. Reads coverage summary files (Istanbul/Jest format)
2. Compares against configured thresholds
3. Generates a validation report
4. Returns exit code for CI/CD integration
"""

import os
import json
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CoverageMetrics:
    lines: float
    statements: float
    functions: float
    branches: float

@dataclass
class ThresholdConfig:
    lines: float = 80.0
    statements: float = 80.0
    functions: float = 80.0
    branches: float = 70.0

@dataclass
class ValidationResult:
    metric: str
    actual: float
    threshold: float
    passed: bool

# =============================================================================
# DEFAULT THRESHOLDS
# =============================================================================

DEFAULT_THRESHOLDS = ThresholdConfig(
    lines=80.0,
    statements=80.0,
    functions=80.0,
    branches=70.0
)

# =============================================================================
# VALIDATOR
# =============================================================================

class CoverageValidator:
    def __init__(self, thresholds: ThresholdConfig = None):
        self.thresholds = thresholds or DEFAULT_THRESHOLDS
        self.results: Dict[str, list] = {}
        
    def validate_coverage_file(self, coverage_file: Path, layer: str) -> bool:
        """Validate a single coverage summary file."""
        if not coverage_file.exists():
            print(f"  ⚠ Coverage file not found: {coverage_file}")
            return False
        
        try:
            data = json.loads(coverage_file.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"  ⚠ Error reading coverage file: {e}")
            return False
        
        # Extract totals
        totals = data.get('total', {})
        
        metrics = CoverageMetrics(
            lines=totals.get('lines', {}).get('pct', 0),
            statements=totals.get('statements', {}).get('pct', 0),
            functions=totals.get('functions', {}).get('pct', 0),
            branches=totals.get('branches', {}).get('pct', 0)
        )
        
        # Validate each metric
        results = []
        all_passed = True
        
        for metric_name in ['lines', 'statements', 'functions', 'branches']:
            actual = getattr(metrics, metric_name)
            threshold = getattr(self.thresholds, metric_name)
            passed = actual >= threshold
            
            results.append(ValidationResult(
                metric=metric_name,
                actual=actual,
                threshold=threshold,
                passed=passed
            ))
            
            if not passed:
                all_passed = False
        
        self.results[layer] = results
        return all_passed
    
    def validate_all(self, backend_file: str = None, frontend_file: str = None) -> bool:
        """Validate all coverage files."""
        overall_pass = True
        
        if backend_file:
            backend_path = Path(backend_file)
            if not self.validate_coverage_file(backend_path, 'Backend'):
                overall_pass = False
                
        if frontend_file:
            frontend_path = Path(frontend_file)
            if not self.validate_coverage_file(frontend_path, 'Frontend'):
                overall_pass = False
        
        return overall_pass
    
    def generate_report(self, output_path: str = None) -> str:
        """Generate markdown validation report."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        lines = [
            '# Coverage Validation Report',
            f'\n**Generated:** {timestamp}',
            f'\n**Thresholds:** Lines {self.thresholds.lines}% | Branches {self.thresholds.branches}% | Functions {self.thresholds.functions}%',
            '\n---\n'
        ]
        
        overall_pass = True
        
        for layer, results in self.results.items():
            layer_pass = all(r.passed for r in results)
            if not layer_pass:
                overall_pass = False
                
            status = '✅ PASS' if layer_pass else '❌ FAIL'
            lines.append(f'## {layer} Coverage {status}\n')
            lines.append('| Metric | Actual | Threshold | Status |')
            lines.append('|--------|--------|-----------|--------|')
            
            for r in results:
                status_icon = '✅' if r.passed else '❌'
                lines.append(f'| {r.metric.capitalize()} | {r.actual:.1f}% | {r.threshold:.1f}% | {status_icon} |')
            
            lines.append('')
        
        # Summary
        lines.append('---\n')
        if overall_pass:
            lines.append('## ✅ Overall: PASS')
            lines.append('\nAll coverage thresholds met. Ready for deployment.')
        else:
            lines.append('## ❌ Overall: FAIL')
            lines.append('\nCoverage thresholds not met. Deployment blocked.')
            lines.append('\n### Action Required')
            lines.append('1. Add more unit tests to increase coverage')
            lines.append('2. Focus on untested branches and functions')
            lines.append('3. Run `npm test -- --coverage` to see detailed report')
        
        report = '\n'.join(lines)
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report, encoding='utf-8')
            print(f'\nReport written to: {output_path}')
        
        return report
    
    def print_summary(self):
        """Print summary to console."""
        print('\n' + '=' * 50)
        print('COVERAGE VALIDATION SUMMARY')
        print('=' * 50)
        
        for layer, results in self.results.items():
            layer_pass = all(r.passed for r in results)
            status = '✅ PASS' if layer_pass else '❌ FAIL'
            print(f'\n{layer}: {status}')
            
            for r in results:
                status_icon = '✓' if r.passed else '✗'
                print(f'  {status_icon} {r.metric}: {r.actual:.1f}% (min: {r.threshold:.1f}%)')
        
        overall = all(all(r.passed for r in results) for results in self.results.values())
        print('\n' + '=' * 50)
        print(f'OVERALL: {"✅ PASS" if overall else "❌ FAIL"}')
        print('=' * 50)
        
        return overall

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Validate test coverage against thresholds'
    )
    parser.add_argument('--backend', '-b', help='Backend coverage-summary.json path')
    parser.add_argument('--frontend', '-f', help='Frontend coverage-summary.json path')
    parser.add_argument('--threshold', '-t', type=float, default=80.0, 
                       help='Line coverage threshold (default: 80)')
    parser.add_argument('--branch-threshold', '-bt', type=float, default=70.0,
                       help='Branch coverage threshold (default: 70)')
    parser.add_argument('--output', '-o', help='Output report path (markdown)')
    parser.add_argument('--strict', action='store_true', 
                       help='Exit with error code if thresholds not met')
    
    args = parser.parse_args()
    
    if not args.backend and not args.frontend:
        # Try to find coverage files automatically
        possible_paths = [
            'analysis/coverage/backend/coverage-summary.json',
            'analysis/coverage/frontend/coverage-summary.json',
            'coverage/coverage-summary.json'
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                if 'backend' in path:
                    args.backend = path
                elif 'frontend' in path:
                    args.frontend = path
                else:
                    args.backend = path
    
    if not args.backend and not args.frontend:
        print("Error: No coverage files found or specified")
        print("Run tests with --coverage to generate coverage files")
        return 1
    
    # Configure thresholds
    thresholds = ThresholdConfig(
        lines=args.threshold,
        statements=args.threshold,
        functions=args.threshold,
        branches=args.branch_threshold
    )
    
    # Run validation
    validator = CoverageValidator(thresholds)
    validator.validate_all(
        backend_file=args.backend,
        frontend_file=args.frontend
    )
    
    # Generate report
    if args.output:
        validator.generate_report(args.output)
    
    # Print summary and get result
    passed = validator.print_summary()
    
    # Return appropriate exit code
    if args.strict and not passed:
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
