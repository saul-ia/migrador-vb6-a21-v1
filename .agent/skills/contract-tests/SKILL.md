---
name: contract-tests
description: Validates frontend-backend API contract synchronization using swagger.json as source of truth.
---

# Contract Tests Skill v1.0

## Purpose

Ensures that the Angular frontend services are **synchronized** with the Express backend API.
Uses `swagger.json` as the single source of truth for the API contract.

## Problem This Solves

```
Backend generates:  POST /api/libros  { titulo, autor, isbn }
Frontend calls:     POST /api/libros  { title, author, isbn }   ← MISMATCH!
```

Without contract tests, this mismatch is only discovered at runtime.

## How It Works

1. **Parse swagger.json** — Extract all endpoints, methods, and request/response schemas
2. **Scan Angular services** — Extract all HttpClient calls (URLs, methods, payloads)
3. **Compare** — Find mismatches in:
   - Missing endpoints (frontend calls API that doesn't exist)
   - Wrong HTTP methods (frontend uses POST, backend expects PUT)
   - Missing fields in request body
   - Wrong field types
   - Missing query parameters

## Checks

| ID | Check | Severity |
|----|-------|----------|
| CT-001 | Frontend calls non-existent endpoint | CRITICAL |
| CT-002 | HTTP method mismatch | CRITICAL |
| CT-003 | Request body field mismatch | WARNING |
| CT-004 | Response field not used by frontend | INFO |
| CT-005 | Backend endpoint not called by any service | INFO |
| CT-006 | URL path mismatch (typo) | CRITICAL |

## Usage

```bash
python .agent/skills/contract-tests/scripts/contract_validator.py \
  --swagger ${OUTPUT_DIR}/swagger.json \
  --services ${OUTPUT_DIR}/apps/frontend/src/app/services \
  --output ${ANALYSIS_DIR}/contract-report.json \
  --html ${ANALYSIS_DIR}/CONTRACT_REPORT.html
```

## Output

- `${ANALYSIS_DIR}/contract-report.json` — Machine-readable results
- `${ANALYSIS_DIR}/CONTRACT_REPORT.html` — Visual HTML report

---

## Contract Test Generator 📋

### Purpose
Automatically generate **executable** Jest/Supertest contract tests from `swagger.json`. These tests validate that API endpoints actually work as documented.

### Usage

```bash
python .agent/skills/contract-tests/scripts/contract_test_generator.py \
  --swagger ${OUTPUT_DIR}/apps/backend/swagger.json \
  --output ${OUTPUT_DIR}/tests/contract \
  --base-url http://localhost:3000
```

### What It Generates

For each API endpoint in swagger.json, generates:

**Test File Structure:**
```typescript
describe('Contract Tests: Users', () => {
  describe('GET /api/users', () => {
    it('should return 200 - Get all users', async () => {
      const response = await request(baseUrl).get('/api/users');
      expect(response.status).toBe(200);
      expect(response.body).toBeDefined();
    });

    it('should match response schema', async () => {
      const response = await request(baseUrl).get('/api/users');
      expect(Array.isArray(response.body)).toBe(true);
    });
  });
});
```

### Generated Tests Include

- ✅ HTTP method validation
- ✅ Status code assertions (200, 201, 404, etc.)
- ✅ Response schema validation
- ✅ Path parameter substitution
- ✅ Query parameter handling
- ✅ Request body examples
- ✅ Auth token support (commented out, enable if needed)

### Output

Generates `*.contract.spec.ts` files grouped by tags:
```
tests/
  contract/
    users.contract.spec.ts
    books.contract.spec.ts
    loans.contract.spec.ts
```

### Running Contract Tests

```bash
# Run all contract tests
npx jest --testMatch="**/contract/**/*.spec.ts"

# Run specific tag
npx jest --testMatch="**/contract/users.contract.spec.ts"

# With coverage
npx jest --testMatch="**/contract/**/*.spec.ts" --coverage
```

### Integration Flow

1. **Generate swagger.json** from Express routes
2. **Run test generator** to create test files
3. **Start backend server** (must be running)
4. **Execute contract tests** with Jest
5. **Fix mismatches** if tests fail

### Benefits

- **Catches API changes** before deployment
- **Documents API behavior** with executable tests
- **Prevents frontend breaks** from backend changes
- **Enforces swagger accuracy** (tests fail if swagger is wrong)
