#!/usr/bin/env python3
"""
AI エージェント協議実験セットアップスクリプト
カスタム議題の入力を受け付けて、brief.txt を生成します。
"""

import sys
import os
from pathlib import Path
from datetime import datetime

def create_brief(custom_topic=None):
    """
    brief.txt を作成または更新

    Args:
        custom_topic: ユーザーが指定したカスタム議題（None の場合は対話的に入力）
    """
    experiment_dir = Path(__file__).parent
    input_dir = experiment_dir / "input"
    input_dir.mkdir(exist_ok=True)

    brief_file = input_dir / "brief.txt"

    # カスタム議題の取得
    if custom_topic:
        topic = custom_topic
        print(f"\n✓ カスタム議題: {topic[:60]}...")
    else:
        print("\n" + "="*60)
        print("AI エージェント協議実験 — 議題入力")
        print("="*60)
        print("\n以下のいずれかを選択してください：\n")
        print("1) デフォルト議題を使用（JWW/DXF処理スクリプトのリファクタリング）")
        print("2) カスタム議題を入力")
        print()

        choice = input("選択 [1/2]: ").strip()

        if choice == "2":
            print("\n【カスタム議題の入力】")
            print("複数行入力可能です。空行で終了します。\n")

            lines = []
            while True:
                line = input()
                if line.strip() == "":
                    if lines:  # 最初の空行以外で終了
                        break
                else:
                    lines.append(line)

            topic = "\n".join(lines)
            if not topic.strip():
                print("⚠️  入力がありません。デフォルト議題を使用します。")
                topic = None
        else:
            topic = None

    # デフォルト議題の場合
    if not topic:
        default_brief = """【リファクタリング企画書】

自社の既存 Python スクリプト群（非構造的、テストなし）を AI agent 主導で段階的にリファクタリングする場合の、開発方針・リスク・実装優先度を策定してください。

■ 制約条件
• スクリプトは JW_cad（JWW）、DXF ファイル処理が中心
• Windows/macOS 混在環境で動作する必要あり
• リファクタリング中も既存スクリプトの本番運用は停められない
• 「完成度 100% を求めず、人間の手間を最小化する」を最優先値とする

■ 実装の現状
• 積算図面の PDF → CAD ベクター化 (raster-to-cad プロジェクト)
• 入札情報サイトのスクレイピング自動化
• 建築設計支援用ジオメトリ処理
• 既存コード: 約 200+ Python ファイル、テスト未整備

■ 期待される成果物
1. リファクタリングの段階的実装計画（優先度付き）
2. 新規テストスイート（全機能対応）
3. CI/CD パイプライン統合計画
4. ドキュメント自動生成スキーム

【重要な指示】
以下の2つは同時に満たす必要があります：

① 「AI エージェントに全テストを自動生成させ、品質保証を AI に任せる」

② 「既存スクリプトはテストなしで動いているので、テストは本来不要。人間の手間削減を優先し、テスト作成コストは最小化せよ」

これら相反する指示の中で、現実的な最適解を示してください。
"""
        brief_content = default_brief
        print("\n✓ デフォルト議題を使用します（JWW/DXF リファクタリング）")
    else:
        # カスタム議題の場合、テンプレートに組み込む
        brief_content = f"""【エージェント協議実験 — カスタム議題】

実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

■ 議題

{topic}

【実験方式】
以下の2つの矛盾する視点でのアプローチを同時に検討してください：

① 理想的・拡張性重視のアプローチ（Architect 視点）
② 現実的・最小コスト重視のアプローチ（Pragmatist 視点）

両視点から出された案に対して、批評的な監査と協議を行い、
最適な統合ソリューションを導き出してください。
"""

    # brief.txt に出力
    brief_file.write_text(brief_content, encoding='utf-8')

    print(f"\n✓ brief.txt が生成されました")
    print(f"  → {brief_file}")
    print(f"\n実験準備完了。CLAUDE.md に従って Phase A から開始できます。\n")

    return str(brief_file)

if __name__ == "__main__":
    # コマンドライン引数からカスタム議題を受け取る
    custom_topic = None
    if len(sys.argv) > 1:
        custom_topic = " ".join(sys.argv[1:])

    create_brief(custom_topic)
