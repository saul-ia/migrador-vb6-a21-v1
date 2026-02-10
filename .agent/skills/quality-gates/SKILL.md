---
name: quality-gates
description: Validation rules to ensure migration quality. Includes Jest unit testing and coverage enforcement.
---

# Quality Gates Skill

## Purpose
Ensure migrated applications meet quality standards through automated testing and coverage validation.

---

## 1. Coverage Thresholds

| Metric | Minimum | Target | Enforcement |
|--------|---------|--------|-------------|
| Line Coverage | 80% | 90% | Block deployment if < 80% |
| Branch Coverage | 70% | 85% | Warning if < 70% |
| Function Coverage | 80% | 90% | Block deployment if < 80% |
| Statement Coverage | 80% | 90% | Block deployment if < 80% |

---

## 2. Jest Configuration

### Backend (Express + TypeScript)
```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: ['**/*.spec.ts', '**/*.test.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/index.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  coverageDirectory: '../analysis/coverage/backend',
  coverageReporters: ['html', 'text', 'lcov']
};
```

### Frontend (Angular)
```javascript
// jest.config.js
module.exports = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/setup-jest.ts'],
  testMatch: ['**/*.spec.ts'],
  collectCoverageFrom: [
    'src/app/**/*.ts',
    '!src/app/**/*.module.ts',
    '!src/main.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  coverageDirectory: '../analysis/coverage/frontend',
  coverageReporters: ['html', 'text', 'lcov']
};
```

---

## 3. Unit Test Patterns

### Service Test Template (Backend)
```typescript
import { describe, it, expect, jest, beforeEach } from '@jest/globals';
import { {{ServiceName}} } from '../src/services/{{serviceName}}.service';
import { prisma } from '../src/lib/prisma';

// Mock Prisma
jest.mock('../src/lib/prisma', () => ({
  prisma: {
    {{entityLower}}: {
      findMany: jest.fn(),
      findUnique: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
    }
  }
}));

describe('{{ServiceName}}', () => {
  let service: {{ServiceName}};

  beforeEach(() => {
    service = new {{ServiceName}}();
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should return all {{entities}}', async () => {
      const mockData = [{ id: 1, name: 'Test' }];
      (prisma.{{entityLower}}.findMany as jest.Mock).mockResolvedValue(mockData);
      
      const result = await service.getAll();
      
      expect(result).toEqual(mockData);
      expect(prisma.{{entityLower}}.findMany).toHaveBeenCalled();
    });
  });

  describe('getById', () => {
    it('should return {{entity}} by id', async () => {
      const mockItem = { id: 1, name: 'Test' };
      (prisma.{{entityLower}}.findUnique as jest.Mock).mockResolvedValue(mockItem);
      
      const result = await service.getById(1);
      
      expect(result).toEqual(mockItem);
      expect(prisma.{{entityLower}}.findUnique).toHaveBeenCalledWith({
        where: { id: 1 }
      });
    });

    it('should return null for non-existent id', async () => {
      (prisma.{{entityLower}}.findUnique as jest.Mock).mockResolvedValue(null);
      
      const result = await service.getById(999);
      
      expect(result).toBeNull();
    });
  });

  describe('create', () => {
    it('should create new {{entity}}', async () => {
      const newItem = { name: 'New Item' };
      const createdItem = { id: 1, ...newItem };
      (prisma.{{entityLower}}.create as jest.Mock).mockResolvedValue(createdItem);
      
      const result = await service.create(newItem);
      
      expect(result).toEqual(createdItem);
      expect(prisma.{{entityLower}}.create).toHaveBeenCalledWith({
        data: newItem
      });
    });
  });

  describe('update', () => {
    it('should update existing {{entity}}', async () => {
      const updateData = { name: 'Updated' };
      const updatedItem = { id: 1, ...updateData };
      (prisma.{{entityLower}}.update as jest.Mock).mockResolvedValue(updatedItem);
      
      const result = await service.update(1, updateData);
      
      expect(result).toEqual(updatedItem);
    });
  });

  describe('delete', () => {
    it('should delete {{entity}}', async () => {
      (prisma.{{entityLower}}.delete as jest.Mock).mockResolvedValue({ id: 1 });
      
      await service.delete(1);
      
      expect(prisma.{{entityLower}}.delete).toHaveBeenCalledWith({
        where: { id: 1 }
      });
    });
  });
});
```

### Controller Test Template (Backend)
```typescript
import request from 'supertest';
import { app } from '../src/app';

describe('{{Entity}} Controller', () => {
  describe('GET /api/{{entities}}', () => {
    it('should return all {{entities}}', async () => {
      const response = await request(app)
        .get('/api/{{entities}}')
        .expect(200);
      
      expect(Array.isArray(response.body)).toBe(true);
    });
  });

  describe('GET /api/{{entities}}/:id', () => {
    it('should return {{entity}} by id', async () => {
      const response = await request(app)
        .get('/api/{{entities}}/1')
        .expect(200);
      
      expect(response.body).toHaveProperty('id');
    });

    it('should return 404 for non-existent {{entity}}', async () => {
      await request(app)
        .get('/api/{{entities}}/99999')
        .expect(404);
    });
  });

  describe('POST /api/{{entities}}', () => {
    it('should create new {{entity}}', async () => {
      const newItem = { /* valid data */ };
      
      const response = await request(app)
        .post('/api/{{entities}}')
        .send(newItem)
        .expect(201);
      
      expect(response.body).toHaveProperty('id');
    });

    it('should return 400 for invalid data', async () => {
      await request(app)
        .post('/api/{{entities}}')
        .send({})
        .expect(400);
    });
  });

  describe('PUT /api/{{entities}}/:id', () => {
    it('should update {{entity}}', async () => {
      const updateData = { /* valid data */ };
      
      await request(app)
        .put('/api/{{entities}}/1')
        .send(updateData)
        .expect(200);
    });
  });

  describe('DELETE /api/{{entities}}/:id', () => {
    it('should delete {{entity}}', async () => {
      await request(app)
        .delete('/api/{{entities}}/1')
        .expect(204);
    });
  });
});
```

### Angular Component Test Template
```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { {{ComponentName}} } from './{{componentName}}.component';
import { {{ServiceName}} } from '../../services/{{serviceName}}.service';

describe('{{ComponentName}}', () => {
  let component: {{ComponentName}};
  let fixture: ComponentFixture<{{ComponentName}}>;
  let mockService: jest.Mocked<{{ServiceName}}>;

  beforeEach(async () => {
    mockService = {
      getAll: jest.fn().mockResolvedValue([]),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
    } as any;

    await TestBed.configureTestingModule({
      imports: [{{ComponentName}}],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: {{ServiceName}}, useValue: mockService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent({{ComponentName}});
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load data on init', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    
    expect(mockService.getAll).toHaveBeenCalled();
  });

  it('should display loading state', () => {
    component.loading.set(true);
    fixture.detectChanges();
    
    const loadingElement = fixture.nativeElement.querySelector('.loading');
    expect(loadingElement).toBeTruthy();
  });

  it('should display data when loaded', async () => {
    mockService.getAll.mockResolvedValue([{ id: 1, name: 'Test' }]);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
    
    const listItems = fixture.nativeElement.querySelectorAll('.list-item, tr');
    expect(listItems.length).toBeGreaterThan(0);
  });
});
```

---

## 4. Running Tests

### Commands
```bash
# Run backend unit tests
cd apps/backend && npm test

# Run frontend unit tests  
cd apps/frontend && npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- --testPathPattern="cliente.spec"

# Watch mode during development
npm test -- --watch
```

---

## 5. Coverage Reports

### Generate Reports
```bash
# Backend coverage
cd apps/backend && npm test -- --coverage --coverageReporters=html

# Frontend coverage
cd apps/frontend && npm test -- --coverage --coverageReporters=html
```

### Output Locations
- Backend: `analysis/coverage/backend/index.html`
- Frontend: `analysis/coverage/frontend/index.html`
- Combined: `analysis/coverage/lcov-report/index.html`

---

## 6. Validation Script

Run coverage validation:
```bash
python .agent/skills/quality-gates/scripts/coverage_validator.py \
  --backend analysis/coverage/backend/coverage-summary.json \
  --frontend analysis/coverage/frontend/coverage-summary.json \
  --threshold 80 \
  --output analysis/coverage-report.md
```

Output:
- ✅ PASS if all thresholds met
- ❌ FAIL with specific gaps if thresholds not met
- 📊 Summary report in markdown

---

## 7. Unit Test Generator 🧪

### Purpose
Automatically generate Jest test skeletons for components, services, and controllers. Reduces manual test writing effort and ensures 80%+ coverage baseline.

### Usage

```bash
# Generate all tests (frontend + backend)
python .agent/skills/quality-gates/scripts/unit_test_generator.py \
  --input ${OUTPUT_DIR} \
  --type all \
  --coverage-threshold 80

# Frontend only
python .agent/skills/quality-gates/scripts/unit_test_generator.py \
  --input ${OUTPUT_DIR} \
  --type frontend

# Backend only
python .agent/skills/quality-gates/scripts/unit_test_generator.py \
  --input ${OUTPUT_DIR} \
  --type backend
```

### What It Generates

**For Angular Components:**
- TestBed configuration with mock providers
- Basic creation test
- Tests for public methods
- Lifecycle hook tests (ngOnInit, etc.)

**For Angular Services:**
- Mock HttpClient spy
- Dependency injection mocks
- Tests for all public methods
- Proper async/await handling

**For Express Controllers:**
- Mock request/response objects
- Tests for all route handlers
- Status code assertions
- Basic validation tests

### Output

Generates `*.spec.ts` files alongside source files:
```
src/
  app/
    components/
      users/
        users.component.ts
        users.component.spec.ts  ← Generated
    services/
      auth/
        auth.service.ts
        auth.service.spec.ts     ← Generated
```

### After Generation

1. Run tests: `npm test`
2. Check coverage: `npm test -- --coverage`
3. Refine test assertions as needed
4. Add edge case tests manually

---

## 8. Integration with CI/CD

### GitHub Actions Example
```yaml
name: Quality Gates

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '24'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run unit tests
        run: npm test -- --coverage
        

      - name: Validate coverage
        run: |
          python .agent/skills/quality-gates/scripts/coverage_validator.py \
            --threshold 80
            
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```
