#!/usr/bin/env python3
"""
VB6 Dead Code Detector
======================
Finds unused functions, subs, and forms in VB6 codebases:
- Unreferenced functions/subs
- Orphan forms (not shown by any code)
- Unused global variables
- Declared but uncalled procedures
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

PATTERNS = {
    # Function/Sub declarations
    'declaration': re.compile(
        r'(Private|Public)?\s*(Sub|Function)\s+(\w+)\s*\(', 
        re.IGNORECASE
    ),
    
    # Property declarations
    'property': re.compile(
        r'Property\s+(Get|Let|Set)\s+(\w+)',
        re.IGNORECASE
    ),
    
    # Form.Show calls
    'form_show': re.compile(
        r'(\w+)\.Show\b',
        re.IGNORECASE
    ),
    
    # Form Load
    'load_form': re.compile(
        r'Load\s+(\w+)',
        re.IGNORECASE
    ),
    
    # Global/Public variable declarations
    'global_var': re.compile(
        r'^(Public|Global)\s+(\w+)\s+As',
        re.IGNORECASE | re.MULTILINE
    ),
    
    # Constant declarations
    'constant': re.compile(
        r'^(Public\s+)?Const\s+(\w+)\s*=',
        re.IGNORECASE | re.MULTILINE
    ),
    
    # Call statements
    'call_statement': re.compile(
        r'Call\s+(\w+)',
        re.IGNORECASE
    ),
    
    # Function calls (word followed by parenthesis)
    'function_call': re.compile(
        r'\b(\w+)\s*\(',
        re.IGNORECASE
    ),
    
    # Event handlers (these are special - called by VB runtime)
    'event_handler': re.compile(
        r'(Private|Public)?\s*Sub\s+(\w+)_(Click|Load|Change|KeyPress|MouseMove|DblClick|GotFocus|LostFocus|Activate|Deactivate|Resize|Unload|Initialize|Terminate)',
        re.IGNORECASE
    ),
    
    # API Declarations
    'api_declare': re.compile(
        r'Declare\s+(Sub|Function)\s+(\w+)',
        re.IGNORECASE
    )
}


class VB6DeadCodeDetector:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.declarations = {}  # name -> {file, type, line}
        self.references = defaultdict(set)  # name -> set of files referencing it
        self.forms = {}  # form name -> file
        self.form_references = defaultdict(set)  # form name -> files showing it
        self.globals = {}  # var name -> {file, type}
        self.global_references = defaultdict(set)
        self.event_handlers = set()  # Names that are event handlers (auto-called)
        
    def analyze(self):
        """Main analysis entry point."""
        print(f"🔍 Detecting dead code: {self.source_dir}")
        
        # Phase 1: Collect all declarations
        self._collect_declarations()
        
        # Phase 2: Find all references
        self._find_references()
        
        # Phase 3: Compare to find dead code
        dead_functions = self._find_dead_functions()
        orphan_forms = self._find_orphan_forms()
        unused_globals = self._find_unused_globals()
        
        results = {
            'summary': {
                'total_functions_declared': len(self.declarations),
                'dead_functions': len(dead_functions),
                'total_forms': len(self.forms),
                'orphan_forms': len(orphan_forms),
                'total_globals': len(self.globals),
                'unused_globals': len(unused_globals),
                'dead_code_percentage': self._calculate_percentage(dead_functions)
            },
            'dead_functions': dead_functions,
            'orphan_forms': orphan_forms,
            'unused_globals': unused_globals
        }
        
        return results
    
    def _collect_declarations(self):
        """Collect all function/sub/form declarations."""
        for root, _, files in os.walk(self.source_dir):
            for filename in files:
                filepath = Path(root) / filename
                ext = filepath.suffix.lower()
                
                if ext == '.frm':
                    # Register form
                    form_name = filepath.stem
                    self.forms[form_name.lower()] = str(filepath)
                
                if ext in ['.frm', '.bas', '.cls', '.ctl']:
                    content = self._read_file(filepath)
                    if not content:
                        continue
                    
                    # Find function/sub declarations
                    for match in PATTERNS['declaration'].finditer(content):
                        func_name = match.group(3).lower()
                        visibility = match.group(1) or 'Private'
                        func_type = match.group(2)
                        
                        self.declarations[func_name] = {
                            'file': str(filepath.name),
                            'visibility': visibility,
                            'type': func_type,
                            'full_name': f"{filepath.stem}.{match.group(3)}"
                        }
                    
                    # Find event handlers (auto-called by VB)
                    for match in PATTERNS['event_handler'].finditer(content):
                        self.event_handlers.add(match.group(2).lower())
                    
                    # Find global variables
                    for match in PATTERNS['global_var'].finditer(content):
                        var_name = match.group(2).lower()
                        self.globals[var_name] = {
                            'file': str(filepath.name),
                            'type': 'Variable'
                        }
                    
                    # Find constants
                    for match in PATTERNS['constant'].finditer(content):
                        const_name = match.group(2).lower()
                        self.globals[const_name] = {
                            'file': str(filepath.name),
                            'type': 'Constant'
                        }
    
    def _find_references(self):
        """Find all references to declared items."""
        for root, _, files in os.walk(self.source_dir):
            for filename in files:
                filepath = Path(root) / filename
                ext = filepath.suffix.lower()
                
                if ext not in ['.frm', '.bas', '.cls', '.ctl']:
                    continue
                
                content = self._read_file(filepath)
                if not content:
                    continue
                
                # Find function calls
                for match in PATTERNS['call_statement'].finditer(content):
                    func_name = match.group(1).lower()
                    self.references[func_name].add(str(filepath.name))
                
                for match in PATTERNS['function_call'].finditer(content):
                    func_name = match.group(1).lower()
                    self.references[func_name].add(str(filepath.name))
                
                # Find form references
                for match in PATTERNS['form_show'].finditer(content):
                    form_name = match.group(1).lower()
                    self.form_references[form_name].add(str(filepath.name))
                
                for match in PATTERNS['load_form'].finditer(content):
                    form_name = match.group(1).lower()
                    self.form_references[form_name].add(str(filepath.name))
                
                # Find global variable usage
                for var_name in self.globals.keys():
                    if re.search(r'\b' + re.escape(var_name) + r'\b', content, re.IGNORECASE):
                        self.global_references[var_name].add(str(filepath.name))
    
    def _find_dead_functions(self):
        """Find functions that are never called."""
        dead = []
        
        # Built-in functions that should not be flagged
        vb_builtins = {
            'left', 'right', 'mid', 'len', 'trim', 'str', 'val', 'int', 
            'cint', 'clng', 'cdbl', 'csng', 'cstr', 'cbool', 'cdate',
            'format', 'msgbox', 'inputbox', 'isnull', 'isnumeric', 'isdate',
            'now', 'date', 'time', 'year', 'month', 'day', 'hour', 'minute',
            'ucase', 'lcase', 'instr', 'replace', 'split', 'join',
            'array', 'ubound', 'lbound', 'redim', 'shell', 'doevents'
        }
        
        for func_name, info in self.declarations.items():
            # Skip event handlers (auto-called)
            if func_name in self.event_handlers:
                continue
            
            # Skip if it's referenced somewhere
            if func_name in self.references:
                # Check if only referenced in its own file (self-reference doesn't count as "used")
                refs = self.references[func_name]
                if len(refs) > 1 or info['file'] not in refs:
                    continue
            
            # Skip VB built-ins that might be shadowed
            if func_name in vb_builtins:
                continue
            
            # Skip Main (entry point)
            if func_name == 'main':
                continue
            
            dead.append({
                'name': info['full_name'],
                'file': info['file'],
                'type': info['type'],
                'visibility': info['visibility'],
                'recommendation': 'Review and remove if truly unused'
            })
        
        return dead
    
    def _find_orphan_forms(self):
        """Find forms that are never shown."""
        orphans = []
        
        # Special forms that shouldn't be flagged
        special_forms = {'mdiproject', 'mdiform', 'splash', 'about', 'frmabout', 'frmsplash', 'frmmain'}
        
        for form_name, filepath in self.forms.items():
            if form_name in self.form_references:
                continue
            
            # Skip special forms
            if form_name in special_forms:
                continue
            
            # Skip if it's a startup form (would be in VBP)
            # For now, don't flag forms - they might be startup forms
            orphans.append({
                'name': form_name,
                'file': filepath,
                'recommendation': 'Check if startup form or truly orphaned'
            })
        
        return orphans
    
    def _find_unused_globals(self):
        """Find global variables that are never used."""
        unused = []
        
        for var_name, info in self.globals.items():
            if var_name not in self.global_references:
                unused.append({
                    'name': var_name,
                    'file': info['file'],
                    'type': info['type'],
                    'recommendation': 'Remove unused global'
                })
            else:
                # Check if only used in declaration file
                refs = self.global_references[var_name]
                if len(refs) == 1 and info['file'] in refs:
                    unused.append({
                        'name': var_name,
                        'file': info['file'],
                        'type': info['type'],
                        'recommendation': 'Used only in declaration file - consider localizing'
                    })
        
        return unused
    
    def _calculate_percentage(self, dead_functions):
        """Calculate dead code percentage."""
        if len(self.declarations) == 0:
            return 0
        return round(len(dead_functions) / len(self.declarations) * 100, 2)
    
    def _read_file(self, filepath):
        """Read file with proper encoding."""
        for enc in ['utf-8', 'latin1', 'cp1252']:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    return f.read()
            except:
                continue
        return None


def main():
    parser = argparse.ArgumentParser(description="VB6 Dead Code Detector")
    parser.add_argument("source_dir", help="Directory containing VB6 source code")
    parser.add_argument("-o", "--output", default="vb6_dead_code.json", help="Output JSON file")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.source_dir):
        print(f"❌ Error: Directory not found: {args.source_dir}")
        return 1
    
    detector = VB6DeadCodeDetector(args.source_dir)
    results = detector.analyze()
    
    indent = 2 if args.pretty else None
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=indent, ensure_ascii=False)
    
    print(f"✅ Dead code detection complete: {args.output}")
    print(f"   🔍 Functions analyzed: {results['summary']['total_functions_declared']}")
    print(f"   💀 Dead functions: {results['summary']['dead_functions']}")
    print(f"   📋 Orphan forms: {results['summary']['orphan_forms']}")
    print(f"   🌐 Unused globals: {results['summary']['unused_globals']}")
    print(f"   📉 Dead code %: {results['summary']['dead_code_percentage']}%")
    
    return 0


if __name__ == "__main__":
    exit(main())
