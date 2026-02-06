---
name: migration-rules
description: Mandatory rules and conventions for VB6 → Angular migration. ZONELESS Angular.
---

# Migration Rules v3.0 (Zoneless Angular)

## 📋 Naming Conventions

### Files
| VB6 | Angular | Example |
|-----|---------|---------|
| `FrmClientes` | `clientes.component.ts` | Kebab-case, singular |
| `ModUtils` | `utils.service.ts` | Service suffix |
| `ClsPersona` | `persona.model.ts` | Model suffix |

### Variables
| VB6 | TypeScript | Example |
|-----|------------|---------|
| `strNombre` | `nombre: string` | No Hungarian prefix |
| `intCantidad` | `cantidad: number` | CamelCase |
| `blnActivo` | `activo: boolean` | Explicit types |

### Functions
| VB6 | Angular | Location |
|-----|---------|----------|
| `Public Function` in `.bas` | `method()` in Service | `*.service.ts` |
| `Private Sub` in `.frm` | `private method()` | `*.component.ts` |

---

## 🔒 Security Rules

### Prohibited
| ❌ NO | ✅ YES | Reason |
|-------|--------|--------|
| Hardcoded credentials | Environment variables | Security |
| Dynamic SQL with concatenation | Prisma parameterized | SQL Injection |
| `On Error Resume Next` | Explicit `try/catch` | Debugging |
| Hardcoded `App.Path` | Relative configuration | Portability |

### Required
- JWT tokens in `localStorage` with expiration
- HTTPS in production
- Validation on frontend AND backend
- User input sanitization

---

## 🏗️ Architecture Rules (ZONELESS Angular)

### Frontend (Angular 21 - Zoneless)
| Rule | Description |
|------|-------------|
| **Zoneless Change Detection** | Use `provideExperimentalZonelessChangeDetection()` - NO Zone.js! |
| **OnPush MANDATORY** | Every component MUST use `changeDetection: ChangeDetectionStrategy.OnPush` |
| **Standalone Components** | NEVER use NgModules |
| **Signals for ALL state** | Never use plain variables for component state |
| Reactive Forms | Template-driven forms prohibited |
| MatDialog for modals | Don't use routes for edit forms |
| Lucide for icons | Material Icons as alternative |

### Zoneless Prohibited
| ❌ Prohibited | ✅ Alternative |
|---------------|----------------|
| `import 'zone.js'` | `provideExperimentalZonelessChangeDetection()` |
| `ChangeDetectionStrategy.Default` | `ChangeDetectionStrategy.OnPush` |
| Plain variables for state | `signal()` |
| `ngOnInit` for data loading | Constructor + `effect()` |
| `setTimeout` / `setInterval` | `signal.set()` + `effect()` |
| `implements OnInit` | Direct constructor initialization |

### Backend (Express)
| Rule | Description |
|------|-------------|
| Prisma required | No raw SQL |
| Thin controllers | Logic in Services |
| Centralized error handling | `errorMiddleware` |
| Pino for logging | `console.log` prohibited |


---

## 📊 Data Rules

### Type Migration
| Access/VB6 | SQLite | TypeScript | Prisma |
|------------|--------|------------|--------|
| `Long` | `INTEGER` | `number` | `Int` |
| `Double` | `REAL` | `number` | `Float` |
| `String` | `TEXT` | `string` | `String` |
| `Date` | `TEXT (ISO)` | `Date` | `DateTime` |
| `Currency` | `REAL` | `number` | `Decimal` |
| `Boolean` | `INTEGER (0/1)` | `boolean` | `Boolean` |
| `Null` | `NULL` | `\| null` | `?` |

### Integrity
- All IDs are `autoincrement`
- Foreign Keys required
- Indexes on frequently searched fields
- Cascade delete only if logically correct

---

## ✅ Quality Rules

### Code
- ESLint + Prettier required
- 0 errors from `ng lint` and `tsc --noEmit`
- Comments only for complex logic
- Descriptive names (no abbreviations)

### Testing (MANDATORY)
| Metric | Minimum | Enforcement |
|--------|---------|-------------|
| Line Coverage | 80% | Jest `--coverage` |
| Branch Coverage | 70% | Jest `--coverage` |
| E2E Flow Coverage | 100% | All VB6 flows must have Playwright tests |
| Critical Path Tests | Required | Login, main CRUD, workflows |

### Testing Tools
| Layer | Tool | Purpose |
|-------|------|---------|
| Unit Backend | Jest | Services, Controllers |
| Unit Frontend | Jest + TestBed | Components, Services |
| E2E | Playwright | Full user flows |
| Coverage | Istanbul/c8 | Threshold enforcement |

### Testing Requirements
1. Every VB6 form MUST have corresponding E2E tests
2. Every backend service MUST have unit tests
3. Every Angular component with logic MUST have unit tests
4. Tests MUST be generated automatically from VB6 analysis
5. Coverage reports MUST be generated in `analysis/coverage/`
6. NO deployment without passing all tests

### Git
- Descriptive commits (not "fix", "update")
- 1 feature = 1 branch
- PR required for `main`
- CI must run tests before merge

---

## 🚫 Prohibited Patterns

| ❌ Prohibited | ✅ Alternative |
|---------------|----------------|
| `import 'zone.js'` | `provideExperimentalZonelessChangeDetection()` |
| `@NgModule` | Standalone components |
| `any` in TypeScript | Explicit types |
| `innerHTML` with user input | Angular binding `[innerText]` |
| Nested callbacks | Async/await or RxJS |
| `setTimeout` for sync | Signals + effects |
| Global variables | Services with `providedIn: 'root'` |
| `implements OnInit` for data | Constructor initialization |
| Plain class properties for state | `signal()` |

