# /discussion Slash Command - Quick Start Guide

議論機能をすぐに使い始めるガイド

---

## ⚡ 30秒セットアップ

```bash
# 1. スクリプトを実行可能にする
chmod +x /Users/in/ai-agent-experiment/tools/discussion_command.py

# 2. シンボリックリンクを作成（オプション）
ln -s /Users/in/ai-agent-experiment/tools/discussion_command.py /usr/local/bin/discussion

# 3. テスト実行
python3 /Users/in/ai-agent-experiment/tools/discussion_command.py discuss "テスト議題"
```

---

## 🎯 即座に使える3つのパターン

### パターン1: 協力的な議論（デフォルト）

```bash
python3 tools/discussion_command.py discuss "200+ファイルのリファクタリング戦略"
```

**何が起こるか:**
- ARCHITECT: 理想的な設計を提案
- PRAGMATIST: 現実的なアプローチを提案
- CRITIC: リスクと矛盾を指摘

**用途:** 複雑な決定を理解する

---

### パターン2: 対立的な議論（ディベート）

```bash
python3 tools/discussion_command.py discuss "テスト自動生成 vs テスト不要" --mode debate
```

**何が起こるか:**
- ARCHITECT: 理想を擁護
- PRAGMATIST: ARCHITECT に異議
- CRITIC: 両方の矛盾を指摘

**用途:** 相反する意見をテストする

---

### パターン3: 質問駆動の探究（ソクラテス）

```bash
python3 tools/discussion_command.py discuss "Obsidian統合の最適アーキテクチャ" --mode socratic
```

**何が起こるか:**
- 各専門家が戦略的な質問をする
- 潜在的な仮定を露出
- 深い理解へ導く

**用途:** 学習と能力開発

---

## 📖 実例

### 例1: デザイン決定の検証

```bash
# コマンド
python3 tools/discussion_command.py discuss "マイクロサービス vs モノリシック" --mode debate

# 出力例:
# 【ARCHITECT】
# マイクロサービスは理想的なスケーラビリティを...
#
# 【PRAGMATIST】
# しかし200+ファイルでの複雑性コストは...
#
# 【CRITIC】
# 両方が見落としている依存関係相互作用は...
```

### 例2: リスク評価

```bash
# コマンド
python3 tools/discussion_command.py discuss "AI生成テストの信頼性30-40%失敗率をどう扱うか" --mode debate

# 出力例:
# 【ARCHITECT】
# テスト失敗率は許容範囲で修正可能...
#
# 【PRAGMATIST】
# しかし工数+3-5日の追加が必要...
#
# 【CRITIC】
# テスト保守性の長期リスクを考慮していない...
```

### 例3: 実行計画の構築

```bash
# コマンド
python3 tools/discussion_command.py discuss "200+ファイルリファクタリングの実行戦略" --mode discussion

# 出力例:
# 【統合分析】
# Phase 0: 診断（4-5週間）
#   - AST解析で優先度スコア
#   - ドメイン専門家ヒアリング（ARCHITECT提案）
#   - 多層依存関係分析
#
# Phase 1: クリティカルパス（14-16週間）
#   - 優先度HIGH のみ集中（PRAGMATIST提案）
#   - AI テスト失敗率を見積に明示（CRITIC検証）
# ...
```

---

## 🚀 3つの利用シーン

### シーン1: 決定が難しいとき

```bash
# 悩んでいる場合
python3 tools/discussion_command.py discuss "決定内容" --mode debate

# 3つの視点から徹底的に検証されます
```

### シーン2: 複数の見方を集めたいとき

```bash
# 包括的な理解が必要な場合
python3 tools/discussion_command.py discuss "テーマ"

# デフォルト=discussion（協力的）
# 複数視点の統合分析が得られます
```

### シーン3: 戦略的な質問が欲しいとき

```bash
# 学習・深い考察が必要な場合
python3 tools/discussion_command.py discuss "テーマ" --mode socratic

# 各専門家からの戦略的質問が得られます
```

---

## 💡 3つの視点の特徴

| 視点 | 強み | 弱点 | 時に言う |
|------|------|------|---------|
| **ARCHITECT** | 理想的、包括的 | 実装可能性を軽視 | "理想的には..." |
| **PRAGMATIST** | 現実的、段階化 | 品質施策を削減 | "実装可能な..." |
| **CRITIC** | リスク検出 | 批判的すぎることも | "でもこのリスクは..." |

---

## 🔧 3つのモード解説

### MODE 1: `discussion` (デフォルト)
- **見方:** 協力的、補完的
- **適切な場合:** 複雑な決定、複合視点が必要
- **出力:** 統合的なインサイト

```bash
python3 tools/discussion_command.py discuss "テーマ"
```

### MODE 2: `debate`
- **見方:** 対立的、検証的
- **適切な場合:** リスク高い決定、相反する意見
- **出力:** 矛盾の露出、強度テスト結果

```bash
python3 tools/discussion_command.py discuss "テーマ" --mode debate
```

### MODE 3: `socratic`
- **見方:** 質問駆動、探究的
- **適切な場合:** 学習、戦略的思考開発
- **出力:** 戦略的な質問リスト

```bash
python3 tools/discussion_command.py discuss "テーマ" --mode socratic
```

---

## 🎁 よくある使用パターン

### パターンA: 決定検証フロー

```bash
# Step 1: 複合視点を理解する
python3 tools/discussion_command.py discuss "決定内容" --mode discussion

# Step 2: 厳密に検証する
python3 tools/discussion_command.py discuss "決定内容" --mode debate

# Step 3: 戦略的に深める
python3 tools/discussion_command.py discuss "決定内容" --mode socratic

# Step 4: Obsidianに記録
```

### パターンB: 高速検証

```bash
# リスク高い決定は即座にdebateで検証
python3 tools/discussion_command.py discuss "重要決定" --mode debate
```

### パターンC: 学習ループ

```bash
# 定期的にsocraticで戦略的思考を深める
python3 tools/discussion_command.py discuss "知識構築テーマ" --mode socratic
```

---

## 📊 実際の成果（Final Report から）

このコマンドの基礎となった議論:

```
【議論対象】
200+ファイルのPythonリファクタリング + テスト自動化の矛盾

【参加者】
- ARCHITECT: 理想的4段階設計
- PRAGMATIST: 現実的2段階計画
- CRITIC: 隠れたリスク・矛盾指摘

【成果】
→ 修正版ハイブリッド案
→ 4.75-5.25人月の現実的工数見積
→ 意思決定ゲートによるリスク管理
→ 本番安全性 60-80% 向上期待

【創発的知見】
単一エージェントでは発見されなかった5つの重要インサイト
```

このコマンドで同じ質の議論を**any topic** について即座に実行できます。

---

## ✅ 次のステップ

### 今すぐできること

```bash
# 1. テスト実行
python3 tools/discussion_command.py discuss "テスト議題"

# 2. 実際の決定で使う
python3 tools/discussion_command.py discuss "実際のテーマ" --mode debate

# 3. 結果をObsidianに保存
python3 tools/discussion_command.py discuss "テーマ" > ~/Obsidian/discussion.md
```

### より高度な使用法

```bash
# シェルエイリアスを設定
alias /discuss='python3 ~/ai-agent-experiment/tools/discussion_command.py discuss'
alias /debate='python3 ~/ai-agent-experiment/tools/discussion_command.py discuss --mode debate'
alias /ask='python3 ~/ai-agent-experiment/tools/discussion_command.py discuss --mode socratic'

# これで簡単に:
/discuss "テーマ"
/debate "難しい決定"
/ask "学習テーマ"
```

---

## 🎓 学習リソース

1. **実装ファイル**: `/Users/in/ai-agent-experiment/tools/discussion_command.py`
2. **詳細ドキュメント**: `/Users/in/ai-agent-experiment/tools/DISCUSSION_COMMAND.md`
3. **実例**: `/Users/in/ai-agent-experiment/output/final_report.md`
4. **エージェントプロンプト**: `/Users/in/ai-agent-experiment/agents/`

---

## 🐛 トラブル対応

### エラー: "command not found"

```bash
# フルパスで実行
python3 /Users/in/ai-agent-experiment/tools/discussion_command.py discuss "テーマ"

# または シンボリックリンクを再作成
ln -s /Users/in/ai-agent-experiment/tools/discussion_command.py /usr/local/bin/discussion
```

### エラー: "Unknown mode"

```bash
# 有効なモード: discussion, debate, socratic のみ
python3 tools/discussion_command.py discuss "テーマ" --mode discussion  # ✅
python3 tools/discussion_command.py discuss "テーマ" --mode invalid     # ❌
```

---

## 📞 サポート

詳細は以下を参照:
- `DISCUSSION_COMMAND.md` - 完全なドキュメント
- `final_report.md` - 実装の背景と理由
- `agents/*.md` - 各エージェントの詳細指示

---

**これで準備完了！**

```bash
python3 /Users/in/ai-agent-experiment/tools/discussion_command.py discuss "任意の議題"
```

を実行して、3つの視点から即座に議論を開始できます。
