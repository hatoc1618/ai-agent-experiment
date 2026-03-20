#!/bin/bash
# NucBoxにpyRevitをインストールするワンライナー
# Mac側から実行: ./tools/nucbox/run_on_mac.sh

set -e

NUCBOX="IN@100.102.217.90"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== NucBox Setup (pyRevit + Always-On) ==="

# 1. SSH接続確認
echo "[1/5] SSH接続確認..."
if ! ssh -o ConnectTimeout=10 "$NUCBOX" "echo SSH_OK" 2>/dev/null; then
    echo "ERROR: NucBoxに接続できません。スリープ中の可能性があります。"
    exit 1
fi

# 2. スクリプト転送
echo "[2/5] スクリプト転送..."
scp "$SCRIPT_DIR/install_pyrevit.ps1" "$NUCBOX:C:/Users/IN/install_pyrevit.ps1"
scp "$SCRIPT_DIR/setup_always_on.ps1" "$NUCBOX:C:/Users/IN/setup_always_on.ps1"

# 3. pyRevitインストール
echo "[3/5] pyRevitインストール実行..."
ssh "$NUCBOX" "powershell -ExecutionPolicy Bypass -File C:\\Users\\IN\\install_pyrevit.ps1"

# 4. 常時オン設定
echo "[4/5] 常時オン設定（スリープ無効化 + SSH/Tailscale自動起動）..."
ssh "$NUCBOX" "powershell -ExecutionPolicy Bypass -File C:\\Users\\IN\\setup_always_on.ps1"

# 5. 設定確認
echo "[5/5] 設定確認..."
ssh "$NUCBOX" "powershell -Command \"powercfg /query SCHEME_CURRENT SUB_SLEEP | Select-String 'Current AC'; Get-Service sshd,Tailscale | Format-Table Name,Status,StartType\""

echo ""
echo "=== 完了 ==="
echo "次のステップ: RevitMCPクローン"
echo "  ssh $NUCBOX \"\\\"C:\\Program Files\\Git\\bin\\git.exe\\\" -c credential.helper= clone https://github.com/oakplank/RevitMCP.git C:\\Users\\IN\\RevitMCP\""
