# NucBox常時オン設定（スリープ完全無効化 + SSH/Tailscale自動起動）

# 1. スリープ・休止を完全無効化
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0
powercfg /change hibernate-timeout-ac 0
powercfg /change hibernate-timeout-dc 0
powercfg /h off

# 2. ディスプレイオフのみ許可（スリープではない）
powercfg /change monitor-timeout-ac 10

# 3. SSHサービスを自動起動に設定
Set-Service -Name sshd -StartupType Automatic
Start-Service sshd

# 4. SSH keepalive設定をサーバー側に追加（重複防止）
$sshdConfig = "C:\ProgramData\ssh\sshd_config"
$content = Get-Content $sshdConfig -Raw
if ($content -notmatch "ClientAliveInterval") {
    Add-Content $sshdConfig "`nClientAliveInterval 60"
    Add-Content $sshdConfig "`nClientAliveCountMax 10"
    Restart-Service sshd
    Write-Host "SSH_KEEPALIVE_ADDED"
} else {
    Write-Host "SSH_KEEPALIVE_ALREADY_SET"
}

# 5. Tailscaleも自動起動確認
Set-Service -Name Tailscale -StartupType Automatic

Write-Host "ALWAYS_ON_CONFIGURED"
