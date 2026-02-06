#!/usr/bin/env python3
"""
VB6 Flow Analyzer - Extracts user flows from VB6 forms for E2E test generation.

This script analyzes VB6 .frm files to detect:
1. Navigation patterns (Form.Show, Unload Me)
2. CRUD operations (cmdnue, cmdmod, cmdbor, cmdreg)
3. Event handlers and their actions
4. Validation patterns (MsgBox, If...Then checks)
5. Form fields and their types

Output: JSON file with extracted flows for E2E test generation.
"""

import os
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class FormField:
    name: str
    type: str  # TextBox, ComboBox, ListBox, CheckBox, etc.
    label: Optional[str] = None
    required: bool = False

@dataclass
class NavigationFlow:
    from_form: str
    to_form: str
    trigger: str  # Event handler that triggers navigation
    suggested_route: str = ""

@dataclass
class CRUDOperation:
    entity: str
    form: str
    handler: str
    operation: str  # create, read, update, delete, search

@dataclass
class ValidationRule:
    form: str
    field: str
    rule_type: str  # required, format, range, custom
    message: str

@dataclass
class WorkflowStep:
    step_number: int
    form: str
    handler: str
    action: str
    description: str

@dataclass
class Workflow:
    name: str
    source_form: str
    steps: List[WorkflowStep] = field(default_factory=list)

@dataclass
class FormAnalysis:
    name: str
    caption: str
    is_mdi: bool
    is_mdi_child: bool
    fields: List[FormField] = field(default_factory=list)
    buttons: List[str] = field(default_factory=list)
    event_handlers: List[str] = field(default_factory=list)

@dataclass
class FlowAnalysisResult:
    forms: List[FormAnalysis] = field(default_factory=list)
    navigation: List[NavigationFlow] = field(default_factory=list)
    crud_operations: List[CRUDOperation] = field(default_factory=list)
    validations: List[ValidationRule] = field(default_factory=list)
    workflows: List[Workflow] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    suggested_routes: Dict[str, str] = field(default_factory=dict)

# =============================================================================
# PATTERNS
# =============================================================================

# VB6 Form patterns
FORM_HEADER_PATTERN = re.compile(r'Begin VB\.(MDI)?Form\s+(\w+)', re.IGNORECASE)
CAPTION_PATTERN = re.compile(r'Caption\s*=\s*"([^"]*)"', re.IGNORECASE)
CONTROL_PATTERN = re.compile(r'Begin VB\.(\w+)\s+(\w+)', re.IGNORECASE)
LABEL_PATTERN = re.compile(r'Caption\s*=\s*"([^"]*)"', re.IGNORECASE)

# Event handler patterns
EVENT_HANDLER_PATTERN = re.compile(r'(Private|Public)?\s*Sub\s+(\w+_\w+)\s*\(\s*\)', re.IGNORECASE)
FORM_SHOW_PATTERN = re.compile(r'(\w+)\.Show', re.IGNORECASE)
UNLOAD_PATTERN = re.compile(r'Unload\s+(Me|\w+)', re.IGNORECASE)

# CRUD operation button patterns
CRUD_PATTERNS = {
    'create': re.compile(r'cmd(nue|new|add|crear|agregar)', re.IGNORECASE),
    'update': re.compile(r'cmd(mod|edit|update|modificar|editar)', re.IGNORECASE),
    'delete': re.compile(r'cmd(bor|del|delete|eliminar|borrar)', re.IGNORECASE),
    'save': re.compile(r'cmd(reg|save|guardar|grabar|aceptar|ace)', re.IGNORECASE),
    'cancel': re.compile(r'cmd(can|cancel|cancelar)', re.IGNORECASE),
    'search': re.compile(r'cmd(bus|search|buscar|find|consultar|cons)', re.IGNORECASE),
    'exit': re.compile(r'cmd(sal|exit|salir|cerrar|close)', re.IGNORECASE),
}

# Validation patterns
MSGBOX_PATTERN = re.compile(r'MsgBox\s+"([^"]+)"', re.IGNORECASE)
REQUIRED_CHECK_PATTERN = re.compile(r'If\s+(\w+)\s*=\s*""\s+Then', re.IGNORECASE)
RECORDCOUNT_PATTERN = re.compile(r'RecordCount\s*=\s*0', re.IGNORECASE)

# =============================================================================
# ANALYZER
# =============================================================================

class VB6FlowAnalyzer:
    def __init__(self, input_dir: str):
        self.input_dir = Path(input_dir)
        self.result = FlowAnalysisResult()
        self.form_name_map: Dict[str, str] = {}  # form_var -> form_file
        
    def analyze(self) -> FlowAnalysisResult:
        """Main analysis entry point."""
        frm_files = list(self.input_dir.rglob('*.frm')) + list(self.input_dir.rglob('*.FRM'))
        
        for frm_file in frm_files:
            self._analyze_form(frm_file)
        
        # Post-processing
        self._detect_entities()
        self._suggest_routes()
        self._detect_workflows()
        
        return self.result
    
    def _analyze_form(self, frm_path: Path):
        """Analyze a single VB6 form file."""
        try:
            # Try multiple encodings
            content = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    content = frm_path.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if not content:
                print(f"Warning: Could not read {frm_path}")
                return
                
        except Exception as e:
            print(f"Error reading {frm_path}: {e}")
            return
        
        # Extract form metadata
        form_analysis = self._extract_form_metadata(content, frm_path.stem)
        self.result.forms.append(form_analysis)
        
        # Extract navigation
        self._extract_navigation(content, form_analysis.name)
        
        # Extract CRUD operations
        self._extract_crud_operations(content, form_analysis.name)
        
        # Extract validations
        self._extract_validations(content, form_analysis.name)
    
    def _extract_form_metadata(self, content: str, filename: str) -> FormAnalysis:
        """Extract form metadata from content."""
        # Form name and type
        form_match = FORM_HEADER_PATTERN.search(content)
        is_mdi = bool(form_match and form_match.group(1))
        form_name = form_match.group(2) if form_match else filename
        
        # Caption
        caption_match = CAPTION_PATTERN.search(content)
        caption = caption_match.group(1) if caption_match else form_name
        
        # Check if MDI child
        is_mdi_child = 'MDIChild' in content and 'True' in content
        
        # Extract controls
        fields: List[FormField] = []
        buttons: List[str] = []
        
        for match in CONTROL_PATTERN.finditer(content):
            control_type = match.group(1)
            control_name = match.group(2)
            
            if control_type in ['TextBox', 'ComboBox', 'ListBox', 'CheckBox', 'OptionButton']:
                fields.append(FormField(
                    name=control_name,
                    type=control_type
                ))
            elif control_type == 'CommandButton':
                buttons.append(control_name)
        
        # Extract event handlers
        handlers = [m.group(2) for m in EVENT_HANDLER_PATTERN.finditer(content)]
        
        # Map form variable names
        self.form_name_map[form_name.lower()] = form_name
        
        return FormAnalysis(
            name=form_name,
            caption=caption,
            is_mdi=is_mdi,
            is_mdi_child=is_mdi_child,
            fields=fields,
            buttons=buttons,
            event_handlers=handlers
        )
    
    def _extract_navigation(self, content: str, form_name: str):
        """Extract navigation patterns from event handlers."""
        # Find all Form.Show calls
        for match in FORM_SHOW_PATTERN.finditer(content):
            target_form = match.group(1)
            
            # Find which handler contains this
            handler = self._find_containing_handler(content, match.start())
            
            if handler and target_form.lower() != 'me':
                self.result.navigation.append(NavigationFlow(
                    from_form=form_name,
                    to_form=target_form,
                    trigger=handler
                ))
    
    def _extract_crud_operations(self, content: str, form_name: str):
        """Extract CRUD operations from button handlers."""
        for handler in EVENT_HANDLER_PATTERN.finditer(content):
            handler_name = handler.group(2)
            
            for operation, pattern in CRUD_PATTERNS.items():
                if pattern.match(handler_name.split('_')[0]):
                    self.result.crud_operations.append(CRUDOperation(
                        entity=self._infer_entity_from_form(form_name),
                        form=form_name,
                        handler=handler_name,
                        operation=operation
                    ))
                    break
    
    def _extract_validations(self, content: str, form_name: str):
        """Extract validation patterns."""
        # Required field checks
        for match in REQUIRED_CHECK_PATTERN.finditer(content):
            field_name = match.group(1)
            # Find associated MsgBox
            msgbox_match = MSGBOX_PATTERN.search(content[match.start():match.start()+500])
            message = msgbox_match.group(1) if msgbox_match else "Required field"
            
            self.result.validations.append(ValidationRule(
                form=form_name,
                field=field_name,
                rule_type='required',
                message=message
            ))
    
    def _find_containing_handler(self, content: str, position: int) -> Optional[str]:
        """Find which event handler contains a given position."""
        handlers = list(EVENT_HANDLER_PATTERN.finditer(content))
        
        for i, handler in enumerate(handlers):
            start = handler.start()
            # Find end (next Sub or End Sub)
            end_match = re.search(r'End Sub', content[start:])
            if end_match:
                end = start + end_match.end()
                if start <= position <= end:
                    return handler.group(2)
        
        return None
    
    def _infer_entity_from_form(self, form_name: str) -> str:
        """Infer entity name from form name."""
        # Common patterns: frmClientes -> Clientes, FRMLIB -> Lib
        name = form_name.lower()
        name = re.sub(r'^frm', '', name)
        name = re.sub(r'^form', '', name)
        return name.capitalize() if name else form_name
    
    def _detect_entities(self):
        """Detect unique entities from forms."""
        entities: Set[str] = set()
        
        for form in self.result.forms:
            if not form.is_mdi:
                entity = self._infer_entity_from_form(form.name)
                if entity:
                    entities.add(entity)
        
        self.result.entities = sorted(list(entities))
    
    def _suggest_routes(self):
        """Suggest Angular routes based on form analysis."""
        route_map = {}
        
        for form in self.result.forms:
            if form.is_mdi:
                continue
                
            entity = self._infer_entity_from_form(form.name).lower()
            
            # Map common patterns
            if 'login' in form.name.lower() or 'password' in form.caption.lower():
                route_map[form.name] = '/login'
            elif 'ayuda' in form.name.lower() or 'help' in form.caption.lower():
                route_map[form.name] = '/ayuda'
            elif 'principal' in form.name.lower() or 'main' in form.caption.lower():
                route_map[form.name] = '/dashboard'
            else:
                route_map[form.name] = f'/{entity}'
        
        self.result.suggested_routes = route_map
        
        # Update navigation with suggested routes
        for nav in self.result.navigation:
            nav.suggested_route = route_map.get(nav.to_form, f'/{nav.to_form.lower()}')
    
    def _detect_workflows(self):
        """Detect multi-step workflows from form interactions."""
        # Group CRUD operations by entity
        entity_ops: Dict[str, List[CRUDOperation]] = {}
        
        for op in self.result.crud_operations:
            if op.entity not in entity_ops:
                entity_ops[op.entity] = []
            entity_ops[op.entity].append(op)
        
        # Create workflow for each entity with multiple operations
        for entity, ops in entity_ops.items():
            if len(ops) >= 3:  # At least search + save + one CRUD
                workflow = Workflow(
                    name=f"{entity} Management",
                    source_form=ops[0].form
                )
                
                # Order operations logically
                op_order = ['search', 'create', 'update', 'delete', 'save', 'cancel']
                sorted_ops = sorted(ops, key=lambda x: op_order.index(x.operation) if x.operation in op_order else 99)
                
                for i, op in enumerate(sorted_ops):
                    workflow.steps.append(WorkflowStep(
                        step_number=i + 1,
                        form=op.form,
                        handler=op.handler,
                        action=op.operation,
                        description=f"{op.operation.capitalize()} {entity}"
                    ))
                
                self.result.workflows.append(workflow)
    
    def to_json(self) -> str:
        """Convert result to JSON string."""
        def serialize(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return asdict(obj)
            return str(obj)
        
        return json.dumps(asdict(self.result), indent=2, default=serialize)

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Analyze VB6 forms to extract user flows for E2E testing'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input directory containing VB6 .frm files'
    )
    parser.add_argument(
        '--output', '-o',
        default='analysis/flows.json',
        help='Output JSON file path'
    )
    
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input directory not found: {args.input}")
        return 1
    
    # Run analysis
    print(f"Analyzing VB6 forms in: {args.input}")
    analyzer = VB6FlowAnalyzer(args.input)
    result = analyzer.analyze()
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    output_path.write_text(analyzer.to_json(), encoding='utf-8')
    
    # Print summary
    print(f"\n=== Analysis Complete ===")
    print(f"Forms analyzed: {len(result.forms)}")
    print(f"Navigation flows: {len(result.navigation)}")
    print(f"CRUD operations: {len(result.crud_operations)}")
    print(f"Validations: {len(result.validations)}")
    print(f"Workflows detected: {len(result.workflows)}")
    print(f"Entities detected: {result.entities}")
    print(f"\nOutput written to: {args.output}")
    
    return 0

if __name__ == '__main__':
    exit(main())
