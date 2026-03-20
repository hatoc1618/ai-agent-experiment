# pyRevit v6.1.0 サイレントインストール（タスクスケジューラ経由で管理者実行）
# NucBox_M7Pro (IN@100.102.217.90) 用

$installerPath = "C:\Users\IN\pyrevit_installer.exe"

if (-not (Test-Path $installerPath)) {
    Write-Host "ERROR: Installer not found at $installerPath"
    exit 1
}

# タスクスケジューラ経由でUACなし管理者実行
schtasks /create /tn "pyRevitInstall" /tr "$installerPath /VERYSILENT /NORESTART" /sc once /st 00:00 /rl highest /f
schtasks /run /tn "pyRevitInstall"
Write-Host "TASK_STARTED"

# 完了待機（最大120秒）
$timeout = 120
$elapsed = 0
while ($elapsed -lt $timeout) {
    Start-Sleep 5
    $elapsed += 5
    $status = schtasks /query /tn "pyRevitInstall" /fo csv 2>$null | ConvertFrom-Csv
    if ($status.Status -eq "Ready") {
        Write-Host "INSTALL_COMPLETE ($elapsed sec)"
        break
    }
    Write-Host "Waiting... ($elapsed sec)"
}

if ($elapsed -ge $timeout) {
    Write-Host "WARNING: Timeout reached, check manually"
}

# クリーンアップ
schtasks /delete /tn "pyRevitInstall" /f

# 検証
$pyrevitPath = Get-Command pyrevit -ErrorAction SilentlyContinue
if ($pyrevitPath) {
    Write-Host "SUCCESS: pyrevit found at $($pyrevitPath.Source)"
    pyrevit --version
} else {
    # よくあるインストール先を確認
    $candidates = @(
        "C:\Program Files\pyRevit-Master\bin\pyrevit.exe",
        "C:\Program Files\pyRevit\bin\pyrevit.exe",
        "$env:APPDATA\pyRevit-Master\bin\pyrevit.exe"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) {
            Write-Host "FOUND: $p"
            & $p --version
            break
        }
    }
    if (-not (Test-Path $p)) {
        Write-Host "NOT_IN_PATH: pyrevit not found, may need PATH update or Revit restart"
    }
}
