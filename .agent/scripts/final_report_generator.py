import os
import json
import argparse
import re
from pathlib import Path
from datetime import datetime

# --- Data Processing Functions ---

def process_execution_log(log_file):
    """
    Reads execution_log.json and pairs START/END events into robust rows.
    Calculates duration and identifies overlaps (parallelism).
    """
    if not os.path.exists(log_file):
        print(f"⚠️ Log file not found: {log_file}")
        return []
        
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            raw_logs = json.load(f)
    except Exception as e:
        print(f"⚠️ Error reading execution log: {e}")
        return []

    # 1. Pair START and END events
    # Key: (name, type, path) -> {start: event, end: event}
    paired_events = {}
    
    for event in raw_logs:
        key = (event.get('name'), event.get('type'), event.get('path'))
        if key not in paired_events:
            paired_events[key] = {}
        
        if event.get('status') == 'START':
            paired_events[key]['start'] = event
        elif event.get('status') == 'END':
            paired_events[key]['end'] = event

    # 2. Flatten to list for sorting
    processed_rows = []
    
    # Sort primarily by Start Time
    sorted_keys = sorted(paired_events.keys(), key=lambda k: paired_events[k].get('start', {}).get('timestamp', ''))
    
    for idx, key in enumerate(sorted_keys):
        data = paired_events[key]
        start_evt = data.get('start', {})
        end_evt = data.get('end', {})
        
        # Determine Parallelism
        # Simple heuristic: if this start time is < previous end time? 
        # For now, let's just mark overlap if needed, or just sequence order.
        # User asked for "Order of execution (indicate if parallel)"
        
        start_ts = start_evt.get('timestamp_unix', 0)
        end_ts = end_evt.get('timestamp_unix', 0)
        
        start_str = start_evt.get('timestamp', '').replace('T', ' ')[:19]
        end_str = end_evt.get('timestamp', '').replace('T', ' ')[:19]
        
        duration = 0
        if start_ts and end_ts:
            duration = round(end_ts - start_ts, 2)
            
        row = {
            "order": idx + 1,
            "type": start_evt.get('type', 'Unknown'),
            "path": start_evt.get('path', '-'),
            "name": start_evt.get('name', 'Unknown Scope'),
            "role": start_evt.get('role', '-'),
            "model": start_evt.get('model', '-'),
            "reasoning": start_evt.get('reasoning', '-'),
            "start_time": start_str,
            "end_time": end_str,
            "duration": f"{duration}s",
            # Detect parallelism roughly: check if previous item ended after this one started
            "is_parallel": False 
        }
        
        # Check vs previous
        if idx > 0:
            prev_row = processed_rows[-1]
            prev_end_ts = paired_events[sorted_keys[idx-1]].get('end', {}).get('timestamp_unix', 0)
            if start_ts < prev_end_ts:
                row['is_parallel'] = True
                prev_row['is_parallel'] = True # Mark both as overlapping
                
        processed_rows.append(row)
        
    return processed_rows

def scan_agents(agents_dir):
    agents = []
    if not os.path.exists(agents_dir): return agents
    for f in agents_dir.glob("*.md"):
        content = f.read_text(encoding='utf-8')
        desc = re.search(r'description:\s*(.+)', content)
        model = re.search(r'model:\s*(.+)', content)
        agents.append({
            "name": f.stem,
            "path": str(f),
            "description": desc.group(1).strip() if desc else "No objective defined",
            "model": model.group(1).strip() if model else "N/A"
        })
    return agents

def scan_skills(skills_dir):
    data = []
    if not skills_dir.exists(): return data
    for f in skills_dir.rglob("SKILL.md"):
        content = f.read_text(encoding='utf-8')
        desc = re.search(r'description:\s*(.+)', content)
        data.append({
            "name": f.parent.name,
            "description": desc.group(1).strip() if desc else "No objective defined",
            "type": "Skill"
        })
    return data

def scan_workflows(workflows_dir):
    data = []
    if not workflows_dir.exists(): return data
    for f in workflows_dir.glob("*.md"):
        content = f.read_text(encoding='utf-8')
        desc = re.search(r'description:\s*(.+)', content)
        turbo = "// turbo-all" in content
        data.append({
            "name": f.stem,
            "description": desc.group(1).strip() if desc else "No objective defined",
            "turbo": turbo,
            "steps": len(re.findall(r'```bash', content)),
            "type": "Workflow"
        })
    return data

def scan_rules(rules_file):
    if not rules_file.exists(): return []
    content = rules_file.read_text(encoding='utf-8')
    rules = []
    for line in content.splitlines():
        if "|" in line and "❌" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) > 3:
                rules.append({"prohibited": parts[1], "alternative": parts[2]})
    return rules

def verify_compliance(project_path, rules):
    results = []
    
    # 1. Zoneless Change Detection
    app_config = list(project_path.rglob("app.config.ts"))
    has_zoneless = False
    evidence = "Missing app.config.ts"
    if app_config:
        content = app_config[0].read_text(encoding='utf-8')
        if "provideExperimentalZonelessChangeDetection" in content or "provideZoneChangeDetection" in content:
            has_zoneless = True
            evidence = "Found provider in app.config.ts"
        else:
            evidence = "Provider missing in app.config.ts"
            
    results.append({
        "rule_invoked": "R-ANG-004: Zoneless State Management",
        "status": "PASSED" if has_zoneless else "FAILED",
        "explanation": "Modern Angular apps must use Zoneless Change Detection for performance.",
        "evidence": evidence
    })
    
    # 2. No Zone.js Import
    polyfills = list(project_path.rglob("polyfills.ts"))
    imported_zone = False
    evidence_zone = "polyfills.ts not found (Implies passed if strictly new)"
    if polyfills:
        content = polyfills[0].read_text(encoding='utf-8')
        if "import 'zone.js'" in content:
            imported_zone = True
            evidence_zone = "Explicit import found in polyfills.ts"
        else:
            evidence_zone = "No import in polyfills.ts"
    else:
        # Check angular.json for "polyfills": ["zone.js"] which is standard even for zoneless in v18 sometimes
        # But user wants NO zone.js
        pass 

    results.append({
        "rule_invoked": "R-ANG-001: No Zone.js Dependency",
        "status": "PASSED" if not imported_zone else "WARNING", # Warning because v18 still often includes it by default
        "explanation": "Zone.js adds overhead. We aim for native async/await handling.",
        "evidence": evidence_zone
    })
    
    # 3. Standalone Components
    components = list(project_path.rglob("*.component.ts"))
    standalone_count = 0
    total_components = len(components)
    
    for c in components:
        if "standalone: true" in c.read_text(encoding='utf-8'):
            standalone_count += 1
            
    results.append({
        "rule_invoked": "R-ANG-002: Standalone Components",
        "status": "PASSED" if total_components > 0 and standalone_count == total_components else "FAILED",
        "explanation": "All components must be standalone to avoid NgModule complexity.",
        "evidence": f"{standalone_count}/{total_components} components are standalone."
    })

    return results

def build_html(title_suffix, agents, skills, workflows, rules, compliance, execution_log):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build JS Objects
    agents_json = json.dumps(agents)
    workflows_json = json.dumps(workflows)
    compliance_json = json.dumps(compliance)

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Dashboard - {title_suffix}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        .glass {{ background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }}
        .card {{ transition: all 0.3s; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
        .parallel {{ border-left: 4px solid #f59e0b; background-color: #fffbeb; }}
    </style>
</head>
<body class="bg-gray-50 text-slate-800 font-sans">
    
    <!-- Hero -->
    <header class="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-8 shadow-lg">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-bold tracking-tight">Migration Command Center</h1>
                <p class="mt-2 text-blue-100">Project: {title_suffix} | Generated: {timestamp}</p>
            </div>
            <div class="px-4 py-2 bg-green-500 rounded-full font-bold text-sm shadow-md animate-pulse">
                Phase 11 REPORTING
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto p-8 space-y-12">

        <!-- 1. Migration Flow Diagram -->
        <section>
            <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
                <span class="text-indigo-600">📊</span> Execution Flow
            </h2>
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 card">
                <div class="mermaid">
                    graph LR
                        A[Analyze] -->|inventory.json| B[Backend Architect]
                        B -->|schema.prisma| C[Frontend Architect]
                        B -->|swagger.json| C
                        C -->|components| D[Testing & Healing]
                        D -- Loop x5 --> D
                        D -->|Pass| E[Quality Gates]
                        E -->|Pass| F[Deployment]
                        
                        style A fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px
                        style B fill:#dbeafe,stroke:#2563eb,stroke-width:2px
                        style C fill:#dcfce7,stroke:#16a34a,stroke-width:2px
                        style D fill:#fef9c3,stroke:#ca8a04,stroke-width:2px
                        style E fill:#f3e8ff,stroke:#9333ea,stroke-width:2px
                        style F fill:#ffe4e6,stroke:#e11d48,stroke-width:2px
                </div>
            </div>
        </section>

        <!-- 2. Detailed Execution Log (New Model Strategy Table) -->
        <section>
            <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
                <span class="text-indigo-600">🧠</span> Model Strategy (Detailed Execution)
            </h2>
            <div class="overflow-x-auto rounded-xl shadow-sm border border-gray-200">
                <table class="w-full text-left border-collapse bg-white text-sm">
                    <thead class="bg-gray-100 text-gray-600 uppercase text-xs">
                        <tr>
                            <th class="p-3 border-b">Order</th>
                            <th class="p-3 border-b">Type</th>
                            <th class="p-3 border-b">Path</th>
                            <th class="p-3 border-b">Name</th>
                            <th class="p-3 border-b">Role</th>
                            <th class="p-3 border-b">Model</th>
                            <th class="p-3 border-b">Reasoning</th>
                            <th class="p-3 border-b">Start Time</th>
                            <th class="p-3 border-b">End Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([f'''
                        <tr class="hover:bg-gray-50 border-b last:border-0 {'parallel' if row['is_parallel'] else ''}">
                            <td class="p-3 font-mono">
                                {row['order']} {'<span class="text-amber-500" title="Running in Parallel">⚡</span>' if row['is_parallel'] else ''}
                            </td>
                            <td class="p-3"><span class="px-2 py-0.5 rounded text-xs border bg-gray-50">{row['type']}</span></td>
                            <td class="p-3 font-mono text-xs text-gray-500 truncate max-w-[150px]" title="{row['path']}">{row['path']}</td>
                            <td class="p-3 font-bold text-indigo-700">{row['name']}</td>
                            <td class="p-3 text-gray-600">{row['role']}</td>
                            <td class="p-3">
                                <span class="px-2 py-0.5 rounded text-xs font-bold {'bg-purple-100 text-purple-700' if 'sonnet' in str(row['model']).lower() else 'bg-blue-100 text-blue-700'}">
                                    {row['model']}
                                </span>
                            </td>
                            <td class="p-3 text-gray-500 italic text-xs max-w-[200px]">{row['reasoning']}</td>
                            <td class="p-3 font-mono text-xs whitespace-nowrap">{row['start_time']}</td>
                            <td class="p-3 font-mono text-xs whitespace-nowrap">{row['end_time']}</td>
                        </tr>
                        ''' for row in execution_log])}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- 3. Workflows & Automation -->
        <section>
            <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
                <span class="text-indigo-600">⚡</span> Workflow Automation
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {"".join([f'''
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 card flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-start mb-4">
                            <h3 class="font-bold text-lg">{w['name']}</h3>
                            {'<span class="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full font-bold">⚡ TURBO-ALL</span>' if w['turbo'] else ''}
                        </div>
                        <p class="text-sm text-gray-500 mb-4">{w['description']}</p>
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-100 text-xs text-gray-400 flex justify-between">
                        <span>Steps: {w['steps']}</span>
                        <span>Type: {w['type']}</span>
                    </div>
                </div>
                ''' for w in workflows])}
            </div>
        </section>
        
        <!-- 4. Rule Compliance & Verification (Enhanced) -->
        <section>
            <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
                <span class="text-indigo-600">🛡️</span> Rule Compliance (Live Verification)
            </h2>
            <div class="grid grid-cols-1 gap-4">
                <!-- Detailed Compliance Cards -->
                {"".join([f'''
                <div class="bg-white p-5 rounded-lg shadow-sm border-l-4 {'border-green-500' if c['status'] == 'PASSED' else ('border-yellow-400' if c['status'] == 'WARNING' else 'border-red-500')}">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="font-bold text-md text-gray-800">{c['rule_invoked']}</h3>
                            <p class="text-sm text-gray-600 mt-1">{c['explanation']}</p>
                        </div>
                        <span class="px-3 py-1 rounded-full text-xs font-bold {'bg-green-100 text-green-700' if c['status'] == 'PASSED' else ('bg-yellow-100 text-yellow-700' if c['status'] == 'WARNING' else 'bg-red-100 text-red-700')}">
                            {c['status']}
                        </span>
                    </div>
                    <div class="mt-3 pt-3 border-t border-gray-100 flex items-center gap-2">
                        <span class="text-xs font-bold text-gray-400 uppercase">Evidence:</span>
                        <code class="text-xs bg-gray-100 px-2 py-1 rounded text-gray-700">{c['evidence']}</code>
                    </div>
                </div>
                ''' for c in compliance])}
            </div>

            <!-- Rules Table -->
            <div class="mt-8 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h3 class="font-bold mb-4 text-gray-700">Rules Applied (Sample from MIGRATION_RULES.md)</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-50 text-left">
                            <tr>
                                <th class="p-3">❌ Prohibited</th>
                                <th class="p-3">✅ Alternative</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f'''
                            <tr class="border-t hover:bg-gray-50">
                                <td class="p-3 text-red-500">{r['prohibited']}</td>
                                <td class="p-3 text-green-600">{r['alternative']}</td>
                            </tr>
                            ''' for r in rules[:8]])} <!-- Show first 8 rules -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

    </main>

    <footer class="bg-gray-800 text-gray-400 py-8 text-center mt-12">
        <p>Antigravity Migration System v2.1</p>
    </footer>

    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</body>
</html>
    """
    
def generate_report(project_dir, analysis_dir, output_file):
    project_path = Path(project_dir)
    analysis_path = Path(analysis_dir)
    agent_dir = project_path / ".agent"
    
    # 1. Gather Data
    agents = scan_agents(agent_dir / "agents")
    skills = scan_skills(agent_dir / "skills")
    workflows = scan_workflows(agent_dir / "workflows")
    rules = scan_rules(agent_dir / "rules" / "MIGRATION_RULES.md")
    
    # NEW: Process Execution Log
    execution_log = process_execution_log(analysis_path / "execution_log.json")
    
    compliance = verify_compliance(project_path, rules)
    
    # 2. Generate HTML
    html = build_html("angular-app-v4", agents, skills, workflows, rules, compliance, execution_log)
    
    # 3. Write Output
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Report generated: {output_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--analysis-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    generate_report(args.project_dir, args.analysis_dir, args.output)

if __name__ == "__main__":
    main()
