VERSION 5.00
Begin VB.Form Form1 
   BackColor       =   &H00C0C0C0&
   BorderStyle     =   1  'Fixed Single
   Caption         =   "Acceso al Programa"
   ClientHeight    =   1452
   ClientLeft      =   48
   ClientTop       =   336
   ClientWidth     =   3372
   LinkTopic       =   "Form7"
   MaxButton       =   0   'False
   MDIChild        =   -1  'True
   MinButton       =   0   'False
   Moveable        =   0   'False
   ScaleHeight     =   1452
   ScaleWidth      =   3372
   Begin VB.CommandButton cmdsal 
      Caption         =   "Salir"
      Height          =   375
      Left            =   1680
      TabIndex        =   2
      Top             =   840
      Width           =   1095
   End
   Begin VB.CommandButton cmdace 
      Caption         =   "Aceptar"
      Height          =   375
      Left            =   480
      TabIndex        =   1
      Top             =   840
      Width           =   975
   End
   Begin VB.TextBox txtlog 
      Height          =   405
      IMEMode         =   3  'DISABLE
      Left            =   480
      MaxLength       =   30
      PasswordChar    =   "*"
      TabIndex        =   0
      Tag             =   "sapo"
      Top             =   240
      Width           =   2295
   End
   Begin VB.Label E 
      Caption         =   "Ingrese su ""LOGUIN"""
      Height          =   255
      Left            =   480
      TabIndex        =   3
      Top             =   0
      Width           =   2295
   End
End
Attribute VB_Name = "Form1"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Dim cont%
Private Sub cmdace_Click()
If txtlog.Tag = txtlog.Text Then
MDIForm1.socios.Enabled = True
MDIForm1.libros.Enabled = True

MDIForm1.ayuda.Enabled = True

MsgBox "Contraseña aceptada", vbInformation, "ACCESO A BIBLIOTECA"

Unload Me
Else
MsgBox "Contraseña Rechazada", vbCritical, "ACCESO A BIBLIOTECA"
cont = cont + 1
txtlog = ""
MDIForm1.socios.Enabled = False
MDIForm1.libros.Enabled = False

MDIForm1.ayuda = True
If cont > 4 Then End
End If
fin
End Sub

Private Sub cmdsal_Click()
Unload Me
End Sub

Private Sub Form_Load()
ini
rsc1.Open "Select pass from clave", cn, adOpenStatic, adLockBatchOptimistic
If rsc1.Fields(0) <> "" Then txtlog.Tag = rsc1.Fields(0)
End Sub

Private Sub txtlog_KeyPress(KeyAscii As Integer)
If KeyAscii = 13 Then cmdace_Click
End Sub
