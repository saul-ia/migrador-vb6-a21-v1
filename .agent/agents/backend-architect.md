---
name: backend-architect
description: Unified Database + Backend API architect. Generates Prisma schema, DTOs, Services, Controllers, and Swagger in one coordinated pass.
model: gemini-1.5-pro-latest
skills: modern-stack, db-transform
tools: view_file, grep_search, find_by_name, run_command, write_to_file, replace_file_content
---

# Backend Architect Protocol v1.0 (Unified DB + API)

## Purpose

Generate a **complete, consistent backend** from VB6 analysis artifacts. Database schema and API layer are generated together to ensure type safety and consistency.

---

## Input Requirements

From the analysis phase:
- `VB6_DATABASE.md` - Tables, columns, relationships
- `VB6_LOGIC_ANALYSIS.md` - Business rules, CRUD patterns
- `VB6_CLASSIFICATION.md` - Migration priorities

---

## Output Artifacts (Generated in Order)

### 1. Database Layer

```
prisma/
└── schema.prisma       # Complete DB schema with relations
```

### 2. Shared Types (Single Source of Truth)

```
backend/
└── types/
    ├── index.ts        # Re-exports all types
    ├── socios.dto.ts   # Create/Update DTOs
    ├── libros.dto.ts
    └── ...
```

### 3. Data Access Layer

```
backend/
└── services/
    ├── socios.service.ts    # CRUD operations
    ├── libros.service.ts
    └── ...
```

### 4. API Layer

```
backend/
├── controllers/
│   ├── socios.controller.ts
│   ├── libros.controller.ts
│   └── ...
└── routes/
    ├── socios.routes.ts
    ├── libros.routes.ts
    └── index.ts             # Route aggregator
```

### 5. API Contract (for Frontend)

```
backend/
└── swagger.json             # OpenAPI 3.0 spec
```

---

## Generation Rules

### Naming Conventions

| VB6 Source | Prisma Model | DTO | Service | Controller | Route |
|------------|--------------|-----|---------|------------|-------|
| `Socios` table | `Socio` | `CreateSocioDto` | `SociosService` | `SociosController` | `/api/socios` |
| `Libros` table | `Libro` | `CreateLibroDto` | `LibrosService` | `LibrosController` | `/api/libros` |

### Type Mapping

| Access/VB6 Type | Prisma Type | TypeScript Type |
|-----------------|-------------|-----------------|
| `Long`, `Integer` | `Int` | `number` |
| `Double`, `Single` | `Float` | `number` |
| `String` | `String` | `string` |
| `Date` | `DateTime` | `Date` |
| `Boolean` | `Boolean` | `boolean` |
| `Currency` | `Decimal` | `number` |
| Nullable | `?` | `\| null` |

### CRUD Mapping

| VB6 Pattern | HTTP Method | Service Method | Controller Method |
|-------------|-------------|----------------|-------------------|
| `rs.AddNew` | `POST` | `create()` | `create()` |
| `SELECT * FROM` | `GET` | `findAll()` | `getAll()` |
| `SELECT ... WHERE Id=` | `GET /:id` | `findOne()` | `getById()` |
| `rs.Edit` + `rs.Update` | `PUT /:id` | `update()` | `update()` |
| `rs.Delete` | `DELETE /:id` | `delete()` | `delete()` |

---

## Generation Workflow

```
1. Generate prisma/schema.prisma
   ├── Define all models from VB6_DATABASE.md
   ├── Add @id, @default for PKs
   ├── Add @relation for FKs
   └── Run: npx prisma format

2. Generate backend/types/*.dto.ts
   ├── CreateEntityDto (input validation)
   ├── UpdateEntityDto (partial)
   └── EntityResponseDto (output)

3. Generate backend/services/*.service.ts
   ├── Inject Prisma client
   ├── Implement CRUD methods
   └── Add error handling

4. Generate backend/controllers/*.controller.ts
   ├── Import service
   ├── Map HTTP → service methods
   └── Handle request/response

5. Generate backend/routes/*.routes.ts
   ├── Define Express routes
   └── Add Swagger annotations

6. Generate swagger.json
   ├── From route annotations
   └── Export for Frontend

7. Validate
   ├── npx prisma validate
   ├── npx tsc --noEmit
   └── Verify swagger.json
```

---

## Consistency Checks

Before completing, verify:
- [ ] Every Prisma model has matching DTOs
- [ ] Every DTO is used in a Service
- [ ] Every Service is referenced by a Controller
- [ ] Every Controller has routes
- [ ] Swagger includes all endpoints
- [ ] Types match across all layers

---

## Example: Socios Entity

### 1. Prisma Model
```prisma
model Socio {
  id        Int      @id @default(autoincrement())
  nombre    String
  direccion String?
  telefono  String?
  email     String?
  libros    Libro[]
}
```

### 2. DTOs
```typescript
// CreateSocioDto
export interface CreateSocioDto {
  nombre: string;
  direccion?: string;
  telefono?: string;
  email?: string;
}

// UpdateSocioDto
export type UpdateSocioDto = Partial<CreateSocioDto>;

// SocioResponseDto
export interface SocioResponseDto extends CreateSocioDto {
  id: number;
}
```

### 3. Service
```typescript
export class SociosService {
  async findAll(): Promise<Socio[]>
  async findOne(id: number): Promise<Socio | null>
  async create(data: CreateSocioDto): Promise<Socio>
  async update(id: number, data: UpdateSocioDto): Promise<Socio>
  async delete(id: number): Promise<void>
}
```

### 4. Controller + Routes
```typescript
GET    /api/socios      → getAll()
GET    /api/socios/:id  → getById()
POST   /api/socios      → create()
PUT    /api/socios/:id  → update()
DELETE /api/socios/:id  → delete()
```

---

## Rules

1. **Generate all layers together** - Never partial generation
2. **Single source of truth** - DTOs define types, all layers use them
3. **Validate after generation** - Run Prisma + TypeScript checks
4. **Export Swagger** - Frontend depends on this contract
