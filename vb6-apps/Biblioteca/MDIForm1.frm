VERSION 5.00
Begin VB.MDIForm MDIForm1 
   BackColor       =   &H8000000C&
   Caption         =   "BIBLIOTECA"
   ClientHeight    =   7368
   ClientLeft      =   132
   ClientTop       =   804
   ClientWidth     =   8628
   Icon            =   "MDIForm1.frx":0000
   LinkTopic       =   "MDIForm1"
   Picture         =   "MDIForm1.frx":030A
   StartUpPosition =   3  'Windows Default
   WindowState     =   2  'Maximized
   Begin VB.Menu ingreso 
      Caption         =   "Ingreso"
      Begin VB.Menu pass 
         Caption         =   "Password"
      End
      Begin VB.Menu Sep0 
         Caption         =   "-"
      End
      Begin VB.Menu cerses 
         Caption         =   "Cerrar Sesion"
      End
   End
   Begin VB.Menu socios 
      Caption         =   "| Socios"
      Enabled         =   0   'False
   End
   Begin VB.Menu libros 
      Caption         =   "|Libros"
      Enabled         =   0   'False
      Begin VB.Menu BuscaL 
         Caption         =   "Buscar Libro"
      End
      Begin VB.Menu Separa1 
         Caption         =   "-"
      End
      Begin VB.Menu cargal 
         Caption         =   "Cargar Libros"
      End
   End
   Begin VB.Menu ayuda 
      Caption         =   "| Ayuda "
      Enabled         =   0   'False
   End
   Begin VB.Menu salir 
      Caption         =   " | Salir |"
   End
End
Attribute VB_Name = "MDIForm1"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Private Sub ayuda_Click()
frmAYUDA.Show
End Sub

Private Sub bd_Click()
Form2.Show
End Sub

Private Sub BuscaL_Click()
frmLib.Show
End Sub

Private Sub cargal_Click()
frmLib.FrameABM.Visible = True
frmLib.cmdcan_Click
frmLib.cmdbus.Enabled = False

frmLib.Show
End Sub

Private Sub cerses_Click()
MDIForm1.socios = False
MDIForm1.libros.Enabled = False
End Sub

Private Sub pass_Click()
Form1.Show
End Sub

Private Sub salir_Click()
End
End Sub

Private Sub socios_Click()
frmCli.Show
End Sub
