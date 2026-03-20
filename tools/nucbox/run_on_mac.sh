#!/bin/bash
# NucBoxにpyRevitをインストールするワンライナー
# Mac側から実行: ./tools/nucbox/run_on_mac.sh

set -e

NUCBOX="IN@100.102.217.90"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== NucBox pyRevit Installer ==="

# 1. SSH接続確認
echo "[1/4] SSH接続確認..."
if ! ssh -o ConnectTimeout=10 "$NUCBOX" "echo SSH_OK" 2>/dev/null; then
    echo "ERROR: NucBoxに接続できません。スリープ中の可能性があります。"
    exit 1
fi

# 2. スリープ無効化
echo "[2/4] スリープ無効化..."
ssh "$NUCBOX" "powershell -Command \"powercfg /change standby-timeout-ac 0; powercfg /change hibernate-timeout-ac 0; echo SLEEP_DISABLED\""

# 3. インストールスクリプトを転送
echo "[3/4] インストールスクリプト転送..."
scp "$SCRIPT_DIR/install_pyrevit.ps1" "$NUCBOX:C:/Users/IN/install_pyrevit.ps1"

# 4. 実行
echo "[4/4] pyRevitインストール実行..."
ssh "$NUCBOX" "powershell -ExecutionPolicy Bypass -File C:\\Users\\IN\\install_pyrevit.ps1"

echo ""
echo "=== 完了 ==="
echo "次のステップ: RevitMCPクローン"
echo "  ssh $NUCBOX \"\\\"C:\\Program Files\\Git\\bin\\git.exe\\\" -c credential.helper= clone https://github.com/oakplank/RevitMCP.git C:\\Users\\IN\\RevitMCP\""
