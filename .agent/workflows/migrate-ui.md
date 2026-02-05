---
description: Migrates a specific VB6 Form to an Angular Component.
---

// turbo-all

# Migrate UI Workflow v2.0

## Purpose

Convert a VB6 Form (`.FRM`) to an Angular standalone component with full functionality preservation.

---

## Prerequisites

- Analysis phase complete (`VB6_LOGIC_ANALYSIS.md`)
- Backend API ready for this entity
- Angular project initialized with Material

---

## Step 1: Analyze VB6 Form

### Extract from FRM file:
```bash
# View form structure
grep -E "Begin|End|Caption|Text|Name" path/to/form.frm

# List all controls
grep -E "^Begin\s+\w+\.\w+" path/to/form.frm

# Find event handlers
grep -E "Private Sub \w+_\w+" path/to/form.frm
```

### Document:
- [ ] Control inventory (TextBox, Button, Grid, etc.)
- [ ] Event handlers (Click, Change, Load, etc.)
- [ ] Business rules (validations, calculations)
- [ ] Data operations (CRUD)

---

## Step 2: Create Component Structure

```bash
# Generate component
ng generate component components/socios --standalone

# Generate dialog component
ng generate component components/socio-dialog --standalone
```

### File structure:
```
src/app/components/
├── socios/
│   ├── socios.component.ts      # List with mat-table
│   ├── socios.component.html
│   └── socios.component.scss
└── socio-dialog/
    ├── socio-dialog.component.ts  # Create/Edit modal
    ├── socio-dialog.component.html
    └── socio-dialog.component.scss
```

---

## Step 3: Implement List Component

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
  templateUrl: './socios.component.html'
})
export class SociosComponent implements OnInit {
  displayedColumns = ['id', 'nombre', 'telefono', 'email', 'actions'];
  dataSource = signal<Socio[]>([]);
  loading = signal(false);

  constructor(
    private sociosService: SociosService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.loading.set(true);
    this.sociosService.getAll().subscribe({
      next: (data) => this.dataSource.set(data),
      complete: () => this.loading.set(false)
    });
  }

  openDialog(item?: Socio) {
    const dialogRef = this.dialog.open(SocioDialogComponent, {
      width: '600px',
      data: item ?? null
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) this.loadData();
    });
  }

  delete(id: number) {
    // Confirm dialog first
    this.sociosService.delete(id).subscribe(() => {
      this.snackBar.open('Eliminado correctamente', 'OK', { duration: 3000 });
      this.loadData();
    });
  }
}
```

---

## Step 4: Implement Dialog Component

```typescript
@Component({
  selector: 'app-socio-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatDatepickerModule,
    LucideAngularModule
  ],
  templateUrl: './socio-dialog.component.html'
})
export class SocioDialogComponent implements OnInit {
  form = new FormGroup({
    nombre: new FormControl('', [Validators.required, Validators.minLength(2)]),
    direccion: new FormControl(''),
    telefono: new FormControl(''),
    email: new FormControl('', Validators.email)
  });

  isEdit = false;

  constructor(
    private dialogRef: MatDialogRef<SocioDialogComponent>,
    private sociosService: SociosService,
    @Inject(MAT_DIALOG_DATA) public data: Socio | null
  ) {}

  ngOnInit() {
    if (this.data) {
      this.isEdit = true;
      this.form.patchValue(this.data);
    }
  }

  save() {
    if (!this.form.valid) return;

    const dto = this.form.value as CreateSocioDto;
    const request$ = this.isEdit
      ? this.sociosService.update(this.data!.id, dto)
      : this.sociosService.create(dto);

    request$.subscribe({
      next: () => this.dialogRef.close(true),
      error: () => {} // Handled by interceptor
    });
  }

  cancel() {
    this.dialogRef.close(false);
  }
}
```

---

## Step 5: VB6 Event → Angular Mapping

| VB6 Event | Angular Equivalent |
|-----------|-------------------|
| `Form_Load` | `ngOnInit()` |
| `cmdNuevo_Click` | `openDialog()` |
| `cmdGuardar_Click` | `save()` |
| `cmdCancelar_Click` | `cancel()` |
| `cmdEliminar_Click` | `delete(id)` |
| `txtField_Change` | Reactive Form binding |
| `txtField_LostFocus` | `(blur)` event |
| `dgGrid_DblClick` | `(click)` on table row |

---

## Step 6: Validation Rules Mapping

| VB6 Validation | Angular Equivalent |
|----------------|-------------------|
| `If Len(txt) = 0 Then` | `Validators.required` |
| `If Len(txt) > 50 Then` | `Validators.maxLength(50)` |
| `If Not IsNumeric(txt) Then` | `Validators.pattern(/^\d+$/)` |
| `If Not IsDate(txt) Then` | `mat-datepicker` handles this |
| `MsgBox "Error"` | `<mat-error>` in form field |

---

## Step 7: Add Route

```typescript
// app.routes.ts
export const routes: Routes = [
  { path: 'socios', component: SociosComponent },
  // ... other routes
];
```

---

## Verification

```bash
# Lint
ng lint

# Build check
ng build --configuration development

# Run app
ng serve
```

### Manual Testing Checklist:
- [ ] List loads data correctly
- [ ] Create new record works
- [ ] Edit existing record works
- [ ] Delete with confirmation works
- [ ] Form validations match VB6
- [ ] Error messages display correctly
- [ ] Responsive design works
