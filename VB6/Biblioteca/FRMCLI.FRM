VERSION 5.00
Object = "{5E9E78A0-531B-11CF-91F6-C2863C385E30}#1.0#0"; "MSFLXGRD.OCX"
Begin VB.Form frmCli 
   BackColor       =   &H00FFC0C0&
   BorderStyle     =   1  'Fixed Single
   Caption         =   "Registro Clientes "
   ClientHeight    =   7128
   ClientLeft      =   3756
   ClientTop       =   2760
   ClientWidth     =   8604
   Icon            =   "FRMCLI.frx":0000
   LinkTopic       =   "Form1"
   MaxButton       =   0   'False
   MDIChild        =   -1  'True
   MinButton       =   0   'False
   Picture         =   "FRMCLI.frx":030A
   ScaleHeight     =   7128
   ScaleWidth      =   8604
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
      Height          =   495
      Left            =   7440
      Style           =   1  'Graphical
      TabIndex        =   29
      Top             =   0
      Width           =   495
   End
   Begin VB.Frame FrameABM 
      BackColor       =   &H00C0FFFF&
      Height          =   615
      Left            =   240
      TabIndex        =   21
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
         TabIndex        =   27
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
         TabIndex        =   26
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
         TabIndex        =   25
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
         TabIndex        =   24
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
         TabIndex        =   23
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
         TabIndex        =   22
         Top             =   120
         Width           =   1335
      End
   End
   Begin VB.Frame Frame1 
      BackColor       =   &H00FFC0C0&
      Caption         =   "Busqueda"
      Height          =   2655
      Left            =   240
      TabIndex        =   13
      Top             =   4320
      Visible         =   0   'False
      Width           =   7935
      Begin VB.CommandButton Command3 
         Caption         =   "No Buscar"
         Height          =   255
         Left            =   4680
         TabIndex        =   28
         Top             =   960
         Width           =   1935
      End
      Begin VB.CommandButton Command2 
         Caption         =   "Todos los registros"
         Height          =   255
         Left            =   4680
         TabIndex        =   20
         Top             =   600
         Width           =   1935
      End
      Begin VB.TextBox txtbleg 
         Height          =   285
         Left            =   600
         MaxLength       =   6
         TabIndex        =   17
         Top             =   240
         Width           =   855
      End
      Begin VB.TextBox txtbape 
         Height          =   285
         Left            =   1800
         MaxLength       =   29
         TabIndex        =   16
         Top             =   240
         Width           =   2655
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
         Left            =   4680
         TabIndex        =   15
         Top             =   240
         Width           =   1935
      End
      Begin MSFlexGridLib.MSFlexGrid grilla 
         Height          =   1335
         Left            =   240
         TabIndex        =   14
         Top             =   1200
         Visible         =   0   'False
         Width           =   7695
         _ExtentX        =   13568
         _ExtentY        =   2350
         _Version        =   393216
      End
      Begin VB.Label Label5 
         Caption         =   "Por IdCliente"
         Height          =   255
         Left            =   360
         TabIndex        =   19
         Top             =   600
         Width           =   1095
      End
      Begin VB.Label Label6 
         Caption         =   "Por letras ó Apellido Completo   Si ingresa  % verá todos los registros"
         Height          =   375
         Left            =   1800
         TabIndex        =   18
         Top             =   600
         Width           =   2655
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
      Top             =   600
      Width           =   1095
   End
   Begin VB.TextBox txtDNI 
      Height          =   375
      Left            =   5400
      MaxLength       =   10
      TabIndex        =   4
      Top             =   2160
      Width           =   1815
   End
   Begin VB.TextBox txtnom 
      Height          =   375
      Left            =   2760
      MaxLength       =   30
      TabIndex        =   3
      Top             =   2160
      Width           =   2415
   End
   Begin VB.TextBox txtdir 
      Height          =   375
      Left            =   360
      MaxLength       =   50
      TabIndex        =   6
      Top             =   3120
      Width           =   4815
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
      Top             =   2160
      Width           =   2055
   End
   Begin VB.TextBox txttel 
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
      Left            =   5400
      MaxLength       =   15
      TabIndex        =   5
      Top             =   3120
      Width           =   2655
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
      Left            =   720
      Locked          =   -1  'True
      MaxLength       =   4
      TabIndex        =   1
      Top             =   600
      Width           =   1095
   End
   Begin VB.Label Label2 
      AutoSize        =   -1  'True
      BackColor       =   &H00C0FFFF&
      Caption         =   "Nº Documento del Socio"
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
      Left            =   5400
      TabIndex        =   12
      Top             =   1680
      Width           =   2100
   End
   Begin VB.Label Label2 
      AutoSize        =   -1  'True
      BackColor       =   &H00C0FFFF&
      Caption         =   "Nombres del Socio"
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
      TabIndex        =   11
      Top             =   1680
      Width           =   1605
   End
   Begin VB.Label Label4 
      AutoSize        =   -1  'True
      BackColor       =   &H00C0FFFF&
      Caption         =   "Direccion del Socio"
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
      TabIndex        =   10
      Top             =   2760
      Width           =   1680
   End
   Begin VB.Label Label3 
      AutoSize        =   -1  'True
      BackColor       =   &H00C0FFFF&
      Caption         =   " Teléfono del Socio"
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
      Left            =   5400
      TabIndex        =   9
      Top             =   2760
      Width           =   1680
   End
   Begin VB.Label Label2 
      AutoSize        =   -1  'True
      BackColor       =   &H00C0FFFF&
      Caption         =   "Apellidos Socio"
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
      TabIndex        =   8
      Top             =   1800
      Width           =   1320
   End
   Begin VB.Label Label1 
      AutoSize        =   -1  'True
      BackColor       =   &H00C0FFFF&
      Caption         =   "Id Socio"
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
      Left            =   720
      TabIndex        =   7
      Top             =   360
      Width           =   720
   End
End
Attribute VB_Name = "frmCli"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Private Sub cmdbus_Click()
mancmd Me, "bus"
Frame1.Visible = True
txtbleg.Locked = False
txtbape.Locked = False
txtbleg.SetFocus
End Sub
Private Sub cmdbor_Click()
ini
mancmd Me, "bor"
If rsc1.State = 1 Then rsc1.Close
If MsgBox("ESTA SEGURO DE DAR DE BAJA ESTE REGISTRO???", vbYesNo, "PRECAUCION!! Se dar  de baja un REGISTRO") = vbYes Then
rsc1.Open "Cliente", cn, adOpenStatic, adLockOptimistic
Do While rsc1.EOF = False
If rsc1!IdCliente = txtid Then
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
Private Sub cmdcan_Click()
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
rsc1.Open "Select * from Cliente", cn, adOpenStatic, adLockOptimistic
txtid = rsc1.RecordCount + 1
rsc1.Close
IdCli = 1
fin
End Sub

Private Sub cmdreg_Click()
ini
                                If rsc1.State = 1 Then rsc1.Close
'On Error GoTo xerror
mancmd Me, "reg"
If modi = 1 Then
cn.Execute "Update Cliente Set Apellidos = '" & txtApe & "', Nombres = '" & _
txtnom & "', NºDoc = '" & txtDNI & "', Domicilio = '" & txtdir & "', Telefono = '" & txttel & "' Where IdCliente = " & txtid



Else
rsc1.Open "Select IdCliente from Cliente order by IdCliente", cn, adOpenStatic, adLockOptimistic
If rsc1.RecordCount > 0 Then
rsc1.MoveLast
IdCli = rsc1!IdCliente + 1
Else
IdCli = 1
End If
                                If rsc1.State = 1 Then rsc1.Close
cn.Execute "Insert Into Cliente Values(" & IdCli & ", '" & txtApe & "', '" & txtnom & _
"', '" & txtDNI & "', '" & txtdir & "', '" & txttel & "', 'Si')"
End If
MsgBox "Operacion exitosa"
cmdcan_Click
FrameABM.Visible = False
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
frmAYUDA.Show
End Sub

Private Sub Form_Activate()
Me.Top = 1
Me.Left = 1000
ini '//funcion que conecta a la base de datos
mancmd Me, "ini"
End Sub

Private Sub grilla_Click()

With grilla
If .RowSel < 1 Then Exit Sub
txtid = .TextMatrix(.RowSel, 0)
txtApe = .TextMatrix(.RowSel, 1)
txtnom = .TextMatrix(.RowSel, 2)
txtDNI = .TextMatrix(.RowSel, 3)
txtdir = .TextMatrix(.RowSel, 4)
txttel = .TextMatrix(.RowSel, 5)
End With

cmdmod.Enabled = True
cmdbor.Enabled = True
cmdreg.Enabled = False
cmdnue.Enabled = False
FrameABM.Visible = True
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
If txtbleg = "" And txtbape <> "" Then
rsc1.Open "Select * From Cliente Where Activo = 'Si' And Apellidos like '" & txtbape & "%'", cn, adOpenStatic, adLockOptimistic
Do While rsc1.EOF = False
.AddItem rsc1.Fields(0) & vbTab & rsc1.Fields(1) & vbTab & rsc1.Fields(2) & vbTab & rsc1.Fields(3) & vbTab & rsc1.Fields(4) & vbTab & rsc1.Fields(5)
rsc1.MoveNext
Loop
If rsc1.RecordCount = 0 Then MsgBox "No se encontró registro que coincida con las caracteristicas pedidas", vbInformation, "NO HAY REGISTROS QUE MOSTRAR"
rsc1.Close
.Visible = True
ElseIf txtbleg <> "" And txtbape = "" Then
rsc1.Open "SELECT * From Cliente Where Activo = 'Si' And IdCliente = " & txtbleg.Text, cn, adOpenStatic, adLockOptimistic
Do While rsc1.EOF = False
.AddItem rsc1.Fields(0) & vbTab & rsc1.Fields(1) & vbTab & rsc1.Fields(2) & vbTab & rsc1.Fields(3) & vbTab & rsc1.Fields(4) & vbTab & rsc1.Fields(5)
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
.FormatString = "IdCliente|Apellido|Nombres|Nº Documento|Domicilio|Telefono"
.ColWidth(0) = 12
.ColWidth(1) = 1200
.ColWidth(2) = 2000
.ColWidth(3) = 1200
.ColWidth(4) = 2100
.ColWidth(5) = 1000
.Rows = 1
End With
End Sub


Private Sub TxtTel_Change()
If txtApe <> "" And txtdir <> "" Then
cmdreg.Enabled = True
Else
cmdreg.Enabled = False
End If
End Sub

Private Sub txtdir_Change()
If txtdir <> "" And txtApe <> "" Then
cmdreg.Enabled = True
End If
End Sub

Private Sub txtDNGA_KeyPress(KeyAscii As Integer)
KeyAscii = sinum(KeyAscii)
End Sub

Private Sub txttel_KeyPress(KeyAscii As Integer)
If KeyAscii = 13 Then
SendKeys "{Tab}" '//permite que cambie de texto con el enter
KeyAscii = 0
End If
End Sub

Private Sub Txtdni_Change()
If txtdir <> "" And txtApe <> "" Then
cmdreg.Enabled = True
End If

End Sub

Private Sub Txtdni_KeyPress(KeyAscii As Integer)
If KeyAscii = 13 Then
SendKeys "{Tab}" '//permite que cambie de texto con el enter
KeyAscii = 0
End If
KeyAscii = sinum(KeyAscii)
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

