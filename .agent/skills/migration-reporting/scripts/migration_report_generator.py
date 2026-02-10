#!/usr/bin/env python3
"""
Migration Report Generator v1.0

Scans migration artifacts across all phases and produces an interactive
HTML dashboard in the project's results/ directory.

Usage:
    python migration_report_generator.py --project-dir <path> --analysis-dir <path> --output <path>/results/MIGRATION_REPORT.html

No external dependencies — stdlib only.
"""

import argparse
import json
import os
import glob
import re
from datetime import datetime
from pathlib import Path


# ── Scanners ────────────────────────────────────────────────────────────────

def scan_analysis(analysis_dir: str) -> dict:
    """Scan analysis/ directory for JSON artifacts and MD documents."""
    result = {"json_files": [], "md_files": [], "inventory": {}, "risks": []}
    if not os.path.isdir(analysis_dir):
        return result

    for f in sorted(glob.glob(os.path.join(analysis_dir, "*.json"))):
        name = os.path.basename(f)
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                data = json.load(fh)
            result["json_files"].append({"name": name, "keys": list(data.keys()) if isinstance(data, dict) else f"array[{len(data)}]"})
            if "inventory" in name.lower():
                result["inventory"] = data
        except (json.JSONDecodeError, IOError):
            result["json_files"].append({"name": name, "keys": "parse_error"})

    for f in sorted(glob.glob(os.path.join(analysis_dir, "*.md"))):
        name = os.path.basename(f)
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            line_count = content.count("\n") + 1
            result["md_files"].append({"name": name, "lines": line_count})
        except IOError:
            result["md_files"].append({"name": name, "lines": 0})

    return result


def scan_prisma(project_dir: str) -> dict:
    """Scan for Prisma schema and extract model names."""
    result = {"found": False, "models": [], "path": ""}
    for candidate in [
        os.path.join(project_dir, "prisma", "schema.prisma"),
        os.path.join(project_dir, "backend", "prisma", "schema.prisma"),
    ]:
        if os.path.isfile(candidate):
            result["found"] = True
            result["path"] = candidate
            try:
                with open(candidate, "r", encoding="utf-8") as fh:
                    for line in fh:
                        m = re.match(r"^model\s+(\w+)\s*\{", line)
                        if m:
                            result["models"].append(m.group(1))
            except IOError:
                pass
            break
    return result


def scan_backend(project_dir: str) -> dict:
    """Scan backend services, controllers, and routes."""
    result = {"services": [], "controllers": [], "routes": [], "swagger_found": False}
    for subdir in ["backend/src", "backend", "src", "apps/backend/src"]:
        base = os.path.join(project_dir, subdir)
        if not os.path.isdir(base):
            continue
        for kind, folder in [("services", "services"), ("controllers", "controllers"), ("routes", "routes")]:
            d = os.path.join(base, folder)
            if os.path.isdir(d):
                result[kind] = [os.path.basename(f) for f in sorted(glob.glob(os.path.join(d, "*.ts")))]
        break

    for sw in ["swagger.json", "backend/swagger.json", "src/swagger.json"]:
        if os.path.isfile(os.path.join(project_dir, sw)):
            result["swagger_found"] = True
            break

    return result


def scan_frontend(project_dir: str) -> dict:
    """Scan Angular components and services."""
    result = {"components": [], "services": [], "app_found": False}
    for subdir in ["src/app", "apps/frontend/src/app", "frontend/src/app"]:
        base = os.path.join(project_dir, subdir)
        if not os.path.isdir(base):
            continue
        result["app_found"] = True
        for root, dirs, files in os.walk(base):
            for f in files:
                if f.endswith(".component.ts"):
                    rel = os.path.relpath(os.path.join(root, f), base)
                    result["components"].append(rel)
                elif f.endswith(".service.ts"):
                    rel = os.path.relpath(os.path.join(root, f), base)
                    result["services"].append(rel)
        break
    result["components"].sort()
    result["services"].sort()
    return result


def scan_tests(project_dir: str, analysis_dir: str) -> dict:
    """Scan for test output and coverage reports."""
    result = {"unit_output": False, "e2e_output": False, "coverage": {}}
    for txt in ["unit-output.txt", "frontend-output.txt"]:
        if os.path.isfile(os.path.join(analysis_dir, txt)):
            result["unit_output"] = True
            break

    if os.path.isfile(os.path.join(analysis_dir, "e2e-output.txt")):
        result["e2e_output"] = True

    for cov in glob.glob(os.path.join(analysis_dir, "**/coverage-summary.json"), recursive=True):
        kind = "backend" if "backend" in cov else "frontend"
        try:
            with open(cov, "r") as fh:
                data = json.load(fh)
            total = data.get("total", {})
            result["coverage"][kind] = {
                "lines": total.get("lines", {}).get("pct", 0),
                "branches": total.get("branches", {}).get("pct", 0),
                "functions": total.get("functions", {}).get("pct", 0),
            }
        except (json.JSONDecodeError, IOError):
            pass

    return result


# ── HTML Generation ─────────────────────────────────────────────────────────

def phase_status(exists: bool, count: int = 0) -> str:
    if not exists:
        return '<span class="status status-missing">❌ Not Found</span>'
    if count == 0:
        return '<span class="status status-warn">⚠️ Empty</span>'
    return '<span class="status status-ok">✅ Complete</span>'


def progress_bar(pct: float) -> str:
    color = "#22c55e" if pct >= 80 else "#eab308" if pct >= 50 else "#ef4444"
    return f'<div class="progress-bar"><div class="progress-fill" style="width:{pct:.0f}%;background:{color}"></div><span class="progress-text">{pct:.0f}%</span></div>'


def generate_html(analysis: dict, prisma: dict, backend: dict, frontend: dict, tests: dict, project_dir: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_name = os.path.basename(os.path.abspath(project_dir))

    # Phase completion calculation
    phases = []
    p1 = len(analysis["json_files"]) + len(analysis["md_files"])
    phases.append(("1. Analysis", p1 > 0, p1))
    phases.append(("2. Database", prisma["found"], len(prisma["models"])))
    p3 = len(backend["services"]) + len(backend["controllers"]) + len(backend["routes"])
    phases.append(("3. Backend", p3 > 0, p3))
    phases.append(("4. Frontend", frontend["app_found"], len(frontend["components"])))
    p5 = 1 if tests["unit_output"] or tests["e2e_output"] else 0
    phases.append(("5. Testing", p5 > 0, p5))

    completed = sum(1 for _, ok, _ in phases if ok)
    overall_pct = (completed / len(phases)) * 100

    # Build phase rows
    phase_rows = ""
    for name, ok, count in phases:
        phase_rows += f"""
        <tr>
            <td><strong>{name}</strong></td>
            <td>{phase_status(ok, count)}</td>
            <td>{count} artifact{"s" if count != 1 else ""}</td>
        </tr>"""

    # Analysis artifacts table
    analysis_rows = ""
    for jf in analysis["json_files"]:
        keys_str = ", ".join(jf["keys"]) if isinstance(jf["keys"], list) else str(jf["keys"])
        analysis_rows += f'<tr><td>📊 {jf["name"]}</td><td>JSON</td><td>{keys_str}</td></tr>'
    for mf in analysis["md_files"]:
        analysis_rows += f'<tr><td>📝 {mf["name"]}</td><td>Markdown</td><td>{mf["lines"]} lines</td></tr>'

    # Prisma models table
    prisma_rows = ""
    for model in prisma["models"]:
        prisma_rows += f'<tr><td>🗃️ {model}</td><td>Prisma Model</td><td>schema.prisma</td></tr>'
    if not prisma["models"]:
        prisma_rows = '<tr><td colspan="3" class="empty">No Prisma models found</td></tr>'

    # Backend artifacts table
    backend_rows = ""
    for s in backend["services"]:
        backend_rows += f'<tr><td>⚙️ {s}</td><td>Service</td><td>CRUD operations</td></tr>'
    for c in backend["controllers"]:
        backend_rows += f'<tr><td>🎮 {c}</td><td>Controller</td><td>HTTP handlers</td></tr>'
    for r in backend["routes"]:
        backend_rows += f'<tr><td>🔀 {r}</td><td>Route</td><td>Express route</td></tr>'
    if not backend_rows:
        backend_rows = '<tr><td colspan="3" class="empty">No backend artifacts found</td></tr>'

    # Frontend artifacts table
    frontend_rows = ""
    for comp in frontend["components"]:
        frontend_rows += f'<tr><td>🧩 {comp}</td><td>Component</td><td>Angular standalone</td></tr>'
    for svc in frontend["services"]:
        frontend_rows += f'<tr><td>📡 {svc}</td><td>Service</td><td>HttpClient</td></tr>'
    if not frontend_rows:
        frontend_rows = '<tr><td colspan="3" class="empty">No frontend artifacts found</td></tr>'

    # Test coverage section
    coverage_rows = ""
    for kind, metrics in tests["coverage"].items():
        coverage_rows += f"""
        <div class="coverage-card">
            <h4>{kind.title()} Coverage</h4>
            <div class="metric">Lines {progress_bar(metrics["lines"])}</div>
            <div class="metric">Branches {progress_bar(metrics["branches"])}</div>
            <div class="metric">Functions {progress_bar(metrics["functions"])}</div>
        </div>"""
    if not coverage_rows:
        has_any = "Unit output found" if tests["unit_output"] else ""
        has_e2e = "E2E output found" if tests["e2e_output"] else ""
        test_status = " | ".join(filter(None, [has_any, has_e2e])) or "No test output found"
        coverage_rows = f'<div class="coverage-card"><p class="empty">{test_status}</p></div>'

    # Statistics
    total_vb6 = 0
    if isinstance(analysis.get("inventory"), dict):
        total_vb6 = sum(len(v) if isinstance(v, list) else 0 for v in analysis["inventory"].values())

    stats = {
        "VB6 Artifacts Analyzed": total_vb6 or len(analysis["json_files"]) + len(analysis["md_files"]),
        "Prisma Models": len(prisma["models"]),
        "Backend Services": len(backend["services"]),
        "Backend Controllers": len(backend["controllers"]),
        "Backend Routes": len(backend["routes"]),
        "Angular Components": len(frontend["components"]),
        "Angular Services": len(frontend["services"]),
        "Swagger Found": "✅" if backend["swagger_found"] else "❌",
    }
    stats_rows = ""
    for label, value in stats.items():
        stats_rows += f'<tr><td>{label}</td><td><strong>{value}</strong></td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Migration Report — {project_name}</title>
<style>
:root {{
    --bg: #0f172a;
    --surface: #1e293b;
    --card: #334155;
    --border: #475569;
    --text: #e2e8f0;
    --text-muted: #94a3b8;
    --accent: #3b82f6;
    --accent-glow: rgba(59,130,246,0.15);
    --ok: #22c55e;
    --warn: #eab308;
    --err: #ef4444;
    --radius: 12px;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}}
.layout {{
    display: flex;
    min-height: 100vh;
}}
/* Sidebar */
.sidebar {{
    width: 260px;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 24px 16px;
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    overflow-y: auto;
}}
.sidebar h2 {{
    font-size: 14px;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 1.5px;
    margin-bottom: 16px;
}}
.sidebar a {{
    display: block;
    padding: 10px 14px;
    color: var(--text);
    text-decoration: none;
    border-radius: 8px;
    font-size: 14px;
    margin-bottom: 4px;
    transition: all 0.2s;
}}
.sidebar a:hover {{
    background: var(--accent-glow);
    color: var(--accent);
}}
.sidebar .logo {{
    font-size: 24px;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 8px;
    display: block;
}}
.sidebar .project {{
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 24px;
}}
/* Main */
.main {{
    margin-left: 260px;
    padding: 40px;
    flex: 1;
    max-width: 1100px;
}}
h1 {{
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
}}
.subtitle {{
    color: var(--text-muted);
    font-size: 14px;
    margin-bottom: 32px;
}}
h2 {{
    font-size: 20px;
    font-weight: 600;
    margin-top: 40px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}}
/* Cards */
.card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 20px;
}}
.card-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}}
.stat-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    text-align: center;
}}
.stat-card .number {{
    font-size: 32px;
    font-weight: 700;
    color: var(--accent);
}}
.stat-card .label {{
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 4px;
}}
/* Tables */
table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}}
th {{
    text-align: left;
    padding: 12px 16px;
    background: var(--card);
    color: var(--text-muted);
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
td {{
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
}}
tr:hover td {{
    background: var(--accent-glow);
}}
.empty {{
    color: var(--text-muted);
    font-style: italic;
    text-align: center;
    padding: 24px;
}}
/* Status badges */
.status {{
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    white-space: nowrap;
}}
.status-ok {{ background: rgba(34,197,94,0.15); color: var(--ok); }}
.status-warn {{ background: rgba(234,179,8,0.15); color: var(--warn); }}
.status-missing {{ background: rgba(239,68,68,0.15); color: var(--err); }}
/* Progress bars */
.progress-bar {{
    height: 22px;
    background: var(--card);
    border-radius: 11px;
    overflow: hidden;
    position: relative;
    min-width: 120px;
    display: inline-block;
    width: 100%;
}}
.progress-fill {{
    height: 100%;
    border-radius: 11px;
    transition: width 0.4s ease;
}}
.progress-text {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 11px;
    font-weight: 600;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}}
/* Coverage */
.coverage-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
}}
.coverage-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
}}
.coverage-card h4 {{
    margin-bottom: 12px;
    font-size: 16px;
}}
.metric {{
    margin-bottom: 10px;
    font-size: 13px;
    color: var(--text-muted);
}}
/* Overall progress */
.overall {{
    background: linear-gradient(135deg, var(--surface), var(--card));
    border: 1px solid var(--accent);
    border-radius: var(--radius);
    padding: 28px;
    margin-bottom: 28px;
    text-align: center;
}}
.overall h3 {{
    font-size: 16px;
    color: var(--text-muted);
    margin-bottom: 12px;
}}
.overall .big {{
    font-size: 48px;
    font-weight: 700;
    color: var(--accent);
}}
footer {{
    margin-top: 48px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
    font-size: 12px;
    color: var(--text-muted);
    text-align: center;
}}
</style>
</head>
<body>
<div class="layout">
    <nav class="sidebar">
        <span class="logo">📊 Migration Report</span>
        <span class="project">{project_name}</span>
        <h2>Navigation</h2>
        <a href="#overview">🏠 Overview</a>
        <a href="#phases">📋 Phase Progress</a>
        <a href="#stats">📈 Statistics</a>
        <a href="#analysis">🔍 Analysis</a>
        <a href="#database">🗃️ Database</a>
        <a href="#backend">⚙️ Backend API</a>
        <a href="#frontend">🧩 Frontend</a>
        <a href="#testing">🧪 Testing</a>
    </nav>
    <main class="main">
        <h1 id="overview">Migration Report</h1>
        <p class="subtitle">Generated on {now} · Project: {project_name}</p>

        <div class="overall">
            <h3>Overall Migration Progress</h3>
            <div class="big">{overall_pct:.0f}%</div>
            <p>{completed} of {len(phases)} phases completed</p>
            {progress_bar(overall_pct)}
        </div>

        <h2 id="phases">📋 Phase Progress</h2>
        <div class="card">
            <table>
                <thead><tr><th>Phase</th><th>Status</th><th>Artifacts</th></tr></thead>
                <tbody>{phase_rows}</tbody>
            </table>
        </div>

        <h2 id="stats">📈 Statistics</h2>
        <div class="card-grid">
            <div class="stat-card">
                <div class="number">{len(prisma["models"])}</div>
                <div class="label">Prisma Models</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(backend["services"])}</div>
                <div class="label">Backend Services</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(frontend["components"])}</div>
                <div class="label">Angular Components</div>
            </div>
            <div class="stat-card">
                <div class="number">{completed}/{len(phases)}</div>
                <div class="label">Phases Complete</div>
            </div>
        </div>
        <div class="card">
            <table>
                <thead><tr><th>Metric</th><th>Value</th></tr></thead>
                <tbody>{stats_rows}</tbody>
            </table>
        </div>

        <h2 id="analysis">🔍 Phase 1: Analysis</h2>
        <div class="card">
            <table>
                <thead><tr><th>File</th><th>Type</th><th>Details</th></tr></thead>
                <tbody>{analysis_rows if analysis_rows else '<tr><td colspan="3" class="empty">No analysis artifacts found</td></tr>'}</tbody>
            </table>
        </div>

        <h2 id="database">🗃️ Phase 2: Database</h2>
        <div class="card">
            <table>
                <thead><tr><th>Model</th><th>Type</th><th>Source</th></tr></thead>
                <tbody>{prisma_rows}</tbody>
            </table>
        </div>

        <h2 id="backend">⚙️ Phase 3: Backend API</h2>
        <div class="card">
            <table>
                <thead><tr><th>File</th><th>Type</th><th>Purpose</th></tr></thead>
                <tbody>{backend_rows}</tbody>
            </table>
        </div>

        <h2 id="frontend">🧩 Phase 4: Frontend</h2>
        <div class="card">
            <table>
                <thead><tr><th>File</th><th>Type</th><th>Framework</th></tr></thead>
                <tbody>{frontend_rows}</tbody>
            </table>
        </div>

        <h2 id="testing">🧪 Phase 5: Testing</h2>
        <div class="coverage-grid">
            {coverage_rows}
        </div>

        <footer>
            Migration Report Generator v1.0 · Generated by migration-documenter agent · {now}
        </footer>
    </main>
</div>
</body>
</html>"""


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate interactive HTML migration report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --project-dir ./angular-app --analysis-dir ./analysis --output ./angular-app/results/MIGRATION_REPORT.html
  %(prog)s --project-dir . --analysis-dir ./analysis
        """,
    )
    parser.add_argument("--project-dir", required=True, help="Root of the migrated project")
    parser.add_argument("--analysis-dir", default="analysis", help="Path to analysis artifacts (default: analysis)")
    parser.add_argument("--output", default=None, help="Output HTML path (default: <project-dir>/results/MIGRATION_REPORT.html)")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    analysis_dir = os.path.abspath(args.analysis_dir)
    output_path = args.output or os.path.join(project_dir, "results", "MIGRATION_REPORT.html")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"📊 Migration Report Generator v1.0")
    print(f"   Project : {project_dir}")
    print(f"   Analysis: {analysis_dir}")
    print(f"   Output  : {output_path}")
    print()

    print("🔍 Scanning analysis artifacts...")
    analysis = scan_analysis(analysis_dir)
    print(f"   Found {len(analysis['json_files'])} JSON + {len(analysis['md_files'])} MD files")

    print("🗃️  Scanning Prisma schema...")
    prisma = scan_prisma(project_dir)
    print(f"   Found {len(prisma['models'])} models" if prisma["found"] else "   No schema.prisma found")

    print("⚙️  Scanning backend artifacts...")
    backend = scan_backend(project_dir)
    print(f"   Found {len(backend['services'])} services, {len(backend['controllers'])} controllers, {len(backend['routes'])} routes")

    print("🧩 Scanning frontend artifacts...")
    frontend = scan_frontend(project_dir)
    print(f"   Found {len(frontend['components'])} components, {len(frontend['services'])} services")

    print("🧪 Scanning test results...")
    tests = scan_tests(project_dir, analysis_dir)
    print(f"   Unit output: {'✅' if tests['unit_output'] else '❌'} | E2E output: {'✅' if tests['e2e_output'] else '❌'}")

    print()
    print("📄 Generating HTML report...")
    html = generate_html(analysis, prisma, backend, frontend, tests, project_dir)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"✅ Report generated: {output_path}")
    print(f"   Open in browser: file://{output_path}")


if __name__ == "__main__":
    main()
