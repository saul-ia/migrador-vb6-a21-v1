---
name: modern-stack
description: Complete specifications and patterns for the target stack (Angular 21, Node 24+, Express 5+, SQLite/Prisma).
allowed-tools: view_file, write_to_file, run_command
---

# Modern Stack Manual v2.0

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

---

# 1. ⚙️ Frontend Specifications

## 1.1 Angular Core Patterns

### Standalone Components (Required)
```typescript
@Component({
  selector: 'app-socios',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    LucideAngularModule
  ],
  templateUrl: './socios.component.html',
  styleUrl: './socios.component.scss'
})
export class SociosComponent implements OnInit {
  // Use Signals for state
  data = signal<Socio[]>([]);
  loading = signal<boolean>(false);
}
```

### Signals for State Management
```typescript
// ✅ Correct: Use Signals
data = signal<Socio[]>([]);
selectedItem = signal<Socio | null>(null);
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

## 1.2 Angular Material + UI

### MatDialog for Modals (VB6 Form Replacement)
```typescript
// Opening dialog
openDialog(item?: Socio): void {
  const dialogRef = this.dialog.open(SocioDialogComponent, {
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
  <mat-label>Fecha de Préstamo</mat-label>
  <input matInput [matDatepicker]="picker" formControlName="fechaPrestamo">
  <mat-datepicker-toggle matIconSuffix [for]="picker">
    <lucide-icon name="calendar" matDatepickerToggleIcon></lucide-icon>
  </mat-datepicker-toggle>
  <mat-datepicker #picker></mat-datepicker>
  <mat-error *ngIf="form.get('fechaPrestamo')?.hasError('required')">
    Fecha requerida
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
export class SocioDialogComponent implements OnInit {
  form = new FormGroup({
    nombre: new FormControl('', [
      Validators.required,
      Validators.minLength(2),
      Validators.maxLength(100)
    ]),
    email: new FormControl('', [
      Validators.email
    ]),
    telefono: new FormControl(''),
    fechaAlta: new FormControl(new Date(), Validators.required)
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
    <mat-label>Nombre</mat-label>
    <input matInput formControlName="nombre" placeholder="Nombre completo">
    <mat-error *ngIf="form.get('nombre')?.hasError('required')">
      El nombre es obligatorio
    </mat-error>
    <mat-error *ngIf="form.get('nombre')?.hasError('minlength')">
      Mínimo 2 caracteres
    </mat-error>
  </mat-form-field>
  
  <div mat-dialog-actions align="end">
    <button mat-button type="button" (click)="cancel()">
      <lucide-icon name="x" size="18"></lucide-icon>
      Cancelar
    </button>
    <button mat-raised-button color="primary" type="submit" [disabled]="!form.valid">
      <lucide-icon name="save" size="18"></lucide-icon>
      Guardar
    </button>
  </div>
</form>
```

## 1.4 HTTP Client + Error Interceptor

### Service Pattern
```typescript
@Injectable({ providedIn: 'root' })
export class SociosService {
  private readonly apiUrl = '/api/socios';

  constructor(private http: HttpClient) {}

  getAll(): Observable<Socio[]> {
    return this.http.get<Socio[]>(this.apiUrl);
  }

  getById(id: number): Observable<Socio> {
    return this.http.get<Socio>(`${this.apiUrl}/${id}`);
  }

  create(dto: CreateSocioDto): Observable<Socio> {
    return this.http.post<Socio>(this.apiUrl, dto);
  }

  update(id: number, dto: UpdateSocioDto): Observable<Socio> {
    return this.http.put<Socio>(`${this.apiUrl}/${id}`, dto);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
```

### Error Interceptor (HttpInterceptorFn)

#### HTTP Error Codes Reference

| Código | Condición | Nombre | Descripción | Acción en Interceptor |
|--------|-----------|--------|-------------|----------------------|
| `0` | `!navigator.onLine` | Offline / Sin Red | Sin conexión a internet | 📡 "Sin conexión a internet. Verifique su red." |
| `0` | `navigator.onLine` | Unknown / CORS / Down | Servidor caído o CORS | ⚠️ "No se pudo contactar con el servidor." |
| `400` | N/A | Bad Request | Sintaxis inválida o JSON mal formado | Mostrar `error.message` del backend |
| `401` | N/A | Unauthorized | Token caducado o faltante | 🔒 Refresh Token o redirigir a Login |
| `403` | N/A | Forbidden | Sin permisos para este recurso | ⛔ "No tiene permisos para esta acción." |
| `404` | N/A | Not Found | Recurso no existe | Redirigir a 404 o mostrar mensaje |
| `405` | N/A | Method Not Allowed | Método HTTP incorrecto | Loguear en consola (error de desarrollo) |
| `408` | N/A | Request Timeout | Cliente tardó en enviar | Sugerir reintentar |
| `409` | N/A | Conflict | Registro duplicado | Mostrar error específico en formulario |
| `422` | N/A | Unprocessable Entity | Error de validación | Mapear errores a campos del formulario |
| `429` | N/A | Too Many Requests | Rate limiting excedido | ⏳ Bloquear botón temporalmente |
| `500` | N/A | Internal Server Error | Bug en backend | 🔥 "Error interno. Intente más tarde." |
| `501` | N/A | Not Implemented | Endpoint en construcción | Loguear error |
| `502` | N/A | Bad Gateway | Respuesta inválida de servicio interno | Pedir reintentar |
| `503` | N/A | Service Unavailable | Mantenimiento o sobrecarga | 🛠️ "Servidor en mantenimiento." |
| `504` | N/A | Gateway Timeout | Timeout del backend | "La operación está tardando más de lo esperado." |

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
      let message = 'Error desconocido';
      let duration = 5000;
      let shouldNavigate = false;
      let navigateTo = '';

      // Handle offline / network errors (status 0)
      if (error.status === 0) {
        if (!navigator.onLine) {
          message = '📡 Sin conexión a internet. Verifique su red.';
        } else {
          message = '⚠️ No se pudo contactar con el servidor.';
        }
      } else {
        switch (error.status) {
          case 400:
            message = error.error?.message || 'Solicitud inválida.';
            break;
          case 401:
            message = '🔒 Sesión expirada. Inicie sesión nuevamente.';
            shouldNavigate = true;
            navigateTo = '/login';
            // TODO: Implement refresh token logic here
            break;
          case 403:
            message = '⛔ No tiene permisos para realizar esta acción.';
            break;
          case 404:
            message = 'El recurso solicitado no existe.';
            break;
          case 405:
            console.error('[DEV] Method Not Allowed:', req.method, req.url);
            message = 'Error de configuración (405).';
            break;
          case 408:
            message = 'La solicitud tardó demasiado. Intente nuevamente.';
            break;
          case 409:
            message = error.error?.message || 'Conflicto: el registro ya existe.';
            break;
          case 422:
            // Validation errors - don't show snackbar, let form handle it
            return throwError(() => error);
          case 429:
            message = '⏳ Demasiadas solicitudes. Espere un momento.';
            duration = 10000;
            break;
          case 500:
            message = '🔥 Error interno del servidor. Intente más tarde.';
            break;
          case 501:
            console.warn('[DEV] Not Implemented:', req.url);
            message = 'Funcionalidad no disponible.';
            break;
          case 502:
            message = 'Error de conexión con servicios internos.';
            break;
          case 503:
            message = '🛠️ Servidor en mantenimiento. Intente en unos minutos.';
            break;
          case 504:
            message = 'La operación está tardando más de lo esperado.';
            break;
          default:
            message = error.error?.message || `Error ${error.status}`;
        }
      }

      // Show snackbar notification
      snackBar.open(message, 'Cerrar', {
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


## 1.5 Internationalization (i18n)

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
│   ├── socios/
│   │   ├── socios.component.ts       # List + Table
│   │   ├── socios.component.html
│   │   └── socios.component.scss
│   ├── socio-dialog/
│   │   ├── socio-dialog.component.ts # Create/Edit Modal
│   │   ├── socio-dialog.component.html
│   │   └── socio-dialog.component.scss
│   └── shared/
│       ├── confirm-dialog/           # Reusable confirm
│       └── loading-spinner/          # Reusable spinner
├── services/
│   ├── socios.service.ts
│   └── auth.service.ts
├── models/
│   ├── socio.model.ts
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
│   │   ├── socios.routes.ts
│   │   └── libros.routes.ts
│   ├── controllers/
│   │   ├── socios.controller.ts
│   │   └── libros.controller.ts
│   ├── services/
│   │   ├── socios.service.ts
│   │   └── libros.service.ts
│   ├── types/
│   │   ├── index.ts
│   │   └── socios.dto.ts
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

model Socio {
  id        Int       @id @default(autoincrement())
  nombre    String
  direccion String?
  telefono  String?
  email     String?
  fechaAlta DateTime  @default(now())
  prestamos Prestamo[]
}

model Libro {
  id        Int       @id @default(autoincrement())
  titulo    String
  autor     String
  isbn      String?   @unique
  prestamos Prestamo[]
}

model Prestamo {
  id          Int       @id @default(autoincrement())
  socioId     Int
  libroId     Int
  fechaInicio DateTime  @default(now())
  fechaFin    DateTime?
  devuelto    Boolean   @default(false)
  socio       Socio     @relation(fields: [socioId], references: [id])
  libro       Libro     @relation(fields: [libroId], references: [id])
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
// src/services/socios.service.ts
import { PrismaClient, Socio } from '@prisma/client';
import { CreateSocioDto, UpdateSocioDto } from '../types';

const prisma = new PrismaClient();

export class SociosService {
  async findAll(): Promise<Socio[]> {
    return prisma.socio.findMany({
      orderBy: { nombre: 'asc' }
    });
  }

  async findOne(id: number): Promise<Socio | null> {
    return prisma.socio.findUnique({
      where: { id },
      include: { prestamos: true }
    });
  }

  async create(data: CreateSocioDto): Promise<Socio> {
    return prisma.socio.create({ data });
  }

  async update(id: number, data: UpdateSocioDto): Promise<Socio> {
    return prisma.socio.update({
      where: { id },
      data
    });
  }

  async delete(id: number): Promise<void> {
    await prisma.socio.delete({ where: { id } });
  }
}

export const sociosService = new SociosService();
```

## 2.5 Controller Layer Pattern

```typescript
// src/controllers/socios.controller.ts
import { Request, Response, NextFunction } from 'express';
import { sociosService } from '../services/socios.service';

export class SociosController {
  async getAll(req: Request, res: Response, next: NextFunction) {
    try {
      const socios = await sociosService.findAll();
      res.json(socios);
    } catch (error) {
      next(error);
    }
  }

  async getById(req: Request, res: Response, next: NextFunction) {
    try {
      const id = parseInt(req.params.id);
      const socio = await sociosService.findOne(id);
      if (!socio) {
        return res.status(404).json({ message: 'Socio no encontrado' });
      }
      res.json(socio);
    } catch (error) {
      next(error);
    }
  }

  async create(req: Request, res: Response, next: NextFunction) {
    try {
      const socio = await sociosService.create(req.body);
      res.status(201).json(socio);
    } catch (error) {
      next(error);
    }
  }

  async update(req: Request, res: Response, next: NextFunction) {
    try {
      const id = parseInt(req.params.id);
      const socio = await sociosService.update(id, req.body);
      res.json(socio);
    } catch (error) {
      next(error);
    }
  }

  async delete(req: Request, res: Response, next: NextFunction) {
    try {
      const id = parseInt(req.params.id);
      await sociosService.delete(id);
      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }
}

export const sociosController = new SociosController();
```

## 2.6 Routes with Swagger

```typescript
// src/routes/socios.routes.ts
import { Router } from 'express';
import { sociosController } from '../controllers/socios.controller';

const router = Router();

/**
 * @swagger
 * /api/socios:
 *   get:
 *     summary: Obtener todos los socios
 *     tags: [Socios]
 *     responses:
 *       200:
 *         description: Lista de socios
 */
router.get('/', sociosController.getAll);

/**
 * @swagger
 * /api/socios/{id}:
 *   get:
 *     summary: Obtener socio por ID
 *     tags: [Socios]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Socio encontrado
 *       404:
 *         description: Socio no encontrado
 */
router.get('/:id', sociosController.getById);

/**
 * @swagger
 * /api/socios:
 *   post:
 *     summary: Crear nuevo socio
 *     tags: [Socios]
 */
router.post('/', sociosController.create);

/**
 * @swagger
 * /api/socios/{id}:
 *   put:
 *     summary: Actualizar socio
 *     tags: [Socios]
 */
router.put('/:id', sociosController.update);

/**
 * @swagger
 * /api/socios/{id}:
 *   delete:
 *     summary: Eliminar socio
 *     tags: [Socios]
 */
router.delete('/:id', sociosController.delete);

export const sociosRoutes = router;
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
        message: 'Ya existe un registro con estos datos'
      });
    }
    if (error.code === 'P2025') {
      return res.status(404).json({
        message: 'Registro no encontrado'
      });
    }
  }

  // Default error
  res.status(500).json({
    message: 'Error interno del servidor',
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
      title: 'Biblioteca API',
      version: '1.0.0',
      description: 'API REST para gestión de biblioteca'
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

| VB6 Concept | Modern Equivalent |
|-------------|-------------------|
| `Form_Load` | `ngOnInit()` |
| `cmdButton_Click` | `(click)="method()"` |
| `txtField.Text` | `formControl.value` |
| `MSFlexGrid` | `mat-table` |
| `DataCombo` | `mat-select` + async data |
| `MsgBox` | `MatSnackBar` |
| `InputBox` | `MatDialog` |
| `Form.Show vbModal` | `MatDialog.open()` |
| `ADODB.Connection` | Prisma Client |
| `Recordset.AddNew` | `prisma.entity.create()` |
| `DoEvents` | Remove (async by default) |
| `Timer` | `setInterval` / RxJS |
