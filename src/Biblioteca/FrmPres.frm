VERSION 5.00
Object = "{5E9E78A0-531B-11CF-91F6-C2863C385E30}#1.0#0"; "MSFLXGRD.OCX"
Object = "{86CF1D34-0C5F-11D2-A9FC-0000F8754DA1}#2.0#0"; "MSCOMCT2.OCX"
Begin VB.Form FrmPres 
   BackColor       =   &H00C0E0FF&
   BorderStyle     =   1  'Fixed Single
   Caption         =   "PRESTAMO DE LIBROS"
   ClientHeight    =   3624
   ClientLeft      =   48
   ClientTop       =   336
   ClientWidth     =   7764
   Icon            =   "FrmPres.frx":0000
   LinkTopic       =   "Form2"
   MaxButton       =   0   'False
   MDIChild        =   -1  'True
   MinButton       =   0   'False
   ScaleHeight     =   3624
   ScaleWidth      =   7764
   Begin VB.CommandButton Command4 
      BackColor       =   &H80000004&
      Caption         =   "?"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   13.8
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   375
      Left            =   7440
      Style           =   1  'Graphical
      TabIndex        =   15
      Top             =   0
      Width           =   375
   End
   Begin VB.CommandButton Command1 
      Caption         =   "Salir"
      Height          =   375
      Left            =   6720
      TabIndex        =   14
      Top             =   3120
      Width           =   855
   End
   Begin MSFlexGridLib.MSFlexGrid Grilla1 
      Height          =   1815
      Left            =   360
      TabIndex        =   13
      Top             =   1560
      Visible         =   0   'False
      Width           =   4455
      _ExtentX        =   7853
      _ExtentY        =   3196
      _Version        =   393216
   End
   Begin VB.CommandButton cmdreg 
      Caption         =   "Registrar Prestamo"
      Enabled         =   0   'False
      Height          =   375
      Left            =   5040
      TabIndex        =   12
      Top             =   3120
      Width           =   1575
   End
   Begin VB.TextBox txttit 
      Height          =   285
      Left            =   1200
      Locked          =   -1  'True
      TabIndex        =   11
      Top             =   1080
      Width           =   2415
   End
   Begin VB.TextBox txtdias 
      Height          =   285
      Left            =   3840
      TabIndex        =   9
      Top             =   1080
      Width           =   615
   End
   Begin VB.TextBox txtidL 
      Height          =   285
      Left            =   360
      Locked          =   -1  'True
      TabIndex        =   5
      Top             =   1080
      Width           =   615
   End
   Begin VB.TextBox txtApe 
      Height          =   285
      Left            =   1800
      TabIndex        =   4
      Top             =   360
      Width           =   1815
   End
   Begin VB.CommandButton cmdcons 
      Caption         =   "Consulta"
      Height          =   255
      Left            =   3720
      TabIndex        =   3
      Top             =   360
      Width           =   975
   End
   Begin VB.TextBox txtsocio 
      Height          =   285
      Left            =   360
      TabIndex        =   1
      Top             =   360
      Width           =   1095
   End
   Begin MSComCtl2.MonthView MonthView1 
      Height          =   2256
      Left            =   5040
      TabIndex        =   0
      Top             =   480
      Width           =   2496
      _ExtentX        =   4403
      _ExtentY        =   3979
      _Version        =   393216
      ForeColor       =   -2147483630
      BackColor       =   -2147483633
      Appearance      =   1
      StartOfWeek     =   16777217
      CurrentDate     =   41006
   End
   Begin VB.Label Label5 
      Caption         =   "Dias Prestamo"
      Height          =   255
      Left            =   3720
      TabIndex        =   10
      Top             =   840
      Width           =   1095
   End
   Begin VB.Label Label4 
      Caption         =   "Apellido del Socio"
      Height          =   255
      Left            =   1800
      TabIndex        =   8
      Top             =   120
      Width           =   1455
   End
   Begin VB.Label Label3 
      Caption         =   "Titulo del Libro"
      Height          =   255
      Left            =   1200
      TabIndex        =   7
      Top             =   840
      Width           =   2055
   End
   Begin VB.Label Label2 
      Caption         =   "IdLibro"
      Height          =   255
      Left            =   360
      TabIndex        =   6
      Top             =   840
      Width           =   615
   End
   Begin VB.Label Label1 
      Caption         =   "Nro Socio"
      Height          =   255
      Left            =   360
      TabIndex        =   2
      Top             =   120
      Width           =   1095
   End
End
Attribute VB_Name = "FrmPres"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Private Sub cmdcons_Click()
Grilla1.Clear
Grilla1.Visible = False
If txtsocio <> "" And txtApe <> "" Then
ini
If rsc1.State = 1 Then rsc1.Close
rsc1.Open "Select Cliente.* From Cliente Where Cliente.IdCliente = " & _
txtsocio & " And Cliente.Apellidos = '" & txtApe & "'", cn, adOpenStatic, adLockOptimistic
If rsc1.RecordCount = 0 Then
MsgBox "Los Datos Ingresados NO SON VALIDOS", vbCritical, "BIBLIOTECA ADVIERTE"
fin
Exit Sub
End If

If rsc1.State = 1 Then rsc1.Close
rsc1.Open "Select Cliente.*, Libros.* From Cliente, Libros Where Cliente.IdCliente = Libros.Socio And Cliente.IdCliente = " & _
txtsocio & " And Cliente.Apellidos = '" & txtApe & "' And Libros.Estado = 'No'", cn, adOpenStatic, adLockOptimistic
If rsc1.RecordCount > 0 Then
MsgBox "Este Socio Tiene " & rsc1.RecordCount & " libros no devueltos", vbCritical, "BIBLIOTECA ADVIERTE"
With Grilla1

.Visible = True
.FormatString = " Titulo | Dia Prestamo |Dia Devolucion"
.ColWidth(0) = 2000
.ColWidth(1) = 1100
.ColWidth(2) = 1100

.Rows = 1

Do While rsc1.EOF = False
.AddItem rsc1.Fields(8) & vbTab & rsc1.Fields(12) & vbTab & rsc1.Fields(13)
rsc1.MoveNext
Loop
End With
fin
Else
cmdreg.Enabled = True
txtsocio.Locked = True
txtApe.Locked = True
End If
Else
MsgBox "Tiene que poner los datos requeridos para verificar", vbCritical, "[BIBLIOECA] ADVIERTE"
Exit Sub
End If
End Sub

Private Sub cmdreg_Click()
Dim suma$
suma = Format(DateAdd("d", Val(txtdias), Now()), "dd/mm/yyyy")
ini
If Grilla1.Visible = False And txtidL <> "" And txtdias <> "" And txtsocio.Locked = True Then
cn.Execute "Update Libros Set  Estado = 'No', Socio = " & txtsocio & ", FecPres = #" & Format(Now(), "dd/mm/yyyy") & _
"#, FecDev = #" & suma & "#, dias = " & txtdias & "  Where IdLibro = " & txtidL
Else
MsgBox "FALTAN DATOS REQUERIDOS", vbCritical, "[BIBLIOTECA] Informa "
fin
Exit Sub
End If
MsgBox "Datos Registrados", vbInformation, "[BIBLIOTECA]Informa "
Dim ct As Control
For Each ct In FrmPres
If TypeOf ct Is TextBox Then ct = ""
Next
fin
Unload Me
End Sub

Private Sub Command1_Click()
Unload Me
End Sub

Private Sub Command4_Click()
frmAYUDA.Show
End Sub
