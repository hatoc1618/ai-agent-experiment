# タスクスケジューラ経由でUACなし管理者実行
schtasks /create /tn "pyRevitInstall" /tr "C:\Users\IN\pyrevit_installer.exe /VERYSILENT /NORESTART" /sc once /st 00:00 /rl highest /f
schtasks /run /tn "pyRevitInstall"
Write-Host "TASK_STARTED"

# 完了待機
Start-Sleep 30
schtasks /query /tn "pyRevitInstall" /fo csv | Select-String "Running|Ready"

# クリーンアップ
schtasks /delete /tn "pyRevitInstall" /f
