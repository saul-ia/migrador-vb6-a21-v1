#!/usr/bin/env python3
"""
Test Failure Auto-Repair - Parses test failures and generates fixes.

This script:
1. Parses Jest/Playwright test output
2. Identifies failure patterns
3. Generates AI-friendly repair instructions
4. Tracks repair iterations

Used by the testing-verifier agent for self-healing migrations.
"""

import os
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TestFailure:
    test_name: str
    file_path: str
    error_type: str
    error_message: str
    expected: Optional[str] = None
    received: Optional[str] = None
    stack_trace: Optional[str] = None
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None

@dataclass
class RepairPlan:
    failures: List[TestFailure]
    iteration: int
    timestamp: str
    repairs_needed: List[Dict]

# =============================================================================
# KNOWN ERROR PATTERNS
# =============================================================================

ERROR_PATTERNS = {
    # TypeScript/Angular errors
    'property_not_exist': {
        'pattern': r"Property '(\w+)' does not exist on type '(\w+)'",
        'fix_template': "Add property '{property}' to interface/class '{type}' or check for typo"
    },
    'cannot_find_module': {
        'pattern': r"Cannot find module '([^']+)'",
        'fix_template': "Import missing module '{module}' or install package"
    },
    'undefined_signal': {
        'pattern': r"Cannot read properties of undefined \(reading '(\w+)'\)",
        'fix_template': "Initialize signal '{property}' before use or check for null"
    },
    'missing_provider': {
        'pattern': r"NullInjectorError: No provider for (\w+)",
        'fix_template': "Add '{service}' to providers in component or app.config"
    },
    
    # Jest assertion errors
    'expect_mismatch': {
        'pattern': r"Expected:.*?Received:",
        'fix_template': "Update expected value or fix implementation to match expected"
    },
    'undefined_function': {
        'pattern': r"(\w+) is not a function",
        'fix_template': "Check that '{name}' is properly exported and imported"
    },
    'mock_not_called': {
        'pattern': r"Expected.*to have been called",
        'fix_template': "Verify mock setup or ensure function is actually called"
    },
    
    # Playwright errors
    'element_not_found': {
        'pattern': r"Timeout.*waiting for selector.*'([^']+)'",
        'fix_template': "Update selector '{selector}' to match actual element or increase timeout"
    },
    'navigation_timeout': {
        'pattern': r"page.goto: Timeout \d+ms exceeded",
        'fix_template': "Increase navigation timeout or check if server is running"
    },
    'assertion_failed': {
        'pattern': r"expect\(.*\)\.toHaveURL\(.*\)",
        'fix_template': "Verify route configuration matches expected URL"
    },
    
    # Zoneless-specific errors
    'zone_change_detection': {
        'pattern': r"NG0100|ExpressionChangedAfterItHasBeenChecked",
        'fix_template': "Use signal.set() inside effect() or move to constructor"
    },
    'onpush_required': {
        'pattern': r"NG0(?:0)?(?:500|501)",
        'fix_template': "Add changeDetection: ChangeDetectionStrategy.OnPush to component"
    }
}

# =============================================================================
# REPAIR SUGGESTIONS
# =============================================================================

REPAIR_STRATEGIES = {
    'property_not_exist': {
        'action': 'add_property',
        'priority': 'high',
        'auto_fixable': True
    },
    'cannot_find_module': {
        'action': 'add_import',
        'priority': 'high',
        'auto_fixable': True
    },
    'undefined_signal': {
        'action': 'initialize_signal',
        'priority': 'high',
        'auto_fixable': True
    },
    'missing_provider': {
        'action': 'add_provider',
        'priority': 'high',
        'auto_fixable': True
    },
    'element_not_found': {
        'action': 'update_selector',
        'priority': 'medium',
        'auto_fixable': False
    },
    'expect_mismatch': {
        'action': 'update_assertion',
        'priority': 'medium',
        'auto_fixable': False
    },
    'zone_change_detection': {
        'action': 'fix_zoneless_pattern',
        'priority': 'critical',
        'auto_fixable': True
    }
}

# =============================================================================
# PARSER
# =============================================================================

class TestFailureParser:
    def __init__(self):
        self.failures: List[TestFailure] = []
        
    def parse_jest_output(self, output: str) -> List[TestFailure]:
        """Parse Jest test output for failures."""
        failures = []
        
        # Find failed test blocks
        fail_pattern = re.compile(
            r'● ([^\n]+)\n\n(.*?)(?=\n\n● |\Z)',
            re.DOTALL
        )
        
        for match in fail_pattern.finditer(output):
            test_name = match.group(1).strip()
            error_block = match.group(2).strip()
            
            failure = self._parse_error_block(test_name, error_block)
            if failure:
                failures.append(failure)
        
        return failures
    
    def parse_playwright_output(self, output: str) -> List[TestFailure]:
        """Parse Playwright test output for failures."""
        failures = []
        
        # Find failed test blocks
        fail_pattern = re.compile(
            r'(\d+)\) \[.*?\] › (.*?)\n(.*?)(?=\n\d+\) |\Z)',
            re.DOTALL
        )
        
        for match in fail_pattern.finditer(output):
            test_path = match.group(2).strip()
            error_block = match.group(3).strip()
            
            failure = self._parse_error_block(test_path, error_block)
            if failure:
                failure.file_path = test_path.split(' › ')[0] if ' › ' in test_path else test_path
                failures.append(failure)
        
        return failures
    
    def _parse_error_block(self, test_name: str, error_block: str) -> Optional[TestFailure]:
        """Parse an error block and identify the error type."""
        # Try to match known patterns
        for error_key, pattern_info in ERROR_PATTERNS.items():
            match = re.search(pattern_info['pattern'], error_block, re.DOTALL)
            if match:
                # Extract file path and line number if present
                file_match = re.search(r'at.*?(\S+\.ts):(\d+)', error_block)
                file_path = file_match.group(1) if file_match else ''
                line_number = int(file_match.group(2)) if file_match else None
                
                # Build suggested fix
                fix_template = pattern_info['fix_template']
                groups = match.groups()
                for i, group in enumerate(groups):
                    fix_template = fix_template.replace(f'{{{list(ERROR_PATTERNS[error_key].keys())[0]}}}', group or '')
                
                return TestFailure(
                    test_name=test_name,
                    file_path=file_path,
                    error_type=error_key,
                    error_message=error_block[:500],  # Limit size
                    line_number=line_number,
                    suggested_fix=fix_template
                )
        
        # Unknown error pattern
        return TestFailure(
            test_name=test_name,
            file_path='',
            error_type='unknown',
            error_message=error_block[:500],
            suggested_fix='Manual review required - unknown error pattern'
        )
    
    def parse_output_file(self, file_path: Path) -> List[TestFailure]:
        """Parse test output from a file."""
        if not file_path.exists():
            return []
        
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # Detect test framework from content
        if 'FAIL' in content and '●' in content:
            return self.parse_jest_output(content)
        elif 'passed' in content and 'failed' in content:
            return self.parse_playwright_output(content)
        
        return []

# =============================================================================
# REPAIR PLANNER
# =============================================================================

class RepairPlanner:
    def __init__(self, output_dir: str, max_iterations_per_error: int = 5):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.iteration = self._get_current_iteration()
        self.max_iterations_per_error = max_iterations_per_error
        self.error_history = self._load_error_history()
    
    def _load_error_history(self) -> Dict[str, int]:
        """Load per-error iteration counts from history file."""
        history_file = self.output_dir / 'error_history.json'
        if history_file.exists():
            try:
                return json.loads(history_file.read_text(encoding='utf-8'))
            except:
                return {}
        return {}
    
    def _save_error_history(self) -> None:
        """Save per-error iteration counts to history file."""
        history_file = self.output_dir / 'error_history.json'
        history_file.write_text(json.dumps(self.error_history, indent=2), encoding='utf-8')
    
    def _generate_error_id(self, failure: TestFailure) -> str:
        """Generate unique ID for an error based on file, line, and type."""
        return f"{failure.file_path}:{failure.line_number}:{failure.error_type}"
        
    def _get_current_iteration(self) -> int:
        """Get the current iteration number from existing repair plans."""
        existing = list(self.output_dir.glob('repair_plan_*.json'))
        if not existing:
            return 1
        
        max_iter = 0
        for f in existing:
            match = re.search(r'repair_plan_(\d+)', f.name)
            if match:
                max_iter = max(max_iter, int(match.group(1)))
        
        return max_iter + 1
    
    def create_repair_plan(self, failures: List[TestFailure]) -> RepairPlan:
        """Create a repair plan from test failures (max 5 iterations PER ERROR)."""
        repairs = []
        skipped_max_iter = []
        
        for failure in failures:
            error_id = self._generate_error_id(failure)
            
            # Check per-error iteration count
            current_count = self.error_history.get(error_id, 0)
            
            if current_count >= self.max_iterations_per_error:
                # Skip this error - max iterations reached for THIS specific error
                skipped_max_iter.append({
                    'test_name': failure.test_name,
                    'file_path': failure.file_path,
                    'error_id': error_id,
                    'iterations': current_count,
                    'status': 'MAX_ITERATIONS_REACHED'
                })
                continue
            
            # Increment iteration count for this error
            self.error_history[error_id] = current_count + 1
            
            strategy = REPAIR_STRATEGIES.get(failure.error_type, {
                'action': 'manual_review',
                'priority': 'low',
                'auto_fixable': False
            })
            
            repairs.append({
                'test_name': failure.test_name,
                'file_path': failure.file_path,
                'line_number': failure.line_number,
                'error_type': failure.error_type,
                'error_id': error_id,
                'iteration_for_error': self.error_history[error_id],
                'max_iterations': self.max_iterations_per_error,
                'suggested_fix': failure.suggested_fix,
                'action': strategy['action'],
                'priority': strategy['priority'],
                'auto_fixable': strategy['auto_fixable']
            })
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        repairs.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return RepairPlan(
            failures=failures,
            iteration=self.iteration,
            timestamp=datetime.now().isoformat(),
            repairs_needed=repairs
        ), skipped_max_iter
    
    def create_repair_plan_with_skipped(self, failures: List[TestFailure]) -> tuple:
        """Wrapper that returns plan and skipped errors separately."""
        plan, skipped = self.create_repair_plan(failures)
        return plan, skipped
    
    def save_repair_plan(self, plan: RepairPlan, skipped_errors: List[Dict] = None) -> Path:
        """Save repair plan to file and update error history."""
        output_file = self.output_dir / f'repair_plan_{plan.iteration:03d}.json'
        
        data = {
            'iteration': plan.iteration,
            'timestamp': plan.timestamp,
            'total_failures': len(plan.failures),
            'auto_fixable': sum(1 for r in plan.repairs_needed if r['auto_fixable']),
            'repairs': plan.repairs_needed,
            'skipped_max_iterations': skipped_errors or []
        }
        
        output_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        
        # Save per-error iteration history
        self._save_error_history()
        
        return output_file
    
    def generate_repair_instructions(self, plan: RepairPlan) -> str:
        """Generate human/AI readable repair instructions."""
        lines = [
            f"# Test Repair Instructions - Iteration {plan.iteration}",
            f"\n**Timestamp:** {plan.timestamp}",
            f"**Total Failures:** {len(plan.failures)}",
            f"**Auto-Fixable:** {sum(1 for r in plan.repairs_needed if r['auto_fixable'])}",
            "\n---\n",
            "## Repairs Required\n"
        ]
        
        for i, repair in enumerate(plan.repairs_needed, 1):
            auto_tag = "🤖 AUTO" if repair['auto_fixable'] else "👤 MANUAL"
            priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '⚪'}.get(repair['priority'], '⚪')
            
            lines.append(f"### {i}. {repair['test_name']}")
            lines.append(f"- **Priority:** {priority_emoji} {repair['priority'].upper()}")
            lines.append(f"- **Type:** {repair['error_type']}")
            lines.append(f"- **File:** `{repair['file_path']}`" + (f" (line {repair['line_number']})" if repair['line_number'] else ""))
            lines.append(f"- **Action:** {auto_tag} {repair['action']}")
            lines.append(f"- **Fix:** {repair['suggested_fix']}")
            lines.append("")
        
        return '\n'.join(lines)

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Parse test failures and generate repair plans for self-healing migrations'
    )
    parser.add_argument('--input', '-i', required=True, help='Test output file to parse')
    parser.add_argument('--output', '-o', default='analysis/repairs', help='Output directory for repair plans')
    parser.add_argument('--max-iterations', '-m', type=int, default=5, help='Maximum repair iterations')
    parser.add_argument('--json', action='store_true', help='Output only JSON (for automation)')
    
    args = parser.parse_args()
    
    # Parse test output
    test_parser = TestFailureParser()
    failures = test_parser.parse_output_file(Path(args.input))
    
    if not failures:
        if not args.json:
            print("✅ No test failures found!")
        else:
            print(json.dumps({'status': 'success', 'failures': 0}))
        return 0
    
    # Create repair plan with per-error iteration tracking
    planner = RepairPlanner(args.output, max_iterations_per_error=args.max_iterations)
    
    # Note: Global iteration check removed - we now track per-error iterations
    # Errors that hit max iter are skipped individually, not blocking others
    
    plan, skipped_errors = planner.create_repair_plan_with_skipped(failures)
    plan_file = planner.save_repair_plan(plan, skipped_errors)
    
    if args.json:
        print(json.dumps({
            'status': 'repairs_needed',
            'iteration': plan.iteration,
            'total_failures': len(failures),
            'auto_fixable': sum(1 for r in plan.repairs_needed if r['auto_fixable']),
            'plan_file': str(plan_file)
        }))
    else:
        print(planner.generate_repair_instructions(plan))
        print(f"\n📄 Repair plan saved to: {plan_file}")
    
    return 1  # Indicate repairs needed

if __name__ == '__main__':
    exit(main())
