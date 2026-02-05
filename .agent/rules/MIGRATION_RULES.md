---
description: Global rules and validation criteria for the VB6 to Angular migration.
---

# Migration Rules v2.0

## 1. Code Generation Rules

### 1.1 Never Skip Functionality
- ❌ **Prohibited**: Removing features that exist in VB6
- ✅ **Required**: Every VB6 feature must have a modern equivalent

### 1.2 Type Safety
- All TypeScript code must use strict typing
- No `any` types except in exceptional documented cases
- DTOs must match between Frontend and Backend

### 1.3 Naming Conventions

| VB6 | Angular/TypeScript | Backend |
|-----|-------------------|---------|
| `frmClientes` | `ClientesComponent` | N/A |
| `modData` | `DataService` | `data.service.ts` |
| `Clientes` (table) | `Cliente` (model) | `Prisma model Cliente` |
| `cmdGuardar` | `save()` method | N/A |
| `txtNombre` | `nombre: FormControl` | N/A |

---

## 2. Architecture Rules

### 2.1 Separation of Concerns
```
VB6 Form → Angular Component (UI only)
VB6 Business Logic → Angular Service / Backend Service
VB6 Data Access → Backend Service via REST API
```

### 2.2 No Direct Database Access from Frontend
- ❌ Frontend must NEVER contain SQL
- ✅ All data operations through `/api/*` endpoints

### 2.3 State Management
- Use Angular Signals for component state
- Use Services for shared state
- No global variables (unlike VB6 Public vars)

---

## 3. Data Migration Rules

### 3.1 Schema Mapping

| Access Type | SQLite/Prisma Type |
|-------------|-------------------|
| AutoNumber | `Int @id @default(autoincrement())` |
| Text | `String` |
| Memo | `String` |
| Number (Long) | `Int` |
| Number (Double) | `Float` |
| Currency | `Decimal` |
| Date/Time | `DateTime` |
| Yes/No | `Boolean @default(false)` |
| OLE Object | ❌ Not migrated (store path only) |

### 3.2 Required Fields
- Every table MUST have a primary key
- Add `createdAt` and `updatedAt` to all new tables
- Preserve original field names when possible

### 3.3 Relationships
- Convert implicit relationships (foreign keys) to explicit Prisma relations
- Document any orphan data found during migration

---

## 4. UI Migration Rules

### 4.1 Control Mapping

| VB6 Control | Angular Material |
|-------------|------------------|
| TextBox | `<input matInput>` |
| CommandButton | `<button mat-raised-button>` |
| DataGrid/MSFlexGrid | `<mat-table>` |
| ComboBox | `<mat-select>` |
| CheckBox | `<mat-checkbox>` |
| DateTimePicker | `<mat-datepicker>` |
| Frame | `<mat-card>` |
| TabStrip | `<mat-tab-group>` |
| MsgBox | `MatSnackBar` |
| InputBox | `MatDialog` |

### 4.2 Modal Forms
- VB6 `Form.Show vbModal` → Angular `MatDialog`
- Must preserve Cancel/Save behavior
- Return data via `dialogRef.afterClosed()`

### 4.3 Validation
- Replicate ALL VB6 validations in Angular Reactive Forms
- Use same error messages (translated if needed)

---

## 5. Error Handling Rules

### 5.1 VB6 to Modern Mapping

| VB6 Pattern | Modern Equivalent |
|-------------|-------------------|
| `On Error Resume Next` | ❌ Remove - use proper try/catch |
| `On Error GoTo Handler` | try/catch block |
| `Err.Number` | `error.status` or exception type |
| `MsgBox "Error"` | `MatSnackBar` or `console.error` |

### 5.2 Backend Error Responses
```typescript
// Standard error response format
{
  status: number,
  message: string,
  errors?: { field: string, message: string }[]
}
```

---

## 6. Testing Rules

### 6.1 Coverage Requirements
- Backend services: 80% minimum
- Frontend components: 70% minimum
- E2E: Critical user flows

### 6.2 What to Test
- Every CRUD operation
- Form validation
- Error handling paths
- Authentication flows

---

## 7. Documentation Rules

### 7.1 Code Comments
- Document non-obvious business logic
- Reference original VB6 function if complex
- Use JSDoc for public methods

### 7.2 Migration Notes
- When a feature changes significantly, document why
- When a feature is deferred, create a TODO issue
