# Slash Command Implementation Index

議論・協議機能のスラッシュコマンド実装

---

## 🎯 What Was Created

スラッシュコマンド `/discussion` - 任意の議題について3つの視点（ARCHITECT, PRAGMATIST, CRITIC）から協議するツール

### 📁 Files Created

```
/Users/in/ai-agent-experiment/tools/
├── discussion_command.py           ← メイン実装
├── QUICK_START.md                  ← 30秒クイックスタート
├── DISCUSSION_COMMAND.md           ← 詳細ドキュメント
├── obsidian_extract.py             ← Obsidian統合（参考）
├── claude_code_integration.json    ← Claude Code設定
├── setup_slash_command.sh          ← セットアップスクリプト
└── README_SLASH_COMMAND.md         ← 背景説明

/Users/in/ai-agent-experiment/
└── SLASH_COMMAND_INDEX.md          ← このファイル
```

---

## 🚀 Quick Usage

```bash
# 即座に使える
python3 /Users/in/ai-agent-experiment/tools/discussion_command.py discuss "議題"

# モード指定
python3 /Users/in/ai-agent-experiment/tools/discussion_command.py discuss "議題" --mode debate

# 3つのモード選択可能
# - discussion (協力的分析)
# - debate (対立的検証)
# - socratic (質問駆動探究)
```

---

## 📖 3つのモード

### 1. DISCUSSION（デフォルト）
各専門家が互いの視点を尊重して補完的に分析

```bash
python3 tools/discussion_command.py discuss "複雑なテーマ"
```

**出力:**
- ARCHITECT: 理想的な設計視点
- PRAGMATIST: 現実的な実装視点
- CRITIC: リスク検出視点
- 統合的なインサイト

**用途:** 複合視点が必要な複雑な決定

---

### 2. DEBATE（対立的）
専門家が互いの仮定に異議を唱え、立場を擁護

```bash
python3 tools/discussion_command.py discuss "リスク高い決定" --mode debate
```

**出力:**
- 立場の明確化
- 仮定への異議
- 相互反論
- 矛盾と陥穽の露出

**用途:** 相反する意見をテストする

---

### 3. SOCRATIC（質問駆動）
戦略的な質問を通じて理解を深める

```bash
python3 tools/discussion_command.py discuss "学習テーマ" --mode socratic
```

**出力:**
- ARCHITECT: 理想的視点からの質問
- PRAGMATIST: 実装視点からの質問
- CRITIC: リスク視点からの質問
- 段階的な思考の深化

**用途:** 学習と戦略的思考開発

---

## 🎭 3つの専門家視点

### ARCHITECT (建築家)
- **視点**: 理想的、包括的、品質重視
- **焦点**: システム設計、長期戦略、ベストプラクティス
- **強み**: 完全性、スケーラビリティ、理論的正確性
- **弱み**: 実装可能性、コスト現実性

### PRAGMATIST (実用主義者)
- **視点**: 現実的、実装可能、コスト重視
- **焦点**: リソース制約、段階化、ROI優先
- **強み**: 実現可能性、段階化戦略、ROI意識
- **弱み**: 品質施策削減、長期投資不足

### CRITIC (批評家)
- **視点**: 懐疑的、リスク重視、仮定挑戦
- **焦点**: 隠れたリスク、矛盾検出、盲点露出
- **強み**: リスク検出、矛盾発見、仮定検証
- **弱み**: 建設的でない、過度に批判的

---

## 💡 実例から学ぶ

### 実例: 200+ファイルのリファクタリング（実際に実施）

```bash
# 実際の議論コマンド（再現可能）
python3 tools/discussion_command.py discuss "200+ファイルのPythonリファクタリング: テスト自動生成 vs テスト不要" --mode debate
```

**実際の結果（Final Report に記載）:**

| 視点 | 提案 | 工数 |
|------|------|------|
| **ARCHITECT** | 4段階フルテスト | 18-29週間 |
| **PRAGMATIST** | 2段階最小化 | 13-15週間 |
| **CRITIC検証** | リスク指摘 | - |
| **最終案** | 修正版ハイブリッド | 18-22週間 |

**成果:**
- 本番安全性 60-80% 向上
- AI テスト失敗率を工数に明示
- テスト保守性リスク検出
- ドメイン専門家ヒアリング追加
- 意思決定ゲート導入

---

## 🔄 推奨ワークフロー

### ステップ1: 複合視点で理解（10-15分）

```bash
python3 tools/discussion_command.py discuss "決定内容"
```

→ 各視点の異なる分析を理解

### ステップ2: 厳密に検証（15-20分）

```bash
python3 tools/discussion_command.py discuss "決定内容" --mode debate
```

→ リスクと矛盾を明確化

### ステップ3: 戦略的に深める（10-15分）

```bash
python3 tools/discussion_command.py discuss "決定内容" --mode socratic
```

→ 戦略的な質問で理解を深化

### ステップ4: 結果を記録（5分）

```bash
# Obsidian に保存
python3 tools/discussion_command.py discuss "決定内容" --mode debate \
  > ~/Obsidian/Discussions/$(date +%Y%m%d).md
```

→ 決定の監査証跡を作成

---

## 📊 3つの議論形式の選択ガイド

| 選択 | 状況 | モード | 期待時間 |
|------|------|--------|---------|
| 理解が必要 | 複雑な決定、複合視点 | discussion | 15-20分 |
| 検証が必要 | リスク高い、相反する意見 | debate | 20-30分 |
| 学習が目標 | 戦略的思考開発、能力構築 | socratic | 15-25分 |

---

## 🛠️ セットアップ

### 最小セットアップ（1分）

```bash
# そのまま使える（フルパス指定）
python3 /Users/in/ai-agent-experiment/tools/discussion_command.py discuss "テーマ"
```

### 快適セットアップ（2分）

```bash
# シンボリックリンク作成
ln -s /Users/in/ai-agent-experiment/tools/discussion_command.py /usr/local/bin/discussion

# シェルエイリアス設定（~/.zshrc or ~/.bashrc に追加）
alias /discuss='discussion discuss'
alias /debate='discussion discuss --mode debate'
alias /ask='discussion discuss --mode socratic'
```

使用:
```bash
/discuss "テーマ"
/debate "難しい決定"
/ask "学習テーマ"
```

---

## 📚 ドキュメント構成

```
ドキュメント構成（推奨読了順）

1. 【QUICK_START.md】← ここから始める（5分）
   - 30秒セットアップ
   - 3つの基本パターン
   - 実例

2. 【DISCUSSION_COMMAND.md】← 詳細理解（20分）
   - コマンドリファレンス
   - 3つのモード詳細
   - 高度な使用法
   - トラブルシューティング

3. 【final_report.md】← 背景理解（30分）
   - 実装の理由
   - 実例での成果
   - 複数エージェント協議の価値

4. 【agents/】← 詳細な指示書（参考用）
   - 01_architect.md
   - 02_pragmatist.md
   - 03_critic.md
```

---

## 🎯 典型的な使用シーン

### シーン1: 重要な決定が必要

```bash
# 3モード全て実施で確実な検証
for mode in discussion debate socratic; do
  echo "=== $mode mode ==="
  python3 tools/discussion_command.py discuss "決定内容" --mode $mode
done
```

### シーン2: 急速に判断が必要

```bash
# debateで即座にリスク検証
python3 tools/discussion_command.py discuss "決定内容" --mode debate
```

### シーン3: チーム学習が目標

```bash
# socraticで戦略的思考を発展
python3 tools/discussion_command.py discuss "学習テーマ" --mode socratic
```

---

## ✨ 実装のハイライト

### 特徴1: すぐに使える
- 複雑なセットアップなし
- フルパスで即座に実行可能
- Python 3.8+があれば動作

### 特徴2: 3つの独立した視点
- ARCHITECT: 理想 × 系統的
- PRAGMATIST: 現実 × 段階化
- CRITIC: リスク × 検証

各視点は独立した分析フレームワーク

### 特徴3: 3つの互いに異なるモード
- discussion: 協力的分析
- debate: 対立的検証
- socratic: 質問駆動探究

同じテーマを3つの方法で検討可能

### 特徴4: 証拠に基づく設計
- Final Report の実例から学習
- 実際に効果があったパターン
- 複数エージェント協議の価値を実証

---

## 🔗 関連リソース

### 実装ファイル
- **Main Script**: `/Users/in/ai-agent-experiment/tools/discussion_command.py`

### ドキュメント
- **Quick Start**: `/Users/in/ai-agent-experiment/tools/QUICK_START.md`
- **Full Guide**: `/Users/in/ai-agent-experiment/tools/DISCUSSION_COMMAND.md`
- **Case Study**: `/Users/in/ai-agent-experiment/output/final_report.md`

### エージェント指示書
- **Architect**: `/Users/in/ai-agent-experiment/agents/01_architect.md`
- **Pragmatist**: `/Users/in/ai-agent-experiment/agents/02_pragmatist.md`
- **Critic**: `/Users/in/ai-agent-experiment/agents/03_critic.md`

### プロジェクト設定
- **Project README**: `/Users/in/ai-agent-experiment/CLAUDE.md`

---

## 💬 使用例

### 例1: デザイン決定

```bash
python3 tools/discussion_command.py discuss "マイクロサービス vs モノリシック設計" --mode debate
```

出力例:
```
【ARCHITECT】
マイクロサービスは理想的なスケーラビリティを...

【PRAGMATIST】
しかし200ファイルでの複雑性コストは...

【CRITIC】
両方とも隠れた依存関係リスクを軽視...
```

### 例2: リスク評価

```bash
python3 tools/discussion_command.py discuss "AI生成テスト30-40%失敗率への対応" --mode debate
```

### 例3: 実行計画構築

```bash
python3 tools/discussion_command.py discuss "リファクタリング実行戦略" --mode discussion
```

---

## ✅ チェックリスト

- [ ] `discussion_command.py` を実行可能にする
- [ ] 一度テスト実行してみる
- [ ] `QUICK_START.md` を読む（5分）
- [ ] 実際の決定で使ってみる
- [ ] Obsidian に結果を保存
- [ ] 3つのモードを使い分ける

---

## 🎓 Next Steps

### 今日中にやること
```bash
# 1. テスト実行
python3 /Users/in/ai-agent-experiment/tools/discussion_command.py discuss "テスト議題"

# 2. 実例で試す
python3 /Users/in/ai-agent-experiment/tools/discussion_command.py discuss "実際の課題" --mode debate
```

### 1週間以内
- [ ] 重要な決定で実際に使う
- [ ] 3つのモードをそれぞれ試す
- [ ] 結果をObsidianに記録

### 継続的に
- [ ] 定期的に戦略的質問でチーム学習（socratic）
- [ ] リスク高い決定は必ずdebateで検証
- [ ] 複雑な決定は3モード全て実施

---

## 📞 Support

### トラブル対応
- コマンド不見: フルパスで実行
- モードエラー: `discussion`, `debate`, `socratic` のみ有効
- Python エラー: `python3 --version` で確認

### より詳しく知るには
1. `QUICK_START.md` - 5分で概要把握
2. `DISCUSSION_COMMAND.md` - 完全なリファレンス
3. `final_report.md` - 実装の背景と成果

---

## 🎉 Ready to Use!

```bash
# これで準備完了
python3 /Users/in/ai-agent-experiment/tools/discussion_command.py discuss "任意の議題"
```

**3つの専門家視点から即座に議論が始まります！**

---

**Created**: 2026-03-06
**Status**: Production Ready
**Version**: 1.0.0
