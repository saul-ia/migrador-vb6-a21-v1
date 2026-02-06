#!/usr/bin/env python3
"""
Self-Healing Repair Report Generator

Generates comprehensive HTML reports of the auto-repair process including:
- Errors repaired vs. not repaired
- Iterations per error
- Explanation of fixes applied
- Final status

Used after the self-healing loop completes.
"""

import os
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import html

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ErrorRepairRecord:
    error_id: str
    error_type: str
    file_path: str
    line_number: Optional[int]
    original_message: str
    iterations: int
    fixes_applied: List[str]
    status: str  # 'REPAIRED', 'FAILED', 'SKIPPED'
    explanation: str
    timestamp: str

@dataclass
class RepairSummary:
    total_errors: int
    repaired: int
    failed: int
    skipped: int
    total_iterations: int
    start_time: str
    end_time: str
    duration_seconds: float

# =============================================================================
# REPORT GENERATOR
# =============================================================================

class RepairReportGenerator:
    def __init__(self, repairs_dir: str):
        self.repairs_dir = Path(repairs_dir)
        self.records: List[ErrorRepairRecord] = []
        self.error_iterations: Dict[str, int] = {}  # Track iterations per error_id
        self.max_iterations_per_error = 5
        
    def load_repair_history(self) -> None:
        """Load all repair plans and build error history."""
        repair_files = sorted(self.repairs_dir.glob('repair_plan_*.json'))
        
        error_history: Dict[str, Dict] = {}
        
        for repair_file in repair_files:
            try:
                data = json.loads(repair_file.read_text(encoding='utf-8'))
                iteration = data.get('iteration', 0)
                
                for repair in data.get('repairs', []):
                    error_id = self._generate_error_id(repair)
                    
                    if error_id not in error_history:
                        error_history[error_id] = {
                            'error_type': repair.get('error_type', 'unknown'),
                            'file_path': repair.get('file_path', ''),
                            'line_number': repair.get('line_number'),
                            'original_message': repair.get('suggested_fix', ''),
                            'iterations': 0,
                            'fixes_applied': [],
                            'first_seen': data.get('timestamp', ''),
                            'last_seen': data.get('timestamp', ''),
                            'auto_fixable': repair.get('auto_fixable', False)
                        }
                    
                    error_history[error_id]['iterations'] += 1
                    error_history[error_id]['last_seen'] = data.get('timestamp', '')
                    error_history[error_id]['fixes_applied'].append(
                        f"Iteration {iteration}: {repair.get('action', 'unknown')}"
                    )
            except Exception as e:
                print(f"Warning: Could not parse {repair_file}: {e}")
        
        # Convert to records and determine status
        for error_id, history in error_history.items():
            status = self._determine_status(error_id, history)
            explanation = self._generate_explanation(history, status)
            
            self.records.append(ErrorRepairRecord(
                error_id=error_id,
                error_type=history['error_type'],
                file_path=history['file_path'],
                line_number=history['line_number'],
                original_message=history['original_message'],
                iterations=history['iterations'],
                fixes_applied=history['fixes_applied'],
                status=status,
                explanation=explanation,
                timestamp=history['last_seen']
            ))
    
    def _generate_error_id(self, repair: Dict) -> str:
        """Generate a unique ID for an error based on file, line, and type."""
        file_path = repair.get('file_path', 'unknown')
        line_number = repair.get('line_number', 0)
        error_type = repair.get('error_type', 'unknown')
        return f"{file_path}:{line_number}:{error_type}"
    
    def _determine_status(self, error_id: str, history: Dict) -> str:
        """Determine if error was repaired, failed, or skipped."""
        if not history.get('auto_fixable', False):
            return 'SKIPPED'
        
        if history['iterations'] >= self.max_iterations_per_error:
            return 'FAILED'
        
        # Check if error appears in the last repair plan
        # If not, it was successfully repaired
        last_plans = sorted(self.repairs_dir.glob('repair_plan_*.json'))
        if last_plans:
            last_plan = json.loads(last_plans[-1].read_text(encoding='utf-8'))
            for repair in last_plan.get('repairs', []):
                if self._generate_error_id(repair) == error_id:
                    if history['iterations'] >= self.max_iterations_per_error:
                        return 'FAILED'
                    return 'IN_PROGRESS'
        
        return 'REPAIRED'
    
    def _generate_explanation(self, history: Dict, status: str) -> str:
        """Generate human-readable explanation for the repair outcome."""
        error_type = history['error_type']
        iterations = history['iterations']
        
        explanations = {
            'REPAIRED': f"Successfully fixed after {iterations} iteration(s). "
                       f"The {error_type} error was auto-repaired by applying the suggested fix.",
            'FAILED': f"Could not repair after {iterations} attempts (max {self.max_iterations_per_error}). "
                     f"The {error_type} error may require manual intervention due to complexity "
                     "or dependencies that couldn't be automatically resolved.",
            'SKIPPED': f"This {error_type} error was marked as not auto-fixable. "
                      "Manual review is required as the fix pattern is not recognized.",
            'IN_PROGRESS': f"Currently being processed. {iterations} iteration(s) so far."
        }
        
        return explanations.get(status, "Unknown status")
    
    def calculate_summary(self) -> RepairSummary:
        """Calculate summary statistics."""
        repaired = sum(1 for r in self.records if r.status == 'REPAIRED')
        failed = sum(1 for r in self.records if r.status == 'FAILED')
        skipped = sum(1 for r in self.records if r.status == 'SKIPPED')
        total_iterations = sum(r.iterations for r in self.records)
        
        # Get timestamps
        timestamps = [r.timestamp for r in self.records if r.timestamp]
        start_time = min(timestamps) if timestamps else datetime.now().isoformat()
        end_time = max(timestamps) if timestamps else datetime.now().isoformat()
        
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = (end_dt - start_dt).total_seconds()
        except:
            duration = 0
        
        return RepairSummary(
            total_errors=len(self.records),
            repaired=repaired,
            failed=failed,
            skipped=skipped,
            total_iterations=total_iterations,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration
        )
    
    def generate_html_report(self, output_path: str) -> Path:
        """Generate comprehensive HTML report."""
        summary = self.calculate_summary()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate percentages
        success_rate = (summary.repaired / summary.total_errors * 100) if summary.total_errors > 0 else 100
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Self-Healing Repair Report</title>
    <style>
        :root {{
            --success: #10b981;
            --error: #ef4444;
            --warning: #f59e0b;
            --info: #3b82f6;
            --bg-dark: #1e293b;
            --bg-card: #334155;
            --text: #f1f5f9;
            --text-muted: #94a3b8;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: var(--text-muted);
            font-size: 1.1rem;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        
        .stat-card {{
            background: var(--bg-card);
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }}
        
        .stat-value {{
            font-size: 3rem;
            font-weight: 700;
            line-height: 1;
        }}
        
        .stat-value.success {{ color: var(--success); }}
        .stat-value.error {{ color: var(--error); }}
        .stat-value.warning {{ color: var(--warning); }}
        .stat-value.info {{ color: var(--info); }}
        
        .stat-label {{
            color: var(--text-muted);
            margin-top: 0.5rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .progress-bar {{
            background: var(--bg-dark);
            border-radius: 9999px;
            height: 1.5rem;
            margin: 2rem 0;
            overflow: hidden;
            position: relative;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 9999px;
            transition: width 0.5s ease;
        }}
        
        .progress-fill.success {{ background: linear-gradient(90deg, #10b981, #34d399); }}
        .progress-fill.mixed {{ background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444); }}
        
        .progress-label {{
            position: absolute;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            font-weight: 600;
            font-size: 0.875rem;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            margin: 2rem 0 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--bg-card);
        }}
        
        .error-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        
        .error-table th,
        .error-table td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--bg-card);
        }}
        
        .error-table th {{
            background: var(--bg-card);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }}
        
        .error-table tr:hover {{
            background: rgba(59, 130, 246, 0.1);
        }}
        
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-REPAIRED {{ background: rgba(16, 185, 129, 0.2); color: var(--success); }}
        .status-FAILED {{ background: rgba(239, 68, 68, 0.2); color: var(--error); }}
        .status-SKIPPED {{ background: rgba(245, 158, 11, 0.2); color: var(--warning); }}
        
        .file-path {{
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            color: var(--info);
        }}
        
        .iteration-badge {{
            background: var(--bg-dark);
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.85rem;
        }}
        
        .explanation {{
            font-size: 0.85rem;
            color: var(--text-muted);
            max-width: 300px;
        }}
        
        .fixes-list {{
            font-size: 0.75rem;
            color: var(--text-muted);
            list-style: none;
            padding: 0;
        }}
        
        .fixes-list li {{
            padding: 0.25rem 0;
        }}
        
        footer {{
            text-align: center;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid var(--bg-card);
            color: var(--text-muted);
            font-size: 0.875rem;
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin: 1rem 0;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        
        .legend-dot.success {{ background: var(--success); }}
        .legend-dot.error {{ background: var(--error); }}
        .legend-dot.warning {{ background: var(--warning); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔧 Self-Healing Repair Report</h1>
            <p class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <div class="summary-grid">
            <div class="stat-card">
                <div class="stat-value info">{summary.total_errors}</div>
                <div class="stat-label">Total Errors</div>
            </div>
            <div class="stat-card">
                <div class="stat-value success">{summary.repaired}</div>
                <div class="stat-label">Repaired ✅</div>
            </div>
            <div class="stat-card">
                <div class="stat-value error">{summary.failed}</div>
                <div class="stat-label">Failed ❌</div>
            </div>
            <div class="stat-card">
                <div class="stat-value warning">{summary.skipped}</div>
                <div class="stat-label">Skipped ⚠️</div>
            </div>
            <div class="stat-card">
                <div class="stat-value info">{summary.total_iterations}</div>
                <div class="stat-label">Total Iterations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="font-size: 1.5rem; color: var(--text);">{summary.duration_seconds:.1f}s</div>
                <div class="stat-label">Duration</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill {'success' if success_rate == 100 else 'mixed'}" 
                 style="width: {success_rate}%"></div>
            <span class="progress-label">{success_rate:.1f}% Success Rate</span>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <span class="legend-dot success"></span>
                <span>Repaired</span>
            </div>
            <div class="legend-item">
                <span class="legend-dot error"></span>
                <span>Failed (max iterations)</span>
            </div>
            <div class="legend-item">
                <span class="legend-dot warning"></span>
                <span>Skipped (not auto-fixable)</span>
            </div>
        </div>
        
        <h2 class="section-title">📋 Error Details</h2>
        
        <table class="error-table">
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Type</th>
                    <th>File</th>
                    <th>Iterations</th>
                    <th>Explanation</th>
                </tr>
            </thead>
            <tbody>
                {self._generate_table_rows()}
            </tbody>
        </table>
        
        <footer>
            <p>Self-Healing Migration System • Max {self.max_iterations_per_error} iterations per error</p>
            <p>Report generated by <strong>testing-verifier</strong> agent</p>
        </footer>
    </div>
</body>
</html>'''
        
        output_file.write_text(html_content, encoding='utf-8')
        return output_file
    
    def _generate_table_rows(self) -> str:
        """Generate HTML table rows for each error."""
        rows = []
        
        # Sort: Failed first, then Skipped, then Repaired
        sorted_records = sorted(
            self.records,
            key=lambda r: {'FAILED': 0, 'SKIPPED': 1, 'REPAIRED': 2}.get(r.status, 3)
        )
        
        for record in sorted_records:
            file_display = Path(record.file_path).name if record.file_path else 'Unknown'
            line_info = f":{record.line_number}" if record.line_number else ""
            
            rows.append(f'''
                <tr>
                    <td><span class="status-badge status-{record.status}">{record.status}</span></td>
                    <td><code>{html.escape(record.error_type)}</code></td>
                    <td>
                        <span class="file-path">{html.escape(file_display)}{line_info}</span>
                    </td>
                    <td><span class="iteration-badge">{record.iterations} / {self.max_iterations_per_error}</span></td>
                    <td><span class="explanation">{html.escape(record.explanation)}</span></td>
                </tr>
            ''')
        
        return '\n'.join(rows)
    
    def generate_json_summary(self, output_path: str) -> Path:
        """Generate JSON summary for programmatic access."""
        summary = self.calculate_summary()
        output_file = Path(output_path)
        
        data = {
            'summary': {
                'total_errors': summary.total_errors,
                'repaired': summary.repaired,
                'failed': summary.failed,
                'skipped': summary.skipped,
                'total_iterations': summary.total_iterations,
                'success_rate': (summary.repaired / summary.total_errors * 100) if summary.total_errors > 0 else 100,
                'start_time': summary.start_time,
                'end_time': summary.end_time,
                'duration_seconds': summary.duration_seconds
            },
            'errors': [
                {
                    'error_id': r.error_id,
                    'error_type': r.error_type,
                    'file_path': r.file_path,
                    'line_number': r.line_number,
                    'iterations': r.iterations,
                    'status': r.status,
                    'explanation': r.explanation,
                    'fixes_applied': r.fixes_applied
                }
                for r in self.records
            ]
        }
        
        output_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        return output_file

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate self-healing repair report from repair history'
    )
    parser.add_argument('--repairs-dir', '-r', default='analysis/repairs',
                       help='Directory containing repair plan JSON files')
    parser.add_argument('--output', '-o', default='analysis/REPAIR_REPORT.html',
                       help='Output HTML report path')
    parser.add_argument('--json-output', '-j', default='analysis/repair-summary.json',
                       help='Output JSON summary path')
    parser.add_argument('--max-iterations', '-m', type=int, default=5,
                       help='Maximum iterations per specific error')
    
    args = parser.parse_args()
    
    # Generate report
    generator = RepairReportGenerator(args.repairs_dir)
    generator.max_iterations_per_error = args.max_iterations
    generator.load_repair_history()
    
    if not generator.records:
        print("✅ No repair history found - all tests passed on first run!")
        # Generate empty success report
        summary = RepairSummary(
            total_errors=0, repaired=0, failed=0, skipped=0,
            total_iterations=0,
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat(),
            duration_seconds=0
        )
        print(f"📄 Report: {args.output}")
        return 0
    
    html_path = generator.generate_html_report(args.output)
    json_path = generator.generate_json_summary(args.json_output)
    
    summary = generator.calculate_summary()
    
    print(f"\n{'='*60}")
    print("🔧 SELF-HEALING REPAIR SUMMARY")
    print(f"{'='*60}")
    print(f"  Total Errors:    {summary.total_errors}")
    print(f"  ✅ Repaired:      {summary.repaired}")
    print(f"  ❌ Failed:        {summary.failed}")
    print(f"  ⚠️  Skipped:       {summary.skipped}")
    print(f"  🔄 Iterations:    {summary.total_iterations}")
    print(f"  ⏱️  Duration:      {summary.duration_seconds:.1f}s")
    print(f"{'='*60}")
    print(f"📄 HTML Report: {html_path}")
    print(f"📊 JSON Summary: {json_path}")
    
    # Return exit code based on status
    if summary.failed > 0:
        print(f"\n⚠️  {summary.failed} error(s) could not be auto-repaired.")
        return 1
    
    print("\n✅ All errors were successfully repaired!")
    return 0

if __name__ == '__main__':
    exit(main())
