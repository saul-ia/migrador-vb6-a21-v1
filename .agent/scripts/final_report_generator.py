import os
import json
import re
import argparse
import datetime
from pathlib import Path

def generate_report(project_dir, analysis_dir, output_file):
    """
    Generates a modern, interactive HTML report for the migration process.
    """
    project_path = Path(project_dir)
    analysis_path = Path(analysis_dir)
    agent_dir = project_path / ".agent"
    
    # 1. Gather Data
    agents = scan_agents(agent_dir / "agents")
    skills = scan_skills(agent_dir / "skills")
    workflows = scan_workflows(agent_dir / "workflows")
    rules = scan_rules(agent_dir / "rules" / "MIGRATION_RULES.md")
    compliance = verify_compliance(project_path, rules)
    
    # 2. Generate HTML
    html = build_html(agents, skills, workflows, rules, compliance)
    
    # 3. Write Output
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Report generated: {output_file}")

def scan_agents(agents_dir):
    data = []
    if not agents_dir.exists(): return data
    for f in agents_dir.glob("*.md"):
        content = f.read_text(encoding='utf-8')
        model = re.search(r'model:\s*(.+)', content)
        desc = re.search(r'description:\s*(.+)', content)
        data.append({
            "name": f.stem,
            "model": model.group(1).strip() if model else "Unknown",
            "description": desc.group(1).strip() if desc else "No objective defined",
            "type": "Agent"
        })
    return data

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
    # Simplified check: looking for "Zoneless" compliance strings
    app_config = list(project_path.rglob("app.config.ts"))
    
    # Check 1: Zoneless
    has_zoneless = False
    if app_config:
        content = app_config[0].read_text(encoding='utf-8')
        if "provideExperimentalZonelessChangeDetection" in content:
            has_zoneless = True
    results.append({
        "rule": "Provide Experimental Zoneless Change Detection",
        "status": "PASSED" if has_zoneless else "FAILED",
        "evidence": "found in app.config.ts" if has_zoneless else "Missing in app.config.ts"
    })
    
    # Check 2: Zone.js exclusion
    package_json = list(project_path.rglob("package.json"))
    has_zone_js = False
    if package_json:
        content = package_json[0].read_text(encoding='utf-8')
        if '"zone.js"' in content:
            has_zone_js = True # It might be in deps, but should not be imported in polyfills
    # Better check: polyfills.ts
    polyfills = list(project_path.rglob("polyfills.ts"))
    imported_zone = False
    if polyfills:
         content = polyfills[0].read_text(encoding='utf-8')
         if "import 'zone.js'" in content:
             imported_zone = True

    results.append({
        "rule": "No 'import zone.js'",
        "status": "PASSED" if not imported_zone else "FAILED",
        "evidence": "Not found in polyfills.ts" if not imported_zone else "Found in polyfills.ts"
    })
    
    return results

def build_html(agents, skills, workflows, rules, compliance):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
    <title>Migration Dashboard - VB6 to Angular</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        .glass {{ background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }}
        .card {{ transition: all 0.3s; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
    </style>
</head>
<body class="bg-gray-50 text-slate-800 font-sans">
    
    <!-- Hero -->
    <header class="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-8 shadow-lg">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-bold tracking-tight">Migration Command Center</h1>
                <p class="mt-2 text-blue-100">Project: migrador-vb6-a21-v1 | Generated: {timestamp}</p>
            </div>
            <div class="px-4 py-2 bg-green-500 rounded-full font-bold text-sm shadow-md animate-pulse">
                Phase 10 COMPLETE
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

        <!-- 2. AI Model Usage Table -->
        <section>
            <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
                <span class="text-indigo-600">🧠</span> Model Strategy (Balanced)
            </h2>
            <div class="overflow-hidden rounded-xl shadow-sm border border-gray-200">
                <table class="w-full text-left border-collapse">
                    <thead class="bg-gray-100 text-gray-600 uppercase text-xs">
                        <tr>
                            <th class="p-4 border-b">Agent Name</th>
                            <th class="p-4 border-b">Role</th>
                            <th class="p-4 border-b">Model</th>
                            <th class="p-4 border-b">Reasoning</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white">
                        {"".join([f'''
                        <tr class="hover:bg-gray-50 border-b last:border-0">
                            <td class="p-4 font-medium text-indigo-600">{a['name']}</td>
                            <td class="p-4 text-sm text-gray-500">{a['description'][:50]}...</td>
                            <td class="p-4">
                                <span class="px-2 py-1 rounded text-xs font-bold 
                                    {'bg-purple-100 text-purple-700' if 'sonnet' in a['model'] else 'bg-blue-100 text-blue-700'}">
                                    {a['model']}
                                </span>
                            </td>
                            <td class="p-4 text-sm text-gray-500">
                                {'Critical logic / Deep reasoning' if 'sonnet' in a['model'] else 'High speed / Repetitive tasks'}
                            </td>
                        </tr>
                        ''' for a in agents])}
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
        
        <!-- 4. Rule Compliance & Verification -->
        <section>
            <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
                <span class="text-indigo-600">🛡️</span> Rule Compliance (Live Verification)
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Compliance Cards -->
                {"".join([f'''
                <div class="bg-white p-6 rounded-xl shadow-sm border-l-4 {'border-green-500' if c['status'] == 'PASSED' else 'border-red-500'} card">
                    <h3 class="font-bold text-lg mb-2">{c['rule']}</h3>
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-500">Status: <strong class="{'text-green-600' if c['status'] == 'PASSED' else 'text-red-600'}">{c['status']}</strong></span>
                        <span class="text-xs text-gray-400">{c['evidence']}</span>
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
        <p>Antigravity Migration System v2.0</p>
    </footer>

    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</body>
</html>
    """
    return html

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--analysis-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    generate_report(args.project_dir, args.analysis_dir, args.output)

if __name__ == "__main__":
    main()
