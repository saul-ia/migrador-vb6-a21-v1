#!/usr/bin/env python3
"""
Contract Test Generator for API endpoint testing.
Generates Jest/Supertest contract tests from swagger.json.
Generic: works with any OpenAPI/Swagger specification.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class SwaggerParser:
    """Parse swagger.json to extract API endpoints."""
    
    def __init__(self, swagger_path: Path):
        self.swagger_path = swagger_path
        self.endpoints: List[Dict] = []
        self.base_path = ''
        self.schemas: Dict = {}
    
    def parse(self) -> List[Dict]:
        """Parse swagger file and extract all endpoints."""
        try:
            data = json.loads(self.swagger_path.read_text(encoding='utf-8'))
        except Exception as e:
            print(f'⚠️  Could not parse swagger file: {e}')
            return []
        
        # Get base path and schemas
        self.base_path = data.get('basePath', '')
        self.schemas = data.get('components', {}).get('schemas', {})
        self.schemas.update(data.get('definitions', {}))  # Swagger 2.0
        
        # Parse paths
        paths = data.get('paths', {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ('get', 'post', 'put', 'patch', 'delete'):
                    endpoint = {
                        'path': f'{self.base_path}{path}'.replace('//', '/'),
                        'method': method.upper(),
                        'operationId': details.get('operationId', ''),
                        'summary': details.get('summary', ''),
                        'parameters': self._extract_parameters(details),
                        'requestBody': self._extract_request_body(details),
                        'responses': self._extract_responses(details),
                        'tags': details.get('tags', []),
                    }
                    self.endpoints.append(endpoint)
        
        return self.endpoints
    
    def _extract_parameters(self, details: Dict) -> List[Dict]:
        """Extract path/query parameters."""
        params = []
        for param in details.get('parameters', []):
            params.append({
                'name': param.get('name', ''),
                'in': param.get('in', ''),
                'type': param.get('type', param.get('schema', {}).get('type', 'string')),
                'required': param.get('required', False),
            })
        return params
    
    def _extract_request_body(self, details: Dict) -> Optional[Dict]:
        """Extract request body schema."""
        # OpenAPI 3.x
        req_body = details.get('requestBody', {})
        if req_body:
            content = req_body.get('content', {})
            schema = content.get('application/json', {}).get('schema', {})
            return self._resolve_schema(schema)
        
        # Swagger 2.0
        for param in details.get('parameters', []):
            if param.get('in') == 'body':
                return self._resolve_schema(param.get('schema', {}))
        
        return None
    
    def _extract_responses(self, details: Dict) -> Dict:
        """Extract response schemas."""
        responses = {}
        for code, resp in details.get('responses', {}).items():
            # OpenAPI 3.x
            content = resp.get('content', {}).get('application/json', {})
            schema = content.get('schema', {})
            if not schema:
                # Swagger 2.0
                schema = resp.get('schema', {})
            
            responses[code] = {
                'description': resp.get('description', ''),
                'schema': self._resolve_schema(schema) if schema else None,
            }
        return responses
    
    def _resolve_schema(self, schema: Dict) -> Dict:
        """Resolve $ref in schema."""
        if not schema:
            return {}
        
        ref = schema.get('$ref', '')
        if ref:
            ref_name = ref.split('/')[-1]
            return self.schemas.get(ref_name, {})
        
        if schema.get('type') == 'array':
            items = schema.get('items', {})
            return {'type': 'array', 'items': self._resolve_schema(items)}
        
        return schema


class ContractTestGenerator:
    """Generate Jest contract tests from endpoints."""
    
    def __init__(self, base_url: str = 'http://localhost:3000'):
        self.base_url = base_url
    
    def generate_test_suite(self, endpoints: List[Dict]) -> str:
        """Generate complete test suite file."""
        # Group by tag
        by_tag: Dict[str, List[Dict]] = {}
        for endpoint in endpoints:
            tags = endpoint.get('tags', ['default'])
            tag = tags[0] if tags else 'default'
            if tag not in by_tag:
                by_tag[tag] = []
            by_tag[tag].append(endpoint)
        
        # Generate test suites for each group
        test_suites = []
        for tag, tag_endpoints in by_tag.items():
            suite_content = self._generate_tag_suite(tag, tag_endpoints)
            test_suites.append((tag, suite_content))
        
        return test_suites
    
    def _generate_tag_suite(self, tag: str, endpoints: List[Dict]) -> str:
        """Generate test suite for a specific tag/group."""
        test_cases = []
        
        for endpoint in endpoints:
            test_case = self._generate_endpoint_test(endpoint)
            test_cases.append(test_case)
        
        tests_content = '\\n\\n'.join(test_cases)
        
        return f'''import request from 'supertest';

const baseUrl = '{self.base_url}';

describe('Contract Tests: {tag.capitalize()}', () => {{
  let authToken: string;

  beforeAll(async () => {{
    // Setup: Login or get auth token if needed
    // const response = await request(baseUrl).post('/api/auth/login').send({{ username: 'test', password: 'test' }});
    // authToken = response.body.token;
  }});

{tests_content}
}});
'''
    
    def _generate_endpoint_test(self, endpoint: Dict) -> str:
        """Generate test for a single endpoint."""
        method = endpoint['method'].lower()
        path = endpoint['path']
        summary = endpoint['summary'] or f'{method.upper()} {path}'
        
        # Build test path (replace params)
        test_path = path
        path_params = [p for p in endpoint['parameters'] if p['in'] == 'path']
        for param in path_params:
            test_path = test_path.replace(f'{{{param["name"]}}}', f'test-{param["name"]}')
        
        # Build query params
        query_params = [p for p in endpoint['parameters'] if p['in'] == 'query']
        query_string = ''
        if query_params:
            query_pairs = [f'{p["name"]}=test' for p in query_params[:2]]  # Limit to 2
            query_string = f'.query({{ {", ".join([f"{p["name"]}: \'test\'" for p in query_params[:2]])} }})'
        
        # Build request body
        request_body = ''
        if endpoint['requestBody'] and method in ['post', 'put', 'patch']:
            body_example = self._generate_example_body(endpoint['requestBody'])
            request_body = f'.send({json.dumps(body_example, indent=4)})'
        
        # Expected status code
        success_codes = [code for code in endpoint['responses'].keys() if code.startswith('2')]
        expected_status = success_codes[0] if success_codes else '200'
        
        # Auth header
        auth_header = ''
        # if 'security' in endpoint or path.startswith('/api/'):
        #     auth_header = ".set('Authorization', `Bearer ${authToken}`)"
        
        return f'''  describe('{method.upper()} {path}', () => {{
    it('should return {expected_status} - {summary}', async () => {{
      const response = await request(baseUrl)
        .{method}('{test_path}'){query_string}{auth_header}{request_body};

      expect(response.status).toBe({expected_status});
      expect(response.body).toBeDefined();
    }});

    it('should match response schema', async () => {{
      const response = await request(baseUrl)
        .{method}('{test_path}'){query_string}{auth_header}{request_body};

      // Validate response structure
      if (response.status === {expected_status}) {{
        {self._generate_schema_assertions(endpoint['responses'].get(expected_status, {}).get('schema'))}
      }}
    }});
  }});'''
    
    def _generate_example_body(self, schema: Dict) -> Dict:
        """Generate example request body from schema."""
        if not schema:
            return {}
        
        if schema.get('type') == 'object':
            props = schema.get('properties', {})
            example = {}
            for key, prop in props.items():
                example[key] = self._get_example_value(prop)
            return example
        
        return {'data': 'test'}
    
    def _get_example_value(self, prop: Dict):
        """Get example value for a schema property."""
        prop_type = prop.get('type', 'string')
        
        if prop_type == 'string':
            return 'test'
        elif prop_type == 'integer' or prop_type == 'number':
            return 1
        elif prop_type == 'boolean':
            return True
        elif prop_type == 'array':
            return []
        elif prop_type == 'object':
            return {}
        else:
            return None
    
    def _generate_schema_assertions(self, schema: Optional[Dict]) -> str:
        """Generate expect assertions for response schema."""
        if not schema:
            return "expect(response.body).toBeDefined();"
        
        schema_type = schema.get('type')
        
        if schema_type == 'array':
            return "expect(Array.isArray(response.body)).toBe(true);"
        elif schema_type == 'object':
            props = schema.get('properties', {})
            assertions = []
            for key in list(props.keys())[:3]:  # First 3 properties
                assertions.append(f"expect(response.body).toHaveProperty('{key}');")
            return '\\n        '.join(assertions) if assertions else "expect(response.body).toBeDefined();"
        else:
            return "expect(response.body).toBeDefined();"


def main():
    parser = argparse.ArgumentParser(description='Generate contract tests from swagger.json')
    parser.add_argument('--swagger', required=True, help='Path to swagger.json / openapi.json')
    parser.add_argument('--output', required=True, help='Output directory for test files')
    parser.add_argument('--base-url', default='http://localhost:3000', help='API base URL for testing')
    args = parser.parse_args()
    
    print('📋 Contract Test Generator v1.0')
    print('=' * 50)
    
    # Parse swagger
    swagger_parser = SwaggerParser(Path(args.swagger))
    endpoints = swagger_parser.parse()
    print(f'📄 Parsed {len(endpoints)} endpoints from swagger')
    
    if not endpoints:
        print('⚠️  No endpoints found. Exiting.')
        return 1
    
    # Generate tests
    generator = ContractTestGenerator(args.base_url)
    test_suites = generator.generate_test_suite(endpoints)
    
    # Write test files
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for tag, content in test_suites:
        filename = f'{tag.lower().replace(" ", "-")}.contract.spec.ts'
        test_file = output_dir / filename
        test_file.write_text(content, encoding='utf-8')
        print(f'✅ Generated: {filename}')
    
    print(f'\\n📊 Generated {len(test_suites)} contract test files')
    print(f'\\n✅ Run tests with: npx jest --testMatch="**/*.contract.spec.ts"')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
