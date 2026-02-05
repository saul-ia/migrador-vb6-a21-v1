Attribute VB_Name = "Module1"
Public cn As New ADODB.Connection
Public rsc1 As New ADODB.Recordset
Public modi%, cl%
Public Function sinum(tx As Integer)
Dim C$
C = Chr(tx)
If InStr("0123456789," & Chr(8), C) = 0 Then
sinum = 0
Else
sinum = tx
End If
End Function
Public Function limpia(fr As Form)
Dim ct As Control
For Each ct In fr
If TypeOf ct Is TextBox Then ct.Text = ""
Next
End Function
Public Sub ini()
If cn.State = 1 Then cn.Close
cn.Open "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" & App.Path & "\Conexion\biblioteca.mdb;Persist Security Info=False"
End Sub

Public Sub fin()
cn.Close
End Sub


Public Function silet(C As Integer) As Integer
Dim a$
a = Chr(C)
If InStr("abcdefghijklmnopqrstuvwxyz·ÈÌÛ˙ABCDEFGHYJKLMNOPQRSTUVWXYZ, " & Chr(8), a) = 0 Then
letra = 0
Else
letra = C
End If
End Function

Public Function mancmd(Parform As Form, hace As String)
With Parform
Select Case hace
Case "ini"
.cmdnue.Enabled = True
.cmdmod.Enabled = False
.cmdreg.Enabled = False
.cmdbus.Enabled = True
.cmdcan.Enabled = False
.cmdbor.Enabled = False

Case "ver"
.cmdnue.Enabled = True
.cmdmod.Enabled = True
.cmdreg.Enabled = False
.cmdbus.Enabled = True
.cmdcan.Enabled = False
.cmdbor.Enabled = True

Case "nue"
.cmdnue.Enabled = False
.cmdmod.Enabled = False
.cmdreg.Enabled = False
.cmdbus.Enabled = False
.cmdcan.Enabled = True
.cmdbor.Enabled = False

Case "mod"
.cmdnue.Enabled = False
.cmdmod.Enabled = False
.cmdreg.Enabled = True
.cmdbus.Enabled = False
.cmdcan.Enabled = True
.cmdbor.Enabled = False

Case "reg"
.cmdnue.Enabled = True
.cmdmod.Enabled = False
.cmdreg.Enabled = True
.cmdbus.Enabled = False
.cmdcan.Enabled = True
.cmdbor.Enabled = False

Case "can"
.cmdnue.Enabled = True
.cmdmod.Enabled = False
.cmdreg.Enabled = False
.cmdbus.Enabled = True
.cmdcan.Enabled = False
.cmdbor.Enabled = False

Case "bus"
.cmdnue.Enabled = False
.cmdmod.Enabled = False
.cmdreg.Enabled = False
.cmdbus.Enabled = False
.cmdcan.Enabled = True
.cmdbor.Enabled = False

End Select
End With
End Function


