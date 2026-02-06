---
name: modern-stack
description: Complete specifications and patterns for the target stack (Angular 21, Node 24+, Express 5+, SQLite/Prisma).
allowed-tools: view_file, write_to_file, run_command
---

# Modern Stack Manual v3.0 (Zoneless)

## 📦 Version Requirements

| Technology | Version | Package |
|------------|---------|---------|
| **Angular** | 21+ | `@angular/core` |
| **Angular Material** | 21+ | `@angular/material` |
| **Node.js** | 24+ | runtime |
| **Express** | 5+ | `express` |
| **SQLite** | 3 | `sqlite3` |
| **Prisma** | Latest | `prisma`, `@prisma/client` |
| **Lucide Icons** | Latest | `lucide-angular` |
| **Pino** | Latest | `pino`, `pino-http` |
| **Swagger** | Latest | `swagger-ui-express`, `swagger-jsdoc` |

> [!IMPORTANT]
> **ZONELESS ANGULAR**: This stack uses `provideExperimentalZonelessChangeDetection()` - NO Zone.js required!



# 1. ⚙️ Frontend Specifications

## 1.1 Angular Core Patterns

### Standalone Components (Required - Strict Mode)
```typescript
@Component({
  selector: 'app-members',
  standalone: true,  // ⚠️ MANDATORY - NEVER use NgModules
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    LucideAngularModule
  ],
  templateUrl: './members.component.html',
  styleUrl: './members.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush  // ⚠️ REQUIRED for Zoneless
})
export class MembersComponent {
  // Use Signals for ALL state - Required for Zoneless
  data = signal<Member[]>([]);
  loading = signal<boolean>(false);
  error = signal<string | null>(null);
}
```

### main.ts Bootstrap (ZONELESS - No Zone.js!)
```typescript
// main.ts - ZONELESS Angular 21
// ⚠️ DO NOT import zone.js - We use Zoneless Change Detection!
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';

bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));
```

### app.config.ts (ZONELESS Configuration)
```typescript
// app.config.ts - CRITICAL: Zoneless Setup
import { ApplicationConfig, provideExperimentalZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { routes } from './app.routes';
import { errorInterceptor } from './interceptors/error.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    // ⚠️ CRITICAL: Enable Zoneless Change Detection
    provideExperimentalZonelessChangeDetection(),
    
    provideRouter(routes),
    provideHttpClient(withInterceptors([errorInterceptor])),
    provideAnimationsAsync()
  ]
};
```

> [!CAUTION]
> **ZONELESS REQUIREMENTS:**
> 1. ALL components MUST use `changeDetection: ChangeDetectionStrategy.OnPush`
> 2. ALL state MUST be managed with Signals (never plain variables)
> 3. NEVER use `setTimeout` or `setInterval` for UI updates - use `effect()` instead
> 4. NEVER import `zone.js` anywhere in the application

### Signals for State Management (MANDATORY for Zoneless)

```typescript
// ✅ Correct: Use Signals
data = signal<Member[]>([]);
selectedItem = signal<Member | null>(null);
isLoading = signal(false);

// Computed signals
totalItems = computed(() => this.data().length);

// Effect for side effects
constructor() {
  effect(() => {
    console.log('Data changed:', this.data().length);
  });
}

// ❌ Avoid: BehaviorSubject for component state
```

> [!CAUTION]
> When using `ngModel` inside a `<form>` tag, you **MUST** add a `name` attribute to the input:
> ```html
> <!-- ✅ Correct -->
> <input name="email" [ngModel]="email()" (ngModelChange)="email.set($event)">
> 
> <!-- ❌ Error NG01352 -->
> <input [ngModel]="email()" (ngModelChange)="email.set($event)">
> ```

### VB6 Pattern: Entity Pre-Validation (cmdcons_Click)
VB6 often validates entity state before allowing operations. Migrate this pattern:

```typescript
// VB6: Check if socio has pending loans before new loan
// cmdcons_Click() -> "Este Socio Tiene X libros no devueltos"

clientPendingLoans = signal<Libro[]>([]);
showPendingWarning = signal(false);

async onClientSelected(clienteId: number) {
  this.selectedClienteId.set(clienteId);
  
  const pendingLoans = this.loanedBooks().filter(
    libro => libro.socioId === clienteId
  );
  
  this.clientPendingLoans.set(pendingLoans);
  this.showPendingWarning.set(pendingLoans.length > 0);
}
```

```html
<!-- Show warning like VB6 MsgBox -->
@if (showPendingWarning()) {
<div class="warning-box">
  <span>⚠️</span>
  <strong>Este socio tiene {{ clientPendingLoans().length }} libro(s) no devuelto(s)</strong>
</div>
}
```

### VB6 Pattern: DateAdd Calculation
```typescript
// VB6: DateAdd("d", Val(txtdias), Now())
returnDate = computed(() => {
  const date = new Date();
  date.setDate(date.getDate() + this.dias());
  return date;
});
```

## 1.2 Angular Material + UI

### MatDialog for Modals (VB6 Form Replacement)
```typescript
// Opening dialog
openDialog(item?: Member): void {
  const dialogRef = this.dialog.open(MemberDialogComponent, {
    width: '600px',
    data: item ?? null,
    disableClose: true
  });

  dialogRef.afterClosed().subscribe(result => {
    if (result) {
      this.loadData();
    }
  });
}
```

### Modern Date Picker
```html
<mat-form-field appearance="outline">
  <mat-label>Loan Date</mat-label>
  <input matInput [matDatepicker]="picker" formControlName="loanDate">
  <mat-datepicker-toggle matIconSuffix [for]="picker">
    <lucide-icon name="calendar" matDatepickerToggleIcon></lucide-icon>
  </mat-datepicker-toggle>
  <mat-datepicker #picker></mat-datepicker>
  <mat-error *ngIf="form.get('loanDate')?.hasError('required')">
    Date is required
  </mat-error>
</mat-form-field>
```

### Lucide Icons (Required Library)
```typescript
// app.config.ts
import { LucideAngularModule, icons } from 'lucide-angular';

export const appConfig: ApplicationConfig = {
  providers: [
    importProvidersFrom(LucideAngularModule.pick(icons))
  ]
};

// In templates
<lucide-icon name="plus" size="20"></lucide-icon>
<lucide-icon name="edit" size="20"></lucide-icon>
<lucide-icon name="trash-2" size="20"></lucide-icon>
<lucide-icon name="search" size="20"></lucide-icon>
<lucide-icon name="save" size="20"></lucide-icon>
```

## 1.3 Reactive Forms

### Form Structure
```typescript
export class MemberDialogComponent implements OnInit {
  form = new FormGroup({
    name: new FormControl('', [
      Validators.required,
      Validators.minLength(2),
      Validators.maxLength(100)
    ]),
    email: new FormControl('', [
      Validators.email
    ]),
    phone: new FormControl(''),
    registrationDate: new FormControl(new Date(), Validators.required)
  });

  // Custom validator example
  private validateNotFutureDate(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const date = control.value;
      if (date && date > new Date()) {
        return { futureDate: true };
      }
      return null;
    };
  }
}
```

### Form Template Pattern
```html
<form [formGroup]="form" (ngSubmit)="save()">
  <mat-form-field appearance="outline" class="full-width">
    <mat-label>Name</mat-label>
    <input matInput formControlName="name" placeholder="Full name">
    <mat-error *ngIf="form.get('name')?.hasError('required')">
      Name is required
    </mat-error>
    <mat-error *ngIf="form.get('name')?.hasError('minlength')">
      Minimum 2 characters
    </mat-error>
  </mat-form-field>
  
  <div mat-dialog-actions align="end">
    <button mat-button type="button" (click)="cancel()">
      <lucide-icon name="x" size="18"></lucide-icon>
      Cancel
    </button>
    <button mat-raised-button color="primary" type="submit" [disabled]="!form.valid">
      <lucide-icon name="save" size="18"></lucide-icon>
      Save
    </button>
  </div>
</form>
```

## 1.4 HTTP Client + Error Interceptor

### Service Pattern
```typescript
@Injectable({ providedIn: 'root' })
export class MembersService {
  private readonly apiUrl = '/api/members';

  constructor(private http: HttpClient) {}

  getAll(): Observable<Member[]> {
    return this.http.get<Member[]>(this.apiUrl);
  }

  getById(id: number): Observable<Member> {
    return this.http.get<Member>(`${this.apiUrl}/${id}`);
  }

  create(dto: CreateMemberDto): Observable<Member> {
    return this.http.post<Member>(this.apiUrl, dto);
  }

  update(id: number, dto: UpdateMemberDto): Observable<Member> {
    return this.http.put<Member>(`${this.apiUrl}/${id}`, dto);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
```

### Error Interceptor (HttpInterceptorFn)

#### HTTP Error Codes Reference

| Code | Condition | Name | Description | Interceptor Action |
|------|-----------|------|-------------|-------------------|
| `0` | `!navigator.onLine` | Offline / No Network | No internet connection | 📡 "No internet connection. Check your network." |
| `0` | `navigator.onLine` | Unknown / CORS / Down | Server down or CORS | ⚠️ "Could not contact the server." |
| `400` | N/A | Bad Request | Invalid syntax or malformed JSON | Show `error.message` from backend |
| `401` | N/A | Unauthorized | Expired or missing token | 🔒 Refresh Token or redirect to Login |
| `403` | N/A | Forbidden | No permissions for this resource | ⛔ "You don't have permission for this action." |
| `404` | N/A | Not Found | Resource doesn't exist | Redirect to 404 or show message |
| `405` | N/A | Method Not Allowed | Wrong HTTP method | Log to console (dev error) |
| `408` | N/A | Request Timeout | Client took too long | Suggest retry |
| `409` | N/A | Conflict | Duplicate record | Show specific error in form |
| `422` | N/A | Unprocessable Entity | Validation error | Map errors to form fields |
| `429` | N/A | Too Many Requests | Rate limiting exceeded | ⏳ Block button temporarily |
| `500` | N/A | Internal Server Error | Backend bug | 🔥 "Internal server error. Try again later." |
| `501` | N/A | Not Implemented | Endpoint under construction | Log error |
| `502` | N/A | Bad Gateway | Invalid response from internal service | Ask to retry |
| `503` | N/A | Service Unavailable | Maintenance or overload | 🛠️ "Server under maintenance." |
| `504` | N/A | Gateway Timeout | Backend timeout | "The operation is taking longer than expected." |

#### Complete Error Interceptor Implementation

```typescript
// interceptors/error.interceptor.ts
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const snackBar = inject(MatSnackBar);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let message = 'Unknown error';
      let duration = 5000;
      let shouldNavigate = false;
      let navigateTo = '';

      // Handle offline / network errors (status 0)
      if (error.status === 0) {
        if (!navigator.onLine) {
          message = '📡 No internet connection. Check your network.';
        } else {
          message = '⚠️ Could not contact the server.';
        }
      } else {
        switch (error.status) {
          case 400:
            message = error.error?.message || 'Invalid request.';
            break;
          case 401:
            message = '🔒 Session expired. Please log in again.';
            shouldNavigate = true;
            navigateTo = '/login';
            // TODO: Implement refresh token logic here
            break;
          case 403:
            message = '⛔ You don\'t have permission for this action.';
            break;
          case 404:
            message = 'The requested resource does not exist.';
            break;
          case 405:
            console.error('[DEV] Method Not Allowed:', req.method, req.url);
            message = 'Configuration error (405).';
            break;
          case 408:
            message = 'The request took too long. Please try again.';
            break;
          case 409:
            message = error.error?.message || 'Conflict: record already exists.';
            break;
          case 422:
            // Validation errors - don't show snackbar, let form handle it
            return throwError(() => error);
          case 429:
            message = '⏳ Too many requests. Please wait a moment.';
            duration = 10000;
            break;
          case 500:
            message = '🔥 Internal server error. Try again later.';
            break;
          case 501:
            console.warn('[DEV] Not Implemented:', req.url);
            message = 'Feature not available.';
            break;
          case 502:
            message = 'Connection error with internal services.';
            break;
          case 503:
            message = '🛠️ Server under maintenance. Try again in a few minutes.';
            break;
          case 504:
            message = 'The operation is taking longer than expected.';
            break;
          default:
            message = error.error?.message || `Error ${error.status}`;
        }
      }

      // Show snackbar notification
      snackBar.open(message, 'Close', {
        duration,
        panelClass: error.status >= 500 ? ['error-snackbar-critical'] : ['error-snackbar']
      });

      // Navigate if needed
      if (shouldNavigate) {
        router.navigate([navigateTo]);
      }

      return throwError(() => error);
    })
  );
};
```

#### App Configuration

```typescript
// app.config.ts
import { provideHttpClient, withInterceptors } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(withInterceptors([errorInterceptor]))
  ]
};
```

#### Snackbar Styles

```scss
// styles.scss
.error-snackbar {
  --mdc-snackbar-container-color: #f44336;
  --mdc-snackbar-supporting-text-color: white;
}

.error-snackbar-critical {
  --mdc-snackbar-container-color: #b71c1c;
  --mdc-snackbar-supporting-text-color: white;
}
```


## 1.5 Navigation & Layout (CRITICAL for UX)

> [!IMPORTANT]
> **All VB6 migrations MUST include a proper navigation system.** VB6 apps use menus/MDI - modern apps need sidebar navigation.

### Layout Component Pattern (Required)
```typescript
// components/layout/layout.component.ts
@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.css'
})
export class LayoutComponent {
  private auth = inject(AuthService);
  
  navItems = [
    { path: '/dashboard', icon: '📊', label: 'Dashboard' },
    { path: '/clientes', icon: '👥', label: 'Clientes' },
    { path: '/libros', icon: '📚', label: 'Libros' },
    { path: '/prestamos', icon: '📤', label: 'Préstamos' },
  ];

  logout() {
    this.auth.logout();
    window.location.href = '/login';
  }
}
```

### Layout Template
```html
<div class="app-layout">
  <aside class="sidebar">
    <div class="sidebar-header">
      <span class="logo">📚</span>
      <h1>App Name</h1>
    </div>
    <nav class="sidebar-nav">
      @for (item of navItems; track item.path) {
        <a [routerLink]="item.path" routerLinkActive="active" class="nav-item">
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </a>
      }
    </nav>
    <div class="sidebar-footer">
      <button class="logout-btn" (click)="logout()">🚪 Cerrar Sesión</button>
    </div>
  </aside>
  <main class="main-content">
    <router-outlet />
  </main>
</div>
```

### Routes with Layout (Nested Children)
```typescript
export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent) },
  // Protected routes wrapped in layout
  {
    path: '',
    loadComponent: () => import('./components/layout/layout.component').then(m => m.LayoutComponent),
    canActivate: [() => authGuard()],
    children: [
      { path: 'dashboard', loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent) },
      { path: 'clientes', loadComponent: () => import('./components/clientes/clientes-list.component').then(m => m.ClientesListComponent) },
      // ... more child routes
    ]
  },
  { path: '**', redirectTo: 'login' }
];
```

> [!TIP]
> **VB6 Menu → Sidebar Mapping:**
> - `mnuFile` → Dashboard/Home
> - `mnuClientes` → /clientes
> - `mnuLibros` → /libros
> - `mnuPrestamos` → /prestamos
> - `mnuSalir` → Logout button in sidebar footer

## 1.6 Internationalization (i18n)

```typescript
// Add to app.config.ts
import { LOCALE_ID } from '@angular/core';
import { registerLocaleData } from '@angular/common';
import localeEs from '@angular/common/locales/es';

registerLocaleData(localeEs);

export const appConfig: ApplicationConfig = {
  providers: [
    { provide: LOCALE_ID, useValue: 'es' },
    { provide: MAT_DATE_LOCALE, useValue: 'es-ES' }
  ]
};
```

## 1.6 Feature Module Structure

```
src/app/
├── components/
│   ├── members/
│   │   ├── members.component.ts       # List + Table
│   │   ├── members.component.html
│   │   └── members.component.scss
│   ├── member-dialog/
│   │   ├── member-dialog.component.ts # Create/Edit Modal
│   │   ├── member-dialog.component.html
│   │   └── member-dialog.component.scss
│   └── shared/
│       ├── confirm-dialog/           # Reusable confirm
│       └── loading-spinner/          # Reusable spinner
├── services/
│   ├── members.service.ts
│   └── auth.service.ts
├── models/
│   ├── member.model.ts
│   └── index.ts
├── interceptors/
│   └── error.interceptor.ts
└── guards/
    └── auth.guard.ts
```

---

# 2. 🛠️ Backend Specifications

## 2.1 Project Structure

```
backend/
├── prisma/
│   └── schema.prisma
├── src/
│   ├── routes/
│   │   ├── index.ts          # Route aggregator
│   │   ├── members.routes.ts
│   │   └── books.routes.ts
│   ├── controllers/
│   │   ├── members.controller.ts
│   │   └── books.controller.ts
│   ├── services/
│   │   ├── members.service.ts
│   │   └── books.service.ts
│   ├── types/
│   │   ├── index.ts
│   │   └── members.dto.ts
│   ├── middlewares/
│   │   ├── error.middleware.ts
│   │   └── logging.middleware.ts
│   └── server.ts
├── package.json
└── tsconfig.json
```

## 2.2 Prisma Schema

```prisma
// prisma/schema.prisma
datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model Member {
  id        Int       @id @default(autoincrement())
  name      String
  address   String?
  phone     String?
  email     String?
  createdAt DateTime  @default(now())
  loans     Loan[]
}

model Book {
  id        Int       @id @default(autoincrement())
  title     String
  author    String
  isbn      String?   @unique
  loans     Loan[]
}

model Loan {
  id          Int       @id @default(autoincrement())
  memberId    Int
  bookId      Int
  startDate   DateTime  @default(now())
  endDate     DateTime?
  returned    Boolean   @default(false)
  member      Member    @relation(fields: [memberId], references: [id])
  book        Book      @relation(fields: [bookId], references: [id])
}
```

## 2.3 Express Server with Pino

```typescript
// src/server.ts
import express from 'express';
import cors from 'cors';
import pino from 'pino-http';
import swaggerUi from 'swagger-ui-express';
import { swaggerSpec } from './swagger';
import { routes } from './routes';
import { errorMiddleware } from './middlewares/error.middleware';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(pino({
  transport: {
    target: 'pino-pretty',
    options: { colorize: true }
  }
}));

// Swagger
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Routes
app.use('/api', routes);

// Error handling (must be last)
app.use(errorMiddleware);

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📚 Swagger docs: http://localhost:${PORT}/api-docs`);
});
```

## 2.4 Service Layer Pattern

```typescript
// src/services/members.service.ts
import { PrismaClient, Member } from '@prisma/client';
import { CreateMemberDto, UpdateMemberDto } from '../types';

const prisma = new PrismaClient();

export class MembersService {
  async findAll(): Promise<Member[]> {
    return prisma.member.findMany({
      orderBy: { name: 'asc' }
    });
  }

  async findOne(id: number): Promise<Member | null> {
    return prisma.member.findUnique({
      where: { id },
      include: { loans: true }
    });
  }

  async create(data: CreateMemberDto): Promise<Member> {
    return prisma.member.create({ data });
  }

  async update(id: number, data: UpdateMemberDto): Promise<Member> {
    return prisma.member.update({
      where: { id },
      data
    });
  }

  async delete(id: number): Promise<void> {
    await prisma.member.delete({ where: { id } });
  }
}

export const membersService = new MembersService();
```

## 2.5 Controller Layer Pattern

```typescript
// src/controllers/members.controller.ts
import { Request, Response, NextFunction } from 'express';
import { membersService } from '../services/members.service';

export class MembersController {
  async getAll(req: Request, res: Response, next: NextFunction) {
    try {
      const members = await membersService.findAll();
      res.json(members);
    } catch (error) {
      next(error);
    }
  }

  async getById(req: Request, res: Response, next: NextFunction) {
    try {
      const id = parseInt(req.params.id);
      const member = await membersService.findOne(id);
      if (!member) {
        return res.status(404).json({ message: 'Member not found' });
      }
      res.json(member);
    } catch (error) {
      next(error);
    }
  }

  async create(req: Request, res: Response, next: NextFunction) {
    try {
      const member = await membersService.create(req.body);
      res.status(201).json(member);
    } catch (error) {
      next(error);
    }
  }

  async update(req: Request, res: Response, next: NextFunction) {
    try {
      const id = parseInt(req.params.id);
      const member = await membersService.update(id, req.body);
      res.json(member);
    } catch (error) {
      next(error);
    }
  }

  async delete(req: Request, res: Response, next: NextFunction) {
    try {
      const id = parseInt(req.params.id);
      await membersService.delete(id);
      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }
}

export const membersController = new MembersController();
```

## 2.6 Routes with Swagger

```typescript
// src/routes/members.routes.ts
import { Router } from 'express';
import { membersController } from '../controllers/members.controller';

const router = Router();

/**
 * @swagger
 * /api/members:
 *   get:
 *     summary: Get all members
 *     tags: [Members]
 *     responses:
 *       200:
 *         description: List of members
 */
router.get('/', membersController.getAll);

/**
 * @swagger
 * /api/members/{id}:
 *   get:
 *     summary: Get member by ID
 *     tags: [Members]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Member found
 *       404:
 *         description: Member not found
 */
router.get('/:id', membersController.getById);

/**
 * @swagger
 * /api/members:
 *   post:
 *     summary: Create new member
 *     tags: [Members]
 */
router.post('/', membersController.create);

/**
 * @swagger
 * /api/members/{id}:
 *   put:
 *     summary: Update member
 *     tags: [Members]
 */
router.put('/:id', membersController.update);

/**
 * @swagger
 * /api/members/{id}:
 *   delete:
 *     summary: Delete member
 *     tags: [Members]
 */
router.delete('/:id', membersController.delete);

export const membersRoutes = router;
```

## 2.7 Error Middleware

```typescript
// src/middlewares/error.middleware.ts
import { Request, Response, NextFunction } from 'express';
import { Prisma } from '@prisma/client';

export function errorMiddleware(
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  req.log.error(error);

  // Prisma errors
  if (error instanceof Prisma.PrismaClientKnownRequestError) {
    if (error.code === 'P2002') {
      return res.status(409).json({
        message: 'A record with this data already exists'
      });
    }
    if (error.code === 'P2025') {
      return res.status(404).json({
        message: 'Record not found'
      });
    }
  }

  // Default error
  res.status(500).json({
    message: 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? error.message : undefined
  });
}
```

## 2.8 Swagger Configuration

```typescript
// src/swagger.ts
import swaggerJsdoc from 'swagger-jsdoc';

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Library API',
      version: '1.0.0',
      description: 'REST API for library management'
    },
    servers: [
      { url: 'http://localhost:3000' }
    ]
  },
  apis: ['./src/routes/*.ts']
};

export const swaggerSpec = swaggerJsdoc(options);
```

---

# 3. 📋 VB6 → Modern Mapping Reference

| VB6 Concept | Modern Equivalent | Migration Path |
|-------------|-------------------|----------------|
| `Form_Load` | `ngOnInit()` | Direct map |
| `cmdButton_Click` | `(click)="method()"` | Direct map |
| `txtField.Text` | `formControl.value` | Reactive forms |
| `MSFlexGrid` | `mat-table` | Angular Material |
| `DataCombo` | `mat-select` + async data | Angular Material |
| `MsgBox` | `MatSnackBar` | UI update |
| `InputBox` | `MatDialog` | Custom dialog |
| `Form.Show vbModal` | `MatDialog.open()` | Direct map |
| `ADODB.Connection` | Prisma Client | ORM pattern |
| `Recordset.AddNew` | `prisma.entity.create()` | CRUD mapping |
| `DoEvents` | Remove | Async by default |
| `Timer` | `setInterval` / RxJS | JS equivalent |
