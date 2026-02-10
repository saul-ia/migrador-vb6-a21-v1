#!/usr/bin/env python3
"""
Unit Test Generator for Angular + Express applications.
Automatically generates Jest test files (.spec.ts) for components, services, and controllers.
Generic: works with any project directory.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set


class TypeScriptParser:
    """Parse TypeScript files to extract classes and methods."""
    
    CLASS_PATTERN = re.compile(
        r'export\s+class\s+(\w+)(?:\s+(?:extends|implements)\s+[\w\s,<>]+)?\\s*{',
        re.MULTILINE
    )
    
    METHOD_PATTERN = re.compile(
        r'(?:public|private|protected)?\s*(?:async\s+)?(\w+)\s*\([^)]*\)(?:\s*:\s*[^{]+)?\\s*{',
        re.MULTILINE
    )
    
    CONSTRUCTOR_PATTERN = re.compile(
        r'constructor\s*\(([^)]*)\)',
        re.MULTILINE
    )
    
    IMPORT_PATTERN = re.compile(
        r'import\s+(?:{[^}]+}|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
        re.MULTILINE
    )
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ''
        self.class_name = ''
        self.methods: List[str] = []
        self.dependencies: List[str] = []
        
    def parse(self) -> Dict:
        """Parse TypeScript file and extract class info."""
        try:
            self.content = self.file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f'⚠️  Could not parse {self.file_path}: {e}')
            return {}
        
        # Extract class name
        class_match = self.CLASS_PATTERN.search(self.content)
        if not class_match:
            return {}
        
        self.class_name = class_match.group(1)
        
        # Extract methods
        for match in self.METHOD_PATTERN.finditer(self.content):
            method_name = match.group(1)
            # Skip lifecycle hooks and special methods
            if method_name not in ['constructor'] and not method_name.startswith('_'):
                self.methods.append(method_name)
        
        # Extract constructor dependencies
        ctor_match = self.CONSTRUCTOR_PATTERN.search(self.content)
        if ctor_match:
            params = ctor_match.group(1)
            # Extract parameter types
            for param in params.split(','):
                if ':' in param:
                    param_type = param.split(':')[1].strip().split('<')[0].split('[')[0]
                    if param_type and param_type[0].isupper():
                        self.dependencies.append(param_type)
        
        return {
            'class_name': self.class_name,
            'methods': self.methods,
            'dependencies': self.dependencies,
            'path': str(self.file_path),
        }


class TestGenerator:
    """Generate Jest test files from TypeScript source."""
    
    def __init__(self, file_type: str):
        self.file_type = file_type  # 'component', 'service', 'controller'
    
    def generate_component_test(self, info: Dict) -> str:
        """Generate Angular component test."""
        class_name = info['class_name']
        methods = info['methods']
        deps = info['dependencies']
        
        # Generate mock providers
        mock_providers = []
        for dep in deps:
            if dep not in ['ChangeDetectorRef', 'ElementRef']:
                mock_providers.append(f"        {{ provide: {dep}, useValue: {{{self._mock_methods(dep)}}} }},")
        
        # Generate test cases
        test_cases = []
        for method in methods:
            if method.startswith('ng'):  # Lifecycle hooks
                test_cases.append(f'''
  it('should call {method}', () => {{
    component.{method}();
    expect(component).toBeTruthy();
  }});''')
            else:
                test_cases.append(f'''
  it('should execute {method}', () => {{
    const result = component.{method}();
    expect(result).toBeDefined();
  }});''')
        
        providers_section = '\\n'.join(mock_providers) if mock_providers else '        // No providers needed'
        tests_section = ''.join(test_cases)
        
        return f'''import {{ ComponentFixture, TestBed }} from '@angular/core/testing';
import {{ {class_name} }} from './{self._to_kebab(class_name).replace('-component', '')}.component';

describe('{class_name}', () => {{
  let component: {class_name};
  let fixture: ComponentFixture<{class_name}>;

  beforeEach(async () => {{
    await TestBed.configureTestingModule({{
      imports: [{class_name}],
      providers: [
{providers_section}
      ]
    }}).compileComponents();

    fixture = TestBed.createComponent({class_name});
    component = fixture.componentInstance;
    fixture.detectChanges();
  }});

  it('should create', () => {{
    expect(component).toBeTruthy();
  }});
{tests_section}
}});
'''
    
    def generate_service_test(self, info: Dict) -> str:
        """Generate Angular service test."""
        class_name = info['class_name']
        methods = info['methods']
        deps = info['dependencies']
        
        # Generate mock providers
        mock_providers = []
        uses_http = 'HttpClient' in deps
        if uses_http:
            mock_providers.append("        { provide: HttpClient, useValue: httpClientSpy },")
        
        for dep in deps:
            if dep not in ['HttpClient']:
                mock_providers.append(f"        {{ provide: {dep}, useValue: {{{self._mock_methods(dep)}}} }},")
        
        # Generate test cases
        test_cases = []
        for method in methods:
            test_cases.append(f'''
  it('should execute {method}', () => {{
    const result = service.{method}();
    expect(result).toBeDefined();
  }});''')
        
        http_import = "import { HttpClient } from '@angular/common/http';" if uses_http else ""
        http_spy = "  let httpClientSpy: jasmine.SpyObj<HttpClient>;" if uses_http else ""
        http_setup = "    httpClientSpy = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put', 'delete']);" if uses_http else ""
        
        providers_section = '\\n'.join(mock_providers) if mock_providers else '        // No providers needed'
        tests_section = ''.join(test_cases)
        
        return f'''import {{ TestBed }} from '@angular/core/testing';
{http_import}
import {{ {class_name} }} from './{self._to_kebab(class_name).replace('-service', '')}.service';

describe('{class_name}', () => {{
  let service: {class_name};
{http_spy}

  beforeEach(() => {{
{http_setup}
    TestBed.configureTestingModule({{
      providers: [
        {class_name},
{providers_section}
      ]
    }});
    service = TestBed.inject({class_name});
  }});

  it('should be created', () => {{
    expect(service).toBeTruthy();
  }});
{tests_section}
}});
'''
    
    def generate_controller_test(self, info: Dict) -> str:
        """Generate Express controller test."""
        class_name = info['class_name']
        methods = info['methods']
        deps = info['dependencies']
        
        # Generate mocks
        mock_deps = []
        for dep in deps:
            if 'Service' in dep or 'Repository' in dep:
                mock_deps.append(f"    {self._to_camel(dep)}: {{{self._mock_methods(dep)}}},")
        
        # Generate test cases
        test_cases = []
        for method in methods:
            test_cases.append(f'''
  describe('{method}', () => {{
    it('should execute successfully', async () => {{
      const req = {{ body: {{}}, params: {{}}, query: {{}} }} as any;
      const res = {{ status: jest.fn().returnThis(), json: jest.fn() }} as any;
      
      await controller.{method}(req, res);
      
      expect(controller).toBeDefined();
    }});
  }});''')
        
        deps_section = '\\n'.join(mock_deps) if mock_deps else '    // No dependencies'
        tests_section = ''.join(test_cases)
        
        return f'''import {{ {class_name} }} from './{self._to_kebab(class_name).replace('-controller', '')}.controller';

describe('{class_name}', () => {{
  let controller: {class_name};
  let mockDeps: any;

  beforeEach(() => {{
    mockDeps = {{
{deps_section}
    }};
    controller = new {class_name}(mockDeps);
  }});

  it('should be defined', () => {{
    expect(controller).toBeDefined();
  }});
{tests_section}
}});
'''
    
    def _mock_methods(self, class_name: str) -> str:
        """Generate mock method stubs."""
        common_methods = {
            'HttpClient': 'get: jest.fn(), post: jest.fn(), put: jest.fn(), delete: jest.fn()',
            'Router': 'navigate: jest.fn()',
            'ActivatedRoute': 'params: of({}), queryParams: of({})',
        }
        return common_methods.get(class_name, 'find: jest.fn(), findAll: jest.fn(), create: jest.fn(), update: jest.fn(), delete: jest.fn()')
    
    def _to_kebab(self, name: str) -> str:
        """Convert PascalCase to kebab-case."""
        return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()
    
    def _to_camel(self, name: str) -> str:
        """Convert PascalCase to camelCase."""
        return name[0].lower() + name[1:] if name else name


class UnitTestGenerator:
    """Main generator that scans directories and creates tests."""
    
    def __init__(self, input_dir: Path, test_type: str):
        self.input_dir = input_dir
        self.test_type = test_type
        self.stats = {
            'components': 0,
            'services': 0,
            'controllers': 0,
            'skipped': 0,
        }
    
    def generate(self) -> None:
        """Generate all test files."""
        if not self.input_dir.exists():
            print(f'⚠️  Input directory not found: {self.input_dir}')
            return
        
        # Scan for TypeScript files
        if self.test_type in ['frontend', 'all']:
            self._generate_angular_tests()
        
        if self.test_type in ['backend', 'all']:
            self._generate_backend_tests()
    
    def _generate_angular_tests(self) -> None:
        """Generate Angular component and service tests."""
        frontend_dir = self.input_dir / 'apps' / 'frontend' / 'src'
        if not frontend_dir.exists():
            frontend_dir = self.input_dir / 'src'
        
        if not frontend_dir.exists():
            print(f'⚠️  Frontend directory not found')
            return
        
        # Components
        for ts_file in frontend_dir.rglob('*.component.ts'):
            if '.spec.ts' in str(ts_file):
                continue
            spec_file = ts_file.parent / f'{ts_file.stem}.spec.ts'
            if spec_file.exists():
                self.stats['skipped'] += 1
                continue
            
            parser = TypeScriptParser(ts_file)
            info = parser.parse()
            if info:
                generator = TestGenerator('component')
                test_content = generator.generate_component_test(info)
                spec_file.write_text(test_content, encoding='utf-8')
                print(f'✅ Generated: {spec_file.name}')
                self.stats['components'] += 1
        
        # Services
        for ts_file in frontend_dir.rglob('*.service.ts'):
            if '.spec.ts' in str(ts_file):
                continue
            spec_file = ts_file.parent / f'{ts_file.stem}.spec.ts'
            if spec_file.exists():
                self.stats['skipped'] += 1
                continue
            
            parser = TypeScriptParser(ts_file)
            info = parser.parse()
            if info:
                generator = TestGenerator('service')
                test_content = generator.generate_service_test(info)
                spec_file.write_text(test_content, encoding='utf-8')
                print(f'✅ Generated: {spec_file.name}')
                self.stats['services'] += 1
    
    def _generate_backend_tests(self) -> None:
        """Generate backend controller tests."""
        backend_dir = self.input_dir / 'apps' / 'backend' / 'src'
        if not backend_dir.exists():
            backend_dir = self.input_dir / 'backend' / 'src'
        
        if not backend_dir.exists():
            print(f'⚠️  Backend directory not found')
            return
        
        for ts_file in backend_dir.rglob('*.controller.ts'):
            if '.spec.ts' in str(ts_file):
                continue
            spec_file = ts_file.parent / f'{ts_file.stem}.spec.ts'
            if spec_file.exists():
                self.stats['skipped'] += 1
                continue
            
            parser = TypeScriptParser(ts_file)
            info = parser.parse()
            if info:
                generator = TestGenerator('controller')
                test_content = generator.generate_controller_test(info)
                spec_file.write_text(test_content, encoding='utf-8')
                print(f'✅ Generated: {spec_file.name}')
                self.stats['controllers'] += 1
    
    def print_summary(self) -> None:
        """Print generation summary."""
        print('\\n📊 Test Generation Summary:')
        print(f'   Components: {self.stats["components"]}')
        print(f'   Services: {self.stats["services"]}')
        print(f'   Controllers: {self.stats["controllers"]}')
        print(f'   Skipped (already exist): {self.stats["skipped"]}')
        total = self.stats['components'] + self.stats['services'] + self.stats['controllers']
        print(f'   Total Generated: {total}')


def main():
    parser = argparse.ArgumentParser(description='Generate Jest unit tests for Angular + Express')
    parser.add_argument('--input', required=True, help='Source directory to scan')
    parser.add_argument('--type', choices=['frontend', 'backend', 'all'], default='all', help='Type of tests to generate')
    parser.add_argument('--coverage-threshold', type=int, default=80, help='Target coverage percentage (default: 80)')
    args = parser.parse_args()
    
    print('🧪 Unit Test Generator v1.0')
    print('=' * 50)
    
    generator = UnitTestGenerator(Path(args.input), args.type)
    generator.generate()
    generator.print_summary()
    
    print(f'\\n🎯 Target coverage: {args.coverage_threshold}%')
    print('\\n✅ Run tests with: npm test -- --coverage')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
