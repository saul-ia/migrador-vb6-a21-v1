#!/usr/bin/env python3
"""
VB6 SQL Schema Extractor
========================
Extracts database schema from embedded SQL in VB6 code:
- Table names from queries
- Column names and types (inferred)
- Relationships (from JOINs)
- CRUD operations per table
Helps plan the database migration layer.
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

PATTERNS = {
    # SQL SELECT
    'select': re.compile(
        r'SELECT\s+(.+?)\s+FROM\s+(\w+)',
        re.IGNORECASE | re.DOTALL
    ),
    
    # SQL INSERT
    'insert': re.compile(
        r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)',
        re.IGNORECASE
    ),
    
    # SQL UPDATE
    'update': re.compile(
        r'UPDATE\s+(\w+)\s+SET\s+(.+?)(?:WHERE|$)',
        re.IGNORECASE | re.DOTALL
    ),
    
    # SQL DELETE
    'delete': re.compile(
        r'DELETE\s+FROM\s+(\w+)',
        re.IGNORECASE
    ),
    
    # SQL JOIN
    'join': re.compile(
        r'(?:INNER|LEFT|RIGHT|OUTER)?\s*JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',
        re.IGNORECASE
    ),
    
    # WHERE clause columns
    'where_column': re.compile(
        r'WHERE\s+.*?(\w+)\s*(?:=|<|>|LIKE|IN)',
        re.IGNORECASE
    ),
    
    # ORDER BY columns
    'order_by': re.compile(
        r'ORDER\s+BY\s+([\w\s,]+)',
        re.IGNORECASE
    ),
    
    # Recordset field access
    'rs_field': re.compile(
        r'rs!(\w+)|rs\("(\w+)"\)|rs\.Fields\("(\w+)"\)',
        re.IGNORECASE
    ),
    
    # Connection string for database type
    'connection': re.compile(
        r'(?:Provider|Driver)\s*=\s*([^;"\s]+)',
        re.IGNORECASE
    ),
    
    # Data Source
    'data_source': re.compile(
        r'Data\s*Source\s*=\s*([^;"\s]+)',
        re.IGNORECASE
    )
}


class VB6SchemaExtractor:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.tables = defaultdict(lambda: {
            'columns': set(),
            'primary_key': None,
            'foreign_keys': [],
            'operations': set(),
            'sources': set()
        })
        self.relationships = []
        self.database_type = None
        self.data_sources = set()
        
    def analyze(self):
        """Main analysis entry point."""
        print(f"🗄️ Extracting schema from: {self.source_dir}")
        
        for root, _, files in os.walk(self.source_dir):
            for filename in files:
                filepath = Path(root) / filename
                ext = filepath.suffix.lower()
                
                if ext in ['.frm', '.bas', '.cls', '.ctl']:
                    self._analyze_file(filepath)
        
        # Convert sets to lists for JSON
        tables_dict = {}
        for table, info in self.tables.items():
            tables_dict[table] = {
                'columns': list(info['columns']),
                'primary_key': info['primary_key'],
                'foreign_keys': info['foreign_keys'],
                'operations': list(info['operations']),
                'sources': list(info['sources'])
            }
        
        results = {
            'summary': {
                'total_tables': len(self.tables),
                'total_relationships': len(self.relationships),
                'database_type': self.database_type,
                'data_sources': list(self.data_sources)
            },
            'tables': tables_dict,
            'relationships': self.relationships,
            'migration_recommendations': self._generate_recommendations()
        }
        
        return results
    
    def _analyze_file(self, filepath):
        """Analyze a single file for SQL patterns."""
        content = self._read_file(filepath)
        if not content:
            return
        
        source = str(filepath.name)
        
        # Detect database type
        for match in PATTERNS['connection'].finditer(content):
            provider = match.group(1)
            if 'jet' in provider.lower() or 'ace' in provider.lower():
                self.database_type = 'Access'
            elif 'sqlserver' in provider.lower() or 'sqlncli' in provider.lower():
                self.database_type = 'SQL Server'
            elif 'oracle' in provider.lower():
                self.database_type = 'Oracle'
            elif 'mysql' in provider.lower():
                self.database_type = 'MySQL'
        
        # Detect data sources
        for match in PATTERNS['data_source'].finditer(content):
            self.data_sources.add(match.group(1))
        
        # Parse SELECT statements
        for match in PATTERNS['select'].finditer(content):
            columns_str = match.group(1).strip()
            table = match.group(2).strip().lower()
            
            self.tables[table]['operations'].add('READ')
            self.tables[table]['sources'].add(source)
            
            # Extract columns
            if columns_str != '*':
                columns = [c.strip().split('.')[-1].split(' ')[0] 
                          for c in columns_str.split(',')]
                for col in columns:
                    if col and col.lower() not in ['as', 'distinct']:
                        self.tables[table]['columns'].add(col.lower())
        
        # Parse INSERT statements
        for match in PATTERNS['insert'].finditer(content):
            table = match.group(1).strip().lower()
            columns_str = match.group(2).strip()
            
            self.tables[table]['operations'].add('CREATE')
            self.tables[table]['sources'].add(source)
            
            columns = [c.strip().lower() for c in columns_str.split(',')]
            for col in columns:
                self.tables[table]['columns'].add(col)
        
        # Parse UPDATE statements
        for match in PATTERNS['update'].finditer(content):
            table = match.group(1).strip().lower()
            set_clause = match.group(2).strip()
            
            self.tables[table]['operations'].add('UPDATE')
            self.tables[table]['sources'].add(source)
            
            # Extract column names from SET clause
            set_parts = set_clause.split(',')
            for part in set_parts:
                if '=' in part:
                    col = part.split('=')[0].strip().lower()
                    self.tables[table]['columns'].add(col)
        
        # Parse DELETE statements
        for match in PATTERNS['delete'].finditer(content):
            table = match.group(1).strip().lower()
            self.tables[table]['operations'].add('DELETE')
            self.tables[table]['sources'].add(source)
        
        # Parse JOINs for relationships
        for match in PATTERNS['join'].finditer(content):
            joined_table = match.group(1).lower()
            table1 = match.group(2).lower()
            col1 = match.group(3).lower()
            table2 = match.group(4).lower()
            col2 = match.group(5).lower()
            
            self.relationships.append({
                'from_table': table1,
                'from_column': col1,
                'to_table': table2,
                'to_column': col2,
                'type': 'JOIN'
            })
            
            # Infer foreign keys
            if col1.lower().endswith('id') and table1 != joined_table:
                self.tables[table1]['foreign_keys'].append({
                    'column': col1,
                    'references_table': joined_table,
                    'references_column': col2
                })
        
        # Parse recordset field access
        for match in PATTERNS['rs_field'].finditer(content):
            field = match.group(1) or match.group(2) or match.group(3)
            if field:
                # Add to all tables found in this file
                for table_info in self.tables.values():
                    if source in table_info['sources']:
                        table_info['columns'].add(field.lower())
        
        # Infer primary keys (columns named Id, or TableNameId)
        for table, info in self.tables.items():
            for col in info['columns']:
                if col == 'id' or col == f'{table}id' or col == f'{table}_id':
                    info['primary_key'] = col
    
    def _generate_recommendations(self):
        """Generate migration recommendations."""
        recommendations = []
        
        # Full CRUD tables
        full_crud = [t for t, info in self.tables.items() 
                     if info['operations'] == {'CREATE', 'READ', 'UPDATE', 'DELETE'}]
        if full_crud:
            recommendations.append({
                'type': 'FULL_CRUD',
                'tables': full_crud,
                'recommendation': 'These tables need complete REST API endpoints (GET, POST, PUT, DELETE)'
            })
        
        # Read-only tables
        read_only = [t for t, info in self.tables.items() 
                     if info['operations'] == {'READ'}]
        if read_only:
            recommendations.append({
                'type': 'READ_ONLY',
                'tables': read_only,
                'recommendation': 'Consider as lookup/reference tables - may only need GET endpoint'
            })
        
        # Tables without primary key
        no_pk = [t for t, info in self.tables.items() if not info['primary_key']]
        if no_pk:
            recommendations.append({
                'type': 'NO_PRIMARY_KEY',
                'tables': no_pk,
                'recommendation': '⚠️ Add primary key during migration for proper REST resource identification'
            })
        
        return recommendations
    
    def _read_file(self, filepath):
        """Read file with proper encoding."""
        for enc in ['utf-8', 'latin1', 'cp1252']:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    return f.read()
            except:
                continue
        return None
    
    def generate_prisma_schema(self, results, output_path):
        """Generate a draft Prisma schema from extracted tables."""
        lines = ['// Auto-generated Prisma schema from VB6 code analysis', 
                 '// Review and adjust types as needed', '', 
                 'datasource db {', '  provider = "sqlite"', 
                 '  url = env("DATABASE_URL")', '}', '',
                 'generator client {', '  provider = "prisma-client-js"', '}', '']
        
        for table, info in results['tables'].items():
            lines.append(f'model {table.capitalize()} {{')
            
            # Add primary key if found
            pk = info.get('primary_key')
            if pk:
                lines.append(f'  {pk} Int @id @default(autoincrement())')
            else:
                lines.append('  id Int @id @default(autoincrement())')
            
            # Add other columns
            for col in info['columns']:
                if col != pk and col != 'id':
                    lines.append(f'  {col} String?  // TODO: verify type')
            
            lines.append('}')
            lines.append('')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description="VB6 SQL Schema Extractor")
    parser.add_argument("source_dir", help="Directory containing VB6 source code")
    parser.add_argument("-o", "--output", default="vb6_schema.json", help="Output JSON file")
    parser.add_argument("--prisma", help="Generate draft Prisma schema file")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.source_dir):
        print(f"❌ Error: Directory not found: {args.source_dir}")
        return 1
    
    extractor = VB6SchemaExtractor(args.source_dir)
    results = extractor.analyze()
    
    # Save JSON
    indent = 2 if args.pretty else None
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=indent, ensure_ascii=False)
    
    # Generate Prisma schema if requested
    if args.prisma:
        extractor.generate_prisma_schema(results, args.prisma)
        print(f"   📝 Prisma schema: {args.prisma}")
    
    print(f"✅ Schema extraction complete: {args.output}")
    print(f"   🗄️ Tables found: {results['summary']['total_tables']}")
    print(f"   🔗 Relationships: {results['summary']['total_relationships']}")
    print(f"   💾 Database type: {results['summary']['database_type'] or 'Unknown'}")
    
    return 0


if __name__ == "__main__":
    exit(main())
