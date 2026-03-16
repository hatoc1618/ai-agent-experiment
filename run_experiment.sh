#!/bin/bash
# AI エージェント協議実験を実行する
# 議題を対話的に受け付けます

set -e

EXPERIMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$EXPERIMENT_DIR"

echo ""
echo "==============================================="
echo "AI エージェント協議実験 — 議題入力"
echo "==============================================="
echo ""
echo "以下のいずれかを選択してください："
echo ""
echo "1) デフォルト議題を使用（JWW/DXF処理スクリプトのリファクタリング）"
echo "2) カスタム議題を入力"
echo ""

read -p "選択 [1/2]: " choice

if [ "$choice" = "2" ]; then
    echo ""
    echo "【カスタム議題の入力】"
    echo "複数行入力可能です。空行で終了します。"
    echo ""

    # 複数行入力を受け付ける
    lines=()
    while true; do
        read -p "" line
        if [ -z "$line" ]; then
            break
        fi
        lines+=("$line")
    done

    # Python スクリプトで brief.txt を生成
    custom_topic=$(printf '%s\n' "${lines[@]}")
    python3 setup_experiment.py "$custom_topic"
else
    # デフォルト議題を使用
    python3 setup_experiment.py
fi

echo ""
echo "✓ 準備完了。CLAUDE.md に従って Phase A から開始します。"
echo ""
