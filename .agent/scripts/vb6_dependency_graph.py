#!/usr/bin/env python3
"""
VB6 Dependency Graph Generator
==============================
Generates interactive dependency graphs showing:
- Form → Module relationships
- Module → Module relationships
- Form → Form references
- Circular dependencies
Outputs: JSON data + HTML with D3.js visualization
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

PATTERNS = {
    # Module/form references
    'module_call': re.compile(
        r'\b(mod\w+)\.(\w+)',
        re.IGNORECASE
    ),
    'form_reference': re.compile(
        r'\b(frm\w+)\.(\w+)',
        re.IGNORECASE
    ),
    'form_show': re.compile(
        r'(\w+)\.Show\b',
        re.IGNORECASE
    ),
    'load_form': re.compile(
        r'Load\s+(\w+)',
        re.IGNORECASE
    ),
    'call_statement': re.compile(
        r'Call\s+(\w+)\.(\w+)',
        re.IGNORECASE
    ),
}


class VB6DependencyGraph:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.nodes = {}  # name -> {type, file}
        self.edges = []  # [{source, target, type, count}]
        self.edge_counts = defaultdict(int)  # (source, target, type) -> count
        
    def analyze(self):
        """Build the dependency graph."""
        print(f"📊 Building dependency graph: {self.source_dir}")
        
        # Phase 1: Collect all nodes
        self._collect_nodes()
        
        # Phase 2: Find all edges
        self._find_edges()
        
        # Phase 3: Detect circular dependencies
        cycles = self._detect_cycles()
        
        # Build edge list from counts
        for (source, target, edge_type), count in self.edge_counts.items():
            self.edges.append({
                'source': source,
                'target': target,
                'type': edge_type,
                'count': count
            })
        
        results = {
            'summary': {
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
                'forms': len([n for n in self.nodes.values() if n['type'] == 'Form']),
                'modules': len([n for n in self.nodes.values() if n['type'] == 'Module']),
                'classes': len([n for n in self.nodes.values() if n['type'] == 'Class']),
                'circular_dependencies': len(cycles)
            },
            'nodes': [{'id': k, **v} for k, v in self.nodes.items()],
            'edges': self.edges,
            'circular_dependencies': cycles,
            'hub_modules': self._identify_hubs()
        }
        
        return results
    
    def _collect_nodes(self):
        """Collect all forms, modules, classes as nodes."""
        for root, _, files in os.walk(self.source_dir):
            for filename in files:
                filepath = Path(root) / filename
                ext = filepath.suffix.lower()
                
                name = filepath.stem.lower()
                
                if ext == '.frm':
                    self.nodes[name] = {'type': 'Form', 'file': str(filepath.name)}
                elif ext == '.bas':
                    self.nodes[name] = {'type': 'Module', 'file': str(filepath.name)}
                elif ext == '.cls':
                    self.nodes[name] = {'type': 'Class', 'file': str(filepath.name)}
                elif ext == '.ctl':
                    self.nodes[name] = {'type': 'Control', 'file': str(filepath.name)}
    
    def _find_edges(self):
        """Find all dependencies between nodes."""
        for root, _, files in os.walk(self.source_dir):
            for filename in files:
                filepath = Path(root) / filename
                ext = filepath.suffix.lower()
                
                if ext not in ['.frm', '.bas', '.cls', '.ctl']:
                    continue
                
                source = filepath.stem.lower()
                content = self._read_file(filepath)
                if not content:
                    continue
                
                # Find module references
                for match in PATTERNS['module_call'].finditer(content):
                    target = match.group(1).lower()
                    if target != source and target in self.nodes:
                        self.edge_counts[(source, target, 'calls')] += 1
                
                # Find form references
                for match in PATTERNS['form_reference'].finditer(content):
                    target = match.group(1).lower()
                    if target != source and target in self.nodes:
                        self.edge_counts[(source, target, 'references')] += 1
                
                # Find form.Show calls
                for match in PATTERNS['form_show'].finditer(content):
                    target = match.group(1).lower()
                    if target != source and target in self.nodes:
                        self.edge_counts[(source, target, 'shows')] += 1
                
                # Find Load statements
                for match in PATTERNS['load_form'].finditer(content):
                    target = match.group(1).lower()
                    if target != source and target in self.nodes:
                        self.edge_counts[(source, target, 'loads')] += 1
    
    def _detect_cycles(self):
        """Detect circular dependencies using DFS."""
        cycles = []
        
        # Build adjacency list
        adj = defaultdict(set)
        for (source, target, _), _ in self.edge_counts.items():
            adj[source].add(target)
        
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in adj[node]:
                if neighbor not in visited:
                    result = dfs(neighbor)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            path.pop()
            rec_stack.remove(node)
            return None
        
        for node in self.nodes:
            if node not in visited:
                cycle = dfs(node)
                if cycle:
                    cycles.append({
                        'nodes': cycle,
                        'description': ' → '.join(cycle)
                    })
        
        return cycles
    
    def _identify_hubs(self):
        """Identify hub modules (most dependencies)."""
        incoming = defaultdict(int)
        outgoing = defaultdict(int)
        
        for (source, target, _), count in self.edge_counts.items():
            outgoing[source] += count
            incoming[target] += count
        
        hubs = []
        for node in self.nodes:
            total = incoming[node] + outgoing[node]
            if total >= 3:  # Threshold for being a hub
                hubs.append({
                    'name': node,
                    'type': self.nodes[node]['type'],
                    'incoming': incoming[node],
                    'outgoing': outgoing[node],
                    'total': total,
                    'recommendation': 'Migrate early - many dependents' if incoming[node] > outgoing[node] else 'Complex - many dependencies'
                })
        
        return sorted(hubs, key=lambda x: x['total'], reverse=True)
    
    def _read_file(self, filepath):
        """Read file with proper encoding."""
        for enc in ['utf-8', 'latin1', 'cp1252']:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    return f.read()
            except:
                continue
        return None
    
    def generate_html(self, data, output_path):
        """Generate interactive D3.js visualization."""
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>VB6 Dependency Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: system-ui; background: #0f0f23; color: #e8e8e8; margin: 0; }
        #graph { width: 100vw; height: 100vh; }
        .node { cursor: pointer; }
        .node-form { fill: #00d4ff; }
        .node-module { fill: #7b2cbf; }
        .node-class { fill: #00ff88; }
        .node-control { fill: #ffcc00; }
        .link { stroke: #555; stroke-opacity: 0.6; }
        .link-calls { stroke: #00d4ff; }
        .link-shows { stroke: #ff4444; }
        text { fill: #fff; font-size: 10px; }
        .legend { position: fixed; top: 20px; right: 20px; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 8px; }
        .legend div { margin: 5px 0; }
        .legend span { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        h3 { margin: 0 0 10px 0; color: #00d4ff; }
    </style>
</head>
<body>
    <div id="graph"></div>
    <div class="legend">
        <h3>📊 Dependency Graph</h3>
        <div><span style="background:#00d4ff"></span>Form</div>
        <div><span style="background:#7b2cbf"></span>Module</div>
        <div><span style="background:#00ff88"></span>Class</div>
        <div><span style="background:#ffcc00"></span>Control</div>
        <hr style="border-color:#333">
        <div>Nodes: ''' + str(data['summary']['total_nodes']) + '''</div>
        <div>Edges: ''' + str(data['summary']['total_edges']) + '''</div>
        <div>Cycles: ''' + str(data['summary']['circular_dependencies']) + '''</div>
    </div>
    <script>
        const data = ''' + json.dumps(data) + ''';
        
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#graph").append("svg")
            .attr("width", width)
            .attr("height", height);
        
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.edges).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(data.edges)
            .join("line")
            .attr("class", d => "link link-" + d.type)
            .attr("stroke-width", d => Math.min(d.count, 5));
        
        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .join("circle")
            .attr("class", d => "node node-" + d.type.toLowerCase())
            .attr("r", d => 8 + (data.edges.filter(e => e.target.id === d.id || e.source.id === d.id).length * 2))
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        const text = svg.append("g")
            .selectAll("text")
            .data(data.nodes)
            .join("text")
            .text(d => d.id)
            .attr("dx", 12)
            .attr("dy", 4);
        
        simulation.on("tick", () => {
            link.attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            node.attr("cx", d => d.x).attr("cy", d => d.y);
            text.attr("x", d => d.x).attr("y", d => d.y);
        });
        
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }
        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }
        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }
    </script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)


def main():
    parser = argparse.ArgumentParser(description="VB6 Dependency Graph Generator")
    parser.add_argument("source_dir", help="Directory containing VB6 source code")
    parser.add_argument("-o", "--output", default="vb6_dependencies.json", help="Output JSON file")
    parser.add_argument("--html", default="VB6_DEPENDENCY_GRAPH.html", help="Output HTML visualization")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.source_dir):
        print(f"❌ Error: Directory not found: {args.source_dir}")
        return 1
    
    generator = VB6DependencyGraph(args.source_dir)
    results = generator.analyze()
    
    # Save JSON
    indent = 2 if args.pretty else None
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=indent, ensure_ascii=False)
    
    # Generate HTML
    generator.generate_html(results, args.html)
    
    print(f"✅ Dependency graph complete:")
    print(f"   📊 JSON: {args.output}")
    print(f"   🌐 HTML: {args.html}")
    print(f"   📦 Nodes: {results['summary']['total_nodes']}")
    print(f"   🔗 Edges: {results['summary']['total_edges']}")
    print(f"   🔄 Circular deps: {results['summary']['circular_dependencies']}")
    
    return 0


if __name__ == "__main__":
    exit(main())
