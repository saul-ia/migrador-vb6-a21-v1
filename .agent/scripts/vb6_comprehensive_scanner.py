#!/usr/bin/env python3
"""
VB6 Comprehensive Scanner
========================
Expert-level analyzer for VB6 codebases supporting ALL file types.
Generates structured JSON output for report generation.
"""

import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================================
# FILE TYPE DEFINITIONS
# ============================================================================

FILE_CATEGORIES = {
    "project": {
        "extensions": [".vbp", ".vbg", ".vbw"],
        "description": "Project and workspace files",
        "icon": "📦"
    },
    "forms": {
        "extensions": [".frm", ".frx"],
        "description": "User interface forms and binary resources",
        "icon": "🖼️"
    },
    "modules": {
        "extensions": [".bas"],
        "description": "Standard code modules with functions and subroutines",
        "icon": "📄"
    },
    "classes": {
        "extensions": [".cls"],
        "description": "Object-oriented class modules",
        "icon": "🔷"
    },
    "controls": {
        "extensions": [".ctl", ".ctx"],
        "description": "User controls and their binary resources",
        "icon": "🎛️"
    },
    "designers": {
        "extensions": [".dsr", ".dsx", ".pag", ".pgx"],
        "description": "Data reports, designers and property pages",
        "icon": "📊"
    },
    "resources": {
        "extensions": [".res", ".rpt"],
        "description": "Resource files and Crystal Reports",
        "icon": "📁"
    },
    "dependencies": {
        "extensions": [".ocx", ".dll", ".tlb", ".oca", ".dca"],
        "description": "ActiveX controls, DLLs and type libraries",
        "icon": "🔌"
    },
    "assets": {
        "extensions": [".ico", ".gif", ".jpg", ".jpeg", ".png", ".bmp", ".cur"],
        "description": "Image and icon assets",
        "icon": "🎨"
    },
    "help": {
        "extensions": [".chm", ".hlp"],
        "description": "Help and documentation files",
        "icon": "❓"
    },
    "documentation": {
        "extensions": [".txt", ".log", ".doc", ".rtf", ".readme"],
        "description": "Text documentation and logs",
        "icon": "📝"
    },
    "executables": {
        "extensions": [".exe"],
        "description": "Compiled executables",
        "icon": "⚙️"
    },
    "temporary": {
        "extensions": [".tmp", ".scc"],
        "description": "Temporary and source control files",
        "icon": "🗑️"
    }
}

# ============================================================================
# VB6 PARSING PATTERNS
# ============================================================================

PATTERNS = {
    # Project file patterns
    "vbp_form": re.compile(r'^Form=(.+\.frm)', re.MULTILINE | re.IGNORECASE),
    "vbp_module": re.compile(r'^Module=(\w+);\s*(.+\.bas)', re.MULTILINE | re.IGNORECASE),
    "vbp_class": re.compile(r'^Class=(\w+);\s*(.+\.cls)', re.MULTILINE | re.IGNORECASE),
    "vbp_reference": re.compile(r'^Reference=\*\\G\{([^}]+)\}#([^#]+)#([^#]+)#(.+)', re.MULTILINE),
    "vbp_object": re.compile(r'^Object=\{([^}]+)\}#([^;]+);(.+)', re.MULTILINE),
    
    # Form patterns
    "frm_control": re.compile(r'Begin\s+(\w+)\.(\w+)\s+(\w+)', re.MULTILINE),
    "frm_property": re.compile(r'^\s+(\w+)\s*=\s*(.+)$', re.MULTILINE),
    "frm_event": re.compile(r'(Private|Public)\s+Sub\s+(\w+)_(\w+)\s*\(', re.MULTILINE),
    
    # Code patterns
    "sub_function": re.compile(r'(Private|Public)?\s*(Sub|Function)\s+(\w+)\s*\(([^)]*)\)', re.MULTILINE),
    "call_pattern": re.compile(r'\b(Call\s+)?(\w+)\s*\(', re.MULTILINE),
    "crud_addnew": re.compile(r'\.AddNew\b', re.IGNORECASE),
    "crud_update": re.compile(r'\.Update\b', re.IGNORECASE),
    "crud_delete": re.compile(r'\.Delete\b', re.IGNORECASE),
    "crud_edit": re.compile(r'\.Edit\b', re.IGNORECASE),
    "sql_select": re.compile(r'SELECT\s+.+\s+FROM\s+(\w+)', re.IGNORECASE),
    "sql_insert": re.compile(r'INSERT\s+INTO\s+(\w+)', re.IGNORECASE),
    "sql_update": re.compile(r'UPDATE\s+(\w+)\s+SET', re.IGNORECASE),
    "sql_delete": re.compile(r'DELETE\s+FROM\s+(\w+)', re.IGNORECASE),
    
    # Connection strings
    "connection_string": re.compile(r'(Provider|Data Source|Database|DSN)\s*=\s*["\']?([^"\';\n]+)', re.IGNORECASE),
    
    # Error handling
    "on_error": re.compile(r'On\s+Error\s+(Resume\s+Next|GoTo\s+\w+)', re.IGNORECASE),
    
    # Global variables
    "global_var": re.compile(r'^(Public|Global)\s+(\w+)\s+As\s+(\w+)', re.MULTILINE),
    
    # API declarations
    "api_declare": re.compile(r'Declare\s+(Sub|Function)\s+(\w+)\s+Lib\s+"([^"]+)"', re.IGNORECASE)
}

# ============================================================================
# SCANNER CLASS
# ============================================================================

class VB6ComprehensiveScanner:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.files = defaultdict(list)
        self.analysis = {
            "metadata": {
                "scan_date": datetime.now().isoformat(),
                "source_directory": str(self.source_dir),
                "scanner_version": "2.0.0"
            },
            "summary": {},
            "inventory": {},
            "projects": [],
            "forms": [],
            "modules": [],
            "classes": [],
            "dependencies": [],
            "crud_operations": [],
            "call_graph": {},
            "global_variables": [],
            "api_calls": [],
            "error_handling": [],
            "database_connections": [],
            "risks": []
        }
    
    def scan(self):
        """Main entry point for scanning."""
        print(f"🔍 Scanning: {self.source_dir}")
        
        # Step 1: Discover all files
        self._discover_files()
        
        # Step 2: Parse project files first
        self._parse_project_files()
        
        # Step 3: Parse forms
        self._parse_forms()
        
        # Step 4: Parse modules and classes
        self._parse_modules()
        self._parse_classes()
        
        # Step 5: Build call graph
        self._build_call_graph()
        
        # Step 6: Generate summary
        self._generate_summary()
        
        # Step 7: Risk assessment
        self._assess_risks()
        
        return self.analysis
    
    def _discover_files(self):
        """Recursively discover all files and categorize them."""
        all_extensions = set()
        for category in FILE_CATEGORIES.values():
            all_extensions.update(category["extensions"])
        
        for root, dirs, files in os.walk(self.source_dir):
            for filename in files:
                filepath = Path(root) / filename
                ext = filepath.suffix.lower()
                
                # Find category
                category_name = "unknown"
                for cat_name, cat_info in FILE_CATEGORIES.items():
                    if ext in cat_info["extensions"]:
                        category_name = cat_name
                        break
                
                file_info = {
                    "name": filename,
                    "path": str(filepath),
                    "relative_path": str(filepath.relative_to(self.source_dir)),
                    "extension": ext,
                    "size_bytes": filepath.stat().st_size,
                    "category": category_name
                }
                
                self.files[category_name].append(file_info)
        
        # Store in inventory
        for category, files in self.files.items():
            cat_info = FILE_CATEGORIES.get(category, {"description": "Unknown", "icon": "❓"})
            self.analysis["inventory"][category] = {
                "description": cat_info.get("description", "Unknown files"),
                "icon": cat_info.get("icon", "❓"),
                "count": len(files),
                "files": files
            }
    
    def _read_file(self, filepath):
        """Read file with proper encoding handling."""
        encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    return f.read()
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        return None
    
    def _parse_project_files(self):
        """Parse .vbp and .vbg files for project structure."""
        for file_info in self.files.get("project", []):
            if file_info["extension"] == ".vbp":
                content = self._read_file(file_info["path"])
                if not content:
                    continue
                
                project = {
                    "name": file_info["name"],
                    "path": file_info["path"],
                    "forms": [],
                    "modules": [],
                    "classes": [],
                    "references": [],
                    "objects": []
                }
                
                # Extract forms
                for match in PATTERNS["vbp_form"].finditer(content):
                    project["forms"].append(match.group(1))
                
                # Extract modules
                for match in PATTERNS["vbp_module"].finditer(content):
                    project["modules"].append({
                        "name": match.group(1),
                        "file": match.group(2)
                    })
                
                # Extract classes
                for match in PATTERNS["vbp_class"].finditer(content):
                    project["classes"].append({
                        "name": match.group(1),
                        "file": match.group(2)
                    })
                
                # Extract references (COM components)
                for match in PATTERNS["vbp_reference"].finditer(content):
                    project["references"].append({
                        "guid": match.group(1),
                        "version": match.group(2),
                        "location": match.group(4)
                    })
                
                # Extract objects (ActiveX)
                for match in PATTERNS["vbp_object"].finditer(content):
                    project["objects"].append({
                        "guid": match.group(1),
                        "version": match.group(2),
                        "name": match.group(3)
                    })
                
                self.analysis["projects"].append(project)
    
    def _parse_forms(self):
        """Parse .frm files for controls and events."""
        for file_info in self.files.get("forms", []):
            if file_info["extension"] != ".frm":
                continue
                
            content = self._read_file(file_info["path"])
            if not content:
                continue
            
            form = {
                "name": file_info["name"].replace(".frm", "").replace(".FRM", ""),
                "path": file_info["path"],
                "controls": [],
                "events": [],
                "crud_operations": [],
                "sql_queries": [],
                "functions": [],
                "error_handling": []
            }
            
            # Extract controls
            for match in PATTERNS["frm_control"].finditer(content):
                form["controls"].append({
                    "library": match.group(1),
                    "type": match.group(2),
                    "name": match.group(3)
                })
            
            # Extract events
            for match in PATTERNS["frm_event"].finditer(content):
                form["events"].append({
                    "visibility": match.group(1),
                    "control": match.group(2),
                    "event": match.group(3)
                })
            
            # Extract functions/subs
            for match in PATTERNS["sub_function"].finditer(content):
                form["functions"].append({
                    "visibility": match.group(1) or "Private",
                    "type": match.group(2),
                    "name": match.group(3),
                    "params": match.group(4)
                })
            
            # CRUD detection
            crud = self._detect_crud(content)
            if crud:
                form["crud_operations"] = crud
                self.analysis["crud_operations"].append({
                    "source": form["name"],
                    "operations": crud
                })
            
            # SQL queries
            form["sql_queries"] = self._extract_sql(content)
            
            # Error handling patterns
            for match in PATTERNS["on_error"].finditer(content):
                form["error_handling"].append(match.group(0))
                self.analysis["error_handling"].append({
                    "source": form["name"],
                    "pattern": match.group(0)
                })
            
            # Database connections
            for match in PATTERNS["connection_string"].finditer(content):
                self.analysis["database_connections"].append({
                    "source": form["name"],
                    "type": match.group(1),
                    "value": match.group(2)
                })
            
            self.analysis["forms"].append(form)
    
    def _parse_modules(self):
        """Parse .bas files for functions and globals."""
        for file_info in self.files.get("modules", []):
            content = self._read_file(file_info["path"])
            if not content:
                continue
            
            module = {
                "name": file_info["name"].replace(".bas", "").replace(".BAS", ""),
                "path": file_info["path"],
                "functions": [],
                "global_variables": [],
                "api_declarations": []
            }
            
            # Extract functions
            for match in PATTERNS["sub_function"].finditer(content):
                module["functions"].append({
                    "visibility": match.group(1) or "Private",
                    "type": match.group(2),
                    "name": match.group(3),
                    "params": match.group(4)
                })
            
            # Global variables
            for match in PATTERNS["global_var"].finditer(content):
                var_info = {
                    "visibility": match.group(1),
                    "name": match.group(2),
                    "type": match.group(3),
                    "source": module["name"]
                }
                module["global_variables"].append(var_info)
                self.analysis["global_variables"].append(var_info)
            
            # API declarations
            for match in PATTERNS["api_declare"].finditer(content):
                api_info = {
                    "type": match.group(1),
                    "name": match.group(2),
                    "library": match.group(3),
                    "source": module["name"]
                }
                module["api_declarations"].append(api_info)
                self.analysis["api_calls"].append(api_info)
            
            self.analysis["modules"].append(module)
    
    def _parse_classes(self):
        """Parse .cls files for class definitions."""
        for file_info in self.files.get("classes", []):
            content = self._read_file(file_info["path"])
            if not content:
                continue
            
            cls = {
                "name": file_info["name"].replace(".cls", "").replace(".CLS", ""),
                "path": file_info["path"],
                "methods": [],
                "properties": []
            }
            
            # Extract methods
            for match in PATTERNS["sub_function"].finditer(content):
                cls["methods"].append({
                    "visibility": match.group(1) or "Private",
                    "type": match.group(2),
                    "name": match.group(3),
                    "params": match.group(4)
                })
            
            self.analysis["classes"].append(cls)
    
    def _detect_crud(self, content):
        """Detect CRUD operations in code."""
        operations = []
        
        if PATTERNS["crud_addnew"].search(content):
            operations.append("CREATE")
        if PATTERNS["sql_select"].search(content):
            operations.append("READ")
        if PATTERNS["crud_edit"].search(content) or PATTERNS["crud_update"].search(content):
            operations.append("UPDATE")
        if PATTERNS["crud_delete"].search(content):
            operations.append("DELETE")
        
        return operations
    
    def _extract_sql(self, content):
        """Extract SQL queries from code."""
        queries = []
        
        for pattern_name in ["sql_select", "sql_insert", "sql_update", "sql_delete"]:
            for match in PATTERNS[pattern_name].finditer(content):
                queries.append({
                    "type": pattern_name.replace("sql_", "").upper(),
                    "table": match.group(1)
                })
        
        return queries
    
    def _build_call_graph(self):
        """Build a call graph between modules."""
        # Collect all public function names
        all_functions = {}
        
        for module in self.analysis["modules"]:
            for func in module["functions"]:
                if func["visibility"] == "Public":
                    all_functions[func["name"]] = module["name"]
        
        for form in self.analysis["forms"]:
            for func in form["functions"]:
                if func["visibility"] == "Public":
                    all_functions[func["name"]] = form["name"]
        
        # Build call relationships
        self.analysis["call_graph"]["nodes"] = list(set(
            [m["name"] for m in self.analysis["modules"]] +
            [f["name"] for f in self.analysis["forms"]]
        ))
        self.analysis["call_graph"]["edges"] = []
        
        # This is a simplified version - real implementation would parse function bodies
    
    def _generate_summary(self):
        """Generate summary statistics."""
        total_files = sum(len(files) for files in self.files.values())
        total_size = sum(
            f["size_bytes"] for files in self.files.values() for f in files
        )
        
        self.analysis["summary"] = {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_human": self._human_size(total_size),
            "projects_count": len(self.analysis["projects"]),
            "forms_count": len(self.analysis["forms"]),
            "modules_count": len(self.analysis["modules"]),
            "classes_count": len(self.analysis["classes"]),
            "total_controls": sum(len(f["controls"]) for f in self.analysis["forms"]),
            "total_functions": sum(
                len(f["functions"]) for f in self.analysis["forms"]
            ) + sum(
                len(m["functions"]) for m in self.analysis["modules"]
            ),
            "crud_forms_count": len(self.analysis["crud_operations"]),
            "global_variables_count": len(self.analysis["global_variables"]),
            "api_calls_count": len(self.analysis["api_calls"]),
            "error_handling_issues": len([
                e for e in self.analysis["error_handling"]
                if "Resume Next" in e["pattern"]
            ]),
            "categories": {
                cat: len(self.files.get(cat, []))
                for cat in FILE_CATEGORIES.keys()
            }
        }
    
    def _assess_risks(self):
        """Assess migration risks."""
        risks = []
        
        # Check for API calls (Windows-specific)
        if self.analysis["api_calls"]:
            risks.append({
                "level": "HIGH",
                "category": "Platform Dependency",
                "description": f"Found {len(self.analysis['api_calls'])} Windows API declarations",
                "mitigation": "These need browser-compatible alternatives or removal"
            })
        
        # Check for On Error Resume Next
        resume_next_count = len([
            e for e in self.analysis["error_handling"]
            if "Resume Next" in e["pattern"]
        ])
        if resume_next_count > 0:
            risks.append({
                "level": "MEDIUM",
                "category": "Error Handling",
                "description": f"Found {resume_next_count} 'On Error Resume Next' statements",
                "mitigation": "Replace with proper try/catch blocks"
            })
        
        # Check for global variables
        if len(self.analysis["global_variables"]) > 10:
            risks.append({
                "level": "MEDIUM",
                "category": "Code Quality",
                "description": f"Found {len(self.analysis['global_variables'])} global variables",
                "mitigation": "Refactor into services or state management"
            })
        
        # Check for ActiveX controls
        ocx_count = len(self.files.get("dependencies", []))
        if ocx_count > 0:
            risks.append({
                "level": "HIGH",
                "category": "Dependencies",
                "description": f"Found {ocx_count} ActiveX/OCX dependencies",
                "mitigation": "Find modern web alternatives or eliminate"
            })
        
        self.analysis["risks"] = risks
    
    def _human_size(self, size_bytes):
        """Convert bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="VB6 Comprehensive Scanner - Expert-level codebase analyzer"
    )
    parser.add_argument(
        "source_dir",
        help="Directory containing VB6 source code"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file path",
        default="vb6_analysis.json"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output"
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.source_dir):
        print(f"❌ Error: Directory not found: {args.source_dir}")
        return 1
    
    scanner = VB6ComprehensiveScanner(args.source_dir)
    analysis = scanner.scan()
    
    # Output
    indent = 2 if args.pretty else None
    output_json = json.dumps(analysis, indent=indent, ensure_ascii=False)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(output_json)
    
    print(f"✅ Analysis complete! Output: {args.output}")
    print(f"   📊 Files: {analysis['summary']['total_files']}")
    print(f"   📄 Forms: {analysis['summary']['forms_count']}")
    print(f"   📦 Modules: {analysis['summary']['modules_count']}")
    print(f"   ⚠️  Risks: {len(analysis['risks'])}")
    
    return 0


if __name__ == "__main__":
    exit(main())
