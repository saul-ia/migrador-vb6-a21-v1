#!/usr/bin/env python3
"""
HTML Report Generator for VB6 Analysis
======================================
Generates modern, interactive HTML reports from VB6 scanner output.
Features Mermaid.js diagrams, dark mode, and responsive design.
"""

import json
import argparse
import os
from datetime import datetime
from pathlib import Path


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 VB6 Audit Report - {project_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        :root {{
            --bg-primary: #0f0f23;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --text-primary: #e8e8e8;
            --text-secondary: #a0a0a0;
            --accent: #00d4ff;
            --accent-secondary: #7b2cbf;
            --success: #00ff88;
            --warning: #ffcc00;
            --danger: #ff4444;
            --border: rgba(255,255,255,0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, var(--accent), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .header .meta {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        /* Cards */
        .card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,212,255,0.1);
        }}
        
        .card h2 {{
            color: var(--accent);
            margin-bottom: 1rem;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .card h3 {{
            color: var(--text-primary);
            margin: 1rem 0 0.5rem;
            font-size: 1.1rem;
        }}
        
        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid var(--border);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(90deg, var(--accent), var(--success));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background: var(--bg-secondary);
            color: var(--accent);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
        }}
        
        tr:hover {{
            background: rgba(0,212,255,0.05);
        }}
        
        /* Badges */
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge-high {{ background: var(--danger); color: white; }}
        .badge-medium {{ background: var(--warning); color: black; }}
        .badge-low {{ background: var(--success); color: black; }}
        .badge-create {{ background: #22c55e; color: white; }}
        .badge-read {{ background: #3b82f6; color: white; }}
        .badge-update {{ background: #f59e0b; color: black; }}
        .badge-delete {{ background: #ef4444; color: white; }}
        
        /* File Tree */
        .file-tree {{
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9rem;
        }}
        
        .file-tree details {{
            margin-left: 1.5rem;
        }}
        
        .file-tree summary {{
            cursor: pointer;
            padding: 0.25rem 0;
            list-style: none;
        }}
        
        .file-tree summary::-webkit-details-marker {{
            display: none;
        }}
        
        .file-tree summary::before {{
            content: '📁 ';
        }}
        
        .file-tree details[open] > summary::before {{
            content: '📂 ';
        }}
        
        .file-item {{
            margin-left: 1.5rem;
            padding: 0.25rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .file-size {{
            color: var(--text-secondary);
            font-size: 0.8rem;
        }}
        
        /* Mermaid */
        .mermaid {{
            background: var(--bg-secondary);
            padding: 2rem;
            border-radius: 8px;
            margin: 1rem 0;
            overflow-x: auto;
        }}
        
        /* Tabs */
        .tabs {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        
        .tab {{
            padding: 0.5rem 1rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            color: var(--text-secondary);
        }}
        
        .tab:hover, .tab.active {{
            background: var(--accent);
            color: var(--bg-primary);
            border-color: var(--accent);
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .container {{ padding: 1rem; }}
            .header h1 {{ font-size: 1.8rem; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        
        /* Collapsible */
        .collapsible {{
            cursor: pointer;
            user-select: none;
        }}
        
        .collapsible::after {{
            content: ' ▼';
            font-size: 0.8rem;
        }}
        
        .collapsed::after {{
            content: ' ▶';
        }}
        
        /* Risk Indicator */
        .risk-indicator {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 0.5rem;
        }}
        
        .risk-high {{ background: var(--danger); box-shadow: 0 0 8px var(--danger); }}
        .risk-medium {{ background: var(--warning); box-shadow: 0 0 8px var(--warning); }}
        .risk-low {{ background: var(--success); box-shadow: 0 0 8px var(--success); }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 VB6 Legacy Audit Report</h1>
            <div class="meta">
                <strong>Source:</strong> {source_directory}<br>
                <strong>Generated:</strong> {scan_date}<br>
                <strong>Scanner Version:</strong> {scanner_version}
            </div>
        </div>
        
        <!-- Summary Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_files}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{forms_count}</div>
                <div class="stat-label">Forms (.FRM)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{modules_count}</div>
                <div class="stat-label">Modules (.BAS)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{classes_count}</div>
                <div class="stat-label">Classes (.CLS)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_controls}</div>
                <div class="stat-label">UI Controls</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{risk_count}</div>
                <div class="stat-label">Migration Risks</div>
            </div>
        </div>
        
        <!-- Risks Section -->
        {risks_section}
        
        <!-- File Inventory -->
        <div class="card">
            <h2>📁 File Inventory</h2>
            {inventory_section}
        </div>
        
        <!-- Application Flow Diagram -->
        <div class="card">
            <h2>🔄 Application Flow Diagram</h2>
            <div class="mermaid">
{flow_diagram}
            </div>
        </div>
        
        <!-- CRUD Analysis -->
        {crud_section}
        
        <!-- Forms Detail -->
        <div class="card">
            <h2>🖼️ Forms Analysis</h2>
            {forms_section}
        </div>
        
        <!-- Modules Detail -->
        <div class="card">
            <h2>📄 Modules Analysis</h2>
            {modules_section}
        </div>
        
        <!-- Dependencies -->
        <div class="card">
            <h2>🔌 External Dependencies</h2>
            {dependencies_section}
        </div>
        
        <!-- Global Variables -->
        {globals_section}
        
        <!-- API Calls -->
        {api_section}
    </div>
    
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#00d4ff',
                primaryTextColor: '#fff',
                primaryBorderColor: '#00d4ff',
                lineColor: '#a0a0a0',
                secondaryColor: '#7b2cbf',
                tertiaryColor: '#1a1a2e'
            }}
        }});
        
        // Tab functionality
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.addEventListener('click', () => {{
                const tabGroup = tab.parentElement;
                const contentId = tab.dataset.tab;
                
                tabGroup.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                const container = tabGroup.nextElementSibling;
                container.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                container.querySelector(`#${{contentId}}`).classList.add('active');
            }});
        }});
    </script>
</body>
</html>
'''


def generate_risks_section(risks):
    """Generate the risks section HTML."""
    if not risks:
        return '<div class="card"><h2>✅ Risk Assessment</h2><p>No significant migration risks detected.</p></div>'
    
    rows = ""
    for risk in risks:
        badge_class = f"badge-{risk['level'].lower()}"
        indicator_class = f"risk-{risk['level'].lower()}"
        rows += f'''
        <tr>
            <td><span class="risk-indicator {indicator_class}"></span><span class="badge {badge_class}">{risk['level']}</span></td>
            <td>{risk['category']}</td>
            <td>{risk['description']}</td>
            <td>{risk['mitigation']}</td>
        </tr>'''
    
    return f'''
    <div class="card">
        <h2>⚠️ Risk Assessment</h2>
        <table>
            <thead>
                <tr><th>Level</th><th>Category</th><th>Description</th><th>Mitigation</th></tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>'''


def generate_inventory_section(inventory):
    """Generate file inventory as interactive tree."""
    html = '<div class="file-tree">'
    
    for category, info in inventory.items():
        if info['count'] == 0:
            continue
            
        icon = info.get('icon', '📁')
        html += f'''
        <details open>
            <summary><strong>{icon} {category.title()}</strong> ({info['count']} files) - {info['description']}</summary>
        '''
        
        for f in info['files'][:50]:  # Limit to prevent huge HTMLs
            size = f.get('size_bytes', 0)
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            html += f'''
            <div class="file-item">
                📄 {f['name']} <span class="file-size">({size_str})</span>
            </div>'''
        
        if info['count'] > 50:
            html += f'<div class="file-item">... and {info["count"] - 50} more files</div>'
        
        html += '</details>'
    
    html += '</div>'
    return html


def generate_flow_diagram(analysis):
    """Generate Mermaid flowchart from analysis."""
    forms = analysis.get('forms', [])
    modules = analysis.get('modules', [])
    
    if not forms and not modules:
        return 'graph LR\n    A[No forms or modules found]'
    
    lines = ['graph TB']
    lines.append('    subgraph Forms')
    
    for i, form in enumerate(forms[:15]):  # Limit nodes
        name = form['name'][:20]
        crud = form.get('crud_operations', [])
        crud_label = ' '.join(crud) if crud else ''
        lines.append(f'        F{i}["{name}<br/>{crud_label}"]')
    
    lines.append('    end')
    lines.append('    subgraph Modules')
    
    for i, module in enumerate(modules[:10]):
        name = module['name'][:20]
        func_count = len(module.get('functions', []))
        lines.append(f'        M{i}["{name}<br/>{func_count} funcs"]')
    
    lines.append('    end')
    
    # Add some sample connections
    if forms and modules:
        for i in range(min(3, len(forms))):
            for j in range(min(2, len(modules))):
                lines.append(f'    F{i} --> M{j}')
    
    return '\n'.join(lines)


def generate_crud_section(crud_operations):
    """Generate CRUD analysis table."""
    if not crud_operations:
        return ''
    
    rows = ""
    for op in crud_operations:
        badges = ""
        for crud in op.get('operations', []):
            badge_class = f"badge-{crud.lower()}"
            badges += f'<span class="badge {badge_class}">{crud}</span> '
        
        rows += f'''
        <tr>
            <td>{op['source']}</td>
            <td>{badges}</td>
        </tr>'''
    
    return f'''
    <div class="card">
        <h2>💾 CRUD Operations Detected</h2>
        <table>
            <thead><tr><th>Form/Module</th><th>Operations</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>'''


def generate_forms_section(forms):
    """Generate forms detail section."""
    if not forms:
        return '<p>No forms found.</p>'
    
    html = '<table><thead><tr><th>Name</th><th>Controls</th><th>Events</th><th>Functions</th></tr></thead><tbody>'
    
    for form in forms:
        controls = len(form.get('controls', []))
        events = len(form.get('events', []))
        functions = len(form.get('functions', []))
        html += f'''
        <tr>
            <td><strong>{form['name']}</strong></td>
            <td>{controls}</td>
            <td>{events}</td>
            <td>{functions}</td>
        </tr>'''
    
    html += '</tbody></table>'
    return html


def generate_modules_section(modules):
    """Generate modules detail section."""
    if not modules:
        return '<p>No modules found.</p>'
    
    html = '<table><thead><tr><th>Name</th><th>Functions</th><th>Global Vars</th><th>API Calls</th></tr></thead><tbody>'
    
    for module in modules:
        functions = len(module.get('functions', []))
        globals_count = len(module.get('global_variables', []))
        api_count = len(module.get('api_declarations', []))
        html += f'''
        <tr>
            <td><strong>{module['name']}</strong></td>
            <td>{functions}</td>
            <td>{globals_count}</td>
            <td>{api_count}</td>
        </tr>'''
    
    html += '</tbody></table>'
    return html


def generate_dependencies_section(inventory):
    """Generate dependencies section."""
    deps = inventory.get('dependencies', {})
    if not deps or deps.get('count', 0) == 0:
        return '<p>No external dependencies detected.</p>'
    
    html = '<table><thead><tr><th>File</th><th>Type</th></tr></thead><tbody>'
    
    for f in deps.get('files', []):
        html += f'''
        <tr>
            <td>{f['name']}</td>
            <td>{f['extension'].upper()}</td>
        </tr>'''
    
    html += '</tbody></table>'
    return html


def generate_globals_section(global_vars):
    """Generate global variables section."""
    if not global_vars:
        return ''
    
    rows = ""
    for v in global_vars:
        rows += f'''
        <tr>
            <td>{v['name']}</td>
            <td>{v['type']}</td>
            <td>{v['visibility']}</td>
            <td>{v['source']}</td>
        </tr>'''
    
    return f'''
    <div class="card">
        <h2>🌐 Global Variables</h2>
        <table>
            <thead><tr><th>Name</th><th>Type</th><th>Visibility</th><th>Source</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>'''


def generate_api_section(api_calls):
    """Generate API calls section."""
    if not api_calls:
        return ''
    
    rows = ""
    for api in api_calls:
        rows += f'''
        <tr>
            <td>{api['name']}</td>
            <td>{api['library']}</td>
            <td>{api['type']}</td>
            <td>{api['source']}</td>
        </tr>'''
    
    return f'''
    <div class="card">
        <h2>🔧 Windows API Declarations</h2>
        <table>
            <thead><tr><th>Function</th><th>Library</th><th>Type</th><th>Source</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>'''


def generate_report(analysis_data, output_path):
    """Generate the complete HTML report."""
    meta = analysis_data.get('metadata', {})
    summary = analysis_data.get('summary', {})
    
    html = HTML_TEMPLATE.format(
        project_name=Path(meta.get('source_directory', 'Unknown')).name,
        source_directory=meta.get('source_directory', 'Unknown'),
        scan_date=meta.get('scan_date', datetime.now().isoformat()),
        scanner_version=meta.get('scanner_version', '2.0.0'),
        total_files=summary.get('total_files', 0),
        forms_count=summary.get('forms_count', 0),
        modules_count=summary.get('modules_count', 0),
        classes_count=summary.get('classes_count', 0),
        total_controls=summary.get('total_controls', 0),
        risk_count=len(analysis_data.get('risks', [])),
        risks_section=generate_risks_section(analysis_data.get('risks', [])),
        inventory_section=generate_inventory_section(analysis_data.get('inventory', {})),
        flow_diagram=generate_flow_diagram(analysis_data),
        crud_section=generate_crud_section(analysis_data.get('crud_operations', [])),
        forms_section=generate_forms_section(analysis_data.get('forms', [])),
        modules_section=generate_modules_section(analysis_data.get('modules', [])),
        dependencies_section=generate_dependencies_section(analysis_data.get('inventory', {})),
        globals_section=generate_globals_section(analysis_data.get('global_variables', [])),
        api_section=generate_api_section(analysis_data.get('api_calls', []))
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Report generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate interactive HTML report from VB6 analysis"
    )
    parser.add_argument(
        "input_json",
        help="Path to VB6 analysis JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output HTML file path",
        default="VB6_AUDIT_REPORT.html"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_json):
        print(f"❌ Error: Input file not found: {args.input_json}")
        return 1
    
    with open(args.input_json, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    generate_report(analysis_data, args.output)
    return 0


if __name__ == "__main__":
    exit(main())
