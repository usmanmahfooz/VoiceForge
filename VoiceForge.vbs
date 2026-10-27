' VoiceForge - Silent Launcher
' Double-click to start VoiceForge and open its browser interface.

Dim WshShell, fso, scriptDir, pythonPath, serverScript
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
venvPath = scriptDir & "\runtime\venv\Scripts\python.exe"
portablePath = scriptDir & "\runtime\python_portable\python.exe"
serverScript = scriptDir & "\engine\server.py"

If fso.FileExists(venvPath) Then
    pythonPath = venvPath
ElseIf fso.FileExists(portablePath) Then
    pythonPath = portablePath
Else
    pythonPath = "python"
End If

If Not fso.FileExists(serverScript) Then
    MsgBox "Error: engine\server.py not found!" & vbCrLf & "Please run Setup.bat first.", vbCritical, "VoiceForge"
    WScript.Quit
End If

If Not fso.FileExists(venvPath) Then
    returnCode = WshShell.Run("cmd /c """ & scriptDir & "\Setup.bat""", 1, True)
    If Not fso.FileExists(venvPath) Then
        MsgBox "Installation was not completed. Please run Setup.bat manually.", vbExclamation, "VoiceForge"
        WScript.Quit
    End If
    pythonPath = venvPath
End If

If Not fso.FolderExists(scriptDir & "\logs") Then
    fso.CreateFolder(scriptDir & "\logs")
End If
WshShell.Run "cmd /c cd /d """ & scriptDir & """ && """ & pythonPath & """ """ & serverScript & """ > logs\server.log 2>&1", 0, False
WScript.Sleep 3000
WshShell.Run "http://localhost:7860"
Set WshShell = Nothing
Set fso = Nothing
