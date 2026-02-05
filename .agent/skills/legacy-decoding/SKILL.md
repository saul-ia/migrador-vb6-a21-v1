---
name: legacy-decoding
description: Expert techniques for parsing and decoding ALL VB6 codebase artifacts with migration-oriented analysis patterns.
allowed-tools: view_file, grep_search, find_by_name, run_command
---

# Legacy Decoding Manual v3.0 (Migration-Oriented)

---

## 📁 Complete VB6 File Type Reference

### Project Files
| Extension | Purpose | Description | Migration Relevance |
|-----------|---------|-------------|---------------------|
| `.VBP` | Project File | Main project definition | Entry point, references, startup form |
| `.VBG` | Project Group | Groups multiple .VBP files | Multi-project dependencies |
| `.VBW` | Workspace | Window positions, IDE state | Not needed for migration |

### Code Files
| Extension | Purpose | Description | Migration Priority |
|-----------|---------|-------------|-------------------|
| `.FRM` | Form | UI + event handlers | 🔴 HIGH - Contains UI + Logic |
| `.FRX` | Form Binary | Embedded icons, images | 🟢 LOW - Extract assets only |
| `.BAS` | Module | Shared functions, globals | 🔴 HIGH - Shared logic, globals |
| `.CLS` | Class | OOP class definition | 🟡 MEDIUM - OOP logic |
| `.CTL` | UserControl | Custom reusable control | 🔴 HIGH - Reusable components |
| `.CTX` | Control Binary | Binary resources for .CTL | 🟢 LOW - Resources only |

### Designer Files
| Extension | Purpose | Description | Migration Priority |
|-----------|---------|-------------|-------------------|
| `.DSR` | Data Report | Visual report layout | 🟡 MEDIUM - Convert to PDF service |
| `.DSX` | Data Report Binary | Binary resources for .DSR | 🟢 LOW - Resources only |
| `.PAG` | Property Page | Custom property editing UI | 🟡 MEDIUM - Config dialogs |
| `.PGX` | Property Page Binary | Binary resources for .PAG | 🟢 LOW - Resources only |

### Dependencies
| Extension | Purpose | Description | Migration Risk |
|-----------|---------|-------------|---------------|
| `.OCX` | ActiveX Control | Third-party UI controls | 🔴 HIGH - Needs web alternative |
| `.OCA` | Extended Type Info | OCX metadata cache | 🟢 LOW - Auto-generated |
| `.DLL` | Dynamic Library | Native code library | 🔴 HIGH - Platform-specific |
| `.TLB` | Type Library | COM interface definitions | 🟡 MEDIUM - API contracts |
| `.DCA` | Designer Cache | Cached designer info | 🟢 LOW - Auto-generated |

### Resources & Reports
| Extension | Purpose | Description | Migration Strategy |
|-----------|---------|-------------|-------------------|
| `.RES` | Resource File | Icons, strings, cursors | Extract and migrate to /assets |
| `.RPT` | Crystal Report | Report template | Convert to PDFMake/Jasper |

### Assets
| Extension | Purpose | Description | Migration Strategy |
|-----------|---------|-------------|-------------------|
| `.ICO` | Icon | Application/toolbar icons | Copy to /assets/icons |
| `.GIF` | Image | Animated/static images | Copy to /assets/images |
| `.JPG`/`.JPEG` | Image | Photos, backgrounds | Copy to /assets/images |
| `.BMP` | Bitmap | Legacy image format | Convert to PNG/JPG |
| `.CUR` | Cursor | Custom mouse cursors | May not be needed |

### Help & Documentation
| Extension | Purpose | Description | Migration Strategy |
|-----------|---------|-------------|-------------------|
| `.CHM` | Compiled Help | Windows Help file | Convert to HTML docs |
| `.HLP` | Help File | Legacy Windows Help | Convert to HTML docs |
| `.TXT` | Text | Readme, notes | Review for requirements |
| `.LOG` | Log File | Debug/execution logs | Analyze for behavior |
| `.DOC` | Document | Word documentation | Extract requirements |

### Executables & Temp
| Extension | Purpose | Description | Migration Relevance |
|-----------|---------|-------------|---------------------|
| `.EXE` | Executable | Compiled application | Reference only (no source) |
| `.TMP` | Temporary | IDE temp files | Ignore - not needed |
| `.SCC` | Source Control | VSS metadata | Ignore - version control |

---

## 🔍 Logic Classification Patterns

### 1. Business Rules Detection

```vb
' VALIDATION RULE
If Len(txtNombre.Text) = 0 Then
    MsgBox "Nombre requerido"
    Exit Sub
End If

' CALCULATION RULE
dblTotal = dblSubtotal * (1 + dblIVA) - dblDescuento

' CONDITIONAL WORKFLOW
If rs!Estado = "Aprobado" And UserLevel >= 3 Then
    Call ProcesarPedido
End If
```

**Extract to:** Shared validation service, calculation utilities

### 2. UI Logic Detection

```vb
' STATE MANAGEMENT
Private Sub Form_Load()
    cmdGuardar.Enabled = False
    cboTipo.ListIndex = 0
End Sub

' VISIBILITY CONTROL
If UserLevel < 2 Then
    cmdEliminar.Visible = False
End If

' MODAL HANDLING
frmDetalles.Show vbModal
If frmDetalles.Cancelled Then Exit Sub
```

**Migrate to:** Angular component state, guards, dialogs

### 3. Data Access Detection

```vb
' CONNECTION
cn.Open "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=C:\db.mdb"

' QUERY
rs.Open "SELECT * FROM Clientes WHERE Id = " & lngId, cn

' CRUD
rs.AddNew          ' → POST
rs!Nombre = valor  ' → request body
rs.Update          ' → commit

rs.Edit            ' → PUT
rs.Delete          ' → DELETE
```

**Migrate to:** REST API endpoints, HttpClient

### 4. Global State Detection

```vb
' In modGlobales.bas
Public gCurrentUser As String
Public gConnectionString As String
Public gUserLevel As Integer

' In any form accessing globals
If gUserLevel >= ADMIN_LEVEL Then
```

**Migrate to:** Angular services, AuthService, ConfigService

---

## 🎯 Migration Classification Matrix

### Early Extraction Candidates ✅
| Pattern | Example | Why Early |
|---------|---------|-----------|
| Pure functions | `FormatDate()`, `CalculateTax()` | No side effects |
| Constants | `Const TAX_RATE = 0.21` | Direct translation |
| Lookups | `GetStatusName(code)` | Simple mapping |
| Validators | `IsValidEmail()` | Reusable |

### Coexistence Required ⚠️
| Pattern | Example | Why Coexist |
|---------|---------|-------------|
| Shared data modules | `modData.OpenConnection()` | Both systems need data |
| Auth logic | `ValidateUser()` | SSO transition period |
| Reports | `GenerateInvoice()` | PDF service needed |
| File operations | `ExportToExcel()` | Backend service needed |

### Defer Migration 🔴
| Pattern | Example | Why Defer |
|---------|---------|-----------|
| COM Automation | `CreateObject("Excel.")` | Major redesign |
| Windows API | `Declare Function` | Platform specific |
| Heavy coupling | Form with 100+ controls | Refactor first |
| Crystal Reports | `.RPT` files | Alternative needed |

---

## 🔧 Strangler Pattern Seam Detection

### Data Layer Seams
```vb
' SEAM: Before database operations
cn.Open strConnection  ' ← Intercept here with API call

' Modern intercept:
' Check if entity exists in new system
' If yes, route to API
' If no, fallback to VB6
```

### Navigation Seams
```vb
' SEAM: Form transitions
frmClientes.Show  ' ← Redirect to Angular route

' Modern intercept:
' Shell("start http://localhost:4200/clientes")
' Unload Me
```

### Report Seams
```vb
' SEAM: Report generation
Crystal.ReportFileName = "Invoice.rpt"  ' ← Route to PDF service

' Modern intercept:
' Dim http As New XMLHTTP
' http.Open "GET", "http://api/reports/invoice/" & id
```

### Facade Pattern Points
```
modData.bas → /api/* (REST facade)
modUtils.bas → npm:@lib/utils
modSecurity.bas → /api/auth/*
```

---

## 📊 Coupling Analysis Queries

### Find Module Dependencies
```bash
# Find all calls to a module
grep -rn "modData\." *.frm *.bas *.cls

# Find all form references
grep -rn "frm\w*\." *.frm *.bas

# Find global variable usage
grep -rn "^Public\|^Global" *.bas
```

### Dependency Matrix Template
```markdown
| Source | Target | Type | Count | Risk |
|--------|--------|------|-------|------|
| FrmMain | modData | Data | 15 | Medium |
| FrmMain | modUtils | Util | 8 | Low |
| FrmPedidos | FrmClientes | Form | 3 | High |
```

---

## 🛠️ Analysis Script Usage

```bash
# Comprehensive scan with migration analysis
python .agent/scripts/vb6_comprehensive_scanner.py "source_dir" -o analysis.json --pretty

# Generate HTML report with seam identification
python .agent/scripts/html_report_generator.py analysis.json -o MIGRATION_REPORT.html
```

---

## ⚡ Quick Reference: VB6 → Modern Mapping

| VB6 Concept | Modern Equivalent | Migration Path |
|-------------|-------------------|----------------|
| `Form_Load` | `ngOnInit()` | Direct map |
| `MsgBox` | `MatSnackBar` | UI update |
| `Recordset` | `HttpClient` | API call |
| `Global` vars | Angular Service | State refactor |
| `Timer` | `setInterval` | JS equivalent |
| `DoEvents` | Remove | Async by default |
| `On Error Resume Next` | `try/catch` | Error handling |
| `Module.Function` | Service method | DI pattern |
