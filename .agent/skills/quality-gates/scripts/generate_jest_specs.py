#!/usr/bin/env python3
"""
Jest Spec Generator - Generates unit test specs from project analysis.

This script analyzes:
1. Backend services (Express) → Generates service tests with mocked Prisma
2. Backend controllers → Generates supertest-based controller tests
3. Frontend services (Angular) → Generates HttpClient tests
4. Frontend components → Generates TestBed-based component tests

Output: Jest test files (.spec.ts) for unit testing.
"""

import os
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ServiceMethod:
    name: str
    is_async: bool
    params: List[str]
    return_type: str

@dataclass
class ServiceAnalysis:
    name: str
    file_path: str
    entity: str
    methods: List[ServiceMethod] = field(default_factory=list)
    is_crud: bool = False

@dataclass
class ControllerRoute:
    method: str  # GET, POST, PUT, DELETE
    path: str
    handler: str

@dataclass
class ControllerAnalysis:
    name: str
    file_path: str
    entity: str
    base_path: str
    routes: List[ControllerRoute] = field(default_factory=list)

# =============================================================================
# PATTERNS
# =============================================================================

# TypeScript patterns
CLASS_PATTERN = re.compile(r'(export\s+)?class\s+(\w+)', re.IGNORECASE)
METHOD_PATTERN = re.compile(r'(async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*(\w+(?:<[^>]+>)?))?\s*{', re.IGNORECASE)
CRUD_METHODS = ['getAll', 'getById', 'findAll', 'findOne', 'create', 'update', 'delete', 'remove']

# Express route patterns
ROUTE_PATTERN = re.compile(r'\.(get|post|put|patch|delete)\s*\(\s*[\'"]([^\'"]+)[\'"]', re.IGNORECASE)

# Angular patterns
INJECT_PATTERN = re.compile(r'inject\s*\(\s*(\w+)\s*\)', re.IGNORECASE)
HTTP_PATTERN = re.compile(r'this\.http\.(get|post|put|delete)', re.IGNORECASE)

# =============================================================================
# TEMPLATES
# =============================================================================

SERVICE_TEST_HEADER = '''/**
 * Auto-generated unit tests for {service_name}
 * Entity: {entity}
 * Generated from: {source_file}
 */

import {{ describe, it, expect, jest, beforeEach }} from '@jest/globals';
import {{ {service_name} }} from '{import_path}';
import {{ prisma }} from '../lib/prisma';

// Mock Prisma client
jest.mock('../lib/prisma', () => ({{
  prisma: {{
    {entity_lower}: {{
      findMany: jest.fn(),
      findUnique: jest.fn(),
      findFirst: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
      count: jest.fn(),
    }}
  }}
}}));

describe('{service_name}', () => {{
  let service: {service_name};

  beforeEach(() => {{
    service = new {service_name}();
    jest.clearAllMocks();
  }});
'''

SERVICE_TEST_METHOD = '''
  describe('{method_name}', () => {{
    it('should execute {method_name} successfully', async () => {{
      // Arrange
      const mockResult = {mock_result};
      {mock_setup}

      // Act
      const result = await service.{method_name}({call_params});

      // Assert
      expect(result).toBeDefined();
      {assertions}
    }});

    it('should handle errors in {method_name}', async () => {{
      // Arrange
      {error_mock}

      // Act & Assert
      await expect(service.{method_name}({call_params})).rejects.toThrow();
    }});
  }});
'''

SERVICE_TEST_FOOTER = '''
}});

'''

CONTROLLER_TEST_HEADER = '''/**
 * Auto-generated controller tests for {controller_name}
 * Entity: {entity}
 * Base path: {base_path}
 */

import request from 'supertest';
import {{ app }} from '../app';

describe('{controller_name}', () => {{
'''

CONTROLLER_ROUTE_TEST = '''
  describe('{method} {path}', () => {{
    it('should return {expected_status} for valid request', async () => {{
      const response = await request(app)
        .{method_lower}('{full_path}')
        {request_body}
        .expect({expected_status});

      {response_assertions}
    }});
{error_cases}
  }});
'''

CONTROLLER_TEST_FOOTER = '''
}});
'''

ANGULAR_SERVICE_TEST = '''/**
 * Auto-generated tests for {service_name}
 * Entity: {entity}
 */

import {{ TestBed }} from '@angular/core/testing';
import {{ provideHttpClient }} from '@angular/common/http';
import {{ HttpTestingController, provideHttpClientTesting }} from '@angular/common/http/testing';
import {{ {service_name} }} from './{service_file}';

describe('{service_name}', () => {{
  let service: {service_name};
  let httpMock: HttpTestingController;

  beforeEach(() => {{
    TestBed.configureTestingModule({{
      providers: [
        {service_name},
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    }});

    service = TestBed.inject({service_name});
    httpMock = TestBed.inject(HttpTestingController);
  }});

  afterEach(() => {{
    httpMock.verify();
  }});

  it('should be created', () => {{
    expect(service).toBeTruthy();
  }});

{method_tests}
}});
'''

ANGULAR_COMPONENT_TEST = '''/**
 * Auto-generated tests for {component_name}
 */

import {{ ComponentFixture, TestBed }} from '@angular/core/testing';
import {{ provideHttpClient }} from '@angular/common/http';
import {{ provideHttpClientTesting }} from '@angular/common/http/testing';
import {{ {component_name} }} from './{component_file}';

describe('{component_name}', () => {{
  let component: {component_name};
  let fixture: ComponentFixture<{component_name}>;

  beforeEach(async () => {{
    await TestBed.configureTestingModule({{
      imports: [{component_name}],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    }}).compileComponents();

    fixture = TestBed.createComponent({component_name});
    component = fixture.componentInstance;
  }});

  it('should create', () => {{
    expect(component).toBeTruthy();
  }});

  it('should render', () => {{
    fixture.detectChanges();
    expect(fixture.nativeElement).toBeTruthy();
  }});

{additional_tests}
}});
'''

# =============================================================================
# ANALYZER
# =============================================================================

class JestSpecGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        
    def analyze_and_generate(self, services_dir: str = None, controllers_dir: str = None, 
                             angular_services_dir: str = None, angular_components_dir: str = None):
        """Main entry point for spec generation."""
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if services_dir:
            self._generate_service_tests(Path(services_dir))
            
        if controllers_dir:
            self._generate_controller_tests(Path(controllers_dir))
            
        if angular_services_dir:
            self._generate_angular_service_tests(Path(angular_services_dir))
            
        if angular_components_dir:
            self._generate_angular_component_tests(Path(angular_components_dir))
    
    def _generate_service_tests(self, services_dir: Path):
        """Generate Jest tests for backend services."""
        if not services_dir.exists():
            print(f"  ⚠ Services directory not found: {services_dir}")
            return
            
        ts_files = list(services_dir.glob('*.service.ts'))
        
        for ts_file in ts_files:
            service = self._analyze_service(ts_file)
            if service:
                self._write_service_test(service)
    
    def _analyze_service(self, file_path: Path) -> Optional[ServiceAnalysis]:
        """Analyze a TypeScript service file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  ⚠ Could not read {file_path}: {e}")
            return None
        
        # Find class name
        class_match = CLASS_PATTERN.search(content)
        if not class_match:
            return None
            
        class_name = class_match.group(2)
        
        # Infer entity from service name
        entity = class_name.replace('Service', '')
        
        # Find methods
        methods = []
        for match in METHOD_PATTERN.finditer(content):
            method_name = match.group(2)
            if method_name.startswith('_') or method_name == 'constructor':
                continue
                
            methods.append(ServiceMethod(
                name=method_name,
                is_async=bool(match.group(1)),
                params=[],  # Simplified
                return_type=match.group(3) or 'void'
            ))
        
        # Check if CRUD service
        is_crud = any(m.name in CRUD_METHODS for m in methods)
        
        return ServiceAnalysis(
            name=class_name,
            file_path=str(file_path),
            entity=entity,
            methods=methods,
            is_crud=is_crud
        )
    
    def _write_service_test(self, service: ServiceAnalysis):
        """Write Jest test file for a service."""
        output_path = self.output_dir / f'{service.name.lower()}.spec.ts'
        
        # Generate header
        content = SERVICE_TEST_HEADER.format(
            service_name=service.name,
            entity=service.entity,
            entity_lower=service.entity.lower(),
            source_file=service.file_path,
            import_path=f'../services/{service.name.lower()}'
        )
        
        # Generate method tests
        for method in service.methods:
            mock_result = self._get_mock_result(method.name)
            mock_setup = self._get_mock_setup(service.entity.lower(), method.name)
            call_params = self._get_call_params(method.name)
            assertions = self._get_assertions(method.name)
            error_mock = self._get_error_mock(service.entity.lower(), method.name)
            
            content += SERVICE_TEST_METHOD.format(
                method_name=method.name,
                mock_result=mock_result,
                mock_setup=mock_setup,
                call_params=call_params,
                assertions=assertions,
                error_mock=error_mock
            )
        
        content += SERVICE_TEST_FOOTER
        
        output_path.write_text(content, encoding='utf-8')
        print(f"  ✓ Generated {output_path.name}")
    
    def _generate_controller_tests(self, controllers_dir: Path):
        """Generate Jest tests for backend controllers."""
        if not controllers_dir.exists():
            print(f"  ⚠ Controllers directory not found: {controllers_dir}")
            return
            
        ts_files = list(controllers_dir.glob('*.controller.ts')) + list(controllers_dir.glob('*.routes.ts'))
        
        for ts_file in ts_files:
            controller = self._analyze_controller(ts_file)
            if controller:
                self._write_controller_test(controller)
    
    def _analyze_controller(self, file_path: Path) -> Optional[ControllerAnalysis]:
        """Analyze a controller/routes file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  ⚠ Could not read {file_path}: {e}")
            return None
        
        # Infer entity from filename
        entity = file_path.stem.replace('.controller', '').replace('.routes', '').capitalize()
        
        # Find routes
        routes = []
        for match in ROUTE_PATTERN.finditer(content):
            routes.append(ControllerRoute(
                method=match.group(1).upper(),
                path=match.group(2),
                handler=''
            ))
        
        if not routes:
            return None
        
        # Infer base path
        base_path = f'/api/{entity.lower()}s'
        
        return ControllerAnalysis(
            name=f'{entity}Controller',
            file_path=str(file_path),
            entity=entity,
            base_path=base_path,
            routes=routes
        )
    
    def _write_controller_test(self, controller: ControllerAnalysis):
        """Write Jest test file for a controller."""
        output_path = self.output_dir / f'{controller.entity.lower()}.controller.spec.ts'
        
        content = CONTROLLER_TEST_HEADER.format(
            controller_name=controller.name,
            entity=controller.entity,
            base_path=controller.base_path
        )
        
        for route in controller.routes:
            full_path = controller.base_path + route.path if route.path != '/' else controller.base_path
            expected_status = self._get_expected_status(route.method)
            request_body = self._get_request_body(route.method)
            response_assertions = self._get_response_assertions(route.method)
            error_cases = self._get_error_cases(route.method, full_path)
            
            content += CONTROLLER_ROUTE_TEST.format(
                method=route.method,
                method_lower=route.method.lower(),
                path=route.path,
                full_path=full_path,
                expected_status=expected_status,
                request_body=request_body,
                response_assertions=response_assertions,
                error_cases=error_cases
            )
        
        content += CONTROLLER_TEST_FOOTER
        
        output_path.write_text(content, encoding='utf-8')
        print(f"  ✓ Generated {output_path.name}")
    
    def _generate_angular_service_tests(self, services_dir: Path):
        """Generate Jest tests for Angular services."""
        if not services_dir.exists():
            print(f"  ⚠ Angular services directory not found: {services_dir}")
            return
            
        ts_files = list(services_dir.glob('*.service.ts'))
        
        for ts_file in ts_files:
            self._write_angular_service_test(ts_file)
    
    def _write_angular_service_test(self, file_path: Path):
        """Write Angular service test file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return
        
        # Find service class name
        class_match = CLASS_PATTERN.search(content)
        if not class_match:
            return
            
        service_name = class_match.group(2)
        entity = service_name.replace('Service', '')
        service_file = file_path.stem
        
        # Generate method tests based on HTTP calls
        method_tests = self._generate_http_method_tests(content, entity.lower())
        
        test_content = ANGULAR_SERVICE_TEST.format(
            service_name=service_name,
            entity=entity,
            service_file=service_file,
            method_tests=method_tests
        )
        
        output_path = self.output_dir / f'{service_file}.spec.ts'
        output_path.write_text(test_content, encoding='utf-8')
        print(f"  ✓ Generated {output_path.name}")
    
    def _generate_angular_component_tests(self, components_dir: Path):
        """Generate Jest tests for Angular components."""
        if not components_dir.exists():
            print(f"  ⚠ Angular components directory not found: {components_dir}")
            return
        
        # Find all component.ts files
        ts_files = list(components_dir.rglob('*.component.ts'))
        
        for ts_file in ts_files:
            self._write_angular_component_test(ts_file)
    
    def _write_angular_component_test(self, file_path: Path):
        """Write Angular component test file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return
        
        # Find component class name
        class_match = CLASS_PATTERN.search(content)
        if not class_match:
            return
            
        component_name = class_match.group(2)
        component_file = file_path.stem
        
        # Generate additional tests based on signals/methods
        additional_tests = self._generate_component_tests(content, component_name)
        
        test_content = ANGULAR_COMPONENT_TEST.format(
            component_name=component_name,
            component_file=component_file,
            additional_tests=additional_tests
        )
        
        output_path = self.output_dir / f'{component_file}.spec.ts'
        output_path.write_text(test_content, encoding='utf-8')
        print(f"  ✓ Generated {output_path.name}")
    
    # Helper methods for generating test content
    def _get_mock_result(self, method_name: str) -> str:
        if 'getAll' in method_name or 'findAll' in method_name or 'findMany' in method_name:
            return '[{ id: 1, name: "Test" }]'
        elif 'getById' in method_name or 'findOne' in method_name:
            return '{ id: 1, name: "Test" }'
        elif 'create' in method_name:
            return '{ id: 1, name: "Created" }'
        elif 'update' in method_name:
            return '{ id: 1, name: "Updated" }'
        elif 'delete' in method_name:
            return '{ id: 1 }'
        return '{}'
    
    def _get_mock_setup(self, entity: str, method_name: str) -> str:
        prisma_method = 'findMany'
        if 'getById' in method_name or 'findOne' in method_name:
            prisma_method = 'findUnique'
        elif 'create' in method_name:
            prisma_method = 'create'
        elif 'update' in method_name:
            prisma_method = 'update'
        elif 'delete' in method_name:
            prisma_method = 'delete'
            
        return f'(prisma.{entity}.{prisma_method} as jest.Mock).mockResolvedValue(mockResult);'
    
    def _get_call_params(self, method_name: str) -> str:
        if 'getById' in method_name or 'findOne' in method_name or 'delete' in method_name:
            return '1'
        elif 'create' in method_name:
            return '{ name: "New" }'
        elif 'update' in method_name:
            return '1, { name: "Updated" }'
        return ''
    
    def _get_assertions(self, method_name: str) -> str:
        if 'getAll' in method_name or 'findAll' in method_name:
            return 'expect(Array.isArray(result)).toBe(true);'
        return ''
    
    def _get_error_mock(self, entity: str, method_name: str) -> str:
        prisma_method = 'findMany'
        if 'getById' in method_name or 'findOne' in method_name:
            prisma_method = 'findUnique'
        elif 'create' in method_name:
            prisma_method = 'create'
        elif 'update' in method_name:
            prisma_method = 'update'
        elif 'delete' in method_name:
            prisma_method = 'delete'
            
        return f"(prisma.{entity}.{prisma_method} as jest.Mock).mockRejectedValue(new Error('Database error'));"
    
    def _get_expected_status(self, method: str) -> int:
        return {'GET': 200, 'POST': 201, 'PUT': 200, 'PATCH': 200, 'DELETE': 204}.get(method, 200)
    
    def _get_request_body(self, method: str) -> str:
        if method in ['POST', 'PUT', 'PATCH']:
            return ".send({ name: 'Test' })"
        return ''
    
    def _get_response_assertions(self, method: str) -> str:
        if method == 'GET':
            return 'expect(response.body).toBeDefined();'
        elif method == 'POST':
            return "expect(response.body).toHaveProperty('id');"
        elif method == 'DELETE':
            return ''
        return 'expect(response.body).toBeDefined();'
    
    def _get_error_cases(self, method: str, path: str) -> str:
        if method == 'GET' and ':id' in path:
            return f'''
    it('should return 404 for non-existent item', async () => {{
      await request(app)
        .get('{path.replace(":id", "99999")}')
        .expect(404);
    }});
'''
        elif method in ['POST', 'PUT', 'PATCH']:
            return f'''
    it('should return 400 for invalid data', async () => {{
      await request(app)
        .{method.lower()}('{path}')
        .send({{}})
        .expect(400);
    }});
'''
        return ''
    
    def _generate_http_method_tests(self, content: str, entity: str) -> str:
        """Generate test cases for Angular service HTTP methods."""
        tests = []
        
        if 'this.http.get' in content:
            tests.append(f'''
  it('should fetch all {entity}s', () => {{
    service.getAll().subscribe();
    const req = httpMock.expectOne('/api/{entity}s');
    expect(req.request.method).toBe('GET');
    req.flush([]);
  }});
''')
        
        if 'this.http.post' in content:
            tests.append(f'''
  it('should create {entity}', () => {{
    service.create({{ name: 'Test' }}).subscribe();
    const req = httpMock.expectOne('/api/{entity}s');
    expect(req.request.method).toBe('POST');
    req.flush({{ id: 1 }});
  }});
''')
        
        return '\n'.join(tests)
    
    def _generate_component_tests(self, content: str, component_name: str) -> str:
        """Generate additional test cases for Angular components."""
        tests = []
        
        # Check for loading state
        if 'loading' in content:
            tests.append('''
  it('should show loading state', () => {
    component.loading.set(true);
    fixture.detectChanges();
    const loading = fixture.nativeElement.querySelector('.loading, .spinner');
    expect(loading).toBeTruthy();
  });
''')
        
        # Check for signals
        if 'signal' in content:
            tests.append('''
  it('should update signals correctly', () => {
    // Test signal updates
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });
''')
        
        return '\n'.join(tests)

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate Jest unit test specs from project analysis'
    )
    parser.add_argument('--services', '-s', help='Backend services directory')
    parser.add_argument('--controllers', '-c', help='Backend controllers directory')
    parser.add_argument('--angular-services', '-as', help='Angular services directory')
    parser.add_argument('--angular-components', '-ac', help='Angular components directory')
    parser.add_argument('--output', '-o', default='tests/unit', help='Output directory')
    
    args = parser.parse_args()
    
    if not any([args.services, args.controllers, args.angular_services, args.angular_components]):
        print("Error: At least one input directory must be specified")
        parser.print_help()
        return 1
    
    print(f"Generating Jest specs...")
    generator = JestSpecGenerator(args.output)
    generator.analyze_and_generate(
        services_dir=args.services,
        controllers_dir=args.controllers,
        angular_services_dir=args.angular_services,
        angular_components_dir=args.angular_components
    )
    
    print(f"\n=== Generation Complete ===")
    print(f"Output directory: {args.output}")
    print(f"Run tests with: npm test")
    
    return 0

if __name__ == '__main__':
    exit(main())
