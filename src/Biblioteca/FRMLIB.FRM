VERSION 5.00
Object = "{5E9E78A0-531B-11CF-91F6-C2863C385E30}#1.0#0"; "MSFLXGRD.OCX"
Begin VB.Form frmLib 
   BackColor       =   &H00FFC0C0&
   BorderStyle     =   1  'Fixed Single
   Caption         =   "Registro Libros "
   ClientHeight    =   7596
   ClientLeft      =   3756
   ClientTop       =   2760
   ClientWidth     =   8604
   Icon            =   "FRMLIB.frx":0000
   LinkTopic       =   "Form2"
   MaxButton       =   0   'False
   MDIChild        =   -1  'True
   MinButton       =   0   'False
   ScaleHeight     =   7596
   ScaleWidth      =   8604
   Begin VB.CommandButton Command6 
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
      Height          =   495
      Left            =   7680
      Style           =   1  'Graphical
      TabIndex        =   39
      Top             =   0
      Width           =   495
   End
   Begin VB.CommandButton cmdpres 
      BackColor       =   &H00FFC0C0&
      Caption         =   "PRESTAR"
      Height          =   375
      Left            =   7200
      Style           =   1  'Graphical
      TabIndex        =   37
      Top             =   2040
      Visible         =   0   'False
      Width           =   975
   End
   Begin VB.Frame Frame2 
      Caption         =   "Ultimo Usuario"
      Height          =   975
      Left            =   360
      TabIndex        =   27
      Top             =   2640
      Visible         =   0   'False
      Width           =   7695
      Begin VB.CommandButton Command5 
         Caption         =   "Devolver"
         Height          =   315
         Left            =   6720
         TabIndex        =   38
         Top             =   240
         Width           =   855
      End
      Begin VB.CommandButton Command4 
         Caption         =   "Ver"
         Height          =   315
         Left            =   6720
         TabIndex        =   36
         Top             =   600
         Width           =   855
      End
      Begin VB.TextBox txtIdSo 
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   9.6
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   375
         Left            =   5760
         MaxLength       =   15
         TabIndex        =   31
         Top             =   480
         Width           =   735
      End
      Begin VB.TextBox txtfecp 
         Height          =   375
         Left            =   120
         MaxLength       =   50
         TabIndex        =   30
         Top             =   480
         Width           =   2295
      End
      Begin VB.TextBox txtfecd 
         Height          =   375
         Left            =   2640
         TabIndex        =   29
         Top             =   480
         Width           =   2295
      End
      Begin VB.TextBox txtdias 
         Height          =   375
         Left            =   5040
         TabIndex        =   28
         Top             =   480
         Width           =   495
      End
      Begin VB.Label Label3 
         AutoSize        =   -1  'True
         BackColor       =   &H00C0FFFF&
         Caption         =   "Id Socio "
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   7.8
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   195
         Index           =   0
         Left            =   5760
         TabIndex        =   35
         Top             =   240
         Width           =   780
      End
      Begin VB.Label Label4 
         AutoSize        =   -1  'True
         BackColor       =   &H00C0FFFF&
         Caption         =   "Fecha de prestamo de libro"
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   7.8
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   195
         Index           =   0
         Left            =   120
         TabIndex        =   34
         Top             =   240
         Width           =   2445
      End
      Begin VB.Label Label4 
         AutoSize        =   -1  'True
         BackColor       =   &H00C0FFFF&
         Caption         =   "Fecha de devolucion"
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   7.8
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   195
         Index           =   1
         Left            =   2640
         TabIndex        =   33
         Top             =   240
         Width           =   1800
      End
      Begin VB.Label Label7 
         BackColor       =   &H00C0FFFF&
         Caption         =   "Dias"
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   7.8
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   255
         Left            =   5040
         TabIndex        =   32
         Top             =   240
         Width           =   495
      End
   End
   Begin VB.TextBox txtesta 
      Height          =   375
      Left            =   5640
      Locked          =   -1  'True
      TabIndex        =   26
      Top             =   2040
      Width           =   1335
   End
   Begin VB.Frame FrameABM 
      BackColor       =   &H00C0FFFF&
      Height          =   615
      Left            =   240
      TabIndex        =   16
      Top             =   3720
      Visible         =   0   'False
      Width           =   7935
      Begin VB.CommandButton cmdnue 
         Caption         =   "&Nuevo"
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   12
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   375
         Left            =   0
         TabIndex        =   22
         Top             =   120
         Width           =   1095
      End
      Begin VB.CommandButton cmdbor 
         Caption         =   "&Borrar"
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   12
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   375
         Left            =   1200
         TabIndex        =   21
         Top             =   120
         Width           =   975
      End
      Begin VB.CommandButton cmdcan 
         Caption         =   "&Cancelar"
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   12
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   375
         Left            =   5160
         TabIndex        =   20
         Top             =   120
         Width           =   1335
      End
      Begin VB.CommandButton cmdreg 
         Caption         =   "&Registrar"
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   12
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   375
         Left            =   3720
         TabIndex        =   19
         Top             =   120
         Width           =   1335
      End
      Begin VB.CommandButton cmdsal 
         Caption         =   "&Salir"
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   12
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   375
         Left            =   6600
         TabIndex        =   18
         Top             =   120
         Width           =   1335
      End
      Begin VB.CommandButton cmdmod 
         Caption         =   "&Modificar"
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   12
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   375
         Left            =   2280
         TabIndex        =   17
         Top             =   120
         Width           =   1335
      End
   End
   Begin VB.Frame Frame1 
      BackColor       =   &H00FFC0C0&
      Caption         =   "Busqueda"
      Height          =   3135
      Left            =   240
      TabIndex        =   8
      Top             =   4440
      Visible         =   0   'False
      Width           =   7935
      Begin VB.TextBox txtnombre 
         Height          =   285
         Left            =   3480
         MaxLength       =   29
         TabIndex        =   24
         Top             =   240
         Width           =   2055
      End
      Begin VB.CommandButton Command3 
         Caption         =   "No Buscar"
         Height          =   255
         Left            =   5880
         TabIndex        =   23
         Top             =   960
         Width           =   1935
      End
      Begin VB.CommandButton Command2 
         Caption         =   "Todos los registros"
         Height          =   255
         Left            =   5880
         TabIndex        =   15
         Top             =   600
         Width           =   1935
      End
      Begin VB.TextBox txtbleg 
         Height          =   285
         Left            =   120
         MaxLength       =   6
         TabIndex        =   12
         Top             =   240
         Width           =   855
      End
      Begin VB.TextBox txtbape 
         Height          =   285
         Left            =   1200
         MaxLength       =   29
         TabIndex        =   11
         Top             =   240
         Width           =   2055
      End
      Begin VB.CommandButton Command1 
         Caption         =   "Iniciar Consulta"
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   9.6
            Charset         =   0
            Weight          =   700
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   255
         Left            =   5880
         TabIndex        =   10
         Top             =   240
         Width           =   1935
      End
      Begin MSFlexGridLib.MSFlexGrid grilla 
         Height          =   1815
         Left            =   240
         TabIndex        =   9
         Top             =   1200
         Visible         =   0   'False
         Width           =   7695
         _ExtentX        =   13568
         _ExtentY        =   3196
         _Version        =   393216
      End
      Begin VB.Label Label8 
         Caption         =   "Por letras ó Autor Completo"
         Height          =   255
         Left            =   3480
         TabIndex        =   25
         Top             =   600
         Width           =   2055
      End
      Begin VB.Label Label5 
         Caption         =   "Por IdLibro"
         Height          =   255
         Left            =   120
         TabIndex        =   14
         Top             =   600
         Width           =   855
      End
      Begin VB.Label Label6 
         Caption         =   "Por letras ó Titulo Completo"
         Height          =   255
         Left            =   1200
         TabIndex        =   13
         Top             =   600
         Width           =   2055
      End
   End
   Begin VB.CommandButton cmdbus 
      Caption         =   "&Buscar"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   12
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   375
      Left            =   2040
      TabIndex        =   0
      Top             =   720
      Width           =   1095
   End
   Begin VB.TextBox txtnom 
      Height          =   375
      Left            =   2880
      MaxLength       =   30
      TabIndex        =   3
      Top             =   2040
      Width           =   2415
   End
   Begin VB.TextBox txtape 
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.6
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   375
      Left            =   360
      MaxLength       =   20
      TabIndex        =   2
      Top             =   2040
      Width           =   2295
   End
   Begin VB.TextBox txtid 
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.6
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   375
      Left            =   360
      Locked          =   -1  'True
      MaxLength       =   4
      TabIndex        =   1
      Top             =   720
      Width           =   1095
   End
   Begin VB.Label Label2 
      AutoSize        =   -1  'True
      BackColor       =   &H00C0FFFF&
      Caption         =   "Esta Disponible"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   7.8
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   195
      Index           =   3
      Left            =   5640
      TabIndex        =   7
      Top             =   1800
      Width           =   1335
   End
   Begin VB.Label Label2 
      AutoSize        =   -1  'True
      BackColor       =   &H00C0FFFF&
      Caption         =   "Autor del Libro"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   7.8
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   195
      Index           =   1
      Left            =   2880
      TabIndex        =   6
      Top             =   1800
      Width           =   1260
   End
   Begin VB.Label Label2 
      AutoSize        =   -1  'True
      BackColor       =   &H00C0FFFF&
      Caption         =   "Titulo del Libro"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   7.8
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   195
      Index           =   0
      Left            =   360
      TabIndex        =   5
      Top             =   1800
      Width           =   1290
   End
   Begin VB.Label Label1 
      AutoSize        =   -1  'True
      BackColor       =   &H00C0FFFF&
      Caption         =   "Id Libro"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   7.8
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   195
      Left            =   360
      TabIndex        =   4
      Top             =   360
      Width           =   1140
   End
End
Attribute VB_Name = "frmLib"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Public Sub cmdbus_Click()
mancmd Me, "bus"
Frame1.Visible = True
txtbleg.Locked = False
txtbape.Locked = False
txtbleg.SetFocus
End Sub
Private Sub cmdbor_Click()
mancmd Me, "bor"
ini
If rsc1.State = 1 Then rsc1.Close
If MsgBox("ESTA SEGURO DE DAR DE BAJA ESTE REGISTRO???", vbYesNo, "PRECAUCION!! Se dar  de baja un REGISTRO") = vbYes Then
rsc1.Open "Libros", cn, adOpenStatic, adLockOptimistic
Do While rsc1.EOF = False
If rsc1!IdLibro = txtid Then
Exit Do
End If
rsc1.MoveNext
Loop
rsc1!Activo = "No"
rsc1.Update
rsc1.MoveLast
rsc1.Close
MsgBox "La Operación se ha efectuado satifactoriamente"
End If
cmdcan_Click
fin
End Sub
Public Sub cmdcan_Click()
limpia Me
mancmd Me, "can"
fgrilla
Frame1.Visible = False
End Sub

Private Sub cmdmod_Click()
mancmd Me, "mod"
modi = 1
End Sub

Private Sub cmdnue_Click()
txtApe.SetFocus
mancmd Me, "nue"
modi = 0
ini
rsc1.Open "Select * from Libros", cn, adOpenStatic, adLockOptimistic
txtid = rsc1.RecordCount + 1
rsc1.Close
IdCli = 1
fin
End Sub

Private Sub cmdpres_Click()
FrmPres.txtidL = txtid
FrmPres.txttit = txtnom
FrmPres.Show
Unload Me
End Sub

Private Sub cmdreg_Click()
ini
                                If rsc1.State = 1 Then rsc1.Close
On Error GoTo xerror
mancmd Me, "reg"
If modi = 1 Then
cn.Execute "Update Libros Set Titulo = '" & txtApe & "', Autor = '" & _
txtnom & "', Estado = '" & txtesta & "', Socio = " & txtIdSo & ", FecPres = #" & txtfecp & _
"#, FecDev = #" & txtfecd & "#, dias = " & txtdias & " Where IdLibro = " & txtid

Else
rsc1.Open "Select IdLibro from Libros order by IdLibro", cn, adOpenStatic, adLockOptimistic
If rsc1.RecordCount > 0 Then
rsc1.MoveLast
IdCli = rsc1!IdLibro + 1
Else
IdCli = 1
End If
                                If rsc1.State = 1 Then rsc1.Close
cn.Execute "Insert Into Libros Values(" & IdCli & ", '" & txtApe & "', '" & txtnom & _
"', '" & txtesta & "', " & txtIdSo & ", #" & txtfecp & "#, #" & txtfecd & "#, " & txtdias & ", 'Si' )"
End If
MsgBox "Operacion exitosa"
cmdcan_Click
cmdbus.Enabled = False
FrameABM.Visible = False
Frame2.Visible = False
fin
Exit Sub
xerror:
If Err.Number = -2147217900 Then
MsgBox "Tiene  que completar los datos faltantes"
fin
Exit Sub
End If
MsgBox " No se realizó operacion por: " & Err.Description & Err.Number
fin
End Sub

Private Sub cmdsal_Click()
Unload Me
End Sub

Private Sub Command2_Click()
txtbape = "%"
Command1_Click
End Sub



Private Sub Command3_Click()
Frame1.Visible = False
FrameABM.Visible = True
cmdnue.Enabled = True
End Sub

Private Sub Command4_Click()
ini
If rsc1.State = 1 Then rsc1.Close
rsc1.Open "Select Apellidos, Nombres, Domicilio, Telefono From Cliente where IdCliente = " & _
txtIdSo, cn, adOpenStatic, adLockOptimistic
MsgBox "Socio: " & rsc1.Fields(0) & "; " & rsc1.Fields(1) & "; Dir: " & rsc1.Fields(2) & _
"; Tel: " & rsc1.Fields(3), vbInformation, "[BIBLIOTECA] Datos del Socio "
If rsc1.State = 1 Then rsc1.Close
fin
End Sub

Private Sub Command5_Click()
ini
If MsgBox("ESTA SEGUO REGISTRAR ESTE" & Chr(13) & _
"LIBRO COMO DEVUELTO?", vbYesNo, "[BIBLIOTECA]Devolucion Libros") = vbYes Then

cn.Execute "Update Libros Set  Estado = 'Si' Where IdLibro = " & txtid
txtesta = "Si"
Frame2.Visible = False
End If
fin
End Sub

Private Sub Command6_Click()
frmAYUDA.Show
End Sub

Private Sub Form_Activate()
Me.Top = 1
Me.Left = 1000
ini '//funcion que conecta a la base de datos
'mancmd Me, "ini"
End Sub

Private Sub grilla_Click()

With grilla
If .RowSel < 1 Then Exit Sub
txtid = .TextMatrix(.RowSel, 0)
txtApe = .TextMatrix(.RowSel, 1)
txtnom = .TextMatrix(.RowSel, 2)
txtesta = .TextMatrix(.RowSel, 3)
If .TextMatrix(.RowSel, 3) = "No" Then
Frame2.Visible = True
cmdpres.Visible = False
Else:
Frame2.Visible = False
cmdpres.Visible = True
End If

txtIdSo = .TextMatrix(.RowSel, 4)
txtfecp = .TextMatrix(.RowSel, 5)
txtfecd = .TextMatrix(.RowSel, 6)
txtdias = .TextMatrix(.RowSel, 7)
End With

cmdmod.Enabled = True
cmdbor.Enabled = True
cmdreg.Enabled = False
cmdnue.Enabled = False
'FrameABM.Visible = True
Frame1.Visible = False

End Sub

Private Sub Command1_Click() 'Busca por legajo o nombre
'//la linea siguiente hace una rutina saltando el error para
'//que no se clave el programa, activar una vez que este todo Ok

'On Error GoTo xerror
ini
fgrilla
If rsc1.State = 1 Then rsc1.Close
With grilla
If txtbleg = "" And txtbape <> "" And txtnombre = "" Then
    rsc1.Open "Select * From Libros Where Activo = 'Si' And Titulo like '" & txtbape & "%'", cn, adOpenStatic, adLockOptimistic
    Do While rsc1.EOF = False
    .AddItem rsc1.Fields(0) & vbTab & rsc1.Fields(1) & vbTab & rsc1.Fields(2) & vbTab & rsc1.Fields(3) & vbTab & rsc1.Fields(4) & vbTab & rsc1.Fields(5) & _
    vbTab & rsc1.Fields(6) & vbTab & rsc1.Fields(7)
    rsc1.MoveNext
    Loop
    If rsc1.RecordCount = 0 Then MsgBox "No se encontró registro que coincida con las caracteristicas pedidas", vbInformation, "NO HAY REGISTROS QUE MOSTRAR"
    rsc1.Close
    .Visible = True
ElseIf txtbleg = "" And txtbape = "" And txtnombre <> "" Then
    rsc1.Open "Select * From Libros Where Activo = 'Si' And Autor like '" & txtnombre & "%'", cn, adOpenStatic, adLockOptimistic
    Do While rsc1.EOF = False
    .AddItem rsc1.Fields(0) & vbTab & rsc1.Fields(1) & vbTab & rsc1.Fields(2) & vbTab & rsc1.Fields(3) & vbTab & rsc1.Fields(4) & vbTab & rsc1.Fields(5) & _
    vbTab & rsc1.Fields(6) & vbTab & rsc1.Fields(7)
    rsc1.MoveNext
    Loop
    If rsc1.RecordCount = 0 Then MsgBox "No se encontró registro que coincida con las caracteristicas pedidas", vbInformation, "NO HAY REGISTROS QUE MOSTRAR"
    rsc1.Close
    .Visible = True
ElseIf txtbleg <> "" And txtbape = "" And txtnombre = "" Then
    rsc1.Open "SELECT * From Libros Where Activo = 'Si' And IdLibro = " & txtbleg.Text, cn, adOpenStatic, adLockOptimistic
    Do While rsc1.EOF = False
    .AddItem rsc1.Fields(0) & vbTab & rsc1.Fields(1) & vbTab & rsc1.Fields(2) & vbTab & rsc1.Fields(3) & vbTab & rsc1.Fields(4) & vbTab & rsc1.Fields(5) & _
    vbTab & rsc1.Fields(6) & vbTab & rsc1.Fields(7)
    rsc1.MoveNext
    Loop
    If rsc1.RecordCount = 0 Then MsgBox "No se encontró registro que coincida con las caracteristicas pedidas", vbInformation, "NO HAY REGISTROS QUE MOSTRAR"
    rsc1.Close
.Visible = True

Else
MsgBox "INGRESE UN DATO PARA LA BUSQUEDA", vbExclamation, "FALTA O EXCESO DE DATOS INGRESADOS"
txtbleg.SetFocus
txtbleg = ""
txtbape = ""
End If

End With
fin
Exit Sub
xerror:
MsgBox "NO SE PUDO BUSCAR POR: " & Err.Description, vbCritical, "NO SE EFECTUO EL PROCEDIMIENTO"
fin
End Sub '----------------------------------------------------------------------

Public Sub fgrilla()
With grilla
.FormatString = "IdL|Titulo |Autor |Está|Socio|Fecha Prestamo|Fecha Devolucion|Dias"
.ColWidth(0) = 12
.ColWidth(1) = 2000
.ColWidth(2) = 2000
.ColWidth(3) = 500
.ColWidth(4) = 500
.ColWidth(5) = 1000
.ColWidth(6) = 1000
.ColWidth(7) = 500

.Rows = 1
End With
End Sub




Private Sub TxtApe_KeyPress(KeyAscii As Integer)
If KeyAscii = 13 Then
SendKeys "{Tab}" '//permite que cambie de texto con el enter
KeyAscii = 0
End If

End Sub

Private Sub TxtDir_KeyPress(KeyAscii As Integer)
If KeyAscii = 13 Then
SendKeys "{Tab}" '//permite que cambie de texto con el enter
KeyAscii = 0
End If
If txtdir <> "" And txtApe <> "" Then
cmdreg.Enabled = True
End If
End Sub

Private Sub txtesta_Change()
If txtApe <> "" And txtnom <> "" And txtesta = No Then
Frame2.Visible = True
Else
cmdpres.Visible = True
End If
End Sub

Private Sub txtesta_KeyPress(KeyAscii As Integer)
If KeyAscii = 13 And txtesta = "Si" Then
cmdpres.Visible = False
Frame2.Visible = True
cmdreg.Enabled = True
txtfecp = Format(Now, "dd/mm/yyyy")
txtfecd = Format(Now, "dd/mm/yyyy")
txtdias = 0
txtIdSo = -1
End If
End Sub

Private Sub Txtnom_Change()
If txtApe <> "" And txtdir <> "" Then
cmdreg.Enabled = True
End If
End Sub

Private Sub Txtnom_KeyPress(KeyAscii As Integer)
If KeyAscii = 13 Then
SendKeys "{Tab}" '//permite que cambie de texto con el enter
KeyAscii = 0
End If
End Sub


Private Sub txtbape_KeyPress(KeyAscii As Integer)
If KeyAscii = 13 Then
Command1_Click
KeyAscii = 0
End If
End Sub

Private Sub txtbleg_KeyPress(KeyAscii As Integer)
If KeyAscii = 13 Then
txtbape.SetFocus
KeyAscii = 0
End If
End Sub

